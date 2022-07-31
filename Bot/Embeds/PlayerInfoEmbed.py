import discord

from Bot.Player import Role, Player, RaidUpgrade, Item
from Bot.Team import Team


class PlayerInfoEmbed(discord.Embed):
    def __init__(self, team: Team, player: Player):
        super().__init__()
        self.title = f"Team {team.name}"
        self.description = f"This is your personal information panel for team {team.name}."

        teaminfo = "**Members**"
        for member in team.members:
            teaminfo += f"\n{team.members[member].player_name} ({team.members[member].role.name.capitalize()})"
        # add total items needed
        teaminfo += "\n**Gear Needed**"
        for (i, item) in enumerate(Item):
            c = len([1 for member in team.members if team.members[member].get_unowned_gear()[i] != RaidUpgrade.NO])
            teaminfo += f"\n{item.name.capitalize()}: {c}"
        # add total twines and coatings needed
        twines = [team.members[member].twines_needed - team.members[member].twines_got for member in team.members]
        coatings = [team.members[member].coatings_needed - team.members[member].coatings_got for member in team.members]
        teaminfo += f"\nTwines: {sum(twines)} "
        teaminfo += f"\nCoatings: {sum(coatings)}"

        self.add_field(name="Team Info",
                       value=teaminfo)

        self_info = f"Name: {player.player_name}" \
                    f"\nRole: {player.role.name.capitalize()}" \
                    f"\n**Gear you need: **"
        for (i, upgrade) in enumerate(Item):
            if player.get_unowned_gear()[i] == RaidUpgrade.STATS:
                self_info += f"\n{upgrade.name.capitalize()}: Same Stats"
            elif player.get_unowned_gear()[i] == RaidUpgrade.SUBSTATS_MINOR:
                self_info += f"\n{upgrade.name.capitalize()}: Minor Substat Increase"
            elif player.get_unowned_gear()[i] == RaidUpgrade.SUBSTATS_MAJOR:
                self_info += f"\n{upgrade.name.capitalize()}: Major Substat Increase"
        if player.twines_needed - player.twines_got > 0:
            self_info += f"\nTwines: {player.twines_needed - player.twines_got}"
        if player.coatings_needed - player.coatings_got > 0:
            self_info += f"\nCoatings: {player.coatings_needed - player.coatings_got}"

        self.add_field(name="Player Info",
                       value=self_info)
