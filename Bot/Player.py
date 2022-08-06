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
        self.gear_upgrades = [RaidUpgrade.NO] * len(Item)
        self.gear_owned = []
        self.is_editing_bis = False
        self.is_adding_item = False
        self.player_message_id = None
        self.player_author_id = None
        self.__player_name = player_name
        self.twines_needed = 0
        self.coatings_needed = 0
        self.twines_got = 0
        self.coatings_got = 0
        self.pity = 0

    def get_remaining_coating_count(self):
        return self.coatings_needed - self.coatings_got

    def get_remaining_twine_count(self):
        return self.twines_needed - self.twines_got

    def get_player_name(self) -> str:
        return self.__player_name

    def get_player_role(self) -> Role:
        return self.__role

    def set_player_role(self, role: Role):
        self.__role = role

    def get_author_id(self) -> int:
        return self.player_author_id

    def get_message_id(self) -> int:
        return self.player_message_id

    def update_twines_and_coatings(self):
        self.twines_needed = len([gear for gear in self.gear_upgrades[1:6] if gear == RaidUpgrade.NO])
        # assume 1 coating always needed for second ring
        self.coatings_needed = 1 + len([gear for gear in self.gear_upgrades[6:] if gear == RaidUpgrade.NO])

    def get_unowned_gear(self):
        return [item if i not in self.gear_owned else RaidUpgrade.NO for i, item in enumerate(self.gear_upgrades)]
