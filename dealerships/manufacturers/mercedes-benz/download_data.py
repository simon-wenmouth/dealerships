#!/usr/bin/env python3

import os
import glob
import json
import errno
import requests

# create the data directory (when missing)

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  '..', 'data', 'mercedes-benz'))

try:
    os.makedirs(directory_name)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(directory_name):
        pass
    else:
        raise

# download the data

state_codes=['AL', 'AK', 'AS', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FM', 'FL', 'GA', 'GU', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MH', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'MP', 'OH', 'OK', 'OR', 'PW', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VI', 'VA', 'WA', 'WV', 'WI', 'WY', 'AE', 'AA', 'AP']

url='http://www.mbusa.com/mercedes/json/dealers?searchType=byState&state={0}&trim=true'

for state_code in state_codes:
    file_name=os.path.join(directory_name, state_code + '.json')
    if not os.path.exists(file_name):
        try:
            response = requests.get(url.format(state_code), stream=True, timeout=5)
            with open(file_name, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=1024):
                    fd.write(chunk)
        except requests.exceptions.Timeout:
            print ("Timeout: %s" % state_code)

# combine the files

file_names=glob.glob(os.path.join(directory_name, '*.json'))

combined_name=os.path.join(os.path.dirname(directory_name), 'mercedes-benz.json')

dealers = {}

for file_name in file_names:
    with open(file_name, 'r') as fd:
        results = json.load(fd)
        if 'dealers' in results:
            for dealer in results['dealers']:
                dealer_id=dealer['dealer']['id']
                dealers[dealer_id] = dealer
        else:
            print 'nothing %s' % file_name

with open(combined_name, 'wb') as fd:
    json.dump(list(dealers.values()), fd, sort_keys=True, indent=2)

