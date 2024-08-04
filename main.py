import logging
import sys

import coloredlogs
import discord

from bot import PredictionBot

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
formatter = coloredlogs.ColoredFormatter(fmt="%(asctime)s [%(levelname)s] - %(name)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

with open("token.txt") as f:
    token = f.readlines()[0]


intents = discord.Intents.default()

client = PredictionBot(intents=intents)
client.run(token, log_handler=None)