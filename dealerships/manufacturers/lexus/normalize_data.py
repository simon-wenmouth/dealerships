#!/usr/bin/env python3

import os
from   collections import namedtuple
import json
import time

# declare normalized data structure

LocalBusiness = namedtuple('LocalBusiness', ['address', 'geo', 'name', 'url', 'telephone', 'faxNumber', 'email', 'id', 'openingHours', 'openingHoursSpecification'])

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

input_name=os.path.join(directory_name, 'lexus.json')

output_name=os.path.join(directory_name, 'normalized-lexus.json')

# normalize the data

def To24h(val):
    try:
        return time.strftime('%H:%M', time.strptime(val, '%I%p'))
    except:
        return time.strftime('%H:%M', time.strptime(val, '%I:%M%p'))

def ToOpeningHours(days, hours):
    if '-' in days:
        day_from, day_upto = days.split('-')
        day = '{0}-{1}'.format(day_from[0:2], day_upto[0:2])
    else:
        day = days[0:2]
    opens, closes = hours.split('-')
    opens = To24h(opens)
    closes = To24h(closes)
    return '{0} {1}-{2}'.format(day, opens, closes)

def ToOpeningHoursSpecification(days, hours):
    # hours
    opens, closes = hours.split('-')
    opens = To24h(opens)
    closes = To24h(closes)
    # days
    n2i = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
    i2n = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
    n2n = {'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday', 'Thu': 'Thursday', 'Fri': 'Friday', 'Sat': 'Saturday', 'Sun': 'Sunday'}
    loop = []
    if '-' in days:
        vals = days.split('-')
        for i in range(n2i[vals[0]], n2i[vals[1]]+1):
            loop.append(n2n[i2n[i]])
    else:
        loop.append(n2n[days])
    # create opening hours
    results = []
    for day in loop:
        results.append(OpeningHoursSpecification(opens, closes, day))
    return results

businesses = []

with open(input_name, 'r') as fd:
    dealers = json.load(fd)
    for dealer in dealers:
        address = Address(
            streetAddress   = dealer['dealerAddress']['address1'],
            addressRegion   = dealer['dealerAddress']['state'],
            postalCode      = dealer['dealerAddress']['zipCode'],
            addressLocality = dealer['dealerAddress']['city'],
            addressCountry  = 'US'
        )
        geo = GeoCoordinates(
            latitude  = dealer['dealerLatitude'],
            longitude = dealer['dealerLongitude']
        )
        openingHours = []
        openingHoursSpecification = []
        if 'hoursOfOperation' in dealer:
            hoursOfOperation = dealer['hoursOfOperation']
            if 'Sales' in hoursOfOperation:
                sales = hoursOfOperation['Sales']
                for days, hours in sales.items():
                    openingHours.append(ToOpeningHours(days, hours))
                    openingHoursSpecification.extend(ToOpeningHoursSpecification(days, hours))
        business = LocalBusiness(
            id           = dealer['id'],
            telephone    = dealer['dealerPhone'],
            faxNumber    = dealer['dealerFax'],
            name         = dealer['dealerName'],
            url          = dealer['dealerWebUrl'],
            email        = dealer['dealerEmail'],
            address      = address,
            geo          = geo,
            openingHours = openingHours,
            openingHoursSpecification = openingHoursSpecification
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd, sort_keys=True, indent=2)

