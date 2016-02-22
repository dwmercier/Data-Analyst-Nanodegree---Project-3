#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO: add file description
'''

'''
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import codecs
import json

# TODO: How to separate English street names that happen to be in expected_french (e.g Concession Road)?


# apt_num = re.compile(r'(Suite|Ste)\s?([-0-9A-Z]+)')
# addr_num = re.compile(r'([0-9]+)[^a-z]\s?')
# no_prefix_num = re.compile(r'[0-9]')
# postcode_num = re.compile('\d\d\d\d\d')
# state_name = re.compile(r'nv|nevada', re.IGNORECASE)

# Unsure: Heights, Landing, Green, Loop, Grove, Pathway, Rand, Path, Bay, Row, Shore, Promenade(English), Allée, Square, Canyon
# All
# Edge Cases: 10e Avenue Ouest, {'Regional Road 174'}, Highway 15, {'prom. des Aubépine Dr.'}, 'County Road 11', Old Highway 17'

# English regex matching patterns

# ToDo: add regex patterns for less common street types found in audit
type_regexes = [
    [re.compile(r'\sSt\.?$'), 'Street'],
    [re.compile(r'\s?Blvd\.?\s|\sBlvd\.?$'), 'Boulevard'],
    [re.compile(r'\s?Ave\.?\s|\sAve\.?$'), 'Avenue'],
    [re.compile(r'\s?Rd\.?\s|\sRd\.?$'), 'Road'],
    [re.compile(r'\s?Dr\.?\s|\sDr\.?$'), 'Drive'],
    [re.compile(r'\s?Ln\.?\s|\sLn\.?$'), 'Lane'],
    [re.compile(r'\s?Mt\.?\s|\sMt\.?$'), 'Mount'],
    [re.compile(r'\s?Pkwy\.?\s|\sPkwy\.?$'), 'Parkway']
]

cardinal_regexes = [
    [re.compile(r'\s?(?<!\S)S\.?\s|\s(?<!\S)S\.?$'), 'South'],
    [re.compile(r'\s?(?<!\S)N\.?\s|\s(?<!\S)N\.?$'), 'North'],
    [re.compile(r'\s?(?<!\S)W\.?\s|\s(?<!\S)W\.?$'), 'West'],
    [re.compile(r'\s?(?<!\S)E\.?\s|\s(?<!\S)E\.?$'), 'East']
]

move_cardinal_regexes = {
    'East' : re.compile(r'(East[^\w]|East$)'),
    'West' : re.compile(r'(West[^\w]|West$)'),
    'South' : re.compile(r'(South$)'),
    'North' : re.compile(r'(North[^\w]|North$)')
}

# ToDo: Convert French street type regexes into list and dict format
# French regex matching patterns
ave_pattern_french = re.compile(r'\s?Rue\.?\s|\sRue\.?$|') # Avenue
blvd_pattern_french = re.compile(r'\s?Blvd\.?\s|\sBlvd\.?$') # Boulevard
st_pattern_french = re.compile(r'\s?St\.?\s|\sSt\.?$') # Rue
rd_pattern_french = re.compile(r'\s?Rd\.?\s|\sRd\.?$') #
dr_pattern_french = re.compile(r'\s?Dr\.?\s|\sDr\.?$')
ln_pattern_french = re.compile(r'\s?Ln\.?\s|\sLn\.?$')
mt_pattern_french = re.compile(r'\s?Mt\.?\s|\sMt\.?$')
pkwy_pattern_french = re.compile(r'\s?Pkwy\.?\s|\sPkwy\.?$')
s_pattern_french = re.compile(r'\s?(?<!\S)S\.?\s|\s(?<!\S)S\.?$')
n_pattern_french = re.compile(r'\s?(?<!\S)N\.?\s|\s(?<!\S)N\.?$')
w_pattern_french = re.compile(r'\s?(?<!\S)O\.?\s|\s(?<!\S)O\.?$')
e_pattern_french = re.compile(r'\s?(?<!\S)E\.?\s|\s(?<!\S)E\.?$')
east_pattern_french = re.compile(r'(Est[^\w]|Est$)')
west_pattern_french = re.compile(r'(Ouest[^\w]|Ouest$)')
south_pattern_french = re.compile(r'(Sud[^\w]|Sud$)')
north_pattern_french = re.compile(r'(Nord[^\w]|Nord$)')

# General regex matching patterns
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
double_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$') # ToDo: (A) remove of incorporate



### Main functions

