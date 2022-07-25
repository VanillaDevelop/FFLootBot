import discord
from Bot.Team import Team


class PlayerInfoEmbed(discord.Embed):
    def __init__(self, team: Team):
        super().__init__()
        self.title = f"Team {team.name}"
        self.description = f"This is the information panel for team {team.name}."
        self.add_field(name="Current Team Status",
                       value=f"Team members: {len(team.members)}")
