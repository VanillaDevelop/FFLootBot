import asyncio
import discord

from Bot.Player import Player, Item, RaidUpgrade


class PlayerPurchaseView(discord.ui.View):
    def __init__(self, player: Player, purchase_callback: callable, cancel_callback: callable, timeout: int,
                 player_message_id: int):
        super().__init__()
        self.player = player
        self.purchase_callback = purchase_callback
        self.cancel_callback = cancel_callback
        self.add_item_options()
        self.timeout = timeout
        self.player_message_id = player_message_id
        asyncio.create_task(self.timeout_func())

    async def timeout_func(self):
        await asyncio.sleep(self.timeout)
        self.player.is_adding_item = False
        self.disable_all_items()

    def add_item_options(self):
        for (i, slot) in enumerate(Item):
            if self.player.gear_upgrades[i] != RaidUpgrade.NO:
                btn_slot = discord.ui.Button(label=f"{slot.name.capitalize()}", style=discord.ButtonStyle.success)
                btn_slot.callback = lambda ctx, e=i: self.purchase_callback(ctx, e, self.player_message_id)
                self.add_item(btn_slot)
        if self.player.twines_needed - self.player.twines_got > 0:
            btn_slot = discord.ui.Button(label="Twine", style=discord.ButtonStyle.success)
            btn_slot.callback = lambda ctx: self.purchase_callback(ctx, 98, self.player_message_id)
            self.add_item(btn_slot)
        if self.player.coatings_needed - self.player.coatings_got > 0:
            btn_slot = discord.ui.Button(label="Coating", style=discord.ButtonStyle.success)
            btn_slot.callback = lambda ctx: self.purchase_callback(ctx, 99, self.player_message_id)
            self.add_item(btn_slot)
        btn_cancel = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger)
        btn_cancel.callback = lambda ctx: self.cancel_callback(ctx, self.player_message_id)
        self.add_item(btn_cancel)
