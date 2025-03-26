from logging import getLogger, StreamHandler, Formatter, DEBUG

def get_logger(name):
    logger = getLogger(name)
    logger.setLevel(DEBUG)
    handler = StreamHandler() # prints to the console
    handler.setLevel(DEBUG)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


common_logger = get_logger('common')