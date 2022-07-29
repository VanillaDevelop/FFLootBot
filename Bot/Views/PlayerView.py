import discord

from Bot.Player import Player, Role
from Bot.Team import Team


class PlayerView(discord.ui.View):
    def __init__(self, player: Player, role_select_callback: callable, bis_callback: callable):
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
                    value=Role.HEALER.name,
                    default=player.role == Role.HEALER
                ),
                discord.SelectOption(
                    label="Role: DPS",
                    value=Role.DPS.name,
                    default=player.role == Role.DPS
                )],
            placeholder="Select your role.")
        select_player_role.callback = lambda ctx: role_select_callback(ctx, select_player_role.values[0])
        self.add_item(select_player_role)

        set_bis_button = discord.ui.Button(
            label="Update Best in Slot Gear",
            style=discord.ButtonStyle.primary
        )
        set_bis_button.callback = bis_callback
        self.add_item(set_bis_button)
