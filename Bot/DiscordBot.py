import discord
import discord.types.components
from discord.ext import commands
from discord.ui import Button, View

from Bot.TeamManager import TeamManager

COMMAND_PREFIX = '!'


class DiscordBot:
    def __init__(self, token: str):
        self.token = token
        self.client = commands.Bot(command_prefix=COMMAND_PREFIX)
        self.team_manager = TeamManager()
        self.team_leaders = {}

        @self.client.event
        async def on_ready():
            self.__handle_on_ready__()

        @self.client.command()
        async def info(ctx):
            embed = discord.Embed(title="XIV Loot Bot", description="This bot was created to simplify loot "
                                                                    "distribution during progression raiding and "
                                                                    "gearing. ", color=0x00ff00)
            embed.add_field(name="Creating a team", value="You may have one active team at any given time. "
                                                          f"To start the flow, DM me with **{COMMAND_PREFIX}"
                                                          "create [name]**. You will be given"
                                                          " an access code through which your team members can join "
                                                          "the team. As the team owner, you are responsible for "
                                                          "supplying logs concerning the loot and specifying loot "
                                                          "distribution settings.", inline=False)
            embed.add_field(name="Joining a team", value="If you are given an access code by the team owner, you "
                                                         f"may join the team by DMing me with **{COMMAND_PREFIX}"
                                                         "join [code]**. You will"
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
        async def create(ctx, name: str):
            if not isinstance(ctx.channel, discord.channel.DMChannel):
                await ctx.send("This command can only be used in DMs.")
                return

            if ctx.author.id in self.team_leaders:
                await ctx.send("You already have an active team.")
                return

            uuid = self.team_manager.create_team(ctx.author.id, name)
            self.team_leaders[ctx.author.id] = uuid

            for (embed, view) in zip(self.__build_team_control_embeds__(name, uuid),
                                     self.__build_team_control_views__(name, uuid)):
                await ctx.send(embed=embed, view=view)

        @self.client.command()
        async def ping(ctx):
            button = Button(label="Click me!", style=discord.ButtonStyle.primary)
            view = View()
            view.add_item(button);
            await ctx.send(f'Pong! {round(self.client.latency * 1000)}ms', view=view)

        self.client.run(self.token)

    def __handle_on_ready__(self):
        print(f'{self.client.user} ready!')

    def __build_team_control_embeds__(self, name: str, uuid: str):
        embeds = []
        embed = discord.Embed(title=f"Team {name}", description=f"This is the control panel for team {name}.")
        embed.add_field(name="Inviting Team Members", value=f"Team members may join the team by DMing the bot with "
                                                            f"**{COMMAND_PREFIX}join {uuid}**.", inline=False)
        embeds.append(embed)

        embed = discord.Embed()
        embed.add_field(name="Loot Distribution", value="Select below who should get priority for loot drops.",
                        inline=False)
        embeds.append(embed)

        return embeds

    def __build_team_control_views__(self, name: str, uuid: str):
        views = [None]

        view = View()
        view.add_item(Button(label="Priority: DPS", style=discord.ButtonStyle.primary))
        view.add_item(Button(label="Priority: Equal Loot", style=discord.ButtonStyle.primary))
        view.add_item(Button(label="Priority: None", style=discord.ButtonStyle.primary))
        views.append(view)

        return views
