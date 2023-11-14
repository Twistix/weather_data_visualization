# ================================ Imports =====================================
import sys
import os
import shutil
import argparse
from datetime import datetime, timedelta
import requests


# ================================ Constants =====================================
API_KEY = "eyJ4NXQiOiJZV0kxTTJZNE1qWTNOemsyTkRZeU5XTTRPV014TXpjek1UVmhNbU14T1RSa09ETXlOVEE0Tnc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJqdWxpZW4uYXJtZW5nYXVkQGNhcmJvbi5zdXBlciIsImFwcGxpY2F0aW9uIjp7Im93bmVyIjoianVsaWVuLmFybWVuZ2F1ZCIsInRpZXJRdW90YVR5cGUiOm51bGwsInRpZXIiOiJVbmxpbWl0ZWQiLCJuYW1lIjoiRGVmYXVsdEFwcGxpY2F0aW9uIiwiaWQiOjIwODksInV1aWQiOiI2ODVmYTFjYS1hOWU0LTRhMzQtODgyYS00ZWFlYWU3MjdjZGMifSwiaXNzIjoiaHR0cHM6XC9cL3BvcnRhaWwtYXBpLm1ldGVvZnJhbmNlLmZyOjQ0M1wvb2F1dGgyXC90b2tlbiIsInRpZXJJbmZvIjp7IjUwUGVyTWluIjp7InRpZXJRdW90YVR5cGUiOiJyZXF1ZXN0Q291bnQiLCJncmFwaFFMTWF4Q29tcGxleGl0eSI6MCwiZ3JhcGhRTE1heERlcHRoIjowLCJzdG9wT25RdW90YVJlYWNoIjp0cnVlLCJzcGlrZUFycmVzdExpbWl0IjowLCJzcGlrZUFycmVzdFVuaXQiOiJzZWMifX0sImtleXR5cGUiOiJQUk9EVUNUSU9OIiwicGVybWl0dGVkUmVmZXJlciI6IiIsInN1YnNjcmliZWRBUElzIjpbeyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IkFST01FIiwiY29udGV4dCI6IlwvcHVibGljXC9hcm9tZVwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW5fbWYiLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn1dLCJleHAiOjE3ODEwNTY3NTIsInBlcm1pdHRlZElQIjoiIiwiaWF0IjoxNjg2NDQ4NzUyLCJqdGkiOiJhZjc0NmIxOC1jZTc4LTQ5OWUtOGJlZi0yNmU2ODJmOTk3MTcifQ==.nwSFYUs5gXpGTA05gFeICY4QgCyNJI_x2AtEfgYnTNljDtYQCzjQhyOzm1jaQzVlRbbsZBySBFEO_LXiwQVGh0AUNbF6lphsgLISOpOpcAWRjCAXqf96bNbWpnFW1wrvSqIRlTkMfZ8Esex1gbfEMLwOsuT0328Xti_i1jp8n_OTOZExPrNdAkeq5lYrvRGMECXl_GyCNBVQQwnJQLPnv-3sH0nDaDb9JaFruyKZmQsyHR4XtBIcgxV4HEGmq6nY3pBV7ifKKSm5PR-YysfjZGNoKz5Uwy7Rvj_Fag-NU7wt0vhYgvOKUur8KeGP-p4dsB31A_r2Pinz4-fXiF93zQ=="
AVAILABLE_DATA_TYPES = ["rain","temp","clouds"]
DEFAULT_DATA_TYPE = AVAILABLE_DATA_TYPES


# ============================= Usefull functions =============================
def gen_time(year, month, day, hour):
	return "{:04d}".format(year)+"-"+"{:02d}".format(month)+"-"+"{:02d}".format(day)+"T"+"{:02d}".format(hour)+":00:00Z"

def get_data_parameters_by_type(data_type):
	# return cover_name,cummul_duration,grid
	if data_type == "rain":
		return "TOTAL_PRECIPITATION__GROUND_OR_WATER_SURFACE","_PT1H","001"
	elif data_type == "temp":
		return "TEMPERATURE__GROUND_OR_WATER_SURFACE","","0025"
	elif data_type == "clouds":
		return "TOTAL_CLOUD_COVER__GROUND_OR_WATER_SURFACE","","0025"

def calculate_ref_time(current_time):
	if int(current_time.hour) < 3:
		ref_time = current_time + timedelta(hours=-int(current_time.hour)-9)
	elif int(current_time.hour) < 6:
		ref_time = current_time + timedelta(hours=-int(current_time.hour)-6)
	elif int(current_time.hour) < 9:
		ref_time = current_time + timedelta(hours=-int(current_time.hour)-3)
	elif int(current_time.hour) < 12:
		ref_time = current_time + timedelta(hours=-int(current_time.hour))
	elif int(current_time.hour) < 15:
		ref_time = current_time + timedelta(hours=-int(current_time.hour)+3)
	elif int(current_time.hour) < 18:
		ref_time = current_time + timedelta(hours=-int(current_time.hour)+6)
	elif int(current_time.hour) < 21:
		ref_time = current_time + timedelta(hours=-int(current_time.hour)+9)
	else:
		ref_time = current_time + timedelta(hours=-int(current_time.hour)+12)
	return ref_time


# =============================== User inputs ==================================
def parse_inputs():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', "--data_types", type=str, default=DEFAULT_DATA_TYPE, nargs='+', choices=AVAILABLE_DATA_TYPES, help="Metrics wanted")

    return parser.parse_args()


# =============================== Globals =========================================
current_dir = os.getcwd()


# ============================ Download grib files =================================
def download(data_type, ref_time):
	#Variables
	current_time = ref_time

	#Initializing directory
	path = current_dir+"/raw_data/"+str(data_type)
	if os.path.exists(path):
		shutil.rmtree(path)
	os.makedirs(path)

	#Downloading data
	for i in range(0, 36):
		print("Downloading grib file for hour H+"+"{:02d}".format(i))
		cover_name,cummul_duration,grid = get_data_parameters_by_type(data_type)
		url = "https://public-api.meteofrance.fr/public/arome/1.0/wcs/MF-NWP-HIGHRES-AROME-"+grid+"-FRANCE-WCS/GetCoverage?SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage&format=application/wmo-grib&coverageId="+cover_name+"___"+gen_time(ref_time.year, ref_time.month, ref_time.day, ref_time.hour)+cummul_duration+"&subset=time("+gen_time(current_time.year, current_time.month, current_time.day, current_time.hour)+")"
		print(url)
		r = requests.get(url, headers={"apikey": API_KEY})
		f = open("raw_data/"+str(data_type)+"/grib_"+str(data_type)+"_"+gen_time(current_time.year, current_time.month, current_time.day, current_time.hour)+".grib2", "wb")
		f.write(r.content)
		f.close()

		current_time = current_time + timedelta(hours=1)


if __name__ == "__main__":
    args = parse_inputs()

    data_types = args.data_types

    current_time = datetime.today()
    ref_time = calculate_ref_time(current_time)

    for data_type in data_types :
        download(data_type, ref_time)