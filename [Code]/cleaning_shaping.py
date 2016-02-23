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

city_regexes = [
    [re.compile(r'.*of\s|.*Of\s'), '']
]
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
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

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
                tag = child.attrib
                tag_key = tag['k']
                tag_value = tag['v']
                address_state = node.get('address')

                if problemchars.search(tag_key):

                    continue

                if address_state == None and 'addr:' in tag_key:
                    node['address'] = {}

                if 'addr:' in tag_key and check_for_extended_addr(tag_key) == False:
                    cleaned_tag = clean_tag(tag_key, tag_value)
                    node['address'][tag_key[5:]] = cleaned_tag

                elif 'addr:' not in tag_key:
                    node[tag_key] = tag_value

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

def check_for_extended_addr(tag_key):
    '''
    Check if the addr value in the tag_key has more than one colon.
    '''

    return len(re.findall(r':', tag_key)) > 1


def update_tag(tag_key, tag_value):
    if tag_key[5:] == 'street':
        tag_value = update_street_name(tag_value)
        tag_value = fix_cardinal_direction(tag_value)

        return tag_value

    if tag_key[5:] == 'city':
        tag_value = compact_city_name(tag_value)

        return tag_value

    return tag_value


def compact_city_name(tag_value):
    for r in city_regexes:
        m = r[0].search(tag_value)

        if m:
            tag_value = re.sub(r[0], r[1], tag_value)

    return tag_value


def fix_cardinal_direction(tag_value):
    for r in cardinal_regexes:
        m = r[0].search(tag_value)

        if m:
            tag_value = address_name.replace(str(m.group()), ' ' + r[1])

        elif move_cardinal_regexes[r[1]].search(tag_value):
            tag_value = move_cardinal_direction(tag_value, r[1])

            return tag_value

        else:
            return tag_value


def move_cardinal_direction(tag_value, cardinal_direction):

    # for r in move_cardinal_regexes:
    #     m = r[0].search(address_name)
    #
    #     if m:
    #         address_name = address_name.replace(str(m.group()), ' ' + r[1])
    #
    #         return address_name

    tag_value = cardinal_direction + ' ' + (tag_value.replace(' ' + cardinal_direction, ''))

    return tag_value


def update_street_name(tag_value):
    for r in type_regexes:
        m = r[0].search(tag_value)

        if m:
            # ToDo: see if it's worthile to switch all .replace statements with .sub statements
            # address_name = address_name.replace(str(m.group()), ' ' + r[1])
            tag_value = re.sub(r[0], ' ' + r[1], tag_value)

            return tag_value

    return tag_value


def remove_whitespace(tag_value):
    tag_value = tag_value.strip()
    tag_value = re.sub(r'(( ) +)', ' ', tag_value)

    return tag_value


def capitalize_tag(tag_value):
    split_tag = tag_value.split()
    word_list = []

    for word in split_tag:
        if word[0].islower():
            word_list.append(word[0].upper() + word[1:].lower())

        else:
            word_list.append(word)

    tag_value = ' '.join(word_list)

    return tag_value


def clean_tag(tag_key, tag_value):
    tag_value = remove_whitespace(tag_value)
    tag_value = update_tag(tag_key, tag_value)
    tag_value = capitalize_tag(tag_value)

    return tag_value


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
    # assert shape_element(
    #     <node changeset="6223495" id="969421551" lat="45.3839697" lon="-75.9596713" timestamp="2010-10-30T00:03:00Z" uid="186592" user="Johnwhelan" version="1">
		# <tag k="source" v="CanVec 6.0 - NRCan" />
		# <tag k="addr:city" v="City of Ottawa" />
		# <tag k="addr:street" v="O'hara Drive" />
		# <tag k="addr:housenumber" v="19" />
    # </node>
    # ) ==

    # Test compact_city_name
    assert compact_city_name('City of Ottawa') == 'Ottawa'
    assert compact_city_name('Township Of Tay Valley') == 'Tay Valley'

    # Test update_element function

    # Test fix_cardinal_direction function

    # Test move_cardinal_direction function

    # Test remove_whitespace function
    assert remove_whitespace('Baker  Street') == 'Baker Street'
    assert remove_whitespace('Baker   Street') == 'Baker Street'
    assert remove_whitespace(' Baker   Street ') == 'Baker Street'

    # Test update_street_name function

    # Test capitalize_tag function
    # assert capitalize_tag('baker Street') == 'Baker Street'
    # assert capitalize_tag('south baker street') == 'South Baker Street'

    # Test clean function
    # assert clean_tag('addr:street', 'Chanonhouse St.') == 'Chanonhouse Street'
    # assert clean_tag('addr:street', 'St. Jerome St.') == 'St. Jerome Street'
    # assert clean_tag('addr:street', 'South Ash Ln ') == 'South Ash Lane'
    # assert clean_tag('addr:street', 'Baker Street South') == 'South Baker Street'
    pass

def main():
    test()
    filename = "ottawa_canada_sample_tiny.osm"

    process_map(filename, True)



if __name__ == '__main__':
    main()