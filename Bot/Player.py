from enum import Enum, IntEnum


class Role(Enum):
    DPS = 1
    TANK = 2
    HEAL = 3


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
    RING1 = 10
    RING2 = 11


class Player:
    def __init__(self):
        self.role = Role.TANK
        self.gear_upgrades = [RaidUpgrade.NO] * 11
        self.is_editing_bis = False
        self.player_message_id = None
        self.player_author_id = None
