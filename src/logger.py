import logging
from pathlib import Path

LOG_DIR = Path("logs")

LOG_DIR.mkdir(
    exist_ok=True
)

LOG_FILE = LOG_DIR / "geoaudit.log"

logging.basicConfig(

    filename=LOG_FILE,

    level=logging.INFO,

    format=
    "%(asctime)s | %(levelname)s | %(message)s",

    datefmt="%Y-%m-%d %H:%M:%S"

)

def get_logger():

    return logging.getLogger("GeoAudit")