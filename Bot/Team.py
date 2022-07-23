from enum import Enum


class LootPriority(Enum):
    DPS = 1
    EQUAL = 2
    NONE = 3


class Team:
    def __init__(self, leader_id: int, name: str):
        self.members = []
        self.leader = leader_id
        self.name = name
        self.loot_priority = LootPriority.NONE

    def add_member(self, member_id: int):
        self.members.append(member_id)

    def set_loot_priority(self, priority: LootPriority):
        self.loot_priority = priority
