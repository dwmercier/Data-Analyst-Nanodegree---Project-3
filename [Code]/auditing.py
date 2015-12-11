#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO: add file description
# TODO: combine overview with auditing?
"""
Your task in this exercise has two steps:

- audit the filename and change the variable 'mapping' to reflect the changes needed to fix 
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this filename,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

street_types = defaultdict(int)

### Regex filters
street_type_re_english = re.compile(r'\S+\.?$', re.IGNORECASE)
street_type_re_french = re.compile(r'^\S+\.?', re.IGNORECASE) # this range covers a large swathe of the Latin character set - reduce to French only?
# street_type_re_french_detect = re.compile(r'[\u00D9-\u00FF]')

# TODO: lists need to have certain types verified (refer to types count file)
# TODO: expand mappings with special cases

### Expected Street type lists

expected_english =['Street', 'Road', 'Drive', 'Avenue', 'Crescent', 'Way', 'Court', 
           'Place', 'Lane', 'Private', 'Boulevard', 'Circle', 'Terrace', 'North', 
           'West', 'East', 'South', 'Sideroad', 'Garden', 'Ridge', 'Park', 'Front', 
           'Plateau', 'Main', 'Walk', 'Gate', 'Line', 'Trail', 'Driveway']

expected_french = ['Rue', 'Chemin', 'Boulevard', 'Avenue', 'Impasse', 'Concession', 
                   'Route', 'Sideroad', 'Montée', 'Promenade', 'Place', 'Voyageur', 
                   'Croissant', 'Principale', 'Parkway', 'Terrace', 'Concourse', ]



### Helper functions

def print_sorted_dict_alpha(street_types):
    for s in sorted(street_types.keys(), key=lambda s: s.lower()):
        print(s, street_types[s])


def print_sorted_dict_frequency(street_types):
    for w in sorted(street_types, key=street_types.get, reverse=True):
        print(w, street_types[w])


def sort_dict_alphabetically(street_types):
    for s in sorted(street_types.keys(), key=lambda s: s.lower()):
        yield(s, street_types[s])


def sort_dict_by_frequency(street_types):
    for s in sorted(street_types, key=street_types.get, reverse=True):
        yield(s, street_types[s])


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit_street_type(street_types, street_name, expected, street_regex):
    m = street_regex.search(street_name)

    if m:
        street_type = m.group()
        if str(street_type) in expected:
            street_types[street_type] += 1


### NEW FUNCTIONS

def check_city():
    pass

    
def list_region():
    pass


def check_dataset():
    pass


# TODO: This works (I think)! Clean up and construct an equivalent French filter. 
# Think of what the filter might miss  - will probably need to split
# street_name and check the first and last entries. UPDATE: This seems to work well, 
# but try comparing it to output using regex. Also normal string comparisons in Python
# check case - you might need to use write a special check with .lower() or .upper())
def audit_street_type_filtered(street_types, street_name):
    
    split_street_name = street_name.split()
    street_pos_english = street_type_re_english.search(split_street_name[-1])
    street_pos_english = street_pos_english.group()
    street_pos_french = street_type_re_french.search(split_street_name[0])
    street_pos_french = street_pos_french.group()
    
    if street_pos_english not in expected_english:
        if street_pos_french not in expected_french:
            street_types[street_pos_english] += 1     


### Main functions

def audit(filename):

    ### ORIGINAL
    # street_types = defaultdict(set) # this variable show up twice

    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    # audit_street_type(street_types, tag.attrib['v'], 
                    #                     expected_english, street_type_re_english)

                    # audit_street_type(street_types, tag.attrib['v'], 
                    #                     expected_french, street_type_re_french)

                    audit_street_type_filtered(street_types, tag.attrib['v'])
    
    # pprint.pprint(list(sort_dict_alphabetically(street_types)))
    # print_sorted_dict_alpha(street_types)

    return street_types


### Main
def main():

    import logging
    import os

    
    filename = "ottawa_canada_sample_small.osm" # TODO: Change to relative path before submission

    # logging.disable(logging.CRITICAL) # Uncomment to disable logging
    logging.basicConfig(filemode='w',
                        filename=os.path.basename(__file__) + ' - log.txt',level=logging.DEBUG,
                        format=' %(asctime)s - %(levelname)s - %(message)s'
                        )
    
    #TODO: resolve logging vs. pprint output
    # def test_audit():
        # logging.debug(pprint.pformat(audit(filename)))
        # logging.debug(pprint.pformat('Special Cases:'))
        # logging.debug(pprint.pformat('Special Cases:'))
        # logging.debug(pprint.pformat(audit(filename)))
    
    logging.debug(pprint.pformat(list(sort_dict_alphabetically(audit(filename)))))
    logging.debug(pprint.pformat(list(sort_dict_by_frequency(audit(filename)))))
    # test_audit()


if __name__ == '__main__':
    main()