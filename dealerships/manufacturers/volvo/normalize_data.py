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

input_name=os.path.join(directory_name, 'volvo.json')

output_name=os.path.join(directory_name, 'normalized-volvo.json')

# normalize the data

businesses = []

with open(input_name, 'r') as fd:
    dealers = json.load(fd)
    for dealer in dealers:
        city_state_zip = dealer['AddressLine2']
        address = Address(
            streetAddress   = dealer['AddressLine1'],
            addressRegion   = city_state_zip[-8:-6],
            postalCode      = city_state_zip[-5:],
            addressLocality = dealer['City'],
            addressCountry  = dealer['Country'],
        )
        geo = GeoCoordinates(
            latitude  = dealer['GeoCode']['Latitude'],
            longitude = dealer['GeoCode']['Longitude']
        )
        business = LocalBusiness(
            id           = dealer['DealerId'],
            telephone    = dealer['Phone'],
            name         = dealer['Name'],
            url          = dealer['Url'],
            email        = dealer['GeneralContactEmail'],
            address      = address,
            geo          = geo
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd)

