import logging

import discord
from discord.ext import commands

from embeds import getErrorEmbed, getInformationEmbed, getSuccessEmbed
from prediction import Prediction
from userdb import UserDB

logger = logging.getLogger('bot')

userdb = UserDB('users.json')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

current_predictions: list[Prediction] = []

bot = commands.Bot(command_prefix='$', intents=intents)

class PredictionSubmitModal(discord.ui.Modal, title='Wie viel Euro willst du wetten?'):
    amount = discord.ui.TextInput(label='! Du kannst nur ein mal wetten !', placeholder='z.B. 100', required=True, style=discord.TextStyle.short, max_length=6)

    def __init__(self, currentpredictionsidx: int, option: int, *,  timeout: float | None = None) -> None:
        super().__init__(title=discord.utils.MISSING, timeout=timeout, custom_id=discord.utils.MISSING)
        self.currpredidx = currentpredictionsidx
        self.option = option

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount.value)
        except ValueError:
            logger.warning(f'{interaction.user.display_name} tried to submit a non-integer value ({self.amount.value})')
            await interaction.response.send_message(embed=getErrorEmbed("Bitte gib nur Zahlen ein!"), ephemeral=True)
            return

        if not userdb.removePoints(interaction.guild, interaction.user, amount):
            logger.warning(f'{interaction.user.display_name} tried to submit more points ({amount}) than they have ({userdb.getMemberPoints(interaction.guild, interaction.user)})')
            await interaction.response.send_message(embed=getErrorEmbed(f"Du hast nicht genug Geld! \nDein aktueller Kontostand betraegt **{userdb.getMemberPoints(interaction.guild, interaction.user)} Euro** "), ephemeral=True)
            return

        current_predictions[self.currpredidx].addVote(interaction.user, self.option, amount)
        logger.info(f'{interaction.user.display_name} predicted option {self.option} with {amount} points')
        await interaction.response.send_message(embed=getSuccessEmbed(f'Du hast mit **{amount} Euro** fuer **{current_predictions[self.currpredidx].getOptionName(self.option)}** gestimmt!'), ephemeral=True)
        predictionembed = discord.Embed()
        predictionembed.title = current_predictions[self.currpredidx].name

        predictionembed.add_field(name=f"{current_predictions[self.currpredidx].option1} | {current_predictions[self.currpredidx].getPercentage(1)}%", value=f"{current_predictions[self.currpredidx].option1_amout} Euro")
        predictionembed.add_field(name=f"{current_predictions[self.currpredidx].option2} | {current_predictions[self.currpredidx].getPercentage(2)}%", value=f"{current_predictions[self.currpredidx].option2_amout} Euro")
        predictionembed.color = discord.Color.purple()

        await interaction.message.edit(embed=predictionembed)


class PredictionView(discord.ui.View):
    def __init__(self, predictionidx: int):
        super().__init__(timeout=None)
        self.value = None
        self.predidx = predictionidx

    @discord.ui.button(label='Option 1', style=discord.ButtonStyle.green)
    async def option1(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.validateIfUserVoted(interaction, interaction.user):
            await interaction.response.send_modal(PredictionSubmitModal(self.predidx, 1))
            logger.info(f'{interaction.user.display_name} selected option 1')

    @discord.ui.button(label='Option 2', style=discord.ButtonStyle.red)
    async def option2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.validateIfUserVoted(interaction, interaction.user):
            await interaction.response.send_modal(PredictionSubmitModal(self.predidx, 2))
            logger.info(f'{interaction.user.display_name} selected option 2')
        
    async def validateIfUserVoted(self, interaction: discord.Interaction, user: discord.Member) -> bool:
        if user.id in current_predictions[self.predidx].all_voters:
            await interaction.response.send_message(embed=getErrorEmbed('Du hast bereits abgestimmt!'), ephemeral=True)
            return True
        else:
            return False

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
async def getPoints(ctx, member: discord.Member):
    points = userdb.getMemberPoints(ctx.guild, member)
    await ctx.reply(embed=getInformationEmbed(f"{member.display_name}'s Kontostand", f"*{member.display_name}* hat **{points} Euro**"))
    logger.info(f'{ctx.author.display_name} requested points of {member.display_name}')

@bot.hybrid_command(name='vorhersage', description='starte eine neue vorhersage')
async def startPrediction(ctx, title: str, option1: str, option2: str):
    prediction = Prediction(title, option1, option2)
    current_predictions.append(prediction)
    logger.info(f'{ctx.author.display_name} started prediction: {prediction.name}: {prediction.option1} | {prediction.option2}')
    predictionembed = discord.Embed()
    predictionembed.title = title
    predictionembed.add_field(name=f"{option1} | 0%", value="0 Euro")
    predictionembed.add_field(name=f"{option2} | 0%", value="0 Euro")
    predictionembed.color = discord.Color.purple()
    await ctx.send(embed=predictionembed, view=PredictionView(current_predictions.index(prediction)))

@bot.command()
async def setPoints(ctx, member: discord.Member, points: int):
    if ctx.author.id == 533275317276770324:
        userdb.setMemberPoints(ctx.guild, member, points)
        await ctx.send(embed=getSuccessEmbed(f'set {member.display_name} points to {points}'))
        logger.info(f'{ctx.author.display_name} set {member.display_name} points to {points}')
    else:
        await ctx.send(embed=getErrorEmbed('Du hast nicht die Berechtigung, diesen Befehl auszufuehren!'))
        logger.info(f'{ctx.author.display_name} tried to use the setPoints command')

@bot.command()
async def manualInitialisation(ctx):
    logger.info('manual guild initialisation')
    initGuild(ctx.guild)
    await ctx.send(embed=getSuccessEmbed('initialised guild'))

def initGuild(guild: discord.Guild):
    result = userdb.addGuild(guild)
    if result == -1:
        logger.info('guild already exists, skipping...')
        return
    
    for member in guild.members:
        if member.bot:
            continue
        userdb.addMember(guild, member)