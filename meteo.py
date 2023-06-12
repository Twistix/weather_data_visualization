# ================================ Imports =====================================
import sys
import os
import shutil
import datetime
from math import *
import requests
import pygrib
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt



# ================================ Constants =====================================
API_KEY = "eyJ4NXQiOiJZV0kxTTJZNE1qWTNOemsyTkRZeU5XTTRPV014TXpjek1UVmhNbU14T1RSa09ETXlOVEE0Tnc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJqdWxpZW4uYXJtZW5nYXVkQGNhcmJvbi5zdXBlciIsImFwcGxpY2F0aW9uIjp7Im93bmVyIjoianVsaWVuLmFybWVuZ2F1ZCIsInRpZXJRdW90YVR5cGUiOm51bGwsInRpZXIiOiJVbmxpbWl0ZWQiLCJuYW1lIjoiRGVmYXVsdEFwcGxpY2F0aW9uIiwiaWQiOjIwODksInV1aWQiOiI2ODVmYTFjYS1hOWU0LTRhMzQtODgyYS00ZWFlYWU3MjdjZGMifSwiaXNzIjoiaHR0cHM6XC9cL3BvcnRhaWwtYXBpLm1ldGVvZnJhbmNlLmZyOjQ0M1wvb2F1dGgyXC90b2tlbiIsInRpZXJJbmZvIjp7IjUwUGVyTWluIjp7InRpZXJRdW90YVR5cGUiOiJyZXF1ZXN0Q291bnQiLCJncmFwaFFMTWF4Q29tcGxleGl0eSI6MCwiZ3JhcGhRTE1heERlcHRoIjowLCJzdG9wT25RdW90YVJlYWNoIjp0cnVlLCJzcGlrZUFycmVzdExpbWl0IjowLCJzcGlrZUFycmVzdFVuaXQiOiJzZWMifX0sImtleXR5cGUiOiJQUk9EVUNUSU9OIiwicGVybWl0dGVkUmVmZXJlciI6IiIsInN1YnNjcmliZWRBUElzIjpbeyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IkFST01FIiwiY29udGV4dCI6IlwvcHVibGljXC9hcm9tZVwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW5fbWYiLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn1dLCJleHAiOjE3ODEwNTY3NTIsInBlcm1pdHRlZElQIjoiIiwiaWF0IjoxNjg2NDQ4NzUyLCJqdGkiOiJhZjc0NmIxOC1jZTc4LTQ5OWUtOGJlZi0yNmU2ODJmOTk3MTcifQ==.nwSFYUs5gXpGTA05gFeICY4QgCyNJI_x2AtEfgYnTNljDtYQCzjQhyOzm1jaQzVlRbbsZBySBFEO_LXiwQVGh0AUNbF6lphsgLISOpOpcAWRjCAXqf96bNbWpnFW1wrvSqIRlTkMfZ8Esex1gbfEMLwOsuT0328Xti_i1jp8n_OTOZExPrNdAkeq5lYrvRGMECXl_GyCNBVQQwnJQLPnv-3sH0nDaDb9JaFruyKZmQsyHR4XtBIcgxV4HEGmq6nY3pBV7ifKKSm5PR-YysfjZGNoKz5Uwy7Rvj_Fag-NU7wt0vhYgvOKUur8KeGP-p4dsB31A_r2Pinz4-fXiF93zQ=="



# ============================= Usefull functions =============================
def gen_time(year, month, day, hour):
	return "{:04d}".format(year)+"-"+"{:02d}".format(month)+"-"+"{:02d}".format(day)+"T"+"{:02d}".format(hour)+":00:00Z"



# =============================== User inputs ==================================
if (len(sys.argv[1:]) != 4):
	print("Bad arguments number")
	sys.exit(1)

if (sys.argv[4] != ("rain")):
	print("Bad data type")
	sys.exit(1)

center_lat = float(sys.argv[1])
center_lon = float(sys.argv[2])
radius = float(sys.argv[3])
data_type = sys.argv[4]

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

path = curent_dir+"/temp"
if os.path.exists(path):
	shutil.rmtree(path)
os.makedirs(path)

path = curent_dir+"/meteo_output"
if os.path.exists(path):
	shutil.rmtree(path)
os.makedirs(path)



# ============================ Downloading data =================================
# Download link parameters
grid = ["001", "0025"]
cover = ["TOTAL_PRECIPITATION_RATE__GROUND_OR_WATER_SURFACE"]

#Indexes for parameters
if data_type == "rain" :
	i_grid = 0
	i_cover = 0

ref_day = actual_day
if actual_hour < 3:
	ref_hour = 15
	ref_day = actual_day - 1
elif actual_hour < 6:
	ref_hour = 18
	ref_day = actual_day - 1
elif actual_hour < 9 :
	ref_hour = 21
	ref_day = actual_day - 1
elif actual_hour < 12 :
	ref_hour = 0
elif actual_hour < 15 :
	ref_hour = 3
elif actual_hour < 18 :
	ref_hour = 6
elif actual_hour < 21 :
	ref_hour = 9
elif actual_hour < 24 :
	ref_hour = 12

for time in range(0, 24):
	current_hour = actual_hour + time
	current_day = actual_day
	if current_hour >= 24:
		current_hour = current_hour - 24
		current_day = actual_day + 1

	print("Downloading grib file for hour H+"+"{:02d}".format(time))
	url = "https://public-api.meteofrance.fr/public/arome/1.0/wcs/MF-NWP-HIGHRES-AROME-"+grid[i_grid]+"-FRANCE-WCS/GetCoverage?token=test&SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage&format=application/wmo-grib&coverageId="+cover[i_cover]+"___"+gen_time(actual_year, actual_month, ref_day, ref_hour)+"&subset=time("+gen_time(actual_year, actual_month, current_day, current_hour)+")&subset=lat("+str(min_lat)+","+str(max_lat)+"7)&subset=long("+str(min_lon)+","+str(max_lon)+")"
	print(url)
	r = requests.get(url, headers={"apikey": API_KEY})
	f = open("temp/grib_file_H"+"{:02d}".format(time)+".grib2", "wb")
	f.write(r.content)
	f.close()


	#Processing grib file
	print("Processing...")
	gribfile = pygrib.open("temp/grib_file_H"+"{:02d}".format(time)+".grib2")

	grib_message = gribfile.message(1)

	lats, lons = grib_message.latlons()
	values = grib_message.values

	#Sur une "ligne" de values, les latitudes sont les memes
	data = np.zeros((len(values[0]),len(values)))
	for lat_index in range(len(values)):
		for lon_index in range(len(values[0])):
			data[lon_index,lat_index] = values[lat_index][lon_index]


	# ======== Carte ===========
	request = cimgt.OSM()
	extent = [min_lon, max_lon, min_lat, max_lat]

	fig, ax = plt.subplots(subplot_kw=dict(projection=request.crs))
	ax.set_extent(extent)
	ax.add_image(request, 10)

	data = np.ma.masked_array(data, data < 0.5)
	data = np.rot90(data, 3)
	data = np.flip(data, axis=1)

	cmap = plt.cm.get_cmap("jet")
	plot = ax.pcolormesh(lons, lats, data, cmap=cmap, transform=ccrs.PlateCarree(), shading="auto", alpha=0.6);

	fig.colorbar(plot)

	fig.suptitle("Rainfall rate - "+str(current_day)+"/"+str(actual_month)+"/"+str(actual_year)+" "+str(current_hour)+"h00")

	plt.savefig("meteo_output/image_"+str(time)+".png")
	plt.close()
