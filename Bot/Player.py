from enum import Enum, IntEnum


class Role(Enum):
    DPS = 1
    TANK = 2
    HEALER = 3

    def __str__(self):
        if self == Role.DPS:
            return "DPS"
        else:
            return self.name.capitalize()


class RaidUpgrade(IntEnum):
    NO = 1,
    STATS = 2,
    SUBSTATS_MINOR = 3,
    SUBSTATS_MAJOR = 4

    def __str__(self):
        if self == RaidUpgrade.NO:
            return "No Upgrade"
        elif self == RaidUpgrade.STATS:
            return "Same Stats"
        elif self == RaidUpgrade.SUBSTATS_MINOR:
            return "Minor Substat Upgrade"
        elif self == RaidUpgrade.SUBSTATS_MAJOR:
            return "Major Substat Upgrade"
        else:
            return "Unknown"


class Item(Enum):
    WEAPON = 1
    HEAD = 2
    BODY = 3
    HANDS = 4
    LEGS = 5
    FEET = 6
    EARRINGS = 7
    NECK = 8
    BRACELET = 9
    RING = 10

    def __str__(self):
        return self.name.capitalize()


class Player:
    def __init__(self, player_name: str):
        self.__role = Role.TANK
        self.__gear_upgrades = [RaidUpgrade.NO] * len(Item)
        self.__gear_owned = []
        self.__is_editing_bis = False
        self.__is_adding_item = False
        self.__player_message_id = None
        self.__player_author_id = None
        self.__player_name = player_name
        self.__twines_needed = 0
        self.__coatings_needed = 0
        self.__twines_got = 0
        self.__coatings_got = 0
        self.__pity = 0

    def get_remaining_coating_count(self):
        return self.__coatings_needed - self.__coatings_got

    def get_remaining_twine_count(self):
        return self.__twines_needed - self.__twines_got

    def get_player_name(self) -> str:
        return self.__player_name

    def get_player_role(self) -> Role:
        return self.__role

    def set_player_role(self, role: Role):
        self.__role = role

    def get_author_id(self) -> int:
        return self.__player_author_id

    def get_message_id(self) -> int:
        return self.__player_message_id

    def get_is_editing_bis(self) -> bool:
        return self.__is_editing_bis

    def set_is_editing_bis(self, is_editing_bis: bool):
        self.__is_editing_bis = is_editing_bis

    def get_is_adding_item(self) -> bool:
        return self.__is_adding_item

    def set_is_adding_item(self, is_adding_item: bool):
        self.__is_adding_item = is_adding_item

    def update_bis(self, gear_upgrades: list):
        self.__gear_upgrades = gear_upgrades
        self.update_twines_and_coatings()

    def give_item(self, item: int):
        if item == 98:
            self.__twines_got += 1
        elif item == 99:
            self.__coatings_got += 1
        else:
            self.__gear_owned.append(item-1)

    def get_upgrade_level(self, item: Item) -> RaidUpgrade:
        return self.__gear_upgrades[item.value-1]

    def link_message(self, message_id: int, author_id: int):
        self.__player_message_id = message_id
        self.__player_author_id = author_id

    def has_gearpiece(self, item: Item):
        return (item.value-1) in self.__gear_owned

    def needs_item(self, item: Item):
        return self.__gear_upgrades[item.value-1] != RaidUpgrade.NO and not (item.value-1) in self.__gear_owned

    def add_pity(self, pity: int):
        self.__pity += pity

    def update_twines_and_coatings(self):
        self.__twines_needed = len([gear for gear in self.__gear_upgrades[1:6] if gear == RaidUpgrade.NO])
        # assume 1 coating always needed for second ring
        self.__coatings_needed = 1 + len([gear for gear in self.__gear_upgrades[6:] if gear == RaidUpgrade.NO])

    def get_unowned_gear(self):
        return [item if i not in self.__gear_owned else RaidUpgrade.NO for i, item in enumerate(self.__gear_upgrades)]
