# downloaders/base_downloader.py
import abc
import os

class GribDownloader(abc.ABC):
    def __init__(self, model_settings, user_settings):
        self.model_settings = model_settings
        self.user_settings = user_settings
        self.output_dir = user_settings.get('output_dir', 'grib_files/')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    @abc.abstractmethod
    def download(self, data_type, area=None):
        """Download grib data for the given data type and area. Implement in subclasses."""
        pass

    def get_latest_run(self):
        """Retrieve the latest run information (this may vary by model)."""
        raise NotImplementedError("This should be implemented in the model-specific downloader")

    def save_grib_file(self, response, file_name):
        """Helper method to save the downloaded GRIB file."""
        file_path = os.path.join(self.output_dir, file_name)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return file_path
