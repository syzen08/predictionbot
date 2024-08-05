import discord


def getSuccessEmbed(message: str) -> discord.Embed:
    embed = discord.Embed(
        title='Erfolg!', 
        description=message,
        color=discord.Colour.from_str('#32C671')
    )
    embed.set_thumbnail(url="https://clipart-library.com/images_k/green-checkmark-transparent/green-checkmark-transparent-17.png")
    embed.set_author(name='Vorhersagen Bot', icon_url='https://cdn.discordapp.com/avatars/1269718308366716928/d618349fc238f3b7274e2db787db0cd8.webp')
    return embed

def getErrorEmbed(message: str) -> discord.Embed:
    embed = discord.Embed(
        title='Upps!',
        description=message,
        color=discord.Colour.from_str('#f26a5f')
    )
    embed.set_thumbnail(url="https://cdn1.iconfinder.com/data/icons/basic-ui-elements-2-5-flat-style-36-expand/512/Basic_UI_Elements_2.5_-_Flat_Style_-_36_-_Expand-10-512.png")
    embed.set_author(name='Vorhersagen Bot', icon_url='https://cdn.discordapp.com/avatars/1269718308366716928/d618349fc238f3b7274e2db787db0cd8.webp')
    return embed

def getInformationEmbed(title: str, message: str) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=message,
        color=discord.Colour.random()
    )
    embed.set_author(name='Vorhersagen Bot', icon_url='https://cdn.discordapp.com/avatars/1269718308366716928/d618349fc238f3b7274e2db787db0cd8.webp')
    return embed