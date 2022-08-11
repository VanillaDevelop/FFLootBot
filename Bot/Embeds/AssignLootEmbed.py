import discord

from Bot.Player import RaidUpgrade
from Bot.Team import LootPriority, Team


# embed for assigning loot to players
class AssignLootEmbed(discord.Embed):
    def __init__(self, team: Team, item: int = None):
        super().__init__()
        self.title = "Assign gear to players."
        self.description = ("In this menu, you may assign drops to players. The corresponding players will have the "
                            "item added to their owned gear, and all other eligible players will obtain pity according"
                            " to the value of the item. "
                            "**This message will automatically be deleted after 3 minutes.**")

        if item is not None and team.get_loot_priority() != LootPriority.NONE:
            priolist = ""
            prio = team.gear_priority(item)
            if len(prio) > 0:
                if item >= 98:
                    for i, (member, missing) in enumerate(team.gear_priority(item), 1):
                        priolist += (f"{i}. {member.get_player_name()} ({str(member.get_player_role())}): "
                                     f"Needs {missing}\n")
                else:
                    for i, (member, upgrade, pity) in enumerate(team.gear_priority(item), 1):
                        priolist += (f"{i}. {member.get_player_name()} ({str(member.get_player_role())}): "
                                     f"{str(RaidUpgrade(upgrade))} (Pity: {pity})\n")
                self.add_field(name="Suggested Priority", value=priolist)

            else:
                self.add_field(name="Suggested Priority", value="This item cannot be assigned to a player, as no player"
                                                                " has indicated that they need this item.")
