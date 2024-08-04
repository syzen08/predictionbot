import logging

import discord
from discord.ext import commands
from discord.utils import MISSING

from prediction import Prediction
from userdb import UserDB

logger = logging.getLogger('bot')

userdb = UserDB('users.json')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

current_predictions = []

bot = commands.Bot(command_prefix='$', intents=intents)

class PredictionSubmitModal(discord.ui.Modal, title='Vorhersage'):
    amount = discord.ui.TextInput(label='Wie viel willst du wetten?', placeholder='100', required=True, style=discord.TextStyle.short, max_length=6)

    def __init__(self, currentpredictionsidx: int, option: int, *, title: str = ..., timeout: float | None = None, custom_id: str = ...) -> None:
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        self.currpredidx = currentpredictionsidx
        self.option = option

    async def on_submit(self, interaction: discord.Interaction):
        current_predictions[self.currpredidx].addVote(interaction.user, int(self.amount.value))
        await interaction.response.send_message(f'du hast mit {self.amount.value} Euro fuer {current_predictions[self.currpredidx].getOptionName(self.option)}', ephemeral=True)

class PredictionView(discord.ui.View):
    def __init__(self, predictionidx: int):
        super().__init__()
        self.value = None
        self.predidx = predictionidx

    @discord.ui.button(label='Option 1', style=discord.ButtonStyle.green)
    async def option1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PredictionSubmitModal(self.predidx, 1))

    @discord.ui.button(label='Option 2', style=discord.ButtonStyle.red)
    async def option2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PredictionSubmitModal(self.predidx, 2))
        

@bot.event
async def on_ready():
    logger.info(f'logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        logger.info(f'synced {len(synced)} command(s)')
    except Exception as e:
        logger.error(f'sync failed: {e}')

    try:
        await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name="ich sehe alles"))
        logger.info("set custom presence")
    except Exception as e:
        logger.error(e)

@bot.event
async def on_guild_join(guild):
    logger.info(f'joined new guild {guild.id} ({guild.name})')
    initGuild(guild)

@bot.hybrid_command(name='echo', description='der bot sagt was du willst')
async def echo(interaction: discord.Interaction, message):
    await interaction.reply(message)

@bot.hybrid_command(name='kontostand', description='zeigt den kontostand von jemanden an')
async def getPoints(interaction: discord.Interaction, member: discord.Member):
    points = userdb.getMemberPoints(interaction.guild, member)
    await interaction.reply(f'{member.display_name} hat {points} Euro')

@bot.hybrid_command(name='vorhersage', description='starte eine neue vorhersage')
async def startPrediction(interaction: discord.Interaction, title: str, option1: str, option2: str):
    current_predictions.append(Prediction(title, option1, option2))
    interaction.response.send_message(embed=discord.Embed(), view=PredictionView(current_predictions.index(Prediction(title, option1, option2))))


@bot.command()
async def setPoints(ctx, member: discord.Member, points: int):
    if ctx.author.id == 533275317276770324:
        userdb.setMemberPoints(ctx.guild, member, points)
        await ctx.send(f'set {member.display_name} points to {points}')
    else:
        await ctx.send('you are not allowed to use this command')

@bot.command()
async def manualInitialisation(ctx):
    initGuild(ctx.guild)
    await ctx.send('initialised all guilds')

def initGuild(guild: discord.Guild):
    result = userdb.addGuild(guild)
    if result == -1:
        logger.info('guild already exists, skipping...')
        return
    
    for member in guild.members:
        if member.bot:
            continue
        userdb.addMember(guild, member)