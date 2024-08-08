# TODO: 
# status aendern   
# 


import asyncio
import datetime
import logging

import discord
from discord import app_commands
from discord.ext import commands, tasks
from embeds import getErrorEmbed, getHelpEmbed, getInformationEmbed, getSuccessEmbed
from prediction import Prediction
from userdb import UserDB

logger = logging.getLogger('bot')

userdb = UserDB('db/users.json')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

current_predictions: dict[Prediction] = {}

bot = commands.Bot(command_prefix='$', intents=intents)



###############
#   CLASSES   #
###############


class PredictionSubmitModal(discord.ui.Modal, title='Wie viel Euro willst du wetten?'):
    amount = discord.ui.TextInput(label='! Du kannst nur ein mal wetten !', placeholder='z.B. 100', required=True, style=discord.TextStyle.short, max_length=6)

    def __init__(self, predictionchannel: discord.TextChannel, option: int, *,  timeout: float | None = None) -> None:
        super().__init__(title=discord.utils.MISSING, timeout=timeout, custom_id=discord.utils.MISSING)
        self.predictionchannel = predictionchannel
        self.option = option

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount.value)
        except ValueError:
            logger.info(f'{interaction.user.display_name} tried to submit a non-integer value ({self.amount.value})')
            await interaction.response.send_message(embed=getErrorEmbed("Bitte gib nur Zahlen ein!"), ephemeral=True)
            return

        if not userdb.removePoints(interaction.guild, interaction.user, amount):
            logger.info(f'{interaction.user.display_name} tried to submit more points ({amount}) than they have ({userdb.getMemberPoints(interaction.guild, interaction.user)})')
            await interaction.response.send_message(embed=getErrorEmbed(f"Du hast nicht genug Geld! \nDein aktueller Kontostand betraegt **{userdb.getMemberPoints(interaction.guild, interaction.user)} Euro** "), ephemeral=True)
            return

        current_predictions[self.predictionchannel.id].addVote(interaction.user, self.option, amount)
        logger.info(f'{interaction.user.display_name} predicted option {self.option} with {amount} points')
        await interaction.response.send_message(embed=getSuccessEmbed(f'Du hast mit **{amount} Euro** fuer **{current_predictions[self.predictionchannel.id].getOptionName(self.option)}** gestimmt!'), ephemeral=True)
        predictionembed = current_predictions[self.predictionchannel.id].message.embeds[0]
        predictionembed.set_field_at(0, name=f"{current_predictions[self.predictionchannel.id].option1} | {current_predictions[self.predictionchannel.id].getPercentage(1)}%", value=f"{current_predictions[self.predictionchannel.id].option1_amout} Euro")
        predictionembed.set_field_at(1, name=f"{current_predictions[self.predictionchannel.id].option2} | {current_predictions[self.predictionchannel.id].getPercentage(2)}%", value=f"{current_predictions[self.predictionchannel.id].option2_amout} Euro")

        await current_predictions[self.predictionchannel.id].message.edit(embed=predictionembed)

