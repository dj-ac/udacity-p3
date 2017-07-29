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
        'zipcode' : { 'src' : ['addr:postc'],  'trg' : ['address', 'postcode'] },
        'street'  : { 'src' : ['addr:stree'],  'trg' : ['address', 'street'] },
        'city'    : { 'src' : ['addr:city' ],  'trg' : ['address', 'city'] }
    }
"""
def get_dict_val(dict_obj, key_chain):
    """Fetches a dictionary element by key chain array: ['key1', 'key2' ... ]"""
    obj = dict_obj
    for key in key_chain:
        if key in obj:
            obj = obj[key]
        else:
            obj = None
    return obj

def set_dict_val(dict_obj, key_chain, val):
    """Assigns a value to dictionary by specified key chain ['key1', 'key2', ...]
    ( if sequence of keys exists within the dictionary )"""
    if key_chain is None:
        logging.debug('Key chain empty. Ignoring operation')
        return None

    obj = dict_obj
    for key in key_chain[:-1]:
        if key in obj:
            obj = obj[key]
        else:
            return False

    if key_chain[-1] in obj:
        logging.warn("Overriding ''%s'' with ''%s''. Path: [%s]",
                     obj[key_chain[-1]], val, '/'.join(key_chain))
    obj[key_chain[-1]] = val
    return True


def enrich_node_from_collection(oml_json_node, m_db, m_coll_name, mappings):
    """Adds geojson data into an OML data node from a particular Mongo collection"""
    logging.debug('Processing collection ''%s''', m_coll_name)
    if m_coll_name not in m_db.collection_names():
        logging.debug('Collection ''%s'' not found in the database ''%s''', m_coll_name, m_db.name)
        return
    gj_data = m_db[m_coll_name].find_one({'properties.osm_id': int(oml_json_node['id'])})
    if gj_data is None:
        logging.debug('Did not find any records matching the properties.osm_id (''%s'')', oml_json_node['id'])
        return

    if 'properties' not in gj_data:
        logging.debug('GeoJson record does not have ''properties'' key ( record id: %s)', gj_data['_id'])
        return

    processed_prp_list = []
    gj_prop = gj_data['properties']
    #Processing mappings
    for m_key in mappings:
        if m_key not in gj_prop:
            logging.debug('The ''%s'' key present in mappings but not found in gj data. GJ id: ''%s''',
                          m_key, gj_data['_id'])
            continue
        res = set_dict_val(oml_json_node, mappings[m_key], gj_prop[m_key])
        if res is None:
            logging.debug('Property ''%s'' ignored as per mapping', m_key)
        elif res:
            logging.debug('Property ''%s'' imported from geojson', m_key)
        else:
            logging.debug('Property ''%s'' not imported due to mapping issue', m_key)
    #Importing the rest of the properties to tags
    for p_key in gj_prop:
        if p_key not in processed_prp_list:
            logging.debug('Importing ''%s'' property to tags', p_key)
            oml_tags = oml_json_node['tags']
            if p_key in oml_tags:
                logging.debug('Overriding ''%s'' tags node. OLD: ''%s'', NEW: ''%s''',
                              p_key, oml_tags[p_key], gj_prop[p_key])
            else:
                logging.debug('Importing ''%s'' tag node', p_key)
            oml_tags[p_key] = gj_prop[p_key]

"""
mapping = {
        'addr:postc' : ['address', 'postcode'],
        'addr:stree' : ['address', 'street'],
        'addr:city'  : ['address', 'city'],
        'abc' : None }
}
"""
def enrich_node(oml_json_node, mongo_db):
    """Adds geojson data into an OML data node converted to JSON"""
    oml_id = oml_json_node['id']
    logging.debug('Processing node ''%s''', oml_id)

    #'landusages.geojson' : 1942 documents total ( 1942 with 'properties' section)
    #{u'z_order': 1942, u'name': 1942, u'area': 1942, u'osm_id': 1942, u'type': 1942, u'id': 1942}
    enrich_node_from_collection(oml_json_node, mongo_db, 'landusages.geojson',
                                {
                                    'z_order' : None,
                                    'osm_id' : None,
                                    'id': None
                                })
    #'barrierpoints.geojson' : 152 documents total ( 152 with 'properties' section)
    #{u'type': 152, u'id': 152, u'name': 152, u'osm_id': 152}
    enrich_node_from_collection(oml_json_node, mongo_db, 'barrierpoints.geojson',
                                {
                                    'osm_id' : None,
                                    'id': None
                                })
    #'admin.geojson' : 7 documents total ( 7 with 'properties' section)
    #{u'admin_leve': 7, u'type': 7, u'id': 7, u'name': 7, u'osm_id': 7}
    enrich_node_from_collection(oml_json_node, mongo_db, 'admin.geojson',
                                {
                                    'osm_id' : None,
                                    'id': None
                                })
    #'housenumbers.geojson' : 9001 documents total ( 9001 with 'properties' section)
    #{u'addr:postc': 9001, u'name': 9001, u'addr:stree': 9001, u'osm_id': 9001, u'type': 9001, u'id': 9001, u'addr:city': 9001}
    enrich_node_from_collection(oml_json_node, mongo_db, 'housenumbers.geojson',
                                {
                                    'addr:postc' : ['address', 'postcode'],
                                    'addr:stree' : ['address', 'street'],
                                    'addr:city'  : ['address', 'city'],
                                    'osm_id' : None,
                                    'id': None
                                })
    #'roads_gen1.geojson' : 3486 documents total ( 3486 with 'properties' section)
    #{u'z_order': 3486, u'bridge': 3486, u'name': 3486, u'service': 3486, u'tunnel': 3486, u'ref': 3486, u'osm_id': 3486, u'access': 3486, u'oneway': 3486, u'type': 3486, u'class': 3486}
    enrich_node_from_collection(oml_json_node, mongo_db, 'roads_gen1.geojson',
                                {
                                    'z_order': None,
                                    'osm_id' : None,
                                    'ref' : None,
                                    'id': None
                                })
    #'amenities.geojson' : 95 documents total ( 95 with 'properties' section)
    #{u'type': 95, u'id': 95, u'name': 95, u'osm_id': 95}
    enrich_node_from_collection(oml_json_node, mongo_db, 'amenities.geojson',
                                {
                                    'osm_id' : None,
                                    'id': None
                                })
    #'transport_areas.geojson' : 5 documents total ( 5 with 'properties' section)
    #{u'type': 5, u'id': 5, u'name': 5, u'osm_id': 5}
    enrich_node_from_collection(oml_json_node, mongo_db, 'transport_areas.geojson',
                                {
                                    'osm_id' : None,
                                    'id': None
                                })
    #'barrierways.geojson' : 180 documents total ( 180 with 'properties' section)
    #{u'type': 180, u'id': 180, u'name': 180, u'osm_id': 180}
    enrich_node_from_collection(oml_json_node, mongo_db, 'barrierways.geojson',
                                {
                                    'osm_id' : None,
                                    'id': None
                                })
    #'housenumbers_interpolated.geojson' : 5 documents total ( 5 with 'properties' section)
    #{u'addr:postc': 5, u'name': 5, u'addr:inclu': 5, u'addr:stree': 5, u'osm_id': 5, u'type': 5, u'id': 5, u'addr:city': 5}
    enrich_node_from_collection(oml_json_node, mongo_db, 'housenumbers_interpolated.geojson',
                                {
                                    'addr:postc' : ['address', 'postcode'],
                                    'addr:stree' : ['address', 'street'],
                                    'addr:city'  : ['address', 'city'],
                                    'osm_id' : None,
                                    'id': None
                                })
    #'buildings.geojson' : 95748 documents total ( 95748 with 'properties' section)
    #{u'type': 95748, u'id': 95748, u'name': 95748, u'osm_id': 95748}
    enrich_node_from_collection(oml_json_node, mongo_db, 'buildings.geojson',
                                {
                                    'osm_id' : None,
                                    'id': None
                                })
    #'roads.geojson' : 16808 documents total ( 16808 with 'properties' section)
    #{u'z_order': 16808, u'bridge': 16808, u'name': 16808, u'service': 16808, u'tunnel': 16808, u'ref': 16808, u'oneway': 16808, u'class': 16808, u'access': 16808, u'osm_id': 16808, u'type': 16808, u'id': 16808}
    enrich_node_from_collection(oml_json_node, mongo_db, 'roads.geojson',
                                {
                                    'z_order': None,
                                    'osm_id' : None,
                                    'ref' : None,
                                    'id': None
                                })
    #'places.geojson' : 23 documents total ( 23 with 'properties' section)
    #{u'z_order': 23, u'name': 23, u'osm_id': 23, u'type': 23, u'id': 23, u'population': 23}
    enrich_node_from_collection(oml_json_node, mongo_db, 'places.geojson',
                                {
                                    'z_order': None,
                                    'osm_id' : None,
                                    'id': None
                                })
    #'transport_points.geojson' : 1011 documents total ( 1011 with 'properties' section)
    #{u'ref': 1011, u'type': 1011, u'id': 1011, u'name': 1011, u'osm_id': 1011}
    enrich_node_from_collection(oml_json_node, mongo_db, 'transport_points.geojson',
                                {
                                    'ref' : None,
                                    'osm_id' : None,
                                    'id': None
                                })
    #'roads_gen0.geojson' : 3486 documents total ( 3486 with 'properties' section)
    #{u'z_order': 3486, u'bridge': 3486, u'name': 3486, u'service': 3486, u'tunnel': 3486, u'ref': 3486, u'osm_id': 3486, u'access': 3486, u'oneway': 3486, u'type': 3486, u'class': 3486}
    enrich_node_from_collection(oml_json_node, mongo_db, 'roads_gen0.geojson',
                                {
                                    'ref': None,
                                    'z_order' : None,
                                    'osm_id' : None,
                                    'id': None
                                })
    logging.debug('Processed node ''%s''', oml_id)
