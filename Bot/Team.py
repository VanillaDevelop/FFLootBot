from enum import Enum

from Bot.Player import Player


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
