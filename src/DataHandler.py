#  Copyright (C)  2021 oohjio, https://github.com/oohjio
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License v3 as published by the Free Software Foundation.

import os.path
from threading import Thread

import requests
from PySide6.QtCore import Signal, QObject, QThread
from PySide6.QtGui import QImage

from APIStringGenerator import APIStringGenerator
from DataParser import *


class DataHandler(QObject):
    """
    This is a convenience wrapper around the DataParser, provides Multithreading
    Not yet used in the Main Application
    """
    # Todo: use QThreads and QNetworkManager

    def __init__(self):
        super().__init__()

    def get_basic_player_data_for_leaderboard(self, leaderboard_id, profile_id, finish_signal: Signal):
        thread = Thread(target=self.__get_basic_player_data_task, args=(leaderboard_id, profile_id, finish_signal))
        thread.start()

    def load_last_matches(self, profile_id: int, count: int, start: int, finish_signal: Signal):
        thread = Thread(target=self.__load_last_matches_task, args=(profile_id, count, start, finish_signal))
        thread.start()

    def load_rating_history_all_lb(self, profile_id: int, count: int, finish_signal: Signal):
        thread = Thread(target=self.__load_rating_history__all_lb_task, args=(profile_id, count, finish_signal))
        thread.start()
    def load_match_with_timestamp_for_leaderboard(self, profile_id: int, timestamp: int, leaderboard_id: int, finish_signal):
        thread = Thread(target=self.__load_match_with_timestamp_for_leaderboard_task, args=(profile_id, timestamp, leaderboard_id, finish_signal))
        thread.start()

    # Tasks

    def __get_basic_player_data_task(self, leaderboard_id, profile_id, finish_signal: Signal):
        url_str = APIStringGenerator.get_API_string_for_rating_history(leaderboard_id, profile_id, 1)

        try:
            response = requests.get(url_str)
            player_info = DataParser.parse_player_data_from_rating_history_object(json.loads(response.text)[0])
        except:
            print("Network Error")
            return_tuple = (0, None)
            finish_signal.emit(return_tuple)
        else:
            return_tuple = (1, player_info)
            finish_signal.emit(return_tuple)

    def __load_last_matches_task(self, profile_id: int, count: int, start: int, finish_signal: Signal):
        url_str = APIStringGenerator.get_API_string_for_match_history(profile_id, count, start)
        try:
            response = requests.get(url_str)
            match_history = DataParser.parse_multiple_matches(json.loads(response.text))
        except:
            print("Network Error")
            return_tuple = (0, None)
            finish_signal.emit(return_tuple)
        else:
            return_tuple = (1, match_history)
            finish_signal.emit(return_tuple)

    def __load_rating_history__all_lb_task(self, profile_id: int, count: int, finish_signal: Signal):
        url_str_1v1_RM = APIStringGenerator.get_API_string_for_rating_history(3, profile_id, count)
        url_str_1v1_EW = APIStringGenerator.get_API_string_for_rating_history(13, profile_id, count)

        url_str_team_RM = APIStringGenerator.get_API_string_for_rating_history(4, profile_id, count)
        url_str_team_EW = APIStringGenerator.get_API_string_for_rating_history(14, profile_id, count)

        try:
            response_team_RM = requests.get(url_str_team_RM)
            data_team_ranking_RM = json.loads(response_team_RM.text)

            response_1v1_RM = requests.get(url_str_1v1_RM)
            data_1v1_ranking_RM = json.loads(response_1v1_RM.text)

            ratings_team_RM, timestamps_team_RM = DataParser.compile_ratings_history(
                data_team_ranking_RM)
            ratings_1v1_RM, timestamps_1v1_RM = DataParser.compile_ratings_history(
                data_1v1_ranking_RM)

            response_team_EW = requests.get(url_str_team_EW)
            data_team_ranking_EW = json.loads(response_team_EW.text)

            response_1v1_EW = requests.get(url_str_1v1_EW)
            data_1v1_ranking_EW = json.loads(response_1v1_EW.text)

            ratings_team_EW, timestamps_team_EW = DataParser.compile_ratings_history(data_team_ranking_EW)
            ratings_1v1_EW, timestamps_1v1_EW = DataParser.compile_ratings_history(data_1v1_ranking_EW)
        except:
            print("Network Error")
            return_tuple = (0, None)
            finish_signal.emit(return_tuple)
        else:
            data = [ratings_1v1_RM, timestamps_1v1_RM, ratings_team_RM, timestamps_team_RM,
                    ratings_1v1_EW, timestamps_1v1_EW, ratings_team_EW, timestamps_team_EW]
            return_tuple = (1, data)
            finish_signal.emit(return_tuple)

    def __load_match_with_timestamp_for_leaderboard_task(self, profile_id: int, timestamp: int, leaderboard_id: int, finish_signal):
        pass

    @staticmethod
    def get_civ_icon_for_id(civ_id: int) -> QImage:
        mapping = dict()
        with open(os.path.dirname(__file__) + "/../img/civs/_mapping", "r") as read_file:
            mapping_list = read_file.read().split("\n")

            for e in mapping_list:
                l = e.split(",")
                if l[0] == "": break
                mapping.update({int(l[0]): l[1]})
        try:
            civ_name = mapping[civ_id]
        except KeyError:
            # Todo: Default Civ Icon
            civ_name = "aztecs"
            path = os.path.dirname(__file__) + "/../img/civs/{}.png".format(civ_name)
            image = QImage(path)
        else:
            path = os.path.dirname(__file__) + "/../img/civs/{}.png".format(civ_name)
            image = QImage(path)

        return image
