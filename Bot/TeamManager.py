class TeamManager:
    def __init__(self):
        self.teams = {}

    def has_team(self, uid):
        return uid in self.teams

    def create_team(self, uid):
        if self.has_team(uid):
            return False
        self.teams[uid] = Team()
        return True