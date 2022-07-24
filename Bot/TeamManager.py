from Bot.Team import Team
import uuid


class TeamManager:
    def __init__(self):
        self.teams = {}
        self.team_member_index = {}

    def create_team(self, name: str):
        team_id = uuid.uuid4().hex
        self.teams[team_id] = Team(name)
        return team_id
