
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

_k_player_id_key = "player/player_id"


class MainWindow(QMainWindow):
    player_basic_data: BasicPlayerInfo
    opp_basic_data: BasicPlayerInfo
    current_match: CurrentMatch = None

    opp_rating_plot: RatingPlotWidget = None
    player_rating_plot: RatingPlotWidget = None

    pref_panel: PrefPanel
    timer: QTimer
    timer_count = 999
    player_id: str

    def __init__(self):
        super().__init__()

        QCoreApplication.setOrganizationName("Aoe2Helper")
        QCoreApplication.setApplicationName("Aoe2Dashboard")

        self.setWindowTitle("AoE 2 Dashboard")
        self.setGeometry(QRect(300, 200, 800, 600))

        # Top
        top_label = QLabel("You are currently playing no match", self)
        font: QFont = top_label.font()
        font.setPointSize(18)
        top_label.setFont(font)
        top_label.setAlignment(Qt.AlignCenter)
        top_label.setGeometry(QRect(20, 20, 760, 30))

        # Player Label Right Side
        self.player_label = QLabel("Your team", self)
        font: QFont = self.player_label.font()
        font.setPointSize(16)
        self.player_label.setFont(font)
        self.player_label.setAlignment(Qt.AlignCenter)
        self.player_label.setGeometry(QRect(480, 70, 300, 25))

        # Opponent Label Left Side
        self.opp_label = QLabel("Opponent's team", self)
        font: QFont = self.opp_label.font()
        font.setPointSize(16)
        self.opp_label.setFont(font)
        self.opp_label.setAlignment(Qt.AlignCenter)
        self.opp_label.setGeometry(QRect(20, 70, 250, 25))

        # Player Stats
        players = 4
        self.player_table = TeamTableWidget(1, 4, self)
        self.player_table.setGeometry(480, 110, 300, 20 + players * 25)

        # Opponent Stats
        players = 4
        self.opp_table = TeamTableWidget(2, 4, self)
        self.opp_table.setGeometry(20, 110, 300, 20 + players * 25)

        self.player_rating_histories = np.empty((2, 4), dtype=tuple)

        # Bar

        pref_icon = QIcon.fromTheme("preferences-system")
        pref_button = QToolButton(self)
        pref_button.setIcon(pref_icon)
        pref_button.setGeometry(750, 550, 35, 35)
        pref_button.clicked.connect(self.open_pref_panel)

        refresh_icon = QIcon.fromTheme("system-software-update")
        refresh_button = QToolButton(self)
        refresh_button.setIcon(refresh_icon)
        refresh_button.setGeometry(700, 550, 35, 35)
        refresh_button.clicked.connect(self.refresh_player)

        self.reload_label = QLabel(self)
        self.reload_label.setGeometry(660, 560, 35, 17)

    def load_infos(self, player_id: int):
        url_str = "https://aoe2.net/api/player/lastmatch?game=aoe2de&profile_id=" + str(player_id)
        response = requests.get(url_str)
        last_match = json.loads(response.text)
        new_match = DataParser.parse_current_match(last_match)
        # check if new match is current match
        if self.current_match is not None:
            if new_match.match_uuid == self.current_match.match_uuid:
                print("Same Game")
                return

        self.current_match = new_match

        # Player Team
        self.player_table.update_team(new_match.team_1_players)

        # opp Team
        self.opp_table.update_team(new_match.team_2_players)
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
            url_str = "https://aoe2.net/api/player/ratinghistory?game=aoe2de&leaderboard_id=4&profile_id=" \
                      + str(player_id) + "&count=" + str(count)
            response = requests.get(url_str)
            data_team_ranking = json.loads(response.text)

            ratings, timestamps = DataParser.compile_ratings_history(data_team_ranking)

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
        if settings.contains(_k_player_id_key):
            player_id = int(settings.value(_k_player_id_key))
            return player_id
        else:
            return 0