class PredictionView(discord.ui.View):
    def __init__(self, predictionchannel: discord.TextChannel):
        super().__init__(timeout=None)
        self.value = None
        self.predictionchannel = predictionchannel
        logger.info(self.children)

    @discord.ui.button(label='Option 1', style=discord.ButtonStyle.green)
    async def option1(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.validateIfUserVoted(interaction, interaction.user):
            await interaction.response.send_modal(PredictionSubmitModal(self.predictionchannel, 1))
            logger.info(f'{interaction.user.display_name} selected option 1')

    @discord.ui.button(label='Option 2', style=discord.ButtonStyle.blurple)
    async def option2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.validateIfUserVoted(interaction, interaction.user):
            await interaction.response.send_modal(PredictionSubmitModal(self.predictionchannel, 2))
            logger.info(f'{interaction.user.display_name} selected option 2')
        
    async def validateIfUserVoted(self, interaction: discord.Interaction, user: discord.Member) -> bool:
        if user.id in current_predictions[self.predictionchannel.id].all_voters:
            await interaction.response.send_message(embed=getErrorEmbed('Du hast bereits abgestimmt!'), ephemeral=True)
            return True
        else:
            return False

class ClosePredictionView(discord.ui.View):
    def __init__(self, result: int):
        super().__init__(timeout=None)
        self.value = None
        self.result = result

    @discord.ui.button(label='Ja, schliessen', style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not current_predictions[interaction.channel.id].open:
            return
        await current_predictions[interaction.channel.id].close(interaction.user)
        logger.info(f'{interaction.user.display_name} closed the prediction {current_predictions[interaction.channel.id].name} in {interaction.channel.name}')
        await interaction.response.send_message(embed=getSuccessEmbed('Vorhersage wurde geschlossen'), ephemeral=True)

    @discord.ui.button(label='Nein, abbrechen', style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=getSuccessEmbed('Vorhersage wurde nicht geschlossen'), ephemeral=True)


##############
#   EVENTS   #
##############


@bot.event
async def on_ready():
    logger.info(f'logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        logger.info(f'synced {len(synced)} command(s)')
    except Exception as e:
        logger.error(f'sync failed: {e}')

    checkPredictions.start()
    logger.info('started checkPredictions loop')

    try:
        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(name='euch beim Schlafen zu', type=discord.ActivityType.watching))
        logger.info("set custom presence")
    except Exception as e:
        logger.error(e)

@bot.event
async def on_guild_join(guild):
    logger.info(f'joined new guild {guild.id} ({guild.name})')
    initGuild(guild)


#################################
#   POINT MANAGEMENT COMMANDS   #
#################################


@bot.hybrid_group(name='geld', description='Zeigt dir deinen Kontostand an', fallback='kontostand')
async def points(ctx):
    points = userdb.getMemberPoints(ctx.guild, ctx.author)
    await ctx.reply(embed=getInformationEmbed(f"{ctx.author.display_name}'s Kontostand", f"*{ctx.author.display_name}* hat **{points} Euro**"), ephemeral=True)
    logger.info(f'{ctx.author.display_name} viewed their points')

@points.command(name='überweise', description='Überweise jemanden ein wenig Asche, für schwere Zeiten')
async def givePoints(ctx, member: discord.Member, amount: int):
    if userdb.removePoints(ctx.guild, ctx.author, amount):
        userdb.addPoints(ctx.guild, member, amount)
        await ctx.reply(embed=getSuccessEmbed(f"Du hast {member.display_name} **{amount} Euro** überwiesen. Dein Kontostand beträgt jetzt **{userdb.getMemberPoints(ctx.guild, ctx.author)} Euro.**"), ephemeral=True)
        await member.send(f'*Psst...* **{ctx.author.display_name}** hat dir **{amount} Euro** geschickt!\nDu hast jetzt **{userdb.getMemberPoints(ctx.guild, member)} Euro.** Mach keinen Quatsch damit.')
        logger.info(f'{ctx.author.display_name} gave {amount} points to {member.display_name}')
    else:
        await ctx.reply(embed=getErrorEmbed(f"Du hast nicht genug Geld! \nDein aktueller Kontostand betraegt **{userdb.getMemberPoints(ctx.guild, ctx.author)} Euro** "), ephemeral=True)

@points.command(name='hartz4', description='Hol dir dein tägliches Geldpaket (500 Euro)')
async def claimDailyPoints(ctx):
    last_claim = userdb.getLastClaimDate(ctx.guild, ctx.author)
    if last_claim is None or last_claim == datetime.date.today() - datetime.timedelta(days=1):
        userdb.setLastClaimDate(ctx.guild, ctx.author, datetime.date.today().isoformat())
        userdb.addPoints(ctx.guild, ctx.author, 500)
        await ctx.reply(embed=getSuccessEmbed(f'Du hast dein Hartz IV erhalten. Dein Kontostand beträgt jetzt **{userdb.getMemberPoints(ctx.guild, ctx.author)} Euro.**'), ephemeral=True)
        logger.info(f'{ctx.author.display_name} claimed their daily points')
    else:
        await ctx.reply(embed=getErrorEmbed(f'Werd mal nicht gierig hier, {ctx.author.display_name}. Komm morgen wieder, dann kriegst du auch wieder was.'), ephemeral=True)


###########################
#   PREDICTION COMMANDS   #
###########################


@bot.hybrid_group(name='vorhersage', description='Starte eine neue Vorhersage', fallback='erstellen')
@app_commands.describe(
    title='Titel der Vorhersage',
    option1='Option 1',
    option2='Option 2',
    endtime='Dauer der Vorhersage in Sekunden. Bei 0 muss sie mit /vorhersage schliessen manuell geschlossen werden'
)
@app_commands.rename(
    title='titel', 
    option1='option_1', 
    option2='option_2', 
    endtime='dauer'
)
async def startPrediction(ctx, title: str, option1: str, option2: str, endtime: int):
    if len(current_predictions.keys()) > 0 and current_predictions[ctx.channel.id] is not None:
        if current_predictions[ctx.channel.id].result is None:
            await ctx.reply(embed=getErrorEmbed('Es gibt bereits eine laufende Vorhersage in diesem Kanal!'), ephemeral=True)
            return

    if endtime <= 0:
        end_time = None
    else:
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=endtime)
    logger.info(f'{ctx.author.display_name} started prediction: {title}: {option1} | {option2}')
    predictionembed = discord.Embed()
    predictionembed.title = title
    predictionembed.add_field(name=f"{option1} | 0%", value="0 Euro")
    predictionembed.add_field(name=f"{option2} | 0%", value="0 Euro")
    predictionembed.color = discord.Color.purple()
    if end_time is None:
        predictionembed.set_footer(text='Vorhersage schliesst nicht automatisch')
    else:
        predictionembed.set_footer(text=f'Vorhersage schliesst nach {endtime} Sekunden')
    prediction_message = await ctx.send(embed=predictionembed, view=PredictionView(ctx.channel))
    prediction = Prediction(title, option1, option2, end_time, ctx.channel, prediction_message)
    current_predictions[ctx.channel.id] = prediction

@startPrediction.command(name='schliessen', description='Schliesst die laufende Vorhersage')
async def closePrediction(ctx):
    try:
        prediction = current_predictions[ctx.channel.id]
        if prediction.open:
            await prediction.close(ctx.author)
            logger.info(f'{ctx.author.display_name} closed the prediction {prediction.name} in {ctx.channel.name}')
            await ctx.send(embed=getSuccessEmbed(f'Vorhersage `{prediction.name}` geschlossen!'), ephemeral=True)
        else:
            logger.info(f'{ctx.author.display_name} tried to close a prediction that is already closed')
            await ctx.reply(embed=getErrorEmbed('Die Vorhersage ist bereits geschlossen!'), ephemeral=True)
    except KeyError:
        logger.info(f'{ctx.author.display_name} tried to close a non-existent prediction')
        await ctx.reply(embed=getErrorEmbed('Es gibt keine laufende Vorhersage in diesem Kanal!'), ephemeral=True)

@startPrediction.command(name='ergebnis', description='Setzt das Ergebnis der Vorhersage fest und zahlt allen Mitspielern ihren Anteil aus')
@app_commands.describe(
    option='Option die gewonnen hat (1 oder 2)'
)
async def setPredictionResult(ctx, option: int):
    if option != 1 and option != 2:
        await ctx.reply(embed=getErrorEmbed('Es gibt nur 2 Optionen, 1 oder 2. Entscheide dich weise'), ephemeral=True)
        return
    try:
        prediction = current_predictions[ctx.channel.id]
        if prediction.open:
            await ctx.send(embed=getErrorEmbed('Die Vorhersage ist nicht geschlossen! Willst du sie jetzt schliessen?'), view=ClosePredictionView(option), ephemeral=True)
            return
        else:
            prediction.setResult(option)
            totalpoints = prediction.option1_amout + prediction.option2_amout
            logger.info(f'{ctx.author.display_name} set the result of {prediction.name} to {option}')
    except KeyError:
        logger.info(f'{ctx.author.display_name} tried to set the result of a non-existent prediction')
        await ctx.reply(embed=getErrorEmbed('Es gibt keine laufende Vorhersage in diesem Kanal!'), ephemeral=True)
        return
    
    embed: discord.Embed = prediction.message.embeds[0]
    embed.set_author(name='Vorhersage vorbei')
    embed.color = discord.Color.green()
    embed.set_footer(text=f'Ergebnis von {ctx.author.display_name}')

    match prediction.result:
        case 1:
            if len(prediction.option1_voters) == 0:
                embed.set_field_at(0, name=f"🎉 **{prediction.option1} | {prediction.getPercentage(1)}%**", value=f"{prediction.option1_amout} Euro\nNiemand hat hier gewettet, **{totalpoints} Euro** gehen verloren!")
                logger.info(f'No one voted for option {prediction.option1}, {totalpoints} Points lost')
            else:
                pointshare = round(totalpoints / len(prediction.option1_voters))
                for member in prediction.option1_voters:
                    userdb.addPoints(ctx.guild, member, pointshare)
                embed.set_field_at(0, name=f"🎉 **{prediction.option1} | {prediction.getPercentage(1)}%**", value=f"{prediction.option1_amout} Euro\n**{totalpoints} Euro** werden an {len(prediction.option1_voters)} Mitglieder verteilt")
                logger.info(f'a price pool of {totalpoints} is split for {len(prediction.option1_voters)} voters, each member gets {pointshare} points')
        case 2:
            if len(prediction.option2_voters) == 0:
                embed.set_field_at(1, name=f"🎉 **{prediction.option2} | {prediction.getPercentage(2)}%**", value=f"{prediction.option2_amout} Euro\nNiemand hat hier gewettet, **{totalpoints} Euro** gehen verloren!")
                logger.info(f'No one voted for option {prediction.option2}, {totalpoints} Points lost')
                await prediction.message.edit(embed=embed)
            else:
                pointshare = round(totalpoints / len(prediction.option2_voters))
                for member in prediction.option2_voters:
                    userdb.addPoints(ctx.guild, member, pointshare)
                embed.set_field_at(1, name=f"🎉 **{prediction.option1} | {prediction.getPercentage(2)}%**", value=f"{prediction.option2_amout} Euro\n**{totalpoints}** werden an {len(prediction.option2_voters)} Mitglieder verteilt")
                logger.info(f'a price pool of {totalpoints} is split for {len(prediction.option2_voters)} voters, each member gets {pointshare} points')
    
    await prediction.message.edit(embed=embed)
    await ctx.send(embed=getSuccessEmbed('Ergebnis festgelegt'), ephemeral=True)

@startPrediction.command(name='abbrechen', description='Bricht die aktuelle Vorhersage ab und löscht sie. !!!GELD GEHT VERLOREN!!!') # TODO: repay users after deletion
async def removePrediction(ctx):
    await current_predictions[ctx.channel.id].message.delete()
    current_predictions[ctx.channel.id] = None
    await ctx.reply(embed=getSuccessEmbed('Vorhersage entfernt'), ephemeral=True)


######################
#   ADMIN COMMANDS   #
######################


@bot.command()
@commands.is_owner()
async def setPoints(ctx, member: discord.Member, points: int):
    if ctx.author.id == 533275317276770324:
        userdb.setMemberPoints(ctx.guild, member, points)
        await ctx.send(embed=getSuccessEmbed(f'set {member.display_name} points to {points}'))
        logger.info(f'{ctx.author.display_name} set {member.display_name} points to {points}')
    else:
        await ctx.send(embed=getErrorEmbed('Du hast nicht die Berechtigung, diesen Befehl auszufuehren!'), ephemeral=True)
        logger.info(f'{ctx.author.display_name} tried to use the setPoints command')

@bot.command()
@commands.is_owner()
async def quitBot(ctx):
    app_info = await bot.application_info()
    if app_info.name == 'VorhersagenBot':
        message = await ctx.send('Willst du den Bot wirklich stoppen?')
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '💀'
        
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=15.0, check=check)
        except asyncio.TimeoutError:
            await message.edit(content='abgebrochen')
            logger.info('cancelled shutdown')
            return
        else:
            logger.info('really confirmed shutdown')

    await ctx.send('Tschaudi Arabien :wave:')
    userdb.saveDb()
    await bot.close()
    logger.info('bot exited, goodbye :wave:')
    exit(0)

