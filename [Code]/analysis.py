#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO: modify file description to reflect final functionality
"""
This file combines all the exploratory techniques from Lesson 6 into a single file.
It has been modified to look for French language entries and for the tests to return
values as well as print them
"""
import xml.etree.cElementTree as ET
import pprint
import re

# Regular expressions for categorizing tag content format
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
#TODO: refine or remove frenchchars
frenchchars = re.compile(r'[\u00D9-\u00FF]') # Subset of Latin charset - rough and inaccurate



### Helper Functions

def filter_key_types(element, keys):
    '''
    Filter each tag's address tag by character type.
    '''
    if element.tag == "tag":
        tag_k = element.get('k')

        if frenchchars.search(element.get('v')):
            keys['frenchchars'] +=1

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

def count_tags(filename):
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


def process_tags(filename):
    '''
    Return a count of each address tag by character type. Uses filter_key_types as helper function.
    '''
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "frenchchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = filter_key_types(element, keys)

    return keys


def process_users(filename):
    '''
    Returns a set of unique user IDs ("uid")
    '''
    users = set()
    uids = []

    for _, element in ET.iterparse(filename):
        if element.get('uid'):
            uid = element.get('uid')
            uids.append(str(uid))

    users = set(uids)

    return users



def main():

    import logging
    import os

    # Path to dataset
    filename = 'ottawa_canada_sample_small.osm'

    # logging.disable(logging.CRITICAL) # Uncomment to disable logging
    logging.basicConfig(filemode='w',
                        filename=os.path.basename(__file__) + ' - log.txt',level=logging.DEBUG,
                        format=' %(asctime)s - %(levelname)s - %(message)s'
                        )

    # Test functions for main functions

    def test_count_tags():

        tags = count_tags(filename)
        logging.debug(pprint.pformat('Tag Counts:',))
        logging.debug(pprint.pformat(tags))

    def test_process_tags():

        keys = process_tags(filename)
        logging.debug(pprint.pformat('Tag type Counts:',))
        logging.debug(pprint.pformat(keys))


    def test_users():

        users = process_users(filename)
        logging.debug(pprint.pformat('Users:',))
        logging.debug(pprint.pformat(users))


    test_count_tags()
    test_process_tags()
    test_users()

if __name__ == "__main__":
    main()