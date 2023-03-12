from decimal import *
import csv
import piexif
from PIL import Image
import os

def main():
    gpsLocationList = readCSVToDict()

    output_path = '../output'

    #Open directory and loop over images
    directory = os.fsencode(output_path)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        img_path = f'{output_path}/{filename}'

        if filename.endswith('.jpg'):
            #TODO: Make dynamic for location start letter or find a better way
            if filename.startswith('i'):
                locationKey = filename[0:3]
                #Grab lat/lon from csv data
                gpsData = gpsLocationList[locationKey.upper()]
                #print(gpsData)
                print('validating ', filename)
                validateGPSData(img_path, gpsData)
            else:
                print('skipping ', filename)
    print('Completed')

    #convertDMSToDD((38, 31, 44.9322))

def readCSVToDict():
    # TODO: Set to command line input?
    # {[locationKey]: {lat: number, lon: number}}
    gpsLocationDict = {}
    with open('CR9_Locations_GPS.csv', mode='r') as file:
        csvFile = csv.DictReader(file)
        for row in csvFile:
            gpsLocationDict[row["Location"]] = {"lat": row['Rec Lat'], "lon": row["Rec Lon"]}
    return gpsLocationDict

def validateGPSData(new_img_path, gpsData):

    im = Image.open(new_img_path)
    
    exif_dict = piexif.load(im.info["exif"])
    newGPSLat = exif_dict["GPS"][piexif.GPSIFD.GPSLatitude]
    decimalDegreesLat = convertDMSToDD(newGPSLat)

    newGPSLon = exif_dict["GPS"][piexif.GPSIFD.GPSLongitude]
    decimalDegreesLon = convertDMSToDD(newGPSLon) * -1

    gpsDataLat = Decimal(gpsData["lat"]).quantize(Decimal('0.0000000001'))
    gpsDataLon = Decimal(gpsData["lon"]).quantize(Decimal('0.0000000001'))

    print(f"    {newGPSLat}, {newGPSLon}")

    print(f"    converted exif GPS lat {decimalDegreesLat} equals csv lat {gpsDataLat}: {decimalDegreesLat == gpsDataLat}")
    print(f"    converted exif GPS lon {decimalDegreesLon} equals csv lon {gpsDataLon}: {decimalDegreesLon == gpsDataLon}")


def convertDMSToDD(dmsTuple):

    degrees = Decimal(dmsTuple[0][0])
    minutes = Decimal(dmsTuple[1][0])
    seconds = Decimal(dmsTuple[2][0]) / Decimal(dmsTuple[2][1])

    decimalDegrees = Decimal(degrees) + Decimal(minutes / 60) + Decimal(seconds / (60 * 60))

    return Decimal(decimalDegrees).quantize(Decimal('0.0000000001'))





def convertDegreesToDMS(decimalDegrees):

    decimal = Decimal(decimalDegrees)
    degrees = abs(int(decimal))
    minutes = (decimal % 1) * 60
    seconds = (minutes % 1) * 60

    minutes = abs(int(minutes))
    (seconds_num, seconds_denominator) = abs((seconds)).as_integer_ratio()
    #print ("Degrees: " + str(degrees) + " Minutes: " + str(minutes) + " Seconds: " + str(seconds))

    return ((degrees, 1), (minutes, 1), (seconds_num, seconds_denominator))

    
if __name__ == "__main__":
    main()