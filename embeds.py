import discord


def getSuccessEmbed(message: str) -> discord.Embed:
    embed = discord.Embed(
        title='Erfolg!', 
        description=message,
        color=discord.Colour.from_str('#32C671')
    )
    embed.set_thumbnail(url="https://clipart-library.com/images_k/green-checkmark-transparent/green-checkmark-transparent-17.png")
    embed.set_author(name='Vorhersagen Bot', icon_url='https://cdn.discordapp.com/avatars/1269718308366716928/cfa8500ccffd02da95272032e17753ac.webp')
    return embed

def getErrorEmbed(message: str) -> discord.Embed:
    embed = discord.Embed(
        title='Upps!',
        description=message,
        color=discord.Colour.from_str('#f26a5f')
    )
    embed.set_thumbnail(url="https://cdn1.iconfinder.com/data/icons/basic-ui-elements-2-5-flat-style-36-expand/512/Basic_UI_Elements_2.5_-_Flat_Style_-_36_-_Expand-10-512.png")
    embed.set_author(name='Vorhersagen Bot', icon_url='https://cdn.discordapp.com/avatars/1269718308366716928/cfa8500ccffd02da95272032e17753ac.webp')
    return embed

def getInformationEmbed(title: str, message: str) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=message,
        color=discord.Colour.random()
    )
    embed.set_author(name='Vorhersagen Bot', icon_url='https://cdn.discordapp.com/avatars/1269718308366716928/cfa8500ccffd02da95272032e17753ac.webp')
    return embed

def getHelpEmbed() -> list[discord.Embed]:
    titleembed = discord.Embed(
        title='Hilfe',
        description='''Du bist verwirrt? Du möchtest wissen, was dieser Bot alles kann? 
        Du willst wissen, warum jemand hinter dir mit nem Messer steht? *ha, reingefallen*
        Dann bist du hier genau richtig! Hier findest du alle Befehle, die der Bot so draufhat.
        (*Pro Tip:* **Wenn du einen Befehl eintippst, siehst du bei jedem Feld oben eine Beschreibung, was es macht und was da genau rein soll. Sehr nützlich.**)''',
        color=discord.Colour.random()
    )
    titleembed.set_thumbnail(url='https://media1.tenor.com/m/ReV7SmZ4CQwAAAAC/live-reaction-honest-reaction.gif')
    titleembed.set_author(name='Vorhersagen Bot')

    predictionEmbed = discord.Embed(
        title='Vorhersagen',
        description='Das große Feature, worauf alle gewartet haben. Der Grund, warum der Bot überhaupt hier ist.\nIch glaub, ich muss nicht viel dazu erklären.',
        color=discord.Colour.random()
    )
    predictionEmbed.add_field(
        name='`/vorhersage erstellen [titel] [option1] [option2] [dauer]`',
        value="""Startet eine neue Vorhersage im Kanal, in dem der Befehl ausgeführt wurde. **Es kann nur eine aktive Vorhersage pro Text-Kanal geben.**
        `[titel]` ist der Titel der Vorhersage.
        `[option1]` und `[option2]` sind die beiden Optionen, auf die ihr wetten könnt.
        `[dauer]` ist die Dauer in Sekunden, in der die Vorhersage laufen soll. Wenn du 0 Sekunden angibts, schließt sich die Vorhersage nicht automatisch.""",
        inline=False
    )
    predictionEmbed.add_field(
        name='`/vorhersage schliessen`',
        value="""Schließt die laufende Vorhersage im Kanal, in dem der Befehl ausgeführt wurde.""",
        inline=False
    )
    predictionEmbed.add_field(
        name="`/vorhersage ergebnis [ergebnis]`",
        value="""Setzt das Ergebnis der Vorhersage fest. Den Gewinnern wird ihr Anteil des Gewinnes überwiesen.
        `[ergebnis]` ist entweder `1` für Option 1 oder `2` für Option 2""",
        inline=False
    )
    predictionEmbed.add_field(
        name='`/vorhersage abbrechen`',
        value="""Bricht die aktuelle Vorhersage ab und löscht sie aus dem Kanal.
        **!!!ACHTUNG!!! ALLES GELD, WAS GEWETTET WURDE GEHT VERLOREN!**""",
        inline=False
    )
    predictionEmbed.set_thumbnail(url='https://media1.tenor.com/m/RK8A2kJ8Mo8AAAAC/curious-cat-lol.gif')
    points_embed = discord.Embed(
        title='Geld',
        description='Was wettet man in den Vorhersagen? Kostbare Euronen natürlich!',
        color=discord.Colour.random()
    )
    points_embed.add_field(
        name='`/geld kontostand`',
        value="""Zeigt dir, wie viel Euro du noch in der Tasche hast.""",
        inline=False
    )
    points_embed.add_field(
        name='`/geld überweise [person] [summe]`',
        value="""'Hast du noch 'n Euro?', aber virtuell.
        `[person]` ist die Person, an die du Geld abgeben möchtest.
        `[summe]` ist die Geld Summe, die du abdrücken willst *(musst)*.""",
        inline=False
    )
    points_embed.add_field(
        name='`/geld hartz4`',
        value='Genau das, wonach es klingt. Hol dir mit diesem Befehl jeden Tag **500 Euro** ab.',
        inline=False
    )
    points_embed.set_thumbnail(url='https://media1.tenor.com/m/BwkdOKNw4cMAAAAd/cat-money.gif')

    endembed = discord.Embed(
        description='Wenn du noch fragen hast, dann schreib mir auf Discord!\nWenn der Bot auf einmal stur wird, dann schreib mir auch, ich helf ihm wieder auf den richtigen Weg zu kommen',
        color=discord.Colour.random()
    )
    endembed.set_thumbnail(url='https://media1.tenor.com/m/Mle3dtAOrfEAAAAd/cat-keyboard.gif')
    endembed.set_footer(text='made by syzen with <3')

    return [titleembed, predictionEmbed, points_embed, endembed]