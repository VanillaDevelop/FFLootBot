from enum import Enum
from typing import Optional

from Bot.Player import Player, Item


class LootPriority(Enum):
    DPS = 1
    EQUAL = 2
    NONE = 3

    def __str__(self):
        return self.name.capitalize()


class Team:
    def __init__(self, team_id: str, team_name: str):
        self.__members = dict[int, Player]()
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

    # returns the number of a given item that the team needs in total
    def number_of_item_needed(self, item: int) -> int:
        if item == 98:
            return sum([self.__members[member].get_remaining_twine_count() for member in self.__members])
        elif item == 99:
            return sum([self.__members[member].get_remaining_coating_count() for member in self.__members])
        else:
            return sum([1 for member in self.__members if self.__members[member].needs_item(Item(item))])

    # gives pity to everyone in the team who needed the item except for the player who received it
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

    # returns the gear priority for a given item
    # the return is either in the form [(player, upgrade_level, pity), ...] if the item is a gear piece
    # or in the form [(Player, num_still_needed), ...] if the item is a twine or coating
    def gear_priority(self, gear_type: int):
        # gear piece
        if gear_type <= len(Item):
            plist = list(map(
                lambda member: (member, member.get_upgrade_level(Item(gear_type)), member.get_pity()),
                [member for member in self.__members.values() if member.needs_item(Item(gear_type))]))
            if self.__loot_priority == LootPriority.DPS:
                # dps priority sorting: sort by role, then by upgrade level (ignore pity)
                plist.sort(key=lambda triple: (triple[0].get_player_role(), -triple[1]))
            elif self.__loot_priority == LootPriority.EQUAL:
                # equal loot sorting: sort by pity, then by upgrade level (ignore role)
                plist.sort(key=lambda triple: (-triple[2], -triple[1]))
            return plist

        # twine or coating
        if gear_type == 98:
            plist = list(map(
                lambda member: (member, member.get_remaining_twine_count()),
                [member for member in self.__members.values()
                 if member.get_remaining_twine_count() > 0]))
        else:
            plist = list(map(
                lambda member: (member, member.get_remaining_coating_count()),
                [member for member in self.__members.values()
                 if member.get_remaining_coating_count() > 0]))
        if self.__loot_priority == LootPriority.DPS:
            # dps priority sorting: sort by role, then by required item count
            plist.sort(key=lambda triple: (triple[0].get_player_role(), -triple[1]))
        else:
            # equal loot sorting: sort by required item count only
            plist.sort(key=lambda triple: -triple[1])
        return plist

    # player leaves team
    def leave(self, player: Player):
        if player.get_author_id() in self.__members:
            del self.__members[player.get_author_id()]
