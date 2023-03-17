import csv
from decimal import *
import piexif
from PIL import Image, ExifTags
import os
import argparse
import time

PRECISION_TEN = Decimal('0.0000000001')


def readCSVToDict(csvPath):
    # {[locationKey]: {lat: number, lon: number}}
    gpsLocationDict = {}
    with open(csvPath, mode='r') as file:
        csvFile = csv.DictReader(file)
        for row in csvFile:
            print(row)
            gpsLocationDict[row["Location"]] = {
                "lat": row['Rec Lat'], "lon": row["Rec Lon"]}
    return gpsLocationDict


def main():
    c = getcontext()
    c.prec = 20

    verboseFlag = 0
    writeFlag = 0

    # Args: image directory, csv file, writeFlag, verbose, validate
    parser = argparse.ArgumentParser(
        description='Insert GPS coordinates into images')
    parser.add_argument('--imageDirectory', type=str, required=True)
    parser.add_argument('--csvFile', type=str, required=True)

    parser.add_argument('--write', required=False, action='store_true')
    parser.add_argument('--verbose', required=False, action='store_true')
    parser.add_argument('--validate', required=False, action='store_true')

    args = parser.parse_args()

    if args.verbose:
        print('verbosity turned on\n')
        verboseFlag = 1

    if args.write:
        print('write mode turned on\n')
        writeFlag = 1

    folder_path = args.imageDirectory
    if not os.path.exists(folder_path):
        raise ValueError(f'Invalid Path. Cannot find {folder_path}.')

    csv_path = args.csvFile
    if not os.path.exists(csv_path):
        raise ValueError(f'Invalid Path. Cannot find {csv_path}.')

    output_path = f'{folder_path}_With_GPS'
    if not os.path.exists(output_path) and args.write:
        print(f'Creating output folder {output_path}\n')
        os.makedirs(output_path)

    gpsLocationDictionary = readCSVToDict(csv_path)
    imageCount = 0

    print(f'\nReading Images from {folder_path}.\n')

    if writeFlag:
        print(f' Writing new GPS images to {output_path}\n')

    # Open directory and loop over images
    directory = os.fsencode(folder_path)
    files = os.listdir(directory)
    # TODO: May include folders too
    fileList = [os.fsdecode(f) for f in files]
    print('Total files in directory... ', len(fileList))

    success = []
    failure = []
    missing = []

    for file in fileList:

        img_path = f'{folder_path}/{file}'
        new_img_path = f'{output_path}/{file}'

        if file.endswith('.jpg') and not (file.startswith('EndSlate') or file.startswith('OpenSlate')):
            location = file.split('-')[0]

            if verboseFlag:
                print(f'Processing Location {location} from csv')

            # Grab lat/lon from csv data
            gpsData = gpsLocationDictionary[location.upper()]

            if args.validate:
                validationStatus = validateGPSData(
                    img_path, gpsData, location, verboseFlag)
                if validationStatus == 1:
                    success.append(location)
                if validationStatus == 0:
                    missing.append(location)
                if validationStatus == -1:
                    failure.append(location)
            else:
                setGPSData(img_path, new_img_path, gpsData,
                           location, writeFlag, verboseFlag)

            imageCount += 1
        else:
            print('skipping ', file)

    print(
        f'Completed Processing {folder_path}. {imageCount} images processed.\n')
    if args.validate:
        print(
            f'\nVALIDATION SUMMARY\n\nSuccess:\n{success}\n{len(success)} files\n\nFailure\n{failure}\n{len(failure)} files\n\nMissing GPS Data\n{missing}\n{len(missing)} files')


