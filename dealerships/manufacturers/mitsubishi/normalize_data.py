#!/usr/bin/env python

import os
from   collections import namedtuple
import json

# declare normalized data structure

LocalBusiness = namedtuple('LocalBusiness', ['address', 'geo', 'name', 'url', 'telephone', 'faxNumber', 'id'])

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

input_name=os.path.join(directory_name, 'mitsubishi.json')

output_name=os.path.join(directory_name, 'normalized-mitsubishi.json')

# normalize the data

businesses = []

with open(input_name, 'r') as fd:
    dealers = json.load(fd)
    for dealer in dealers:
        address = Address(
            streetAddress   = dealer['address1'],
            addressRegion   = dealer['state'],
            postalCode      = dealer['zipcode'],
            addressLocality = dealer['city'],
            addressCountry  = dealer['country'],
        )
        geo = GeoCoordinates(
            latitude  = dealer['latitude'],
            longitude = dealer['longitude']
        )
        business = LocalBusiness(
            id           = dealer['bizId'],
            telephone    = dealer['phone'],
            faxNumber    = dealer['fax'],
            name         = dealer['dealerName'],
            url          = dealer['dealerUrl'],
            address      = address,
            geo          = geo
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd)

