"""
Script to import geojson data ( from https://mapzen.com/data/metro-extracts/ )
into a Mongo database collection

TODO:
    Params
        Connectionstring
        targetDb
        targetCollection

    Get timestamp // datetime.datetime.now().isoformat()
    Rename target collection if exists // print("posts" in db.collection_names())
    Logging // logging.basicConfig(level=logging.INFO)
"""
import json
import argparse
import logging
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
    #m_client = MongoClient(args['cst'])

    input_filename = args.inF
    logging.info("Loading input JSON file '%s'", input_filename)
    try:
        with open(input_filename) as geojson_file:
            json_data = json.load(geojson_file)
    except:
        logging.fatal('Failed to load the input file')
        raise
    logging.info("Done")
    logging.debug(json_data.keys())

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
