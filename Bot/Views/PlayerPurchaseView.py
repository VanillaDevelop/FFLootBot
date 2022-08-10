import discord

from Bot.Player import Player, Item
from Bot.Views.TemporaryView import TemporaryView


# view for a player to purchase a gear piece
class PlayerPurchaseView(TemporaryView):
    def __init__(self, player: Player, purchase_callback: callable, cancel_callback: callable, timeout: int,
                 player_message_id: int):
        super().__init__(timeout, self.timeout_func)
        self.player = player
        self.purchase_callback = purchase_callback
        self.cancel_callback = cancel_callback
        self.add_item_options()
        self.player_message_id = player_message_id

    async def timeout_func(self):
        self.player.__is_adding_item = False
        self.disable_all_items()

    def add_item_options(self):
        for slot in Item:
            if self.player.needs_item(slot):
                btn_slot = discord.ui.Button(label=f"{str(slot)}", style=discord.ButtonStyle.success)
                btn_slot.callback = lambda ctx, e=slot.value: self.purchase_callback(ctx, e, self.player_message_id)
                self.add_item(btn_slot)
        if self.player.get_remaining_twine_count() > 0:
            btn_slot = discord.ui.Button(label="Twine", style=discord.ButtonStyle.success)
            btn_slot.callback = lambda ctx: self.purchase_callback(ctx, 98, self.player_message_id)
            self.add_item(btn_slot)
        if self.player.get_remaining_coating_count() > 0:
            btn_slot = discord.ui.Button(label="Coating", style=discord.ButtonStyle.success)
            btn_slot.callback = lambda ctx: self.purchase_callback(ctx, 99, self.player_message_id)
            self.add_item(btn_slot)
        btn_cancel = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger)
        btn_cancel.callback = lambda ctx: self.cancel_callback(ctx, self.player_message_id)
        self.add_item(btn_cancel)
