import json
import os.path
from dataclasses import dataclass

import arrow
import numpy as np
from PySide6.QtCore import QSettings

import keys as keys


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
    def win_percentage_str(self) -> str:
        if self.losses == 0:
            return "0"
        return "{:10.2f} %".format(self.wins / (self.wins + self.losses) * 100)

    @property
    def civ_name(self) -> str:
        if self.civ_id == 999:
            return "Unknown"
        from MainWindow import MainWindow
        civ_name = MainWindow.localized_api_strings.get_key_for_civ(self.civ_id)
        return civ_name


@dataclass
class Match:
    match_uuid: str
    map_type: int  # map name
    is_ranked: bool
    num_players: int
    leaderboard_id: int
    server: str
    time_str: str

    team_1_players: list[BasicPlayerInfo]
    team_2_players: list[BasicPlayerInfo]

    @property
    def time_started_humanized(self) -> str:
        time = arrow.get(self.time_str)

        return time.humanize()

    @property
    def time_started_plain(self) -> str:
        time = arrow.get(self.time_str)

        return time.format()


class DataParser:
    """
    This class provides static methods for parsing json from Aoe2.net data.
    Example Data can be found in the example_data directory
    """

    @staticmethod
    def parse_player_data_from_rating_history_object(rating_json: dict) -> BasicPlayerInfo:
        name = ""
        rating = rating_json.get("rating", 0)
        wins = rating_json.get("num_wins", 0)
        losses = rating_json.get("num_losses", 0)

        player_data = BasicPlayerInfo(name, rating, wins, losses, 0, 0, 0, 0)
        return player_data

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
    def parse_multiple_matches(matches: list) -> []:
        return_list = []
        for match in matches:
            return_list.append(DataParser.parse_match(match))

        return return_list

    @staticmethod
    def parse_current_match(last_match: dict) -> Match:
        match_info: dict = last_match.get("last_match", {})
        return DataParser.parse_match(match_info)

    @staticmethod
    def parse_match(match: dict) -> Match:
        # Match MetaData
        match_uuid = match.get("match_uuid", "_")
        match_num_players = match.get("num_players")
        match_map_type = match.get("map_type", 999)
        match_is_ranked = match.get("ranked", False)
        match_leaderboard_id = match.get("leaderboard_id", 999)
        match_server = match.get("server", "Unknown")
        match_time = match.get("started", "0")

        team_1: list[BasicPlayerInfo] = []
        team_2: list[BasicPlayerInfo] = []

        players = match.get("players", [])

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
        profile_id = int(settings.value(keys.k_profile_id_key))
        player_found = False
        for player in team_1:
            if player.profile_id == profile_id:
                player_found = True
        if not player_found:
            team_2_temp = list(team_2)
            team_2 = team_1
            team_1 = team_2_temp

        new_match = Match(match_uuid, match_map_type, match_is_ranked, match_num_players, match_leaderboard_id,
                          match_server, match_time, team_1, team_2)
        return new_match


class LocalizedAPIStrings:
    # The next methods provide the language specific names for civs, maps, and the leaderboard
    # Currently a local json file is loaded

    def __init__(self):
        index = 0
        settings = QSettings()
        if settings.contains(keys.k_opt_api_locale):
            index = int(settings.value(keys.k_opt_api_locale))
        with open(os.path.dirname(__file__) + "/../data/api_strings/locals.csv", "r") as read_file:
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
        return "{}/../data/api_strings/strings_{}.json".format(os.path.dirname(__file__), self.locale)
