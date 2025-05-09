import logging

logger = logging.getLogger("job_service_logger")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(console_handler)
