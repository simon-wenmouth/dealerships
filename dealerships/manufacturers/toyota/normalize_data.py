#!/usr/bin/env python

import os
from   collections import namedtuple
import json

# declare normalized data structure

LocalBusiness = namedtuple('LocalBusiness', ['address', 'geo', 'name', 'url', 'telephone', 'faxNumber', 'id', 'openingHours', 'openingHoursSpecification'])

GeoCoordinates = namedtuple('GeoCoordinates', ['latitude', 'longitude'])

Address = namedtuple('Address', ['addressCountry', 'addressLocality', 'addressRegion', 'postalCode', 'streetAddress'])

OpeningHoursSpecification = namedtuple('OpeningHoursSpecification', ['opens', 'closes', 'dayOfWeek'])

def ToDictionary(obj):
    if isinstance(obj, tuple) and hasattr(obj, '_asdict'):
        return {k: ToDictionary(v) for k, v in obj._asdict().iteritems() if v is not None}
    if isinstance(obj, list):
        return map(ToDictionary, obj)
    else:
        return obj;

# declare input and output file names

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data'))

input_name=os.path.join(directory_name, 'toyota.json')

output_name=os.path.join(directory_name, 'normalized-toyota.json')

# normalize the data

def ToOpeningHours(idx, val):
    if val == 'Closed':
        return None
    i2n = {1: 'Mo', 2: 'Tu', 3: 'We', 4: 'Th', 5: 'Fr', 6: 'Sa', 0: 'Su'}
    opens, closes = val.split(',')
    opens  = '{0}:{1}'.format(opens[:2], opens[2:])
    closes = '{0}:{1}'.format(closes[:2], closes[2:])
    return '{0} {1}-{2}'.format(i2n[idx], opens, closes)

def ToOpeningHoursSpecification(idx, val):
    if val == 'Closed':
        return None
    i2n = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday', 0: 'Sunday'}
    opens, closes = val.split(',')
    opens  = '{0}:{1}'.format(opens[:2], opens[2:])
    closes = '{0}:{1}'.format(closes[:2], closes[2:])
    return OpeningHoursSpecification(opens, closes, i2n[idx])

businesses = []

with open(input_name, 'r') as fd:
    dealers = json.load(fd)
    for dealer in dealers:
        address = Address(
            streetAddress   = dealer['address1'],
            addressRegion   = dealer['state'],
            postalCode      = dealer['zipCode'],
            addressLocality = dealer['city'],
            addressCountry  = 'US'
        )
        geo = GeoCoordinates(
            latitude  = dealer['latitude'],
            longitude = dealer['longitude']
        )
        openingHours = []
        openingHoursSpecification = []
        if dealer['general']['hours']:
            for idx, val in enumerate(dealer['general']['hours']):
                x = ToOpeningHours(idx, val[0])
                if x is not None:
                    openingHours.append(x)
                y = ToOpeningHoursSpecification(idx, val[0])
                if y is not None:
                    openingHoursSpecification.append(y)
        business = LocalBusiness(
            id           = dealer['code'],
            telephone    = dealer['phone'],
            name         = dealer['name'],
            url          = dealer['url'],
            faxNumber    = dealer['fax'],
            address      = address,
            geo          = geo,
            openingHours = openingHours,
            openingHoursSpecification = openingHoursSpecification
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd)

