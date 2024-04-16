# weather_data_visualization : Weather map generator for for short-term forecasting

The aim of this repository is to provide a Python API for generating maps using data from Météo France's weather models.

The project is divided into two parts:

- download_data, which allows you to download data from the AROME model of Météo France. Depending on the date and time of launch, the most recent run is selected to obtain the most accurate data possible at time t

- process_data which uses the downloaded data to generate maps with the data on an open street map background, for the next 24 hours

<br>

## Requierments

The API requires Python 3.X with the following libraries:

- eccodes
- numpy
- matplotlib
- cartopy

The eccodes Python library is just a wrapper, and then need the libeccodes-dev package to be installed (with apt for example).

<br>

## Usage

- **download_arome_data.py**

        python3 download_arome_data.py [-h] [-d {rain,temp,clouds} [{rain,temp,clouds} ...]]

        options:
        -h, --help            show this help message and exit
        -d {rain,temp,clouds} [{rain,temp,clouds} ...], --data_types {rain,temp,clouds} [{rain,temp,clouds} ...]
                                Metrics wanted (default: ['rain', 'temp', 'clouds'])

        example :
        python3 download_arome_data.py -d temp

- **arome_data_to_image.py**

        python3 arome_data_to_image.py [-h] [--mlat MLAT] [--Mlat MLAT] [--mlon MLON] [--Mlon MLON] [-p PROJECTION] [-d {rain,temp,clouds} [{rain,temp,clouds} ...]]

        options:
        -h, --help            show this help message and exit
        --mlat MLAT           Minimum latitude (in deg) (default: None)
        --Mlat MLAT           Maximum latitude (in deg) (default: None)
        --mlon MLON           Minimum longitude (in deg) (default: None)
        --Mlon MLON           Maximum longitude (in deg) (default: None)
        -p PROJECTION, --projection PROJECTION
                                Projection code (default: EPSG:4326)
        -d {rain,temp,clouds} [{rain,temp,clouds} ...], --data_types {rain,temp,clouds} [{rain,temp,clouds} ...]
                                Metrics wanted (default: ['rain', 'temp', 'clouds'])

        example :
        python3 arome_data_to_image.py --mlat 40 --Mlat 54 --mlon -8 --Mlon 12 -p EPSG:3857 -d temp
