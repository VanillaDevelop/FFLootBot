import atexit
import os
import pickle

import discord
import discord.types.components
from discord.ext import commands

from Bot.Embeds.AssignLootEmbed import AssignLootEmbed
from Bot.Embeds.BiSEmbed import BiSEmbed
from Bot.Embeds.InfoEmbed import InfoEmbed
from Bot.Embeds.ManagementEmbed import ManagementEmbed
from Bot.Embeds.PlayerInfoEmbed import PlayerInfoEmbed
from Bot.Embeds.PlayerPurchaseEmbed import PlayerPurchaseEmbed
from Bot.Player import Role, Item
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
        # manages teams
        self.team_manager = TeamManager()

        # event that runs when the bot is started
        @self.client.event
        async def on_ready():
            print(f'{self.client.user} ready!')
            atexit.register(self.on_disconnect)

            # if config file exists and bot is set to use stored information, load config file
            if LOAD_CONFIG_FILE and os.path.exists('TeamData.obj'):
                with open('TeamData.obj', 'rb') as f:
                    self.team_manager = pickle.load(f)

                # load persistent views for each team and player that was stored
                for team_id in self.team_manager.get_all_team_ids():
                    team = self.team_manager.get_team_by_uuid(team_id)
                    self.client.add_view(ManagementView(team,
                                                        self.__handle_loot_priority_click__,
                                                        self.__assign_loot_callback__,
                                                        self.__handle_disband_team__))
                    for player_id in team.get_all_member_ids():
                        player = team.get_member_by_author_id(player_id)
                        self.client.add_view(PlayerView(player,
                                                        self.__handle_role_change__, self.__bis_callback__,
                                                        self.__purchase_callback__, self.__handle_leave_team__))

        # event that runs when the "info" command is sent
        @self.client.command()
        async def info(ctx):
            await ctx.send(embed=InfoEmbed(COMMAND_PREFIX))

        # event that runs when the "create [team_name] [player_name]" command is sent
        @self.client.command()
        async def create(ctx, team_name: str, *, player_name: str):
            if not isinstance(ctx.channel, discord.channel.DMChannel):
                await ctx.send("This command can only be used in DMs.")
                return

            if self.team_manager.get_team_by_leader(ctx.author.id):
                await ctx.send("You already have an active team.", delete_after=5)
                return

            if not player_name:
                await ctx.send("Please enter a player name.", delete_after=5)
                return

            if not team_name:
                await ctx.send("Please enter a team name.", delete_after=5)
                return

            # create team and add player to team
            team = self.team_manager.create_team(team_name, ctx.author.id)
            player = team.add_member(ctx.author.id, player_name)

            # add persistent views for the created team and player
            self.client.add_view(ManagementView(team, self.__handle_loot_priority_click__,
                                                self.__assign_loot_callback__,
                                                self.__handle_disband_team__))
            self.client.add_view(PlayerView(team.get_member_by_author_id(ctx.author.id),
                                            self.__handle_role_change__, self.__bis_callback__,
                                            self.__purchase_callback__, self.__handle_leave_team__))

            # send the management view (leader only)
            await ctx.send(embed=ManagementEmbed(team, COMMAND_PREFIX),
                           view=ManagementView(team, self.__handle_loot_priority_click__,
                                               self.__assign_loot_callback__,
                                               self.__handle_disband_team__))

            # send the player view (everyone)
            member_message = await ctx.send(embed=PlayerInfoEmbed(team, player),
                                            view=PlayerView(player,
                                                            self.__handle_role_change__, self.__bis_callback__,
                                                            self.__purchase_callback__, self.__handle_leave_team__))

            # link the member message id to the team
            self.team_manager.map_message_id_to_team(ctx.author.id, member_message.id, team, player)

        # event that runs when the "join [team_uuid] [player_name]" command is sent
        @self.client.command()
        async def join(ctx, uuid: str, *, player_name: str):
            if not isinstance(ctx.channel, discord.channel.DMChannel):
                await ctx.send("This command can only be used in DMs.")
                return

            if self.team_manager.get_team_by_uuid(uuid) is None:
                await ctx.send("That team does not exist.", delete_after=5)
                return

            team = self.team_manager.get_team_by_uuid(uuid)
            if team.get_member_by_author_id(ctx.author.id):
                await ctx.send("You are already part of this team.", delete_after=5)
                return

            if not player_name:
                await ctx.send("Please enter a player name.", delete_after=5)
                return

            # add player to the team
            player = team.add_member(ctx.author.id, player_name)
            # add persistent view for the player
            self.client.add_view(PlayerView(player,
                                            self.__handle_role_change__, self.__bis_callback__,
                                            self.__purchase_callback__, self.__handle_leave_team__))
            # send the player view
            member_message = await ctx.send(embed=PlayerInfoEmbed(team, player),
                                            view=PlayerView(player,
                                                            self.__handle_role_change__, self.__bis_callback__,
                                                            self.__purchase_callback__, self.__handle_leave_team__))
            # link the member message id to the team
            self.team_manager.map_message_id_to_team(ctx.author.id, member_message.id, team, player)
            # update the player view of all players in the team
            await self.update_all_member_embeds(team)

        # run client
        self.client.run(self.token)

    # callback for when a player changes their role
    async def __handle_role_change__(self, interaction: discord.Interaction, role: str):
        team = self.team_manager.get_team_by_member(interaction.message.id)
        player = team.get_member_by_author_id(interaction.user.id)
        player.set_player_role(Role[role])
        await self.update_all_member_embeds(team)
        await interaction.response.edit_message(
            view=PlayerView(player, self.__handle_role_change__, self.__bis_callback__,
                            self.__purchase_callback__, self.__handle_leave_team__))

    # updates all player embeds for a given team
    async def update_all_member_embeds(self, team: Team):
        for member in team.get_all_member_ids():
            player = team.get_member_by_author_id(member)
            author = player.get_author_id()
            message_id = player.get_message_id()
            channel = await self.client.fetch_user(author)
            message = await channel.fetch_message(message_id)
            await message.edit(embed=PlayerInfoEmbed(team, player))

    # callback for when a team leader changes the general loot priority
    async def __handle_loot_priority_click__(self, interaction: discord.Interaction, priority: str):
        team = self.team_manager.get_team_by_leader(interaction.user.id)
        team.set_loot_priority(LootPriority[priority])
        await interaction.response.edit_message(
            view=ManagementView(team,
                                self.__handle_loot_priority_click__, self.__assign_loot_callback__,
                                self.__handle_disband_team__))
        await self.update_all_member_embeds(team)

    # callback for when a team member finishes editing their gear
    async def __handle_bis_finish__(self, interaction: discord.Interaction, bis, player_message_id: int):
        team = self.team_manager.get_team_by_member(player_message_id)
        player = team.get_member_by_author_id(interaction.user.id)
        player.update_bis(bis)
        player.set_is_editing_bis(False)
        await self.update_all_member_embeds(team)
        await interaction.response.send_message("Gear updated.", delete_after=5)
        await interaction.message.delete()

    # callback for when a team member clicks the button to update their BiS gear
    async def __bis_callback__(self, interaction: discord.Interaction):
        team = self.team_manager.get_team_by_member(interaction.message.id)
        player = team.get_member_by_author_id(interaction.user.id)
        if player.get_is_editing_bis():
            await interaction.response.send_message("You are already editing your BiS gear. Please use the existing "
                                                    "interface.", delete_after=5)
        else:
            player.set_is_editing_bis(True)
            await interaction.response.send_message(embed=BiSEmbed(team),
                                                    view=BiSView(player,
                                                                 self.__handle_bis_finish__,
                                                                 self.__handle_cancel_bis__,
                                                                 BIS_TIMEOUT - 1,
                                                                 interaction.message.id),
                                                    delete_after=BIS_TIMEOUT)

    # callback for when the team leader clicks the button to assign loot
    async def __assign_loot_callback__(self, interaction: discord.Interaction):
        team = self.team_manager.get_team_by_leader(interaction.user.id)
        if team.get_is_assigning_loot():
            await interaction.response.send_message("You are already assigning loot. Please use the existing "
                                                    "interface.", delete_after=5)
            return
        team.set_is_assigning_loot(True)
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

    # callback for when the team leader clicks the button to confirm the loot assignment
    async def __handle_assign_loot_callback__(self, interaction: discord.Interaction, item: int, member_id: int):
        if item is None:
            await interaction.response.send_message("Please select an item.", delete_after=5)
            return

        if member_id is None:
            await interaction.response.send_message("Please select a player.", delete_after=5)
            return

        team = self.team_manager.get_team_by_leader(interaction.user.id)
        team.set_is_assigning_loot(False)
        player = team.get_member_by_author_id(member_id)

        # handle twines and coatings
        if item == 98 and player.get_remaining_twine_count() <= 0:
            await interaction.response.send_message("This player does not need any more twines.", delete_after=5)
            return
        elif item == 98:
            player.give_item(98)
            await interaction.response.send_message(f"Assigned Twine to {player.get_player_name()}.",
                                                    delete_after=5)
        elif item == 99 and player.get_remaining_coating_count() <= 0:
            await interaction.response.send_message("This player does not need any more coatings.", delete_after=5)
            return
        elif item == 99:
            player.give_item(99)
            await interaction.response.send_message(f"Assigned Coating to {player.get_player_name()}.",
                                                    delete_after=5)
        if item >= 98:
            await self.update_all_member_embeds(team)
            await interaction.message.delete()
            return

        # handle gear pieces
        item = Item(item)
        if not player.needs_item(item):
            await interaction.response.send_message(f"{player.get_player_name()} does not need this item. "
                                                    f"Process aborted", delete_after=5)
        else:
            player.give_item(item.value)
            team.give_pity(item, player)
            await interaction.response.send_message(f"{player.get_player_name()} "
                                                    f"has been assigned the {item.name} piece.",
                                                    delete_after=5)
        await self.update_all_member_embeds(team)
        await interaction.message.delete()

    # callback for when the team leader clicks the button to cancel the loot assignment
    async def __handle_cancel_assign_loot__(self, interaction: discord.Interaction):
        team = self.team_manager.get_team_by_leader(interaction.user.id)
        team.set_is_assigning_loot(False)
        await interaction.response.send_message("Loot assignment cancelled.", delete_after=5)
        await interaction.message.delete()

    # callback for when a team member clicks the button to purchase a gear piece
    async def __purchase_callback__(self, interaction: discord.Interaction):
        team = self.team_manager.get_team_by_member(interaction.message.id)
        player = team.get_member_by_author_id(interaction.user.id)
        if player.get_is_adding_item():
            await interaction.response.send_message("You are already adding an item. Please use the existing "
                                                    "interface.", delete_after=5)
        elif (len(player.get_unowned_gear()) == 0
                and player.get_remaining_twine_count() <= 0
                and player.get_remaining_coating_count() <= 0):
            await interaction.response.send_message("There is no gear for you to log. Set up your BiS first.",
                                                    delete_after=5)
        else:
            player.set_is_adding_item(True)
            await interaction.response.send_message(embed=PlayerPurchaseEmbed(),
                                                    view=PlayerPurchaseView(player,
                                                                            self.__handle_purchase_finish__,
                                                                            self.__handle_cancel_purchase__,
                                                                            PURCHASE_TIMEOUT - 1,
                                                                            interaction.message.id),
                                                    delete_after=PURCHASE_TIMEOUT)

    # callback for when a team member clicks the button to confirm the purchase of an item
    async def __handle_purchase_finish__(self, interaction: discord.Interaction, item: int, player_message_id: int):
        team = self.team_manager.get_team_by_member(player_message_id)
        player = team.get_member_by_author_id(interaction.user.id)
        player.give_item(item)
        player.set_is_adding_item(False)
        await self.update_all_member_embeds(team)
        await interaction.response.send_message("Item logged.", delete_after=5)
        await interaction.message.delete()

    # callback for when a team member clicks the button to cancel the BiS setup
    async def __handle_cancel_bis__(self, interaction: discord.Interaction, player_message_id: int):
        team = self.team_manager.get_team_by_member(player_message_id)
        player = team.get_member_by_author_id(interaction.user.id)
        player.set_is_editing_bis(False)
        await interaction.response.send_message("Action cancelled.", delete_after=5)
        await interaction.message.delete()

    # callback for when a team member clicks the button to cancel the purchase of an item
    async def __handle_cancel_purchase__(self, interaction: discord.Interaction, player_message_id: int):
        team = self.team_manager.get_team_by_member(player_message_id)
        player = team.get_member_by_author_id(interaction.user.id)
        player.set_is_adding_item(False)
        await interaction.response.send_message("Action cancelled.", delete_after=5)
        await interaction.message.delete()

    # callback for when a team member clicks the button to leave the team
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

    # callback for when a team leader clicks the button to disband the team
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

    # callback before the bot exits (stores the current team manager data)
    def on_disconnect(self):
        with open('TeamData.obj', 'wb') as f:
            pickle.dump(self.team_manager, f)
