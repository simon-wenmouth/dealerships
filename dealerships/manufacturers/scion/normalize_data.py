#!/usr/bin/env python3

import os
from   collections import namedtuple
import json

# declare normalized data structure

LocalBusiness = namedtuple('LocalBusiness', ['address', 'geo', 'name', 'url', 'telephone', 'email', 'id'])

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
    json.dump(list(map(ToDictionary, businesses)), fd, sort_keys=True, indent=2)

