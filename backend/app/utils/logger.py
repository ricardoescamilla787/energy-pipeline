import logging
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent.parent.parent / "pipeline.log"


def setup_logger():
    """Configura el logger para escribir en consola y en archivo."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    console_handler = logging.FileHandler(LOG_PATH)
    console_handler.setFormatter(formatter)

    file_handler = logging.StreamHandler()
    file_handler.setFormatter(formatter)

    logger.handlers = []
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
