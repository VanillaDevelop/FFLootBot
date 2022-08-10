import discord

from Bot.Player import Player, Item, RaidUpgrade
from Bot.Views.TemporaryView import TemporaryView


# view for setting up a player's BiS
class BiSView(TemporaryView):
    def __init__(self, player: Player, bis_finish_callback: callable,
                 bis_cancel_callback: callable, timeout: int, player_message_id: int):
        super().__init__(timeout, lambda: self.player.set_is_editing_bis(False))
        self.bis_items = player.get_bis().copy()
        self.player = player
        self.finish_callback = bis_finish_callback
        self.cancel_callback = bis_cancel_callback
        self.add_all_items()
        self.player_message_id = player_message_id

    # add a button for each item that when clicked increases the raid upgrade level for this item
    def add_all_items(self):
        for slot in Item:
            btn_slot = discord.ui.Button(label=f"{str(slot)}: "
                                               f"{str(self.bis_items[slot.value-1])}",
                                         style=discord.ButtonStyle.secondary)
            btn_slot.callback = lambda ctx, e=slot: self.change_gear(ctx, e)
            self.add_item(btn_slot)

        btn_cancel = discord.ui.Button(label="Cancel", row=4, style=discord.ButtonStyle.danger)
        btn_cancel.callback = lambda ctx: self.cancel_callback(ctx, self.player_message_id)
        self.add_item(btn_cancel)

        btn_finish = discord.ui.Button(label="Confirm", row=4, style=discord.ButtonStyle.success)
        btn_finish.callback = lambda ctx: self.finish_callback(ctx, self.bis_items, self.player_message_id)
        self.add_item(btn_finish)

    # callback when user clicks one of the buttons
    async def change_gear(self, interaction: discord.Interaction, slot: Item):
        self.bis_items[slot.value-1] = RaidUpgrade(1 + (self.bis_items[slot.value-1]) % 4)
        self.clear_items()
        self.add_all_items()
        await interaction.response.edit_message(view=self)

