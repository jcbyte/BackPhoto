import json
import os
from typing import Optional


class ConfigManager:
    """Manages configuration settings by loading and saving from a JSON file."""

    def __init__(self, config_file: Optional[str] = None) -> None:
        """Initializes the ConfigManager with default values and optionally loads a configuration file.

        Args:
            config_file (Optional[str], optional): Optional path to a JSON configuration file. Defaults to None.
        """
        # Record the config file path for saving/loading later
        self._config_file = config_file

        # Set default values for properties which will be used if no configuration file or the setting does not exist in the config file
        self.adb_device: str | None = None
        self.destination: str = ""
        self.ignored_dirs: list[str] = ["Internal storage\\Android", "Internal storage\\storage"]
        self.file_types: list[str] = [".jpg", ".jpeg", ".webp", ".png", ".mp4"]
        self.set_time: bool = True
        self.include_dot: bool = False
        self.move_files: bool = True
        self.delete_temporary_files: bool = True

        # If a configuration file is specified then load it initially
        if self._config_file:
            self.load_config(config_file)

    def load_config(self, config_file: Optional[str] = None) -> None:
        """Loads configuration from a JSON file and updates class attributes.

        Args:
            config_file (Optional[str], optional): Optional path to a JSON configuration file. If not provided, the existing file path is used. Defaults to None.

        Raises:
            ValueError: If no configuration file is specified.
        """
        if config_file:
            self._config_file = config_file

        if not self._config_file:
            raise ValueError("No config file specified.")

        if not os.path.exists(self._config_file):
            return

        # Read the config file
        with open(self._config_file, "r") as f:
            config = json.load(f)

            # Set attributes dynamically
            for key, value in config.items():
                if hasattr(self, key):
                    setattr(self, key, value)

    def save_config(self, config_file: Optional[str] = None) -> None:
        """Saves the current configuration to a JSON file.

        Args:
            config_file (Optional[str], optional): Optional path to a JSON configuration file. If not provided, the existing file path is used. Defaults to None.

        Raises:
            ValueError: If no configuration file is specified.
        """
        if config_file:
            self._config_file = config_file

        if not self._config_file:
            raise ValueError("No config file specified.")

        # Get attributes dynamically
        config = {key: value for key, value in vars(self).items() if not key.startswith("_")}

        # Save these back into the config file
        with open(self._config_file, "w") as f:
            json.dump(config, f)
