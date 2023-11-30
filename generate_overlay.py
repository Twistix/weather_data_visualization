# ================================ Imports =====================================
import sys
import os
import argparse
import shutil
from datetime import datetime, timedelta
import math
import eccodes
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import gc
from PIL import Image


# ================================ Constants =====================================
AVAILABLE_DATA_TYPES = ["rain","temp","clouds"]
DEFAULT_DATA_TYPE = AVAILABLE_DATA_TYPES


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
    parser.add_argument('-d', "--data_types", type=str, default=DEFAULT_DATA_TYPE, nargs='+', choices=AVAILABLE_DATA_TYPES, help="Metrics wanted")

    return parser.parse_args()


# ============================ Processing data =================================
def gen_overlay(data_type):
    #Variables
    current_time = datetime.today()
    current_dir = os.getcwd()

    #Initializing directory
    path = current_dir+"/overlays/"+str(data_type)
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

    for i in range(0, 3):
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
        values = np.ma.masked_array(values, values < 0.5)

        #Nomalize values
        min_val = 0
        max_val = 20
        values = (values - min_val) / (max_val - min_val)

        #Create image
        cmap = mpl.cm.get_cmap("jet")
        im = Image.fromarray(np.uint8(cmap(values)*255))
        im.save("overlays/"+str(data_type)+"/image_"+str(i)+".png")
        #rgb_img = cmap.colors[values, :]
        #print(rgb_img)
        # values = np.ma.masked_array(values, values < 0.5)
        # img = Image.fromarray(values, 'L')
        # img.show()
        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        # values = np.ma.masked_array(values, values < 0.5)
        # cmap = plt.get_cmap("jet")
        # plot = ax.pcolormesh(lons, lats, values, cmap=cmap, shading="auto", alpha=0.6)
        # ax.set_axis_off()

        # fig.savefig("overlays/"+str(data_type)+"/image_"+str(i)+".png")

        # # Clear the current axes
        # plt.cla() 
        # # Clear the current figure
        # plt.clf() 
        # # Closes all the figure windows
        # plt.close("all")
        # #Collect garbage
        # gc.collect()

        current_time = current_time + timedelta(hours=1)


if __name__ == "__main__":
    args = parse_inputs()

    data_types = args.data_types

    for data_type in data_types :
        gen_overlay(data_type)