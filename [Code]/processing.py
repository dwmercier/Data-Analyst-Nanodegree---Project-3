#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import json
import re
import xml.etree.cElementTree as ET

### Regex matching patterns

type_regexes = [
    [re.compile(r'\sSt.\s|\sSt\.?$', re.IGNORECASE), 'Street'],
    [re.compile(r'\s?Rd\.?\s|\sRd\.?$', re.IGNORECASE), 'Road'],
    [re.compile(r'\s?Dr\.?\s|\sDr\.?$', re.IGNORECASE), 'Drive'],
    [re.compile(r'\s?Ave\.?\s|\sAve\.?$', re.IGNORECASE), 'Avenue'],
    [re.compile(r'\s?Cr\.?\s|\sCr\.?$', re.IGNORECASE), 'Crescent'],
    [re.compile(r'\s?Wy\.?\s|\sWy\.?$', re.IGNORECASE), 'Way'],
]

type_regexes_french = [
    [re.compile(r'\sR.\s|\sR\.?$', re.IGNORECASE), 'Rue'],
    [re.compile(r'\s?Ch\.?\s|\sCh\.?$', re.IGNORECASE), 'Chemin'],
    [re.compile(r'\s?Blvd\.?\s|\Blvd\.?$', re.IGNORECASE), 'Boulevard'],
    [re.compile(r'\s?Ave\.?\s|\sAve\.?$', re.IGNORECASE), 'Avenue'],
    [re.compile(r'\sImp.\s|\sImp\.?$', re.IGNORECASE), 'Impasse'],
    [re.compile(r'\s?Conc\.?\s|\sConc\.?$', re.IGNORECASE), 'Concession'],
]

cardinal_regexes = [
    [re.compile(r'\s?(?<!\S)N\.?\s|\s(?<!\S)N\.?$', re.IGNORECASE), 'North'],
    [re.compile(r'\s?(?<!\S)W\.?\s|\s(?<!\S)W\.?$', re.IGNORECASE), 'West'],
    [re.compile(r'\s?(?<!\S)E\.?\s|\s(?<!\S)E\.?$', re.IGNORECASE), 'East'],
    [re.compile(r'\s?(?<!\S)S\.?\s|\s(?<!\S)S\.?$', re.IGNORECASE), 'South']
]

move_cardinal_regexes = {
    'North': re.compile(r'(North[^\w]|North$)', re.IGNORECASE),
    'West': re.compile(r'(West[^\w]|West$)', re.IGNORECASE),
    'East': re.compile(r'(East[^\w]|East$)', re.IGNORECASE),
    'South': re.compile(r'(South$[^\w]|South$)', re.IGNORECASE)
}

city_regexes = [
    [re.compile(r'.*of\s|.*Of\s'), '']
]

problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


### Main functions

def shape_element(element):
    """Cleans the contents of an individual element from the OSM file.

    Iterates over the children of the element, cleaning any that match the regex
    patterns of the cleaning functions that shape_element calls. Each child is 
    added to a dict that represents the contents of the original element in a 
    JSON-compatible format.

    Args:
        element: An elementTree Element object

    Returns:
        A dict containing a cleaned version of the element in JSON-compatible 
        format.
        
    """
    top_level_tags = ['id', 'type', 'visible', 'created', 'address']
    created = ["version", "changeset", "timestamp", "user", "uid"]
    pos = ['lat', 'lon']
    node = {}
    node['created'] = dict()

    if element.tag == "node" or element.tag == "way":
        node['type'] = element.tag
        attributes = element.attrib

        for a in attributes:
            if a in pos:
                if node.get('pos') == None:
                    node['pos'] = [0, 0]

                if node.get('pos'):
                    if a == 'lat':
                        node['pos'][0] = (float(attributes[a]))

                    elif a == 'lon':
                        node['pos'][1] = (float(attributes[a]))

            elif a in top_level_tags:
                node[a] = attributes[a]

            elif a in created:
                node['created'][a] = attributes[a]

            else:
                node[a] = attributes[a]

        for child in element:
            if child.tag == 'tag':
                tag = child.attrib
                tag_key = tag['k']
                tag_value = tag['v']

                if problemchars.search(tag_key):
                    continue

                if node.get('address') == None and 'addr:' in tag_key:
                    node['address'] = {}

                if 'addr:' in tag_key and check_for_extended_addr(
                        tag_key) == False:
                    cleaned_tag = clean_tag(tag_key, tag_value)
                    node['address'][tag_key[5:]] = cleaned_tag

                elif 'addr:' not in tag_key:
                    node[tag_key] = tag_value

            elif child.tag == 'nd':
                if node.get('node_refs') == None:
                    node['node_refs'] = []

                node['node_refs'].append(child.attrib['ref'])

        return node

    else:
        return None


### Helper Functinos

def check_for_extended_addr(tag_key):
    """Checks if tag_key has more than one colon.

    Args:
        tag_key: A string specifying the type of value contained in tag_value.

    Returns:
        An integer specifying the number of times a colon was found in tag_key.
    """
    return len(re.findall(r':', tag_key)) > 1


def update_tag(tag_key, tag_value):
    if tag_key[5:] == 'street':
        tag_value = update_cardinal_direction(tag_value)
        tag_value = update_street_type(tag_value)

        return tag_value

    if tag_key[5:] == 'city':
        tag_value = update_city_name(tag_value)

        return tag_value

    return tag_value


def update_city_name(tag_value):
    for r in city_regexes:
        regex = r[0]
        replacement = r[1]
        match = regex.search(tag_value)

        if match:
            tag_value = re.sub(regex, replacement, tag_value)

    return tag_value


