import discord

from Bot.Player import Item, RaidUpgrade
from Bot.Team import LootPriority


class AssignLootEmbed(discord.Embed):
    def __init__(self, team, item: int = None):
        super().__init__()
        self.title = "Assign gear to players."
        self.description = "In this menu, you may assign drops to players. The corresponding players will have the " \
                           "item added to their owned gear, and all other eligible players will obtain pity according" \
                           " to the value of the item. **This message will automatically be deleted after 3 minutes.**"

        if item is not None and team.__loot_priority != LootPriority.NONE:
            priolist = ""
            prio = team.gear_priority(item)
            if len(prio) > 0:
                if item >= 98:
                    for i, (player, role, missing) in enumerate(team.gear_priority(item), 1):
                        priolist += f"{i}. {team.__members[player].__player_name} ({role.__name.capitalize()}): " \
                                    f"Needs {missing}\n"
                else:
                    for i, (player, role, upgrade, pity) in enumerate(team.gear_priority(item), 1):
                        priolist += f"{i}. {team.__members[player].__player_name} ({role.__name.capitalize()}): " \
                                    f"{str(RaidUpgrade(upgrade))} (Pity: {pity})\n"
                self.add_field(name="Suggested priority", value=priolist)
