"""
The module allows to load Polygon data from CSV file generated with
https://github.com/censusreporter/census-shapefile-utils
"""
import sys
import csv
import logging
from shapely.wkt import loads
from shapely.geometry import Point

# Having issues reading large data records
# https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072
csv.field_size_limit(sys.maxsize)

def try_load_polygon(polygon_str):
    """Loads polygon data from string POLYGON((lon lat, lon lat, ...))
    https://stackoverflow.com/questions/38532816/how-to-transform-a-polygon-string-on-a-real-polygon"""
    return loads(polygon_str)

def coord_within_ziparea(latlong, shapely_zcta_poly):
    """Determines if a point is withing the polygon for a zip code area
    https://stackoverflow.com/questions/16625507/python-checking-if-point-is-inside-a-polygon"""
    return Point(latlong).intersects(shapely_zcta_poly)

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
                z_poly = try_load_polygon(z_poly_str)
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
