#  Copyright (C)  2021 oohjio, https://github.com/oohjio
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License v3 as published by the Free Software Foundation.

import json

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from DataHandler import DataHandler
from DataParser import BasicPlayerInfo
from ui.ui_analytics_window import Ui_AnalyticsWindow

from AnalyticsWidgets import MatchDetailWidget
from Widgets import RatingPlotWidget, LegendItem


class AnalyticsWindow(QWidget, Ui_AnalyticsWindow):
    # SIGNALS
    # return type is a tuple where [0] is either 0 or 1 for success and [1] is the data

    sig_player_data_loaded = Signal(tuple)
    sig_match_history_loaded = Signal(tuple)
    sig_rating_history_loaded = Signal(tuple)
    sig_rating_plot_point_clicked = Signal(tuple)

    def __init__(self, main_window, profile_id: int):
        super().__init__()
        self.set_up_UI()

        self.main_window = main_window
        self.profile_id = profile_id
        self.player_data = None

        self.rh_rating_plot = None

        # FLAGS
        self.has_loaded_player_data = False
        self.is_currently_loading_matches = False
        self.current_player_data_ladder = 3  # 1v1 RM




        # SIGNALS
        self.sig_player_data_loaded.connect(self.player_data_loaded)
        self.sig_match_history_loaded.connect(self.match_history_loaded)
        self.sig_rating_history_loaded.connect(self.rating_history_loaded)
        self.sig_rating_plot_point_clicked.connect(self.rating_plot_point_clicked)

        # setup Data
        self.data_handler = DataHandler()
        self.data_handler.get_basic_player_data_for_leaderboard(self.current_player_data_ladder, self.profile_id,
                                                                finish_signal=self.sig_player_data_loaded)
        # PLACEHOLDERS
        self.player_data = None
        self.rh_rating_plot = None
        self.mh_match_detail_widget: MatchDetailWidget = None

        self.mh_matches = []
        self.mh_matches_loaded = 0
        self.loaded_match_detail_widgets = []
        self.loaded_match_timestamps = []

    def set_up_UI(self):
        self.setupUi(self)

        # Layouts da QtDesinger dumm ist
        self.setLayout(self.toplevel_v_layout)
        self.toplevel_v_layout.setContentsMargins(15, 15, 15, 15)
        self.match_history_tab.setLayout(self.mh_tab_v_layout)
        self.mh_tab_v_layout.setContentsMargins(10, 10, 10, 10)
        self.rating_history_tab.setLayout(self.rh_tab_v_layout)
        self.rh_tab_v_layout.setContentsMargins(10, 10, 10, 10)

        # SIGNALS
        self.tab_widget.currentChanged.connect(self.tab_widget_changed_index)
        self.tab_widget_changed_index(0)

        self.mh_tab_scroll_area.verticalScrollBar().actionTriggered.connect(self.scrollbarAction)
        self.mh_tab_load_more_button.clicked.connect(self.match_history_load_more_button_clicked)

        self.rh_tab_load_more_button.clicked.connect(self.load_rating_history_button_clicked)

        self.button_team_EW.clicked.connect(self.ladder_buttons_changed)
        self.button_team_RM.clicked.connect(self.ladder_buttons_changed)
        self.button_1v1_EW.clicked.connect(self.ladder_buttons_changed)
        self.button_1v1_RM.clicked.connect(self.ladder_buttons_changed)

        # Create Hidden QProgressBars

        self.rh_busy_indicator = QProgressBar()
        self.rh_busy_indicator.setMaximumHeight(10)
        self.rh_busy_indicator.setTextVisible(False)
        self.rh_busy_indicator.setMinimum(0)
        self.rh_busy_indicator.setMaximum(0)
        self.rh_busy_indicator.setHidden(True)

        self.mh_busy_indicator = QProgressBar()
        self.mh_busy_indicator.setMaximumHeight(10)
        self.mh_busy_indicator.setTextVisible(False)
        self.mh_busy_indicator.setMinimum(0)
        self.mh_busy_indicator.setMaximum(0)
        self.mh_busy_indicator.setHidden(True)

        self.rh_tab_v_layout.addWidget(self.rh_busy_indicator)
        self.mh_tab_v_layout.addWidget(self.mh_busy_indicator)

        # Stlye Highlight
        style_sheet_orange = "color: orange"
        highlighted_labels = [self.play_displ_label, self.pd_displ_rating_label, self.pd_displ_wins_label, self.pd_displ_losses_label, self.pd_displ_winperc_label, self.play_displ_lb_label]
        for e in highlighted_labels:
            e.setStyleSheet(style_sheet_orange)

    # UI Signals

    def ladder_buttons_changed(self):
        lb = 0
        if self.button_1v1_RM.isChecked():
            lb = 3
        elif self.button_1v1_EW.isChecked():
            lb = 13
        elif self.button_team_RM.isChecked():
            lb = 4
        elif self.button_team_EW.isChecked():
            lb = 14

        if lb != 0:
            self.current_player_data_ladder = lb
            self.data_handler.get_basic_player_data_for_leaderboard(self.current_player_data_ladder, self.profile_id,
                                                                    finish_signal=self.sig_player_data_loaded)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.main_window.analytics_window_closed(self)

    def match_history_load_more_button_clicked(self):
        self.mh_busy_indicator.setHidden(False)
        self.is_currently_loading_matches = True

        load_matches = 0
        try:
            load_matches = int(self.mh_tab_load_line_edit.text())
        except ValueError:
            if self.mh_tab_load_line_edit.placeholderText() != "":
                load_matches = int(self.mh_tab_load_line_edit.placeholderText())
                self.mh_tab_load_line_edit.setPlaceholderText("")
        else:
            if load_matches > 1000:
                load_matches = 1000

        self.mh_tab_load_line_edit.setText(str(load_matches))

        if load_matches > 0:
            self.data_handler.load_last_matches(self.profile_id, load_matches, self.mh_matches_loaded,
                                                self.sig_match_history_loaded)

    def load_rating_history_button_clicked(self):
        self.rh_busy_indicator.setHidden(False)
        self.data_handler.load_rating_history_all_lb(self.profile_id, 1000, self.sig_rating_history_loaded)
        self.rh_tab_load_more_button.setDisabled(True)

    def scrollbarAction(self, action: int):
        slider = self.mh_tab_scroll_area.verticalScrollBar()

        max = slider.maximum()
        current = slider.sliderPosition()
        state = float(current) / float(max)

        if state > 0.99:
            pass

    def tab_widget_changed_index(self, index: int):
        pass

    # Rating History
    def rating_history_loaded(self, data):
        """
        :param data: Tuple(success, list:
                        ratings_1v1_RM, timestamps_1v1_RM, ratings_team_RM, timestamps_team_RM,
                        ratings_1v1_EW, timestamps_1v1_EW, ratings_team_EW, timestamps_team_EW)
        """
        if data[0] == 0:
            self.main_window.display_network_error()
            return

        ratings_1v1_RM, timestamps_1v1_RM, ratings_team_RM, timestamps_team_RM = data[1][0:4]
        ratings_1v1_EW, timestamps_1v1_EW, ratings_team_EW, timestamps_team_EW = data[1][4:8]

        plot_widget = RatingPlotWidget(parent=self, player_name=str(self.profile_id))
        plot_widget.plot_rating(
            rating_data=[ratings_team_RM, timestamps_team_RM], leaderboard_id=4)
        plot_widget.plot_rating(
            rating_data=[ratings_1v1_RM, timestamps_1v1_RM], leaderboard_id=3)

        plot_widget.plot_rating(
            rating_data=[ratings_team_EW, timestamps_team_EW], leaderboard_id=14)
        plot_widget.plot_rating(
            rating_data=[ratings_1v1_EW, timestamps_1v1_EW], leaderboard_id=13)

        self.mh_tab_graphics_view.close()
        self.rh_tab_v_layout.addWidget(plot_widget)
        plot_widget.show()

        plot_widget.setMouseEnabled(x=True, y=True)
        plot_widget.set_up_for_big_scale_display(True)
        plot_widget.register_clicked_signal(self.sig_rating_plot_point_clicked)

        plot_widget.setLabel("left", "")

        legend_label = QLabel("Legend")
        font_bold = legend_label.font()
        font_bold.setBold(True)
        legend_label.setFont(font_bold)

        rating_1v1_RM_legend_checkbox = QCheckBox("1v1 RM")
        rating_team_RM_legend_checkbox = QCheckBox("Team RM")

        rating_1v1_RM_legend_checkbox.setChecked(True)
        rating_team_RM_legend_checkbox.setChecked(True)

        rating_1v1_RM_legend_checkbox.stateChanged.connect(self.check_box_1v1_RM_changed)
        rating_team_RM_legend_checkbox.stateChanged.connect(self.check_box_team_RM_changed)

        legend_item_team_RM = LegendItem(None, (15, 153, 246))
        legend_item_1v1_RM = LegendItem(None, (255, 96, 62))

        h_item_team_RM = QHBoxLayout()
        h_item_team_RM.addWidget(legend_item_team_RM)
        h_item_team_RM.addWidget(rating_team_RM_legend_checkbox)

        h_item_1v1_RM = QHBoxLayout()
        h_item_1v1_RM.addWidget(legend_item_1v1_RM)
        h_item_1v1_RM.addWidget(rating_1v1_RM_legend_checkbox)

        # EW
        rating_1v1_EW_legend_checkbox = QCheckBox("1v1 EW")
        rating_team_EW_legend_checkbox = QCheckBox("Team EW")

        rating_1v1_EW_legend_checkbox.setChecked(True)
        rating_team_EW_legend_checkbox.setChecked(True)

        rating_1v1_EW_legend_checkbox.stateChanged.connect(self.check_box_1v1_EW_changed)
        rating_team_EW_legend_checkbox.stateChanged.connect(self.check_box_team_EW_changed)

        legend_item_team_EW = LegendItem(None, (82, 168, 39))
        legend_item_1v1_EW = LegendItem(None, (226, 185, 15))

        h_item_team_EW = QHBoxLayout()
        h_item_team_EW.addWidget(legend_item_team_EW)
        h_item_team_EW.addWidget(rating_team_EW_legend_checkbox)

        h_item_1v1_EW = QHBoxLayout()
        h_item_1v1_EW.addWidget(legend_item_1v1_EW)
        h_item_1v1_EW.addWidget(rating_1v1_EW_legend_checkbox)

        h_legend_layout = QHBoxLayout()
        h_legend_layout.addWidget(legend_label)

        h_legend_layout.addLayout(h_item_1v1_RM)
        h_legend_layout.addLayout(h_item_team_RM)

        h_legend_layout.addLayout(h_item_1v1_EW)
        h_legend_layout.addLayout(h_item_team_EW)

        self.rh_tab_v_layout.addLayout(h_legend_layout)
        self.rh_busy_indicator.setHidden(True)
        self.rh_info_label.setText("Tip: Click the A Button in the bottom left corner to return to the default view")
        self.rh_rating_plot = plot_widget

    def check_box_1v1_RM_changed(self, state: int):
        # 0: not checked, 2: checked
        checked = True if state == 2 else False

        self.update_display_options(3, checked)

    def check_box_team_RM_changed(self, state: int):
        # 0: not checked, 2: checked
        checked = True if state == 2 else False
        self.update_display_options(4, checked)

    def check_box_1v1_EW_changed(self, state: int):
        # 0: not checked, 2: checked
        checked = True if state == 2 else False
        self.update_display_options(13, checked)

    def check_box_team_EW_changed(self, state: int):
        # 0: not checked, 2: checked
        checked = True if state == 2 else False
        self.update_display_options(14, checked)

    def update_display_options(self, leaderboard_id, checked):
        self.rh_rating_plot.update_displayed_plots(leaderboard_id, checked)

    def rating_plot_point_clicked(self, data):
        """
        :param data: (timestamp, leaderboard_id)
        """
        min_index = -1
        min_diff = 9999999999

        for index, timestamp in enumerate(self.loaded_match_timestamps):
            # timestamp_saved ist immer kleiner als data
            timestamp_data = int(data[0])
            timestamp_saved = int(timestamp)

            diff = timestamp_data - timestamp_saved
            if diff < 0:
                continue
            if diff < min_diff:
                min_diff = diff
                min_index = index

        if min_index != -1:
            if self.mh_match_detail_widget != None:
                self.mh_match_detail_widget.close()
            match = self.loaded_match_detail_widgets[min_index].match
            match_widget = MatchDetailWidget(None, match, has_close_button=True)
            self.mh_match_detail_widget = match_widget
            self.rh_tab_v_layout.addWidget(match_widget)

    # show match history

    def match_history_loaded(self, data):

        v_layout = QVBoxLayout()
        if self.mh_tab_scroll_area_content.layout() is not None:
            v_layout = self.mh_tab_scroll_area_content.layout()
        for match in data[1]:
            match_view = MatchDetailWidget(None, match, has_close_button=False)
            v_layout.addWidget(match_view, alignment=Qt.AlignTop)
            self.mh_matches_loaded += 1

            self.loaded_match_timestamps.append(match.time_str)
            self.loaded_match_detail_widgets.append(match_view)

        if self.mh_tab_scroll_area_content.layout() is None:
            self.mh_tab_scroll_area_content.setLayout(v_layout)

        self.is_currently_loading_matches = False

        print(f"{self.mh_matches_loaded = }")
        self.mh_busy_indicator.setHidden(True)

    # load Player Data

    def player_data_loaded(self, data):
        if data[0] == 1:
            self.player_data: BasicPlayerInfo = data[1]
            self.player_data.profile_id = self.profile_id
            self.player_name_label.setText(str(self.player_data.profile_id))
            self.populate_player_data_bar(self.player_data)
            self.has_loaded_player_data = True
        else:
            if self.current_player_data_ladder == 3:
                self.current_player_data_ladder = 4
                self.button_team_RM.setChecked(True)
                self.data_handler.get_basic_player_data_for_leaderboard(self.current_player_data_ladder,
                                                                        self.profile_id,
                                                                        finish_signal=self.sig_player_data_loaded)
            elif self.current_player_data_ladder == 4:
                self.current_player_data_ladder = 13
                self.button_1v1_EW.setChecked(True)
                self.data_handler.get_basic_player_data_for_leaderboard(self.current_player_data_ladder,
                                                                        self.profile_id,
                                                                        finish_signal=self.sig_player_data_loaded)
            elif self.current_player_data_ladder == 13:
                self.current_player_data_ladder = 14
                self.button_team_EW.setChecked(True)
                self.data_handler.get_basic_player_data_for_leaderboard(self.current_player_data_ladder,
                                                                        self.profile_id,
                                                                        finish_signal=self.sig_player_data_loaded)
            else:
                self.button_1v1_RM.setChecked(True)
                self.main_window.display_network_error()

    def populate_player_data_bar(self, player_data: BasicPlayerInfo):
        self.pd_rating_label.setText(str(player_data.rating))
        self.pd_wins_label.setText(str(player_data.wins))
        self.pd_losses_label.setText(str(player_data.losses))
        self.pd_winperc_label.setText(player_data.win_percentage_str)

        if self.current_player_data_ladder == 3:
            self.play_lb_label.setText("1v1 RM")
        elif self.current_player_data_ladder == 4:
            self.play_lb_label.setText("Team RM")
        elif self.current_player_data_ladder == 13:
            self.play_lb_label.setText("1v1 EW")
        elif self.current_player_data_ladder == 14:
            self.play_lb_label.setText("Team EW")