
# Apartment Condition Classification
_By Kamil Sabbagh, Fadi Younes, Rafik Hachana (PMLDL project course, Innopolis University, Fall 2022)_

Apartment condition classification from images in order to detect overpriced apartment on online rental websites.

## Image Extractor and Compressor

This project features an Image Extractor that deals with apartment images, extracts them from MongoDB, and compresses them in order to store them in a new directory based on the apartment's condition.  

## Technical Requirements

The building blocks of this project were built using the following software:

*   Python 3.8.
*   Pandas 1.4.0, Numpy 1.22.1 for tabular data manipulation.
*   Pillow 8.4.0, Opencv 4.5.5.62 for Image Processing.
*   Pymongo 4.2.0 for working with MongoDB.

## DB Schema

The database was stored in Mongodb, which has two collections, one for Morizon and one for Otodom. Each document in these collections has the following schema:

`_id`: string(unique)  
`address`: string  
`area`: string  
`condition`: enumeration of Polish words  
`description`: string  
`m2price`: string  
`offer_number`: string  
`price`: string  
`rooms`: string  
`url`: string  
`year_of_build`: string  
`images`: list of strings  
`date_scrapped`: string (datatime)

The second database is a csv file containing the words used to describe the apartment's condition along with its appropriate standard (1 for good condition, 0 for bad condition).

## How to Run

Create `secret.py` in the root directory and add `MONGODB_CONNECTION_URL` variable

```css
pip install -r requirments.txt

python main.py
```
