"""
The module allows to load Polygon data from CSV file generated with
https://github.com/censusreporter/census-shapefile-utils
"""
import re
import csv
import logging
import numpy as np
import matplotlib.path as mplPath

def load_polygon(polygon_str):
    """Loads polygon data from string POLYGON((lon lat, lon lat, ...))
    https://stackoverflow.com/questions/38532816/how-to-transform-a-polygon-string-on-a-real-polygon"""
    polygon_re = re.compile(r"^POLYGON \(\((.*)\)\)")
    polygon_match = polygon_re.match(polygon_str)

    if polygon_match is not None:
        coord_str = polygon_match.groups()[0]

        # parse string of coordinates into a list of float pairs
        return [[float(s) for s in p.split()] for p in coord_str.split(",")]
    return None

def coord_within_ziparea(latlong, poly_array):
    """Determines if a point is withing the polygon for a zip code area
    https://stackoverflow.com/questions/16625507/python-checking-if-point-is-inside-a-polygon"""
    return mplPath.Path(np.array(poly_array)).contains_point(latlong)

def load_zcta5_data(zcta_csv_file):
    """Loads zcta5 data into a dictionary ZIP=>POLYGON from CSV data file extracted with
    https://github.com/censusreporter/census-shapefile-utils"""
    input_file = csv.DictReader(open(zcta_csv_file))
    zcta_data = {}
    processed_counter = 0
    for row in input_file:
        z_key = row['GEOID']
        z_poly_str = row['GEOMETRY']
        if z_key not in zcta_data:
            try:
                z_poly = load_polygon(z_poly_str)
                if z_poly is not None:
                    zcta_data[z_key] = z_poly
                else:
                    logging.error('Failed to parse polygon. GEOID: ''%s''', z_key)
            except Exception as e:
                logging.error('Failed to process polygon. GEOID: ''%s''', z_key)
                logging.exception(e)
        processed_counter += 1
        logging.debug('Processed %d items', processed_counter)
    return zcta_data
