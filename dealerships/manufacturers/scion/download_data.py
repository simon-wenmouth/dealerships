#!/usr/bin/env python3

import os
import glob
import json
import errno
import requests
from lxml import etree
from zip_code_radius import solver

# create data directory (when missing)

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  '..', 'data', 'scion'))

try:
    os.makedirs(directory_name)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(directory_name):
        pass
    else:
        raise

# download data
# also:
# http://www.toyota.com/ToyotaSite/rest/dealerLocator/locateDealers?brandId=3&zipCode=60202&radius=500

url='http://www.scion.com/scion/pub/service/dealers/locator.do?zipCode={0}&radius={1}&searchType=zipcode'

radius=25

locations=solver.solve(float(radius))

for location in locations:
    file_name=os.path.join(directory_name, location.zip_code + '.xml')
    if not os.path.exists(file_name):
        try:
            response = requests.get(url.format(location.zip_code, radius), stream=True, timeout=5)
            with open(file_name, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=1024):
                    fd.write(chunk)
        except requests.exceptions.Timeout:
            print ("Timeout: %s" % location.zip_code)

# combine XML files

file_names=glob.glob(os.path.join(directory_name, '*.xml'))

combined_name=os.path.join(os.path.dirname(directory_name), 'scion.json')

dealers = {}

for file_name in file_names:
    with open(file_name, 'r') as fd:
        try:
            tree = etree.parse(fd)
            results = [{item.tag: item.text for item in ch} for ch in tree.findall('dealer')]
            for dealer in results:
                dealer_id=dealer['code']
                dealers[dealer_id] = dealer
        except etree.XMLSyntaxError:
            print 'not xml %s' % file_name

with open(combined_name, 'wb') as fd:
    json.dump(list(dealers.values()), fd, sort_keys=True, indent=2)

