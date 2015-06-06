#!/usr/bin/env python

import os
import re
import csv
import json
import glob
import errno
import requests
from urlparse import urlparse

# create data directory (when missing)

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  '..', 'data', 'clickmotive.com'))

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
        if row['site_vendor'] == 'clickmotive.com' and int(row['status_code']) == 200:
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
        map_html='http://{0}/MapLocation.aspx'.format(url)
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

file_names=glob.glob(os.path.join(directory_name, '*.html'))

combined_name=os.path.join(os.path.dirname(directory_name), 'clickmotive.json')

dealers = []

for file_name in file_names:
    with open(file_name, 'r') as fd:
        html = fd.read()
        try:
            char_begin = html.index('CM.customer = {')
            char_end   = html.index('};', char_begin)
            text = html[char_begin+14:char_end+1]
            text = re.sub('([a-zA-z0-9_]+) ?:', ' "\\1":', text)
            vals = json.loads(text)
            vals['url'] = os.path.splitext(os.path.basename(file_name))[0]
            del vals['msve_id']
            del vals['page']
            del vals['isDepartment']
            dealers.append(vals)
        except ValueError, e:
            pass

with open(combined_name, 'wb') as fd:
    json.dump(list(dealers), fd)


