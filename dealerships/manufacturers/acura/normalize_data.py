#!/usr/bin/env python3

import os
from   collections import namedtuple
import json
import time
from   itertools import chain

# declare normalized data structure

LocalBusiness = namedtuple('LocalBusiness', ['contactPoint', 'address', 'geo', 'name', 'url', 'email', 'faxNumber', 'telephone', 'id', 'openingHours'])

ContactPoint = namedtuple('ContactPoint', ['contactType', 'telephone', 'hoursAvailable'])

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

input_name=os.path.join(directory_name, 'acura.json')

output_name=os.path.join(directory_name, 'normalized-acura.json')

# normalize the data

def ToOpeningHours(obj):
    # extract hours
    if obj['Hours'] == 'Closed':
        return []
    hours = obj['Hours'].split('-')
    opens = time.strftime('%H:%M', time.strptime(hours[0], '%I:%M%p'))
    closes = time.strftime('%H:%M', time.strptime(hours[1], '%I:%M%p'))
    # extract days
    day = obj['Day']
    if '-' in day:
        vals = day.split('-')
        day = '{0}-{1}'.format(vals[0][0:2], vals[1][0:2])
    else:
        day = day[0:2]
    return '{0} {1}-{2}'.format(day, opens, closes)

def ToOpeningHoursSpecification(obj):
    # extract hours
    if obj['Hours'] == 'Closed':
        return []
    hours = obj['Hours'].split('-')
    opens = time.strftime('%H:%M:%S', time.strptime(hours[0], '%I:%M%p'))
    closes = time.strftime('%H:%M:%S', time.strptime(hours[1], '%I:%M%p'))
    # extract days
    n2i = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
    i2n = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
    n2n = {'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday', 'Thu': 'Thursday', 'Fri': 'Friday', 'Sat': 'Saturday', 'Sun': 'Sunday'}
    days = []
    day = obj['Day']
    if '-' in day:
        vals = day.split('-')
        for i in range(n2i[vals[0]], n2i[vals[1]]):
            days.append(n2n[i2n[i]])
    else:
        days.append(n2n[day])
    # create opening hours
    results = []
    for day in days:
        results.append(OpeningHoursSpecification(opens, closes, day))
    return results

businesses = []

with open(input_name, 'r') as fd:
    dealers = json.load(fd)
    for dealer in dealers:
        address = Address(
            streetAddress   = dealer['DealerAddress'],
            addressRegion   = dealer['DealerState'],
            postalCode      = dealer['DealerZip'],
            addressLocality = dealer['DealerCity'],
            addressCountry  = 'US'
        )
        geo = GeoCoordinates(
            latitude  = dealer['DealerLat'],
            longitude = dealer['DealerLong']
        )
        contact_points = []
        openingHours = []
        if 'ServicePhoneNumber' in dealer:
            contact_points.append(ContactPoint(
                contactType    = 'Service',
                telephone      = dealer['ServicePhoneNumber'],
                hoursAvailable = list(chain(*map(ToOpeningHoursSpecification, dealer['ServiceHours'])))
            ))
        if 'SalesHours' in dealer and dealer['SalesHours'] is not None:
            contact_points.append(ContactPoint(
                contactType    = 'Sales',
                telephone      = dealer['CPOPhoneNumber'],
                hoursAvailable = list(chain(*map(ToOpeningHoursSpecification, dealer['SalesHours'])))
            ))
            openingHours = list(map(ToOpeningHours, dealer['SalesHours']))
        if 'PartsHours' in dealer:
            contact_points.append(ContactPoint(
                contactType    = 'Parts',
                telephone      = dealer['PartsPhoneNumber'],
                hoursAvailable = list(chain(*map(ToOpeningHoursSpecification, dealer['PartsHours'])))
            ))
        business = LocalBusiness(
            id           = dealer['DealerID'],
            faxNumber    = dealer['DealerFaxNo'],
            telephone    = dealer['DealerPhoneNo'],
            email        = dealer['DealerEmail'],
            name         = dealer['DealerName'],
            url          = dealer['DealerURL'],
            contactPoint = contact_points,
            address      = address,
            geo          = geo,
            openingHours = openingHours
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd, sort_keys=True, indent=2)

