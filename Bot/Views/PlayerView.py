import discord

from Bot.Player import Player, Role
from Bot.Team import Team


class PlayerView(discord.ui.View):
    def __init__(self, team: Team, player: Player, role_select_callback: callable):
        super().__init__()
        select_player_role = discord.ui.Select(
            options=[
                discord.SelectOption(
                    label="Role: Tank",
                    value=Role.TANK.name,
                    default=player.role == Role.TANK
                ),
                discord.SelectOption(
                    label="Role: Healer",
                    value=Role.HEAL.name,
                    default=player.role == Role.HEAL
                ),
                discord.SelectOption(
                    label="Role: DPS",
                    value=Role.DPS.name,
                    default=player.role == Role.DPS
                )],
            placeholder="Select your role.")
        select_player_role.callback = lambda ctx: role_select_callback(ctx, select_player_role.values[0])
        self.add_item(select_player_role)