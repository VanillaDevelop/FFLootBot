import discord
from discord import ChannelType

from Bot.Embeds.AssignLootEmbed import AssignLootEmbed
from Bot.Embeds.BiSEmbed import BiSEmbed
from Bot.Embeds.ManagementEmbed import ManagementEmbed
from Bot.Embeds.PlayerInfoEmbed import PlayerInfoEmbed
from Bot.Embeds.PlayerPurchaseEmbed import PlayerPurchaseEmbed
from Bot.Player import Item, Role
from Bot.Team import Team, LootPriority
from Bot.TeamManager import TeamManager
from Bot.Views.AssignLootView import AssignLootView
from Bot.Views.BiSView import BiSView
from Bot.Views.ManagementView import ManagementView
from Bot.Views.PlayerPurchaseView import PlayerPurchaseView
from Bot.Views.PlayerView import PlayerView

BIS_TIMEOUT = 600
PURCHASE_TIMEOUT = 180


class TeamCog(discord.Cog):
    def __init__(self, bot, team_manager=None):
        self.bot = bot
        self.team_manager = TeamManager() if team_manager is None else team_manager

        # load persistent views for each team and player that was stored
        for team_id in self.team_manager.get_all_team_ids():
            team = self.team_manager.get_team_by_uuid(team_id)
            self.bot.add_view(ManagementView(team,
                                             self.__handle_loot_priority_click__,
                                             self.__assign_loot_callback__,
                                             self.__handle_disband_team__))
            for player_id in team.get_all_member_ids():
                player = team.get_member_by_author_id(player_id)
                self.bot.add_view(PlayerView(player,
                                             self.__handle_role_change__, self.__bis_callback__,
                                             self.__purchase_callback__, self.__handle_leave_team__))

    def get_team_manager(self) -> TeamManager:
        return self.team_manager

    # event that runs when the "create [team_name] [player_name]" command is sent
    @discord.application_command()
    async def create(self, ctx, team_name: str, *, player_name: str):
        """
        Create a team. This command can only be used in DMs.

        :param ctx: The calling context
        :param team_name: The name of the team.
        :param player_name: The personal name of the team leader.
        """
        if ctx.channel.type is not ChannelType.private:
            await ctx.respond("This command can only be used in DMs.")
            return

        if self.team_manager.get_team_by_leader(ctx.author.id):
            await ctx.respond("You already have an active team.", delete_after=5)
            return

        if not player_name:
            await ctx.respond("Please enter a player name.", delete_after=5)
            return

        if not team_name:
            await ctx.respond("Please enter a team name.", delete_after=5)
            return

        # create team and add player to team
        team = self.team_manager.create_team(team_name, ctx.author.id)
        player = team.add_member(ctx.author.id, player_name)

        # add persistent views for the created team and player
        self.bot.add_view(ManagementView(team, self.__handle_loot_priority_click__,
                                         self.__assign_loot_callback__,
                                         self.__handle_disband_team__))
        self.bot.add_view(PlayerView(team.get_member_by_author_id(ctx.author.id),
                                     self.__handle_role_change__, self.__bis_callback__,
                                     self.__purchase_callback__, self.__handle_leave_team__))

        # send the management view (leader only)
        await ctx.respond(embed=ManagementEmbed(team),
                          view=ManagementView(team, self.__handle_loot_priority_click__,
                                              self.__assign_loot_callback__,
                                              self.__handle_disband_team__))

        # send the player view (everyone)
        member_message = await ctx.respond(embed=PlayerInfoEmbed(team, player),
                                           view=PlayerView(player,
                                                           self.__handle_role_change__, self.__bis_callback__,
                                                           self.__purchase_callback__, self.__handle_leave_team__))

        # link the member message id to the team
        self.team_manager.map_message_id_to_team(ctx.author.id, member_message.id, team, player)

    # event that runs when the "join [team_uuid] [player_name]" command is sent
    @discord.application_command()
    async def join(self, ctx, uuid: str, *, player_name: str):
        """
        Join a team. This command can only be used in DMs.

        :param ctx: The calling context.
        :param uuid: The unique identifier of the team. Ask your team leader for this.
        :param player_name: The personal name of the player joining the team.
        """
        if ctx.channel.type is not ChannelType.private:
            await ctx.respond("This command can only be used in DMs.")
            return

        if self.team_manager.get_team_by_uuid(uuid) is None:
            await ctx.respond("That team does not exist.", delete_after=5)
            return

        team = self.team_manager.get_team_by_uuid(uuid)
        if team.get_member_by_author_id(ctx.author.id):
            await ctx.respond("You are already part of this team.", delete_after=5)
            return

        if not player_name:
            await ctx.respond("Please enter a player name.", delete_after=5)
            return

        # add player to the team
        player = team.add_member(ctx.author.id, player_name)
        # add persistent view for the player
        self.bot.add_view(PlayerView(player,
                                     self.__handle_role_change__, self.__bis_callback__,
                                     self.__purchase_callback__, self.__handle_leave_team__))
        # send the player view
        member_message = await ctx.respond(embed=PlayerInfoEmbed(team, player),
                                           view=PlayerView(player,
                                                           self.__handle_role_change__, self.__bis_callback__,
                                                           self.__purchase_callback__, self.__handle_leave_team__))
        # link the member message id to the team
        self.team_manager.map_message_id_to_team(ctx.author.id, member_message.id, team, player)
        # update the player view of all players in the team
        await self.update_all_member_embeds(team)

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
            channel = await self.bot.fetch_user(author)
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
                                                    f"has been assigned the {str(item)} piece.",
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
            channel = await self.bot.fetch_user(author)
            message = await channel.fetch_message(message_id)
            await message.delete()
        # delete leader index and message, then delete team
        await interaction.message.delete()
        self.team_manager.delete_team(team, team.get_member_by_author_id(interaction.user.id))
        await interaction.response.send_message("Team disbanded.", delete_after=10)
