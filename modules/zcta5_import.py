"""
The module allows to load Polygon data from CSV file generated with
https://github.com/censusreporter/census-shapefile-utils
"""
import re

def load_polygondata(polygon_str):
    """Loads polygon data from string POLYGON((lon lat, lon lat, ...))
    https://stackoverflow.com/questions/38532816/how-to-transform-a-polygon-string-on-a-real-polygon"""
    polygon_re = re.compile(r"^POLYGON \(\((.*)\)\)")
    polygon_match = polygon_re.match(polygon_str)

    if polygon_match is not None:
        coord_str = polygon_match.groups()[0]

        # parse string of coordinates into a list of float pairs
        return [[float(s) for s in p.split(',')] for p in coord_str.split(";")]
    return None