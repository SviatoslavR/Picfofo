import json
import os
from pathlib import Path
import keyring

class ConfigManager:
    APP_NAME = "picfofo"
    KEYRING_SERVICE = "picfofo_r2_credentials"

    def __init__(self, config_path: str = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Cross-platform config directory
            import sys
            if sys.platform == "win32":
                base_dir = Path(os.getenv('APPDATA', Path.home() / "AppData/Roaming")) / self.APP_NAME
            elif sys.platform == "darwin":
                base_dir = Path.home() / "Library/Application Support" / self.APP_NAME
            else:  # Linux and others
                base_dir = Path.home() / ".config" / self.APP_NAME
            
            base_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = base_dir / "config.json"

        self.config = {
            "language": "zh",
            "endpoint_url": "",
            "access_key": "",
            "bucket_name": "",
            "custom_domain": "",
            "upload_path": "picfofo/",
            "markdown_template": "![image]({url})"
        }
        self._secret_key = ""
        self.load()

    def load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Don't overwrite the entire dict to preserve defaults for new keys
                    for k, v in data.items():
                        if k != "secret_key": # Ensure we don't load secret_key from json if it accidentally exists
                            self.config[k] = v
                
                # Load secret key from system keyring
                if self.config.get("access_key"):
                    saved_pw = keyring.get_password(self.KEYRING_SERVICE, self.config["access_key"])
                    if saved_pw:
                        self._secret_key = saved_pw
            except Exception as e:
                print(f"Error loading config: {e}")

    def save(self):
        try:
            # Save non-sensitive data to JSON
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            # Save sensitive secret_key to system keyring
            if self.config.get("access_key") and self._secret_key:
                keyring.set_password(self.KEYRING_SERVICE, self.config["access_key"], self._secret_key)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key, default=None):
        if key == "secret_key":
            return self._secret_key
        return self.config.get(key, default)

    def set(self, key, value):
        if key == "secret_key":
            self._secret_key = value
        else:
            self.config[key] = value
        self.save()

    def is_valid(self):
        required = ["endpoint_url", "access_key", "bucket_name"]
        has_config = all(self.config.get(k) for k in required)
        return has_config and bool(self._secret_key)
