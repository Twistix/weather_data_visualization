from datetime import datetime
from models.arome001 import AROME001Model

# Create AROME001 model
model = AROME001Model("settings/user_settings.json")

# Use downloader
print(f"Available data types : "+str(model.get_data_types()))

latest_run_time = model.get_last_run("rain")
print(f"Last run time : " + datetime.strftime(latest_run_time, "%Y-%m-%dT%H.%M.%SZ"))

model.download_run("rain", latest_run_time, "grib_files")