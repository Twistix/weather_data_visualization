# ================================ Imports =====================================
import sys
import os
import argparse
import shutil
from datetime import datetime, timedelta
import math
import eccodes
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import gc
import json


# ================================ Constants =====================================
AVAILABLE_DATA_TYPES = ["rain","temp","clouds"]
AVAILABLE_BACKGROUNDS = ["none","osm"]

DEFAULT_BACKGROUND = "none"
DEFAULT_DATA_TYPE = AVAILABLE_DATA_TYPES

LAT_RATIO = 110.574
LON_RATIO = 111.320


# ============================= Useful functions =============================
def deg_to_rad(angle):
    return angle*math.pi/180


def time_format_iso8601(time):
    return "{:04d}".format(time.year)+"-"+"{:02d}".format(time.month)+"-"+"{:02d}".format(time.day)+"T"+"{:02d}".format(time.hour)+":00:00Z"


# =============================== Functions =======================================
def parse_inputs(available_data_types):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--mlat", type=float, help="Minimum latitude (in deg)")
    parser.add_argument("--Mlat", type=float, help="Maximum latitude (in deg)")
    parser.add_argument("--mlon", type=float, help="Minimum longitude (in deg)")
    parser.add_argument("--Mlon", type=float, help="Maximum longitude (in deg)")
    parser.add_argument("-b", "--background", type=str, default=DEFAULT_BACKGROUND, choices=AVAILABLE_BACKGROUNDS, help="Image background")
    parser.add_argument('-d', "--data_types", type=str, default=DEFAULT_DATA_TYPE, nargs='+', choices=AVAILABLE_DATA_TYPES, help="Metrics wanted")

    return parser.parse_args()


def create_data_figure(min_lat, max_lat, min_lon, max_lon, data_type, current_time, modele_info):
    #Process grib file
    print("Processing grib file for "+str(data_type)+" at hour H+"+"{:02d}".format(i))
    f = open("raw_data/"+str(data_type)+"/grib_"+str(data_type)+"_"+time_format_iso8601(current_time)+".grib2", "rb")
    gid = eccodes.codes_grib_new_from_file(f)
    Ni = eccodes.codes_get(gid, "Ni")   #Number of points allong a parallel or x axis
    Nj = eccodes.codes_get(gid, "Nj")   #Number of points allong a meridian or y axis
    values = eccodes.codes_get_array(gid, "values", float)
    lats = eccodes.codes_get_array(gid, "latitudes", float)
    lons = eccodes.codes_get_array(gid, "longitudes", float)
    grib_min_lat = np.min(lats)
    grib_max_lat = np.max(lats)
    grib_min_lon = np.min(lons)
    grib_max_lon = np.max(lons)
    values = np.reshape(values, (Nj, Ni))
    lats = np.reshape(lats, (Nj, Ni))
    lons = np.reshape(lons, (Nj, Ni))
    eccodes.codes_release(gid)
    f.close()

    #Crop numpy array to the region selected by user
    min_x_index = int(Ni * ((min_lon - grib_min_lon) / (grib_max_lon - grib_min_lon)))
    max_x_index = math.ceil(Ni * ((max_lon - grib_min_lon) / (grib_max_lon - grib_min_lon)))
    min_y_index = int(Nj * ((min_lat - grib_min_lat) / (grib_max_lat - grib_min_lat)))
    max_y_index = math.ceil(Nj * ((max_lat - grib_min_lat) / (grib_max_lat - grib_min_lat)))
    values = values[Nj-max_y_index:Nj-min_y_index,min_x_index:max_x_index]
    lats = lats[Nj-max_y_index:Nj-min_y_index,min_x_index:max_x_index]
    lons = lons[Nj-max_y_index:Nj-min_y_index,min_x_index:max_x_index]

    #Filter missing values
    values[values>9998] = 0

    #Apply data_type operation
    values = eval("values"+modele_info["data_types"][data_type]["operation"])

    #Filter transparent values
    values = np.ma.masked_array(values, eval("values"+modele_info["data_types"][data_type]["filter"]))

    #Create figure
    extent = [min_lon, max_lon, min_lat, max_lat]
    fig = plt.figure()
    ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
    ax.set_extent(extent)
    ax.set_axis_off()

    #Plot data according to plot type
    if (modele_info["data_types"][data_type]["plot_type"] == "heatmap"):
        cmap = plt.get_cmap("jet")
        plot = ax.pcolormesh(lons, lats, values, cmap=cmap, vmin=float(modele_info["data_types"][data_type]["range_min"]), vmax=float(modele_info["data_types"][data_type]["range_max"]), transform=ccrs.PlateCarree(), shading="auto", alpha=0.6)
        fig.colorbar(plot)

    return fig


def add_background_to_figure(data_figure, background):
    #Retreive axes from figure
    ax = data_figure.get_axes()[0]

    if (background == "osm"):
        request = cimgt.OSM()
        ax.add_image(request, 9)

    return data_figure


if __name__ == "__main__":
    # Opening JSON file
    f = open("settings.json")
    json_data = json.load(f)
    # Closing file
    f.close()

    #Get modele informations
    modele_info = json_data["modeles"]["arome"]

    #Find available data types
    available_data_types = []
    for data_type in modele_info["data_types"]:
        available_data_types.append(data_type)

    #Parse user inputs
    args = parse_inputs(available_data_types)
    mlat = args.mlat
    Mlat = args.Mlat
    mlon = args.mlon
    Mlon = args.Mlon
    background = args.background
    data_types = args.data_types

    for data_type in data_types:
        #Initializing directory
        current_dir = os.getcwd()
        path = current_dir+"/meteo_outputs/"+str(data_type)
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)

        current_time = datetime.now()

        for i in range(0, 24):
            data_figure = create_data_figure(mlat, Mlat, mlon, Mlon, data_type, current_time, modele_info)
            data_figure = add_background_to_figure(data_figure, background)

            #Save figure
            data_figure.savefig("meteo_outputs/"+str(data_type)+"/image_"+str(i)+".png")
            # Clear the current axes
            plt.cla() 
            # Clear the current figure
            plt.clf() 
            # Closes all the figure windows
            plt.close("all")
            #Collect garbage
            gc.collect()

            current_time = current_time + timedelta(hours=1)