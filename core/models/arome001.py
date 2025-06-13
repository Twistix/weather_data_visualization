import os
import shutil
import time
import json
import requests
import re
from datetime import datetime, timedelta
from models.base_model import BaseModel


AROME001_PARAMETERS = {
    "server": "https://public-api.meteofrance.fr/public/arome/1.0",
    "get_capabilities_path": "/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS/GetCapabilities",
    "describe_coverage_path": "/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS/DescribeCoverage",
    "get_coverage_path": "/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS/GetCoverage",
    "run_times": [0, 6, 12, 18],
    "forecast_range": {"start": 1, "end": 36},
    "data_types": {
        "rain": {
            "coverage_id": "TOTAL_PRECIPITATION__GROUND_OR_WATER_SURFACE___{run_time}_PT1H"
        }
    }
}


class AROME001Model(BaseModel):
    def __init__(self, user_settings):
        with open(user_settings, "r") as file:
            data = json.load(file)
            self.api_key = data["arome_api_key"]


    def get_data_types(self):
        return list(AROME001_PARAMETERS["data_types"].keys())


    def get_last_run(self, data_type):
        latest_run_time = None

        # Check if the requested data type is present in this model
        data_type_params = AROME001_PARAMETERS["data_types"].get(data_type)
        if (data_type_params == None):
            return None

        # Get patterns to be searched in the capabilities XML file
        prefix_pattern, suffix_pattern = data_type_params["coverage_id"].split("{run_time}")
        run_time_pattern = r"(\d{4}-\d{2}-\d{2}T\d{2}\.\d{2}\.\d{2}Z)"

        # Regex
        regex = re.escape(prefix_pattern) + run_time_pattern + re.escape(suffix_pattern)

        # Construct the request URL to download model capabilities XML file
        url = AROME001_PARAMETERS["server"]+AROME001_PARAMETERS["get_capabilities_path"]
        params = {
            "service": "WCS",
            "version": "2.0.1",
            "language": "eng"
        }
        headers = {
            "apikey": self.api_key
        }

        # Make the HTTP request and retry when time out
        while True:
            try:
                response = requests.get(url, params=params, headers=headers, timeout=5)
                response.raise_for_status()
                break
            except requests.exceptions.Timeout:
                time.sleep(2)
            except requests.exceptions.RequestException:
                return None

        # Find all pattern matches in the capabilities XML file
        matches = re.findall(regex, response.text)

        for run_time_str in matches:
            run_time = datetime.strptime(run_time_str, "%Y-%m-%dT%H.%M.%SZ")
            # Check if it is an intermediate run (3Z, 9Z, 15Z and 21Z) or complete run
            if run_time.hour not in AROME001_PARAMETERS["run_times"]:
                continue
            # Check if this run time is more recent than the previous one
            if not latest_run_time or run_time > latest_run_time:
                latest_run_time = run_time

        # Return the latest run time
        return latest_run_time


    def download_run(self, data_type, run_time, output_dir):
        # Check if the requested data type is present in this model
        data_type_params = AROME001_PARAMETERS["data_types"].get(data_type)
        if (data_type_params == None):
            return None

        # Clear output directory
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)

        # Form the CoverageId field
        coverage_id = data_type_params["coverage_id"].format(run_time=datetime.strftime(run_time, "%Y-%m-%dT%H.%M.%SZ"))

        # Calculate start and end time for this coverage
        start_time = run_time + timedelta(hours=AROME001_PARAMETERS["forecast_range"]["start"])
        end_time = run_time + timedelta(hours=AROME001_PARAMETERS["forecast_range"]["end"])

        # Loop through all available subset times in the range
        current_time = start_time
        while current_time <= end_time:
            current_time_str = datetime.strftime(current_time, "%Y-%m-%dT%H:%M:%SZ")

            # Construct the request URL to download coverage for each subset time
            url = AROME001_PARAMETERS["server"]+AROME001_PARAMETERS["get_coverage_path"]
            params = {
                "service": "WCS",
                "version": "2.0.1",
                "coverageid": coverage_id,
                "subset": f"time({current_time_str})",
                "format": "application/wmo-grib"
            }
            headers = {
                "apikey": self.api_key
            }

            # Make the HTTP request and retry when time out
            while True:
                try:
                    response = requests.get(url, params=params, headers=headers, timeout=5)
                    response.raise_for_status()
                    break
                except requests.exceptions.Timeout:
                    time.sleep(2)
                except requests.exceptions.RequestException:
                    return None

            # Save the file to the output directory
            output_path = os.path.join(output_dir, f"{data_type}_{current_time_str}.grib")
            
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            print(f"File downloaded successfully: {output_path}")

            # Increment current time by 1h
            current_time += timedelta(hours=1)
        
        # Save run_info.json in the output directory
        run_info = {
            "data_type": data_type,
            "run_time": datetime.strftime(run_time, "%Y-%m-%dT%H.%M.%SZ"),
            "start_time": datetime.strftime(start_time, "%Y-%m-%dT%H.%M.%SZ"),
            "end_time": datetime.strftime(end_time, "%Y-%m-%dT%H.%M.%SZ")
        }
        run_info_path = os.path.join(output_dir, "run_info.json")

        with open(run_info_path, "w") as f:
            json.dump(run_info, f, indent=4)

        print(f"Run info saved: {run_info_path}")


