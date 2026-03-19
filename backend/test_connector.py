import logging
from app.services.pipeline import run_pipeline
from app.utils.logger import setup_logger
from app.utils.http_client import get_with_retry
from app.services.validator import validate_data

print("Validator import OK")

print("Import OK")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    setup_logger()
    run_pipeline()