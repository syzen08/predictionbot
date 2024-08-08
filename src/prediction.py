import discord


class Prediction():
    def __init__(self, name: str, option1: str, option2: str, endtime, channel: discord.TextChannel, message: discord.Message) -> None:
        self.name = name
        self.option1 = option1
        self.option2 = option2
        self.open = True
        self.result = None
        self.message = message

        self.end_time = endtime
        self.channel = channel

        self.option1_voters: list[discord.Member] = []
        self.option2_voters: list[discord.Member] = []
        self.all_voters: list[int] = []

        self.option1_amout = 0
        self.option2_amout = 0

    def addVote(self, member: discord.Member, option: int, amount: int):
        if option == 1:
            self.option1_voters.append(member)
            self.all_voters.append(member.id)
            self.option1_amout += amount
        elif option == 2:
            self.option2_voters.append(member)
            self.all_voters.append(member.id)
            self.option2_amout += amount

    async def close(self, user = None):
        self.open = False
        embed = self.message.embeds[0]
        embed.set_author(name="Vorhersage geschlossen")
        embed.color = discord.Color.dark_grey()
        if user is None:
            embed.remove_footer()
        else:
            embed.set_footer(text=f"Geschlossen von {user.display_name}")
        await self.message.edit(embed=embed, view=None)

    def setResult(self, option: int):
        self.result = option

    def getOptionName(self, option: int):
        if option == 1:
            return self.option1
        elif option == 2:
            return self.option2
        else:
            return None
        
    def getVoters(self, option: int):
        if option == 1:
            return self.option1_voters
        elif option == 2:
            return self.option2_voters
        else:
            return None
        
    def getPercentage(self, option: int):
        if self.option1_amout + self.option2_amout == 0:
            return 0
        if option == 1:
            return round(self.option1_amout / (self.option1_amout + self.option2_amout) * 100)
        elif option == 2:
            return round(self.option2_amout / (self.option1_amout + self.option2_amout) * 100)
        else:
            return None