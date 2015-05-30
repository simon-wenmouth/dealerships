#!/usr/bin/env python

import os
import glob
import json
import errno
import requests
from zip_code_radius import solver

# create the data directory (when missing)

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'acura'))

try:
    os.makedirs(directory_name)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(directory_name):
        pass
    else:
        raise

# download the data

url='http://www.acura.com/tools/dealerlocator/DealerLocatorHandler.aspx'

radius=100

locations=solver.solve(float(radius))

for location in locations:
    file_name=os.path.join(directory_name, location.zip_code + '.json')
    response = requests.get(url, params={'z': location.zip_code, 'r': radius}, stream=True)
    with open(file_name, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=1024):
            fd.write(chunk)

# combine the JSON files

file_names=glob.glob(os.path.join(directory_name, '*.json'))

combined_name=os.path.join(os.path.dirname(directory_name), 'acura.json')

dealers = {}

for file_name in file_names:
    with open(file_name, 'r') as fd:
        results = json.load(fd)
        if 'Dealers' in results:
            for dealer in results['Dealers']:
                dealers[dealer['DealerID']] = dealer

with open(combined_name, 'wb') as fd:
    json.dump(list(dealers.values()), fd)

