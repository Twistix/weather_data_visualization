# main.py
from downloader_factory import get_downloader
from utils.settings_manager import SettingsManager

def main():
    settings_manager = SettingsManager('settings/model_settings.json', 'settings/user_settings.json')
    
    # For now, assume the user selects the model and data type
    model_name = 'AROME'  # This can come from user input or configuration
    data_type = 'rain'    # User selects the type of data they need

    model_settings = settings_manager.get_model_settings(model_name)
    user_settings = settings_manager.get_user_settings()

    downloader = get_downloader(model_name, model_settings, user_settings)
    grib_file = downloader.download(data_type)
    
    print(f"GRIB file downloaded: {grib_file}")

if __name__ == "__main__":
    main()
