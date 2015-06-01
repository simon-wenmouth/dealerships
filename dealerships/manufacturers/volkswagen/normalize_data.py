#!/usr/bin/env python

import os
from   collections import namedtuple
import json

# declare normalized data structure

LocalBusiness = namedtuple('LocalBusiness', ['department', 'address', 'geo', 'name', 'url', 'telephone', 'id'])

Department = namedtuple('Department', ['name', 'openingHours', 'openingHoursSpecification'])

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

input_name=os.path.join(directory_name, 'volkswagen.json')

output_name=os.path.join(directory_name, 'normalized-volkswagen.json')

# normalize the data

def ToOpeningHours(obj):
    if obj['isClosed'] == 'Y':
        return None
    day = obj['dayText']
    opens = obj['openHour']
    closes = obj['closeHour']
    return '{0} {1}-{2}'.format(day[:2], opens, closes)

def ToOpeningHoursSpecification(obj):
    if obj['isClosed'] == 'Y':
        return None
    n2n = {'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday', 'Thu': 'Thursday', 'Fri': 'Friday', 'Sat': 'Saturday', 'Sun': 'Sunday'}
    day = obj['dayText']
    opens = obj['openHour']
    closes = obj['closeHour']
    return OpeningHoursSpecification(opens, closes, n2n[day])

businesses = []

with open(input_name, 'r') as fd:
    dealers = json.load(fd)
    for dealer in dealers:
        address = Address(
            streetAddress   = dealer['address1'],
            addressRegion   = dealer['state'],
            postalCode      = dealer['postalcode'],
            addressLocality = dealer['city'],
            addressCountry  = dealer['country']
        )
        latlon = dealer['latlong'].split(',')
        geo = GeoCoordinates(
            latitude  = latlon[0],
            longitude = latlon[1]
        )
        departments = []
        for dept in dealer['hours']:
            openingHours = []
            openingHoursSpecification = []
            name = dept['departmentName']
            for hours in dept['departmentHours']:
                x = ToOpeningHours(hours)
                if x is not None:
                    openingHours.append(x)
                y = ToOpeningHoursSpecification(hours)
                if y is not None:
                    openingHoursSpecification.append(y)
            departments.append(Department(name, openingHours, openingHoursSpecification))
        business = LocalBusiness(
            id           = dealer['dealerid'],
            telephone    = dealer['phone'],
            name         = dealer['name'],
            url          = dealer['url'],
            address      = address,
            department   = departments,
            geo          = geo
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd)

