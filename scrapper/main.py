from src.scrappers import daily_scrapper
import config
from argparse import ArgumentParser


def read_arguments():
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="filename",
                        help="write output to FILE", metavar="FILE")
    args = parser.parse_args()
    config.output = args.filename


def main():
    read_arguments()
    daily_scrapper.main()


if __name__ == '__main__':
    main()