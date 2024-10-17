# downloaders/arome_downloader.py
import requests
from datetime import datetime
from .base_downloader import GribDownloader

class AromeDownloader(GribDownloader):
    def download(self, data_type, area=None):
        api_key = self.user_settings['api_keys'].get('AROME')
        base_url = self.model_settings.get('base_url')
        parameter = self.model_settings['parameters'].get(data_type)
        
        # Use current date and time to get the latest run
        latest_run = self.get_latest_run()

        # Define the download URL (this might be model-specific)
        url = f"{base_url}/{latest_run}/grib?param={parameter}&area={area or self.model_settings['default_area']}&apikey={api_key}"
        
        # Download the file
        response = requests.get(url)
        if response.status_code == 200:
            file_name = f"arome_{data_type}_{latest_run}.grib"
            return self.save_grib_file(response, file_name)
        else:
            raise Exception(f"Failed to download AROME data: {response.status_code}")

    def get_latest_run(self):
        # Logic to determine the latest available run for AROME, for example:
        now = datetime.utcnow()
        run_hour = now.strftime("%H")
        latest_run = f"{now.strftime('%Y%m%d')}/{run_hour}00"  # Format might vary
        return latest_run
