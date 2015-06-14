#!/usr/bin/env python3

import os
from   collections import namedtuple
from   itertools import chain
import json

# declare normalized data structure

LocalBusiness = namedtuple('LocalBusiness', ['department', 'address', 'geo', 'name', 'url', 'telephone', 'faxNumber', 'email', 'id'])

Department = namedtuple('Department', ['name', 'telephone', 'openingHours', 'openingHoursSpecification'])

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

input_name=os.path.join(directory_name, 'nissan.json')

output_name=os.path.join(directory_name, 'normalized-nissan.json')

# normalize the data

def ToOpeningHours(obj):
    startingHour = obj['startingHour']
    closingHour  = obj['closingHour']
    if startingHour == closingHour:
        return None
    startingHour = '{0}:{1}'.format(startingHour[:2], startingHour[2:])
    closingHour = '{0}:{1}'.format(closingHour[:2], closingHour[2:])
    days = obj['days']
    if '-' in days:
        day_from, day_upto = days.split('-')
        days = '{0}-{1}'.format(day_from[0:2], day_upto[0:2])
    else:
        days = days[0:2]
    return '{0} {1}-{2}'.format(days, startingHour, closingHour)

def ToOpeningHoursSpecification(obj):
    # hours
    startingHour = obj['startingHour']
    closingHour  = obj['closingHour']
    if startingHour == closingHour:
        return []
    startingHour = '{0}:{1}'.format(startingHour[:2], startingHour[2:])
    closingHour = '{0}:{1}'.format(closingHour[:2], closingHour[2:])
    # days
    n2i = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
    i2n = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
    n2n = {'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday', 'Thu': 'Thursday', 'Fri': 'Friday', 'Sat': 'Saturday', 'Sun': 'Sunday'}
    days = obj['days']
    loop = []
    if '-' in days:
        vals = days.split('-')
        for i in range(n2i[vals[0]], n2i[vals[1]]):
            loop.append(n2n[i2n[i]])
    else:
        loop.append(n2n[days])
    # create opening hours
    results = []
    for day in loop:
        results.append(OpeningHoursSpecification(startingHour, closingHour, day))
    return results

businesses = []

with open(input_name, 'r') as fd:
    dealers = json.load(fd)
    for dealer in dealers:
        address = Address(
            streetAddress   = dealer['addressLine1'].title(),
            addressRegion   = dealer['state'],
            postalCode      = dealer['zipCode'],
            addressLocality = dealer['city'].title(),
            addressCountry  = 'US'
        )
        geo = GeoCoordinates(
            latitude  = dealer['latitude'],
            longitude = dealer['longitude']
        )
        departments = []
        if 'serviceHours' in dealer and len(dealer['serviceHours']) > 0:
            serviceHours = dealer['serviceHours'].values()
            departments.append(Department(
                name         = 'Service',
                telephone    = dealer['servicePhone'],
                openingHours = [x for x in map(ToOpeningHours, serviceHours) if x is not None],
                openingHoursSpecification = [x for x in chain(*map(ToOpeningHoursSpecification, serviceHours))]
            ))
        if 'salesHours' in dealer and len(dealer['salesHours']) > 0:
            salesHours = dealer['salesHours'].values()
            departments.append(Department(
                name         = 'Sales',
                telephone    = dealer['salesPhone'],
                openingHours = [x for x in map(ToOpeningHours, salesHours) if x is not None],
                openingHoursSpecification = [x for x in chain(*map(ToOpeningHoursSpecification, salesHours))]
            ))
        email = dealer['emailAddress']
        if len(email) == 0:
            email = None
        url = dealer['url']
        if len(url) == 0:
            url = None
        faxNumber = dealer['fax']
        if len(faxNumber) == 0:
            faxNumber = None
        business = LocalBusiness(
            id           = dealer['dealerId'],
            telephone    = dealer['phoneNumber'],
            faxNumber    = faxNumber,
            email        = email,
            name         = dealer['name'].title(),
            url          = url,
            department   = departments,
            address      = address,
            geo          = geo
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd, sort_keys=True, indent=2)

