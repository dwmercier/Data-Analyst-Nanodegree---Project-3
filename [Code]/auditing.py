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

# ToDo: Check if this is necessary - I believe sets sort alphabetically by default
def sort_alphabetically(street_types_frequency):
    for s in sorted(street_types_frequency.keys(), key=lambda s: s.lower()):
        yield(s, street_types_frequency[s])


def sort_by_frequency(street_types_frequency):
    for s in sorted(street_types_frequency, key=street_types_frequency.get, reverse=True):
        yield(s, street_types_frequency[s])


# def sort_by_frequency_2(street_types_set):
#     # print(street_types_set)
#     for s in sorted(street_types_set, key=street_types_set.get, reverse=True):
#         yield(s, street_types_set[s])


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
    users = set()

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

# def unexpected_streets_by_type(street_types, street_name):
#     '''
#     Checks if a street belongs to the expected French or English street
#     types. If the street is in neither the street is added to street_types_set
#     list and its frequency is incremented by 1.
#     '''
#     street_name_english, street_name_french = search_for_streets(street_types_set,
#                                                                  street_name)
#
#     if street_name_english not in expected:
#         if street_name_french not in expected:
#             street_types_set[street_name_english].add(street_name)
#
#     if street_name_french not in expected:
#         if street_name_english not in expected:
#             street_types_set[street_name_french].add(street_name)
#
#     return street_types_set
#
#
# def unexpected_streets_by_frequency(street_types_frequency, street_name):
#     '''
#     Checks if a street belongs to the expected French or English street
#     types. If the street is in neither the street is added to the street_types_frequency
#     list and its frequency is incremented by 1.
#     '''
#     street_name_english, street_name_french = search_for_streets(street_types_frequency,
#                                                                  street_name)
#
#     if street_name_english not in expected:
#         if street_name_french not in expected:
#             street_types_frequency[street_name_english] += 1
#
#     if street_name_french not in expected:
#         if street_name_english not in expected:
#             street_types_frequency[street_name_french] += 1
#
#     return street_types_frequency


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

# def streets_by_type(street_types_set, street_name, street_regex):
#     m = street_regex.search(street_name)
#
#     if m:
#         street_type = m.group()
#         if street_type in expected:
#             street_types_set[street_type].add(street_name)
#
#
# def streets_by_frequency(street_types_frequency, street_name, street_regex):
#     m = street_regex.search(street_name)
#
#     if m:
#         street_type = m.group()
#         if str(street_type) in expected:
#             street_types_frequency[street_type] += 1


### Main functions
# def audit_by_frequency(filename):
#     '''
#     Returns a list of tuples containing the street type and the number
#     of times the street type appears in the dataset.
#     '''
#     for event, elem in ET.iterparse(filename, events=("start",)):
#         if elem.tag == "node" or elem.tag == "way":
#             for tag in elem.iter("tag"):
#                 if is_street_name(tag):
#                     streets_by_frequency(street_types_frequency,
#                                          tag.attrib['v'],
#                                          street_type_re_english)
#
#     return street_types_frequency
#
#
# def audit_by_type(filename):
#     '''
#     Returns a dictionary of unique street types, with each street type containing
#     a sub-dictionary of the full names of every street of that type.
#     '''
#     for event, elem in ET.iterparse(filename, events=("start",)):
#         if elem.tag == "node" or elem.tag == "way":
#             for tag in elem.iter("tag"):
#                 if is_street_name(tag):
#                     streets_by_type(street_types_set,
#                                     tag.attrib['v'],
#                                     street_type_re_english)
#
#     return street_types_set


# def audit_by_unexpected_type(filename):
#     '''
#
#     '''
#     for event, elem in ET.iterparse(filename, events=("start",)):
#         if elem.tag == "node" or elem.tag == "way":
#             for tag in elem.iter("tag"):
#                 if is_street_name(tag):
#                     unexpected_streets_by_type(street_types_set, tag.attrib['v'])
#
#     return street_types_set
#
#
# def audit_by_unexpected_frequency(filename):
#     '''
#
#     '''
#     for event, elem in ET.iterparse(filename, events=("start",)):
#         if elem.tag == "node" or elem.tag == "way":
#             for tag in elem.iter("tag"):
#                 if is_street_name(tag):
#                     unexpected_streets_by_frequency(street_types_frequency, tag.attrib['v'])
#
#     return street_types_frequency


# def audit_by_unexpected(filename, sort_type):
#     for event, elem in ET.iterparse(filename, events=("start",)):
#         if elem.tag == "node" or elem.tag == "way":
#             for tag in elem.iter("tag"):
#                 if is_street_name(tag):
#                     check_unexpected_street_types(sort_type, tag.attrib['v'])
#
#     return street_types_frequency, street_types_set


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



