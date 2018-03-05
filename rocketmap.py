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
from random import randint

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
        
        
        if telegram_token:
            self.telegram_updater = Updater(token=telegram_token)
            self.telegram_bot = self.telegram_updater.bot            
            self.telegram_spool = []        
            self.telegram_interested_pokemon = load_from_file('telegram_interested_pokemon.json', {})
            self.telegram_interested_raid = load_from_file('telegram_interested_raid.json', {})
            self.telegram_clients = load_from_file('telegram_clients.json', {})
            self.telegram_dispatcher = self.telegram_updater.dispatcher
            self.telegram_dispatcher.add_handler(CommandHandler('spawns', self.telegram_command_spawns))
            self.telegram_dispatcher.add_handler(CommandHandler('show', self.telegram_command_show_pokemon, pass_args=True))
            self.telegram_dispatcher.add_handler(CommandHandler('start', self.telegram_command_start))
            self.telegram_clients_ignore = {}
            self.telegram_dispatcher.add_handler(CommandHandler('chatid', self.telegram_command_chatid))
            n = tuple()
            thread.start_new_thread(self.telegram_updater.start_polling, n)
            
        else:
            self.telegram_updater = None
            self.telegram_bot = None

        if auto_start:           
            self.start()            

    def telegram_check_permission_command(function):
        def check(*args, **kwargs):
            authorized = True
            self = args[0]
            bot = args[1]
            update = args[2]
            try:
                chat_id = str(update.message.chat_id)
                if not chat_id in self.telegram_clients:
                    try:
                        query = update.callback_query
                        chat_id = str(query.message.chat_id)
                        if not chat_id in self.telegram_clients:
                            authorized = True
                    except:
                        authorized = False
            except AttributeError:
                pass
            if authorized:
                function(*args, **kwargs)
            else:
                msg = 'Você não está autorizado a conversar comigo. Seu código é {0}.'.format(chat_id)
                bot.send_message(chat_id=chat_id, text=msg)
        return check

    @telegram_check_permission_command
    def telegram_command_start(self, bot, update):
        global WELCOME_MESSAGE, WELCOME_MESSAGE_GROUP
        #print WELCOME_MESSAGE
        chat_id = update.message.chat_id
        
        if chat_id < 0:
            wmsg = WELCOME_MESSAGE_GROUP
            #chat_id = update.message.from_user.id
        else:
            wmsg = WELCOME_MESSAGE
        self.telegram_send_to_user(chat_id, wmsg.format(
                                    name=update.message.from_user.first_name, 
                                    botname=bot.username,
                                    funny_obs=FUNNY_OBS[randint(0, len(FUNNY_OBS)-1)],
                                    cmds=COMMANDS_HELP,
                                    )
                            )




    @telegram_check_permission_command
    def telegram_command_spawns(self, bot, update):
        try:
            del self.telegram_clients_ignore[str(update.message.chat_id)]
        except:
            pass
        self.telegram_send_to_user(chat_id=update.message.chat_id, msg='Verificando spawns...')
        self.verify(chat_id_request=update.message.chat_id)    
        self.telegram_send_to_user(chat_id=update.message.chat_id, msg='Verificado.')
        time.sleep(0.1)

    def telegram_command_chatid(self, bot, update):
        try:
            del self.telegram_clients_ignore[str(update.message.chat_id)]
        except:
            pass
        self.telegram_send_to_user(chat_id=update.message.chat_id, msg=update.message.chat_id)
        



    @telegram_check_permission_command
    def telegram_command_show_pokemon(self, bot, update, args):
        pokemon_id=args[0]
        try:
            del self.telegram_clients_ignore[str(update.message.chat_id)]
        except:
            pass
        if pokemon_id.lower() == 'level':
            raid_level_request = int(args[1])
            self.telegram_send_to_user(chat_id=update.message.chat_id, msg='Verificando raids level {0}...'.format(raid_level_request))
            self.verify(chat_id_request=update.message.chat_id, raid_level_request=raid_level_request) 
        else:
            self.telegram_send_to_user(chat_id=update.message.chat_id, msg='Verificando pokémon...')
            self.verify(chat_id_request=update.message.chat_id, pokemon_id_request=pokemon_id)    
        self.telegram_send_to_user(chat_id=update.message.chat_id, msg='Verificado.')
        time.sleep(0.1)


    def stop(self):
        self._running = False


    def restart(self):
        self.stop()
        time.sleep(5)
        self._running = False
        self.start()
    
    def telegram_spool_runner(self):
        while True:            
            try: 
                chat_id, msg, photo, preview = self.telegram_spool.pop(0)                           
                self.log.info('[t] Analisando envio para {0}...'.format(chat_id))
                if not chat_id in self.telegram_clients_ignore: 
                    if not chat_id in self.telegram_clients and not str(chat_id) in self.telegram_clients:
                        self.log.info('[t] Não autorizado: {0}'.format(chat_id))
                        try:
                            msg = MESSAGE_CLIENT_DENIED.format(chat_id=chat_id)
                            self.telegram_bot.send_message(chat_id=int(chat_id), text=msg, disable_web_page_preview=not preview) 
                        except telegram.error.BadRequest as bre:
                            if 'not found' in bre.message:
                                self.telegram_clients_ignore[chat_id] = 1
                        except:
                            pass
                    else:
                        time.sleep(0.1)
                        self.log.info('[t] Enviando para {0}...'.format(chat_id))
                        try:
                            if photo:
                                if len(msg) < 200:                           
                                    self.telegram_bot.send_photo(chat_id=int(chat_id), photo=photo, caption=msg)
                                    self.log.info('[t] Enviado.') 
                                else:
                                    final_text = '<a href="{1}">&#8205;</a>{0}'.format(msg, photo)                            
                                    self.telegram_bot.send_message(chat_id=int(chat_id), text=final_text, parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=False)
                                    self.log.info('[t] Enviado.')                                
                            else:
                                self.telegram_bot.send_message(chat_id=int(chat_id), text=msg, disable_web_page_preview=not preview) 
                        except telegram.error.Unauthorized:
                            self.telegram_clients_ignore[chat_id] = 1
                        except telegram.error.BadRequest as bre:
                            if 'not found' in bre.message:
                                self.telegram_clients_ignore[chat_id] = 1
                        except telegram.error.TimedOut or telegram.error.NetworkError or telegram.error.RetryAfter:
                            time.sleep(2)  
                            self.telegram_send_to_user(chat_id, msg, photo,preview,)
                        
            except IndexError: 
                time.sleep(1)  
            time.sleep(0.3)                   
    
    def telegram_send_to_user(self, chat_id, msg, photo=None, preview=True):                   
        self.telegram_spool.append((chat_id, msg, photo,preview,))


    
        
    def send_to_interested(self, latitude, longitude, raid_level=None, is_egg=True, pokemon_id=None, iv=-1, message=None, time_delay=0, photo=None, telegram_chat_id=None):        
        if self.telegram_updater is None:
            self.log.info('''Não é possível enviar via Telegram''')
        else:
            telegram_interested = []              
            if raid_level:
                try:
                    if telegram_chat_id is None:
                        _list = self.telegram_interested_raid[str(raid_level)].iterkeys()
                    else:
                        _list = [telegram_chat_id,]
                    for chat_id in _list:                        
                        if not chat_id in telegram_interested:           
                            self.log.info('L{0} para {1}'.format(raid_level, chat_id))                            
                            self.telegram_send_to_user(chat_id, message, photo=photo)
                            telegram_interested.append(chat_id)
                except KeyError:
                    pass
            if pokemon_id:
                try:                    
                    if telegram_chat_id is None:
                        _list = self.telegram_interested_pokemon[str(pokemon_id)].iterkeys()
                    else:
                        _list = [telegram_chat_id,]
                    for chat_id in _list:
                        if not chat_id in telegram_interested:
                            self.log.info('#{0} para {1}'.format(pokemon_id, chat_id))
                            self.telegram_send_to_user(chat_id, message, photo=photo)
                            telegram_interested.append(chat_id)
                except KeyError:
                    pass        


        
    def get_updates(self, timestamp):
        self.log.info('Busca...')
        now =  int(time.time() * 1000)
        self.last_url_index += 1           
        if self.last_url_index >= len(self.servers_map):
            self.last_url_index = 0                            

        self.log.debug('last_url_index={0}'.format(self.last_url_index))
        self.log.debug('len={0}'.format(len(self.servers_map) ))
        self.running_update = True
        last_raw_data = self.servers_map[self.last_url_index].get_raw_data(timestamp)
        try:
            if self.scan_gyms: 
                _ = last_raw_data['gyms']
            if self.scan_pokemon: 
                _ = last_raw_data['pokemons']
            _ = None
        except:
            self._running = False
            self.running_update = False
            return
        if self.scan_gyms:
            #self.last_scan_gyms.update(last_raw_data['gyms'])
            dict_v = isinstance(last_raw_data['gyms'], dict)  
            for g in last_raw_data['gyms']:                
                # Há diferença em 'gyms' entre versões antigas e novas do RocketMap
                if dict_v:                    
                    gym = last_raw_data['gyms'][g] 
                    gym_id = g
                else:
                    gym = g
                    gym_id = gym['gym_id']  
                if not gym_id in self.last_scan_gyms:
                    self.last_scan_gyms[gym_id] = gym     
                    self.last_scan_gyms[gym_id]['gym_updated'] = True  
                if  gym['last_scanned'] > self.last_scan_gyms[gym_id]['last_scanned']:
                    self.last_scan_gyms[gym_id].update(gym)
                    self.last_scan_gyms[gym_id]['gym_updated'] = True  
                
        if self.scan_pokemon:
            
            if isinstance(last_raw_data['pokemons'], list):
                list_pokemons_scan = last_raw_data['pokemons']
                is_list = True
            else:
                list_pokemons_scan = last_raw_data['pokemons'].iteritems()
                is_list = False
            
            for p in list_pokemons_scan:
                if not is_list:
                    _, pokemon = p
                else:
                    pokemon = p
                if pokemon['disappear_time'] > now:
                    encounter_id = pokemon['encounter_id']
                    latitude = pokemon['latitude']
                    longitude = pokemon['longitude']
                    key = "{0},{1},{2}".format(encounter_id, latitude, longitude)
                    if not key in self.last_scan_pokemon:
                        self.last_scan_pokemon[key] = pokemon   
                        self.last_scan_pokemon[key]['already_notify'] = False
                        self.last_scan_pokemon[key]['iv_updated'] = False
                        self.log_pokemon.debug('Adicionando {0}...'.format(timestamp_to_time(pokemon['disappear_time'])))
                    
                    elif 'individual_attack' not in self.last_scan_pokemon[key] or self.last_scan_pokemon[key]['individual_attack'] is None :
                        self.last_scan_pokemon[key].update(pokemon)
                        self.last_scan_pokemon[key]['iv_updated'] = True
                        self.log_pokemon.debug('Atualizando IV {0}...'.format(timestamp_to_time(pokemon['disappear_time'])))

        self.running_update = False

                
                    
    def clear_disappear(self):
        self.log.info('Limpando...')
        encounters = self.last_scan_pokemon.copy()
        now =  int(time.time() * 1000)
        for key in encounters.iterkeys():
            if encounters[key]['disappear_time'] < now:
                
                self.log_pokemon.debug('Removendo {0}...'.format(timestamp_to_time(encounters[key]['disappear_time'])))
                del self.last_scan_pokemon[key]
        self.log.info('Limpo.')

        
        
    def verify(self, chat_id_request=None, pokemon_id_request=None, raid_level_request=None):
        #raw_data = self.last_raw_data
        now =  int(time.time() * 1000)         
        details = ''
        is_request_client = (chat_id_request is not None)
        is_show_unique_pokemon = (pokemon_id_request is not None)
        #self.log.info(('verify args', chat_id_request, pokemon_id_request,raid_level_request))

        # ========== Gyms ========= #
        if self.scan_gyms:
            self.log_raid.info('Verificando ginásios ({0})...'.format(len(self.last_scan_gyms))) 
            
            for gym_id in self.last_scan_gyms.iterkeys():
                gym = self.last_scan_gyms[gym_id] 
                
                details = ''
                raid_start = gym['raid_start']     
                raid_end = gym['raid_end'] 
                
                raid_level = gym['raid_level'] 
                raid_pokemon_id =  None  
                if 'raid_pokemon_id' in gym and gym['raid_pokemon_id'] != 0:
                    raid_pokemon_id = gym['raid_pokemon_id']

                raid_pokemon_name = None 
                if 'raid_pokemon_name' in gym:
                    raid_pokemon_name = gym['raid_pokemon_name']
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
                

                gym_name = self.gym_details[gym_id]['name'] 
                is_egg = (raid_start > now)
                raid_status_string = (str(raid_start) + str(raid_level) + str(raid_pokemon_id) + str(is_egg))
                last_raid_status_string = None if not 'raid_status_string' in self.gym_details[gym_id] else self.gym_details[gym_id]['raid_status_string']
                gym_updated = (gym['last_scanned'] >= self.gym_details[gym_id]['last_scanned'])
                gym_changed = (last_raid_status_string != raid_status_string)
                gym_without_raid = (raid_end == 0 or raid_end < now or raid_level == 0)
                is_dominated = (self.gym_details[gym_id]['team_id'] != gym['team_id'])
                
                is_client_interested_raid = False
                try:
                    is_requested_level = raid_level_request is not None and int(raid_level_request) == int(raid_level)
                except:
                    is_requested_level = False

                try:
                    is_requested_pokemon = is_show_unique_pokemon and raid_pokemon_id == pokemon_id_request
                except:
                    is_requested_pokemon = False

                has_interested = False
                if is_request_client: 
                    if is_requested_level or is_requested_pokemon:
                        is_client_interested_raid = True
                        has_interested = True                    
                if raid_level_request is None and pokemon_id_request is None:                    
                    if str(raid_level) in self.telegram_interested_raid:
                        has_interested = True
                        if str(chat_id_request) in self.telegram_interested_raid[str(raid_level)]:
                            is_client_interested_raid = True                    
                    if str(raid_pokemon_id) in self.telegram_interested_pokemon:
                        has_interested = True
                        if str(chat_id_request) in self.telegram_interested_pokemon[str(raid_pokemon_id)]:
                            is_client_interested_raid = True

                

                self.log.debug(('is_request_client=', is_request_client))
                self.log.debug(('has_interested=', has_interested))
                self.log.debug(('is_requested_level=', is_requested_level))
                self.log.debug(('raid_level_request=', raid_level_request))
                self.log.debug(('raid_level=', raid_level))
                        
                        
                
                
                if gym_without_raid:
                    self.log_raid.debug('== --  [---]')
                elif has_interested:
                    
                    if is_request_client or gym_changed:                                             
                        time_raid_start = timestamp_to_time(raid_start)
                        time_raid_end = timestamp_to_time(raid_end)  
                        self.log_raid.info('= analisando: {0} (de {1} para {2})'.format(gym_name, 
                                                        timestamp_to_time(self.gym_details[gym_id]['last_scanned']), 
                                                        timestamp_to_time(gym['last_scanned']), 
                                                        ))  
                        team_name = TEAM_LIST[gym['team_id']]
                        icon = ''
                        diff = (abs(gym['last_scanned'] / 1000 - now / 1000) / 60)                            
                        if diff > 5:
                            details = '\nAtraso do mapa: {diff}min.'.format(diff=diff)
                        if is_egg:
                            ''' Raid não começou '''
                            self.log_raid.info('== L{0} = [---] (start: {1})'.format(raid_level, time_raid_start))
                            msg = NOTIFICATION_RAID_EGG_FORMAT
                            icon = RAID_EGG_ICONS[int(raid_level)]
                        else:
                            if raid_pokemon_id is None:
                                ''' Mapa Atrasado '''
                                self.log_raid.info('== L{0} = [{1}] (end: {2}) bot atrasado'.format(raid_level, '????', time_raid_end))
                                
                                msg = NOTIFICATION_RAID_HATCH_LAZY_FORMAT
                                
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
                        if not is_request_client:                   
                            self.send_to_interested(latitude=latitude, longitude=longitude, raid_level=raid_level, pokemon_id=raid_pokemon_id, message=msg, photo=photo)
                        else:
                            if is_client_interested_raid:
                                self.telegram_send_to_user(chat_id_request, msg, photo=photo)

                if gym_updated:
                    if chat_id_request is None:
                        self.gym_details[gym_id].update(gym) 
                        self.gym_details[gym_id]['raid_status_string'] = raid_status_string
                        


        if raid_level_request is None and self.scan_pokemon:
            self.log_pokemon.info('Verificando pokémon ({0})...'.format(len(self.last_scan_pokemon))) 
            poke_counter = 0

            for key in self.last_scan_pokemon.iterkeys():                
                pokemon = self.last_scan_pokemon[key]
                disappear_time = pokemon['disappear_time']
                
                if disappear_time - 15 > now:
                    encounter_id = pokemon['encounter_id']
                    pokemon_id = pokemon['pokemon_id']
                    pokemon_name = pokemon['pokemon_name'] 
                    latitude = pokemon['latitude']
                    longitude = pokemon['longitude'] 
                    already_notify = pokemon['already_notify']
                    iv_changed = 'iv_changed' in pokemon and pokemon['iv_changed']                          

                    move_list = ''
                    try:
                        move_1=self.MOVES_LIST[str(gym['move_1'])]['name']
                        move_2=self.MOVES_LIST[str(gym['move_2'])]['name']
                        move_list = 'Moves: {0} / {1}'.format(move_1, move_2)
                    except:
                        pass
                       
                                    
                    key = "{0},{1},{2}".format(encounter_id, latitude, longitude)
                    
                    client_has_interested = False
                    if pokemon_id_request is None:
                        try:
                            client_has_interested = str(chat_id_request) in self.telegram_interested_pokemon[str(pokemon_id)]
                        except: 
                            pass
                    elif str(pokemon_id_request) == str(pokemon_id) or str(pokemon_id_request).lower() == pokemon_name.lower() :
                        client_has_interested = True
                        
                    if not already_notify or client_has_interested or (chat_id_request is None and iv_changed):                        
                        self.log_pokemon.debug(pokemon_name + ' apareceu') 
                        try:
                            gender = GENDER_LIST[pokemon['gender']]
                        except:
                            gender = ''
                        poke_counter += 1
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
                        
                        if pokemon_id in RARE_LIST:
                            no_cache = True
                        details = '{0}\n{1}'.format(details, get_address(latitude, longitude, self.googlemaps_api_key,no_cache=no_cache, force=False))
                        disappear_time_str = timestamp_to_time(disappear_time)
                        msg = NOTIFICATION_WILD_FORMAT.format(**locals())
                        icon = POKEMON_ICON.format(pokemon_id=pokemon_id)
                        photo = POKEMON_THUMBNAIL_MAP_URL.format(icon=icon, latitude=latitude, longitude=longitude, googlemaps_api_key=self.googlemaps_api_key)           
                        if not is_request_client:
                            self.send_to_interested(latitude=latitude, longitude=longitude, pokemon_id=pokemon_id, message=msg, iv=iv, photo=photo)
                            self.last_scan_pokemon[key]['already_notify'] = True
                            self.last_scan_pokemon[key]['iv_changed'] = False
                            
                        else:        
                            if client_has_interested:                                    
                                self.telegram_send_to_user(chat_id_request, msg, photo=photo)

            if not is_request_client:
                len_storage = len(self.last_scan_pokemon)
                self.log_pokemon.info('Novos: {0}; Armazenados: {1}'.format(
                                    poke_counter, 
                                    len_storage))           
                     

    
    def run(self):
        c = 0   
        self.running_update = False
        first = True
        timestamp = 0
        thread.start_new_thread(self.telegram_spool_runner, tuple() )
        count_errors = 0
        for chat_id in self.telegram_clients:
            self.telegram_send_to_user(chat_id, 'O robô foi reiniciado.')

        while self._running:
            c += 1
            try:
                if not first and self.scan_update <= 5:
                    timestamp = int(time.time())
                #if not self.running_update:
                self.get_updates(timestamp,)
                
            except Exception as e:
                try:
                    traceback.print_exc()
                    count_errors += 1
                except:
                    pass 
            first = False
            #if not self.running_update:
            self.verify()  

            self.log.info('Pause')
            time.sleep(self.scan_update+4)    
               
            if c > 30:
                c = 0
                self.clear_disappear()
                time.sleep(self.scan_update - 1)
                self.running_update = False
            else:
                time.sleep(self.scan_update)
            if count_errors > 5:
                self._running = False
            
            
if __name__ == "__main__": 
    try:
        import run
    except: 
        traceback.print_exc()

