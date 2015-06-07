#!/usr/bin/env python

import os
import re
import csv
import json
import glob
import errno
import requests
from urlparse import urlparse
import lxml.html

# create data directory (when missing)

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  '..', 'data', 'dealerfire.com'))

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
        if row['site_vendor'] == 'dealerfire.com' and int(row['status_code']) == 200:
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
        map_html='http://{0}/contact-us'.format(url)
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
        txt = els[0].text_content()
        txt = txt.strip()
        txt = re.sub('\s+', ' ', txt)
        return txt
    else:
        return ''

def get_value(el):
    return get_text(el, 'value') or el.text_content()

def get_lat_lng(text):
    lat, lng = text.split(',')
    lat = lat.replace('[', '').replace('Geo:', '').strip()
    lng = lng.replace(']', '').strip()
    return (lat, lng)

file_names=glob.glob(os.path.join(directory_name, '*.html'))

combined_name=os.path.join(os.path.dirname(directory_name), 'dealerfire.json')

dealers = []

for file_name in file_names:
    with open(file_name, 'r') as fd:
        url = os.path.splitext(os.path.basename(file_name))[0]
        text = fd.read()
        if not '.dealerfire.com' in text:
            print 'Dealer %s has moved on ...' % url
            continue
        try:
            html = lxml.html.document_fromstring(text)
            data = {'url': url, 'address': {}, 'geo': {}, 'departments': []}
            for info in html.find_class('dealer-info'):
                fail = True
                for meta in info.iter('meta'):
                    itemprop = meta.get('itemprop')
                    content  = meta.get('content')
                    if itemprop is not None and len(itemprop) > 0:
                        fail = False
                        if itemprop == 'name':
                            if itemprop not in data:
                                data[itemprop] = content
                        elif itemprop == 'email':
                            data[itemprop] = content
                        elif itemprop == 'telephone':
                            data[itemprop] = content
                        elif itemprop == 'streetAddress':
                            data['address'][itemprop] = content
                        elif itemprop == 'postalCode':
                            data['address'][itemprop] = content
                        elif itemprop == 'addressLocality':
                            data['address'][itemprop] = content
                        elif itemprop == 'addressRegion':
                            data['address'][itemprop] = content
                        elif itemprop == 'addressCountry':
                            data['address'][itemprop] = content
                        elif itemprop == 'latitude':
                            data['geo'][itemprop] = content
                        elif itemprop == 'longitude':
                            data['geo'][itemprop] = content
                if fail:
                    data['name'] = get_text(info, 'dealer-name')
                    for dept in info.find_class('main-dep'):
                        city_state_zip = get_text(dept, 'dealer-city')
                        city, state_zip = city_state_zip.split(',')
                        state, zip_code = state_zip.strip().split(' ')
                        data['address'] = {}
                        data['address']['street_address'] = get_text(dept, 'dealer-location')
                        data['address']['locality']       = city
                        data['address']['region']         = state
                        data['address']['postal_code']    = zip_code
                        latlng = get_text(dept, 'dealer-latlng')
                        if latlng:
                            lat, lng = get_lat_lng(latlng)
                            data['geo'] = {'latitude': lat, 'longitude': lng }
                        break
                    for cat in info.find_class('cat'):
                        department = {}
                        department['name'] = get_text(cat, 'dealer-department-name')
                        department['telephone'] = get_text(cat, 'dealer-phone')
                        for box in cat.find_class('hours-box'):
                            hours = []
                            department['hours'] = hours
                            for group in box.find_class('group'):
                                hour = {}
                                hour['days'] = get_text(group, 'days')
                                hour['hours'] = get_text(group, 'hours')
                                hours.append(hour)
                            break
                        data['departments'].append(department)
                else:
                    for dept in info.find_class('department'):
                        department = {}
                        hours = []
                        some = False
                        for meta in dept.iter('meta'):
                            itemprop = meta.get('itemprop')
                            content  = meta.get('content')
                            if itemprop is not None and len(itemprop) > 0:
                                if itemprop == 'name':
                                    department[itemprop] = content
                                    some = True
                                elif itemprop == 'openingHours':
                                    hours.append(content)
                                    some = True
                        if some:
                            department['hours'] = hours
                            data['departments'].append(department)
                break
            dealers.append(data)
        except ValueError, e:
            pass

with open(combined_name, 'wb') as fd:
    json.dump(list(dealers), fd)