###### Return City names code
# def city_names_by_type(city_names_list, city_name):
#     city_names_list.add(city_name)
#
# def is_city_name(elem):
#     return (elem.attrib['k'] == "addr:city")
#
# def audit_cities(filename):
#     for event, elem in ET.iterparse(filename, events=("start",)):
#         if elem.tag == "node" or elem.tag == "way":
#             for tag in elem.iter("tag"):
#                 if is_city_name(tag):
#                     city_names_list.add(tag.attrib['v'])
#
#     return city_names_list


### Main
def main():

    import logging
    import os

    filename = "ottawa_canada_sample.osm" # TODO: Change to relative path before submission
    language = 'English'

    # logging.disable(logging.CRITICAL) # Uncomment to disable logging
    logging.basicConfig(filemode='w',
                        filename=os.path.basename(__file__) + ' - output.txt',level=logging.DEBUG,
                        format=' %(asctime)s - %(levelname)s - %(message)s'
                        )


    #TODO: resolve logging vs. pprint output
    # def test_audit():
        # logging.debug(pprint.pformat('Special Cases:'))
        # logging.debug(pprint.pformat(audit_by_type(filename)))
        # logging.debug(pprint.pformat(audit_by_frequency(filename)))
        # logging.debug(pprint.pformat(list(sort_dict_alphabetically(audit_by_frequency(filename)))))
        # logging.debug(pprint.pformat(list(sort_dict_by_frequency(audit_by_frequency(filename)))))


        # Test functions for main functions

    def test_count_tags_by_element():

        tags = count_tags_by_element(filename)
        logging.debug(pprint.pformat('Tag Counts:',))
        logging.debug(pprint.pformat(tags))


    def test_count_tags_by_char_content():

        keys = count_tags_by_char_content(filename)
        logging.debug(pprint.pformat('Tag type Counts:',))
        logging.debug(pprint.pformat(keys))


    def test_list_users():

        users = list_users(filename)
        logging.debug(pprint.pformat('Users:',))
        logging.debug(pprint.pformat(users))


    # def test_audit_by_unexpected_type():
    #
    #     unexpected_type = audit_by_unexpected_type(filename)
    #     logging.debug(pprint.pformat('Unexpected (by type):',))
    #     logging.debug(pprint.pformat(unexpected_type))

    # def test_audit_by_unexpected_frequency():
    #
    #     unexpected_frequency = audit_by_unexpected_frequency(filename)
    #     logging.debug(pprint.pformat('Unexpected (by frequency):',))
    #     # logging.debug(pprint.pformat(list(sort_dict_by_frequency_2(street_types_frequency))))
    #     logging.debug(pprint.pformat(unexpected_frequency))

    # def test_audit_by_type():
    #
    #     expected_type = audit_by_type(filename)
    #     logging.debug(pprint.pformat('Expected (by type):',))
    #     logging.debug(pprint.pformat(expected_type))
    #
    #
    # def test_audit_by_frequency():
    #
    #     expected_frequency = audit_by_frequency(filename)
    #     logging.debug(pprint.pformat('Expected (by frequency):',))
    #     logging.debug(pprint.pformat(expected_frequency))





    # def test_audit_unexpected_types(sort_type):
    #     unexpected_types = audit_by_unexpected(filename, sort_type)
    #     # pprint.pformat('Unexpected (by frequency):',)
    #     # logging.debug(pprint.pformat(list(sort_dict_by_frequency_2(street_types_frequency))))
    #     logging.debug(pprint.pformat(unexpected_types))


    def test_audit(filename, sort_type, filter, language):
        print('\n' + "Running audit on " + filename)
        print("Sorting by: " + sort_type)
        print("Filtering by: " + filter)
        print("Regex language is: " + str(language)+ '\n')
        output = audit(filename, sort_type, filter, language)
        # pprint.pformat('Unexpected (by frequency):',)
        # logging.debug(pprint.pformat(list(sort_dict_by_frequency_2(street_types_frequency))))
        pprint.pprint(output)

    # test_count_tags_by_element()
    # test_count_tags_by_char_content()
    # test_list_users()

    # Run test functions
    # test_audit()
    # test_count_tags_by_element()
    # test_count_tags_by_char_content()
    # test_list_users()

    # test_audit_by_type()
    # test_audit_by_frequency()

    # test_audit_by_unexpected_type()
    # test_audit_by_unexpected_frequency()


    # EXPERIMENTAL
    # test_audit_by_unexpected_type_single_regex()
    # def test_audit_city_by_type():
    #
    #     expected_type = audit_cities(filename)
    #     logging.debug(pprint.pformat('City (by type):',))
    #     logging.debug(pprint.pformat(expected_type))

    # test_audit_city_by_type()

    # test_audit_unexpected_types('type')
    # test_audit_unexpected_types('frequency')
    test_audit(filename, 'frequency', 'unexpected', 'English')
    test_audit(filename, 'frequency', 'unexpected', 'French')

if __name__ == '__main__':
    main()