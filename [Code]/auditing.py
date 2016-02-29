#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO: add file description

"""

"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint



# Globals
street_types_frequency = defaultdict(int)
street_types_set = defaultdict(set)
city_names_list = set()

# Regular expressions for categorizing tag content format
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
extra_spaces = re.compile(r'(( ) +)')

# Language regexes
street_type_re_english = re.compile(r'\S+\.?$', re.IGNORECASE)
street_type_re_french = re.compile(r'^\S+\.?', re.IGNORECASE)

# Expected Street type lists

expected_english =['Street', 'Road', 'Drive', 'Avenue', 'Crescent', 'Way', 'Court',
                   'Place', 'Lane', 'Private', 'Boulevard', 'Circle', 'Terrace', 'North',
                   'West', 'East', 'South', 'Sideroad', 'Garden', 'Ridge', 'Park', 'Front',
                   'Plateau', 'Main', 'Walk', 'Gate', 'Line', 'Trail', 'Driveway', 'Green',
                   'Square', 'Grove', 'Bay', 'Square', 'Heights', 'Row']

expected_french = ['Rue', 'Chemin', 'Boulevard', 'Avenue', 'Impasse', 'Concession',
                   'Route', 'Sideroad', 'Montée', 'Promenade', 'Place', 'Voyageur',
                   'Croissant', 'Principale', 'Parkway', 'Terrace', 'Concourse','Allée']

expected = expected_english + expected_french



### Helper functions

def sort_by_frequency(street_types_frequency):
    for s in sorted(street_types_frequency, key=street_types_frequency.get, reverse=True):
        yield(s, street_types_frequency[s])


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def is_city_name(elem):
    return (elem.attrib['k'] == "addr:city")


def filter_key_types(element, keys):
    '''
    Filter each tag's address tag by character type.
    '''
    if element.tag == "tag":
        tag_k = element.get('k')

        if extra_spaces.search(tag_k):
            keys['extra_spaces'] +=1

        elif lower.search(tag_k):
            keys['lower'] +=1

        elif lower_colon.search(tag_k):
            keys['lower_colon'] +=1

        elif problemchars.search(tag_k):
            keys['problemchars'] +=1

        else:
            keys['other'] +=1

    return keys



### Main functions

def count_tags_by_element(filename):
    '''
    Take a count of all the different tag types in the file.
    Iterate over all elements and their children, add unique tags
    to the tag_counts dictionary and set their value to 0 using the
    setdefault() method. Add 1 to the tag's value for each occurrence
    of the tag.
    '''

    tag_counts = {}

    for _, element in ET.iterparse(filename):
        tag_counts.setdefault(element.tag, 0)
        tag_counts[element.tag] += 1

    return tag_counts


def count_tags_by_char_content(filename):
    '''
    Return a count of each address tag by character type. Uses filter_key_types as helper function.
    '''
    keys = {"lower": 0,
            "lower_colon": 0,
            "problemchars": 0,
            "other": 0,
            "extra_spaces": 0
            }

    for _, element in ET.iterparse(filename):
        keys = filter_key_types(element, keys)

    return keys


def list_users(filename, uids=[]):
    '''
    Returns a set of unique user IDs ("uid")
    '''

    for _, element in ET.iterparse(filename):
        if element.get('uid'):
            uid = element.get('uid')
            uids.append(str(uid))

    users = set(uids)

    return users


def check_unexpected_street_types(sort_type, street_name):
    '''
    Checks if any of the expected street types appear in the street
    name. If not added to either street_types_set or street)type_list.

    input
    sort_type = either str'type' or 'frequency'

    output
    '''

    is_expected = False

    for e in expected:
        if e in street_name:
            is_expected = True
            break

    if is_expected == False:
        if sort_type == 'type':
            street_types_set[street_name].add(street_name)

        elif sort_type == 'frequency':
            street_types_frequency[street_name] += 1


def check_expected_street_types(sort_type, street_name, language):
    if language == 'English':
        match = street_type_re_english.search(street_name)

    if language == 'French':
        match = street_type_re_french.search(street_name)

    if match:
        street_type = match.group()

        if street_type in expected:
            if sort_type == 'type':
                street_types_set[street_type].add(street_name)

            elif sort_type == 'frequency':
                street_types_frequency[street_type] += 1


def parse_output(street_types_frequency, street_types_set, city_names_list):
    if len(street_types_frequency) > 1:
        ranked_street_types = list(sort_by_frequency(street_types_frequency))
        return ranked_street_types

    elif len(street_types_set) > 1:
        return street_types_set

    elif len(city_names_list) > 1:
        return city_names_list


def audit(filename, sort_type, filter, language):
    global street_types_frequency
    global street_types_set
    global city_names_list

    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):

                    if filter == 'unexpected':
                        check_unexpected_street_types(sort_type, tag.attrib['v'])

                    if filter == 'expected':
                        check_expected_street_types(sort_type, tag.attrib['v'], language)

                elif filter == 'city':
                    if is_city_name(tag):
                        city_names_list.add(tag.attrib['v'])

    results = parse_output(street_types_frequency, street_types_set, city_names_list)

    # Reset global variables
    street_types_frequency = defaultdict(int)
    street_types_set = defaultdict(set)
    city_names_list = set()

    return results



def main():

    import logging
    import os


    filename = "..\\[Data]\\ottawa_canada_sample.osm"

    # Line below toggles logging output to external file - uncomment to disable
    # logging.disable(logging.CRITICAL) # Uncomment to disable logging
    logging.basicConfig(filemode='w',
                        filename='..\\[Output]\\' + os.path.basename(__file__) + ' - output.txt',
                        level=logging.DEBUG,
                        format='%(levelname)s - %(message)s'
                        )


    def run_count_tags_by_element():
        tags = count_tags_by_element(filename)
        print('\n' + 'Tag counts:',)
        pprint.pprint(tags, indent=4)

        logging.debug(pprint.pformat('Tag Counts:',))
        logging.debug(pprint.pformat(tags, indent=4))


    def run_count_tags_by_char_content():
        keys = count_tags_by_char_content(filename)
        print('\n' + 'Tag type counts:',)
        pprint.pprint(keys, indent=4)

        logging.debug(pprint.pformat('Tag type Counts:',))
        logging.debug(pprint.pformat(keys, indent=4))


    def run_list_users():
        users = list_users(filename)
        print('\n' + 'Unique users:',)
        pprint.pprint(users, indent=4)

        logging.debug(pprint.pformat('Users:',))
        logging.debug(pprint.pformat(users, indent=4))


    def run_audit(filename, sort_type, filter, language):
        print('\n' + "Running audit on " + filename)
        print("Sorting by: " + sort_type)
        print("Filtering by: " + filter)
        print("Regex language is: " + str(language)+ '\n')
        output = audit(filename, sort_type, filter, language)
        pprint.pprint(output, indent=4)

        logging.debug(pprint.pformat("Running audit on " + filename))
        logging.debug(pprint.pformat("Sorting by: " + sort_type))
        logging.debug(pprint.pformat("Filtering by: " + filter))
        logging.debug(pprint.pformat("Regex language is: " + str(language)))
        logging.debug(pprint.pformat(output, indent=4))

    run_audit(filename, 'frequency', 'expected', 'English')
    run_audit(filename, 'frequency', 'expected', 'French')
    run_audit(filename, 'frequency', 'unexpected', 'French')
    run_count_tags_by_element()
    run_count_tags_by_char_content()
    run_list_users()



if __name__ == '__main__':
    main()