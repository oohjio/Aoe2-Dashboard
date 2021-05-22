import json
from dataclasses import dataclass
from datetime import datetime
import numpy as np


@dataclass
class BasicPlayerInfo:
    rating: int
    wins: int
    losses: int

    @property
    def win_percentage(self) -> float:
        if self.losses == 0: return 0
        return self.wins / (self.wins + self.losses) * 100


@dataclass
class CurrentMatch:
    opp_name: str
    opp_clan: str
    opp_steam_id: int

@dataclass
class CurrentMatchTeam:
    match_uuid: int



class DataParser:

    @staticmethod
    def parse_basic_player_info(player_data: list) -> BasicPlayerInfo:
        if len(player_data) != 0:
            last_match: dict = player_data[0]

            rating = last_match.get("rating", 0)
            wins = last_match.get("num_wins", 0)
            losses = last_match.get("num_losses", 0)

            return BasicPlayerInfo(rating, wins, losses)

        else:
            return BasicPlayerInfo(0, 0, 0)

    @staticmethod
    def parse_current_match(last_match: dict) -> CurrentMatch:
        # print(json.dumps(last_match, indent=2))
        name = last_match.get("name", "No Name")
        steam_id = last_match.get("steam_id", 0)
        clan = last_match.get("clan", "No Clan")

        return CurrentMatch(name, clan, steam_id)

    @staticmethod
    def compile_ratings_history(rating_history: list) -> ([], []):

        ratings = np.zeros(len(rating_history), dtype=int)
        timestamps = np.zeros(len(rating_history), dtype=int)

        for index, step in enumerate(rating_history):
            ratings[index] = step.get("rating", 0)
            timestamps[index] = step.get("timestamp", 0)

        return ratings, timestamps

    @staticmethod
    def parse_current_match_team(last_match: dict):
        # print(json.dumps(last_match, indent=2))
        match_info: dict = last_match.get("last_match", {})
        players = match_info.get("players", [])

        for player in players:
            # print(json.dumps(player, indent=2))
            player_name = player.get("name", "NN")
            player_team = player.get("team", 0)
            player_color = player.get("")
            print(player_name, player_team)