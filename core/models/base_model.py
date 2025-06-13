from abc import ABC, abstractmethod

class BaseModel(ABC):
    @abstractmethod
    def get_data_types(self):
        """Return data types of the model available for download"""
        pass

    @abstractmethod
    def get_last_run(self, data_type):
        """Return the timestamp of the latest available run for a specific data type"""
        pass

    @abstractmethod
    def download_run(self, data_type, run_time, output_dir):
        """Download entire run of the specified data type in a folder"""
        pass