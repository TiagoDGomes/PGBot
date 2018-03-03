# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import time
import requests
import telegram
import threading
import traceback
import logging
import json
import thread
from googleapi import get_address

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

from servermap import ServerMap

from util import load_from_file, save_to_file, datetime_from_utc_to_local, timestamp_to_time

from constants import *

class RocketMapBot(threading.Thread, object):
    
    def __init__(self, url_list, center_latitude, 
                            center_longitude, 
                            radius_lat=0.05,
                            radius_lng=0.16,
                            auto_start=False, 
                            scan_pokemon=True, 
                            scan_pokestops=False, 
                            scan_gyms=False, 
                            scan_update=30,
                            googlemaps_api_key=None,
                            telegram_token=None,
                            ):
        super(RocketMapBot, self).__init__()
        self.scan_update = scan_update
        self.center_latitude = center_latitude
        self.center_longitude = center_longitude
        self.log = logging.getLogger('log ')  
        self.log_raid = logging.getLogger('raid')  
        self.log_pokemon = logging.getLogger('poke') 
        self.scan_pokemon = scan_pokemon
        self.scan_pokestops = scan_pokestops
        self.scan_gyms = scan_gyms
        self._running = auto_start
        self.last_raw_data = None
        self.last_scan_gyms = {}
        self.last_scan_pokemon = {}
        self.gym_details = {}
        self.test_count_file_index = 1

        self.googlemaps_api_key = googlemaps_api_key
        self.encounters = {}
        if not url_list or not isinstance(url_list, list):
            raise Exception('invalid url_list')

        self.url_list = url_list
        self.last_url_index = 0  
        self.servers_map = []
        for u in url_list:
            s = ServerMap(u, self)
            self.servers_map.append(s)

        self.swLat = self.center_latitude - radius_lat
        self.neLat = self.center_latitude + radius_lat
        self.swLng = self.center_longitude - radius_lng
        self.neLng = self.center_longitude + radius_lng

        try:
            self.MOVES_LIST = load_from_file('moves.min.json', {})
        except:
            self.MOVES_LIST = {}
        if auto_start:           
            self.start()            
        
        self.telegram_interested_pokemon = load_from_file('telegram_interested_pokemon.json', {})
        self.telegram_interested_raid = load_from_file('telegram_interested_raid.json', {})
        self.telegram_clients = load_from_file('telegram_clients.json', {})

        if telegram_token:
            self.telegram_updater = Updater(token=telegram_token)
            self.telegram_bot = self.telegram_updater.bot            
            self.telegram_updater.start_polling()

        else:
            self.telegram_updater = None
            self.telegram_bot = None


     
        

    def stop(self):
        self._running = False


    def restart(self):
        self.stop()
        time.sleep(5)
        self._running = False
        self.start()
    

    
    def telegram_send_to_user(self, chat_id, msg, photo=None, preview=True):        
        def send(c_id, msg):            
            if not c_id in self.telegram_clients:
                #msg = MESSAGE_CLIENT_DENIED.format(chat_id=c_id)
                #self.telegram_bot.send_message(chat_id=int(c_id), text=msg, disable_web_page_preview=not preview) 
                pass
            else:
                self.log.info('[t] Enviando para {0}...'.format(c_id))
                if photo:
                    self.telegram_bot.send_photo(chat_id=int(c_id), photo=photo, caption=msg)
                else:
                    self.telegram_bot.send_message(chat_id=int(c_id), text=msg, disable_web_page_preview=not preview) 
                self.log.info('[t] Enviado.')

        self.log.info('Enviando para {0}...'.format(chat_id))
        thread.start_new_thread(send, (chat_id,msg,))
        time.sleep(1)


    
        
    def send_to_interested(self, latitude, longitude, raid_level=None, is_egg=True, pokemon_id=None, iv=-1, message=None, time_delay=0, photo=None):        
        if self.telegram_updater is None:
            self.log.info('''Não é possível enviar via Telegram''')
        else:
            telegram_interested = []
                            
            if raid_level:
                try:
                    for chat_id in self.telegram_interested_raid[str(raid_level)].iterkeys():                        
                        if not chat_id in telegram_interested:           
                            self.log.info('L{0} para {1}'.format(raid_level, chat_id))                            
                            self.telegram_send_to_user(chat_id, message, photo=photo)
                            telegram_interested.append(chat_id)
                except KeyError:
                    pass
            if pokemon_id:
                try:                    
                    for chat_id in self.telegram_interested_pokemon[str(pokemon_id)].iterkeys():
                        if not chat_id in telegram_interested:
                            self.log.info('#{0} para {1}'.format(pokemon_id, chat_id))
                            self.telegram_send_to_user(chat_id, message, photo=photo)
                            telegram_interested.append(chat_id)
                except KeyError:
                    pass        


        
    def get_updates(self, timestamp):
        self.log.info('Busca...')
        self.last_url_index += 1           
        if self.last_url_index >= len(self.servers_map):
            self.last_url_index = 0                            

        self.log.debug('last_url_index={0}'.format(self.last_url_index))
        self.log.debug('len={0}'.format(len(self.servers_map) ))
        self.running_update = True
        self.last_raw_data = self.servers_map[self.last_url_index].get_raw_data(timestamp)
        self.running_update = False


        
        
    def verify(self, chat_id_request=None, pokemon_id_request=None):
        raw_data = self.last_raw_data
        now =  int(time.time() * 1000)         
        details = ''
        # ========== Gyms ========= #
        if self.scan_gyms:
            actual_gym_state = raw_data['gyms']            
            dict_v = isinstance(actual_gym_state, dict)  
            self.log.info('Total de ginásios: {0}'.format(len(actual_gym_state)))              
            for g in actual_gym_state: 
                # Há diferença em 'gyms' entre versões antigas e novas do RocketMap
                if dict_v:                    
                    gym = actual_gym_state[g] 
                    gym_id = g
                else:
                    gym = g
                    gym_id = gym['gym_id']    
                details = ''
                raid_start = gym['raid_start']     
                raid_end = gym['raid_end'] 
                
                raid_level = gym['raid_level'] 
                raid_pokemon_id = gym['raid_pokemon_id'] if 'raid_pokemon_id' in gym or gym['raid_pokemon_id'] != 0 else None
                raid_pokemon_name = gym['raid_pokemon_name'] if 'raid_pokemon_name' in gym or gym['raid_pokemon_id'] != 0 else None
                
                first_update = False
                if not gym_id in self.gym_details:
                    self.gym_details[gym_id] = {}
                    self.gym_details[gym_id].update(gym)
                    first_update = True
                if self.gym_details[gym_id]['name'] is None:
                    self.gym_details[gym_id]['name'] = get_address(gym['latitude'], gym['longitude'], self.googlemaps_api_key)
                    self.gym_details[gym_id]['generic_name'] = True
                if 'generic_name' in self.gym_details[gym_id] and self.gym_details[gym_id]['generic_name'] and gym['name'] is not None:
                    self.gym_details[gym_id]['name'] = gym['name']
                    self.gym_details[gym_id]['generic_name'] = False
                latitude = self.gym_details[gym_id]['latitude']
                longitude = self.gym_details[gym_id]['longitude']
                
                is_egg = raid_start > now              
                raid_status_string = str(raid_start) + str(raid_level) + str(raid_pokemon_id) 

                gym_name = self.gym_details[gym_id]['name'] 
                
                if not first_update:       
                    if gym['last_scanned'] <= self.gym_details[gym_id]['last_scanned']:
                        self.log.debug('=  ignorando: {0}'.format(gym_name))
                    else:  
                        self.log.info('= analisando: {0} (de {1} para {2})'.format(gym_name, 
                                                                timestamp_to_time(self.gym_details[gym_id]['last_scanned']), 
                                                                timestamp_to_time(gym['last_scanned']), ))      
                        if raid_end == 0 or raid_end < now or raid_level == 0:
                            self.log_raid.debug('== --  [---]')
                        else:
                            if not 'raid_status_string' in self.gym_details[gym_id] or self.gym_details[gym_id]['raid_status_string'] != raid_status_string:                                             
                                time_raid_start = timestamp_to_time(raid_start)
                                time_raid_end = timestamp_to_time(raid_end)  
                                team_name = TEAM_LIST[gym['team_id']]
                                if is_egg:
                                    ''' Raid não começou '''
                                    self.log_raid.info('== L{0} = [---] (start: {1})'.format(raid_level, time_raid_start))
                                    msg = NOTIFICATION_RAID_EGG_FORMAT
                                    icon = RAID_EGG_ICONS[raid_level]
                                else:
                                    if raid_pokemon_id is None:
                                        ''' Mapa Atrasado '''
                                        self.log_raid.info('== L{0} = [{1}] (end: {2}) bot atrasado'.format(raid_level, '????', time_raid_end))
                                        msg = NOTIFICATION_RAID_HATCH_LAZY_FORMAT
                                        diff = (abs(gym['last_scanned'] / 1000 - now / 1000) / 60)                            
                                        if diff > 5:
                                            details = '\nAtraso do mapa: {diff}min.'.format(diff=diff)
                                    else:
                                        ''' Mapa com pokémon '''
                                        raid_pokemon_move_1 = '[AR:{0}]'.format(gym['raid_pokemon_move_1'])
                                        raid_pokemon_move_2 = '[AC:{0}]'.format(gym['raid_pokemon_move_2'])
                                        try:
                                            raid_pokemon_move_1=self.MOVES_LIST[str(gym['raid_pokemon_move_1'])]['name']
                                        except:
                                            pass
                                        try:
                                            raid_pokemon_move_2=self.MOVES_LIST[str(gym['raid_pokemon_move_2'])]['name']
                                        except:
                                            pass
                                        
                                        self.log_raid.info('== L{0} = [{1}] (end: {2})'.format(raid_level, raid_pokemon_name, time_raid_end))
                                        msg = NOTIFICATION_RAID_HATCH_FORMAT
                                        try:
                                            icon = RAID_HATCH_ICON_LIST[str(raid_pokemon_id)]
                                        except:
                                            icon = RAID_HATCH_ICON.format(pokemon_id=raid_pokemon_id)   
                
                                photo = POKEMON_THUMBNAIL_MAP_URL.format(icon=icon, latitude=latitude, longitude=longitude, googlemaps_api_key=self.googlemaps_api_key) 
                                msg = msg.format(**locals())    
                                if chat_id_request is None:                   
                                    self.send_to_interested(latitude=latitude, longitude=longitude, raid_level=raid_level, pokemon_id=raid_pokemon_id, message=msg, photo=photo)
                                else:
                                    self.send_to_users(chat_id_request, msg)

                        if self.gym_details[gym_id]['team_id'] != gym['team_id']:     
                            self.log.debug('== Derrubado: {0} por {1}'.format( 
                                            TEAM_LIST[self.gym_details[gym_id]['team_id']] , 
                                            TEAM_LIST[gym['team_id']],
                                        ))
                        if self.gym_details[gym_id]['slots_available'] > gym['slots_available']:     
                            self.log.debug('== Reforcado com {0}; {1} vaga(s) '.format( 
                                            gym['guard_pokemon_name'],
                                            gym['slots_available'], 
                                        ))
                        elif self.gym_details[gym_id]['slots_available'] < gym['slots_available']:               
                            self.log.debug('== Queda de pokemon! {0} vaga(s) '.format( 
                                            gym['slots_available'], 
                                        ))    
                        
                        
                        
                        self.gym_details[gym_id].update(gym)    
                
                self.gym_details[gym_id]['raid_status_string'] = raid_status_string
                    


        if self.scan_pokemon and 'pokemons' in raw_data:
            self.log_pokemon.info('Verificando pokémon...') 
            if isinstance(raw_data['pokemons'], list):
                list_pokemons = raw_data['pokemons']
            else:
                list_pokemons = raw_data['pokemons'].iteritems()
            poke_counter = 0
            pokemon_total = len(list_pokemons)
            if pokemon_total == 0 and chat_id_request is not None:
                self.send_to_users(chat_id_request, 'Lista vazia. Aguarde.')
            else:
                for p in list_pokemons:
                    
                    if not isinstance(raw_data['pokemons'], list):
                        _, pokemon = p
                    else:
                        pokemon = p
                    disappear_time = pokemon['disappear_time']
                    
                    if disappear_time - 15 > now:
                        encounter_id = pokemon['encounter_id']
                        pokemon_id = pokemon['pokemon_id']
                        pokemon_name = pokemon['pokemon_name'] 
                        latitude = pokemon['latitude']
                        longitude = pokemon['longitude'] 
                        
                        move_list = ''
                        try:
                            move_1=self.MOVES_LIST[str(gym['move_1'])]['name']
                            move_2=self.MOVES_LIST[str(gym['move_2'])]['name']
                            move_list = 'Moves: {0} / {1}'.format(move_1, move_2)
                        except:
                            pass
                        

                                        
                                        
                        key = "{0},{1},{2}".format(encounter_id, latitude, longitude)
                        
                        is_encounter = False
                        try:
                            _ = self.encounters[key]['pokemon_name']
                            is_encounter = True
                        except:
                            pass
                        if not is_encounter:
                            poke_counter += 1
                            self.log_pokemon.debug(pokemon_name + ' apareceu') 
                            self.encounters[key] = {'pokemon_name': pokemon_name, 'disappear_time': disappear_time }
                            try:
                                gender = GENDER_LIST[pokemon['gender']]
                            except:
                                gender = ''
                            
                            iv = -1
                            no_cache = False
                            details = ''
                            if pokemon['individual_attack'] is not None and pokemon['individual_defense'] is not None and pokemon['individual_stamina'] is not None :
                                at = pokemon['individual_attack']
                                df = pokemon['individual_defense']
                                st = pokemon['individual_stamina']
                                iv = round(100.0 * (at + df + st) / 45, 1)
                                details = '{d}\nIV: {iv}% ({at}/{df}/{st})'.format(d=details, iv=iv, at=at, df=df, st=st)
                                if iv > 93:
                                    no_cache = True
                            if pokemon['cp'] is not None:
                                details = '{0}\nCP: {1}'.format(details, pokemon['cp'])
                            if pokemon['level'] is not None:
                                details = '{0} | L{1}'.format(details, pokemon['level'])
                            
                            details = '{0}\n{1}'.format(details, get_address(latitude, longitude, self.googlemaps_api_key,no_cache=no_cache, force=False))
                            disappear_time_str = timestamp_to_time(disappear_time)
                            msg = NOTIFICATION_WILD_FORMAT.format(**locals())
                            icon = POKEMON_ICON.format(pokemon_id=pokemon_id)
                            photo = POKEMON_THUMBNAIL_MAP_URL.format(icon=icon, latitude=latitude, longitude=longitude, googlemaps_api_key=self.googlemaps_api_key)           
                            if chat_id_request is None:
                                self.send_to_interested(latitude=latitude, longitude=longitude, pokemon_id=pokemon_id, message=msg, iv=iv, photo=photo)
                            else:
                                self.send_to_users(chat_id_request, msg)
            len_storage = len(self.encounters)
            self.log_pokemon.info('Total: {0} ; Novos: {1}; Armazenados: {2}'.format(pokemon_total, poke_counter, len_storage))           
                     
                
                    
    def clear_disappear(self):
        self.log.info('Limpando...')
        encounters = self.encounters.copy()
        now =  int(time.time() * 1000)
        for key in encounters.iterkeys():
            if encounters[key]['disappear_time'] < now:
                del self.encounters[key]
        self.log.info('Limpo.')
    
    def run(self):
        c = 0   
        self.running_update = False
        while self._running:
            c += 1
            try:
                timestamp = int(time.time())
                if not self.running_update:
                    thread.start_new_thread(self.get_updates, (timestamp,) )
                
            except Exception as e:
                try:
                    traceback.print_exc()
                except:
                    pass 
            time.sleep(self.scan_update)    
            if not self.running_update:
                self.verify()    
               
            if c > 5:
                c = 0
                self.clear_disappear()
                time.sleep(self.scan_update - 1)
                self.running_update = False
            else:
                time.sleep(self.scan_update)
            
            
if __name__ == "__main__": 
    try:
        import run
    except: 
        traceback.print_exc()

