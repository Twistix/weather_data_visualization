# ================================ Imports =====================================
import sys
import os
import shutil
import argparse
from datetime import datetime, timedelta
import requests
import re
import json


# ================================ Constants =====================================


# ============================= Usefull functions =============================
def time_format_iso8601(time):
    return "{:04d}".format(time.year)+"-"+"{:02d}".format(time.month)+"-"+"{:02d}".format(time.day)+"T"+"{:02d}".format(time.hour)+":00:00Z"


# =============================== Functions =======================================
def parse_inputs(available_data_types):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', "--data_types", type=str, default=available_data_types, nargs='+', choices=available_data_types, help="Metrics wanted")

    return parser.parse_args()


def calculate_arome_ref_time(data_type, modele_info):
    #Variables
    cover_name = modele_info["data_types"][data_type]["cover_name"]
    grid = modele_info["data_types"][data_type]["grid"]
    cummul_duration = modele_info["data_types"][data_type]["cummul_duration"]
    line_content_search = [cover_name, cummul_duration]
    line_matches = []
    ref_time = datetime(2000, 1, 1, 0, 0, 0)

    #Initializing temporary directory
    current_dir = os.getcwd()
    path = current_dir+"/temp"
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

    #Download WCS capabilities file
    print("Downloading WCS capabilities file")
    url = "https://public-api.meteofrance.fr/public/arome/1.0/wcs/MF-NWP-HIGHRES-AROME-"+grid+"-FRANCE-WCS/GetCapabilities?service=WCS&version=2.0.1&language=eng"
    print(url)
    r = requests.get(url, headers={"apikey": modele_info["api_key"]})
    r.raise_for_status()
    f = open("temp/WCS_capabilities", "wb")
    f.write(r.content)
    f.close()

    #First we search each line that matches cover name and cummul time in the file
    with open("temp/WCS_capabilities", "r") as fp:
        for l_no, line in enumerate(fp):
            if all(x in line for x in line_content_search):
                line_matches.append(line)

    #The corresponding lines are recorded from the oldest to the most recent, 
    #since the times of the runs are more and more recent as we go down in the file

    #We take the second to last line that matches as the ref time (sometimes the last run available is not totaly finished)
    int_in_line = [int(s) for s in re.findall(r"\d+", line_matches[-2])]
    ref_time = ref_time.replace(year=int_in_line[0], month=int_in_line[1], day=int_in_line[2], hour=int_in_line[3])

    #Remove temp files
    shutil.rmtree(path)

    print("Ref time for " + data_type + " is "+str(ref_time))
    return ref_time


def download_data_arome(data_type, modele_info, ref_time, nb_hours):
    #Variables
    cover_name = modele_info["data_types"][data_type]["cover_name"]
    grid = modele_info["data_types"][data_type]["grid"]
    cummul_duration = modele_info["data_types"][data_type]["cummul_duration"]
    start_time = modele_info["data_types"][data_type]["start_time"]
    subset_time = ref_time + timedelta(hours=int(start_time))

    #Downloading data
    for i in range(int(start_time), nb_hours):
        print("Downloading grib file for hour H+"+"{:02d}".format(i))
        url = "https://public-api.meteofrance.fr/public/arome/1.0/wcs/MF-NWP-HIGHRES-AROME-"+grid+"-FRANCE-WCS/GetCoverage?service=WCS&version=2.0.1&format=application/wmo-grib&coverageid="+cover_name+"___"+time_format_iso8601(ref_time)+cummul_duration+"&subset=time("+time_format_iso8601(subset_time)+")"
        print(url)
        r = requests.get(url, headers={"apikey": modele_info["api_key"]})
        r.raise_for_status()
        f = open("raw_data/"+data_type+"/grib_"+data_type+"_"+time_format_iso8601(subset_time)+".grib2", "wb")
        f.write(r.content)
        f.close()

        subset_time = subset_time + timedelta(hours=1)


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
    data_types = args.data_types

    for data_type in data_types:
        #Initializing directory
        current_dir = os.getcwd()
        path = current_dir+"/raw_data/"+str(data_type)
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)       

        ref_time = calculate_arome_ref_time(data_type, modele_info)
        download_data_arome(data_type, modele_info, ref_time, 36)