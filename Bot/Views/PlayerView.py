import discord

from Bot.Player import Player, Role
from Bot.Team import Team


class PlayerView(discord.ui.View):
    def __init__(self, player: Player, role_select_callback: callable, bis_callback: callable,
                 purchase_callback: callable, leave_team_callback: callable):
        super().__init__(timeout=None)
        select_player_role = discord.ui.Select(
            options=[
                discord.SelectOption(
                    label="Role: Tank",
                    value=Role.TANK.name,
                    default=player.get_player_name() == Role.TANK
                ),
                discord.SelectOption(
                    label="Role: Healer",
                    value=Role.HEALER.name,
                    default=player.get_player_name() == Role.HEALER
                ),
                discord.SelectOption(
                    label="Role: DPS",
                    value=Role.DPS.name,
                    default=player.get_player_name() == Role.DPS
                )],
            placeholder="Select your role.",
            custom_id="SELECT_PLAYER_ROLE",)
        select_player_role.callback = lambda ctx: role_select_callback(ctx, select_player_role.values[0])
        self.add_item(select_player_role)

        set_bis_button = discord.ui.Button(
            label="Update Best in Slot Gear",
            style=discord.ButtonStyle.primary,
            custom_id="SET_BIS_BUTTON",
        )
        set_bis_button.callback = bis_callback
        self.add_item(set_bis_button)

        add_item_button = discord.ui.Button(
            label="Add Purchased Item",
            style=discord.ButtonStyle.primary,
            custom_id="ADD_ITEM_BUTTON",
        )
        add_item_button.callback = purchase_callback
        self.add_item(add_item_button)

        leave_team_button = discord.ui.Button(
            label="Leave Team",
            style=discord.ButtonStyle.danger,
            custom_id="LEAVE_TEAM_BUTTON",
        )
        leave_team_button.callback = leave_team_callback
        self.add_item(leave_team_button)
