#!/usr/bin/env python

import os
from   collections import namedtuple
import json

# declare normalized data structure

LocalBusiness = namedtuple('LocalBusiness', ['address', 'geo', 'name', 'url', 'telephone', 'email', 'id'])

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

input_name=os.path.join(directory_name, 'scion.json')

output_name=os.path.join(directory_name, 'normalized-scion.json')

# normalize the data

businesses = []

with open(input_name, 'r') as fd:
    dealers = json.load(fd)
    for dealer in dealers:
        address = Address(
            streetAddress   = dealer['address'],
            addressRegion   = dealer['state'],
            postalCode      = dealer['zipCode'],
            addressLocality = dealer['city'],
            addressCountry  = 'US'
        )
        geo = GeoCoordinates(
            latitude  = dealer['latitude'][:8],
            longitude = dealer['longitude'][:10]
        )
        email = None
        if 'emailAddress' in dealer:
            email = dealer['emailAddress']
        business = LocalBusiness(
            id           = dealer['code'],
            telephone    = dealer['phoneNumber'],
            name         = dealer['name'],
            url          = dealer['url'],
            email        = email,
            address      = address,
            geo          = geo
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd)

