#



'''
Command to import cleaned osm json file:
  mongoimport --db osm_ottawa --collection full --file ottawa_canada_sample.osm.json
'''


def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db





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
                    {"$match" : {"_id" : {"$ne" : None}}},
                    {'$sort' : {'count' : -1}}
                ]

    return pipeline


# def address_query():
#     # query = {"address.city" : {"$exists" : 1}}
#     query = {"type" : {"$exists" : 1}}
#     return query


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


def aggregate(db, pipeline):
    result = db.full.aggregate(pipeline)

    return result


if __name__ == '__main__':
    db = get_db('osm_ottawa')

    import pprint
    # result = aggregate(db, furthest_from_parliament())
    # result = aggregate(db, cuisine_types_pipeline())
    # result = aggregate(db, data_source_pipeline())
    # result = aggregate(db, city_by_region_pipeline())
    # result = aggregate(db, top_contributors_pipeline())
    pprint.pprint(result['result'])
