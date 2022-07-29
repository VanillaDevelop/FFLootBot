from enum import Enum, IntEnum


class Role(Enum):
    DPS = 1
    TANK = 2
    HEALER = 3


class RaidUpgrade(IntEnum):
    NO = 1,
    STATS = 2,
    SUBSTATS_MINOR = 3,
    SUBSTATS_MAJOR = 4


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


class Player:
    def __init__(self):
        self.role = Role.TANK
        self.gear_upgrades = [RaidUpgrade.NO] * len(Item)
        self.is_editing_bis = False
        self.player_message_id = None
        self.player_author_id = None
        self.player_name = None
        self.twines_needed = 0
        self.coatings_needed = 0
        self.twines_got = 0
        self.coatings_got = 0
        self.pity = 0

    def update_twines_and_coatings(self):
        self.twines_needed = len([gear for gear in self.gear_upgrades[1:6] if gear == RaidUpgrade.NO])
        # assume 1 coating always needed for second ring
        self.coatings_needed = 1 + len([gear for gear in self.gear_upgrades[6:] if gear == RaidUpgrade.NO])
