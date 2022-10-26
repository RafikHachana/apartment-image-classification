from .database import Database
import datetime
from pymongo.errors import DuplicateKeyError


class AdsDB(Database):
    def __init__(self, collection):
        super().__init__('adsDB', collection)

    def insert_ad(self, parameters):
        parameters['_id'] = parameters['offer_number']
        parameters['date_scrapped'] = str(datetime.datetime.now().date())
        try:
            self.insert_one(parameters)
        except DuplicateKeyError:
            pass
