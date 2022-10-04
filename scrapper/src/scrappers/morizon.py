import time
from src.scrappers import Scrapper
import traceback
import re
import utils
import config
from src.database import AdsDB
from src.multithreading import MultiThreading
import os
import uuid
import lxml


class MorizonScrapper(Scrapper):
    def __init__(self):
        super().__init__()
        self.page_limit = 30
        self.website_name = 'morizon'
        self.website_url = 'morizon.pl'
        self.poland_search_page = 'https://www.morizon.pl/mieszkania/warszawa/?ps%5Bmarket_type%5D%5B0%5D=2'
        self.total_properties = self.get_num_properties(utils.get_request(self.poland_search_page))
        self.tqdm_bar = utils.Mytqdm(self.total_properties, desc='number of scrapped properties')
        self.db = AdsDB(config.morizon.db_collection)

    def parse_property(self, url):
        response = utils.get_request(url)
        if not response:
            return None, None
        try:  # check if ad still exists
            response.html.xpath('//th[contains(text(),"Numer oferty:")]/following-sibling::td')[0]
        except IndexError:
            utils.log(f'ad {url} does not exist', error=True)
            return None, None
        html = lxml.html.fromstring(response.text)
        parameters = self.scrap_parameters(html, url)
        return parameters, response.html

    def scrap_parameters(self, html, url):
        def fix_area(area_):
            """
            change the format of area
            """
            area_ = area_.replace(',', '.')
            area_ = area_.replace('\xa0', ' ')
            area_ = float(re.sub(r' .+', '', area_))
            return area_

        def fix_m2price(_m2price):
            """
            change the format of price per square
            """
            _m2price = _m2price.replace('\xa0', "")
            _m2price = _m2price.replace('zł', "")
            _m2price = _m2price.replace(',', ".")
            _m2price = re.sub(r'\s', '', _m2price)
            _m2price = float(_m2price)
            return _m2price

        def fix_description(text):
            ret = text.replace(u'\xa0', u' ')
            return ret

        def to_text(elem):
            txt = elem.text_content()
            try:
                if txt[0] == '\n':
                    txt = txt[1:]
            except:
                pass
            try:
                if txt[-1] == ' ':
                    txt = txt[: -1]
            except:
                pass
            return txt

        row = {
            'url': url,
        }
        offer_number1 = to_text(html.xpath('//th[contains(text(),"Numer oferty:")]/following-sibling::td')[0])
        offer_number2 = url.split('-')[-1].split('?')[0]
        row['offer_number'] = offer_number1 + '-' + offer_number2
        try:
            text = [el.text for el in html.xpath('//div[@class="col-xs-9"]//h1/strong/span')]
            text = ''.join(text)
            if text[0] == '\n':
                text = text[1:]
            row['address'] = text
        except:
            return None
        try:
            price = to_text(html.xpath('//li[@class="paramIconPrice"]/em')[0])
            row['price'] = int(re.sub(r'\D', '', price))
        except ValueError:
            row['price'] = None
        try:
            m2price = to_text(html.xpath('//li[@class="paramIconPriceM2"]/em')[0])
            row['m2price'] = fix_m2price(m2price)
        except IndexError:
            row['m2price'] = None
        area = to_text(html.xpath('//li[@class="paramIconLivingArea"]/em')[0])
        row['area'] = fix_area(area)
        try:
            row['rooms'] = int(to_text(html.xpath('//li[@class="paramIconNumberOfRooms"]/em')[0]))
        except IndexError:
            row['rooms'] = None
        try:
            row['year_of_build'] = int(
                to_text(html.xpath('//th[contains(text(),"Rok budowy:")]/following-sibling::td')[0]))
        except IndexError:
            row['year_of_build'] = None
        try:
            description = to_text(html.xpath('//div[@id="description"]')[0])
            row['description'] = fix_description(description)
        except IndexError:
            row['description'] = None
        try:
            row['condition'] = \
                to_text(html.xpath('//th[contains(text(),"Stan nieruchomości")]/following-sibling::td')[0])
        except IndexError:
            return None
        row = {key: value for key, value in sorted(row.items())}
        return row

    def scrap_images(self, html, ad_url, num_images=5):
        images = html.xpath('//div[@class="row imageThumbs"]//li/img/@data-original')
        if num_images == 'all':
            num_images = len(images)
        if not images:
            return []
        ret = []
        for i in range(min(num_images, len(images))):
            image = images[i]
            parts = image.split('/')
            parts[-2] = '2'
            parts[-3] = '936'
            parts[-4] = '1664'
            image_url = '/'.join(parts)
            fname = str(uuid.uuid4()) + '.jpg'
            if not utils.download_image(image_url, fname, resize=(832, 468)):
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
            tree = response.html
            links = tree.xpath('//a[@class="property_link property-url"]/@href')
            if len(links) == 0:
                if tries:
                    time.sleep(10)
                    self.scrap_search_result(url, tries-1)
                else:
                    utils.log(f"Scrapped 0 apartments from {url}!", error=True)
            multithreading = MultiThreading()
            for full_url in links:
                if full_url not in self.property_links:
                    self.property_links.append(full_url)
                    multithreading.add_thread(self.join_property, (full_url, ))
        except:
            utils.log(traceback.format_exc(), error=True)

    def get_num_properties(self, response):
        tree = response.html
        text = tree.xpath("//p[@class='listing-header__description']")[0].text.split(' ')[1]
        if text == 'jedno':
            num_properties = 1
        else:
            num_properties = int(text)
        return num_properties

    def scrap_administrative_divisions(self, url):
        response = utils.get_request(url)
        if not response:
            return
        tree = response.html
        divisions_urls = tree.xpath('//div[@id="locationListChildren"]//li[@class="clearfix"]/a/@href')
        multithreading = MultiThreading()
        for division_url in divisions_urls:
            full_url = 'https://www.morizon.pl' + division_url
            multithreading.add_thread(self.scrap_search_pages, (full_url, ))
