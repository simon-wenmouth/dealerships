#!/usr/bin/env python

import os
from   collections import namedtuple
import json

# declare normalized data structure

LocalBusiness = namedtuple('LocalBusiness', ['address', 'geo', 'name', 'url', 'telephone', 'id'])

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

input_name=os.path.join(directory_name, 'jaguar.json')

output_name=os.path.join(directory_name, 'normalized-jaguar.json')

# normalize the data

businesses = {}

with open(input_name, 'r') as fd:
    dealers = json.load(fd)
    for dealer in dealers.values():
        address = Address(
            streetAddress   = dealer['address1'],
            addressRegion   = dealer['state'],
            postalCode      = dealer['zip'],
            addressLocality = dealer['city'],
            addressCountry  = 'US'
        )
        geo = GeoCoordinates(
            latitude  = dealer['latitude'],
            longitude = dealer['longitude']
        )
        dealer_id = dealer['dealerId']
        business = LocalBusiness(
            id           = dealer_id,
            telephone    = dealer['salesPhone'],
            name         = dealer['name'],
            url          = dealer['url'],
            address      = address,
            geo          = geo
        )
        if not dealer_id in businesses:
            businesses[dealer_id]= business

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses.values())), fd)

