# ================================ Imports =====================================
import sys
import os
import shutil
import datetime
from math import *
import pygrib
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt


# ================================ Constants =====================================


# ============================= Usefull functions =============================


# =============================== User inputs ==================================
if (len(sys.argv[1:]) != 5):
	print("Bad arguments number")
	sys.exit(1)

if (sys.argv[4] not in ("rain", "temp")):
	print("Bad data type")
	sys.exit(1)

center_lat = float(sys.argv[1])
center_lon = float(sys.argv[2])
radius = float(sys.argv[3])
data_type = sys.argv[4]
raw_data_path = sys.argv[5]

min_lat = center_lat - radius/110.574
max_lat = center_lat + radius/110.574
min_lon = center_lon - radius/(111.320*cos(center_lat*(pi/180)))
max_lon = center_lon + radius/(111.320*cos(center_lat*(pi/180)))

actual_year = int(datetime.date.today().year)
actual_month = int(datetime.date.today().month)
actual_day = int(datetime.date.today().day)
actual_hour = int(datetime.datetime.now().hour)



# ========================= Initializing directories ===========================
curent_dir = os.getcwd()

path = curent_dir+"/meteo_outputs"
if os.path.exists(path):
	shutil.rmtree(path)
os.makedirs(path)



# ============================ Processing data =================================
for time in range(0, 24):
	current_hour = actual_hour + time
	current_day = actual_day
	if current_hour >= 24:
		current_hour = current_hour - 24
		current_day = actual_day + 1


	#Process grib file
	print("Processing grib file for "+str(data_type)+" at hour H+"+"{:02d}".format(time))
	gribfile = pygrib.open(raw_data_path+"/"+str(data_type)+"/grib_file_"+str(data_type)+"_H"+"{:02d}".format(time)+".grib2")

	grib_message = gribfile.message(1)

	values, lats, lons = grib_message.data(lat1=min_lat,lat2=max_lat,lon1=min_lon,lon2=max_lon)

	gribfile.close()


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

	fig.suptitle(str(data_type)+" - "+str(current_day)+"/"+str(actual_month)+"/"+str(actual_year)+" "+str(current_hour)+"h00")

	plt.savefig("meteo_outputs/image_"+str(time)+".png")
	plt.close()