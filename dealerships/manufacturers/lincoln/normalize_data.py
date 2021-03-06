#!/usr/bin/env python3

import os
from   collections import namedtuple
import json

# declare normalized data structure

LocalBusiness = namedtuple('LocalBusiness', ['department', 'address', 'geo', 'name', 'url', 'telephone', 'faxNumber', 'id', 'map'])

Department = namedtuple('Department', ['name', 'openingHours', 'openingHoursSpecification'])

GeoCoordinates = namedtuple('GeoCoordinates', ['latitude', 'longitude'])

Address = namedtuple('Address', ['addressCountry', 'addressLocality', 'addressRegion', 'postalCode', 'streetAddress'])

OpeningHoursSpecification = namedtuple('OpeningHoursSpecification', ['opens', 'closes', 'dayOfWeek'])

def ToDictionary(obj):
    if isinstance(obj, tuple):
        return {k: ToDictionary(v) for k, v in vars(obj).items()}
    if isinstance(obj, list):
        return list(map(ToDictionary, obj))
    else:
        return obj;

# declare input and output file names

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data'))

input_name=os.path.join(directory_name, 'lincoln.json')

output_name=os.path.join(directory_name, 'normalized-lincoln.json')

# normalize the data

def ToOpeningHours(obj):
    if 'closed' in obj:
        return None
    day    = obj['name']
    opens  = obj['open']
    closes = obj['close']
    return '{0} {1}-{2}'.format(day[:2], opens, closes)

def ToOpeningHoursSpecification(obj):
    if 'closed' in obj:
        return None
    day    = obj['name']
    opens  = obj['open']
    closes = obj['close']
    return OpeningHoursSpecification(opens, closes, day)

businesses = []

with open(input_name, 'r') as fd:
    dealers = json.load(fd)
    for dealer in dealers:
        address = Address(
            streetAddress   = dealer['Address']['Street1'],
            addressRegion   = dealer['Address']['State'],
            postalCode      = dealer['Address']['PostalCode'],
            addressLocality = dealer['Address']['City'],
            addressCountry  = dealer['Address']['Country'],
        )
        geo = GeoCoordinates(
            latitude  = dealer['Latitude'],
            longitude = dealer['Longitude']
        )
        departments = []
        if 'ServiceHours' in dealer and 'Day' in dealer['ServiceHours']:
            departments.append(Department(
                name         = 'Service',
                openingHours = [ x for x in map(ToOpeningHours, dealer['ServiceHours']['Day']) if x is not None],
                openingHoursSpecification = [x for x in map(ToOpeningHoursSpecification, dealer['ServiceHours']['Day']) if x is not None]
            ))
        if 'SalesHours' in dealer and 'Day' in dealer['SalesHours']:
            departments.append(Department(
                name         = 'Sales',
                openingHours = [ x for x in map(ToOpeningHours, dealer['SalesHours']['Day']) if x is not None],
                openingHoursSpecification = [x for x in map(ToOpeningHoursSpecification, dealer['SalesHours']['Day']) if x is not None]
            ))
        url = dealer['URL']
        if isinstance(url, dict):
            url = None
        telephone = dealer['Phone']
        if isinstance(telephone, dict):
            telephone = None
        faxNumber = dealer['Fax']
        if isinstance(faxNumber, dict):
            faxNumber = None
        business = LocalBusiness(
            id           = dealer['PACode'],
            telephone    = telephone,
            faxNumber    = faxNumber,
            name         = dealer['Name'],
            url          = url,
            map          = dealer['MapURL'],
            department   = departments,
            address      = address,
            geo          = geo
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd, sort_keys=True, indent=2)

