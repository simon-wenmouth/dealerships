#!/usr/bin/env python

import os
import glob
import json
import errno
import requests
from zip_code_radius import solver

# create data directory (when missing)

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  '..', 'data', 'lincoln'))

try:
    os.makedirs(directory_name)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(directory_name):
        pass
    else:
        raise

# download data

url='http://www.lincoln.com/core-services/dealers/byzipcode.json?zipCode={0}&distance={1}&pageSize=100&pageIndex=1'

radius=250

locations=solver.solve(float(radius))

for location in locations:
    file_name=os.path.join(directory_name, location.zip_code + '.json')
    if not os.path.exists(file_name):
        try:
            response = requests.get(url.format(location.zip_code, radius), stream=True, timeout=5)
            with open(file_name, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=1024):
                    fd.write(chunk)
        except requests.exceptions.Timeout:
            print ("Timeout: %s" % location.zip_code)

# combine JSON files

file_names=glob.glob(os.path.join(directory_name, '*.json'))

combined_name=os.path.join(os.path.dirname(directory_name), 'lincoln.json')

dealers = {}

for file_name in file_names:
    with open(file_name, 'r') as fd:
        results = json.load(fd)
        if 'Response' in results:
            response = results['Response']
            if 'Dealer' in response:
                if int(response['total']) == 1:
                    dealer = response['Dealer']
                    dealers[dealer['PACode']] = dealer
                else:
                    for dealer in response['Dealer']:
                        dealers[dealer['PACode']] = dealer

with open(combined_name, 'wb') as fd:
    json.dump(list(dealers.values()), fd)

