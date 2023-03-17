# Inserting GPS coordinates into images with Python - Work in Progress

## Overview
Included in this repo is a script to bulk insert GPS coordinate data into a set of images.
Using piexif, this script reads longitude and latitude coordindates from a csv file, and updates the image with the corresponding GPS data. Read more about piexif here: https://piexif.readthedocs.io/en/latest/about.html
This script also uses PIL: https://pillow.readthedocs.io/en/latest/index.html

## Installation
* Install the latest version of Python: https://www.python.org/downloads/
* And then:
```bash
git clone https://github.com/wolcade/pando-metadata.git
cd pando-metadata
pip install piexif
pip install Pillow
```

## Running the script
To see required and optional arguments run:
```bash
py Test.py
```
To see a preview of the GPS conversion process without updating the image files:
```bash
py Test.py --imageDirectory 'PATH_TO_IMAGE_FOLDER' --csvFile 'PATH_TO_CSV_FILE' --verbose
```

To insert the GPS coordinates into the metadata of the images :
```bash
py Test.py --imageDirectory 'PATH_TO_IMAGE_FOLDER' --csvFile 'PATH_TO_CSV_FILE' --verbose --write
```

After metadata insertion, you can validate the results :
```bash
py Test.py --imageDirectory 'PATH_TO_IMAGE_FOLDER' --csvFile 'PATH_TO_CSV_FILE' --verbose --validate
```
