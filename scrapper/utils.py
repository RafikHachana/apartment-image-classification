import traceback
from datetime import datetime
from requests_html import HTMLSession
from time import sleep
import psutil
import os
import random
import sys
import config
import tqdm
import base64
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


class Mytqdm(tqdm.tqdm):
    def __init__(self, steps=1, desc=None):
        tqdm.tqdm.__init__(self, desc=desc)
        self.total = steps

    def step(self):
        self.update()


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


with open(f'proxies/proxies.txt', 'r') as f:
    lines = f.read()
temp_proxies = lines.split('\n')
proxies = []
for proxy in temp_proxies:
    try:
        ip, port, username, password = proxy.split(':')
        proxies.append(proxy)
    except:
        pass


def log(*argv, end='\n', error=False):
    process = psutil.Process(os.getpid())
    memory = str(process.memory_info().rss // 1024 // 1024) + ' MB'
    print(f'{Bcolors.BOLD}{Bcolors.OKBLUE}{memory} {Bcolors.OKGREEN}{datetime.now().replace(microsecond=0)}:{Bcolors.ENDC}', end=' ')
    if error:
        print(f'{Bcolors.BOLD}{Bcolors.FAIL}WARNING:{Bcolors.ENDC}', end=' ')
        for arg in argv:
            print(f'{Bcolors.BOLD}{Bcolors.FAIL}{arg}{Bcolors.ENDC}', end=' ')
    else:
        for arg in argv:
            print(arg, end=' ')
    print('', end=end)


def get_request(URL, use_proxy=True, attempt=5):
    def _return(wait_time=1):
        if attempt:
            sleep(wait_time)
            return get_request(URL, use_proxy, attempt - 1)
        else:
            log(f'failed to GET request {URL}', error=True)
            return None

    session = HTMLSession()
    proxy = _get_random_proxy()
    try:
        if use_proxy:
            response = session.get(URL, stream=True, proxies={
                "http": proxy,
                "https": proxy
            })
        else:
            response = session.get(URL, stream=True)
    except:
        return _return()
    session.close()

    if _invalid_morizon(response) or response.status_code == 403:
        log(proxy, 'is banned', error=True)
        with open('proxies/banned.txt', 'a') as f:
            f.write(proxy + '\n')
        return get_request(URL, use_proxy=use_proxy, attempt=attempt)

    if response.status_code in [404, 502]:
        return _return()
    if response.status_code == 503 or response.status_code == 500 or response.status_code == 502:
        return _return()
    if response.status_code != 200:
        raise Exception(f'{datetime.now()} Requesting URL {URL} returned {response.status_code} response!')

    return response


def _get_random_proxy():
    proxy = random.choice(proxies)
    ip, port, username, password = proxy.split(':')
    proxy = f'http://{username}:{password}@{ip}:{port}'
    with open('proxies/banned.txt', 'r') as f:
        lines = f.read().split('\n')
        if proxy in lines:
            return _get_random_proxy()
    return proxy


def _invalid_morizon(response):
    try:
        tree = response.html
        element = tree.xpath('/html/head/script[1]/@src')[0]
        return element == 'https://www.google.com/recaptcha/api.js'
    except:
        return False


def concat(lst):
    ret = []
    for element in lst:
        ret += element
    return ret


def download_image(url, fname, resize=None):
    """
    Downloads the image in the given url and saves it to the file name passed

    :return: True if process succeeded, False otherwise
    """
    try:
        r = get_request(url, use_proxy=False)
        if r and r.status_code == 200:
            with open(fname, 'wb') as f:
                f.write(r.content)
            if resize:
                img = Image.open(fname)
                img.thumbnail(resize)
                img.save(fname)
            return True
        else:
            return False
    except:
        log(traceback.format_exc(), error=True)
        return False


def img2json(fname):
    """converts an image in the given file name to a json with img data in utf-8 and returns it"""
    with open(fname, 'rb') as f:
        img = f.read()
    ret = {
        'img': base64.encodebytes(img).decode('utf-8')
    }
    return ret
