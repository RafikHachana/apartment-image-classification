from pathlib import Path
import io
from PIL import Image
import base64
import json
import config


def get_collections_names():
    return config.DATABASES['MONGODB']['collections']


def get_db_name():
    return config.DATABASES['MONGODB']['name']


def get_connection_url():
    return config.DATABASES['MONGODB']['connection_url']


def get_csv_filename_for_mapper():
    return config.DATABASES['CSV']['MAPPER']


def check_if_file_exists(directory: str):
    return Path(directory).is_file()


def get_condition(numeric_val):
    return 'bad' if numeric_val == 0 else 'good'


def get_directory(condition_numeric):
    condition = get_condition(condition_numeric)
    return f'./images/{condition}/'


def get_image_name(_id: str, index, collection=None):
    prefix = ''
    _id = _id.replace('/', '-')
    if (collection is not None) and (_id.find(collection) == -1):
        prefix = collection
    return f"{prefix}-{_id}-{index}.png"


def compress_image(image_base64_str):
    buffer = io.BytesIO()
    imgdata = base64.b64decode(image_base64_str)
    img = Image.open(io.BytesIO(imgdata))
    new_img = img.resize((128, 128))
    new_img.save(buffer, format="PNG")
    img_b64 = base64.b64encode(buffer.getvalue())
    return img_b64


def save_image_file(_id, index, condition, image, collection=None):
    root_data_directory = get_directory(condition)
    image_name = get_image_name(_id, index, collection)
    file_directory = root_data_directory + image_name
    if check_if_file_exists(file_directory):
        return
    with open(file_directory, "wb") as fh:
        img_b64 = compress_image(image)
        fh.write(base64.decodebytes(img_b64))


def parse_string_representation_of_list(list_str: str):
    return json.loads(list_str)
