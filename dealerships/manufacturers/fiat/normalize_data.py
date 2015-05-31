#!/usr/bin/env python

import os
from   collections import namedtuple
import json

# declare normalized data structure

LocalBusiness = namedtuple('LocalBusiness', ['address', 'geo', 'name', 'url', 'telephone', 'id', 'brand'])

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

input_name=os.path.join(directory_name, 'fiat.json')

output_name=os.path.join(directory_name, 'normalized-fiat.json')

businesses = []

with open(input_name, 'r') as fd:
    results = json.load(fd)
    for dealer in results[0]['data']['dealers']:
        postalCode = dealer['zip'].strip()
        address = Address(
            streetAddress   = dealer['address1'].strip(),
            addressRegion   = dealer['state'].strip(),
            postalCode      = '{0}-{1}'.format(postalCode[:5], postalCode[5:]),
            addressLocality = dealer['city'].strip(),
            addressCountry  = 'US'
        )
        geo = GeoCoordinates(
            latitude  = dealer['latitude'],
            longitude = dealer['longitude']
        )
        telephone = None
        for field in ['phone', 'salesPhone', 'usedPhone']:
            value = dealer[field]
            if value is not None and len(value) > 0 and not value.isspace():
                telephone = value
                break
        brands = []
        if dealer['isChrysler'] == 'Y':
            brands.append('Chrysler')
        if dealer['isDodge'] == 'Y':
            brands.append('Dodge')
        if dealer['isFiat'] == 'Y':
            brands.append('Fiat')
        if dealer['isJeep'] == 'Y':
            brands.append('Jeep')
        if dealer['isRam'] == 'Y' or dealer['isRamTrucks'] == 'Y':
            brands.append('RAM')
        business = LocalBusiness(
            id        = dealer['dealerCode'],
            telephone = telephone,
            name      = dealer['name'].strip(),
            url       = dealer['url'].strip(),
            address   = address,
            geo       = geo,
            brand     = brands
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd)

