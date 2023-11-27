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

- **download_data.py**

        download_data.py [-h] [-d {rain,temp,clouds} [{rain,temp,clouds} ...]]

        options:
            -h, --help            show this help message and exit
            -d {rain,temp,clouds} [{rain,temp,clouds} ...], --data_types {rain,temp,clouds} [{rain,temp,clouds} ...]
                                  Metrics wanted (default: ['rain', 'temp', 'clouds'])

        example :
        python3 down_data.py -d rain temp

- **process_data.py**

        python3 process_data.py [-h] [--lat LAT] [--lon LON] [-r RADIUS] [-d {rain,temp,clouds} [{rain,temp,clouds} ...]]

        options:
            -h, --help            show this help message and exit
            --lat LAT             Center latitude (in deg) (default: None)
            --lon LON             Center longitude (in deg) (default: None)
            -r RADIUS, --radius RADIUS
                                  Radius (in km) (default: 100)
            -d {rain,temp,clouds} [{rain,temp,clouds} ...], --data_types {rain,temp,clouds} [{rain,temp,clouds} ...]
                                  Metrics wanted (default: ['rain', 'temp', 'clouds'])

        example :
        python3 process_data.py --lat 43.6 --lon 1.44 -r 100 -d rain temp
