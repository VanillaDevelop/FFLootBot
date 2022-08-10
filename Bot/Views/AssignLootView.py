import discord

from Bot.Embeds.AssignLootEmbed import AssignLootEmbed
from Bot.Player import Item
from Bot.Team import Team
from Bot.Views.TemporaryView import TemporaryView


# view for assigning loot to team members
class AssignLootView(TemporaryView):
    def __init__(self, team: Team, assign_callback: callable, cancel_callback: callable, timeout: int,
                 player_message_id: int, item: int = None, player: int = None):
        super().__init__(timeout, lambda: self.timeout_func)
        self.team = team
        self.assign_callback = assign_callback
        self.cancel_callback = cancel_callback
        self.player_message_id = player_message_id
        self.item = item
        self.player = player

        dropdown_items = discord.ui.Select()
        dropdown_items.custom_id = "SELECT_ITEM"
        for slot in Item:
            dropdown_items.add_option(label=str(slot), value=slot.name,
                                      default=self.item is not None and self.item == slot.value)
        dropdown_items.add_option(label="Twine", value=str(98),
                                  default=self.item == 98)
        dropdown_items.add_option(label="Coating", value=str(99),
                                  default=self.item == 99)
        dropdown_items.callback = lambda interaction: self.change_item(interaction, dropdown_items.values[0])
        self.add_item(dropdown_items)

        if item is None:
            eligible_players = []
        elif item == 98:
            eligible_players = [player_id for player_id in self.team.get_all_member_ids()
                                if team.get_member_by_author_id(player_id).get_remaining_twine_count() > 0]
        elif item == 99:
            eligible_players = [player_id for player_id in self.team.get_all_member_ids()
                                if team.get_member_by_author_id(player_id).get_remaining_coating_count() > 0]
        else:
            eligible_players = [player_id for player_id in self.team.get_all_member_ids()
                                if team.get_member_by_author_id(player_id).needs_item(Item(item))]
        if item is not None and len(eligible_players) > 0:
            dropdown_players = discord.ui.Select(
                placeholder="Select an eligible player."
            )
            for player in eligible_players:
                dropdown_players.add_option(label=team.get_member_by_author_id(player).get_player_name(),
                                            value=str(player), default=self.player == player)
            dropdown_players.callback = lambda interaction: self.change_player(interaction, dropdown_players.values[0])
            self.add_item(dropdown_players)

        btn_cancel = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger)
        btn_cancel.callback = lambda ctx: self.cancel_callback(ctx)
        self.add_item(btn_cancel)

        btn_assign = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.success)
        btn_assign.callback = lambda ctx: self.assign_callback(ctx, self.item, self.player)
        self.add_item(btn_assign)

    # function called when this view times out
    async def timeout_func(self):
        self.team.__is_assigning_loot = False
        self.disable_all_items()

    # callback when the item dropdown is changed
    async def change_item(self, interaction: discord.Interaction, item):
        if item == "98" or item == "99":
            self.item = int(item)
        else:
            self.item = Item[item].value
        await interaction.response.edit_message(embed=AssignLootEmbed(self.team, self.item),
                                                view=AssignLootView(self.team, self.assign_callback,
                                                                    self.cancel_callback, self.timeout,
                                                                    self.player_message_id, self.item,
                                                                    self.player))

    # callback when the player dropdown is changed
    async def change_player(self, interaction, player):
        self.player = int(player)
        await interaction.response.defer()
