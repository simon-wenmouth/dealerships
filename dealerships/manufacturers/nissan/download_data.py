#!/usr/bin/env python

import os
import glob
import json
import errno
import requests
from zip_code_radius import solver

# create data directory (when missing)

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  '..', 'data', 'nissan'))

try:
    os.makedirs(directory_name)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(directory_name):
        pass
    else:
        raise

# download data

url='http://www.nissanusa.com/nissandealers/locate/dealersAjax?channelCode=in&zipCode={0}&format=json'

radius=250

locations=solver.solve(float(radius))

for location in locations:
    file_name=os.path.join(directory_name, location.zip_code + '.json')
    if not os.path.exists(file_name):
        try:
            response = requests.get(url.format(location.zip_code), stream=True, timeout=5)
            with open(file_name, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=1024):
                    fd.write(chunk)
        except requests.exceptions.Timeout:
            print ("Timeout: %s" % location.zip_code)

# combine JSON files

file_names=glob.glob(os.path.join(directory_name, '*.json'))

combined_name=os.path.join(os.path.dirname(directory_name), 'nissan.json')

dealers = {}

for file_name in file_names:
    with open(file_name, 'r') as fd:
        try:
            results = json.load(fd)
            if 'dealers' in results:
                for dealer in results['dealers']:
                    dealer_id=dealer['dealerId']
                    dealers[dealer_id] = dealer
        except ValueError:
            print 'not a JSON file %s' % file_name

with open(combined_name, 'wb') as fd:
    json.dump(list(dealers.values()), fd)

