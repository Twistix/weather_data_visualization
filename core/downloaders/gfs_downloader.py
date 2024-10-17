# downloaders/gfs_downloader.py
import requests
from .base_downloader import GribDownloader

class GFSDownloader(GribDownloader):
    def download(self, data_type, area=None):
        base_url = self.model_settings.get('base_url')
        parameter = self.model_settings['parameters'].get(data_type)
        
        # Use current date and time to get the latest run
        latest_run = self.get_latest_run()

        # Define the download URL (GFS-specific)
        url = f"{base_url}/gfs.{latest_run}/{parameter}.grib2"

        response = requests.get(url)
        if response.status_code == 200:
            file_name = f"gfs_{data_type}_{latest_run}.grib2"
            return self.save_grib_file(response, file_name)
        else:
            raise Exception(f"Failed to download GFS data: {response.status_code}")

    def get_latest_run(self):
        # Logic to determine the latest available run for GFS
        from datetime import datetime
        now = datetime.utcnow()
        latest_run = now.strftime("%Y%m%d%H")  # GFS-specific format for latest run
        return latest_run
