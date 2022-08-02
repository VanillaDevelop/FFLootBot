import asyncio
import discord

from Bot.Embeds.AssignLootEmbed import AssignLootEmbed
from Bot.Player import Player, Item, RaidUpgrade
from Bot.Team import Team


class AssignLootView(discord.ui.View):
    def __init__(self, team: Team, assign_callback: callable, cancel_callback: callable, timeout: int,
                 player_message_id: int, item: int = None, player: int = None):
        super().__init__()
        self.team = team
        self.assign_callback = assign_callback
        self.cancel_callback = cancel_callback
        self.timeout = timeout
        self.player_message_id = player_message_id
        self.item = item
        self.player = player
        asyncio.create_task(self.timeout_func())

        dropdown_items = discord.ui.Select()
        dropdown_items.custom_id = "SELECT_ITEM"
        for slot in Item:
            dropdown_items.add_option(label=slot.name.capitalize(), value=slot.name,
                                      default=self.item is not None and self.item == slot.value)
        dropdown_items.add_option(label="Twine", value=str(98),
                                  default=self.item == 98)
        dropdown_items.add_option(label="Coating", value=str(99),
                                  default=self.item == 99)
        dropdown_items.callback = lambda interaction: self.change_item(interaction, dropdown_items.values[0])

        self.add_item(dropdown_items)

        dropdown_players = discord.ui.Select()
        for player in self.team.members:
            dropdown_players.add_option(label=team.members[player].player_name, value=str(player),
                                        default=self.player == player)
        dropdown_players.callback = lambda interaction: self.change_player(interaction, dropdown_players.values[0])
        self.add_item(dropdown_players)

        btn_cancel = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger)
        btn_cancel.callback = lambda ctx: self.cancel_callback(ctx)
        self.add_item(btn_cancel)

        btn_assign = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.success)
        btn_assign.callback = lambda ctx: self.assign_callback(ctx, self.item, self.player)
        self.add_item(btn_assign)

    async def timeout_func(self):
        await asyncio.sleep(self.timeout)
        self.team.is_assigning_loot = False
        self.disable_all_items()

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

    async def change_player(self, interaction, player):
        self.player = int(player)
        await interaction.response.defer()
