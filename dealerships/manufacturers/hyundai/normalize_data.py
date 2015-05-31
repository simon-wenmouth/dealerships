#!/usr/bin/env python

import os
from   collections import namedtuple
import json

# declare normalized data structure

LocalBusiness = namedtuple('LocalBusiness', ['address', 'geo', 'name', 'url', 'telephone', 'faxNumber', 'email', 'id'])

GeoCoordinates = namedtuple('GeoCoordinates', ['latitude', 'longitude'])

Address = namedtuple('Address', ['addressCountry', 'addressLocality', 'addressRegion', 'postalCode', 'streetAddress'])

def ToDictionary(obj):
    if isinstance(obj, tuple) and hasattr(obj, '_asdict'):
        return {k: ToDictionary(v) for k, v in obj._asdict().iteritems() if v is not None}
    if isinstance(obj, list):
        return map(ToDictionary, obj)
    else:
        return obj;

# declare input and output file names

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data'))

input_name=os.path.join(directory_name, 'hyundai.json')

output_name=os.path.join(directory_name, 'normalized-hyundai.json')

businesses = []

with open(input_name, 'r') as fd:
    dealers = json.load(fd)
    for dealer in dealers['GetDealerLocationNewJSONResult']:
        address = Address(
            streetAddress   = dealer['Address1'],
            addressRegion   = dealer['State'],
            postalCode      = dealer['Zip'],
            addressLocality = dealer['City'],
            addressCountry  = 'US'
        )
        geo = GeoCoordinates(
            latitude  = dealer['Latitude'],
            longitude = dealer['Longitude']
        )
        email = dealer['DealerEmail']
        if email == '':
            email = None
        url = dealer['DealerUrl']
        if url == '':
            url = None
        business = LocalBusiness(
            id           = dealer['DealerCode'],
            telephone    = dealer['SalesPhone'],
            faxNumber    = dealer['SalesFax'],
            name         = dealer['DealerName'],
            url          = url,
            email        = email,
            address      = address,
            geo          = geo
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd)

