import argparse

def parse_cmdline():
    """Parsing command line arguments"""
    parser = argparse.ArgumentParser(
        description='Runs basic analysis of address data from an imported OpenStreed dataset'
    )
    parser.add_argument('--json', required=True, action='store',
                        help='Path to the JSON file to be processed',
                        metavar='<JSON-FILE>', dest='json')
    return parser.parse_args()

#read key from file
#check info
#create local cache