import traceback
from datetime import datetime
from src.scrappers import MorizonScrapper, OtodomScrapper
from time import sleep
import gc
import utils


def scrap_portal(scrapper):
    try:
        scrapper.scrap()
        del scrapper
        gc.collect()
        sleep(2)
    except:
        utils.log(traceback.format_exc(), error=True)


def main():
    last_scrapped = None
    while True:
        today = datetime.today().date()
        if last_scrapped != today:
            scrap_portal(MorizonScrapper())
            sleep(1)
            scrap_portal(OtodomScrapper())
            sleep(1)
            last_scrapped = today
