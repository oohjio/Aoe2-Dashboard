import json
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from PySide6.QtCore import QSettings

_k_player_id_key = "player/player_id"


@dataclass
class BasicPlayerInfo:
    name: str
    rating: int
    wins: int
    losses: int

    team: int
    color: int
    civ_id: int

    profile_id: int

    @property
    def win_percentage(self) -> float:
        if self.losses == 0: return 0
        return self.wins / (self.wins + self.losses) * 100

    @property
    def civ_name(self) -> str:
        if self.civ_id == 999: return "Unknown"
        return DataParser.get_key_for_civ(self.civ_id)


@dataclass
class CurrentMatch:
    match_uuid: str
    map_type: int  # map name
    is_ranked: bool
    num_players: int
    leaderboard_id: int

    team_1_players: [BasicPlayerInfo]
    team_2_players: [BasicPlayerInfo]


class DataParser:

    @staticmethod
    def compile_ratings_history(rating_history: list) -> ([], []):

        ratings = np.zeros(len(rating_history), dtype=int)
        timestamps = np.zeros(len(rating_history), dtype=int)

        for index, step in enumerate(rating_history):
            ratings[index] = step.get("rating", 0)
            timestamps[index] = step.get("timestamp", 0)

        return ratings, timestamps

    @staticmethod
    def parse_current_match(last_match: dict) -> CurrentMatch:
        match_info: dict = last_match.get("last_match", {})
        # Match MetaData
        match_uuid = match_info.get("match_uuid", "XXXX")
        match_num_players = match_info.get("num_players")
        match_map_type = match_info.get("map_type", 999)
        match_is_ranked = match_info.get("ranked", False)
        match_leaderboard_id = match_info.get("leaderboard_id", 999)

        team_1: [BasicPlayerInfo] = []
        team_2: [BasicPlayerInfo] = []

        players = match_info.get("players", [])

        for player in players:
            player_name = player.get("name", "NN")
            player_team = player.get("team", 0)
            player_color = player.get("color", 999)
            player_rating = player.get("rating", 0)
            player_civ_id = player.get("civ", 999)
            player_profile_id = player.get("profile_id", 0)

            player_info = BasicPlayerInfo(player_name, player_rating, 0, 0, player_team, player_color, player_civ_id,
                                          player_profile_id)
            if player_team == 1:
                team_1.append(player_info)
            if player_team == 2:
                team_2.append(player_info)

        # check if team 1 has player, else switch
        settings = QSettings()
        player_id = int(settings.value(_k_player_id_key))
        player_found = False
        for player in team_1:
            if player.profile_id == player_id: player_found = True
        if not player_found:
            team_2_temp = list(team_2)
            team_2 = team_1
            team_1 = team_2_temp

        new_match = CurrentMatch(match_uuid, match_map_type, match_is_ranked, match_num_players, match_leaderboard_id,
                                 team_1, team_2)
        return new_match

    @staticmethod
    def get_key_for_civ(civ_id: int) -> str:
        with open("example_data/string_list_aoe2net.json", "r") as read_file:
            data = json.load(read_file)
            civ_info = data.get("civ", 0)
            for civ in civ_info:
                id_enumerate = civ.get("id")
                if id_enumerate == civ_id: return civ.get("string")
            return "Unknown"
