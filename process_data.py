# ================================ Imports =====================================
import sys
import os
import shutil
import datetime
from math import *
import eccodes
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
min_lon = center_lon - radius/(111.320*cos(center_lat))
max_lon = center_lon + radius/(111.320*cos(center_lat))

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
	f = open(raw_data_path+"/"+str(data_type)+"/grib_file_"+str(data_type)+"_H"+"{:02d}".format(time)+".grib2", "rb")
	gid = eccodes.codes_grib_new_from_file(f)
	Ni = eccodes.codes_get(gid, "Ni")	#Number of points allong a parallel or x axis
	Nj = eccodes.codes_get(gid, "Nj")	#Number of points allong a meridian or y axis
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
	max_x_index = ceil(Ni * ((max_lon - grib_min_lon) / (grib_max_lon - grib_min_lon)))
	min_y_index = int(Nj * ((min_lat - grib_min_lat) / (grib_max_lat - grib_min_lat)))
	max_y_index = ceil(Nj * ((max_lat - grib_min_lat) / (grib_max_lat - grib_min_lat)))
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

	fig.suptitle(str(data_type)+" - "+str(current_day)+"/"+str(actual_month)+"/"+str(actual_year)+" "+str(current_hour)+"h00")

	plt.savefig("meteo_outputs/image_"+str(time)+".png")
	plt.close()