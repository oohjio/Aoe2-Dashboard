#  Copyright (C)  2021 oohjio, https://github.com/oohjio
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License v3 as published by the Free Software Foundation.

import json
import os.path
import platform
from threading import Thread

import numpy as np
import requests
from PySide2.QtCore import QCoreApplication, QTimer, SIGNAL, Qt, Signal
from PySide2.QtGui import QFont, QIcon
from PySide2.QtWidgets import QLabel, QToolButton, QVBoxLayout, QHBoxLayout, QGridLayout, QCheckBox, \
    QWidget, QMessageBox, QProgressBar

from APIStringGenerator import APIStringGenerator
from AnalyticsWindow import AnalyticsWindow
from AcknowledgementsWindow import AcknowledgementsWindow
from DataParser import BasicPlayerInfo, Match, DataParser, LocalizedAPIStrings
from PrefPanel import PrefPanel
from SettingsHandler import SettingsHandler
from Widgets import LegendItem, RatingPlotWidget, TeamTableWidget


# noinspection PyUnresolvedReferences
class MainWindow(QWidget):
    QCoreApplication.setOrganizationName("Aoe2Helper")
    QCoreApplication.setApplicationName("Aoe2Dashboard")
    localized_api_strings = LocalizedAPIStrings()

    sig_player_data_updated = Signal()
    sig_player_data_loaded = Signal()
    sig_rating_history_loaded = Signal(tuple)

    is_running_windows = True

    def __init__(self):
        super().__init__()

        self.dark_theme = True

        system = platform.system()
        if system == "Windows":
            self.is_running_windows = True
        elif system == "Darwin":
            self.is_running_windows = False
        else:
            self.is_running_windows = False

        # SIGNALS
        self.sig_player_data_updated.connect(self.player_profiles_updated)
        self.sig_player_data_loaded.connect(self.player_data_loaded)
        self.sig_rating_history_loaded.connect(self.player_rating_history_loaded)

        # UI

        self.setWindowTitle("AoE 2 Dashboard")
        self.setGeometry(500, 500, 800, 550)
        self.active_windows = [self]

        self.player_basic_data: BasicPlayerInfo
        self.opp_basic_data: BasicPlayerInfo
        self.current_match: Match = None

        self.opp_rating_plot: RatingPlotWidget = None
        self.player_rating_plot: RatingPlotWidget = None

        self.opp_busy_indicator = QProgressBar()
        self.opp_busy_indicator.setMaximumHeight(10)
        self.opp_busy_indicator.setTextVisible(False)
        self.opp_busy_indicator.setMinimum(0)
        self.opp_busy_indicator.setMaximum(0)
        self.opp_busy_indicator.setHidden(True)

        self.player_busy_indicator = QProgressBar()
        self.player_busy_indicator.setMaximumHeight(10)
        self.player_busy_indicator.setTextVisible(False)
        self.player_busy_indicator.setMinimum(0)
        self.player_busy_indicator.setMaximum(0)
        self.player_busy_indicator.setHidden(True)

        # set the timer_count to 999 indicating that no timer has started yet
        self.timer_count = 999
        self.timer = QTimer()

        self.profile_id = ""
        self.has_updated_players = False

        # Top
        top_label = QLabel("AoE 2 Dashboard")
        font: QFont = top_label.font()
        font.setPointSize(18)
        top_label.setFont(font)
        top_label.setAlignment(Qt.AlignCenter)
        top_label.setMaximumHeight(30)

        # Player Label Right Side
        self.player_label = QLabel("Your team")
        font: QFont = self.player_label.font()
        font.setPointSize(16)
        self.player_label.setFont(font)
        self.player_label.setAlignment(Qt.AlignCenter)

        # Player Stats
        self.player_table = TeamTableWidget(1, 4)

        # Opponent Label Left Side
        self.opp_label = QLabel("Opponent's team")
        font: QFont = self.opp_label.font()
        font.setPointSize(16)
        self.opp_label.setFont(font)
        self.opp_label.setAlignment(Qt.AlignCenter)

        # Opponent Stats
        self.opp_table = TeamTableWidget(2, 4)

        self.player_rating_histories_team_RM = np.empty((2, 4), dtype=tuple)
        self.player_rating_histories_1v1_RM = np.empty((2, 4), dtype=tuple)

        self.player_rating_histories_team_EW = np.empty((2, 4), dtype=tuple)
        self.player_rating_histories_1v1_EW = np.empty((2, 4), dtype=tuple)

        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.opp_label)
        self.left_layout.addWidget(self.opp_table)
        self.left_layout.addWidget(self.opp_busy_indicator)

        self.left_layout.addSpacing(15)

        self.right_layout = QVBoxLayout()
        self.right_layout.addWidget(self.player_label)
        self.right_layout.addWidget(self.player_table)
        self.right_layout.addWidget(self.player_busy_indicator)

        self.right_layout.addSpacing(15)

        # Bar
        # Todo: Check if Icon Path exists??
        # pref_icon = QIcon.fromTheme("preferences-system")
        pref_icon = QIcon(os.path.dirname(__file__) + "/../img/resources/settings_white_24dp.svg")
        pref_button = QToolButton()
        pref_button.setIcon(pref_icon)
        pref_button.setMinimumSize(35, 35)
        pref_button.clicked.connect(self.open_pref_panel)

        # refresh_icon = QIcon.fromTheme("system-software-update")
        refresh_icon = QIcon(os.path.dirname(__file__) + "/../img/resources/cached_white_24dp.svg")
        refresh_button = QToolButton()
        refresh_button.setIcon(refresh_icon)
        refresh_button.setMinimumSize(35, 35)
        refresh_button.clicked.connect(self.refresh_player)

        show_analytics_button = QToolButton()
        show_analytics_button.setMinimumSize(35, 35)
        analytics_icon = QIcon(QIcon(os.path.dirname(__file__) + "/../img/resources/insights_white_24dp.svg"))
        show_analytics_button.setIcon(analytics_icon)
        show_analytics_button.clicked.connect(self.show_analytics)

        show_acknowledgement_button = QToolButton()
        show_acknowledgement_button.setMinimumSize(35, 35)
        acknowledgement_icon = QIcon(os.path.dirname(__file__) + "/../img/resources/attribution_white_24dp.svg")
        show_acknowledgement_button.setIcon(acknowledgement_icon)
        show_acknowledgement_button.clicked.connect(self.show_acknowledgements)

        self.reload_label = QLabel("")

        font_italic = self.reload_label.font()
        font_italic.setItalic(True)

        font_bold = self.reload_label.font()
        font_bold.setBold(True)

        tip_str = "Tip: Set your Aoe2.net ID in the settings, then hit reload"
        self.info_label = QLabel(tip_str)
        self.info_label.setFont(font_italic)

        self.bar_layout = QHBoxLayout()
        self.bar_layout.addWidget(self.reload_label)
        self.bar_layout.addWidget(refresh_button)
        self.bar_layout.addWidget(pref_button)
        self.bar_layout.addWidget(show_analytics_button)
        self.bar_layout.addWidget(show_acknowledgement_button)

        # Display Legend
        legend_label = QLabel("Legend")

        legend_label.setFont(font_bold)

        # RM
        check_box_1v1_RM = QCheckBox("1v1 RM")
        check_box_1v1_RM.setChecked(
            SettingsHandler.get_1v1_RM_display_option_from_settings())

        check_box_team_RM = QCheckBox("Team RM")
        check_box_team_RM.setChecked(
            SettingsHandler.get_team_RM_display_option_from_settings())

        check_box_1v1_RM.stateChanged.connect(self.check_box_1v1_RM_changed)
        check_box_team_RM.stateChanged.connect(self.check_box_team_RM_changed)

        legend_item_team_RM = LegendItem(None, (15, 153, 246))
        legend_item_1v1_RM = LegendItem(None, (255, 96, 62))

        h_item_team_RM = QHBoxLayout()
        h_item_team_RM.addWidget(legend_item_team_RM)
        h_item_team_RM.addWidget(check_box_team_RM)

        h_item_1v1_RM = QHBoxLayout()
        h_item_1v1_RM.addWidget(legend_item_1v1_RM)
        h_item_1v1_RM.addWidget(check_box_1v1_RM)

        # EW
        check_box_1v1_EW = QCheckBox("1v1 EW")
        check_box_1v1_EW.setChecked(
            SettingsHandler.get_1v1_EW_display_option_from_settings())

        check_box_team_EW = QCheckBox("Team EW")
        check_box_team_EW.setChecked(
            SettingsHandler.get_team_EW_display_option_from_settings())

        check_box_1v1_EW.stateChanged.connect(self.check_box_1v1_EW_changed)
        check_box_team_EW.stateChanged.connect(self.check_box_team_EW_changed)

        legend_item_team_EW = LegendItem(None, (82, 168, 39))
        legend_item_1v1_EW = LegendItem(None, (226, 185, 15))

        h_item_team_EW = QHBoxLayout()
        h_item_team_EW.addWidget(legend_item_team_EW)
        h_item_team_EW.addWidget(check_box_team_EW)

        h_item_1v1_EW = QHBoxLayout()
        h_item_1v1_EW.addWidget(legend_item_1v1_EW)
        h_item_1v1_EW.addWidget(check_box_1v1_EW)

        # Assemble

        v_legend_layout = QVBoxLayout()
        v_legend_layout.addWidget(legend_label)

        v_legend_layout.addLayout(h_item_1v1_RM)
        v_legend_layout.addLayout(h_item_team_RM)

        v_legend_layout.addLayout(h_item_1v1_EW)
        v_legend_layout.addLayout(h_item_team_EW)

        # Info Metadata Bar

        style_sheet_orange = "color: orange"
        # style_sheet_light_blue = "color: rgb(51,149,255)"

        accented_style_sheet = style_sheet_orange  # if self.dark_theme else style_sheet_light_blue

        label_cur_pl = QLabel("Leaderboard:")

        self.leader_board_label = QLabel("")
        self.leader_board_label.setFont(font_italic)
        self.leader_board_label.setStyleSheet(accented_style_sheet)

        label_cur_size = QLabel("Size: ")
        label_cur_size.setGeometry(250, 470, 30, 17)

        self.size_label = QLabel("")
        self.size_label.setFont(font_italic)
        self.size_label.setStyleSheet(accented_style_sheet)

        label_cur_map = QLabel("Map:")

        self.map_label = QLabel("")
        self.map_label.setFont(font_italic)
        self.map_label.setStyleSheet(accented_style_sheet)

        label_cur_server = QLabel("Server:")

        self.server_label = QLabel("")
        self.server_label.setFont(font_italic)
        self.server_label.setStyleSheet(accented_style_sheet)

        self.h_layout_metadata = QHBoxLayout()

        label_cur_time = QLabel("Match Started:")
        self.time_match_started_label = QLabel("")
        self.time_match_started_label.setFont(font_italic)
        self.time_match_started_label.setStyleSheet(accented_style_sheet)

        self.metadata_labels = [label_cur_pl, self.leader_board_label, label_cur_size, self.size_label,
                                label_cur_map, self.map_label, label_cur_server, self.server_label]

        for e in self.metadata_labels:
            self.h_layout_metadata.addWidget(e)
            e.setHidden(True)

        h_layout_match_time = QHBoxLayout()
        self.time_labels = [label_cur_time, self.time_match_started_label]

        for e in self.time_labels:
            h_layout_match_time.addWidget(e)
            e.setHidden(True)

        v_metadata_layout = QVBoxLayout()
        v_metadata_layout.addSpacing(15)
        v_metadata_layout.addLayout(self.h_layout_metadata)
        v_metadata_layout.addLayout(h_layout_match_time)
        v_metadata_layout.addSpacing(15)

        self.hidden_labels = []
        self.hidden_labels.extend(self.metadata_labels)
        self.hidden_labels.extend(self.time_labels)

        center_layout_v = QVBoxLayout()
        # center_layout_v.addLayout(v_display_option_layout)
        # center_layout_v.addSpacing(15)
        center_layout_v.addLayout(v_legend_layout)
        center_layout_v.addSpacing(12)

        center_layout = QHBoxLayout()
        center_layout.addSpacing(15)
        center_layout.addLayout(center_layout_v)
        center_layout.addSpacing(15)

        # Grid View
        self.grid_layout = QGridLayout()

        self.grid_layout.addWidget(top_label, 0, 0, 1, 3, Qt.AlignTop)
        self.grid_layout.addLayout(self.left_layout, 1, 0, Qt.AlignTop)
        self.grid_layout.addLayout(self.right_layout, 1, 2, Qt.AlignTop)

        self.grid_layout.addLayout(v_metadata_layout, 2, 0, 1, 3, Qt.AlignLeft)

        self.grid_layout.addWidget(self.info_label, 3, 0, 1, 2)
        self.grid_layout.addLayout(self.bar_layout, 3, 2, Qt.AlignRight)

        self.grid_layout.addLayout(center_layout, 1, 1, Qt.AlignBottom)

        self.setLayout(self.grid_layout)

        self.resize(self.minimumSizeHint())

        # self.refresh_player()

    def start_load_player_data_thread(self, profile_id: int):
        thread = Thread(target=self.load_player_data, kwargs={"profile_id": profile_id})
        thread.start()
        # self.load_player_data(profile_id)

    def load_player_data(self, profile_id: int):
        url_str = APIStringGenerator.get_API_string_for_last_match(profile_id)

        try:
            response = requests.get(url_str)
            last_match = json.loads(response.text)
            new_match = DataParser.parse_current_match(last_match)
        except:
            self.display_network_error()
            return

        # check if new match is current match
        if self.current_match is not None:
            if new_match.match_uuid == self.current_match.match_uuid:
                print("Same Game")
                return

        self.current_match = new_match
        self.has_updated_players = False
        self.sig_player_data_loaded.emit()

    def player_data_loaded(self):
        players_per_team = int(self.current_match.num_players / 2)
        self.player_rating_histories_team_RM = np.empty(
            (2, players_per_team), dtype=tuple)
        self.player_rating_histories_1v1_RM = np.empty(
            (2, players_per_team), dtype=tuple)
        # Player Team
        self.player_table.update_team(self.current_match.team_1_players)

        # opp Team
        self.opp_table.update_team(self.current_match.team_2_players)

        self.populate_metadata()
        self.update()

        if self.timer_count == 999:
            self.connect(self.timer, SIGNAL("timeout()"), self.update_timer)
            self.timer.start(1000)

    def update_player_profiles(self):
        for player in self.current_match.team_1_players:
            url_str = APIStringGenerator.get_API_string_for_rating_history(
                self.current_match.leaderboard_id, player.profile_id, 1)
            response = requests.get(url_str)

            loads = json.loads(response.text)
            if len(loads) != 0:
                DataParser.parse_player_data_from_rating_history_and_store(
                    loads[0], player)

        for player in self.current_match.team_2_players:
            url_str = APIStringGenerator.get_API_string_for_rating_history(
                self.current_match.leaderboard_id, player.profile_id, 1)
            response = requests.get(url_str)

            loads = json.loads(response.text)
            if len(loads) != 0:
                DataParser.parse_player_data_from_rating_history_and_store(
                    loads[0], player)
        self.sig_player_data_updated.emit()

    def player_profiles_updated(self):
        self.player_table.update_civ_names()
        self.opp_table.update_civ_names()
        self.has_updated_players = True

    def update_timer(self):
        """
        This is getting called every second by the timer. If timer_count == 999 that means that its the first call
        since program start
        """
        if self.timer_count == 999:
            self.timer_count = 60
        elif self.timer_count == 0:
            self.start_load_player_data_thread(self.profile_id)
            self.timer_count = 60
        elif self.timer_count == 59:
            self.timer_count -= 1
            if self.has_updated_players is False:
                # update Player
                thread = Thread(target=self.update_player_profiles)
                thread.start()
        else:
            self.timer_count -= 1
        self.reload_label.setText(str(self.timer_count) + " s")

    def load_player_rating_history(self, team, player, profile_id, player_name):
        count = 50
        leaderboard_id_1v1_RM = 3  # 1v1 RM
        leaderboard_id_team_RM = 4  # Team RM

        leaderboard_id_1v1_EW = 13  # 1v1 RM
        leaderboard_id_team_EW = 14  # Team RM

        url_str_1v1_RM = APIStringGenerator.get_API_string_for_rating_history(
            leaderboard_id_1v1_RM, profile_id, count)
        url_str_team_RM = APIStringGenerator.get_API_string_for_rating_history(
            leaderboard_id_team_RM, profile_id, count)

        url_str_1v1_EW = APIStringGenerator.get_API_string_for_rating_history(
            leaderboard_id_1v1_EW, profile_id, count)
        url_str_team_EW = APIStringGenerator.get_API_string_for_rating_history(
            leaderboard_id_team_EW, profile_id, count)

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

            ratings_team_EW, timestamps_team_EW = DataParser.compile_ratings_history(
                data_team_ranking_EW)
            ratings_1v1_EW, timestamps_1v1_EW = DataParser.compile_ratings_history(
                data_1v1_ranking_EW)

        except:
            self.display_network_error()
            return
        data = (
            team, player, profile_id, player_name,
            ratings_1v1_RM, timestamps_1v1_RM, ratings_team_RM, timestamps_team_RM,
            ratings_1v1_EW, timestamps_1v1_EW, ratings_team_EW, timestamps_team_EW)
        self.sig_rating_history_loaded.emit(data)

    def player_rating_history_loaded(self, data: tuple):
        """
        :param data: Tuple(team, player, profile_id, player_name,
                            ratings_1v1_RM, timestamps_1v1_RM, ratings_team_RM, timestamps_team_RM, 
                            ratings_1v1_EW, timestamps_1v1_EW, ratings_team_EW, timestamps_team_EW
        """
        team, player = data[0], data[1]
        profile_id, player_name = data[2], data[3]
        ratings_1v1_RM, timestamps_1v1_RM, ratings_team_RM, timestamps_team_RM = data[4:8]
        ratings_1v1_EW, timestamps_1v1_EW, ratings_team_EW, timestamps_team_EW = data[8:12]

        plot_widget = RatingPlotWidget(parent=self, player_name=player_name)
        plot_widget.plot_rating(
            rating_data=[ratings_team_RM, timestamps_team_RM], leaderboard_id=4)
        plot_widget.plot_rating(
            rating_data=[ratings_1v1_RM, timestamps_1v1_RM], leaderboard_id=3)

        plot_widget.plot_rating(
            rating_data=[ratings_team_EW, timestamps_team_EW], leaderboard_id=14)
        plot_widget.plot_rating(
            rating_data=[ratings_1v1_EW, timestamps_1v1_EW], leaderboard_id=13)

        plot_widget.setMinimumSize(300, 200)

        if team == 1:
            if self.player_rating_plot is not None:
                self.right_layout.removeWidget(self.player_rating_plot)
                self.player_rating_plot.close()
            self.player_rating_plot = plot_widget
            self.right_layout.addWidget(self.player_rating_plot)
            self.player_busy_indicator.setHidden(True)
        if team == 2:
            if self.opp_rating_plot is not None:
                self.left_layout.removeWidget(self.opp_rating_plot)
                self.opp_rating_plot.close()
            self.opp_rating_plot = plot_widget
            self.left_layout.addWidget(self.opp_rating_plot)
            self.opp_busy_indicator.setHidden(True)

        self.player_rating_histories_team_RM[team -
                                             1][player] = (ratings_team_RM, timestamps_team_RM)
        self.player_rating_histories_1v1_RM[team -
                                            1][player] = (ratings_1v1_RM, timestamps_1v1_RM)

        self.player_rating_histories_team_EW[team -
                                             1][player] = (ratings_team_EW, timestamps_team_EW)
        self.player_rating_histories_1v1_EW[team -
                                            1][player] = (ratings_1v1_EW, timestamps_1v1_EW)

        plot_widget.update_displayed_plots(
            3, SettingsHandler.get_1v1_RM_display_option_from_settings())
        plot_widget.update_displayed_plots(
            4, SettingsHandler.get_team_RM_display_option_from_settings())

        plot_widget.update_displayed_plots(
            13, SettingsHandler.get_1v1_EW_display_option_from_settings())
        plot_widget.update_displayed_plots(
            14, SettingsHandler.get_team_EW_display_option_from_settings())

    def player_selection_changed(self, team: int, player: int):
        """
        This method gets called by the Team Table Widget that indicates that selection has changed and the Rating
        Plot needs to display the rating of another player. :params team is either 1 or 2, player is zero indexed
        """

        profile_id = 0
        player_name = "Unknown"
        if team == 1:
            player_info = self.current_match.team_1_players[player]
            profile_id = player_info.profile_id
            player_name = player_info.name
            self.player_busy_indicator.setHidden(False)
        if team == 2:
            player_info = self.current_match.team_2_players[player]
            profile_id = player_info.profile_id
            player_name = player_info.name
            self.opp_busy_indicator.setHidden(False)

        """
        for saving network resources the rating history can be reused
        in player_rating_histories is an array that contains for each player in a matrix a 
        tuple with ratings and timestamps
        """
        ratings_team_RM = None

        item = self.player_rating_histories_team_RM[team - 1][player]
        if item is not None:
            ratings_team_RM, timestamps_team_RM = self.player_rating_histories_team_RM[team - 1][player]
            ratings_1v1_RM, timestamps_1v1_RM = self.player_rating_histories_1v1_RM[team - 1][player]

            ratings_team_EW, timestamps_team_EW = self.player_rating_histories_team_EW[team - 1][player]
            ratings_1v1_EW, timestamps_1v1_EW = self.player_rating_histories_1v1_EW[team - 1][player]

            data = (team, player, profile_id, player_name, ratings_1v1_RM, timestamps_1v1_RM, ratings_team_RM,
                    timestamps_team_RM, ratings_1v1_EW, timestamps_1v1_EW, ratings_team_EW, timestamps_team_EW)
            self.sig_rating_history_loaded.emit(data)

        if ratings_team_RM is None:
            thread = Thread(target=self.load_player_rating_history, args=(team, player, profile_id, player_name))
            thread.start()

    def populate_metadata(self):
        """Displays interesting data from the current match like server, Leaderboard etc."""
        for e in self.hidden_labels:
            e.setHidden(False)
        self.leader_board_label.setText(
            self.localized_api_strings.get_key_for_leaderboard(self.current_match.leaderboard_id))
        self.map_label.setText(
            self.localized_api_strings.get_key_for_map(self.current_match.map_type))
        self.server_label.setText(self.current_match.server)
        num_pl_per_team = str(int(self.current_match.num_players / 2))
        self.size_label.setText(num_pl_per_team + "v" + num_pl_per_team)

        # Time
        if SettingsHandler.get_saved_option_for_humanized_time():
            self.time_match_started_label.setText(self.current_match.time_started_humanized)
        else:
            self.time_match_started_label.setText(self.current_match.time_started_plain)

    def refresh_player(self):
        """Loads a profile_id from QSettings if none was yet set in the runtime"""
        current_profile_id = SettingsHandler.get_profile_id_from_settings()
        if current_profile_id != 0:
            self.start_load_player_data_thread(current_profile_id)
            self.profile_id = current_profile_id

    def update_display_options(self, leaderboard_id, checked):
        if self.player_rating_plot is None:
            return
        self.player_rating_plot.update_displayed_plots(leaderboard_id, checked)
        self.opp_rating_plot.update_displayed_plots(leaderboard_id, checked)

    def check_box_1v1_RM_changed(self, state: int):
        # 0: not checked, 2: checked
        checked = True if state == 2 else False
        SettingsHandler.set_1v1_RM_display_option_in_settings(checked)

        self.update_display_options(3, checked)

    def check_box_team_RM_changed(self, state: int):
        # 0: not checked, 2: checked
        checked = True if state == 2 else False
        SettingsHandler.set_team_RM_display_option_in_settings(checked)

        self.update_display_options(4, checked)

    def check_box_1v1_EW_changed(self, state: int):
        # 0: not checked, 2: checked
        checked = True if state == 2 else False
        SettingsHandler.set_1v1_EW_display_option_in_settings(checked)

        self.update_display_options(13, checked)

    def check_box_team_EW_changed(self, state: int):
        # 0: not checked, 2: checked
        checked = True if state == 2 else False
        SettingsHandler.set_team_EW_display_option_in_settings(checked)

        self.update_display_options(14, checked)

    @staticmethod
    def display_network_error():
        message_box = QMessageBox()
        message_box.setText("There might be a networking error")
        message_box.setInformativeText("Check your internet connection or check if Aoe2.net is down")
        message_box.setStandardButtons(QMessageBox.Ok)

        message_box.exec()

    # Manage Windows

    def open_pref_panel(self):
        pref_panel = PrefPanel(main_window=self)
        pref_panel.setGeometry(500, 500, 300, 150)
        pref_panel.show()
        self.active_windows.append(pref_panel)

    def pref_panel_closed(self, pref_panel: PrefPanel):
        self.active_windows.remove(pref_panel)

    def update_display_due_to_options_changes(self):
        if self.current_match is None:
            return
        MainWindow.localized_api_strings = LocalizedAPIStrings()
        self.populate_metadata()
        self.player_table.update_civ_names()
        self.opp_table.update_civ_names()

    def show_acknowledgements(self):
        acknowledgement_window = AcknowledgementsWindow(main_window=self)
        acknowledgement_window.show()

        self.active_windows.append(acknowledgement_window)

    def show_analytics(self):
        analytics_window = AnalyticsWindow(main_window=self, profile_id=SettingsHandler.get_profile_id_from_settings())
        analytics_window.show()

        self.active_windows.append(analytics_window)

    def active_window_closed(self, window: QWidget):
        self.active_windows.remove(window)
