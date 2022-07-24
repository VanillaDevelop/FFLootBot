import discord
import discord.types.components
from discord.ext import commands
from discord.ui import Button, View

from Bot.Player import Player, Role
from Bot.Team import Team, LootPriority
from Bot.TeamManager import TeamManager

COMMAND_PREFIX = '!'


class DiscordBot:
    def __init__(self, token: str):
        self.token = token
        self.client = commands.Bot(command_prefix=COMMAND_PREFIX)
        self.team_manager = TeamManager()
        self.team_leaders = {}
        self.message_map = {}

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

            uuid = self.team_manager.create_team(name)
            self.team_leaders[ctx.author.id] = uuid
            self.team_manager.teams[uuid].add_member(ctx.author.id)

            for (embed, view) in zip(self.__build_team_control_embeds__(self.team_manager.teams[uuid], uuid),
                                     self.__build_team_control_views__(self.team_manager.teams[uuid], uuid)):
                message = await ctx.send(embed=embed, view=view)
                if view is not None:
                    self.message_map[message.id] = uuid

            for (embed, view) in zip(self.__build_team_member_embeds__(self.team_manager.teams[uuid], self.team_manager.teams[uuid].members[ctx.author.id]),
                                     self.__build_team_member_views__(self.team_manager.teams[uuid], self.team_manager.teams[uuid].members[ctx.author.id])):
                message = await ctx.send(embed=embed, view=view)
                if view is not None:
                    self.message_map[message.id] = uuid

        self.client.run(self.token)

    def __handle_on_ready__(self):
        print(f'{self.client.user} ready!')

    async def __handle_loot_priority_click__(self, ctx, priority: LootPriority):
        self.team_manager.teams[self.message_map[ctx.message.id]].loot_priority = priority
        await ctx.response.edit_message(view=self.__build_loot_priority_view__(self.team_manager.teams[self.message_map[ctx.message.id]], self.message_map[ctx.message.id]))

    async def __handle_role_click__(self, ctx, role: Role):
        self.team_manager.teams[self.message_map[ctx.message.id]].members[ctx.message.id].role = role
        await ctx.response.edit_message(view=self.__build_role_view(self.team_manager.teams[self.message_map[ctx.message.id]], self.message_map[ctx.message.id]))

    def __build_team_member_embeds__(self, team: Team, player: Player):
        embeds = []
        embed = discord.Embed(title=f"Team {team.name}", description=f"This is the information panel for team {team.name}.")
        embed.add_field(name="Current Team Status",
                        value=f"Team members: {len(team.members)}")
        embeds.append(embed)

        embed = discord.Embed()
        embed.add_field(name="Role", value="Please correctly identify your in-game role below. "
                                           "This will be used to properly distribute loot.",
                        inline=False)
        embeds.append(embed)

        embed = discord.Embed()
        embed.add_field(name="Best in Slot", value="To change your Best in Slot selection, "
                                                   "click the button below.",
                        inline=False)
        embeds.append(embed)
        return embeds

    def __build_team_member_views__(self, team: Team, player: Player):
        views = [None, self.__build_role_view(team, player), None]
        return views

    def __build_role_view(self, team: Team, player: Player):
        view = View()
        btn_tank = Button(label="Tank",
                         style=discord.ButtonStyle.red if player.role != Role.TANK else discord.ButtonStyle.green)
        btn_tank.callback = lambda ctx: self.__handle_role_click__(ctx=ctx, role=Role.Tank)
        view.add_item(btn_tank)

        btn_heal = Button(label="Healer",
                         style=discord.ButtonStyle.red if player.role != Role.HEAL else discord.ButtonStyle.green)
        btn_heal.callback = lambda ctx: self.__handle_role_click__(ctx=ctx, role=Role.HEAL)
        view.add_item(btn_heal)

        btn_dps = Button(label="DPS",
                         style=discord.ButtonStyle.red if player.role != Role.DPS else discord.ButtonStyle.green)
        btn_dps.callback = lambda ctx: self.__handle_role_click__(ctx=ctx, role=Role.DPS)
        view.add_item(btn_dps)
        return view

    def __build_team_control_embeds__(self, team: Team, uuid: str):
        embeds = []
        embed = discord.Embed(title=f"Team {team.name}", description=f"This is the control panel for team {team.name}.")
        embed.add_field(name="Inviting Team Members", value=f"Team members may join the team by DMing the bot with "
                                                            f"**{COMMAND_PREFIX}join {uuid}**.", inline=False)
        embeds.append(embed)

        embed = discord.Embed()
        embed.add_field(name="Loot Distribution", value="Select below who should get priority for loot drops."
                                                        "\n**DPS**\n"
                                                        "Loot will be distributed according to the biggest DPS "
                                                        "improvement. This means loot will go exclusively to DPS "
                                                        "(unless all DPS already possess a similar or better item)"
                                                        " and large item upgrades will be prioritized."
                                                        "\n**Equal Loot**\n"
                                                        "Loot will be distributed in such "
                                                        "a way that the power increase of all players is roughly "
                                                        "equal. Players who have less loot will receive priority "
                                                        "on drops which benefit them."
                                                        "\n**None**\n"
                                                        "No loot priority will be provided, but the bot will "
                                                        "show the potential upgrade for every player.",
                        inline=False)
        embeds.append(embed)
        return embeds

    def __build_team_control_views__(self, team: Team, uuid: str):
        views = [None, None, self.__build_loot_priority_view__(team, uuid)]
        return views

    def __build_loot_priority_view__(self, team: Team, uuid: str):
        view = View()
        btn_dps = Button(label="Priority: DPS",
                         style=discord.ButtonStyle.red if team.loot_priority != LootPriority.DPS else discord.ButtonStyle.green)
        btn_dps.callback = lambda ctx: self.__handle_loot_priority_click__(ctx=ctx, priority=LootPriority.DPS)
        view.add_item(btn_dps)

        btn_equal = Button(label="Priority: Equal Loot",
                           style=discord.ButtonStyle.red if team.loot_priority != LootPriority.EQUAL else discord.ButtonStyle.green)
        btn_equal.callback = lambda ctx: self.__handle_loot_priority_click__(ctx=ctx, priority=LootPriority.EQUAL)
        view.add_item(btn_equal)

        btn_none = Button(label="Priority: None",
                          style=discord.ButtonStyle.red if team.loot_priority != LootPriority.NONE else discord.ButtonStyle.green)
        btn_none.callback = lambda ctx: self.__handle_loot_priority_click__(ctx=ctx, priority=LootPriority.NONE)
        view.add_item(btn_none)
        return view
