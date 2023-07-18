import logging
import sys

def get_system_log():
    logger = logging.getLogger('system_log')
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
