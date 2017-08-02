#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import argparse
import codecs
import traceback
import inspect
import json
import sys
import os

# Bit of trickery to import custom modules by relative path
# https://stackoverflow.com/questions/279237/import-a-module-from-a-relative-path
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
# Now the import
from modules import geodata_import
from pymongo import MongoClient

CREATED = ["version", "changeset", "timestamp", "user", "uid"]

def shape_element(element):
    """Processes XML element and returns JSON representation of the data
        - all attributes of "node" and "way" should be turned into regular key/value pairs, except:
        - attributes in the CREATED array should be added under a key "created"
        - attributes for latitude and longitude should be added to a "pos" array,
            for use in geospacial indexing. Make sure the values inside "pos" array are floats
            and not strings.

    - for "way" specifically: "node_refs": ["305896090", "1719825889", ...]
    """
    node = {"created" : {}}

    if element.tag == "node" or element.tag == "way":
        node['type'] = element.tag
        # Processing attributes
        if element.tag == "node":
            node['pos'] = [float(element.get('lat')), float(element.get('lon'))]

        for k in element.keys():
            if k in CREATED:
                node['created'][k] = element.get(k)
            elif k not in ['lat', 'lon']: #avoid adding latitude, longitude since they are processed separately
                node[k] = element.get(k)

        contentNodes = element.getchildren()
        for n in contentNodes:
            if n.tag == "tag":
                process_tag(n, node)
            elif n.tag == "nd" and element.tag == "way":
                if 'node_refs' not in node: node['node_refs'] = []
                node['node_refs'].append(n.get("ref"))
            else:
                print "Unknown tag '%s' ( element id: %s)" % (n.tag, element.get('id'))

        return node
    else:
        return None

def process_tag(tag_element, out_json_node):
    """Processes nested 'tag' elements of an XML node and adds them
       to the JSON representation

       - if the second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
       - all other tags are to be added to the 'tags' dictionary
    """
    tag_key = tag_element.get('k')
    tag_val = tag_element.get('v')

    addr_marker = 'addr:'
    if tag_key.startswith(addr_marker):
        #handle addr:* entries
        tag_key_val = tag_key[(len(addr_marker)):]

        if 'address' not in out_json_node: out_json_node['address'] = {}
        out_json_node['address'][tag_key_val] = tag_val
    else:
        if 'tags' not in out_json_node: out_json_node['tags'] = {}
        out_json_node['tags'][tag_key] = tag_val


def process_map(file_in, mongo_db, pretty = False):
    elements_processed = 0
    elements_failed = 0

    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            try:
                el = shape_element(element)
                elements_processed += 1
                if el:
                    #Attempt to load data from geojson
                    geodata_import.enrich_node(el, mongo_db)
                    data.append(el)
                    if pretty:
                        fo.write(json.dumps(el, indent=2)+"\n")
                    else:
                        fo.write(json.dumps(el) + "\n")
                stdout_map_processing_status(elements_processed, elements_failed)
            except Exception as e:
                elements_failed += 1
                print element, element.get('id')
                print e
                traceback.print_exc()

    stdout_map_processing_status(elements_processed, elements_failed, refresh=False)
    return data

def parse_cmdline():
    parser = argparse.ArgumentParser(description='Converts OSM openstreet data to JSON')
    parser.add_argument('--osm', required=True, action='store',
                        help='Path to the OSM file to be processed',
                        metavar='<OSM-FILE>', dest='osm')
    parser.add_argument('--mconn', required=True, action='store',
                        help='Mongo connection string for geojson data',
                        metavar='<MONGO-CONNECTION-STRING>', dest='mconn')
    parser.add_argument('--mdb', required=True, action='store',
                        help='Mongo database hosting geojson data',
                        metavar='<MONGO-DATABASE>', dest='mdb')
    return parser.parse_args()

def stdout_map_processing_status(elements_processed, elements_failed, refresh=True):
    line_end = "\r" if refresh else ""
    status_msg = "Status:  [ processed: %d;  failed: %d ]%s" % (elements_processed, elements_failed, line_end)
    sys.stdout.write(status_msg)
    sys.stdout.flush()


if __name__ == "__main__":
    args = parse_cmdline()
    data = process_map(args.osm, MongoClient(args.mconn)[args.mdb])
