#!/usr/bin/env python3

import os
from   collections import namedtuple
import json

# declare normalized data structure

LocalBusiness = namedtuple('LocalBusiness', ['department', 'address', 'geo', 'name', 'url', 'telephone', 'id', 'openingHours'])

Department = namedtuple('Department', ['name', 'email', 'faxNumber', 'telephone', 'openingHoursSpecification'])

ContactPoint = namedtuple('ContactPoint', ['contactType', 'telephone', 'email'])

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

input_name=os.path.join(directory_name, 'audi.json')

output_name=os.path.join(directory_name, 'normalized-audi.json')

# normalize the data

def ToOpeningHours(obj):
    return '{0} {1}-{2}'.format(obj.dayOfWeek[0:2], obj.opens, obj.closes)

businesses = []

with open(input_name, 'r') as fd:
    dealers = json.load(fd)
    for dealer in dealers:
        address = Address(
            streetAddress   = dealer['address1'],
            addressRegion   = dealer['state'],
            postalCode      = dealer['zip'],
            addressLocality = dealer['city'],
            addressCountry  = 'US'
        )
        geo = GeoCoordinates(
            latitude  = dealer['latitude'],
            longitude = dealer['longitude']
        )
        departments = []
        openingHours = []
        for item in dealer['departments']:
            name      = item['description']
            email     = item['email']
            if email == '':
                email = None
            faxNumber = None
            telephone = None
            for phone in item['phones']:
                if phone['type'] == 'Primary phone':
                    telephone = phone['number']
                elif phone['type'] == 'Primary fax':
                    faxNumber = phone['number']
            openingHoursSpecification = []
            for hours in item['hoursOfOperation']:
                if hours['closedIndicator'] == 'N':
                    day    = hours['name']
                    opens  = hours['hours'][0]['openTime']
                    closes = hours['hours'][0]['closeTime']
                    openingHoursSpecification.append(OpeningHoursSpecification(opens, closes, day))
            if name == 'Sales':
                openingHours = list(map(ToOpeningHours, openingHoursSpecification))
            if len(openingHoursSpecification) == 0:
                openingHoursSpecification = None
            departments.append(Department(
                name = name,
                email = email,
                faxNumber = faxNumber,
                telephone = telephone,
                openingHoursSpecification = openingHoursSpecification
            ))
        business = LocalBusiness(
            id           = dealer['id'],
            telephone    = dealer['phone'],
            name         = dealer['name'],
            url          = dealer['url'],
            department   = departments,
            address      = address,
            geo          = geo,
            openingHours = openingHours
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd, sort_keys=True, indent=2)

