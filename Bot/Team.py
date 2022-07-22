class Team:
    def __init__(self, leader_id: int, name: str):
        self.members = []
        self.leader = leader_id
        self.name = name

    def add_member(self, member_id: int):
        self.members.append(member_id)
