import discord


class PlayerPurchaseEmbed(discord.Embed):
    def __init__(self):
        super().__init__()
        self.title = "Log purchased gear."
        self.description = "In this menu, you may add gear you purchased using books. The gear purchased in this way " \
                           "will not increase or decrease your pity. Select the appropriate item purchased from the " \
                           "list below. **This message will automatically be deleted after 3 minutes.**"
