#!/usr/bin/env python3

import os
import glob
import json

# declare input and output file names

directory_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))

input_names=glob.glob(os.path.join(directory_name, 'normalized-*.json'))

output_name=os.path.join(directory_name, 'normalized.json')

dealers = {}

for input_name in input_names:
    with open(input_name, 'r') as fd:
        print (input_name)
        items = json.load(fd)
        for item in items:
            if 'url' in item and item['url'] is not None:
                url = item['url'].replace('http://', '').lower()
                if not url in dealers:
                    dealers[url] = item
            else:
                name = item['name'].lower()
                if not name in dealers:
                    dealers[name] = item

with open(output_name, 'w') as fd:
    json.dump(list(dealers.values()), fd, sort_keys=True, indent=2)

