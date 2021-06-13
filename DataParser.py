import json
from dataclasses import dataclass

import numpy as np
from PySide6.QtCore import QSettings

import keys


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
        if self.losses == 0:
            return 0
        return self.wins / (self.wins + self.losses) * 100

    @property
    def civ_name(self) -> str:
        if self.civ_id == 999:
            return "Unknown"
        from MainWindow import MainWindow
        civ_name = MainWindow.localized_api_strings.get_key_for_civ(self.civ_id)
        return civ_name


@dataclass
class CurrentMatch:
    match_uuid: str
    map_type: int  # map name
    is_ranked: bool
    num_players: int
    leaderboard_id: int
    server: str

    team_1_players: list[BasicPlayerInfo]
    team_2_players: list[BasicPlayerInfo]


class DataParser:
    """
    This class provides static methods for parsing json from Aoe2.net data.
    Example Data can be found in the example_data directory
    """

    @staticmethod
    def parse_player_data_from_rating_history_and_store(player_json: dict, player_basic_info: BasicPlayerInfo):
        player_basic_info.rating = player_json.get("rating", player_basic_info.rating)
        player_basic_info.wins = player_json.get("num_wins", player_basic_info.wins)
        player_basic_info.losses = player_json.get("num_losses", player_basic_info.losses)

    @staticmethod
    def compile_ratings_history(rating_history: list) -> tuple[list, list]:

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
        match_server = match_info.get("server", "Unknown")

        team_1: list[BasicPlayerInfo] = []
        team_2: list[BasicPlayerInfo] = []

        players = match_info.get("players", [])

        for player in players:
            player_name = player.get("name", "NN")
            player_team = player.get("team", 0)
            player_color = player.get("color", 999)
            player_rating = player.get("rating", 0)
            if player_rating is None:
                # If the last match isnt recent, rating cann be None, will be updated in the Main Menu
                player_rating = 0
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
        player_id = int(settings.value(keys.k_player_id_key))
        player_found = False
        for player in team_1:
            if player.profile_id == player_id:
                player_found = True
        if not player_found:
            team_2_temp = list(team_2)
            team_2 = team_1
            team_1 = team_2_temp

        new_match = CurrentMatch(match_uuid, match_map_type, match_is_ranked, match_num_players, match_leaderboard_id,
                                 match_server, team_1, team_2)
        return new_match


class LocalizedAPIStrings:
    # The next methods provide the language specific names for civs, maps, and the leaderboard
    # Currently a local json file is loaded

    def __init__(self):
        index = 0
        settings = QSettings()
        if settings.contains(keys.k_set_api_locale):
            index = int(settings.value(keys.k_set_api_locale))
        with open("api_strings/locals.csv", "r") as read_file:
            locales = read_file.read().split(",")
            self.locale = locales[index]

        with open(self.get_api_string_file(), "r") as read_file:
            self.locale_data = json.load(read_file)

    def get_key_for_civ(self, civ_id: int) -> str:
        civ_info = self.locale_data.get("civ", 0)
        for civ in civ_info:
            id_enumerate = civ.get("id")
            if id_enumerate == civ_id:
                return civ.get("string")
        return "Unknown"

    def get_key_for_map(self, map_id: int) -> str:
        map_info = self.locale_data.get("map_type", [])
        for map_key in map_info:
            id_enumerate = map_key.get("id")
            if id_enumerate == map_id:
                return map_key.get("string")
        return "Unknown"

    def get_key_for_leaderboard(self, leaderboard_id: int) -> str:
        lb_info = self.locale_data.get("leaderboard", [])
        for lb_id in lb_info:
            id_enumerate = lb_id.get("id")
            if id_enumerate == leaderboard_id:
                return lb_id.get("string")
        return "Unknown"

    def get_api_string_file(self):
        return "api_strings/strings_{}.json".format(self.locale)
