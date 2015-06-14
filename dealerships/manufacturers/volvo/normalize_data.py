#!/usr/bin/env python3

import os
import re
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

input_name=os.path.join(directory_name, 'volvo.json')

output_name=os.path.join(directory_name, 'normalized-volvo.json')

# normalize the data

businesses = []

with open(input_name, 'r') as fd:
    dealers = json.load(fd)
    for dealer in dealers:
        city_state_zip = re.sub('\\s+', ' ', dealer['AddressLine2'])
        city, state_zip = [s.strip() for s in city_state_zip.split(',')]
        state, zip_code = state_zip.strip().split(' ')
        address = Address(
            streetAddress   = dealer['AddressLine1'],
            addressRegion   = state,
            postalCode      = zip_code,
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
    json.dump(list(map(ToDictionary, businesses)), fd, sort_keys=True, indent=2)

