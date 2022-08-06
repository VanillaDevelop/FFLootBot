import discord
from Bot.Team import Team


class BiSEmbed(discord.Embed):
    def __init__(self, team: Team):
        super().__init__()
        self.title = f"Best in Slot settings for Team {team.__name}"
        self.description = "You may set your BiS by clicking the buttons below to select the appropriate " \
                           "upgrade level for each gear slot, then click confirm to finish the process. " \
                           "See below for which level to select. **This message " \
                           "will automatically be deleted after 10 minutes.**"
        self.add_field(name="No Upgrade", value="Use this value if your BiS for the given slot is **not**"
                                                " a raid item (e.g., your BiS item comes from tomestones)."
                       , inline=False)
        self.add_field(name="Same Stats", value="Use this value if your BiS for the given slot is from raid, but "
                                                "your substat distribution does not change from acquiring it "
                                                "(e.g., Crit/Det crafted item, and Crit/Det raid item).", inline=False)
        self.add_field(name="Minor Substat Upgrade", value="Use this value if your BiS for the given slot is from "
                                                           "raid, and acquiring it provides you with a minor substat "
                                                           "improvement (e.g., Crit/Det crafted item, "
                                                           "and Crit/DH raid item)", inline=False)
        self.add_field(name="Major Substat Upgrade", value="Use this value if your BiS for the given slot is from "
                                                           "raid, and acquiring it provides you with a major substat "
                                                           "improvement (e.g., Crit/SS crafted item, "
                                                           "and Crit/DH raid item)", inline=False)
