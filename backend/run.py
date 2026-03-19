import logging
from app.services.pipeline import run_pipeline
from app.utils.logger import setup_logger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    setup_logger()
    run_pipeline()