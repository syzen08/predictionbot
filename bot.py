import discord
import logging

class PredictionBot(discord.Client):
    async def on_ready(self):
        logging.info(f"logged on as {self.user}!")