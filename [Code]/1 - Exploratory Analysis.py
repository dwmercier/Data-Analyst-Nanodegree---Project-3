#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Your task is to use the iterative parsing to process the map file and
find out not only what tags are there, but also how many, to get the
feeling on how much of which data you can expect to have in the map.
Fill out the count_tags function. It should return a dictionary with the 
tag name as the key and number of times this tag can be encountered in 
the map as value.

Note that your code will be tested with a different data file than the 'example.osm'
"""
import xml.etree.cElementTree as ET
import pprint
import re

# Regular expressions for categorizing formatting of tag contents
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
# TODO: Write a new regex statement for distinguishing French names and characters

# Path to dataset
filename = 'ottawa_canada_sample_small.osm'
tree = ET.parse(filename)
root = tree.getroot()  

def count_tags(filename):
    '''
    Take a count of all the different tag types in the file.
    Iterate over all elements and their children, add unique tags
    to the tag_counts dictionary and set their value to 0 using the 
    setdefault() method. Add 1 to the tag's value for each occurrence 
    of the tag.
    '''

    tag_counts = {}

    for child in root.iter():
        tag_counts.setdefault(child.tag, 0)
        tag_counts[child.tag] += 1

    return tag_counts


# TODO: Add functionality for distinguishing French addresses
def filter_key_types(element, keys):
    '''
    Filter each tag's address tag by character type. 
    '''
    if element.tag == "tag":
        tag_k = element.get('k')

        if lower.search(tag_k):
            keys['lower'] +=1

        elif lower_colon.search(tag_k):
            keys['lower_colon'] +=1
 
        elif problemchars.search(tag_k):
            keys['problemchars'] +=1

        else:
            keys['other'] += 1

    return keys


def process_tags(filename):
    '''
    Return a count of each address tag by character type. Uses filter_key_types.
    '''
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = filter_key_types(element, keys)

    return keys


### Users is not particularly useful information, will probably remove in future
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
    
    # logging.disable(logging.CRITICAL) # Uncomment to disable logging
    logging.basicConfig(filemode='w',
                        filename=os.path.basename(__file__) + ' - log.txt',level=logging.DEBUG,
                        format=' %(asctime)s - %(levelname)s - %(message)s'
                        )
    
    def test_count_tags():

        tags = count_tags(filename)
        logging.debug(pprint.pformat('Tag Counts:',))
        logging.debug(pprint.pformat(tags))

    
    def test_tags():

        keys = process_tags(filename)
        logging.debug(pprint.pformat('Tag type Counts:',))
        logging.debug(pprint.pformat(keys))


    def test_users():

        users = process_users(filename)
        logging.debug(pprint.pformat('Users:',))
        logging.debug(pprint.pformat(users))

    test_count_tags()
    test_tags()
    test_users()

if __name__ == "__main__":
    main()