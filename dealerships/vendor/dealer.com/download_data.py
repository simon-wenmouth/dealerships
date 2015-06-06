#!/usr/bin/env python

import os
import csv
import json
import glob
import errno
import requests
from urlparse import urlparse
import lxml.html

# create data directory (when missing)

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  '..', 'data', 'dealer.com'))

try:
    os.makedirs(directory_name)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(directory_name):
        pass
    else:
        raise

# load URLs from site.csv

sites=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  '..', 'data', 'sites.csv'))

urls = []

with open(sites) as fd:
    reader = csv.DictReader(fd)
    for row in reader:
        if row['site_vendor'] == 'dealer.com' and int(row['status_code']) == 200:
            url = row['url']
            uri = urlparse(url)
            urls.append(uri.hostname)

# download the data

referer='http://{0}/'

headers={
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
}

for url in urls:
    file_name=os.path.join(directory_name, url + '.html')
    if not os.path.exists(file_name):
        map_html='http://{0}/dealership/directions.htm'.format(url)
        try:
            headers['Referer'] = referer.format(url)
            response = requests.get(map_html, stream=True, timeout=5, headers=headers)
            response.raise_for_status()
            with open(file_name, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=1024):
                    fd.write(chunk)
        except requests.exceptions.Timeout:
            print ("Timeout: %s" % map_html)
        except requests.exceptions.HTTPError, e:
            print ("HTTP Error: %s [%d]" % (map_html, e.response.status_code))
        except requests.exceptions.ConnectionError:
            print ("Connect Error: %s" % map_html)
        except Exception, e:
            print e

# combine HTML files

def get_text(el, class_name):
    els = el.find_class(class_name)
    if els:
        return els[0].text_content()
    else:
        return ''

def get_value(el):
    return get_text(el, 'value') or el.text_content()

def get_lat_lng(text):
    lat, lng = text.split(',')
    lat = lat.replace('[', '').strip()
    lng = lng.replace(']', '').strip()
    return (lat, lng)

file_names=glob.glob(os.path.join(directory_name, '*.html'))

combined_name=os.path.join(os.path.dirname(directory_name), 'dealer.com.json')

dealers = []

for file_name in file_names:
    with open(file_name, 'r') as fd:
        url = os.path.splitext(os.path.basename(file_name))[0]
        text = fd.read()
        if not 'static.dealer.com' in text:
            print 'Dealer %s has moved on ...' % url
            continue
        try:
            html = lxml.html.document_fromstring(text)
            data = {}
            data['url'] = url
            for vcard in html.find_class('vcard'):
                data['name'] = get_text(vcard, 'org')
                data['tels'] = []
                for tel_el in vcard.find_class('tel'):
                    tel = {}
                    tel['value'] = get_text(tel_el, 'value')
                    tel['type']  = get_text(tel_el, 'type')
                    data['tels'].append(tel)
                for adr in vcard.find_class('adr'):
                    data['address'] = {}
                    data['address']['street_address'] = get_text(adr, 'street-address')
                    data['address']['locality']       = get_text(adr, 'locality')
                    data['address']['region']         = get_text(adr, 'region')
                    data['address']['postal_code']    = get_text(adr, 'postal-code')
                    break
                for geo in vcard.find_class('geo'):
                    data['geo'] = {}
                    for lat_el in geo.find_class('latitude'):
                        for value in lat_el.find_class('value-title'):
                            data['geo']['latitude'] = value.get('title')
                    for lng_el in geo.find_class('longitude'):
                        for value in lng_el.find_class('value-title'):
                            data['geo']['longitude'] = value.get('title')
                break
            for maps in html.find_class('google-map'):
                latlng = maps.get('data-markers-list')
                if latlng:
                    lat, lng = get_lat_lng(latlng)
                    data['geo'] = {'latitude': lat, 'longitude': lng }
            for link in html.iter('link'):
                if link.get('rel') == 'publisher':
                    data['google_plus'] = link.get('href')
#            for meta in html.iter('meta'):
#                name = meta.get('name')
#                if name == 'geo.position' or name == 'ICBM':
#                    latlng = meta.get('content')
#                    if latlng:
#                        lat, lng = get_lat_lng(latlng)
#                        data['geo'] = {'latitude': lat, 'longitude': lng }
            dealers.append(data)
        except ValueError, e:
            pass

with open(combined_name, 'wb') as fd:
    json.dump(list(dealers), fd)

