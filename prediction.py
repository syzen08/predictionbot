import discord


class Prediction():
    def __init__(self, name: str, option1: str, option2: str) -> None:
        self.name = name
        self.option1 = option1
        self.option2 = option2
        self.open = True

        self.option1_voters = []
        self.option2_voters = []
        self.all_voters = []

        self.option1_amout = 0
        self.option2_amout = 0

    def addVote(self, member: discord.Member, option: int, amount: int):
        if option == 1:
            self.option1_voters.append(member.id)
            self.all_voters.append(member.id)
            self.option1_amout += amount
        elif option == 2:
            self.option2_voters.append(member.id)
            self.all_voters.append(member.id)
            self.option2_amout += amount

    def close(self):
        self.open = False

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
        if option == 1:
            return round(self.option1_amout / (self.option1_amout + self.option2_amout) * 100)
        elif option == 2:
            return round(self.option2_amout / (self.option1_amout + self.option2_amout) * 100)
        else:
            return None