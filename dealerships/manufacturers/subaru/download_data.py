#!/usr/bin/env python

import os
import json
import errno
import requests
from lxml import etree

url='http://www.subaru.com/form/retailer/getmapmarkers/60202/3000/sales/'

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  '..', 'data', 'subaru'))

try:
    os.makedirs(directory_name)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(directory_name):
        pass
    else:
        raise

file_name=os.path.join(directory_name, 'usa.xml')

response = requests.get(url, stream=True)

with open(file_name, 'wb') as fd:
    for chunk in response.iter_content(chunk_size=1024):
        fd.write(chunk)

combined_name=os.path.join(os.path.dirname(directory_name), 'subaru.json')

dealers = {}

with open(file_name, 'r') as fd:
    try:
        tree = etree.parse(fd)
        for marker in tree.findall('marker'):
            dealer = {name: value for name, value in marker.items()}
            dealer_id=dealer['id']
            dealers[dealer_id] = dealer
    except etree.XMLSyntaxError:
        print 'not xml %s' % file_name

with open(combined_name, 'wb') as fd:
    json.dump(list(dealers.values()), fd)

