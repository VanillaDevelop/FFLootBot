import discord
from Bot.Team import LootPriority, Team


class ManagementView(discord.ui.View):
    def __init__(self, team: Team, loot_select_callback: callable):
        super().__init__()
        select_loot_distribution = discord.ui.Select(
            options=[
                discord.SelectOption(
                    label="Loot Priority: DPS",
                    value=LootPriority.DPS.name,
                    description="Distribute loot to DPS first, according to highest stat gain.",
                    default=team.loot_priority == LootPriority.DPS
                ),
                discord.SelectOption(
                    label="Loot Priority: Equal",
                    value=LootPriority.EQUAL.name,
                    description="Distribute loot to all players, "
                                "prioritizing those who have received the least loot so far.",
                    default=team.loot_priority == LootPriority.EQUAL
                ),
                discord.SelectOption(
                    label="Loot Priority: None",
                    value=LootPriority.NONE.name,
                    description="Do not prioritize loot distribution.",
                    default=team.loot_priority == LootPriority.NONE
                )],
            placeholder="Select loot distribution priority")
        select_loot_distribution.callback = lambda interaction: loot_select_callback(interaction,
                                                                                     select_loot_distribution.values[0])
        self.add_item(select_loot_distribution)
