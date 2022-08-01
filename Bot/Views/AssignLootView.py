import asyncio
import discord

from Bot.Player import Player, Item, RaidUpgrade
from Bot.Team import Team


class AssignLootView(discord.ui.View):
    def __init__(self, team: Team, assign_callback: callable, cancel_callback: callable, timeout: int,
                 player_message_id: int):
        super().__init__()
        self.team = team
        self.assign_callback = assign_callback
        self.cancel_callback = cancel_callback
        self.timeout = timeout
        self.player_message_id = player_message_id
        self.item = None
        self.player = None
        asyncio.create_task(self.timeout_func())

        dropdown_items = discord.ui.Select()
        for slot in Item:
            dropdown_items.add_option(label=slot.name.capitalize(), value=slot.name)
        dropdown_items.callback = lambda interaction: self.change_item(interaction, dropdown_items.values[0])
        self.add_item(dropdown_items)

        dropdown_players = discord.ui.Select()
        for player in self.team.members:
            dropdown_players.add_option(label=team.members[player].player_name, value=str(player))
        dropdown_players.callback = lambda interaction: self.change_player(interaction, dropdown_players.values[0])
        self.add_item(dropdown_players)

        btn_cancel = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger)
        btn_cancel.callback = lambda ctx: self.cancel_callback(ctx, self.player_message_id)
        self.add_item(btn_cancel)

        btn_assign = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.success)
        btn_assign.callback = lambda ctx: self.assign_callback(ctx, self.item, self.player, self.player_message_id)
        self.add_item(btn_assign)

    async def timeout_func(self):
        await asyncio.sleep(self.timeout)
        self.team.is_assigning_loot = False
        self.disable_all_items()

    async def change_item(self, interaction: discord.Interaction, item):
        self.item = Item[item]
        await interaction.response.defer()

    async def change_player(self, interaction, player):
        self.player = self.team.members[int(player)]
        await interaction.response.defer()