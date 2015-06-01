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

input_name=os.path.join(directory_name, 'mercedes-benz.json')

output_name=os.path.join(directory_name, 'normalized-mercedes-benz.json')

# normalize the data

businesses = []

with open(input_name, 'r') as fd:
    results = json.load(fd)
    for result in results:
        dealer  = result['dealer']
        contact = dealer['contact']
        address = Address(
            streetAddress   = contact['address']['street'],
            addressRegion   = contact['address']['state'],
            postalCode      = contact['address']['zip'],
            addressLocality = contact['address']['city'],
            addressCountry  = 'US'
        )
        geo = GeoCoordinates(
            latitude  = result['pointOfInterest']['latitude'],
            longitude = result['pointOfInterest']['longitude']
        )
        telephone = None
        faxNumber = None
        for phone in contact['phones']:
            if phone['phoneType'].startswith('FAX'):
                faxNumber = phone['number']
            elif phone['phoneType'].startswith('PHONE'):
                telephone = phone['number']
        business = LocalBusiness(
            id           = dealer['id'],
            telephone    = telephone,
            faxNumber    = faxNumber,
            name         = contact['name'],
            url          = contact['url'],
            address      = address,
            geo          = geo
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd)

