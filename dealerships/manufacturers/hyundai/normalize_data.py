#!/usr/bin/env python3

import os
from   collections import namedtuple
import json

# declare normalized data structure

LocalBusiness = namedtuple('LocalBusiness', ['address', 'geo', 'name', 'url', 'telephone', 'faxNumber', 'email', 'id'])

GeoCoordinates = namedtuple('GeoCoordinates', ['latitude', 'longitude'])

Address = namedtuple('Address', ['addressCountry', 'addressLocality', 'addressRegion', 'postalCode', 'streetAddress'])

def ToDictionary(obj):
    if isinstance(obj, tuple):
        return {k: ToDictionary(v) for k, v in vars(obj).items()}
    if isinstance(obj, list):
        return list(map(ToDictionary, obj))
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
            streetAddress   = dealer['Address1'].title(),
            addressRegion   = dealer['State'],
            postalCode      = dealer['Zip'],
            addressLocality = dealer['City'].title(),
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
            name         = dealer['DealerName'].title(),
            url          = url,
            email        = email,
            address      = address,
            geo          = geo
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd, sort_keys=True, indent=2)

