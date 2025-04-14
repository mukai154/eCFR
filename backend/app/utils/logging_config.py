import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("ecfr_app.log"),
            logging.StreamHandler()
        ]
    )
    logging.info("Logging is configured.")