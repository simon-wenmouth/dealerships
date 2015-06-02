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

input_name=os.path.join(directory_name, 'smart.json')

output_name=os.path.join(directory_name, 'normalized-smart.json')

# normalize the data

businesses = []

with open(input_name, 'r') as fd:
    results = json.load(fd)
    for dealer in results['Result']['Dealers']:
        address = Address(
            streetAddress   = dealer['Address'].title(),
            addressRegion   = dealer['State'],
            postalCode      = dealer['Zipcode'],
            addressLocality = dealer['City'].title(),
            addressCountry  = 'US'
        )
        geo = GeoCoordinates(
            latitude  = dealer['Latitude'],
            longitude = dealer['Longitude']
        )
        email = None
        if 'emailAddress' in dealer:
            email = dealer['emailAddress']
        business = LocalBusiness(
            id           = dealer['DealerCode'],
            telephone    = dealer['Phone'],
            name         = dealer['DealerName'].title(),
            url          = dealer['DealerWebsite'].lower(),
            address      = address,
            geo          = geo
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd)

