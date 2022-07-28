import discord

from Bot.Player import Role
from Bot.Team import Team


class PlayerInfoEmbed(discord.Embed):
    def __init__(self, team: Team):
        super().__init__()
        self.title = f"Team {team.name}"
        self.description = f"This is the information panel for team {team.name}."

        tanks = [member for member in team.members if team.members[member].role == Role.TANK]
        healers = [member for member in team.members if team.members[member].role == Role.HEAL]
        dps = [member for member in team.members if team.members[member].role == Role.DPS]

        teammates = f"**Tanks: {len(tanks)}**\n**Healers: {len(healers)}**\n**DPS: {len(dps)}**"
        self.add_field(name="Current Team Members",
                       value=teammates)
