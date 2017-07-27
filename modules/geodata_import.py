"""Module with routines to import geojson data during oml2json conversion

TODO: define mapping of properties
"""
import logging


"""
{
    "tags": {
        "source": "City of Redwood City, CA 1013",
        "redwood_city_ca:addr_id": "4190"
    },
    "created": {
        "changeset": "18165721",
        "user": "oldtopos",
        "version": "1",
        "uid": "169004",
        "timestamp": "2013-10-03T17:33:32Z"
    },
    "pos": [
        37.4730575,
        -122.2602116
    ],
    "address": {
        "city": "Redwood City",
        "street": "Canyon Road",
        "housenumber": "575"
    },
    "type": "node",
    "id": "2481419230"
}
#{u'addr:postc': 9001, u'name': 9001, u'addr:stree': 9001, u'osm_id': 9001, u'type': 9001, u'id': 9001, u'addr:city': 9001}
    mapping = {
        'addr:postc' : ['address', 'postcode'],
        'addr:stree' : ['address', 'street'],
        'addr:city'  : ['address', 'city'],
    }
"""
def enrich_node_from_collection(oml_json_node, m_db, m_coll_name, mappings, exclude_props):
    logging.debug('Processing collection ''%s''', m_coll_name)
    if m_coll_name not in m_db.collection_names():
        logging.debug('Collection ''%s'' not found in the database ''%s''', m_coll_name, m_db.name)
        return
    logging.debug('Fetching record for oml node...')
        

def enrich_node(oml_json_node, mongo_db):
    """Adds geojson data into an OML data node converted to JSON"""
    oml_id = oml_json_node['id']
    logging.debug('Processing node ''%s''', oml_id)
    for m_collection in mongo_db.collection_names():
        enrich_node_from_collection(oml_json_node, mongo_db, m_collection, {}, [])
    #fetch data by oml_id w/ mapping ( routine )
    logging.debug('Processed node ''%s''', oml_id)
