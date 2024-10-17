# utils/settings_manager.py
import json

class SettingsManager:
    def __init__(self, model_settings_file, user_settings_file):
        self.model_settings = self._load_json(model_settings_file)
        self.user_settings = self._load_json(user_settings_file)
    
    def _load_json(self, file_path):
        with open(file_path, 'r') as f:
            return json.load(f)

    def get_model_settings(self, model_name):
        return self.model_settings.get(model_name, {})

    def get_user_settings(self):
        return self.user_settings
