import logging
import os

log_level = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - [%(levelname)s] %(name)s - %(message)s'
)

# Create a logger for the application
log = logging.getLogger(__name__)
