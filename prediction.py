import discord

class Prediction():
    def __init__(self, name: str, option1: str, option2: str) -> None:
        self.name = name
        self.option1 = option1
        self.option2 = option2
        self.open = True

        self.option1_voters = []
        self.option2_voters = []

    def addVote(self, member: discord.Member, option: int):
        if option == 1:
            self.option1_voters.append(member.id)
        elif option == 2:
            self.option2_voters.append(member.id)

    def close(self):
        self.open = False

    def getOptionName(self, option: int):
        if option == 1:
            return self.option1
        elif option == 2:
            return self.option2
        else:
            return None