#!/usr/bin/env python3

import os
import errno
import requests

url='http://www.dodge.com/hostd/getlocatedealers.json?zipCode=60202&zipDistance=2500'

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  '..', 'data'))

try:
    os.makedirs(directory_name)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(directory_name):
        pass
    else:
        raise

file_name=os.path.join(directory_name, 'dodge.json')

response = requests.get(url, stream=True)

with open(file_name, 'wb') as fd:
    for chunk in response.iter_content(chunk_size=1024):
        fd.write(chunk)

