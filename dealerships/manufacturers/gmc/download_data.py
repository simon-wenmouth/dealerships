#!/usr/bin/env python3

import os
import glob
import json
import errno
import requests
from zip_code_radius import solver

# create the data directory (when missing)

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  '..', 'data', 'gmc'))

try:
    os.makedirs(directory_name)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(directory_name):
        pass
    else:
        raise

# download the data

url='http://www.gmc.com/bypass/gmna/dealerlocator/services/getdealers?type=PostalCode&format=JSON&x-country=US&x-language=en&x-brand=GMC&postalcode={0}'

radius=50

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

# combine the JSON files

file_names=glob.glob(os.path.join(directory_name, '*.json'))

combined_name=os.path.join(os.path.dirname(directory_name), 'gmc.json')

dealers = {}

for file_name in file_names:
    with open(file_name, 'r') as fd:
        results = json.load(fd)
        if not 'http_response_code' in results:
            for dealer in results:
                dealers[dealer['dealerId']] = dealer

with open(combined_name, 'wb') as fd:
    json.dump(list(dealers.values()), fd, sort_keys=True, indent=2)

