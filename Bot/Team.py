from enum import Enum
from typing import Optional

from Bot.Player import Player, Item, RaidUpgrade


class LootPriority(Enum):
    DPS = 1
    EQUAL = 2
    NONE = 3

    def __str__(self):
        return self.name.capitalize()


class Team:
    def __init__(self, team_id: str, team_name: str):
        self.__members = {}
        self.__name = team_name
        self.__uuid = team_id
        self.__loot_priority = LootPriority.NONE
        self.__is_assigning_loot = False

    def get_uuid(self) -> str:
        return self.__uuid

    def get_member_by_author_id(self, author_id: int) -> Optional[Player]:
        if author_id in self.__members:
            return self.__members[author_id]
        return None

    def get_team_name(self) -> str:
        return self.__name

    def get_all_member_ids(self) -> list:
        return list(self.__members.keys())

    def add_member(self, member_id: int, player_name: str):
        self.__members[member_id] = Player(player_name)
        return self.__members[member_id]

    def get_loot_priority(self) -> LootPriority:
        return self.__loot_priority

    def set_loot_priority(self, loot_priority: LootPriority) -> None:
        self.__loot_priority = loot_priority

    def get_is_assigning_loot(self) -> bool:
        return self.__is_assigning_loot

    def set_is_assigning_loot(self, is_assigning_loot: bool) -> None:
        self.__is_assigning_loot = is_assigning_loot

    def give_pity(self, item: Item, except_player: Player):
        for member_id in self.__members:
            player = self.__members[member_id]
            if player != except_player and player.needs_item(item):
                if item.value > 6:
                    player.add_pity(4)
                elif item == Item.WEAPON or item == Item.BODY or item == Item.LEGS:
                    player.add_pity(8)
                else:
                    player.add_pity(6)

    def gear_priority(self, gear_type: int):
        if gear_type <= len(Item):
            plist = list(map(
                lambda p: (
                    p, self.__members[p].__role, self.__members[p].__gear_upgrades[gear_type - 1], self.__members[p].__pity),
                [member for member in self.__members
                 if self.__members[member].__gear_upgrades[gear_type - 1] != RaidUpgrade.NO
                 and (gear_type - 1) not in self.__members[member].__gear_owned]))
            if self.__loot_priority == LootPriority.DPS:
                plist.sort(key=lambda p: (p[1].value, -p[2]))
            elif self.__loot_priority == LootPriority.EQUAL:
                plist.sort(key=lambda p: (-p[3], -p[2]))
            return plist

        # priority for twines and coatings is based on who needs the most, prioritizing DPS if DPS priority is selected
        if gear_type == 98:
            plist = list(map(lambda p: (p, self.__members[p].__role,
                                        self.__members[p].__twines_needed - self.__members[p].__twines_got),
                             [member for member in self.__members
                              if self.__members[member].__twines_needed - self.__members[member].__twines_got > 0]))
        elif gear_type == 99:
            plist = list(map(
                lambda p: (
                    p, self.__members[p].__role, self.__members[p].__coatings_needed - self.__members[p].__coatings_got),
                [member for member in self.__members
                 if self.__members[member].__coatings_needed - self.__members[member].__coatings_got > 0]))
        if self.__loot_priority == LootPriority.DPS:
            plist.sort(key=lambda p: (p[1].value, -p[2]))
        else:
            plist.sort(key=lambda p: -p[2])
        return plist

    def leave(self, player: Player):
        if player.get_author_id() in self.__members:
            del self.__members[player.get_author_id()]
