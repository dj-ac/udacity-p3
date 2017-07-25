"""
Script to import geojson data ( from https://mapzen.com/data/metro-extracts/ )
into a Mongo database collection

TODO: calculate collection stats
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

def produce_collection_stats():
    pass

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
        logging.info(" > done")
    logging.info("Done")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()

