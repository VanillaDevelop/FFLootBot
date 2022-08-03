from Bot.Team import Team
import uuid


class TeamManager:
    def __init__(self):
        self.teams = {}
        # maps author IDs to team IDs
        self.team_leaders = {}
        # maps message IDs to team IDs
        self.team_members = {}

    def create_team(self, name: str):
        team_id = uuid.uuid4().hex
        self.teams[team_id] = Team(name)
        return team_id
