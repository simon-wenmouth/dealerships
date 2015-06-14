#!/usr/bin/env python3

import os
import json
import errno
import requests
from lxml import etree

url='http://www.porsche.com/all/dealer2/usa/externalSearchXml.aspx?geo=42.0301291|-87.68276759999998&lim=1000'

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  '..', 'data', 'porsche'))

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

# covert XML file into JSON

combined_name=os.path.join(os.path.dirname(directory_name), 'porsche.json')

dealers = {}

with open(file_name, 'r') as fd:
    try:
        tree = etree.parse(fd)
        for node in tree.findall('dealer'):
            dealer = {item.tag: item.text for item in node}
            dealer['address'] = {item.tag: item.text for item in node.find('address')}
            details = node.find('details')
            if details is not None:
                dealer['details'] = {item.tag: item.text for item in details}
                for name in ['main', 'sales', 'parts', 'service', 'address']:
                    child = details.find(name)
                    if child is not None:
                        dealer['details'][name] = {item.tag: item.text for item in child}

            dealer_id=dealer['id']
            dealers[dealer_id] = dealer
    except etree.XMLSyntaxError:
        print 'not xml %s' % file_name

with open(combined_name, 'wb') as fd:
    json.dump(list(dealers.values()), fd, sort_keys=True, indent=2)

