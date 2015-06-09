#!/usr/bin/env python

import os
import re
import csv
import json
import glob
import errno
import requests
from urlparse import urlparse #, parse_qs
import lxml.html

# create data directory (when missing)

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  '..', 'data', 'dealeron.com'))

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
        if row['site_vendor'] == 'dealeron.com' and int(row['status_code']) == 200:
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
        map_html='http://{0}/hours.aspx'.format(url)
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

combined_name=os.path.join(os.path.dirname(directory_name), 'dealeron.json')

dealers = []

for file_name in file_names:
    with open(file_name, 'r') as fd:
        url = os.path.splitext(os.path.basename(file_name))[0]
        text = fd.read()
        if not '.dlron.' in text:
            print 'Dealer %s has moved on ...' % url
            continue
        try:
            html = lxml.html.document_fromstring(text)
            data = {'url': url, 'address': {}, 'geo': {}, 'departments': []}
            for meta in html.iter('meta'):
                name    = meta.get('name')
                content = meta.get('content')
                if name is not None:
                    if name == 'geo.position':
                        lat, lng = content.split(',')
                        data['geo']['latitude']  = lat
                        data['geo']['longitude'] = lng
                    elif name == 'geo.placement':
                        data['address']['addressLocality'] = content
                    elif name == 'geo.region':
                        data['address']['addressRegion'] = content
            for div in html.find_class('hours-page'):
                for span in div.iter('span'):
                    itemprop = span.get('itemprop')
                    content  = span.text_content()
                    if itemprop is not None and len(itemprop) > 0 and len(content) > 0:
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
            if not 'streetAddress' in data['address']:
                for address in html.iter('address'):
                    lines = [s.strip() for s in address.text_content().strip().splitlines()]
                    if len(lines) == 2:
                        street_address, city_state_zip = lines
                    elif len(lines) == 3:
                        store_name, street_address, city_state_zip = lines
                    else:
                        continue
                    city, state_zip = city_state_zip.split(',')
                    state, zip_code = state_zip.strip().split(' ')
                    data['address']['streetAddress']   = street_address.strip()
                    data['address']['postalCode']      = zip_code.strip()
                    data['address']['addressLocality'] = city.strip()
                    data['address']['addressRegion']   = state.strip()
                    break
            for table in html.iter('table'):
                names  = {'SalesHours': 'Sales',
                          'PartsHours': 'Parts',
                          'ServiceHours': 'Service',
                          'tblSales': 'Sales',
                          'tblParts': 'Parts',
                          'tblService': 'Service',
                          'tbl_Sales': 'Sales',
                          'tbl_Parts': 'Parts',
                          'tbl_Service': 'Service'}
                pname = table.getparent().get('id')
                tname = table.get('id')
                if names.has_key(pname):
                    name = names[pname]
                elif names.has_key(tname):
                    name = names[tname]
                else:
                    continue
                hours = []
                department = {'name': name, 'hours': hours}
                for tr in table.iter('tr'):
                    bits = []
                    for cell in tr.iter('td'):
                        text = cell.text_content()
                        if text is not None:
                            bits.append(text.strip())
                    if len(bits) == 3:
                        hours.append({'day': bits[0], 'opens': bits[1], 'closes': bits[2]})
                data['departments'].append(department)
            dealers.append(data)
        except ValueError, e:
            print e

with open(combined_name, 'wb') as fd:
    json.dump(list(dealers), fd, sort_keys=True, indent=2)

