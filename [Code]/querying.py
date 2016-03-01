#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Command to import cleaned osm json file:
  mongoimport --db osm --collection ottawa --file ottawa_canada.osm.json
'''



### MongoDB Pipelines

def city_by_region_pipeline():
    '''
    View entries by the city region
    '''
    pipeline = [

        {'$group' :
            {
            '_id' : '$address.city',
            'count' :  {'$sum' : 1}
            }
        },
        {'$sort' : {'count' : -1}}
    ]

    return pipeline


def data_source_pipeline():
    '''
    View entries by data source used
    '''
    pipeline = [

        {'$group' :
            {
                '_id' : '$source',
                'count' :  {'$sum' : 1}
            }
        },
        {'$match' : {'_id' : {'$ne' : None}}},
        {'$sort' : {'count' : -1}}
    ]

    return pipeline


def cuisine_types_pipeline():
    '''
    Sort cuisine by type
    '''
    pipeline = [

        {'$group' :
            {
                '_id' : '$cuisine',
                'count' :  {'$sum' : 1}
            }
        },

        {'$sort' : {'count' : -1}}
    ]

    return pipeline


def top_contributors_pipeline():
    '''
    Sort users by their number of contributions
    '''
    pipeline = [

        {'$group' :
            {
                '_id' : '$created.user',
                'count' :  {'$sum' : 1}
            }
        },

        {'$sort' : {'count' : -1}}
    ]

    return pipeline


def single_entry_users_pipeline():
    pipeline = [
        {'$group':
            {
                '_id' : '$created.user',
                'count' : {'$sum': 1}
            }
        },
        {'$group':
             {
                 '_id' : '$count',
                 'users' : {'$sum': 1}
             }
        },
        {'$sort' : {'_id' : 1}},
        {'$limit': 1 }
    ]

    return pipeline



### Database operations

def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db


def aggregate(db, pipeline):
    result = db.ottawa.aggregate(pipeline)

    return result



### Main

if __name__ == '__main__':
    db = get_db('osm')

    import logging
    import pprint
    import os



    # Line below toggles logging output to external file - uncomment to disable
    # logging.disable(logging.CRITICAL) # Uncomment to disable logging
    logging.basicConfig(filemode='w',
                        filename='..\\[Output]\\' + os.path.basename(__file__) + ' - output.txt',
                        level=logging.DEBUG,
                        format='%(levelname)s - %(message)s'
                        )
    def query_db_composition():
        print('Number of documents: ' + str(db.ottawa.find().count()))
        print('Number of nodes: ' + str(db.ottawa.find({'type' : 'node'}).count()))
        print('Number of ways: ' + str(db.ottawa.find({'type' : 'way'}).count()))

        logging.debug(pprint.pformat('Number of documents: ' + str(db.ottawa.find().count())))
        logging.debug(pprint.pformat('Number of nodes: ' + str(db.ottawa.find({'type' : 'node'}).count())))
        logging.debug(pprint.pformat('Number of ways: ' + str(db.ottawa.find({'type' : 'way'}).count())))


    def query_unique_users():
        users = str(len(db.ottawa.distinct('created.user')))
        print('Number of unique users: '+ users)

        logging.debug(pprint.pformat('Number of unique users: ' + users))


    def query_user_list():
        result = db.ottawa.distinct('created.user')
        users = []

        for r in result:
            users.append(r)

        print('List of unique users: ')
        pprint.pprint(users)

        # logging.debug(pprint.pformat('Users:'))
        # logging.debug(pprint.pformat(users, indent=4)) # Unicode error in logging output

    def query_single_entry_users():
        result = aggregate(db, single_entry_users_pipeline())
        users = []

        for r in result:
            users.append(r)

        print('Number of users with a single entry: ')
        pprint.pprint(users, indent=4)

        logging.debug(pprint.pformat('Number of users with a single entry:: '))
        logging.debug(pprint.pformat(users, indent=4))


    def query_top_contributors():
        result = aggregate(db, top_contributors_pipeline())
        contributors = []

        for r in result:
            contributors.append(r)

        print('\n' + 'Contributors: ')
        pprint.pprint(contributors, indent=4)

        # logging.debug(pprint.pformat('Contributors: '))
        # logging.debug(pprint.pformat(contributors, indent=4)) # Unicode error in logging output


    def query_data_sources():
        result = aggregate(db, data_source_pipeline())
        sources = []

        for r in result:
            sources.append(r)

        print('\n' + 'Data Source: ')
        pprint.pprint(sources, indent=4)

        # logging.debug(pprint.pformat('Data Source: '))
        # logging.debug(pprint.pformat(sources, indent=4)) # Unicode error in logging output


    def query_city_by_regions():
        result = aggregate(db, city_by_region_pipeline())
        regions = []

        for r in result:
            regions.append(r)

        print('\n' + 'Regions: ')
        pprint.pprint(regions, indent=4)

        logging.debug(pprint.pformat('Regions: '))
        logging.debug(pprint.pformat(regions, indent=4))


    def query_cuisine_types():
        result = aggregate(db, cuisine_types_pipeline())
        cuisines = []

        for r in result:
            cuisines.append(r)

        print('\n' + 'Cuisine type: ')
        pprint.pprint(cuisines, indent=4)

        # logging.debug(pprint.pformat('Cuisine type: '))
        # logging.debug(pprint.pformat(cuisines, indent=4)) # Unicode error in logging output


    query_db_composition()
    query_unique_users()
    query_user_list()
    query_single_entry_users()
    query_top_contributors()
    query_data_sources()
    query_city_by_regions()
    query_cuisine_types()
