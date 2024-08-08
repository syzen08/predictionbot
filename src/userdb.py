import json
import logging
from datetime import date, timedelta
from pathlib import Path

import discord


class UserDB():
    def __init__(self, file) -> None:
        self.logger = logging.getLogger('db')
        self.file = Path(file)
        if not self.file.exists():
            with open(self.file, 'w') as f:
                f.write(json.dumps({}, indent=4))
                self.logger.info('created db')
        try:
            with open(self.file) as f:
                self.db = json.loads(f.read())
        except Exception as e:
            self.logger.fatal(f"Failed to load database (corrupt?). Error: {e}", exc_info=True)
            raise Exception("Failed to load database (corrupt?)")

    def saveDb(self):
        with open(self.file, 'w') as f:
            f.write(json.dumps(self.db, indent=4))
        
        with open(self.file) as f:
            self.db = json.loads(f.read())
        self.logger.debug('saved db to disk')

    def addGuild(self, guild: discord.Guild):
        if guild.id not in self.db:
            self.db[guild.id] = {}
            self.logger.info(f'created new guild {guild.id} ({guild.name}) in db')
            self.saveDb()
        else:
            self.logger.debug('guild {guild.id} ({guild.name}) already exists')
            return -1

    def addMember(self, guild: discord.Guild, member: discord.Member):
        if member not in self.db[str(guild.id)]:
            self.db[str(guild.id)][member.id] = {'points': 500, 'last_claim': date.isoformat(date.today() - timedelta(days=1))}
            self.logger.info(f'created new member {member.id} ({member.display_name}) in guild {guild.id} ({guild.name}) in db')
            self.saveDb()

    def getMemberPoints(self, guild: discord.Guild, member: discord.Member):
        return self.db[str(guild.id)][str(member.id)]['points']
    
    def setMemberPoints(self, guild: discord.Guild, member: discord.Member, points: int):
        self.db[str(guild.id)][str(member.id)]['points'] = points
        self.logger.debug(f'set {member.id} ({member.display_name}) points to {points}')
        self.saveDb()

    def addPoints(self, guild: discord.Guild, member: discord.Member, points: int):
        self.db[str(guild.id)][str(member.id)]['points'] += points
        self.logger.debug(f'added {points} points to {member.id} ({member.display_name}). current points: {self.db[str(guild.id)][str(member.id)]['points']}')
        self.saveDb()

    def removePoints(self, guild: discord.Guild, member: discord.Member, points: int) -> bool:
        newpoints = self.db[str(guild.id)][str(member.id)]['points'] - points
        if newpoints < 0:
            return False
        self.db[str(guild.id)][str(member.id)]['points'] = newpoints
        self.logger.debug(f'removed {points} points from {member.id} ({member.display_name}). current points: {self.db[str(guild.id)][str(member.id)]['points']}')
        self.saveDb()
        return True
    
    def setLastClaimDate(self, guild: discord.Guild, member: discord.Member, date: str):
        self.db[str(guild.id)][str(member.id)]['last_claim'] = date
        self.logger.debug(f'set {member.id} ({member.display_name}) last_claim to {date}')
        self.saveDb()

    def getLastClaimDate(self, guild: discord.Guild, member: discord.Member) -> date:
        return date.fromisoformat(self.db[str(guild.id)][str(member.id)]['last_claim'])
