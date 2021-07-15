import os.path
from threading import Thread

import requests
from PySide6.QtCore import Signal, QObject
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

    def get_basic_player_data(self, profile_id, finish_signal: Signal):
        thread = Thread(target=self.__get_basic_player_data_task, args=(profile_id, finish_signal))
        thread.start()

    def load_last_matches(self, profile_id: int, count: int, start: int, finish_signal: Signal):
        thread = Thread(target=self.__load_last_matches_task(profile_id, count, start, finish_signal))
        thread.start()

    # Tasks

    def __get_basic_player_data_task(self, profile_id, finish_signal: Signal):
        url_str = APIStringGenerator.get_API_string_for_rating_history(3, profile_id, 1)

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


    @staticmethod
    def get_civ_icon_for_id(civ_id: int) -> QImage:
        mapping = dict()
        with open(os.path.dirname(__file__) + "/../img/civs/_mapping", "r") as read_file:
            mapping_list = read_file.read().split("\n")

            for e in mapping_list:
                l = e.split(",")
                if l[0] == "": break
                mapping.update({int(l[0]): l[1]})

        civ_name = mapping[civ_id]
        path = os.path.dirname(__file__) + "/../img/civs/{}.png".format(civ_name)
        image = QImage(path)

        return image
