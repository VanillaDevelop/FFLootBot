import discord

from Bot.Player import Player, Item
from Bot.Team import Team


# embed for player info
class PlayerInfoEmbed(discord.Embed):
    def __init__(self, team: Team, player: Player):
        super().__init__()
        self.title = f"Team {team.get_team_name()}"
        self.description = f"This is your personal information panel for team {team.get_team_name()}."

        teaminfo = "**Members**"
        for member in team.get_all_member_ids():
            team_member = team.get_member_by_author_id(member)
            teaminfo += f"\n{team_member.get_player_name()} ({str(team_member.get_player_role())})"
        teaminfo += "\n\n**Settings**"
        teaminfo += f"\nLoot priority rule: {str(team.get_loot_priority())}"

        # add total items needed
        teaminfo += "\n\n**Gear Needed**"
        for item in Item:
            count = team.number_of_item_needed(item)
            if count > 0:
                teaminfo += f"\n{str(item)}: {count}"
        # add total twines and coatings needed
        twines = team.number_of_item_needed(98)
        coatings = team.number_of_item_needed(99)
        if twines > 0:
            teaminfo += f"\nTwines: {twines} "
        if coatings > 0:
            teaminfo += f"\nCoatings: {coatings}"
        self.add_field(name="Team Info",
                       value=teaminfo)

        # add player info
        self_info = (f"Name: {player.get_player_name()}"
                     f"\nRole: {player.get_player_role()}"
                     f"\n\n**Gear you need**")
        for item in Item:
            if player.needs_item(item):
                self_info += f"\n{str(item)} ({str(player.get_upgrade_level(item))})"
        if player.get_remaining_twine_count() > 0:
            self_info += f"\nTwines: {player.get_remaining_twine_count()}"
        if player.get_remaining_coating_count() > 0:
            self_info += f"\nCoatings: {player.get_remaining_coating_count()}"

        self.add_field(name="Player Info",
                       value=self_info)
