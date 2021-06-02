import json
from inspect import currentframe
#from os import stat
from threading import Thread
import platform

import numpy as np
import pyqtgraph as pg
import requests
from pyqtgraph.debug import printTrace
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import keys
from APIStringGenerator import APIStringGenerator
from DataParser import BasicPlayerInfo, CurrentMatch, DataParser
from PrefPanel import PrefPanel
from Widgets import RatingPlotWidget, TeamTableWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        QCoreApplication.setOrganizationName("Aoe2Helper")
        QCoreApplication.setApplicationName("Aoe2Dashboard")

        system = platform.system()
        if system == "Windows":
            self.is_running_windows = True
        else:
            self.is_running_windows = False

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
        # set the timer_count to 999 indicating that no timer has started yet
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

        self.player_rating_histories_team = np.empty((2, 4), dtype=tuple)
        self.player_rating_histories_1v1 = np.empty((2, 4), dtype=tuple)

        # Bar
        pref_icon = QIcon.fromTheme("preferences-system")
        if pref_icon == None or self.is_running_windows:
            pref_icon = QIcon("ressources/settings_black_24dp.svg")
        pref_button = QToolButton(self)
        pref_button.setIcon(pref_icon)
        pref_button.setGeometry(750, 500, 35, 35)
        pref_button.clicked.connect(self.open_pref_panel)

        refresh_icon = QIcon.fromTheme("system-software-update")
        if refresh_icon == None or self.is_running_windows:
            refresh_icon = QIcon("ressources/cached_black_24dp.svg")
        refresh_button = QToolButton(self)
        refresh_button.setIcon(refresh_icon)
        refresh_button.setGeometry(700, 500, 35, 35)
        refresh_button.clicked.connect(self.refresh_player)

        self.reload_label = QLabel(self)
        self.reload_label.setGeometry(660, 508, 35, 17)

        font_italic = self.reload_label.font()
        font_italic.setItalic(True)

        font_bold = self.reload_label.font()
        font_bold.setBold(True)

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

        self.server_label = QLabel("", self)
        self.server_label.setGeometry(500, 470, 100, 17)
        self.server_label.setFont(font_italic)
        self.server_label.setStyleSheet(style_sheet_orange)

        # Display Legende
        legende_label = QLabel("Legend", self)
        legende_label.setGeometry(340, 370, 100, 17)
        legende_label.setFont(font_bold)

        rating_1v1_legende_label = QLabel("1v1 Rank", self)
        rating_1v1_legende_label.setGeometry(385, 395, 80, 17)

        rating_team_legende_label = QLabel("Team Rank", self)
        rating_team_legende_label.setGeometry(385, 420, 80, 17)

        # Display Options
        options_label = QLabel("Options", self)
        options_label.setGeometry(340, 250, 100, 17)
        options_label.setFont(font_bold)

        check_box_1v1 = QCheckBox("Display 1v1", self)
        check_box_1v1.setGeometry(340, 280, 110, 17)
        check_box_1v1.setChecked(
            MainWindow.get_1v1_display_option_from_settings())

        check_box_team = QCheckBox("Display Team", self)
        check_box_team.setGeometry(340, 310, 110, 17)
        check_box_team.setChecked(
            MainWindow.get_team_display_option_from_settings())

        check_box_1v1.stateChanged.connect(self.check_box_1v1_changed)
        check_box_team.stateChanged.connect(self.check_box_team_changed)

        # alle Metadata und Legenden Labels are added to this array to then set to be hidden
        self.hidden_labels = [label_cur_pl, self.leader_board_label, label_cur_size, self.size_label,
                              label_cur_map, self.map_label, label_cur_server, self.server_label, rating_team_legende_label, rating_1v1_legende_label, legende_label]
        for e in self.hidden_labels:
            e.setHidden(True)

    def paintEvent(self, e):
        if self.current_match == None:
            return
        painter = QPainter(self)

        # 1v1 line
        pen_1v1 = pg.mkPen((255, 96, 62), width=2)
        painter.setPen(pen_1v1)
        painter.drawLine(340, 405, 375, 405)

        # Team Rating Line
        pen_team = pg.mkPen((15, 153, 246), width=2)
        painter.setPen(pen_team)
        painter.drawLine(340, 430, 375, 430)
        painter.end()

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
        self.player_rating_histories_team = np.empty(
            (2, players_per_team), dtype=tuple)
        self.player_rating_histories_1v1 = np.empty(
            (2, players_per_team), dtype=tuple)
        # Player Team
        self.player_table.update_team(new_match.team_1_players)

        # opp Team
        self.opp_table.update_team(new_match.team_2_players)

        self.populate_metadata()
        self.update()

        if self.timer_count == 999:
            self.timer = QTimer()
            self.connect(self.timer, SIGNAL("timeout()"), self.update_timer)
            self.timer.start(1000)

    def update_player_profiles(self):
        for player in self.current_match.team_1_players:
            url_str = APIStringGenerator.get_API_string_for_rating_history(
                self.current_match.leaderboard_id, player.profile_id, 1)
            response = requests.get(url_str)
            DataParser.parse_player_data_from_rating_history_and_store(
                json.loads(response.text)[0], player)

        for player in self.current_match.team_2_players:
            url_str = APIStringGenerator.get_API_string_for_rating_history(
                self.current_match.leaderboard_id, player.profile_id, 1)
            response = requests.get(url_str)
            DataParser.parse_player_data_from_rating_history_and_store(
                json.loads(response.text)[0], player)

    def update_timer(self):
        """This is getting called every second by the timer. If timer_count == 999 that meens that its the first call since programm start"""
        if self.timer_count == 999:
            self.timer_count = 60
        elif self.timer_count == 0:
            self.load_infos(self.player_id)
            self.timer_count = 60
        elif self.timer_count == 50:
            # update Player
            thread = Thread(target=self.update_player_profiles)
            thread.start()
            self.timer_count -= 1
        elif self.timer_count == 40:
            self.player_table.update_team(self.current_match.team_1_players)
            self.opp_table.update_team(self.current_match.team_2_players)
            self.timer_count -= 1
        else:
            self.timer_count -= 1
        self.reload_label.setText(str(self.timer_count) + " s")

    def player_selection_changed(self, team: int, player: int):
        """This method gets caled by the Team Table Widget that indicates that selection has changed and the Rating Plot needs to display the rating of another player. 
            :params team is either 1 or 2, player is zero indexed"""

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

        ratings_team = None
        timestamps_team = None

        # for sparring network ressources the rating history can be reused
        # in player_rating_histories is an array that cointains for each player in a matrix a tuple with ratings and timestamps
        item = self.player_rating_histories_team[team - 1][player]
        if item is not None:
            ratings_team, timestamps_team = self.player_rating_histories_team[team - 1][player]
            ratings_1v1, timestamps_1v1 = self.player_rating_histories_1v1[team - 1][player]

        if ratings_team is None:
            count = 50
            leaderboard_id_1v1 = 3  # 1v1 RM
            leaderboard_id_team = 4  # Team RM

            url_str_1v1 = APIStringGenerator.get_API_string_for_rating_history(
                leaderboard_id_1v1, player_id, count)
            url_str_team = APIStringGenerator.get_API_string_for_rating_history(
                leaderboard_id_team, player_id, count)

            response_team = requests.get(url_str_team)
            data_team_ranking = json.loads(response_team.text)

            response_1v1 = requests.get(url_str_1v1)
            data_1v1_ranking = json.loads(response_1v1.text)

            ratings_team, timestamps_team = DataParser.compile_ratings_history(
                data_team_ranking)
            ratings_1v1, timestamps_1v1 = DataParser.compile_ratings_history(
                data_1v1_ranking)

        plot_widget = RatingPlotWidget(parent=self, player_name=player_name)
        plot_widget.plot_rating(
            ratingdata=[ratings_team, timestamps_team], leaderboard_id=4)
        plot_widget.plot_rating(
            ratingdata=[ratings_1v1, timestamps_1v1], leaderboard_id=3)

        if team == 1:
            plot_widget.setGeometry(480, 250, 300, 200)
            if self.player_rating_plot is not None:
                self.player_rating_plot.hide()
            self.player_rating_plot = plot_widget
            self.player_rating_plot.show()
        if team == 2:
            plot_widget.setGeometry(15, 250, 300, 200)
            if self.opp_rating_plot is not None:
                self.opp_rating_plot.hide()
            self.opp_rating_plot = plot_widget
            self.opp_rating_plot.show()

        self.player_rating_histories_team[team -
                                          1][player] = (ratings_team, timestamps_team)
        self.player_rating_histories_1v1[team -
                                         1][player] = (ratings_1v1, timestamps_1v1)

        plot_widget.update_displayed_plots(
            3, MainWindow.get_1v1_display_option_from_settings())
        plot_widget.update_displayed_plots(
            4, MainWindow.get_team_display_option_from_settings())

    def populate_metadata(self):
        """Displays interesting data from the current match like server, Leaderboard etc."""
        for e in self.hidden_labels:
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
        """Loads a player_id from QSettings if none was yet set in the runtime"""
        current_player_id = self.get_player_id_from_settings()
        if current_player_id != 0:
            self.load_infos(current_player_id)
            self.player_id = current_player_id

    def update_display_options(self, leaderboard_id, checked):
        if self.player_rating_plot == None:
            return
        self.player_rating_plot.update_displayed_plots(leaderboard_id, checked)
        self.opp_rating_plot.update_displayed_plots(leaderboard_id, checked)

    def check_box_1v1_changed(self, state: int):
        # 0: not checked, 2: checked
        checked = True if state == 2 else False
        MainWindow.set_1v1_display_option_in_settings(checked)

        self.update_display_options(3, checked)

    def check_box_team_changed(self, state: int):
        # 0: not checked, 2: checked
        checked = True if state == 2 else False
        MainWindow.set_team_display_option_in_settings(checked)

        self.update_display_options(4, checked)

    @staticmethod
    def get_player_id_from_settings() -> int:
        """This is returning the player_id saved via QSettings"""
        settings = QSettings()
        if settings.contains(keys._k_player_id_key):
            player_id = int(settings.value(keys._k_player_id_key))
            return player_id
        else:
            return 0

    @staticmethod
    def get_1v1_display_option_from_settings() -> bool:
        settings = QSettings()
        if settings.contains(keys._k_1v1_display_option):
            checked = settings.value(keys._k_1v1_display_option)
            print("1v1", checked)
            if checked == "false":
                return False
            else:
                return True
        else:
            return True

    @staticmethod
    def get_team_display_option_from_settings() -> bool:
        settings = QSettings()
        if settings.contains(keys._k_team_display_option):
            checked = settings.value(keys._k_team_display_option)
            print("team", checked)
            if checked == "false":
                return False
            else:
                return True
        else:
            return True

    @staticmethod
    def set_1v1_display_option_in_settings(checked: bool):
        settings = QSettings()
        settings.setValue(keys._k_1v1_display_option, checked)

    @staticmethod
    def set_team_display_option_in_settings(checked: bool):
        settings = QSettings()
        settings.setValue(keys._k_team_display_option, checked)
