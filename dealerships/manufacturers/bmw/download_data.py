#!/usr/bin/env python

import os
import errno
import requests

# http://www.bmwusa.com/Services/DealerLocator.svc/help

# http://www.bmwusa.com/Services/DealerLocator.svc/GetDealersByCityState/{state}/{radius}/{typeService}/{pageNumber}/?city={city}

url='http://www.bmwusa.com/Services/DealerLocator.svc/GetDealersByCityState/IL/3000/1/1/?city=Chicago'

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  '..', 'data'))

try:
    os.makedirs(directory_name)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(directory_name):
        pass
    else:
        raise

file_name=os.path.join(directory_name, 'bmw.json')

response = requests.get(url, stream=True)

with open(file_name, 'wb') as fd:
    for chunk in response.iter_content(chunk_size=1024):
        fd.write(chunk)

