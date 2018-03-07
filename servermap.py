# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import logging
import requests
import json
import time
import traceback


class ServerMap(object):
    def __init__(self, url, rm_obj):
        self.rm_obj = rm_obj
        self.url = url
        self.log = logging.getLogger('site') 
        self.host = self.url.replace('http://','').replace('https://','').split('/')[0]
        self.cookies = {}
        self.token = None
        
        
        

    def get_home_page(self):
        self.error_count = 0
        self.cookies = {}
        home_page = self._request(self.url + '/')
        self.method = 'post'     
        
        if home_page.find('Method Not Allowed')>=0 or home_page.find('Bad Request')>=0:
            self.log.info('Esta versao do RocketMap utiliza metodo GET')
            home_page = self._request(self.url + '/', method='get')
            self.method = 'get'   

        try:
            token_string_search="token = '"
            token_start_position = home_page.index(token_string_search) + len(token_string_search)
            token_stop_position = (home_page[token_start_position:]).index("'")
            self.token = home_page[token_start_position:token_start_position+token_stop_position]
        except:
            self.token = '0' 
        
            


    def _request(self, url, data=None, add_headers={}, method='get'):
        h = { 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', 
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language':'pt-BR,pt;q=0.8,en-US;q=0.6,en;q=0.4',
            'Accept': '*/*; q=0.01',
            'Connection':'keep-alive',  
            'Referer': url,
            'Host': self.host,
        }
        
        h.update(add_headers)        
        self.log.debug('cookies a=' + str(self.cookies))
        self.log.info ('Baixando {0}...'.format(url))
        try:
            if method == 'post':
                result = requests.post(url, data=data, cookies=self.cookies, headers=h)
            else:
                result = requests.get(url, data=data, cookies=self.cookies, headers=h)
            self.log.info ('Baixado.')
            cookies = {i.name: i.value for i in list(result.cookies)}
            if result.cookies.get('PHPSESSID') is not None:     
                self.cookies = cookies
                self.log.debug('cookies b=' + str(self.cookies))
            self.log.debug('token={0}'.format(self.token))
        except:
            return ''
        return result.text
    

    def get_raw_data(self, timestamp=0):
        add_headers = {
            'Origin': self.url,
            'Referer': self.url + '/', 
            'X-Requested-With' : 'XMLHttpRequest' ,
            'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',       
        }   
        
        data = {
            'timestamp': timestamp, 
            'pokemon': str(self.rm_obj.scan_pokemon).lower() ,
            'lastpokemon': str(self.rm_obj.scan_pokemon).lower() ,
            'pokestops' : str(self.rm_obj.scan_pokestops).lower(),
            'gyms' : str(self.rm_obj.scan_gyms).lower() ,
            'luredonly' : 'false',
            'scanned' : 'false' ,
            'spawnpoints' : 'false' ,
            'swLat': str(self.rm_obj.swLat),
            'swLng': str(self.rm_obj.swLng),
            'neLat': str(self.rm_obj.neLat),
            'neLng': str(self.rm_obj.neLng), 
            'oSwLat': str(self.rm_obj.swLat),
            'oSwLng': str(self.rm_obj.swLng),
            'oNeLat': str(self.rm_obj.neLat),
            'oNeLng': str(self.rm_obj.neLng), 
            'reids' : '' ,
            #'eids' : '1,2,4,5,7,8,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,60,61,63,64,66,67,69,70,71,72,74,75,77,78,79,84,85,88,92,93,95,96,97,98,99,102,104,105,107,108,109,111,114,116,117,118,119,120,121,123,124,125,126,127,129,132,133,138,140,142,152,153,155,156,158,159,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,177,178,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,223,224,226,227,228,229,230,231,232,233,234,236,238,239,240' ,
            'token': self.token,
            'eids' : '',
        }
        raw_data_url = self.url + '/raw_data'
        count_error = 1
        while not count_error == -1: 
            try:        
                text = self._request(raw_data_url, add_headers=add_headers, data=data, method=self.method)
                raw_data = json.loads(text)
                if 'token' in raw_data and raw_data['token'] != self.token:
                    self.token = raw_data['token']
                self.last_raw_data = raw_data
                count_error = -1
            except Exception as e:
                raw_data = {}
                time.sleep(1)
                traceback.print_exc()
                self.log.error('Falha ao baixar dados do servidor. {0}. Contagem de erros: {1}'.format( e.message, count_error ))
                count_error += 1
                data['timestamp'] = 0
            if count_error == 3:
                self.get_home_page()
            elif count_error == 6:
                break
        return raw_data    