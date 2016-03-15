#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pprint
import re
import xml.etree.cElementTree as ET
from collections import defaultdict

# Globals
street_types_frequency = defaultdict(int)
street_types_set = defaultdict(set)
city_names_set = set()

# Regular expressions for categorizing tag content format
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
extra_spaces = re.compile(r'(( ) +)')

# Language regexes
street_type_re_english = re.compile(r'\S+\.?$', re.IGNORECASE)
street_type_re_french = re.compile(r'^\S+\.?', re.IGNORECASE)

# Expected Street type lists
expected_english = ['Street', 'Road', 'Drive', 'Avenue', 'Crescent', 'Way',
                    'Court', 'Place', 'Lane', 'Private', 'Boulevard', 'Circle',
                    'Terrace', 'North', 'West', 'East', 'South', 'Sideroad',
                    'Garden', 'Ridge', 'Park', 'Front', 'Plateau', 'Main',
                    'Walk',
                    'Gate', 'Line', 'Trail', 'Driveway', 'Green', 'Square',
                    'Grove', 'Bay', 'Square', 'Heights', 'Row']

expected_french = ['Rue', 'Chemin', 'Boulevard', 'Avenue', 'Impasse',
                   'Concession', 'Route', 'Sideroad', 'Montée', 'Promenade',
                   'Place', 'Voyageur', 'Croissant', 'Principale', 'Parkway',
                   'Terrace', 'Concourse', 'Allée']

expected = expected_english  + expected_french


### Helper functions

def sort_by_frequency(street_types_frequency):
    """Sorts the street_types_frequency dict in descending order

    Args:
        street_types_frequency: A global dict that stores the frequency of
        each street type's occurrence.

    Returns:
        None
    """
    for s in sorted(street_types_frequency,
                    key=street_types_frequency.get,
                    reverse=True):
        yield (s, street_types_frequency[s])


def is_street_name(elem):
    return elem.attrib['k'] == "addr:street"


def is_city_name(elem):
    return elem.attrib['k'] == "addr:city"


def filter_key_types(element, keys):
    if element.tag == "tag":
        tag_k = element.get('k')

        if extra_spaces.search(tag_k):
            keys['extra_spaces'] += 1

        elif lower.search(tag_k):
            keys['lower'] += 1

        elif lower_colon.search(tag_k):
            keys['lower_colon'] += 1

        elif problemchars.search(tag_k):
            keys['problemchars'] += 1

        else:
            keys['other'] += 1

    return keys


### Main functions

def count_tags_by_element(filename):
    """Counts up each element by their type.

    Args:
       filename: A string containing the pathname of an .osm file.

    Returns:
        A dict containing tag types as keys and a count as a value.
    """
    tag_counts = {}

    for _, element in ET.iterparse(filename):
        tag_counts.setdefault(element.tag, 0)
        tag_counts[element.tag] += 1

    return tag_counts


def count_tags_by_char_content(filename):
    """Counts up each each address tag by their character content.
     Uses filter_key_types as helper function.

    Args:
       filename: A string containing the pathname of an .osm file.

    Returns:
        A dict containing character types as keys and a count as a value.
    """
    keys = {"lower": 0,
            "lower_colon": 0,
            "problemchars": 0,
            "other": 0,
            "extra_spaces": 0
            }

    for _, element in ET.iterparse(filename):
        keys = filter_key_types(element, keys)

    return keys


def list_users(filename):
    """Generates a set of unique user IDs ("uid")

    Args:
       filename: A string containing the pathname of an .osm file.

    Returns:
        A set of unique user ids.
    """
    uids = []

    for _, element in ET.iterparse(filename):
        if element.get('uid'):
            uid = element.get('uid')
            uids.append(str(uid))

    users = set(uids)

    return users


def check_unexpected_street_types(output_type, street_name):
    """Checks if a given street's type is not in the global expected list of street types.

    Checks the street name against the global list containing all expected street
    types. If one of the known types in the street name, the function breaks,
    otherwise it modifies the sort type specified by the user.

    Args:
        output_type: A string specifying how to display the output.
        street_name: A string containing the name of a street.

    Returns:
        Modifies the global variable corresponding to the output_type.
    """
    is_expected = False

    for e in expected:
        if e in street_name:
            is_expected = True
            break

    if is_expected == False:
        if output_type == 'type':
            street_types_set[street_name].add(street_name)

        elif output_type == 'frequency':
            street_types_frequency[street_name] += 1


def check_expected_street_types(output_type, street_name, language):
    """Checks if a street's type belongs to the global list of expected street
    types.

    Args:
        output_type: A string specifying how to display the output.
        street_name: A string containing the name of a street.
        language: A string specifying which language to use. Accepts 'French'
            or Endlish

    Returns:
        Modifies the global variable corresponding to the output_type.
    """
    if language == 'English':
        match = street_type_re_english.search(street_name)

    if language == 'French':
        match = street_type_re_french.search(street_name)

    if match:
        street_type = match.group()

        if street_type in expected:
            if output_type == 'type':
                street_types_set[street_type].add(street_name)

            elif output_type == 'frequency':
                street_types_frequency[street_type] += 1


