from database import AdsDB
from utilities import *
from .standards_mapping import get_mapper


def main():
    mapper = get_mapper()
    for collection in get_collections_names():
        db = AdsDB(collection)
        data_list = db.find({'year_of_build': {'$lt': '2022'}})
        for data in data_list:
            try:
                images = parse_string_representation_of_list(data['images'])
                condition = mapper[data['condition'].upper()]
                for index, image in enumerate(images):
                    save_image_file(data['_id'], index, condition, image, collection)
            except:
                pass


if __name__ == '__main__':
    main()
