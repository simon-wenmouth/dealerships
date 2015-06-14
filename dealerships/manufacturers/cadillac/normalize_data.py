#!/usr/bin/env python3

import os
from   collections import namedtuple
from   itertools import chain
import json
import time

# declare normalized data structure

LocalBusiness = namedtuple('LocalBusiness', ['department', 'address', 'geo', 'name', 'url', 'telephone', 'faxNumber', 'id', 'openingHours', 'openingHoursSpecification'])

Department = namedtuple('Department', ['name', 'faxNumber', 'telephone', 'openingHours', 'openingHoursSpecification'])

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

input_name=os.path.join(directory_name, 'cadillac.json')

output_name=os.path.join(directory_name, 'normalized-cadillac.json')

# normalize the data

def FormatOpeningHours(obj):
    days = {
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday',
        7: 'Sunday',
    }
    day_from = int(obj['dayFrom'])
    day_upto = int(obj['dayTo'])
    opens    = time.strftime('%H:%M', time.strptime(obj['timeFrom'], '%I:%M %p'))
    closes   = time.strftime('%H:%M', time.strptime(obj['timeTo'], '%I:%M %p'))
    if day_from == day_upto:
        days = days[day_from][0:2]
    else:
        days = '{0}-{1}'.format(days[day_from][0:2], days[day_upto][0:2])
    return '{0} {1}-{2}'.format(days, opens, closes)

def ToOpeningHoursSpecification(obj):
    days = {
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday',
        7: 'Sunday',
    }
    day_from = int(obj['dayFrom'])
    day_upto = int(obj['dayTo'])
    opens    = time.strftime('%H:%M', time.strptime(obj['timeFrom'], '%I:%M %p'))
    closes   = time.strftime('%H:%M', time.strptime(obj['timeTo'], '%I:%M %p'))
    results = []
    for i in range(day_from, day_upto+1):
        results.append(OpeningHoursSpecification(opens, closes, days[i]))
    return results

businesses = []

with open(input_name, 'r') as fd:
    dealers = json.load(fd)
    for dealer in dealers:
        address = Address(
            streetAddress   = dealer['address']['street'].title(),
            addressRegion   = dealer['address']['province'],
            postalCode      = dealer['address']['postCode'],
            addressLocality = dealer['address']['city'].title(),
            addressCountry  = dealer['address']['country']
        )
        geo = GeoCoordinates(
            latitude  = dealer['address']['latitude'],
            longitude = dealer['address']['longitud']
        )
        openingHours = list(map(FormatOpeningHours, dealer['openingHours']))
        openingHoursSpecification = list(chain(*map(ToOpeningHoursSpecification, dealer['openingHours'])))
        departments = []
        for item in dealer['departments']:
            name      = item['departmentName'].replace(' Hours', '').strip()
            telephone = None
            faxNumber = None
            if isinstance(item['contact'], dict):
                telephone = item['contact']['phone']
                faxNumber = item['contact']['fax']
                if telephone == '':
                    telephone = None
                if faxNumber == '':
                    faxNumber = None
            departments.append(Department(
                name         = name,
                faxNumber    = faxNumber,
                telephone    = telephone,
                openingHours = list(map(FormatOpeningHours, item['openingHour'])),
                openingHoursSpecification = list(chain(*map(ToOpeningHoursSpecification, item['openingHour'])))
            ))
        telephone = dealer['contact']['phone']
        faxNumber = dealer['contact']['fax']
        if telephone == '':
            telephone = None
        if faxNumber == '':
            faxNumber = None
        business = LocalBusiness(
            id                        = dealer['dealerId'],
            telephone                 = telephone,
            faxNumber                 = faxNumber,
            name                      = dealer['legalEntityName'].title(),
            url                       = dealer['url'],
            department                = departments,
            address                   = address,
            geo                       = geo,
            openingHours              = openingHours,
            openingHoursSpecification = openingHoursSpecification
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd, sort_keys=True, indent=2)

