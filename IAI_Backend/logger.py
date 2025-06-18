# logger.py

import logging

# Create a custom logger
logger = logging.getLogger("my_app_logger")
logger.setLevel(logging.DEBUG)

# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
ch.setFormatter(formatter)

# Avoid adding multiple handlers if reloaded
if not logger.handlers:
    logger.addHandler(ch)
