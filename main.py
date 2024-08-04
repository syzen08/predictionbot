import logging
import sys

import coloredlogs

logger = logging.getLogger('discord')
botlogger = logging.getLogger('bot')
dblogger = logging.getLogger('db')
logger.setLevel(logging.INFO)
botlogger.setLevel(logging.INFO)
dblogger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
formatter = coloredlogs.ColoredFormatter(fmt="%(asctime)s [%(levelname)s] - %(name)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
botlogger.addHandler(handler)
dblogger.addHandler(handler)

from bot import bot

with open("token.txt") as f:
    token = f.readlines()[0]

bot.run(token, log_handler=None)