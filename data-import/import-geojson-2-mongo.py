"""
Script to import geojson data ( from https://mapzen.com/data/metro-extracts/ )
into a Mongo database collection

TODO:
    Add mongo index for properties.osm_id
"""
import json
import logging
import argparse
import datetime
from pymongo import MongoClient

def parse_cmdline():
    """Parses commandline arguments"""
    parser = argparse.ArgumentParser(
        description='Imports mapzen geojson data to a specified Mongo collection')
    parser.add_argument('--in', required=True, action='store',
                        help='Input GEOJSON file',
                        metavar='<GEOJSON-FILE>', dest='inF')
    parser.add_argument('--cst', required=True, action='store',
                        help='Target Mongo instance connection string',
                        metavar='<CONNECTION-STRING>', dest='cst')
    parser.add_argument('--tDb', required=True, action='store',
                        help='Target Mongo database',
                        metavar='<TARGET-DATABASE>', dest='tdb')
    parser.add_argument('--tC', required=True, action='store',
                        help='Target Mongo collection',
                        metavar='<TARGET-COLLECTION>', dest='tc')
    return parser.parse_args()

def main():
    """Main routine"""
    args = parse_cmdline()

    input_filename = args.inF
    logging.info("Loading input JSON file '%s' ...", input_filename)
    try:
        with open(input_filename) as geojson_file:
            json_data = json.load(geojson_file)
    except:
        logging.fatal('Failed to load the input file')
        raise
    logging.info("Done")
    logging.debug(json_data.keys())

    logging.info("Creating MongoClient from connection string ...")
    m_client = MongoClient(args.cst)
    logging.info("Done")

    target_db_name = args.tdb
    target_db = m_client[target_db_name]
    target_coll_name = args.tc
    logging.info("Checking if '%s' collection already exists in the '%s' database ...",
                 target_coll_name, target_db_name)
    if target_coll_name in target_db.collection_names():
        backup_collection_name = target_coll_name + datetime.datetime.now().isoformat()
        logging.warn(" > '%s' collection already exists, renaming to '%s'",
                     target_coll_name, backup_collection_name)
        target_db[target_coll_name].rename(backup_collection_name)
        logging.warn(" > Done")
    logging.info("Done")
    logging.info("Bulk importing %d records...", len(json_data['features']))
    target_db[target_coll_name].insert_many(json_data['features'])
    logging.info("Done")
    property_to_index = 'properties.osm_id'
    logging.info("Creating index on the '%s' property ...", property_to_index)
    target_db[target_coll_name].create_index(property_to_index)
    logging.info("Done")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
