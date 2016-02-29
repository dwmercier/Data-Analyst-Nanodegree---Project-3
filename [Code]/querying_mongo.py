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


def one_time_users_pipeline():
    pipeline = [
        {'$group':
            {
                '_id' : '$created.user',
                'count' : {'$sum':1}
            }
        },
        {'$group':
             {
                 '_id' : '$count',
                 'num_users' : {'$sum':1}
             }
        },
        {'$sort' : { '_id' : 1}},
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

    import pprint
    
    print('Number of documents: ' + str(db.ottawa.find().count()))
    print('Number of nodes: ' + str(db.ottawa.find({'type' : 'node'}).count()))
    print('Number of ways: ' + str(db.ottawa.find({'type' : 'way'}).count()))
    # result = db.ottawa.distinct('created.user')
    # print(len(db.ottawa.distinct('created.user')))
    # result = aggregate(db, cuisine_types_pipeline())
    # result = aggregate(db, data_source_pipeline())
    # result = aggregate(db, city_by_region_pipeline())
    result = aggregate(db, top_contributors_pipeline())
    for r in result:
        pprint.pprint(r)
