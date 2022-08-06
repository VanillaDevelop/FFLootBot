import os
import pickle

import discord
import discord.types.components
from discord.ext import commands
import atexit

from Bot.Embeds.AssignLootEmbed import AssignLootEmbed
from Bot.Embeds.BiSEmbed import BiSEmbed
from Bot.Embeds.InfoEmbed import InfoEmbed
from Bot.Embeds.ManagementEmbed import ManagementEmbed
from Bot.Embeds.PlayerInfoEmbed import PlayerInfoEmbed
from Bot.Embeds.PlayerPurchaseEmbed import PlayerPurchaseEmbed
from Bot.Player import Role, RaidUpgrade, Item
from Bot.Team import Team, LootPriority
from Bot.TeamManager import TeamManager
from Bot.Views.AssignLootView import AssignLootView
from Bot.Views.BiSView import BiSView
from Bot.Views.ManagementView import ManagementView
from Bot.Views.PlayerPurchaseView import PlayerPurchaseView
from Bot.Views.PlayerView import PlayerView

COMMAND_PREFIX = '!'
BIS_TIMEOUT = 600
PURCHASE_TIMEOUT = 180
LOAD_CONFIG_FILE = False


class DiscordBot:
    def __init__(self, token: str):
        # take the discord auth token
        self.token = token
        # create the discord client with the given command prefix
        self.client = commands.Bot(command_prefix=COMMAND_PREFIX)
        # manages __teams
        self.team_manager = TeamManager()

        @self.client.event
        async def on_ready():
            self.__handle_on_ready__()
            atexit.register(self.on_disconnect)

            if LOAD_CONFIG_FILE and os.path.exists('TeamData.obj'):
                with open('TeamData.obj', 'rb') as f:
                    self.team_manager = pickle.load(f)

                for team_id in self.team_manager.get_all_team_ids():
                    team = self.team_manager.get_team_by_uuid(team_id)
                    self.client.add_view(ManagementView(team,
                                                        self.__handle_loot_priority_click__,
                                                        self.__assign_loot_callback__,
                                                        self.__handle_disband_team__))
                    for player_id in team.__members:
                        player = team.__members[player_id]
                        self.client.add_view(PlayerView(player,
                                                        self.__handle_role_click__, self.__bis_callback__,
                                                        self.__purchase_callback__, self.__handle_leave_team__))

        @self.client.command()
        async def info(ctx):
            await ctx.send(embed=InfoEmbed(COMMAND_PREFIX))

        @self.client.command()
        async def create(ctx, team_name: str, *, player_name):
            if not isinstance(ctx.channel, discord.channel.DMChannel):
                await ctx.send("This command can only be used in DMs.")
                return

            if self.team_manager.get_team_by_leader(ctx.author.id) is not None:
                await ctx.send("You already have an active team.", delete_after=5)
                return

            if not player_name:
                await ctx.send("Please enter a player name.", delete_after=5)
                return

            if not team_name:
                await ctx.send("Please enter a team name.", delete_after=5)
                return

            # create team and player in team
            team = self.team_manager.create_team(team_name, ctx.author.id)
            player = team.add_member(ctx.author.id, player_name)

            self.client.add_view(ManagementView(team, self.__handle_loot_priority_click__,
                                                self.__assign_loot_callback__,
                                                self.__handle_disband_team__))
            self.client.add_view(PlayerView(team.get_member_by_author_id(ctx.author.id),
                                            self.__handle_role_click__, self.__bis_callback__,
                                            self.__purchase_callback__, self.__handle_leave_team__))

            await ctx.send(embed=ManagementEmbed(team, COMMAND_PREFIX),
                           view=ManagementView(team, self.__handle_loot_priority_click__,
                                               self.__assign_loot_callback__,
                                               self.__handle_disband_team__))

            member_message = await ctx.send(embed=PlayerInfoEmbed(team, player),
                                            view=PlayerView(team.get_member_by_author_id(ctx.author.id),
                                                            self.__handle_role_click__, self.__bis_callback__,
                                                            self.__purchase_callback__, self.__handle_leave_team__))

            self.team_manager.map_message_id_to_team(member_message.id, team, player)
            player.player_message_id = member_message.id
            player.player_author_id = ctx.author.id

        @self.client.command()
        async def join(ctx, uuid: str, *, player_name):
            if not isinstance(ctx.channel, discord.channel.DMChannel):
                await ctx.send("This command can only be used in DMs.")
                return

            if self.team_manager.get_team_by_uuid(uuid) is None:
                await ctx.send("That team does not exist.", delete_after=5)
                return

            team = self.team_manager.get_team_by_uuid(uuid)
            if ctx.author.id in team.__members:
                await ctx.send("You are already part of this team.", delete_after=5)
                return

            if not player_name:
                await ctx.send("Please enter a player team_name.", delete_after=5)
                return

            player = team.add_member(ctx.author.id, player_name)
            player.__player_name = player_name

            self.client.add_view(PlayerView(team.__members[ctx.author.id],
                                            self.__handle_role_click__, self.__bis_callback__,
                                            self.__purchase_callback__, self.__handle_leave_team__))
            member_message = await ctx.send(embed=PlayerInfoEmbed(team, player),
                                            view=PlayerView(team.__members[ctx.author.id],
                                                            self.__handle_role_click__, self.__bis_callback__,
                                                            self.__purchase_callback__, self.__handle_leave_team__))
            self.team_manager.map_message_id_to_team(member_message.id, team, player)
            player.player_message_id = member_message.id
            player.player_author_id = ctx.author.id
            await self.update_all_member_embeds(team)

        self.client.run(self.token)

    def __handle_on_ready__(self):
        print(f'{self.client.user} ready!')

    async def __handle_role_click__(self, interaction, role: str):
        team = self.team_manager.get_team_by_member(interaction.message.id)
        player = team.get_member_by_author_id(interaction.user.id)
        player.set_player_role(Role[role])
        await self.update_all_member_embeds(team)
        await interaction.response.edit_message(
            view=PlayerView(team.__members[interaction.user.id], self.__handle_role_click__, self.__bis_callback__,
                            self.__purchase_callback__, self.__handle_leave_team__))

    async def update_all_member_embeds(self, team: Team):
        for member in team.get_all_member_ids():
            player = team.get_member_by_author_id(member)
            author = player.get_author_id()
            message_id = player.get_message_id()
            channel = await self.client.fetch_user(author)
            message = await channel.fetch_message(message_id)
            await message.edit(embed=PlayerInfoEmbed(team, player))

    async def __handle_loot_priority_click__(self, interaction: discord.Interaction, priority: str):
        team = self.team_manager.get_team_by_leader(interaction.user.id)
        team.set_loot_priority(LootPriority[priority])
        await interaction.response.edit_message(
            view=ManagementView(team,
                                self.__handle_loot_priority_click__, self.__assign_loot_callback__,
                                self.__handle_disband_team__))
        await self.update_all_member_embeds(team)

    async def __handle_bis_finish__(self, interaction: discord.Interaction, bis, player_message_id: int):
        team = self.team_manager.get_team_by_member(player_message_id)
        player = team.get_member_by_author_id(interaction.user.id)
        player.gear_upgrades = bis
        player.is_editing_bis = False
        player.update_twines_and_coatings()
        await self.update_all_member_embeds(team)
        await interaction.response.send_message("Gear updated.", delete_after=5)
        await interaction.message.delete()

    async def __bis_callback__(self, interaction: discord.Interaction):
        team = self.team_manager.get_team_by_member(interaction.message.id)
        player = team.get_member_by_author_id(interaction.user.id)
        if player.is_editing_bis:
            await interaction.response.send_message("You are already editing your BiS gear. Please use the existing "
                                                    "interface.", delete_after=5)
        else:
            player.is_editing_bis = True
            await interaction.response.send_message(embed=BiSEmbed(team),
                                                    view=BiSView(player,
                                                                 self.__handle_bis_finish__,
                                                                 self.__handle_cancel_bis__,
                                                                 BIS_TIMEOUT - 1,
                                                                 interaction.message.id),
                                                    delete_after=BIS_TIMEOUT)

    async def __assign_loot_callback__(self, interaction: discord.Interaction):
        team = self.team_manager.get_team_by_leader(interaction.user.id)
        if team.is_assigning_loot:
            await interaction.response.send_message("You are already assigning loot. Please use the existing "
                                                    "interface.", delete_after=5)
            return
        team.is_assigning_loot = True
        await interaction.response.send_message(
            embed=AssignLootEmbed(team),
            view=AssignLootView(
                team,
                self.__handle_assign_loot_callback__,
                self.__handle_cancel_assign_loot__,
                PURCHASE_TIMEOUT - 1,
                interaction.message.id
            ),
            delete_after=PURCHASE_TIMEOUT)

    async def __handle_assign_loot_callback__(self, interaction: discord.Interaction, item: int, player: str):
        if item is None:
            await interaction.response.send_message("Please select an item.", delete_after=5)
            return

        if player is None:
            await interaction.response.send_message("Please select a player.", delete_after=5)
            return

        team = self.team_manager.get_team_by_leader(interaction.user.id)
        team.is_assigning_loot = False

        if item == 98 or item == 99:
            if item == 98 and team.__members[player].twines_needed - team.__members[player].twines_got <= 0:
                await interaction.response.send_message("This player does not need any more twines.", delete_after=5)
                return
            if item == 99 and team.__members[player].coatings_needed - team.__members[player].coatings_got <= 0:
                await interaction.response.send_message("This player does not need any more coatings.", delete_after=5)
                return

            if item == 98:
                team.__members[player].twines_got += 1
                await interaction.response.send_message(f"Assigned Twine to {team.__members[player].__player_name}.",
                                                        delete_after=5)
            else:
                team.__members[player].coatings_got += 1
                await interaction.response.send_message(f"Assigned Coating to {team.__members[player].__player_name}.",
                                                        delete_after=5)
            await self.update_all_member_embeds(team)
            await interaction.message.delete()
            return

        if item - 1 in team.__members[player].gear_owned:
            await interaction.response.send_message(f"{team.__members[player].__player_name} already has this item. "
                                                    f"Process aborted", delete_after=5)
        else:
            team.__members[player].gear_owned.append(item - 1)
            for member in team.__members:
                if member != player and team.__members[member].gear_upgrades[item - 1] != RaidUpgrade.NO:
                    if item > 6:
                        team.__members[member].pity += 4
                    elif item == Item.WEAPON or item == Item.BODY or item == Item.LEGS:
                        team.__members[member].pity += 8
                    else:
                        team.__members[member].pity += 6
            await interaction.response.send_message(f"{team.__members[player].__player_name} has been assigned the item.",
                                                    delete_after=5)
        await self.update_all_member_embeds(team)
        await interaction.message.delete()

    async def __handle_cancel_assign_loot__(self, interaction: discord.Interaction):
        team = self.team_manager.get_team_by_leader(interaction.user.id)
        team.is_assigning_loot = False
        await interaction.response.send_message("Loot assignment cancelled.", delete_after=5)
        await interaction.message.delete()

    async def __purchase_callback__(self, interaction: discord.Interaction):
        team = self.team_manager.get_team_by_leader(interaction.user.id)
        if team.__members[interaction.user.id].is_adding_item:
            await interaction.response.send_message("You are already adding an item. Please use the existing "
                                                    "interface.", delete_after=5)
        elif len([i for i in team.__members[interaction.user.id].gear_upgrades if i != RaidUpgrade.NO]) == 0:
            await interaction.response.send_message("There is no gear for you to log. Set up your BiS first.",
                                                    delete_after=5)
        else:
            team.__members[interaction.user.id].is_adding_item = True
            await interaction.response.send_message(embed=PlayerPurchaseEmbed(),
                                                    view=PlayerPurchaseView(team.__members[interaction.user.id],
                                                                            self.__handle_purchase_finish__,
                                                                            self.__handle_cancel_purchase__,
                                                                            PURCHASE_TIMEOUT - 1,
                                                                            interaction.message.id),
                                                    delete_after=PURCHASE_TIMEOUT)

    async def __handle_purchase_finish__(self, interaction: discord.Interaction, item: int, player_message_id: int):
        team = self.team_manager.get_team_by_member(player_message_id)
        player = team.__members[interaction.user.id]
        if item == 98:
            player.twines_got += 1
        elif item == 99:
            player.coatings_got += 1
        else:
            team.__members[interaction.user.id].gear_owned.append(item)
        player.is_adding_item = False
        await self.update_all_member_embeds(team)
        await interaction.response.send_message("Item logged.", delete_after=5)
        await interaction.message.delete()

    async def __handle_cancel_bis__(self, interaction: discord.Interaction, player_message_id: int):
        team = self.team_manager.get_team_by_member(player_message_id)
        team.__members[interaction.user.id].is_editing_bis = False
        await interaction.response.send_message("Action cancelled.", delete_after=5)
        await interaction.message.delete()

    async def __handle_cancel_purchase__(self, interaction: discord.Interaction, player_message_id: int):
        team = self.team_manager.get_team_by_member(player_message_id)
        team.__members[interaction.user.id].is_adding_item = False
        await interaction.response.send_message("Action cancelled.", delete_after=5)
        await interaction.message.delete()

    async def __handle_leave_team__(self, interaction: discord.Interaction):
        team = self.team_manager.get_team_by_member(interaction.message.id)
        if self.team_manager.get_team_by_leader(interaction.user.id) == team:
            await interaction.response.send_message("You cannot leave your own team. Please disband the "
                                                    "team if you wish to abandon it.", delete_after=5)
            return
        player = team.get_member_by_author_id(interaction.user.id)
        self.team_manager.leave_team(interaction.message.id, team, player)
        await interaction.response.send_message("You have left the team.", delete_after=10)
        await interaction.message.delete()
        await self.update_all_member_embeds(team)

    async def __handle_disband_team__(self, interaction: discord.Interaction):
        team = self.team_manager.get_team_by_leader(interaction.user.id)
        for member in team.get_all_member_ids():
            player = team.get_member_by_author_id(member)
            # delete player view
            author = player.get_author_id()
            message_id = player.get_message_id()
            channel = await self.client.fetch_user(author)
            message = await channel.fetch_message(message_id)
            await message.delete()
        # delete leader index and message, then delete team
        await interaction.message.delete()
        self.team_manager.delete_team(team, team.get_member_by_author_id(interaction.user.id))
        await interaction.response.send_message("Team disbanded.", delete_after=10)

    def on_disconnect(self):
        with open('TeamData.obj', 'wb') as f:
            pickle.dump(self.team_manager, f)
