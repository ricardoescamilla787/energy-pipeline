import logging

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    # Consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Archivo
    file_handler = logging.FileHandler("pipeline.log")
    file_handler.setFormatter(formatter)

    # Evitar duplicados
    logger.handlers = []

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)