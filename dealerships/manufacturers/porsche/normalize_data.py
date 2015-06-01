#!/usr/bin/env python

import os
from   collections import namedtuple
import json
import time

# declare normalized data structure

LocalBusiness = namedtuple('LocalBusiness', ['department', 'address', 'name', 'url', 'telephone', 'id'])

Department = namedtuple('Department', ['name', 'telephone', 'openingHours', 'openingHoursSpecification'])

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

input_name=os.path.join(directory_name, 'porsche.json')

output_name=os.path.join(directory_name, 'normalized-porsche.json')

# normalize the data

def ToOpeningHours(text):
    try:
        # Monday-Friday: 9:00 - 8:00
        # Saturday: 9:00 - 6:00
        # Sunday: Closed
        text = text.replace('&nbsp;', ' ')
        i = text.index(':')
        days = text[:i].strip()
        hours = text[i+1:].strip()
        if hours == 'Closed':
            return None
        hours = [x.strip() for x in hours.split('-')]
        opens = time.strftime('%H:%M', time.strptime(hours[0]+'AM', '%I:%M%p'))
        closes = time.strftime('%H:%M', time.strptime(hours[1]+'PM', '%I:%M%p'))
        if '-' in days:
            day_from, day_upto = days.split('-')
            days = '{0}-{1}'.format(day_from[:2], day_upto[:2])
        else:
            days = days[:2]
        return '{0} {1}-{2}'.format(days, opens, closes)
    except:
        # the hours is an ugly free form piece of text ... will eventually handle all the patterns
        return None

def ToOpeningHoursSpecification(text):
    try:
        i = text.index(':')
        days = text[:i].strip()
        hours = text[i+1:].strip()
        if hours == 'Closed':
            return None
        # hours
        hours = [x.strip() for x in hours.split('-')]
        opens = time.strftime('%H:%M', time.strptime(hours[0]+'AM', '%I:%M%p'))
        closes = time.strftime('%H:%M', time.strptime(hours[1]+'PM', '%I:%M%p'))
        # days
        n2i = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
        i2n = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
        n2n = {'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday', 'Thu': 'Thursday', 'Fri': 'Friday', 'Sat': 'Saturday', 'Sun': 'Sunday'}
        loop = []
        if '-' in days:
            vals = days.split('-')
            for i in range(n2i[vals[0][:3]], n2i[vals[1][:3]]):
                loop.append(n2n[i2n[i]])
        else:
            loop.append(days)
        # create opening hours
        results = []
        for day in loop:
            results.append(OpeningHoursSpecification(opens, closes, day))
        return results
    except:
        return None

businesses = []

with open(input_name, 'r') as fd:
    dealers = json.load(fd)
    for dealer in dealers:
        address = Address(
            streetAddress   = dealer['address']['street'],
            addressRegion   = dealer['address']['region'],
            postalCode      = dealer['address']['postalcode'],
            addressLocality = dealer['address']['city'],
            addressCountry  = 'US'
        )
        departments = []
        for name in ['service', 'sales', 'parts']:
            if name in dealer['details']:
                service = dealer['details'][name]
                hours = [x.strip() for x in service['hours'].split('<br />')]
                departments.append(Department(
                    name         = name.title(),
                    telephone    = service['phone'],
                    openingHours = [ x for x in map(ToOpeningHours, hours) if x is not None],
                    openingHoursSpecification = [x for x in map(ToOpeningHoursSpecification, hours) if x is not None]
                ))
        business = LocalBusiness(
            id           = dealer['id'],
            telephone    = dealer['address']['phone'],
            name         = dealer['name'],
            url          = dealer['url'],
            department   = departments,
            address      = address
        )
        businesses.append(business)

with open(output_name, 'w') as fd:
    json.dump(list(map(ToDictionary, businesses)), fd)

