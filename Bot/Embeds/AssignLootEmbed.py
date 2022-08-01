import discord


class AssignLootEmbed(discord.Embed):
    def __init__(self):
        super().__init__()
        self.title = "Assign gear to players."
        self.description = "In this menu, you may assign drops to players. The corresponding players will have the " \
                           "item added to their owned gear, and all other eligible players will obtain pity according" \
                           " to the value of the item. **This message will automatically be deleted after 3 minutes.**"
