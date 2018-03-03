# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
import json
import traceback
import logging
from util import load_from_file, save_to_file

addresses = load_from_file('address.json', {})
log_google = logging.getLogger('goog')  

def get_address(latitude, longitude, googlemaps_api_key, force=True, no_cache=False):
    latlng = '{0},{1}'.format(latitude, longitude)
    if latlng in addresses:
        return addresses[latlng]['results'][0]['formatted_address']
    if no_cache:
        try:                    
            url = "https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={api_key}".format(
                lat=latitude,
                lng=longitude,
                api_key=googlemaps_api_key
            )    
            log_google.info('Buscando endereco {0},{1} (Google Maps API)...'.format(latitude, longitude))   
            raw_data = requests.get(url)
            data = json.loads(raw_data.text)                
            log_google.info('Endereco obtido.')   
            if 'results' in data:
                formatted_address = data['results'][0]['formatted_address']
                addresses[latlng] = data
                save_to_file('address.json', addresses)
                return formatted_address
        except:
            traceback.print_exc()
    if force:
        return '[{0},{1}]'.format(latitude, longitude)
    else:
        return ''