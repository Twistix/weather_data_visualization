# ================================ Imports =====================================
import sys
import os
import argparse
import shutil
from datetime import datetime, timedelta
import math
import eccodes
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt


# ================================ Constants =====================================
AVAILABLE_DATA_TYPES = ["rain","temp","clouds"]

DEFAULT_RADIUS = 100
DEFAULT_DATA_TYPE = AVAILABLE_DATA_TYPES

LAT_RATIO = 110.574
LON_RATIO = 111.320


# ============================= Useful functions =============================
def deg_to_rad(angle):
    return angle*math.pi/180


def gen_time(year, month, day, hour):
    return "{:04d}".format(year)+"-"+"{:02d}".format(month)+"-"+"{:02d}".format(day)+"T"+"{:02d}".format(hour)+":00:00Z"


# =============================== User inputs ==================================
def parse_inputs():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--lat", type=float, help="Center latitude (in deg)")
    parser.add_argument("--lon", type=float, help="Center longitude (in deg)")
    parser.add_argument('-r', "--radius", type=float, default=DEFAULT_RADIUS, help="Radius (in km)")
    parser.add_argument('-d', "--data_types", type=str, default=DEFAULT_DATA_TYPE, nargs='+', choices=AVAILABLE_DATA_TYPES, help="Metrics wanted")

    return parser.parse_args()


# ============================ Processing data =================================
def process(center_lat, center_lon, radius, data_type):
    #Variables
    min_lat = center_lat - radius/LAT_RATIO
    max_lat = center_lat + radius/LAT_RATIO
    min_lon = center_lon - radius/(LON_RATIO*math.cos(deg_to_rad(center_lat)))
    max_lon = center_lon + radius/(LON_RATIO*math.cos(deg_to_rad(center_lat)))
    current_time = datetime.today()
    current_dir = os.getcwd()

    #Initializing directory
    path = current_dir+"/meteo_outputs/"+str(data_type)
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

    for i in range(0, 24):
        #Process grib file
        print("Processing grib file for "+str(data_type)+" at hour H+"+"{:02d}".format(i))
        f = open("raw_data/"+str(data_type)+"/grib_"+str(data_type)+"_"+gen_time(current_time.year, current_time.month, current_time.day, current_time.hour)+".grib2", "rb")
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

        #Filter missing values
        values[values>9998] = 0

        #Crop numpy array to the region selected by user
        min_x_index = int(Ni * ((min_lon - grib_min_lon) / (grib_max_lon - grib_min_lon)))
        max_x_index = math.ceil(Ni * ((max_lon - grib_min_lon) / (grib_max_lon - grib_min_lon)))
        min_y_index = int(Nj * ((min_lat - grib_min_lat) / (grib_max_lat - grib_min_lat)))
        max_y_index = math.ceil(Nj * ((max_lat - grib_min_lat) / (grib_max_lat - grib_min_lat)))
        values = values[Nj-max_y_index:Nj-min_y_index,min_x_index:max_x_index]
        lats = lats[Nj-max_y_index:Nj-min_y_index,min_x_index:max_x_index]
        lons = lons[Nj-max_y_index:Nj-min_y_index,min_x_index:max_x_index]

        #Construct map
        request = cimgt.OSM()
        extent = [min_lon, max_lon, min_lat, max_lat]

        fig, ax = plt.subplots(subplot_kw=dict(projection=request.crs))
        ax.set_extent(extent)
        ax.add_image(request, 10)

        values = np.ma.masked_array(values, values < 0.5)
        cmap = plt.cm.get_cmap("jet")
        plot = ax.pcolormesh(lons, lats, values, cmap=cmap, transform=ccrs.PlateCarree(), shading="auto", alpha=0.6);

        fig.colorbar(plot)

        fig.suptitle(str(data_type)+" - "+gen_time(current_time.year, current_time.month, current_time.day, current_time.hour))

        plt.savefig("meteo_outputs/"+str(data_type)+"/image_"+str(i)+".png")
        plt.close()

        current_time = current_time + timedelta(hours=1)


if __name__ == "__main__":
    args = parse_inputs()

    center_lat = args.lat
    center_lon = args.lon
    radius = args.radius
    data_types = args.data_types

    for data_type in data_types :
        process(center_lat, center_lon, radius, data_type)