from typing import Optional

from Bot.Player import Player
from Bot.Team import Team
import uuid


class TeamManager:
    def __init__(self):
        # maps team ids to teams
        self.__teams = {}
        # maps author IDs to team IDs
        self.__team_leaders = {}
        # maps message IDs to team IDs
        self.__team_members = {}

    # creates a team and returns the corresponding team ID
    def create_team(self, team_name: str, author_id: int) -> Team:
        team_id = str(uuid.uuid4().hex)
        self.__teams[team_id] = Team(team_id, team_name)
        self.__team_leaders[author_id] = team_id
        return self.get_team_by_leader(author_id)

    # assigns a message id to a team
    def map_message_id_to_team(self, message_id: str, team: Team, player: Player) -> None:
        self.__team_members[message_id] = team.get_uuid()
        player.player_message_id = message_id

    # if a team exists from given author ID, return the team
    def get_team_by_leader(self, author_id: int) -> Optional[Team]:
        if author_id in self.__team_leaders:
            return self.__teams[self.__team_leaders[author_id]]
        return None

    # if a team exists from given message ID, return the team
    def get_team_by_member(self, message_id: int) -> Optional[Team]:
        if message_id in self.__team_members:
            return self.__teams[self.__team_members[message_id]]
        return None

    # if a team exists with given team ID, return the team
    def get_team_by_uuid(self, team_id: str) -> Optional[Team]:
        if team_id in self.__teams:
            return self.__teams[team_id]
        return None

    # get the IDs of all existing teams
    def get_all_team_ids(self) -> list:
        return list(self.__teams.keys())

    # removes a player from a team
    def leave_team(self, message_id: int, team: Team, player: Player):
        self.__team_members.pop(message_id)
        team.leave(player)

    def delete_team(self, team: Team, leader: Player):
        for member in team.get_all_member_ids():
            player = team.get_member_by_author_id(member)
            del self.__team_members[player.player_message_id]
        del self.__team_leaders[leader.player_author_id]
        self.__teams.pop(team.get_uuid())