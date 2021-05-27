import numpy as np
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from DataParser import DataParser, BasicPlayerInfo, CurrentMatch

import json
import requests

import pyqtgraph as pg
from Widgets import RatingPlotWidget, TeamTableWidget
from PrefPanel import PrefPanel
from APIStringGenerator import APIStringGenerator

import keys


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        QCoreApplication.setOrganizationName("Aoe2Helper")
        QCoreApplication.setApplicationName("Aoe2Dashboard")

        self.setWindowTitle("AoE 2 Dashboard")
        self.setGeometry(500, 500, 800, 550)
        self.setMaximumSize(self.size())
        self.setMinimumSize(self.size())

        self.player_basic_data: BasicPlayerInfo
        self.opp_basic_data: BasicPlayerInfo
        self.current_match: CurrentMatch = None

        self.opp_rating_plot: RatingPlotWidget = None
        self.player_rating_plot: RatingPlotWidget = None

        self.pref_panel: PrefPanel
        self.timer: QTimer
        self.timer_count = 999
        self.player_id: str

        # Top
        top_label = QLabel("AoE 2 Dashboard", self)
        font: QFont = top_label.font()
        font.setPointSize(18)
        top_label.setFont(font)
        top_label.setAlignment(Qt.AlignCenter)
        top_label.setGeometry(20, 20, 760, 30)

        # Player Label Right Side
        self.player_label = QLabel("Your team", self)
        font: QFont = self.player_label.font()
        font.setPointSize(16)
        self.player_label.setFont(font)
        self.player_label.setAlignment(Qt.AlignCenter)
        self.player_label.setGeometry(480, 70, 300, 25)

        # Opponent Label Left Side
        self.opp_label = QLabel("Opponent's team", self)
        font: QFont = self.opp_label.font()
        font.setPointSize(16)
        self.opp_label.setFont(font)
        self.opp_label.setAlignment(Qt.AlignCenter)
        self.opp_label.setGeometry(20, 70, 250, 25)

        # Player Stats
        players = 4
        self.player_table = TeamTableWidget(1, 4, self)
        self.player_table.setGeometry(480, 110, 300, 20 + players * 25)
        self.player_table.setHidden(True)

        # Opponent Stats
        players = 4
        self.opp_table = TeamTableWidget(2, 4, self)
        self.opp_table.setGeometry(20, 110, 300, 20 + players * 25)
        self.opp_table.setHidden(True)

        self.player_rating_histories = np.empty((2, 4), dtype=tuple)

        # Bar
        pref_icon = QIcon.fromTheme("preferences-system")
        pref_button = QToolButton(self)
        pref_button.setIcon(pref_icon)
        pref_button.setGeometry(750, 500, 35, 35)
        pref_button.clicked.connect(self.open_pref_panel)

        refresh_icon = QIcon.fromTheme("system-software-update")
        refresh_button = QToolButton(self)
        refresh_button.setIcon(refresh_icon)
        refresh_button.setGeometry(700, 500, 35, 35)
        refresh_button.clicked.connect(self.refresh_player)

        self.reload_label = QLabel(self)
        self.reload_label.setGeometry(660, 508, 35, 17)

        font_italic = self.reload_label.font()
        font_italic.setItalic(True)

        tip_str = "Tip: Set your Aoe2.net ID in the settings, then hit reload"
        self.info_label = QLabel(tip_str, self)
        self.info_label.setGeometry(20, 508, 450, 17)
        self.info_label.setFont(font_italic)

        # Info Metadata Bar

        style_sheet_orange = "color: orange"

        label_cur_pl = QLabel("Leaderboard:", self)
        label_cur_pl.setGeometry(20, 470, 100, 17)

        self.leader_board_label = QLabel("", self)
        self.leader_board_label.setGeometry(120, 470, 120, 17)
        self.leader_board_label.setFont(font_italic)
        self.leader_board_label.setStyleSheet(style_sheet_orange)

        label_cur_size = QLabel("Size: ", self)
        label_cur_size.setGeometry(250, 470, 30, 17)

        self.size_label = QLabel("", self)
        self.size_label.setGeometry(290, 470, 30, 17)
        self.size_label.setFont(font_italic)
        self.size_label.setStyleSheet(style_sheet_orange)

        label_cur_map = QLabel("Map:", self)
        label_cur_map.setGeometry(330, 470, 30, 17)

        self.map_label = QLabel("", self)
        self.map_label.setGeometry(370, 470, 120, 17)
        self.map_label.setFont(font_italic)
        self.map_label.setStyleSheet(style_sheet_orange)

        label_cur_server = QLabel("Server:", self)
        label_cur_server.setGeometry(450, 470, 40, 17)

        self.server_label = QLabel("s", self)
        self.server_label.setGeometry(500, 470, 100, 17)
        self.server_label.setFont(font_italic)
        self.server_label.setStyleSheet(style_sheet_orange)

        self.metadata_bar_labels = [label_cur_pl, self.leader_board_label, label_cur_size, self.size_label,
                                    label_cur_map, self.map_label, label_cur_server, self.server_label]
        for e in self.metadata_bar_labels:
            e.setHidden(True)

    def load_infos(self, player_id: int):
        url_str = APIStringGenerator.get_API_string_for_last_match(player_id)
        response = requests.get(url_str)
        last_match = json.loads(response.text)
        new_match = DataParser.parse_current_match(last_match)
        # check if new match is current match
        if self.current_match is not None:
            if new_match.match_uuid == self.current_match.match_uuid:
                print("Same Game")
                return

        self.current_match = new_match
        players_per_team = int(self.current_match.num_players / 2)
        self.player_rating_histories = np.empty(
            (2, players_per_team), dtype=tuple)
        # Player Team
        self.player_table.update_team(new_match.team_1_players)

        # opp Team
        self.opp_table.update_team(new_match.team_2_players)

        self.populate_metadata()

        if self.timer_count == 999:
            self.timer = QTimer()
            self.connect(self.timer, SIGNAL("timeout()"), self.update_data)
            self.timer.start(1000)

    def update_data(self):
        if self.timer_count == 999:
            self.timer_count = 60
        elif self.timer_count == 0:
            self.load_infos(self.player_id)
            self.timer_count = 60
        else:
            self.timer_count -= 1
        self.reload_label.setText(str(self.timer_count) + " s")

    def player_selection_changed(self, team: int, player: int):
        """Team is either 1 or 2, player is zero indexed"""

        player_id = 0
        player_name = "Unknown"
        if team == 1:
            player_info = self.current_match.team_1_players[player]
            player_id = player_info.profile_id
            player_name = player_info.name
        if team == 2:
            player_info = self.current_match.team_2_players[player]
            player_id = player_info.profile_id
            player_name = player_info.name

        ratings = None
        timestamps = None
        item = self.player_rating_histories[team - 1][player]
        if item is not None:
            ratings, timestamps = self.player_rating_histories[team - 1][player]

        if ratings is None:
            count = 50
            leaderboard_id = 4  # Team RM
            url_str = APIStringGenerator.get_API_string_for_rating_history(
                leaderboard_id, player_id, count)
            response = requests.get(url_str)
            data_team_ranking = json.loads(response.text)

            ratings, timestamps = DataParser.compile_ratings_history(
                data_team_ranking)

        plot_widget = RatingPlotWidget(parent=self, player_name=player_name, data_team_ranking=[ratings, timestamps],
                                       axisItems={'bottom': pg.DateAxisItem()})
        if team == 1:
            plot_widget.setGeometry(480, 250, 300, 200)
            if self.player_rating_plot is not None:
                self.player_rating_plot.hide()
            self.player_rating_plot = plot_widget
            self.player_rating_plot.show()
        if team == 2:
            plot_widget.setGeometry(25, 250, 300, 200)
            if self.opp_rating_plot is not None:
                self.opp_rating_plot.hide()
            self.opp_rating_plot = plot_widget
            self.opp_rating_plot.show()

        self.player_rating_histories[team - 1][player] = (ratings, timestamps)

    def populate_metadata(self):
        for e in self.metadata_bar_labels:
            e.setHidden(False)

        self.leader_board_label.setText(
            DataParser.get_key_for_leaderboard(self.current_match.leaderboard_id))
        self.map_label.setText(
            DataParser.get_key_for_map(self.current_match.map_type))
        self.server_label.setText(self.current_match.server)
        num_pl_per_team = str(int(self.current_match.num_players / 2))
        self.size_label.setText(num_pl_per_team + "v" + num_pl_per_team)

    def open_pref_panel(self):
        self.pref_panel = PrefPanel()
        self.pref_panel.setGeometry(500, 500, 300, 150)
        self.pref_panel.show()

    def refresh_player(self):
        current_player_id = self.get_set_player_id()
        if current_player_id != 0:
            self.load_infos(current_player_id)
            self.player_id = current_player_id

    @staticmethod
    def get_set_player_id() -> int:
        settings = QSettings()
        if settings.contains(keys._k_player_id_key):
            player_id = int(settings.value(keys._k_player_id_key))
            return player_id
        else:
            return 0
