import logging

formatter = logging.Formatter('[%(name)s][%(levelname)s][%(asctime)s] >>> %(message)s')
logger = logging.getLogger('watchers')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
