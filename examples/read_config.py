import json
import os
from pathlib import Path


def load_config(path: str) -> dict:
    """Load a JSON config file, letting environment variables override values."""
    config = json.loads(Path(path).read_text())
    for key in list(config):
        override = os.environ.get(f"APP_{key.upper()}")
        if override is not None:
            config[key] = override
    return config
