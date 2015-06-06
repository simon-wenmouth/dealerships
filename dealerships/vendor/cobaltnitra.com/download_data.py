#!/usr/bin/env python

import os
import csv
import json
import glob
import errno
import requests
from urlparse import urlparse
from lxml import etree, objectify

# create data directory (when missing)

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  '..', 'data', 'cobaltnitra.com'))

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
        if row['site_vendor'] == 'cobaltnitra.com' and int(row['status_code']) == 200:
            url = row['url']
            uri = urlparse(url)
            urls.append(uri.hostname)

# download the data

referer='http://{0}/'

headers={
    'Accept': '*/*',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
}

for url in urls:
    file_name=os.path.join(directory_name, url + '.xml')
    if not os.path.exists(file_name):
        try:
            site_xml='http://{0}/xml/site.xml?output=xml&_=1433555683653'.format(url)
            headers['Referer'] = referer.format(url)
            response = requests.get(site_xml, stream=True, timeout=5, headers=headers)
            response.raise_for_status()
            with open(file_name, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=1024):
                    fd.write(chunk)
        except requests.exceptions.Timeout:
            print ("Timeout: %s" % site_xml)
        except requests.exceptions.HTTPError, e:
            print ("HTTP Error: %s [%d]" % (site_xml, e.response.status_code))
            print e

# combine the XML into a single JSON file

def explode(element):
    data = {}
    if element.text is not None:
        text = element.text.strip()
        if len(text) > 0:
            data['@text'] = element.text
    for name, value in element.attrib.iteritems():
        data[name] = value
    for child in element.iterchildren():
        rest = explode(child)
        if child.tag in data:
            item = data[child.tag]
            if isinstance(item, list):
                item.append(rest)
            else:
                data[child.tag] = [item, rest]
        else:
            data[child.tag] = rest
    if len(data) == 0:
        return None
    if len(data) == 1 and '@text' in data:
        return data['@text']
    return data

file_names=glob.glob(os.path.join(directory_name, '*.xml'))

combined_name=os.path.join(os.path.dirname(directory_name), 'cobaltnitra.json')

dealers = []

for file_name in file_names:
    with open(file_name, 'r') as fd:
        xml = fd.read()
        try:
            tree = objectify.fromstring(xml)
            dealers.append(explode(tree))
        except etree.XMLSyntaxError:
            print 'not xml %s' % file_name

with open(combined_name, 'wb') as fd:
    json.dump(list(dealers), fd)

