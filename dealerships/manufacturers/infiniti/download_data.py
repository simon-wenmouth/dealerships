#!/usr/bin/env python3

import os
import errno
import requests
from zip_code_radius import solver

url='http://www.infinitiusa.com/infinitiretailers/locate/retailersAjax?channelCode=in&zipCode={0}&format=json'

radius=250

locations=solver.solve(float(radius))

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  '..', 'data', 'infiniti'))

try:
    os.makedirs(directory_name)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(directory_name):
        pass
    else:
        raise

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

