"""
Script to import geojson data ( from https://mapzen.com/data/metro-extracts/ )
into a Mongo database collection

TODO: define mapping of properties
"""
import json
import logging
import argparse
import datetime
from pymongo import MongoClient

def parse_cmdline():
    """Parses commandline arguments"""
    parser = argparse.ArgumentParser(
        description='Generates report on available properties from geojson data')
    parser.add_argument('--cst', required=True, action='store',
                        help='Target Mongo instance connection string',
                        metavar='<CONNECTION-STRING>', dest='cst')
    parser.add_argument('--db', required=True, action='store',
                        help='Target Mongo database',
                        metavar='<TARGET-DATABASE>', dest='db')
    return parser.parse_args()

def produce_collection_stats(m_db, m_coll):
    """Produces basic stats on available geojson properties to console"""
    doc_total = 0
    doc_with_prop = 0
    prop_summary = {}
    for doc in m_db[m_coll].find():
        doc_total += 1
        if doc['properties'] != None:
            doc_with_prop += 1
            for key in doc['properties']:
                if key not in prop_summary:
                    prop_summary[key] = 0
                else:
                    prop_summary[key] += 1
    print "%d documents total" % doc_total
    print "%d documents with 'properties' section" % doc_with_prop
    print "properties list:"
    print prop_summary


def main():
    """Main routine"""
    args = parse_cmdline()
    logging.info("Creating MongoClient from connection string ...")
    m_client = MongoClient(args.cst)
    logging.info("Done")
    logging.info("Retrieving database ...")
    target_db_name = args.db
    target_db = m_client[target_db_name]
    logging.info("Done")
    logging.info("Scanning collections and collecting statistics")
    for collection in target_db.collection_names():
        logging.info(" > scanning collection '%s' ...", collection)
        produce_collection_stats(target_db, collection)
        logging.info(" > done")
    logging.info("Done")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()

