import discord
import discord.types.components
from discord.ext import commands
from discord.ui import Button, View

from Bot.Embeds.BiSEmbed import BiSEmbed
from Bot.Embeds.InfoEmbed import InfoEmbed
from Bot.Embeds.ManagementEmbed import ManagementEmbed
from Bot.Embeds.PlayerInfoEmbed import PlayerInfoEmbed
from Bot.Player import Player, Role
from Bot.Team import Team, LootPriority
from Bot.TeamManager import TeamManager
from Bot.Views.BiSView import BiSView
from Bot.Views.ManagementView import ManagementView
from Bot.Views.PlayerView import PlayerView

COMMAND_PREFIX = '!'


class DiscordBot:
    def __init__(self, token: str):
        # take the discord auth token
        self.token = token
        # create the discord client with the given command prefix
        self.client = commands.Bot(command_prefix=COMMAND_PREFIX)
        # manages teams
        self.team_manager = TeamManager()
        # maps author IDs to team IDs
        self.team_leaders = {}
        # maps message IDs to team IDs
        self.team_members = {}

        @self.client.event
        async def on_ready():
            self.__handle_on_ready__()

        @self.client.command()
        async def info(ctx):
            await ctx.send(embed=InfoEmbed())

        @self.client.command()
        async def create(ctx, name: str):
            if not isinstance(ctx.channel, discord.channel.DMChannel):
                await ctx.send("This command can only be used in DMs.")
                return

            if ctx.author.id in self.team_leaders:
                await ctx.send("You already have an active team.")
                return

            uuid = self.team_manager.create_team(name)
            team = self.team_manager.teams[uuid]
            self.team_leaders[ctx.author.id] = uuid
            team.add_member(ctx.author.id)

            await ctx.send(embed=ManagementEmbed(team, COMMAND_PREFIX, uuid),
                           view=ManagementView(team, self.__handle_loot_priority_click__))

            member_message = await ctx.send(embed=PlayerInfoEmbed(team),
                                            view=PlayerView(team, team.members[ctx.author.id],
                                                            self.__handle_role_click__, self.__bis_callback__))
            self.team_members[member_message.id] = uuid

        self.client.run(self.token)

    def __handle_on_ready__(self):
        print(f'{self.client.user} ready!')

    async def __handle_role_click__(self, interaction, role: str):
        team = self.team_manager.teams[self.team_members[interaction.message.id]]
        team.members[interaction.user.id].role = Role[role]
        await interaction.response.edit_message(
            view=PlayerView(team, team.members[interaction.user.id], self.__handle_role_click__))

    async def __handle_loot_priority_click__(self, interaction: discord.Interaction, priority: str):
        self.team_manager.teams[self.team_leaders[interaction.user.id]].loot_priority = LootPriority[priority]
        await interaction.response.edit_message(
            view=ManagementView(self.team_manager.teams[self.team_leaders[interaction.user.id]],
                                self.__handle_loot_priority_click__))

    async def __handle_bis_finish__(self, interaction: discord.Interaction, bis):
        await interaction.response.send_message(bis)
        await interaction.message.delete()

    async def __bis_callback__(self, interaction: discord.Interaction):
        team = self.team_manager.teams[self.team_members[interaction.message.id]]
        await interaction.response.send_message(embed=BiSEmbed(team),
                                                view=BiSView(team.members[interaction.user.id],
                                                             self.__handle_bis_finish__),
                                                delete_after=600)