def setGPSData(img_path, new_img_path, gpsData, location, writeFlag, verboseFlag):
    # For each image, load the exif
    # set the tags for GPS
    # insert new tags into image
    # save image

    im = Image.open(img_path)
    exif_dict = piexif.load(img_path)

    if gpsData["lat"] != '' and gpsData["lon"] != '':
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = convertDegreesToDMS(
            gpsData["lat"])
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = convertDegreesToDMS(
            gpsData["lon"])
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = "W"
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = "N"

        if verboseFlag:
            print(
                f'    Set GPSLatitude: {gpsData["lat"]} to {exif_dict["GPS"][piexif.GPSIFD.GPSLatitude]}')
            print(
                f'    Set GPSLongitude: {gpsData["lon"]} to {exif_dict["GPS"][piexif.GPSIFD.GPSLongitude]}')
            print(
                f'    Set GPSLatitudeRef to {exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef]}')
            print(
                f'    Set GPSLongitudeRef to {exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef]}')
            print('')

    else:
        if verboseFlag:
            print(f'    Missing Coordinates for location {location}\n')

    if writeFlag == 1:
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, img_path)
        # im.save(new_img_path,"jpeg",exif=exif_bytes)
        print(new_img_path + ' saved successfully')
        print('')


def convertDegreesToDMS(decimalDegrees):
    # Set precision to at least 10 decimal places. Need to validate further
    c = getcontext()
    c.prec = 20

    decimal = Decimal(decimalDegrees)
    degrees = abs(int(decimal))
    minutes = (decimal % 1) * 60
    seconds = (minutes % 1) * 60

    minutes = abs(int(minutes))
    (seconds_num, seconds_denominator) = abs((seconds)).as_integer_ratio()
    return ((degrees, 1), (minutes, 1), (seconds_num, seconds_denominator))


def convertDegreesToDMSBridge(decimalDegrees):
    # Set precision to at least 10 decimal places. Need to validate further
    c = getcontext()
    c.prec = 20

    decimal = Decimal(decimalDegrees)
    degrees = abs(int(decimal))
    minutes = (decimal % 1) * 60
    seconds = (minutes % 1) * 60

    minutes = abs(minutes)
    return (degrees, minutes)


def convertDMSToDD(dmsTuple):

    degrees = Decimal(dmsTuple[0][0])
    minutes = Decimal(dmsTuple[1][0])
    seconds = Decimal(dmsTuple[2][0]) / Decimal(dmsTuple[2][1])

    decimalDegrees = Decimal(
        degrees) + Decimal(minutes / 60) + Decimal(seconds / (60 * 60))

    return Decimal(decimalDegrees)


def validateGPSData(new_img_path, gpsData, location, verbose):

    if gpsData["lat"] != '' and gpsData["lon"] != '':
        im = Image.open(new_img_path)
        mTime = os.path.getmtime(new_img_path)
        modifiedTime = time.ctime(mTime)

        exif_dict = piexif.load(im.info["exif"])

        newGPSLat = exif_dict["GPS"][piexif.GPSIFD.GPSLatitude]
        decimalDegreesLat = convertDMSToDD(newGPSLat)

        newGPSLon = exif_dict["GPS"][piexif.GPSIFD.GPSLongitude]
        decimalDegreesLon = convertDMSToDD(newGPSLon) * -1
        print(f"FROM IMAGE {newGPSLat}, {newGPSLon}")

        print("FROM CSV ", gpsData["lat"], gpsData["lon"])
        gpsDataLat = Decimal(gpsData["lat"])
        gpsDataLon = Decimal(gpsData["lon"])

        if verbose:
            print(f"    Reading Image {location} modified at {modifiedTime}")
            print(f"    DMS Coordinates in Image: {newGPSLat}, {newGPSLon}")

            print(
                f"    converted exif GPS lat {decimalDegreesLat} equals csv lat {gpsDataLat}: {decimalDegreesLat == gpsDataLat}")
            print(
                f"    converted exif GPS lon {decimalDegreesLon} equals csv lon {gpsDataLon}: {decimalDegreesLon == gpsDataLon}")
            print(
                f"    DMS Coordinates in Bridge Format: {convertDegreesToDMSBridge(decimalDegreesLat)}, {convertDegreesToDMSBridge(decimalDegreesLon)}")

            print('')

        if decimalDegreesLat == gpsDataLat and decimalDegreesLon == gpsDataLon:
            return 1
        else:
            return -1

    else:
        if verbose:
            print(f"    missing gps data for {location}")
        return 0


if __name__ == "__main__":
    main()
