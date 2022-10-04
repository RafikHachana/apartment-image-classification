import json
import time
import os
import traceback
import utils
import config
from src.scrappers import Scrapper
from src.database import AdsDB
from src.multithreading import MultiThreading
from bs4 import BeautifulSoup
import warnings
import uuid
import lxml
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')


class OtodomScrapper(Scrapper):
    def __init__(self):
        super().__init__()
        self.page_limit = 500
        self.website_name = 'otodom'
        self.website_url = 'otodom.pl'
        self.poland_search_page = 'https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa?market=SECONDARY'
        self.total_properties = self.get_num_properties(utils.get_request(self.poland_search_page))
        self.tqdm_bar = utils.Mytqdm(self.total_properties, desc='number of scrapped properties')
        self.db = AdsDB(config.otodom.db_collection)

    def parse_property(self, url):
        response = utils.get_request(url)
        if not response:
            return None, None
        try:
            html = response.html
        except lxml.etree.ParserError:
            return self.parse_property(url)
        json_data = json.loads(html.xpath('//script[@id="__NEXT_DATA__"]')[0].text)
        try:
            json_data = json_data['props']['pageProps']['ad']
        except KeyError:
            utils.log(f'ad {url} does not exist', error=True)
            return None, None
        except:
            utils.log(traceback.format_exc(), error=True)
            return None, None
        parameters = self.scrap_parameters(json_data, url)
        return parameters, json_data

    def scrap_parameters(self, json_data, url):
        def fix_description(text):
            ret = BeautifulSoup(text, 'html5lib').text
            ret = ret.replace(u'\xa0', u' ')
            return ret

        parts = list(filter(lambda x: x != '', [doc['locative'] for doc in json_data['breadcrumbs']][2:]))
        address = ', '.join(parts)
        row = {
            'url': url,
            'address': address,
            'offer_number': json_data['target']['Id'],
            'description': fix_description(json_data['description'])
        }
        try:
            row['price'] = json_data['target']['Price']
        except KeyError:
            row['price'] = None
        except TypeError:
            row['price'] = None
        try:
            row['m2price'] = json_data['target']['Price_per_m']
        except KeyError:
            row['m2price'] = None
        except TypeError:
            row['m2price'] = None
        try:
            row['area'] = float(json_data['target']['Area'])
        except KeyError:
            row['area'] = None
        except TypeError:
            row['area'] = None
        try:
            if json_data['target']['Rooms_num'][0] == 'more':
                row['rooms'] = 11
            else:
                row['rooms'] = int(json_data['target']['Rooms_num'][0])
        except KeyError:
            row['rooms'] = None
        except TypeError:
            row['rooms'] = None
        except ValueError:
            row['rooms'] = 11
        try:
            row['condition'] = json_data['target']['Construction_status'][0]
        except KeyError:
            return None
        try:
            row['year_of_build'] = int(json_data['target']['Build_year'])
        except KeyError:
            row['year_of_build'] = None
        row = {key: value for key, value in sorted(row.items())}
        return row

    def scrap_images(self, json_data, ad_url, num_images=5):
        images = json_data['images']
        if num_images == 'all':
            num_images = len(images)
        if not images:
            return []
        ret = []
        for i in range(min(num_images, len(images))):
            image = images[i]
            image_url = image['medium']
            fname = str(uuid.uuid4()) + '.jpg'
            if not utils.download_image(image_url, fname):
                utils.log(f'Downloading image {image_url} failed from ad {ad_url}!', error=True)
                return []
            img = utils.img2json(fname)['img']
            os.remove(fname)
            ret.append(img)
        return ret

    def scrap_search_result(self, url, tries=1):
        response = utils.get_request(url)
        if not response:
            return
        try:
            html = response.html
            links = html.xpath('//div[@data-cy="search.listing"]//li/a/@href')
            if len(links) == 0:
                if tries:
                    time.sleep(10)
                    self.scrap_search_result(url, tries-1)
                else:
                    utils.log(f"Scrapped 0 apartments from {url}!", error=True)
            multithreading = MultiThreading()
            for link in links:
                full_url = 'https://www.otodom.pl' + link
                if full_url not in self.property_links:
                    self.property_links.append(full_url)
                    multithreading.add_thread(self.join_property, (full_url, ))
        except:
            utils.log(traceback.format_exc(), error=True)

    def get_num_properties(self, response):
        html = response.html
        json_data = json.loads(html.xpath('//script[@id="__NEXT_DATA__"]')[0].text)
        return json_data['props']['pageProps']['data']['searchAds']['pagination']['totalResults']

    def scrap_administrative_divisions(self, url):
        response = utils.get_request(url)
        if not response:
            return
        html = response.html
        divisions_urls = html.xpath('//a[@class="css-1s8gywf exbxamm1"]/@href')
        multithreading = MultiThreading()
        for division_url in divisions_urls:
            full_url = 'https://www.otodom.pl' + division_url
            multithreading.add_thread(self.scrap_search_pages, (full_url, ))
