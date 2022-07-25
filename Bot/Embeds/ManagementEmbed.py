import discord

from Bot.Team import Team


class ManagementEmbed(discord.Embed):
    def __init__(self, team: Team, command_prefix: str, uuid: str):
        super().__init__()
        self.title = "Team Management"
        self.set_author(name=f"Team {team.name}")
        self.description = f"This is the control panel for team {team.name}."
        self.add_field(name="Inviting Team Members", value=f"Team members may join the team by DMing the bot with "
                                                           f"**{command_prefix}join {uuid}**.", inline=False)
        self.add_field(name="Loot Distribution", value="Select below who should get priority for loot drops."
                                                       "\n**DPS**\n"
                                                       "Loot will be distributed according to the biggest DPS "
                                                       "improvement. This means loot will go exclusively to DPS "
                                                       "(unless all DPS already possess a similar or better item)"
                                                       " and large item upgrades will be prioritized."
                                                       "\n**Equal Loot**\n"
                                                       "Loot will be distributed in such "
                                                       "a way that the power increase of all players is roughly "
                                                       "equal. Players who have less loot will receive priority "
                                                       "on drops which benefit them."
                                                       "\n**None**\n"
                                                       "No loot priority will be provided, but the bot will "
                                                       "show the potential upgrade for every player.",
                       inline=False)