@bot.command()
async def manualInitialisation(ctx):
    logger.info('manual guild initialisation')
    initGuild(ctx.guild)
    await ctx.send(embed=getSuccessEmbed('initialised guild'))


#############
#   OTHER   #
#############


@bot.hybrid_command(name='echo', description='🦜🦜🦜')
async def echo(interaction: discord.Interaction, message):
    logger.info('ran echo')
    await interaction.reply(message)

@bot.hybrid_command(name='hilfe', description='hilfe? was passiert hier?!? hallo? was soll das?! ich hab angst :(. mama, kannst du mich abholen?')
async def printHelp(ctx):
    logger.info(f'showing help to {ctx.author.display_name}')
    await ctx.reply(embeds=getHelpEmbed(), ephemeral=True)

@tasks.loop(seconds=5)
async def checkPredictions():
    logger.debug('checking predictions')
    for prediction in current_predictions.values():
        if prediction is None:
            continue

        if not prediction.open:
            continue

        if prediction.end_time is None:
            logger.debug(f'prediction {prediction.name} is set to never end')
            continue

        if prediction.end_time < datetime.datetime.now():
            await prediction.close()
            logger.info(f'prediction {prediction.name} has ended and is now closed')

def initGuild(guild: discord.Guild):
    result = userdb.addGuild(guild)
    if result == -1:
        logger.info('guild already exists, skipping...')
        return
    
    for member in guild.members:
        if member.bot:
            continue
        userdb.addMember(guild, member)