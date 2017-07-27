"""
Script to import geojson data ( from https://mapzen.com/data/metro-extracts/ )
into a Mongo database collection
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
                    prop_summary[key] = 1
                else:
                    prop_summary[key] += 1
    print "'%s' : %d documents total ( %d with 'properties' section)" % (m_coll, doc_total, doc_with_prop)
    print prop_summary

def main():
    """Main routine"""
    args = parse_cmdline()
    logging.debug("Creating MongoClient from connection string ...")
    m_client = MongoClient(args.cst)
    logging.debug("Done")
    logging.debug("Retrieving database ...")
    target_db_name = args.db
    target_db = m_client[target_db_name]
    logging.debug("Done")
    logging.debug("Scanning collections and collecting statistics")
    for collection in target_db.collection_names():
        logging.debug(" > scanning collection '%s' ...", collection)
        produce_collection_stats(target_db, collection)
        logging.debug(" > done")
    logging.debug("Done")

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    main()

