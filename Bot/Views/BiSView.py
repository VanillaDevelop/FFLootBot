import discord

from Bot.Player import Player, Role, Item, RaidUpgrade
from Bot.Team import Team


class BiSView(discord.ui.View):
    def __init__(self, player: Player, bis_finish_callback: callable):
        super().__init__()
        self.bis_items = player.gear_upgrades.copy()
        self.player = player
        self.finish_callback = bis_finish_callback
        self.add_all_items()

    async def change_gear(self, interaction: discord.Interaction, slot: int):
        self.bis_items[slot] = 1 + (self.bis_items[slot]) % 4
        self.clear_items()
        self.add_all_items()
        await interaction.response.edit_message(view=self)

    def add_all_items(self):
        for (i, slot) in enumerate(Item):
            if self.bis_items[i] == RaidUpgrade.NO:
                lvl = "No Upgrade"
            elif self.bis_items[i] == RaidUpgrade.STATS:
                lvl = "Same Stats"
            elif self.bis_items[i] == RaidUpgrade.SUBSTATS_MINOR:
                lvl = "Minor Substat Upgrade"
            elif self.bis_items[i] == RaidUpgrade.SUBSTATS_MAJOR:
                lvl = "Major Substat Upgrade"

            btn_slot = discord.ui.Button(label=f"{slot.name.capitalize()}: {lvl}", style=discord.ButtonStyle.secondary)
            btn_slot.callback = lambda ctx, e=i: self.change_gear(ctx, e)
            self.add_item(btn_slot)

        btn_finish = discord.ui.Button(label="Confirm", row=4, style=discord.ButtonStyle.success)
        btn_finish.callback = lambda ctx: self.finish_callback(ctx, self.bis_items)
        self.add_item(btn_finish)
