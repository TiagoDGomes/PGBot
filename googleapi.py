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
urls = load_from_file('urls.json', {})

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
                if len(addresses) % 25 == 0:
                    save_to_file('address.json', addresses)
                return formatted_address
        except:
            traceback.print_exc()
    if force:
        return '[{0},{1}]'.format(latitude, longitude)
    else:
        return ''


def get_url(url, google_api_key, force=True):
    global urls
    if url in urls:
        return urls[url]

    if google_api_key and force:
        log_google.info('usando Google API Shortner ')
        try:                    
            url_api = "https://www.googleapis.com/urlshortener/v1/url?key={key}".format(key=google_api_key)
            post = {'longUrl': url}
            raw_data = requests.post(url_api, json=post)
            data = json.loads(raw_data.text) 
            log_google.info(data)              
            urls[url] = data['id']
            save_to_file('urls.json', urls)
            return data['id']
        except:
            traceback.print_exc()
    if force:
        return url
    else:
        return ''