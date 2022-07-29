from enum import Enum

from Bot.Player import Player, Item, Role, RaidUpgrade


class LootPriority(Enum):
    DPS = 1
    EQUAL = 2
    NONE = 3


class Team:
    def __init__(self, name: str):
        self.members = {}
        self.name = name
        self.loot_priority = LootPriority.NONE

    def add_member(self, member_id: int):
        self.members[member_id] = Player()
        return self.members[member_id]

    def gear_priority(self, gear_type: Item):
        if self.loot_priority == LootPriority.DPS:
            # prioritize DPS by substat upgrades
            eligible = [member for member in self.members if self.members[member].role == Role.DPS and
                        self.members[member].gear_upgrades[gear_type.value-1] != RaidUpgrade.NO]
            # if no dps needs this item, check all team members
            if len(eligible) == 0:
                eligible = [member for member in self.members
                            if self.members[member].gear_upgrades[gear_type.value-1] != RaidUpgrade.NO]
            # sort by who needs this item the most
            eligible.sort(key=lambda x: self.members[x].gear_upgrades[gear_type.value-1])
            return eligible
        elif self.loot_priority == LootPriority.EQUAL:
            # prioritize by pity
            eligible = [member for member in self.members
                        if self.members[member].gear_upgrades[gear_type.value-1] != RaidUpgrade.NO]
            eligible.sort(key=lambda x: self.members[x].pity)
            return eligible
        else:
            eligible = [member for member in self.members
                        if self.members[member].gear_upgrades[gear_type.value-1] != RaidUpgrade.NO]
            return eligible
