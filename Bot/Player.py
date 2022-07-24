from enum import Enum


class Role(Enum):
    DPS = 1
    TANK = 2
    HEAL = 3


class Player:
    def __init__(self, uid):
        self.role = None
        self.uid = uid

    def set_role(self, role: Role):
        self.role = role


