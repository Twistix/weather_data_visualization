# downloader_factory.py
from downloaders.arome_downloader import AromeDownloader
from downloaders.gfs_downloader import GFSDownloader

def get_downloader(model_name, model_settings, user_settings):
    if model_name == 'AROME':
        return AromeDownloader(model_settings, user_settings)
    elif model_name == 'GFS':
        return GFSDownloader(model_settings, user_settings)
    # Add more models here
    else:
        raise ValueError(f"Model '{model_name}' is not supported")
