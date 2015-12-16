#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO: add file description
# TODO: combine overview with auditing?

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

street_types_frequency = defaultdict(int)
street_types_set = defaultdict(set)

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

unexpected = []

### Helper functions

# def print_sorted_dict_alpha(street_types_frequency):
#     for s in sorted(street_types_frequency.keys(), key=lambda s: s.lower()):
#         print(s, street_types_frequency[s])


# def print_sorted_dict_frequency(street_types_frequency):
#     for w in sorted(street_types_frequency, key=street_types_frequency.get, reverse=True):
#         print(w, street_types_frequency[w])


def sort_dict_alphabetically(street_types_frequency):
    for s in sorted(street_types_frequency.keys(), key=lambda s: s.lower()):
        yield(s, street_types_frequency[s])


def sort_dict_by_frequency(street_types_frequency):
    for s in sorted(street_types_frequency, key=street_types_frequency.get, reverse=True):
        yield(s, street_types_frequency[s])


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def streets_by_frequency(street_types_frequency, street_name, expected, street_regex):
    m = street_regex.search(street_name)

    if m:
        street_type = m.group()
        if str(street_type) in expected:
            street_types_frequency[street_type] += 1


# TODO:  Is regex necessary here? Also normal string comparisons in Python
# check case - you might need to use write a special check with .lower() or .upper())
def filter_street_types(street_types_frequency, street_name):
    '''
    Checks if a street belongs to the expected French or English street
    types. If the street is in neither the street is added to the street_types_frequency
    list and its frequency is incremented by 1.
    '''
    split_street_name = street_name.split()
    street_pos_english = street_type_re_english.search(split_street_name[-1])
    street_pos_english = street_pos_english.group()
    street_pos_french = street_type_re_french.search(split_street_name[0])
    street_pos_french = street_pos_french.group()
    
    if street_pos_english not in expected_english:
        if street_pos_french not in expected_french:
            street_types_frequency[street_pos_english] += 1     


def streets_by_type(street_types_set, street_name, expected, street_regex):
    m = street_regex.search(street_name)
    if m:
        street_type = m.group()
        if street_type in expected:
            street_types_set[street_type].add(street_name)
            


### Main functions
def audit_by_frequency(filename):
    '''
    Returns a list of tuples containing the street type and the number
    of times the street type appears in the dataset.
    '''
    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    streets_by_frequency(street_types_frequency, tag.attrib['v'], 
                                        expected_english, street_type_re_english)
    
    return street_types_frequency


# TODO: Output needs to be in dictionary or json format
def audit_by_type(filename):
    '''
    Returns a dictionary of unique street types, with each street type containing
    a sub-dictionary of the full names of every street of that type.
    '''
    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    streets_by_type(street_types_set, tag.attrib['v'], 
                                        expected_french, street_type_re_french)

    return street_types_set



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
    def test_audit():
        # logging.debug(pprint.pformat('Special Cases:'))
        logging.debug(pprint.pformat(audit_by_type(filename)))
        logging.debug(pprint.pformat(audit_by_frequency(filename)))
        logging.debug(pprint.pformat(list(sort_dict_alphabetically(audit_by_frequency(filename)))))
        logging.debug(pprint.pformat(list(sort_dict_by_frequency(audit_by_frequency(filename)))))
    
    # Run test functions
    test_audit()

if __name__ == '__main__':
    main()