#!/usr/bin/env python

import os
import errno
import requests

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

