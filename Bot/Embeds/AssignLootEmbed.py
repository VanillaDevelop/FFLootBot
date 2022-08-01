import discord

from Bot.Player import Item


class AssignLootEmbed(discord.Embed):
    def __init__(self, team: discord.Team, item: int = None):
        super().__init__()
        self.title = "Assign gear to players."
        self.description = "In this menu, you may assign drops to players. The corresponding players will have the " \
                           "item added to their owned gear, and all other eligible players will obtain pity according" \
                           " to the value of the item. **This message will automatically be deleted after 3 minutes.**"

        if item is not None:
            self.add_field(name="Suggested priority: ", value=team.gear_priority(item))
