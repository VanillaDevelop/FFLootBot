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
        self.is_assigning_loot = False

    def add_member(self, member_id: int):
        self.members[member_id] = Player()
        return self.members[member_id]

    def gear_priority(self, gear_type: int):
        if gear_type <= len(Item):
            plist = list(map(
                lambda p: (p, self.members[p].role, self.members[p].gear_upgrades[gear_type-1], self.members[p].pity),
                [member for member in self.members
                 if self.members[member].gear_upgrades[gear_type-1] != RaidUpgrade.NO]))
            if self.loot_priority == LootPriority.DPS:
                plist.sort(key=lambda p: (-p[1].value, p[2]))
            elif self.loot_priority == LootPriority.EQUAL:
                plist.sort(key=lambda p: (p[3], p[2]))
            return plist

        # priority for twines and coatings is based on who needs the most, prioritizing DPS if DPS priority is selected
        if gear_type == 98:
            plist = list(map(lambda p: (p, self.members[p].role,
                                        self.members[p].twines_needed - self.members[p].twines_got),
                             self.members))
        elif gear_type == 99:
            plist = list(map(
                lambda p: (p, self.members[p].role, self.members[p].coatings_needed - self.members[p].coatings_got),
                self.members))
        if self.loot_priority == LootPriority.DPS:
            plist.sort(key=lambda p: (-p[1].value, p[2]))
        else:
            plist.sort(key=lambda p: p[2])
        return plist
