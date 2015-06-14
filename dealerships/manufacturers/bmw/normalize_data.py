#!/usr/bin/env python3

import os
from   collections import namedtuple
import json
import time

# declare normalized data structure

LocalBusiness = namedtuple('LocalBusiness', ['department', 'address', 'geo', 'name', 'url', 'telephone', 'faxNumber', 'id', 'openingHours'])

Department = namedtuple('Department', ['name', 'faxNumber', 'telephone', 'openingHours'])

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

input_name=os.path.join(directory_name, 'bmw.json')

output_name=os.path.join(directory_name, 'normalized-bmw.json')

# normalize the data

def FormatOpeningHours(obj):
    # "Mon-Thu: 10:00 am - 8:00 pm"
    i = obj.index(':')
    days = obj[:i]
    hours = obj[i+1:]
    if '-' in days:
        day_from, day_upto = days.split('-', 2)
        days = '{0}-{1}'.format(day_from[0:2], day_upto[0:2])
    else:
        days = days[0:2]
    opens, closes = list(map(lambda x: time.strftime('%H:%M', time.strptime(x, '%I:%M %p')), list(map(lambda x: x.strip(), hours.split('-', 2)))))
    return '{0} {1}-{2}'.format(days, opens, closes)

businesses = []

with open(input_name, 'r') as fd:
    dealers = json.load(fd)
    for dealer in dealers['ViewModel']['Dealers']:
        address = Address(
            streetAddress   = dealer['DefaultService']['Address'],
            addressRegion   = dealer['DefaultService']['State'],
            postalCode      = dealer['DefaultService']['ZipCode'],
            addressLocality = dealer['DefaultService']['City'],
            addressCountry  = 'US'
        )
        geo = GeoCoordinates(
            latitude  = dealer['DefaultService']['LonLat']['Lat'],
            longitude = dealer['DefaultService']['LonLat']['Lon']
        )
        openingHours = list(map(FormatOpeningHours, dealer['DefaultService']['Hours']))
        departments = []
        for service in dealer['Services']:
            mappings = {
                1: "New Vehicles",
                2: "Certified Pre-Owned Vehicles",
                3: "BMW Service",
                4: "Collision Repair Center",
                5: "M Certified Center",
                6: "BMW i New Vehicles",
                7: "BMW i Certified Pre-Owned Vehicles",
                8: "BMW i Service",
            }
            name      = mappings[int(service['ServiceType'])]
            hours     = list(map(FormatOpeningHours, service['Hours']))
            telephone = service['Phone']
            faxNumber = service['Fax']
            departments.append(Department(
                name         = name,
                faxNumber    = faxNumber,
                telephone    = telephone,
                openingHours = hours
            ))
        business = LocalBusiness(
            id           = dealer['CenterId'],
            telephone    = dealer['DefaultService']['Phone'],
            faxNumber    = dealer['DefaultService']['Fax'],
            name         = dealer['DefaultService']['Name'],
            url          = dealer['DefaultService']['Url'],
            department   = departments,
            address      = address,
            geo          = geo,
            openingHours = openingHours
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd, sort_keys=True, indent=2)

