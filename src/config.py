from pathlib import Path
import yaml

def load_config():
    config_path = Path("config/config.yaml")
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config