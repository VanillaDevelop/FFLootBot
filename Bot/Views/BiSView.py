import asyncio

import discord

from Bot.Player import Player, Item, RaidUpgrade


class BiSView(discord.ui.View):
    def __init__(self, player: Player, bis_finish_callback: callable,
                 bis_cancel_callback: callable, timeout: int, player_message_id: int):
        super().__init__()
        self.bis_items = player.__gear_upgrades.copy()
        self.player = player
        self.finish_callback = bis_finish_callback
        self.cancel_callback = bis_cancel_callback
        self.add_all_items()
        self.timeout = timeout
        self.player_message_id = player_message_id
        asyncio.create_task(self.timeout_func())

    async def timeout_func(self):
        await asyncio.sleep(self.timeout)
        self.player.__is_editing_bis = False
        self.disable_all_items()

    async def change_gear(self, interaction: discord.Interaction, slot: int):
        self.bis_items[slot] = 1 + (self.bis_items[slot]) % 4
        self.clear_items()
        self.add_all_items()
        await interaction.response.edit_message(view=self)

    def add_all_items(self):
        for (i, slot) in enumerate(Item):
            btn_slot = discord.ui.Button(label=f"{slot.__name.capitalize()}: {str(RaidUpgrade(self.bis_items[i]))}",
                                         style=discord.ButtonStyle.secondary)
            btn_slot.callback = lambda ctx, e=i: self.change_gear(ctx, e)
            self.add_item(btn_slot)

        btn_cancel = discord.ui.Button(label="Cancel", row=4, style=discord.ButtonStyle.danger)
        btn_cancel.callback = lambda ctx: self.cancel_callback(ctx, self.player_message_id)
        self.add_item(btn_cancel)

        btn_finish = discord.ui.Button(label="Confirm", row=4, style=discord.ButtonStyle.success)
        btn_finish.callback = lambda ctx: self.finish_callback(ctx, self.bis_items, self.player_message_id)
        self.add_item(btn_finish)
