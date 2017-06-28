"""Runs basic analysis of address data from an imported OpenStreed dataset"""
import sys
import argparse
import json
import pandas as pd
def get_addr_data(json_dataset):
    """
    # info on available address fields ( and how are they used )
    # export addr data to pandas-dataset [ element-id, addr-field, addr-field-val ]
    #   run analysis of the dataset
    """
    data_header = ['node_id', 'node_type', 'tag', 'val']
    raw_data = []
    for json_node in json_dataset:
        if 'address' in json_node:
            for tag in json_node['address']:
                raw_data.append([
                    json_node['id'],
                    json_node['type'],
                    tag,
                    json_node['address'][tag]
                ])
        else:
            raw_data.append([
                json_node['id'],
                json_node['type'],
                None,
                None
            ])
    return pd.DataFrame(raw_data, columns=data_header)

def parse_cmdline():
    parser = argparse.ArgumentParser(description='Runs basic analysis of address data from an imported OpenStreed dataset')
    parser.add_argument('--json', required=True, action='store',
                        help='Path to the JSON file to be processed',
                        metavar='<JSON-FILE>', dest='json')
    return parser.parse_args()

def stdout_status(message, refresh=True):
    line_end = "\r" if refresh else ""
    status_msg = "%s%s" % (message, line_end)
    sys.stdout.write(status_msg)
    sys.stdout.flush()

if __name__ == "__main__":
    args = parse_cmdline()

    parsed_json_data = []

    entries_loaded = 0
#TODO: change input to XML ( the original dataset ) 
    for line in open(args.json, 'r'):
        parsed_json_data.append(json.loads(line))
        stdout_status("%d JSON documents loaded" % entries_loaded)
    
    addr_data = get_addr_data(parsed_json_data)

    print addr_data.describe()