# ToDo: Decide how to process the 'way' node type tags, <tag k="source" v="CanVec 6.0 - NRCan" /> and 	<tag k="addr:interpolation" v="odd" />
# ToDo: What to do with 'source' tag?
def shape_element(element):
    top_level_tags = ['id', 'type', 'visible', 'created', 'address']
    created = [ "version", "changeset", "timestamp", "user", "uid"]
    pos = ['lat', 'lon']
    node = {}
    node['pos'] = [0,0]
    node['created'] = dict()


    if element.tag == "node" or element.tag == "way" :
        node['type'] = element.tag
        attributes = element.attrib

        for a in attributes: # this refers to the top level elements of the node
            if a in top_level_tags:
                node[a]= attributes[a]

            elif a in pos:
                if a == 'lon':
                    node['pos'][1] = (float(attributes[a]))

                elif a == 'lat':
                    node['pos'][0] = (float(attributes[a]))

            elif a in created:
                node['created'][a] = attributes[a]

            else:
                node[a]= attributes[a]

        for child in element:
            if child.tag == 'tag':
                address = child.attrib
                address_state = node.get('address')

                if address_state == None:
                    node['address'] = {}

                else:
                    if 'addr:' in address['k']:
                        '''
                        Check for extended address information. If true, skip over
                        the entry, otherwise add the address to node.
                        '''
                        if len(re.findall(r':', address['k'])) > 1:
                            continue

                        else:
                            cleaned_address = clean(address['k'], address['v'])
                            node['address'][address['k'][5:]] = cleaned_address

                    elif "addr:" not in address['k']:
                        node[address['k']] = address['v']

                    elif problemchars.search(address['k']):
                        continue

            if child.tag == 'nd':
                '''
                Check if any node_refs entries exist in the node dictionary. If not
                create node_refs entry and add the value of nd to it. Otherwise just append
                the value of nd.
                '''
                nd_state = node.get('node_refs')

                if nd_state == None:
                    node['node_refs'] = {}

                else:
                    node['node_refs'] = [child.attrib['ref']]

        return node

    else:
        return None



### Helper Functinos

# ToDo: the hierarchy of function execution in the cleaning process needs to be sorted out
def update_element(address_type, address_name):
    if address_type[5:] == 'street':

        address_name = fix_cardinal_direction(address_name)
        address_name = update_street_name(address_name)
        print(address_type, address_name)

        return address_name

    # if address_type[5:] == 'city':
    #
    # elif address_type[5:] == 'housenumber':
    #
    # elif address_type[5:] == 'interpolation':
    #
    # else:
    #

    return address_name


def fix_cardinal_direction(address_name):
    for r in cardinal_regexes:
        m = r[0].search(address_name)

        if m:
            address_name = address_name.replace(str(m.group()), ' ' + r[1])

        elif move_cardinal_regexes[r[1]].search(address_name):
            address_name = move_cardinal_direction(address_name, r[1])

            return address_name

        else:
            return address_name


def move_cardinal_direction(address_name, cardinal_direction):

    # for r in move_cardinal_regexes:
    #     m = r[0].search(address_name)
    #
    #     if m:
    #         address_name = address_name.replace(str(m.group()), ' ' + r[1])
    #
    #         return address_name

    address_name = cardinal_direction + ' ' + (address_name.replace(' ' + cardinal_direction, ''))

    return address_name


def update_street_name(address_name):
    for r in type_regexes:
        m = r[0].search(address_name)

        if m:
            address_name = address_name.replace(str(m.group()), ' ' + r[1])

            return address_name

    return address_name


def clean_whitespace(address_name):
    address_name = address_name.strip()
    address_name = re.sub(r'(( ) +)', ' ', address_name)

    return address_name


def capitalize_street(address_name):
    split_address_name = address_name.split()
    word_list = []

    for word in split_address_name:
        if word[0].islower():
            word_list.append(word[0].upper() + word[1:].lower())

        else:
            word_list.append(word)

    return ' '.join(word_list)


def clean(address_type, address_name):
    address_name = clean_whitespace(address_name)
    address_name = update_element(address_type, address_name)
    address_name = capitalize_street(address_name)

    return address_name


def process_map(file_in, pretty = False):
    '''
    Runs the shape_element and clean functions, then returnswrites json file
    '''
    file_out = "{0}.json".format(file_in)
    data = []

    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)

            if el:
                data.append(el)

                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")

                else:
                    fo.write(json.dumps(el) + "\n")
# ToDo: The return data is indeed for testing, use it in your assertion tests with the model from the coursework
    return data


### Test functions
def test():
    # ToDo: Finish assertion tests
    # Test shape_element function

    # Test update_element function

    # Test fix_cardinal_direction function

    # Test move_cardinal_direction function

    # Test clean_whitespace function
    assert clean_whitespace('Baker  Street') == 'Baker Street'
    assert clean_whitespace('Baker   Street') == 'Baker Street'
    assert clean_whitespace(' Baker   Street ') == 'Baker Street'

    # Test update_street_name function

    # Test capitalize_street function
    # assert capitalize_street('baker Street') == 'Baker Street'
    # assert capitalize_street('south baker street') == 'South Baker Street'

    # Test clean function
    # assert clean('addr:street', 'Chanonhouse St.') == 'Chanonhouse Street'
    # assert clean('addr:street', 'St. Jerome St.') == 'St. Jerome Street'
    # assert clean('addr:street', 'South Ash Ln ') == 'South Ash Lane'
    # assert clean('addr:street', 'Baker Street South') == 'South Baker Street'
    pass

def main():
    test()
    filename = "ottawa_canada_sample_tiny.osm"

    process_map(filename, True)



if __name__ == '__main__':
    main()