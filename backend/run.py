import sys
import logging
from app.utils.logger    import setup_logger
from app.services.pipeline import run_pipeline

if __name__ == "__main__":
    setup_logger()

    try:
        result = run_pipeline()
        logging.info(f"Resultado: {result}")
    except Exception as e:
        logging.critical(f"Pipeline falló: {e}")
        sys.exit(1)
