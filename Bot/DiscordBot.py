import discord
import discord.types.components
from discord.ext import commands
from discord.ui import Button, View


class DiscordBot:
    def __init__(self, token):
        self.token = token
        self.client = commands.Bot(command_prefix='!')

        @self.client.event
        async def on_ready():
            self.__handle_on_ready__()

        @self.client.command()
        async def info(ctx):
            embed = discord.Embed(title="XIV Loot Bot", description="This bot was created to simplify loot "
                                                                    "distribution during progression raiding and "
                                                                    "gearing. ", color=0x00ff00)
            embed.add_field(name="Creating a team", value="You may have one active team at any given time. "
                                                          "To start the flow, DM me with **!create**. You will be given"
                                                          " an access code through which your team members can join "
                                                          "the team. As the team owner, you are responsible for "
                                                          "supplying logs concerning the loot and specifying loot "
                                                          "distribution settings.", inline=False)
            embed.add_field(name="Joining a team", value="If you are given an access code by the team owner, you "
                                                         "may join the team by DMing me with **!join [code]**. You will"
                                                         " then receive further instructions on how to specify your BiS"
                                                         " set. As a team member, you are responsible for reporting "
                                                         "on item purchases, and providing the correct BiS "
                                                         "information prior to prog start.", inline=False)
            embed.add_field(name="Loot distribution", value="When a team owner provides the log of a loot drop, "
                                                            "the bot will determine who benefits most from the "
                                                            "item drop, and will inform all members accordingly. "
                                                            "The team owner may set different settings for the "
                                                            "loot distribution, such as gear funnel, dps prioritization"
                                                            ", or all equal.", inline=False)
            await ctx.send(embed=embed)

        @self.client.command()
        async def create(ctx):
            if not isinstance(ctx.channel, discord.channel.DMChannel):
                await ctx.send("This command can only be used in DMs.")
                return

        @self.client.command()
        async def ping(ctx):
            button = Button(label="Click me!", style=discord.ButtonStyle.primary)
            view = View()
            view.add_item(button);
            await ctx.send(f'Pong! {round(self.client.latency * 1000)}ms', view=view)

        self.client.run(self.token)

    def __handle_on_ready__(self):
        print(f'{self.client.user} ready!')
