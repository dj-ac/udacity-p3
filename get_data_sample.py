#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow
import argparse
import os
import sys

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def parse_cmdline():
    parser = argparse.ArgumentParser(description='Creates sample sub-set of data by taking every k-th record')
    parser.add_argument('--osm', required=True, action='store',
                        help='Path to the OSM file to be used as a source file',
                        metavar='<OSM-FILE>', dest='osm')
    parser.add_argument('--k', required=True, action='store',
                        help='The index specifying how many elements to take from the original set (every k''th element is to be taken)',
                        metavar='<K>', dest='k', type=int)
    return parser.parse_args()

def get_out_filename(input_file_path, k):
    input_file_name = os.path.basename(input_file_path)
    return "sample-{0}-{1}".format(k, input_file_name)

args = parse_cmdline()

with open(get_out_filename(args.osm, args.k), 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    status_msg = None
    for i, element in enumerate(get_element(args.osm)):
        if i % args.k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))
            status_msg = "Records added to sample: %d ( out of %d scanned )" % ((i/args.k), i)
            sys.stdout.write(status_msg + '\r')
            sys.stdout.flush()
    
    sys.stdout.write(status_msg)

    output.write('</osm>')