def update_cardinal_direction(tag_value):
    for r in cardinal_regexes:
        regex = r[0]
        replacement = r[1]
        match = regex.search(tag_value)

        if match:
            tag_value = tag_value.replace(str(match.group()), ' ' + replacement)

        if move_cardinal_regexes[replacement].search(tag_value):
            tag_value = move_cardinal_direction(tag_value, replacement)

            return tag_value

    return tag_value


def move_cardinal_direction(tag_value, replacement):
    tag_value = replacement + ' ' + (tag_value.replace(' ' + replacement, ''))

    return tag_value


def update_street_type(tag_value):
    for r in type_regexes:
        regex = r[0]
        replacement = r[1]
        match = r[0].search(tag_value)

        if match:
            tag_value = re.sub(regex, ' ' + replacement, tag_value)

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
    tag_value = capitalize_tag(tag_value)
    tag_value = update_tag(tag_key, tag_value)

    return tag_value


def process_map(file_in, pretty=False):
    """Iteratively cleans an OSM file and outputs the results to a JSON file.

    Iterates over the contents of the OSM file using ElementTree, passing each
    element to the shape_element function for cleaning. Adds each element to
    both the JSON file and a list.

    Args:
        file_in: A string containing the pathname of an OSM file.
        pretty: A boolean specifying whether the output should be formatted
        for better readability.

    Returns:
        In addition to the JSON output, returns a list containing the elements
        of the OSM file in JSON-compatible format for testing if needed.
    """
    output_dir = "..\\[Output]\\ottawa_canada_sample.osm"
    file_out = "{0}.json".format(output_dir)

    data = []

    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)

            if el:
                data.append(el)

                if pretty:
                    fo.write(json.dumps(el, indent=2) + "\n")

                else:
                    fo.write(json.dumps(el) + "\n")

    return data


### Test functions
def test_functions():
    # Test process_map function
    data = process_map('..\\[Data]\\ottawa_canada_sample_tiny.osm', True)
    correct_first_elem = {
        "name": "Shell",
        "id": "969421551",
        "created": {
            "user": "Johnwhelan",
            "uid": "186592",
            "version": "1",
            "timestamp": "2010-10-30T00:03:00Z",
            "changeset": "6223495"
        },
        "address": {
            "housenumber": "19",
            "city": "Ottawa",
            "street": "O'hara Drive"
        },
        "website": "http://www.shell.ca/",
        "source": "CanVec 6.0 - NRCan",
        "amenity": "fuel",
        "type": "node",
        "pos": [
            45.3839697,
            -75.9596713
        ]
    }

    assert data[0] == correct_first_elem

    # Test check_for_extended_addr function
    assert check_for_extended_addr('addr::') == True
    assert check_for_extended_addr('addr:') == False

    # Test update_city_name function
    assert update_city_name('City of Ottawa') == 'Ottawa'
    assert update_city_name('Township Of Tay Valley') == 'Tay Valley'

    # Test update_cardinal_direction function
    assert update_cardinal_direction('Baker Street S.') == 'South Baker Street'
    assert update_cardinal_direction('Baker Street E.') == 'East Baker Street'
    assert update_cardinal_direction('Baker Street N') == 'North Baker Street'
    assert update_cardinal_direction('Baker Street W') == 'West Baker Street'

    # Test move_cardinal_direction function
    assert move_cardinal_direction('Baker Street South',
                                   'South') == 'South Baker Street'
    assert move_cardinal_direction('Baker Street East',
                                   'East') == 'East Baker Street'
    assert move_cardinal_direction('Baker Street North',
                                   'North') == 'North Baker Street'
    assert move_cardinal_direction('Baker Street West',
                                   'West') == 'West Baker Street'

    # Test remove_whitespace function
    assert remove_whitespace('Baker  Street') == 'Baker Street'
    assert remove_whitespace('Baker   Street') == 'Baker Street'
    assert remove_whitespace(' Baker   Street ') == 'Baker Street'

    # Test update_street_type function
    assert update_street_type('South Ash St.') == 'South Ash Street'
    assert update_street_type('St. Ash St.') == 'St. Ash Street'
    assert update_street_type('South Ash Rd.') == 'South Ash Road'
    assert update_street_type('South Ash Dr.') == 'South Ash Drive'
    assert update_street_type('South Ash Ave.') == 'South Ash Avenue'
    assert update_street_type('South Ash Cr.') == 'South Ash Crescent'
    assert update_street_type('South Ash Wy') == 'South Ash Way'

    # Test capitalize_tag function
    assert capitalize_tag('baker Street') == 'Baker Street'
    assert capitalize_tag('south baker street') == 'South Baker Street'

    # Test update_tag function function
    assert update_tag('addr:city', 'City of Ottawa') == 'Ottawa'
    assert update_tag('addr:street', 'Ash St. S.') == 'South Ash Street'

    # Test clean_tag function
    assert clean_tag('addr:street', 'Chanonhouse st.') == 'Chanonhouse Street'
    assert clean_tag('addr:street', 'St. Jerome St') == 'St. Jerome Street'
    assert clean_tag('addr:street', 'South Ash Cr ') == 'South Ash Crescent'
    assert clean_tag('addr:street',
                     'Baker   Street south') == 'South Baker Street'


def main():
    filename = '..\\[Data]\\ottawa_canada_sample.osm'

    test_functions()

    process_map(filename, True)


if __name__ == '__main__':
    main()
