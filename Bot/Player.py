from enum import Enum


class Player:
    def __init__(self, uid):
        self.role = None
        self.uid = uid

    def set_role(self, role):
        self.role = role


class Role(Enum):
    DPS = 1
    TANK = 2
    HEAL = 3
