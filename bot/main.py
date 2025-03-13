import logging


logger: logging.Logger = logging.getLogger(name='IssuesJiraBot')
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(filename='log.txt', encoding='utf8')
file_handler.setFormatter(fmt=formatter)
logger.addHandler(hdlr=file_handler)
