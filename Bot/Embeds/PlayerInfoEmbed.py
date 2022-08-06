import discord

from Bot.Player import Role, Player, RaidUpgrade, Item
from Bot.Team import Team


class PlayerInfoEmbed(discord.Embed):
    def __init__(self, team: Team, player: Player):
        super().__init__()
        self.title = f"Team {team.get_team_name()}"
        self.description = f"This is your personal information panel for team {team.get_team_name()}."

        teaminfo = "**Members**"
        for member in team.get_all_member_ids():
            player = team.get_member_by_author_id(member)
            teaminfo += f"\n{player.get_player_name()} ({str(player.get_player_role())})"
        teaminfo += "\n\n**Settings**"
        teaminfo += f"\nLoot priority rule: {str(team.get_loot_priority())}"
        # add total items needed
        teaminfo += "\n\n**Gear Needed**"
        for (i, item) in enumerate(Item):
            c = len([1 for member in team.get_all_member_ids()
                     if team.get_member_by_author_id(member).get_unowned_gear()[i] != RaidUpgrade.NO])
            if c > 0:
                teaminfo += f"\n{str(item)}: {c}"
        # add total twines and coatings needed
        twines = [team.get_member_by_author_id(member).get_remaining_twine_count()
                  for member in team.get_all_member_ids()]
        coatings = [team.get_member_by_author_id(member).get_remaining_coating_count()
                    for member in team.get_all_member_ids()]
        if sum(twines) > 0:
            teaminfo += f"\nTwines: {sum(twines)} "
        if sum(coatings) > 0:
            teaminfo += f"\nCoatings: {sum(coatings)}"

        self.add_field(name="Team Info",
                       value=teaminfo)

        self_info = f"Name: {player.get_player_name()}" \
                    f"\nRole: {player.get_player_role()}" \
                    f"\n\n**Gear you need**"
        for (i, upgrade) in enumerate(Item):
            item = player.get_unowned_gear()[i]
            if item != RaidUpgrade.NO:
                self_info += f"\n{str(upgrade)} ({str(RaidUpgrade(item))})"
        if player.get_remaining_twine_count() > 0:
            self_info += f"\nTwines: {player.get_remaining_twine_count()}"
        if player.get_remaining_coating_count() > 0:
            self_info += f"\nCoatings: {player.get_remaining_coating_count()}"

        self.add_field(name="Player Info",
                       value=self_info)
