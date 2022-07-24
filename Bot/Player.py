from enum import Enum


class Role(Enum):
    DPS = 1
    TANK = 2
    HEAL = 3


class RaidUpgrade(Enum):
    NO = 1,
    STATS = 2,
    SUBSTATS_MINOR = 3,
    SUBSTATS_MAJOR = 4


class Player:
    def __init__(self):
        self.role = None
        self.gear_upgrades = [RaidUpgrade.NO] * 11
