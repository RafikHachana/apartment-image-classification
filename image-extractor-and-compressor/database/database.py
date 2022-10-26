import pymongo
from .. import config


class Database:
    def __init__(self, db, collection):
        client = pymongo.MongoClient(config.MONGODB_CONNECTION_URL)
        self.collection = client[db][collection]

    def find_one_by_id(self, _id):
        obj = self.collection.find_one({'_id': _id})
        return obj

    def find(self, query=None):
        if query:
            obj = self.collection.find(query)
        else:
            obj = self.collection.find()
        return obj

    def find_one(self, query):
        obj = self.collection.find_one(query)
        return obj

    def get_all_ids(self):
        ids = []
        for _id in self.collection.find({}, {'_id': 1}):
            ids.append(_id['_id'])
        return ids

    def update_many(self, query, _set):
        self.collection.update_many(query, {'$set': _set})

    def update_one_by_id(self, _id, _set):
        self.collection.update_many({'_id': _id}, {'$set': _set})

    def insert_one(self, document):
        self.collection.insert_one(document)

    def delete_one_by_id(self, _id):
        self.collection.delete_one({'_id': _id})

    def count_documents(self, query):
        return self.collection.count_documents(query)

    @property
    def length(self):
        return self.collection.count_documents({})
