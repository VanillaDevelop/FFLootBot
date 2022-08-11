import discord


# embed for info command
class InfoEmbed(discord.Embed):
    def __init__(self):
        super().__init__()
        self.title = "XIV Loot Bot"
        self.description = "This bot was created to simplify loot distribution during progression raiding and gearing."
        self.add_field(name="Creating a team", value="You may have one active team at any given time. "
                                                     f"To create a team, DM me with "
                                                     "**/create [team name] [player name]**. You will be given"
                                                     " an access code through which your team members can join "
                                                     "the team. As the team owner, you can decide loot distribution "
                                                     "settings as well as assign loot to players according to a "
                                                     "predetermined priority.", inline=False)
        self.add_field(name="Joining a team", value="If you are given an access code by the team owner, you "
                                                    f"may join a team by DMing me with "
                                                    "**/join [team uuid] [player name]**. You will"
                                                    " then be able to set up your BiS gear, as well as report on "
                                                    "item purchases you make outside of raid (i.e. through books).",
                       inline=False)
        self.add_field(name="Loot distribution", value="When a team owner provides the log of a loot drop, "
                                                       "the bot will determine who benefits most from the "
                                                       "item drop, and will inform all members accordingly. "
                                                       "The team owner may set different settings for the "
                                                       "loot distribution, such as gear funnel, dps prioritization"
                                                       ", or all equal.", inline=False)
