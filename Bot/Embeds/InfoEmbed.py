import discord


class InfoEmbed(discord.Embed):
    def __init__(self, command_prefix: str):
        super().__init__()
        self.title = "XIV Loot Bot"
        self.description = "This bot was created to simplify loot distribution during progression raiding and gearing."
        self.add_field(name="Creating a team", value="You may have one active team at any given time. "
                                                     f"To start the flow, DM me with **{command_prefix}"
                                                     "create [name]**. You will be given"
                                                     " an access code through which your team members can join "
                                                     "the team. As the team owner, you are responsible for "
                                                     "supplying logs concerning the loot and specifying loot "
                                                     "distribution settings.", inline=False)
        self.add_field(name="Joining a team", value="If you are given an access code by the team owner, you "
                                                    f"may join the team by DMing me with **{command_prefix}"
                                                    "join [code]**. You will"
                                                    " then receive further instructions on how to specify your BiS"
                                                    " set. As a team member, you are responsible for reporting "
                                                    "on item purchases, and providing the correct BiS "
                                                    "information prior to prog start.", inline=False)
        self.add_field(name="Loot distribution", value="When a team owner provides the log of a loot drop, "
                                                       "the bot will determine who benefits most from the "
                                                       "item drop, and will inform all members accordingly. "
                                                       "The team owner may set different settings for the "
                                                       "loot distribution, such as gear funnel, dps prioritization"
                                                       ", or all equal.", inline=False)
