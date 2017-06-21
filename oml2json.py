#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import xml.etree.cElementTree as ET
import argparse
import pprint
import re
import codecs
import traceback
import json
import warnings

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

"""
    - all attributes of "node" and "way" should be turned into regular key/value pairs, except:
        - attributes in the CREATED array should be added under a key "created"
        - attributes for latitude and longitude should be added to a "pos" array,
            for use in geospacial indexing. Make sure the values inside "pos" array are floats
            and not strings. 
- if the second level tag "k" value contains problematic characters, it should be ignored
- if the second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if the second level tag "k" value does not start with "addr:", but contains ":", you can
  process it in a way that you feel is best. For example, you might split it into a two-level
  dictionary like with "addr:", or otherwise convert the ":" to create a valid key.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored
- for "way" specifically: "node_refs": ["305896090", "1719825889"]
"""

def shape_element(element):
    node = { "created" : {} }
    
    key_subkey = re.compile(r'^(([a-z]|_)*):(([a-z]|_)*)$')

    if element.tag == "node" or element.tag == "way" :
        node['type'] = element.tag
        # Processing attributes
        if element.tag == "node":
            node['pos'] = [ float(element.get('lat')), float(element.get('lon')) ]
        
        for k in element.keys():
            if k in CREATED:
                node['created'][k] = element.get(k)
            elif k not in [ 'lat', 'lon' ]:
                node[k] = element.get(k)
        
        contentNodes = element.getchildren()
        for n in contentNodes:
            if n.tag == "tag":
                tagKey = n.get('k')
                tagVal = n.get('v')
                if problemchars.match(tagKey):
                    continue
                
                if tagKey.count(':') > 1:
                    continue
                
                key_match = key_subkey.match(tagKey)
                if key_match:
                    tagKeyPre = key_match.group(1)
                    tagKeyVal = key_match.group(3)

                    if tagKeyPre == "addr":
                        if 'address' not in node:
                            node['address'] = {}
                        node['address'][tagKeyVal] = tagVal
                    else:
                        if tagKeyPre not in node:
                            node[tagKeyPre] = {}
                        elif type(node[tagKeyPre]) == dict:
                            node[tagKeyPre][tagKeyVal] = tagVal
                        else:
                            warnings.warn("ELEMENT: '{0}', ID: '{1}' - ignoring tag '{2}' due to conflict with existing '{3}' key".format(element.tag, element.get('id'), tagKey, tagKeyPre))
            elif n.tag == "nd" and element.tag == "way":
                if 'node_refs' not in node:
                    node['node_refs'] = []
                node['node_refs'].append(n.get("ref"))

        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            try:
                el = shape_element(element)
                if el:
                    data.append(el)
                    if pretty:
                        fo.write(json.dumps(el, indent=2)+"\n")
                    else:
                        fo.write(json.dumps(el) + "\n")
            except Exception as e:
                print element, element.get('id')
                print e
                traceback.print_exc()

    return data

def test():
    data = process_map('example.osm', True)
    #pprint.pprint(data)
    
    correct_first_elem = {
        "id": "261114295", 
        "visible": "true", 
        "type": "node", 
        "pos": [41.9730791, -87.6866303], 
        "created": {
            "changeset": "11129782", 
            "user": "bbmiller", 
            "version": "7", 
            "uid": "451048", 
            "timestamp": "2012-03-28T18:31:23Z"
        }
    }
    
    pprint.pprint( data[-1] )
    
    assert data[0] == correct_first_elem
    assert data[-1]["address"] == {
                                    "street": "West Lexington St.", 
                                    "housenumber": "1412"
                                      }
    assert data[-1]["node_refs"] == [ "2199822281", "2199822390",  "2199822392", "2199822369", 
                                    "2199822370", "2199822284", "2199822281"]

def parse_cmdline():
    parser = argparse.ArgumentParser(description='Converts OSM openstreet data to JSON')
    parser.add_argument('--osm', required=True, action='store',
                        help='Path to the OSM file to be processed',
                        metavar='<OSM-FILE>', dest='osm')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_cmdline()
    data = process_map(args.osm)
    #test()