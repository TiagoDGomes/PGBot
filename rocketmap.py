# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import json
import logging
import thread
import threading
import time
import traceback
from random import randint

import requests
import telegram
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

from constants import *
from googleapi import get_address, get_url
from servermap import ServerMap
from util import (datetime_from_utc_to_local, load_from_file, save_to_file,
                  timestamp_to_time)








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
                            main_group=[],
                            min_iv=90,
                            always_full_address=False,
                            ignore_first_scan=True,
                            ):
        super(RocketMapBot, self).__init__()
        self.ignore_first_scan = ignore_first_scan
        self.count_first_scan = 1
        self.always_full_address = always_full_address
        self.min_iv = min_iv
        self.main_group = main_group
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
        self.gym_details = load_from_file('gym_details.json', {})
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
            self.telegram_interested_iv = load_from_file('telegram_interested_iv.json', {'clients':{}, 'iv':{}, })
            self.telegram_clients = load_from_file('telegram_clients.json', {})
            self.telegram_dispatcher = self.telegram_updater.dispatcher
            self.telegram_dispatcher.add_handler(CommandHandler('spawns', self.telegram_command_spawns))
            self.telegram_dispatcher.add_handler(CommandHandler('show', self.telegram_command_show_pokemon, pass_args=True))
            self.telegram_dispatcher.add_handler(CommandHandler('start', self.telegram_command_start))
            self.telegram_clients_ignore = {}
            self.telegram_dispatcher.add_handler(CommandHandler('chatid', self.telegram_command_chatid))
            self.telegram_dispatcher.add_handler(CommandHandler('gyms', self.telegram_command_gyms, pass_args=True))
            self.telegram_dispatcher.add_handler(CommandHandler('add', self.telegram_command_add_pokemon_notify, pass_args=True))
            self.telegram_dispatcher.add_handler(CommandHandler('remove', self.telegram_command_remove_pokemon_notify, pass_args=True))
            self.telegram_dispatcher.add_handler(CommandHandler('export', self.telegram_command_export))
            self.telegram_dispatcher.add_handler(CommandHandler('iv', self.telegram_command_iv_notify,pass_args=True))
            self.telegram_dispatcher.add_handler(MessageHandler((Filters.command | Filters.text), self.telegram_get_message))
            self.telegram_dispatcher.add_handler(MessageHandler((Filters.location), self.telegram_get_location))
            self.telegram_dispatcher.add_handler(CallbackQueryHandler(self.telegram_button_click))
            '''
            self.telegram_dispatcher.add_handler(CommandHandler('remove', self.command_remove_pokemon_notify, pass_args=True))
            self.telegram_dispatcher.add_handler(CommandHandler('addraid', self.command_add_raid_notify, pass_args=True))
            self.telegram_dispatcher.add_handler(CommandHandler('removeraid', self.command_remove_raid_notify, pass_args=True))
            self.telegram_dispatcher.add_handler(CommandHandler('delete', self.command_remove_pokemon_notify, pass_args=True))
            self.telegram_dispatcher.add_handler(CommandHandler('stats', self.command_stats, pass_args=True))
            self.telegram_dispatcher.add_handler(CommandHandler('rares', self.command_rares))
            self.telegram_dispatcher.add_handler(CommandHandler('list', self.command_list))
            self.telegram_dispatcher.add_handler(CommandHandler('clear', self.command_clear))
            self.telegram_dispatcher.add_handler(CommandHandler('notifygymchange', self.command_gym_change))
            self.telegram_dispatcher.add_handler(CommandHandler('dontnotifygymchange', self.command_not_gym_change))
            self.telegram_dispatcher.add_handler(CommandHandler('notifygymcpchange', self.command_gym_cp_change))
            self.telegram_dispatcher.add_handler(CommandHandler('dontnotifygymcpchange', self.command_not_gym_cp_change))
            self.telegram_dispatcher.add_handler(CommandHandler('limpar', self.command_clear))
            self.telegram_dispatcher.add_handler(CommandHandler('save', self.command_save))
            self.telegram_dispatcher.add_handler(CallbackQueryHandler(self.button_click))
            self.telegram_dispatcher.add_handler(MessageHandler([Filters.command, Filters.text], self.get_message))'''
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
                chat_id = update.message.chat_id
                if not chat_id in self.main_group:
                    if not str(chat_id) in self.telegram_clients:
                        try:
                            query = update.callback_query
                            chat_id = str(query.message.chat_id)
                            if not chat_id in self.telegram_clients:
                                authorized = False
                        except:
                            authorized = False
            except AttributeError:
                pass
            if authorized:
                function(*args, **kwargs)
            else:
                msg = MESSAGE_CLIENT_DENIED.format(chat_id)
                bot.send_message(chat_id=chat_id, text=msg)
                #self.log.error(msg)
        return check


    @telegram_check_permission_command
    def telegram_command_export(self, bot, update):
        m = self._get_message_from_update(update)
        if m.chat_id < 0:
            chat_id = m.from_user.id
        else:
            chat_id = m.chat_id
        export = {'pokemon':[], 'raid': [], 'chat_id': chat_id}
        for pokemon in self.telegram_interested_pokemon.iterkeys():
            self.log.info(('pokemon', pokemon))
            if str(chat_id) in self.telegram_interested_pokemon[pokemon]:
                export['pokemon'].append(pokemon)
                
        for raid in self.telegram_interested_raid.iterkeys():
            self.log.info(('raid', raid))
            if str(chat_id) in self.telegram_interested_raid[raid]:
                export['raid'].append(raid)
                
        self.telegram_send_to_user(chat_id, json.dumps(export))    


    @telegram_check_permission_command
    def telegram_command_start(self, bot, update):
        global WELCOME_MESSAGE, WELCOME_MESSAGE_GROUP
        #print WELCOME_MESSAGE
        chat_id = update.message.chat_id
        self.telegram_unlock_chat_id(chat_id)
        if chat_id < 0:
            wmsg = WELCOME_MESSAGE_GROUP
            user_chat_id = update.message.from_user.id
            user_name = update.message.from_user.username
            #self.telegram_clients[str(chat_id)][user_chat_id] = {'username': user_name, 'chat_id': user_chat_id}
            self.telegram_clients[str(user_chat_id)] = {'username': user_name, 'chat_id': user_chat_id}
            save_to_file('telegram_clients.json',self.telegram_clients,)
        else:
            wmsg = WELCOME_MESSAGE
        self.telegram_send_to_user(chat_id, wmsg.format(
                                    name=update.message.from_user.first_name, 
                                    botname=bot.username,
                                    funny_obs=FUNNY_OBS[randint(0, len(FUNNY_OBS)-1)],
                                    cmds=COMMANDS_HELP,
                                    ),
                                    parse_mode=telegram.ParseMode.HTML,
                            )

    @telegram_check_permission_command
    def telegram_get_location(self, bot, update):        
        self.log.info('{0}: {1},{2}'.format(
            update.message.from_user.first_name,
            update.message.location.latitude,
            update.message.location.longitude,
            
        ))
        latitude_request = update.message.location.latitude
        longitude_request = update.message.location.longitude
        chat_id = update.message.chat_id
        markers = ''
        msg = ''
        count = 0
        for key in self.last_scan_pokemon.iterkeys():                
            pokemon = self.last_scan_pokemon[key]
            latitude = pokemon['latitude']
            longitude = pokemon['longitude']  
            iv, at, df, st = self._pokemon_stats(pokemon) 
            diff = 0.0017
            swLat = latitude - diff
            neLat = latitude + diff
            swLng = longitude - diff
            neLng = longitude + diff
            client_has_interested = (latitude_request < neLat and \
                                    latitude_request  > swLat) and \
                                    (longitude_request < neLng and \
                                    longitude_request > swLng )
            if client_has_interested:
                count += 1
                if count >=10:
                    label = chr(55+count)
                else:
                    label = count
                #icon = POKEMON_ICON.format(pokemon_id=pokemon['pokemon_id'])
                #markers += MULTI_POKEMON_MARKER.format(**locals()) 
                markers += '&markers=size:mid%7Ccolor:{color}%7Clabel:{label}%7C{latitude},{longitude}'.format(color='0xff0000', label=label, latitude=latitude, longitude=longitude)
                other = ''
                if iv >= 0:
                    other = ' - {0}%'.format(iv)
                msg += '{0} - {1} ⏱ {2} {3}\n'.format(label, pokemon['pokemon_name'], timestamp_to_time(pokemon['disappear_time']), other)

        if markers:
            photo = MULTI_POKEMON_THUMBNAIL_MAP_URL.format(markers=markers, googlemaps_api_key=self.googlemaps_api_key)
            photo = get_url(photo, self.googlemaps_api_key)
            #self.log.info(('photo=', photo))
            self.telegram_send_to_user(chat_id, msg=msg, photo=photo)
        else:
            self.telegram_send_to_user(chat_id, msg='Nenhum pokémon encontrado nesta localização.')

    def get_pokemon_id(self, name):
        pokemon_id = None
        try:
            pokemon_id = int(name)
            return pokemon_id
        except: pass
        pokemon_list = [x.lower() for x in POKEMON_LIST]
        if name.lower() in pokemon_list:
            pokemon_id = int(pokemon_list.index(name.lower()))    
        return pokemon_id           
        
    def telegram_button_click(self, bot, update):
        query = update.callback_query 
        msg = 'Escolha inválida.'
        try:
            self.log.info(query.data)
            data_split = query.data.split('|')
            if data_split[0] == 'SHOW':
                msg = query.message.text
                bot.editMessageText(
                    message_id=update.callback_query.message.message_id,
                    chat_id=update.callback_query.message.chat.id,
                    text=msg
                )
                self.telegram_command_show_pokemon(bot, query, data_split[1:])
            elif data_split[0] == 'IV':
                key = data_split[1]
                pokemon = self.last_scan_pokemon[key]
                details = ''
                iv, at, df, st = self._pokemon_stats(pokemon)
                
                if at is not None and df is not None and st is not None :
                    details += '\nIV: {iv}% ({at}/{df}/{st})'.format(iv=iv, at=at, df=df, st=st)
                else:
                    details += '\nIV: ??% (??/??/??)'                                    
                if pokemon['cp'] is not None:
                    details += '\nCP: {0}'.format(pokemon['cp'])
                else:
                    details += '\nCP: ????'
                if pokemon['level'] is not None:
                    details += ' | L{0}'.format( pokemon['level'])
                else:
                    details += ' | L ??'
                details += '\nAtualizado em {0}'.format(timestamp_to_time(time.time()*1000))
                g = pokemon['gender']
                try:
                    pokemon['gender'] = GENDER_LIST[int(g)] 
                except:
                    pass
                if iv < 0:
                    keyboard = [
                        [InlineKeyboardButton("Atualizar novamente",callback_data='IV|{0},{1},{2}'.format(pokemon['encounter_id'], pokemon['latitude'], pokemon['longitude']))],
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                else:
                    reply_markup = None    
                pokemon['details'] = '{0}\n{1}'.format(details, get_address(pokemon['latitude'], pokemon['longitude'], self.googlemaps_api_key,no_cache=True, force=False))
                msg = NOTIFICATION_WILD_FORMAT.format(**pokemon)
                msg = '<a href="{1}">&#8205;</a>{0}'.format(msg, pokemon['photo'])
                try:
                    bot.editMessageText(
                        message_id=update.callback_query.message.message_id,
                        chat_id=update.callback_query.message.chat.id,
                        text=msg,
                        reply_markup=reply_markup,
                        parse_mode=telegram.ParseMode.HTML
                    )
                except:
                    try:
                        bot.editMessageCaption(
                            message_id=update.callback_query.message.message_id,
                            chat_id=update.callback_query.message.chat.id,
                            caption=msg,
                            reply_markup=reply_markup,
                        )
                    except Exception as e:
                        self.log.error(e.message)
                pokemon['gender'] = g

        except Exception as e:
            try: traceback.print_exc()           
            except: self.log.error(e.message)
            msg = 'Erro ao processar o comando: ' + e.message

        


    @telegram_check_permission_command
    def telegram_command_add_pokemon_notify(self, bot, update, args):   
        m = self._get_message_from_update(update)
        chat_id = m.chat_id
        if chat_id < 0:
            details = {}
        else:
            details = {'username': m.from_user.username,'firstname': m.from_user.first_name }           
        poke_name_add = []    
        for pokemon_request in args:
            pokemon_request_comma = pokemon_request.split(',')
            for pokemon_request_c in pokemon_request_comma:
                pokemon_id = self.get_pokemon_id(pokemon_request_c)                
                if not str(pokemon_id) in self.telegram_interested_pokemon:            
                    self.telegram_interested_pokemon[str(pokemon_id)] = {'_details_':{'name': POKEMON_LIST[pokemon_id]}}
                self.telegram_interested_pokemon[str(pokemon_id)][str(chat_id)] = details
                poke_name_add.append(POKEMON_LIST[pokemon_id]) 
        save_to_file('telegram_interested_pokemon.json', self.telegram_interested_pokemon)
        reply_markup = None
        if len(poke_name_add) == 0:
            msg = 'Nenhum pokémon foi inserido.'
        elif len(poke_name_add) == 1:
            msg = '{0} foi adicionado à sua lista de monitorados.'.format(poke_name_add[0])
            keyboard = [
                [InlineKeyboardButton("Onde tem {0}?".format(poke_name_add[0]),callback_data='SHOW|{0}'.format(pokemon_id))],
            ]                                    
            reply_markup = InlineKeyboardMarkup(keyboard)  
        elif len(poke_name_add) <= 5:
            msg = '{0} foram adicionados à sua lista de monitorados.'.format(', '.join(poke_name_add))
        else:
            msg = '{0} pokémon foram adicionados à sua lista de monitorados.'.format(len(poke_name_add))
        self.telegram_send_to_user(chat_id, msg, reply_markup=reply_markup)
    


    @telegram_check_permission_command
    def telegram_command_iv_notify(self, bot, update, args):   
        m = self._get_message_from_update(update)
        chat_id = m.chat_id        
        iv = int(args[0])
        if iv >= self.min_iv:
            self.telegram_interested_iv['clients'][str(chat_id)] = iv
            save_to_file('telegram_interested_iv.json', self.telegram_interested_iv)
            self.telegram_send_to_user(chat_id, 'Pokémon com IV maior que {0} serão monitorados para você.'.format(iv), )
        else:
            self.telegram_send_to_user(chat_id, 'Somente pokémon com IV maior que 90 serão monitorados.', )
                

        
    @telegram_check_permission_command
    def telegram_command_remove_pokemon_notify(self, bot, update, args):        
        m = self._get_message_from_update(update)
        pokemon_id = self.get_pokemon_id(args[0])
        chat_id = m.chat_id
        try:
            del self.telegram_interested_pokemon[str(pokemon_id)][str(chat_id)]
            save_to_file('telegram_interested_pokemon.json', self.telegram_interested_pokemon)
            self.telegram_send_to_user(chat_id, '{0} removido da sua lista de monitorados.'.format(POKEMON_LIST[pokemon_id]))
        except KeyError:
            self.telegram_send_to_user(chat_id, '{0} não estava sendo monitorado.'.format(POKEMON_LIST[pokemon_id]))
        


    @telegram_check_permission_command
    def telegram_get_message(self, bot, update):
        m = self._get_message_from_update(update)
        text = m.text
        chat_id = m.chat_id
        try:
            self.log.info('{0}: {1}'.format(
                m.from_user.first_name,
                text,
            ))            
        except AttributeError:
            self.log.info('{0}: {1}'.format( 
                chat_id,
                text,
            ))            
        
        try:
            command = [x.upper() for x in text.split(' ')]
            try:
                command1 = command[1]
            except:
                command1 = ''
            if command[0] == 'MOSTRE':                
                self.telegram_command_show_pokemon(bot, update, command[1:])                          
            elif command[0] in MESSAGE_HI_LIST:
                self.telegram_send_to_user(chat_id, MESSAGE_HI_RESPONSE_LIST[randint(0, len(MESSAGE_HI_RESPONSE_LIST)-1)] )                    
            else:
                self.telegram_send_to_user(chat_id, DONT_KNOW_LIST[randint(0, len(DONT_KNOW_LIST)-1)])                    
        except Exception as e:
            self.telegram_send_to_user(chat_id, 'Buguei.\n{0}'.format(e.message))
            traceback.print_exc()


    @telegram_check_permission_command
    def telegram_command_spawns(self, bot, update):
        m = self._get_message_from_update(update)
        self.telegram_unlock_chat_id(m.chat_id)
        self.telegram_send_to_user(chat_id=m.chat_id, msg='Verificando spawns...')
        self.verify(chat_id_request=m.chat_id)    
        self.telegram_send_to_user(chat_id=m.chat_id, msg='Verificado.')
        time.sleep(0.1)

    def telegram_command_chatid(self, bot, update):
        m = self._get_message_from_update(update)
        self.telegram_unlock_chat_id(m.chat_id)
        self.telegram_send_to_user(chat_id=m.chat_id, msg=m.chat_id)
        

    def _get_message_from_update(self, update):
        try:
            _ = update.message.chat_id
            return update.message
        except AttributeError:
            try:            
                _ = update.channel_post.chat_id
                return update.channel_post
            except:
                pass
        return None
            
    def telegram_unlock_chat_id(self, chat_id):
        try:
            del self.telegram_clients_ignore[str(chat_id)]
        except:
            pass
        try:
            del self.telegram_clients_ignore[chat_id]
        except:
            pass

    @telegram_check_permission_command
    def telegram_command_show_pokemon(self, bot, update, args):
        m = self._get_message_from_update(update)
        chat_id =  m.chat_id        
        try:
            pokemon_id=args[0]
        except IndexError:
            self.telegram_send_to_user(chat_id=chat_id, msg='O comando está errado. Veja /start.')
            return
        self.telegram_unlock_chat_id(chat_id)
        if pokemon_id.lower() == 'level':
            raid_level_request = int(args[1])
            self.telegram_send_to_user(chat_id=chat_id, msg='Verificando raids level {0}...'.format(raid_level_request))
            self.verify(chat_id_request=chat_id, raid_level_request=raid_level_request) 
        else:
            self.telegram_send_to_user(chat_id=chat_id, msg='Verificando pokémon...')
            self.verify(chat_id_request=chat_id, pokemon_id_request=pokemon_id)    
        self.telegram_send_to_user(chat_id=chat_id, msg='Verificado.')
        time.sleep(0.1)

    @telegram_check_permission_command
    def telegram_command_gyms(self, bot, update, args):
        self.telegram_send_to_user(chat_id=update.message.chat_id, msg='Comando não implementado.')
        


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
                chat_id, msg, photo, preview, parse_mode, reply_markup = self.telegram_spool.pop(0)                           
                if not chat_id in self.telegram_clients_ignore and not '_' in str(chat_id): 
                    if not chat_id in self.telegram_clients and not str(chat_id) in self.telegram_clients and not chat_id in self.main_group:
                        self.log.info('[t] Não permitido envio para: {0}'.format(chat_id))
                        try:
                            msg = MESSAGE_CLIENT_DENIED.format(chat_id=chat_id)
                            #self.telegram_bot.send_message(chat_id=chat_id, text=msg, disable_web_page_preview=not preview, parse_mode=parse_mode, reply_markup=reply_markup)                                                         
                        except:
                            pass
                        self.telegram_clients_ignore[chat_id] = 1
                    else:
                        time.sleep(0.1)
                        self.log.info('[t] Enviando para {0}...'.format(chat_id))
                        try:
                            if photo:
                                final_text = '<a href="{1}">&#8205;</a>{0}'.format(msg, photo)                            
                                self.telegram_bot.send_message(chat_id=chat_id, text=final_text, parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=False, reply_markup=reply_markup)
                                self.log.info('[t] Enviado.')                                
                            else:
                                self.telegram_bot.send_message(chat_id=chat_id, text=msg, disable_web_page_preview=not preview, parse_mode=parse_mode, reply_markup=reply_markup) 
                        except telegram.error.Unauthorized:
                            self.telegram_clients_ignore[chat_id] = 1
                        except telegram.error.TimedOut:
                            pass
                        except telegram.error.BadRequest as bre:
                            if 'not found' in bre.message:
                                self.telegram_clients_ignore[chat_id] = 1
                        except Exception as e:
                            self.log.error('[t] Erro ao enviar para {0}...'.format(chat_id))     
                            self.log.error(e.message) 
                            time.sleep(2)  
                            #self.telegram_send_to_user(chat_id, msg, photo,preview ,parse_mode, reply_markup=reply_markup)
                        
            except IndexError: 
                time.sleep(0.5)  
            time.sleep(0.1)                   
    
    def telegram_send_to_user(self, chat_id, msg, photo=None, preview=True, parse_mode=None, reply_markup=None):                   
        self.telegram_spool.append((chat_id, msg, photo,preview,parse_mode,reply_markup))


    def telegram_has_interested(self, pokemon_id=None, raid_level=None, iv=None):
        if pokemon_id is not None:
            if pokemon_id in self.telegram_interested_pokemon:                
                return len(self.telegram_interested_pokemon[pokemon_id]) >= 2
            if str(pokemon_id) in self.telegram_interested_pokemon:
                return len(self.telegram_interested_pokemon[str(pokemon_id)]) >= 2
            
        if raid_level is not None:
            if raid_level in self.telegram_interested_raid:
                return len(self.telegram_interested_raid[raid_level]) > 2
            if str(raid_level) in self.telegram_interested_raid:
                return len(self.telegram_interested_raid[str(raid_level)]) > 2
        if iv is not None:
            for c in self.telegram_interested_iv['clients'].iterkeys():
                if iv > self.telegram_interested_iv['clients'][c]:
                    return True
        return False
        
    def send_to_interested(self, latitude, longitude, raid_level=None, is_egg=True, pokemon_id=None, iv=-1, message=None, time_delay=0, photo=None, telegram_chat_id=None, encounter_id=None):        
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
                        if not chat_id in telegram_interested and not '_' in str(chat_id):                                       
                            self.log.info('L{0} para {1}'.format(raid_level, chat_id))                            
                            self.telegram_send_to_user(chat_id, message, photo=photo)
                            telegram_interested.append(chat_id)
                except KeyError:
                    pass
                
            if pokemon_id:
                try:                     
                    keyboard = [
                        [InlineKeyboardButton("Atualizar",callback_data='IV|{0},{1},{2}'.format(encounter_id, latitude, longitude))],
                    ]                     
                    if telegram_chat_id is None:
                        _list = self.telegram_interested_pokemon[str(pokemon_id)].iterkeys()
                    else:
                        _list = [telegram_chat_id,]
                    for chat_id in _list:
                        if not chat_id in telegram_interested and not '_' in str(chat_id):
                            if iv < 0 and raid_level is None:
                                reply_markup = InlineKeyboardMarkup(keyboard) 
                            else:
                                reply_markup = None
                            self.log.info('#{0} para {1}'.format(pokemon_id, chat_id))
                            self.telegram_send_to_user(chat_id, message, photo=photo, reply_markup=reply_markup)
                            telegram_interested.append(chat_id)
                except KeyError:
                    pass        
            
            for chat_id in self.telegram_interested_iv['clients'].iterkeys():

                if not chat_id in telegram_interested:
                    iv_client = self.telegram_interested_iv['clients'][str(chat_id)]
                    if iv_client <= iv:                     
                        self.log.info('#{0} para {1}'.format(pokemon_id, chat_id))
                        self.telegram_send_to_user(chat_id, message, photo=photo)
                        telegram_interested.append(chat_id)


        
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
                        self.last_scan_pokemon[key]['iv_changed'] = False
                        self.last_scan_pokemon[key]['is_notified_iv'] = False
                        self.log_pokemon.debug('Adicionando {0}...'.format(timestamp_to_time(pokemon['disappear_time'])))
                    
                    #elif 'individual_attack' in self.last_scan_pokemon[key] and self.last_scan_pokemon[key]['individual_attack'] is not None :
                    elif 'individual_attack' in pokemon and pokemon['individual_attack'] is not None :
                        if not self.last_scan_pokemon[key]['is_notified_iv']:
                            self.last_scan_pokemon[key].update(pokemon)
                            self.last_scan_pokemon[key]['iv_changed'] = True                        
                            self.log_pokemon.info('Atualizando IV {0}...'.format(timestamp_to_time(pokemon['disappear_time'])))

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

        
        
    def verify(self, chat_id_request=None, pokemon_id_request=None, raid_level_request=None, latitude_request=None, longitude_request=None,):
        #raw_data = self.last_raw_data
        NEED_IGNORE = False
        if self.ignore_first_scan:
            if self.count_first_scan <= len(self.url_list) :
                self.log.info('''Ignorando primeiros scans''')
                self.count_first_scan += 1 
                NEED_IGNORE = True

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
                if not gym_id in self.gym_details:
                    self.gym_details[gym_id] = {}
                    self.gym_details[gym_id].update(gym)
                    save_to_file('gym_details.json', self.gym_details)
                if self.gym_details[gym_id]['name'] is None:
                    self.gym_details[gym_id]['name'] = get_address(gym['latitude'], gym['longitude'], self.googlemaps_api_key)
                    self.gym_details[gym_id]['generic_name'] = True
                if 'generic_name' in self.gym_details[gym_id] and self.gym_details[gym_id]['generic_name'] and gym['name'] is not None:
                    self.gym_details[gym_id]['name'] = gym['name']
                    self.gym_details[gym_id]['generic_name'] = False
                latitude = self.gym_details[gym_id]['latitude']
                longitude = self.gym_details[gym_id]['longitude']
                

                gym_name = self.gym_details[gym_id]['name'] 
                is_egg = raid_start > now
                is_normal = raid_end < now
                is_raid = not is_egg and not is_normal

                    
                    
                
                raid_status_string = str(is_egg) + str(is_normal) + str(is_raid)
                last_raid_status_string = None if not 'raid_status_string' in self.gym_details[gym_id] else self.gym_details[gym_id]['raid_status_string']
                gym_updated = (gym['last_scanned'] >= self.gym_details[gym_id]['last_scanned'])
                gym_changed = (last_raid_status_string != raid_status_string) or (is_raid and raid_pokemon_id != self.gym_details[gym_id]['raid_pokemon_id'])
                
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
                        if is_egg and raid_pokemon_id is None:
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
     
                        if not is_request_client and not NEED_IGNORE:                   
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
                    is_notified_iv = 'is_notified_iv' in pokemon and pokemon['is_notified_iv']                          

                    move_list = ''
                    try:
                        move_1=self.MOVES_LIST[str(gym['move_1'])]['name']
                        move_2=self.MOVES_LIST[str(gym['move_2'])]['name']
                        move_list = 'Moves: {0} / {1}'.format(move_1, move_2)
                    except:
                        pass
                       
                                    
                    key = "{0},{1},{2}".format(encounter_id, latitude, longitude)
                    
                    client_has_interested = False
                    if latitude_request and longitude_request:
                        diff = 0.001
                        swLat = latitude - diff
                        neLat = latitude + diff
                        swLng = longitude - diff
                        neLng = longitude + diff

                        client_has_interested = (latitude_request < neLat and \
                                                latitude_request  > swLat) and \
                                                (longitude_request < neLng and \
                                                longitude_request > swLng )
                    else:    
                        if pokemon_id_request is None:
                            try:
                                client_has_interested = str(chat_id_request) in self.telegram_interested_pokemon[str(pokemon_id)]
                            except: 
                                pass
                             
                        elif str(pokemon_id_request) == str(pokemon_id) or str(pokemon_id_request).lower() == pokemon_name.lower() :
                            client_has_interested = True
     
                    if not already_notify or client_has_interested or (chat_id_request is None and not is_notified_iv):                        
                        self.log_pokemon.debug(pokemon_name + ' apareceu') 
                        try:
                            gender = GENDER_LIST[int(pokemon['gender'])]
                        except:
                            try:
                                gender = GENDER_LIST[pokemon['gender']]
                            except:
                                gender = ''
                        poke_counter += 1
                        iv, at, df, st = self._pokemon_stats(pokemon)
                                              
                        details = ''
                        if at is not None and df is not None and st is not None :
                            details = '{d}\nIV: {iv}% ({at}/{df}/{st})'.format(d=details, iv=iv, at=at, df=df, st=st)                                    
                        if pokemon['cp'] is not None:
                            details = '{0}\nCP: {1}'.format(details, pokemon['cp'])
                        if pokemon['level'] is not None:
                            details = '{0} | L{1}'.format(details, pokemon['level'])
                        
                        no_cache = False
                                              
                        if self.always_full_address or pokemon_id in RARE_LIST or iv > 93:
                            no_cache = True
                        if self.telegram_has_interested(pokemon_id=pokemon_id, iv=iv):
                            no_cache = True
                        details = '{0}\n{1}'.format(details, get_address(latitude, longitude, self.googlemaps_api_key,no_cache=no_cache, force=False))
                        disappear_time_str = timestamp_to_time(disappear_time)
                        pokemon['disappear_time_str'] = disappear_time_str
                        msg = NOTIFICATION_WILD_FORMAT.format(**locals())
                        icon = POKEMON_ICON.format(pokemon_id=pokemon_id)
                        photo = POKEMON_THUMBNAIL_MAP_URL.format(icon=icon, latitude=latitude, longitude=longitude, googlemaps_api_key=self.googlemaps_api_key)           
                        pokemon['photo'] = photo
                        if not is_request_client and not NEED_IGNORE:
                            self.send_to_interested(latitude=latitude, longitude=longitude, pokemon_id=pokemon_id, message=msg, iv=iv, photo=photo, encounter_id=pokemon['encounter_id'])
                            self.last_scan_pokemon[key]['already_notify'] = True
                            self.last_scan_pokemon[key]['iv_changed'] = False     
                            if iv > 0:
                                self.last_scan_pokemon[key]['is_notified_iv'] = True                       
                        else:        
                            if client_has_interested:                                    
                                self.telegram_send_to_user(chat_id_request, msg, photo=photo)

            if not is_request_client:
                len_storage = len(self.last_scan_pokemon)
                self.log_pokemon.info('Novos: {0}; Armazenados: {1}'.format(
                                    poke_counter, 
                                    len_storage))  


    def _pokemon_stats(self, pokemon):
        iv, at, df, st = -1, None, None, None
        if pokemon['individual_attack'] is not None and pokemon['individual_defense'] is not None and pokemon['individual_stamina'] is not None :
            at = pokemon['individual_attack']
            df = pokemon['individual_defense']
            st = pokemon['individual_stamina']
            iv = round(100.0 * (at + df + st) / 45, 1)
        return iv, at, df, st                             
                        
    
    def run(self):
        c = 0   
        self.running_update = False
        first = True
        timestamp = 0
        thread.start_new_thread(self.telegram_spool_runner, tuple() )
        count_errors = 0
        #for chat_id in self.telegram_clients:
        #    self.telegram_send_to_user(chat_id, 'O robô foi reiniciado.')
        
        while True:
            self.log.info('========= INICIANDO =========')
            for m in self.servers_map:
                m.get_home_page()

            while self._running:
                c += 1
                try:
                    if not first and self.scan_update <= 5:
                        timestamp = int(time.time())
                    #if not self.running_update:
                    self.get_updates(timestamp,)
                    
                except:
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
        self
            
            
if __name__ == "__main__": 
    try:
        import run
    except: 
        traceback.print_exc()
