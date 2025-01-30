import json
import os


class ConfigManager:
    def __init__(self, config_file=None):
        self._config_file = config_file

        self.mtp_device = None
        self.remote_destination = ""
        self.ignored_dirs = []
        self.file_types = []
        self.set_time = True
        self.include_dot = False
        self.move_files = True

        if self._config_file:
            self.load_config(config_file)

    def load_config(self, config_file=None):
        if config_file:
            self._config_file = config_file

        if not self._config_file:
            raise ValueError("No config file specified.")

        if not os.path.exists(self._config_file):
            return

        with open(self._config_file, "r") as f:
            config = json.load(f)

            # Set attributes dynamically
            for key, value in config.items():
                if hasattr(self, key):
                    setattr(self, key, value)

    def save_config(self, config_file=None):
        if config_file:
            self._config_file = config_file

        if not self._config_file:
            raise ValueError("No config file specified.")

        # Get attributes dynamically 
        config = {
            key: value for key, value in vars(self).items() if not key.startswith('_')
        }

        with open(self._config_file, "w") as f:
            json.dump(config, f)