def parse_output(street_types_frequency, street_types_set, city_names_set):
    """Checks if any of street_types_frequency, street_types_set or
        city_names_set globals have content and returns those with values.

    Args:
        street_types_frequency: An integer representing the frequency of each
            street type.

        street_types_set: A dict with unique street types as keys and
            values are all street names of that street type.

        city_names_set: A set of all unique city names in addr:city

    Returns:
        None
    """
    if len(street_types_frequency) > 1:
        ranked_street_types = list(sort_by_frequency(street_types_frequency))
        return ranked_street_types

    elif len(street_types_set) > 1:
        return street_types_set

    elif len(city_names_set) > 1:
        return city_names_set


def audit(filename, output_type, filter, language='English'):
    """Runs an audit on an Open Street Map (.osm) data file.

    Loads a user-specified OSM file and uses ElementTree to parse 
    top level xml elements and their children. The audit can be adjusted
    according to the args below:

    Args:
        filename: A string containing the pathname of an .osm file.
        output_type: A string specifying how to display the output.
            Accepts 'frequency' or 'type'.
            'frequency' will direct the audit to show how many times each street
            type occurs.
            'type' will direct the audit to show a dict of unique street
            types containing every street name of that street type.

        filter: Filters the output. Accepts 'expected', 'unexpected', or 'city'.
            'expected' outputs streets whose type has a match in the expected
            list.
            'unexpected' outputs streets whose type doesn't have a match in
            the expected list.
            'city' outputs all unique city names.

        language: Sets the language to use. Accepts 'French'
            or 'English' and will include only the streets that match an
            associated regex for the language. Not used for audits using the
            unexpected filter type or the city filter.
    
    Returns:
        If output_type is set to 'frequency' returns a list of tuples with
        with the given address and a count of how many times that address type
        occurs in the file.

            Example output:
            [   ('ch. Pagé Rd.', 25),
                ('Highway 7', 24),
                ('Highway 15', 16),
                ('Highway  17', 9),
                ('Des Grands Champs', 7),
                ('Highway 511', 6),
                ('McCulloughs Landing', 5),
                ('Highway  15', 4),
                ('Old Highway 17', 4)
            ]
            
        If output_type is set to 'type' returns a dict mapping the address type 
        as a key and all the streets that match that type in a dict the value
        of each street type of that type.
        
            Example output:
            defaultdict(<class 'set'>,
            {   'Avenue': {   'Acacia Avenue',
                              'Admiral Avenue',
                              'Aline Avenue'},
                'Boulevard': {   'Barker Boulevard',
                                 'Belcourt Boulevard',
                                 'Bisley Boulevard',}})

        If the filter is set to 'city' returns a dict that list all unique city 
        entries.

            Example output:
            {   'Almonte',
                'Appleton',
                'Arnprior',
                'City of Ottawa'}
    """
    global street_types_frequency
    global street_types_set
    global city_names_set

    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):

                    if filter == 'unexpected':
                        check_unexpected_street_types(output_type,
                                                      tag.attrib['v'])

                    if filter == 'expected':
                        check_expected_street_types(output_type,
                                                    tag.attrib['v'], language)

                elif filter == 'city':
                    if is_city_name(tag):
                        city_names_set.add(tag.attrib['v'])

    results = parse_output(street_types_frequency, street_types_set,
                           city_names_set)

    # Reset global variables
    street_types_frequency = defaultdict(int)
    street_types_set = defaultdict(set)
    city_names_set = set()

    return results


def main():
    import logging
    import os

    filename = "..\\[Data]\\ottawa_canada_sample.osm"

    # Line below toggles logging output to external file - uncomment to disable
    # logging.disable(logging.CRITICAL) # Uncomment to disable logging
    logging.basicConfig(filemode='w',
                        filename='..\\[Output]\\' + os.path.basename(
                            __file__) + ' - output.txt',
                        level=logging.DEBUG,
                        format='%(levelname)s - %(message)s'
                        )

    def run_count_tags_by_element():
        tags = count_tags_by_element(filename)
        print('\n' + 'Tag counts:', )
        pprint.pprint(tags, indent=4)

        logging.debug(pprint.pformat('Tag Counts:', ))
        logging.debug(pprint.pformat(tags, indent=4))

    def run_count_tags_by_char_content():
        keys = count_tags_by_char_content(filename)
        print('\n' + 'Tag type counts:', )
        pprint.pprint(keys, indent=4)

        logging.debug(pprint.pformat('Tag type Counts:', ))
        logging.debug(pprint.pformat(keys, indent=4))

    def run_list_users():
        users = list_users(filename)
        print('\n' + 'Unique users:', )
        pprint.pprint(users, indent=4)

        logging.debug(pprint.pformat('Users:', ))
        logging.debug(pprint.pformat(users, indent=4))

    def run_audit(filename, output_type, filter, language):
        print('\n' + "Running audit on " + filename)
        print("Sorting by: " + output_type)
        print("Filtering by: " + filter)
        print("Regex language is: " + str(language) + '\n')
        output = audit(filename, output_type, filter, language)
        pprint.pprint(output, indent=4)

        logging.debug(pprint.pformat("Running audit on " + filename))
        logging.debug(pprint.pformat("Sorting by: " + output_type))
        logging.debug(pprint.pformat("Filtering by: " + filter))
        logging.debug(pprint.pformat("Regex language is: " + str(language)))
        logging.debug(pprint.pformat(output, indent=4))

    run_audit(filename, 'frequency', 'unexpected', 'English')
    run_audit(filename, 'type', 'expected', 'French')
    run_audit(filename, 'frequency', 'city')
    run_count_tags_by_element()
    run_count_tags_by_char_content()
    run_list_users()


if __name__ == '__main__':
    main()
