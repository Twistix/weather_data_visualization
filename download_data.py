# ================================ Imports =====================================
import sys
import os
import shutil
import argparse
from datetime import datetime, timedelta
import requests
import re


# ================================ Constants =====================================
API_KEY = "eyJ4NXQiOiJZV0kxTTJZNE1qWTNOemsyTkRZeU5XTTRPV014TXpjek1UVmhNbU14T1RSa09ETXlOVEE0Tnc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJqdWxpZW4uYXJtZW5nYXVkQGNhcmJvbi5zdXBlciIsImFwcGxpY2F0aW9uIjp7Im93bmVyIjoianVsaWVuLmFybWVuZ2F1ZCIsInRpZXJRdW90YVR5cGUiOm51bGwsInRpZXIiOiJVbmxpbWl0ZWQiLCJuYW1lIjoiRGVmYXVsdEFwcGxpY2F0aW9uIiwiaWQiOjIwODksInV1aWQiOiI2ODVmYTFjYS1hOWU0LTRhMzQtODgyYS00ZWFlYWU3MjdjZGMifSwiaXNzIjoiaHR0cHM6XC9cL3BvcnRhaWwtYXBpLm1ldGVvZnJhbmNlLmZyOjQ0M1wvb2F1dGgyXC90b2tlbiIsInRpZXJJbmZvIjp7IjUwUGVyTWluIjp7InRpZXJRdW90YVR5cGUiOiJyZXF1ZXN0Q291bnQiLCJncmFwaFFMTWF4Q29tcGxleGl0eSI6MCwiZ3JhcGhRTE1heERlcHRoIjowLCJzdG9wT25RdW90YVJlYWNoIjp0cnVlLCJzcGlrZUFycmVzdExpbWl0IjowLCJzcGlrZUFycmVzdFVuaXQiOiJzZWMifX0sImtleXR5cGUiOiJQUk9EVUNUSU9OIiwicGVybWl0dGVkUmVmZXJlciI6IiIsInN1YnNjcmliZWRBUElzIjpbeyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IkFST01FIiwiY29udGV4dCI6IlwvcHVibGljXC9hcm9tZVwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW5fbWYiLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn1dLCJleHAiOjE3ODEwNTY3NTIsInBlcm1pdHRlZElQIjoiIiwiaWF0IjoxNjg2NDQ4NzUyLCJqdGkiOiJhZjc0NmIxOC1jZTc4LTQ5OWUtOGJlZi0yNmU2ODJmOTk3MTcifQ==.nwSFYUs5gXpGTA05gFeICY4QgCyNJI_x2AtEfgYnTNljDtYQCzjQhyOzm1jaQzVlRbbsZBySBFEO_LXiwQVGh0AUNbF6lphsgLISOpOpcAWRjCAXqf96bNbWpnFW1wrvSqIRlTkMfZ8Esex1gbfEMLwOsuT0328Xti_i1jp8n_OTOZExPrNdAkeq5lYrvRGMECXl_GyCNBVQQwnJQLPnv-3sH0nDaDb9JaFruyKZmQsyHR4XtBIcgxV4HEGmq6nY3pBV7ifKKSm5PR-YysfjZGNoKz5Uwy7Rvj_Fag-NU7wt0vhYgvOKUur8KeGP-p4dsB31A_r2Pinz4-fXiF93zQ=="
AVAILABLE_DATA_TYPES = ["rain","temp","clouds"]
DEFAULT_DATA_TYPE = AVAILABLE_DATA_TYPES


# ============================= Usefull functions =============================
def string_time_from_time(time):
    return "{:04d}".format(time.year)+"-"+"{:02d}".format(time.month)+"-"+"{:02d}".format(time.day)+"T"+"{:02d}".format(time.hour)+":00:00Z"


def get_data_parameters_by_type(data_type):
    # return cover_name,cummul_duration,grid,start_time
    if data_type == "rain":
        return "TOTAL_PRECIPITATION__GROUND_OR_WATER_SURFACE","_PT1H","001",1
    elif data_type == "temp":
        return "TEMPERATURE__GROUND_OR_WATER_SURFACE","","0025",0
    elif data_type == "clouds":
        return "TOTAL_CLOUD_COVER__GROUND_OR_WATER_SURFACE","","0025",1


# =============================== User inputs ==================================
def parse_inputs():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', "--data_types", type=str, default=DEFAULT_DATA_TYPE, nargs='+', choices=AVAILABLE_DATA_TYPES, help="Metrics wanted")

    return parser.parse_args()


# =============================== Globals =========================================


# ============================ Find last run time =================================
def calculate_ref_time(data_type, current_time):
    #Variables
    cover_name,cummul_duration,grid,start_time = get_data_parameters_by_type(data_type)
    line_content_search = [cover_name, cummul_duration]
    ref_time = datetime(2000, 1, 1, 0, 0, 0)

    #Initializing temporary directory
    current_dir = os.getcwd()
    path = current_dir+"/temp"
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

    #Download WCS capabilities file
    print("Downloading WCS capabilities file")
    url = "https://public-api.meteofrance.fr/public/arome/1.0/wcs/MF-NWP-HIGHRES-AROME-"+grid+"-FRANCE-WCS/GetCapabilities?SERVICE=WCS&VERSION=1.3.0&REQUEST=GetCapabilities"
    print(url)
    r = requests.get(url, headers={"apikey": API_KEY})
    r.raise_for_status()
    f = open("temp/WCS_capabilities", "wb")
    f.write(r.content)
    f.close()

    #First we search cover in the 001 file
    with open("temp/WCS_capabilities", "r") as fp:
        for l_no, line in enumerate(fp):
            #We enumerate through all lines, each time we find the cover we update ref_time, and we continue searching
            #since the run times are more recent when descending in the file
            if all(x in line for x in line_content_search):
                int_in_line = [int(s) for s in re.findall(r"\d+", line)]
                ref_time = ref_time.replace(year=int_in_line[0], month=int_in_line[1], day=int_in_line[2], hour=int_in_line[3])

    #Remove temp files
    shutil.rmtree(path)

    print("Ref time for "+data_type+" is "+str(ref_time))

    return ref_time


# ============================ Download grib files =================================
def download(data_type, ref_time, nb_hours):
    #Variables
    cover_name,cummul_duration,grid,start_time = get_data_parameters_by_type(data_type)
    current_time = ref_time + timedelta(hours=start_time)

    #Initializing directory
    current_dir = os.getcwd()
    path = current_dir+"/raw_data/"+str(data_type)
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

    #Downloading data
    for i in range(start_time, nb_hours):
        print("Downloading grib file for hour H+"+"{:02d}".format(i))
        url = "https://public-api.meteofrance.fr/public/arome/1.0/wcs/MF-NWP-HIGHRES-AROME-"+grid+"-FRANCE-WCS/GetCoverage?SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage&format=application/wmo-grib&coverageId="+cover_name+"___"+string_time_from_time(ref_time)+cummul_duration+"&subset=time("+string_time_from_time(current_time)+")"
        print(url)
        r = requests.get(url, headers={"apikey": API_KEY})
        r.raise_for_status()
        f = open("raw_data/"+str(data_type)+"/grib_"+str(data_type)+"_"+string_time_from_time(current_time)+".grib2", "wb")
        f.write(r.content)
        f.close()

        current_time = current_time + timedelta(hours=1)


if __name__ == "__main__":
    args = parse_inputs()

    data_types = args.data_types

    current_time = datetime.now()

    for data_type in data_types :
        ref_time = calculate_ref_time(data_type, current_time)
        download(data_type, ref_time, 36)