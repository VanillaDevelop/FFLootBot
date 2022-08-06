import discord

from Bot.Team import Team


class ManagementEmbed(discord.Embed):
    def __init__(self, team: Team, command_prefix: str):
        super().__init__()
        self.title = "Team Management"
        self.set_author(name=f"Team {team.get_team_name()}")
        self.description = f"This is the control panel for team {team.get_team_name()}."
        self.add_field(name="Inviting Team Members", value=f"Team members may join the team by DMing the bot with\n"
                                                           f"**{command_prefix}join {team.get_uuid()}** [Player Name]",
                       inline=False)
        self.add_field(name="Settings", value="**Loot Priority**"
                                              "\n__DPS__\n"
                                              "The bot will suggest giving loot to DPS, prioritizing those who have "
                                              "noted the item as the biggest upgrade."
                                              "\n__Equal__\n"
                                              "The bot will suggest giving loot to players who have given up "
                                              "the most loot so far, regardless of role."
                                              "\n**None**\n"
                                              "The bot will not suggest any loot distribution.",
                       inline=False)
