import time

import numpy as np
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from DataParser import DataParser, BasicPlayerInfo, CurrentMatch

import json
import pyqtgraph as pg
from Widgets import RatingPlotWidget, TeamTableWidget


class MainWindow(QWidget):
    player_basic_data: BasicPlayerInfo
    opp_basic_data: BasicPlayerInfo
    current_match: CurrentMatch

    def __init__(self):
        super().__init__()

        self.setWindowTitle("AoE 2 Dashboard")
        self.setGeometry(QRect(300, 200, 800, 600))

        # Top
        top_label = QLabel("AoE 2 Dashboard", self)
        font: QFont = top_label.font()
        font.setPointSize(20)
        top_label.setFont(font)
        top_label.setAlignment(Qt.AlignCenter)
        top_label.setGeometry(QRect(100, 20, 600, 30))

        # Player Label Right Side
        self.player_label = QLabel("Player", self)
        font: QFont = self.player_label.font()
        font.setPointSize(16)
        self.player_label.setFont(font)
        self.player_label.setAlignment(Qt.AlignCenter)
        self.player_label.setGeometry(QRect(550, 70, 150, 25))

        # Opponent Label Left Side
        self.opp_label = QLabel("Opponent", self)
        font: QFont = self.opp_label.font()
        font.setPointSize(16)
        self.opp_label.setFont(font)
        self.opp_label.setAlignment(Qt.AlignCenter)
        self.opp_label.setGeometry(QRect(50, 70, 150, 25))

        # Player Stats
        players = 4
        self.player_table = TeamTableWidget(4, self)
        self.player_table.setGeometry(480, 100, 300, 20 + players * 25)


        # Opponent Stats
        players = 4
        self.opp_table = TeamTableWidget(4, self)
        self.opp_table.setGeometry(20, 100, 300, 20 + players * 25)

        self.load_infos()

    def load_infos(self):
        data_parser = DataParser()

        # Basic Player Data
        with open("example_data/player_ratinghistory.json", "r") as read_file:
            rating_history = json.load(read_file)

            self.player_basic_data = DataParser.parse_basic_player_info(rating_history)

            self.player_table.update_player(0, self.player_basic_data)

        # Opponent Player Data
        with open("example_data/current_match.json", "r") as read_file:
            last_match = json.load(read_file)

            self.current_match = DataParser.parse_current_match(last_match)
            self.opp_label.setText(self.current_match.opp_name)

        # get Opponent Data witch Rating Request
        with open("example_data/opponent_ratinghistory.json", "r") as read_file:
            rating_history = json.load(read_file)

            self.opp_basic_data = DataParser.parse_basic_player_info(rating_history)

            self.opp_table.update_player(0, self.opp_basic_data)


        # draw Rating of Player
        with open("example_data/player_ratinghistory.json", "r") as read_file:
            rating_history = json.load(read_file)
            ratings, timestamps = DataParser.compile_ratings_history(rating_history)

            plot_widget = RatingPlotWidget(parent=self, data1v1=[ratings, timestamps],
                                           axisItems={'bottom': pg.DateAxisItem()})
            plot_widget.setGeometry(480, 250, 300, 200)

        # draw Rating of Opp
        with open("example_data/opponent_ratinghistory.json", "r") as read_file:
            rating_history = json.load(read_file)
            ratings, timestamps = DataParser.compile_ratings_history(rating_history)

            plot_widget = RatingPlotWidget(parent=self, data1v1=[ratings, timestamps],
                                           axisItems={'bottom': pg.DateAxisItem()})
            plot_widget.setGeometry(25, 250, 300, 200)


        with open("example_data/current_match_3v3.json", "r") as read_file:
            last_match = json.load(read_file)
            DataParser.parse_current_match_team(last_match)