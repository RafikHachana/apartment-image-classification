from datetime import datetime
import abc
import utils
import traceback
from src.multithreading import MultiThreading
import math
import config


class Scrapper:
    def __init__(self):
        self.data = []
        self.search_pages = []
        self.property_links = []
        self.page_limit = 0
        self.website_name = ''
        self.website_url = ''
        self.poland_search_page = ''
        self.db = None
        self.results = {'added': 0, 'skipped': 0, 'failed': 0}
        self.total_properties = 0
        self.start_time = None
        self.tqdm_bar = None

    def scrap(self):
        try:
            self.start_time = datetime.today()
            utils.log(f'Started scrapping {self.total_properties} properties from {self.website_url}')
            self.scrap_search_pages(self.poland_search_page)
            MultiThreading().join_all()
        finally:
            end = datetime.today()
            total_scrapped = sum(self.results.values())
            utils.log(f'Scrapped {total_scrapped} properties from {self.website_url} in '
                      f'{(end - self.start_time).seconds // 60} minutes')
            utils.log(self.results)
            utils.log('\n\n--------------------------------------\n\n')

    def join_property(self, url):
        try:
            parameters, data = self.parse_property(url)
            if not parameters:
                self.results['skipped'] += 1
            else:
                if self.db.count_documents({'_id': parameters['offer_number']}) == 0:
                    parameters['images'] = self.scrap_images(data, url)
                    self.db.insert_ad(parameters)
                    self.results['added'] += 1
                else:
                    self.results['skipped'] += 1
        except:
            utils.log(f'failed to join property {url}', error=True)
            print(traceback.format_exc())
            self.results['failed'] += 1
        self.tqdm_bar.step()

    @abc.abstractmethod
    def parse_property(self, url):
        pass

    @abc.abstractmethod
    def scrap_images(self, data, ad_url, num_images=5):
        pass

    @abc.abstractmethod
    def scrap_search_result(self, url):
        pass

    @abc.abstractmethod
    def get_num_properties(self, response):
        pass

    @abc.abstractmethod
    def scrap_administrative_divisions(self, url):
        pass

    def scrap_search_pages(self, url):
        response = utils.get_request(url)
        if not response:
            return
        num_properties = self.get_num_properties(response)
        total_pages = int(math.ceil(num_properties / self.page_limit))
        if num_properties >= config.otodom.search_limit:
            self.scrap_administrative_divisions(url)
        else:
            multithreading = MultiThreading()
            for cnt in range(1, total_pages + 1):
                full_url = f'{url}&page={cnt}&limit={self.page_limit}'
                multithreading.add_thread(self.scrap_search_result, (full_url, ))
