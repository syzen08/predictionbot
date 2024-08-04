import logging

import discord
from discord.ext import commands

from userdb import UserDB

logger = logging.getLogger('bot')

userdb = UserDB('users.json')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='$', intents=intents)

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
    
@bot.command()
async def manualInitialisation(ctx):
    for guild in bot.guilds:
        initGuild(guild)
    await ctx.send('initialised guild')

def initGuild(guild: discord.Guild):
    result = userdb.addGuild(guild)
    if result == -1:
        logger.info('guild already exists, skipping...')
        return
    
    for member in guild.members:
        if member.bot:
            continue
        userdb.addUser(guild, member)