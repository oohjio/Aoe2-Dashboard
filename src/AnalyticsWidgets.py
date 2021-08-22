#  Copyright (C)  2021 oohjio, https://github.com/oohjio
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License v3 as published by the Free Software Foundation.

import typing

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from DataParser import Match, LocalizedAPIStrings
from DataHandler import DataHandler
from SettingsHandler import SettingsHandler
from Widgets import RatingPlotWidget

from pyqtgraph import mkPen
import pyqtgraph as pg
import os


class MatchDetailWidget(QWidget):
    def __init__(self, parent: typing.Optional[QWidget], match: Match, has_close_button: bool) -> None:
        super().__init__(parent=parent)

        # Size
        self.match = match
        self.has_close_button = has_close_button
        self.localized_api_strings = LocalizedAPIStrings()
        self.collapsed = False

        # Set Up UI
        self.metadata_labels = []
        self.time_started_labels = []

        self.h_metadata_layout = QHBoxLayout()
        self.h_metadata_layout.setSpacing(5)
        self.h_time_started_layout = QHBoxLayout()
        self.h_time_started_layout.setSpacing(5)

        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(4)

        metadata_label = QLabel("Metadata:")

        accented_style_sheet = "color: orange"
        font_italic = metadata_label.font()
        font_bold = metadata_label.font()

        font_italic.setItalic(True)
        font_bold.setBold(True)

        metadata_label.setFont(font_bold)

        label_cur_pl = QLabel("Leaderboard:")

        leader_board_label = QLabel(None)
        leader_board_label.setText(self.localized_api_strings.get_key_for_leaderboard(self.match.leaderboard_id))
        leader_board_label.setFont(font_italic)
        leader_board_label.setStyleSheet(accented_style_sheet)

        label_cur_size = QLabel("Size: ")
        label_cur_size.setGeometry(250, 470, 30, 17)

        size_label = QLabel(None)
        num_pl_per_team = str(int(self.match.num_players / 2))
        size_label.setText(num_pl_per_team + "v" + num_pl_per_team)
        size_label.setFont(font_italic)
        size_label.setStyleSheet(accented_style_sheet)

        label_cur_map = QLabel("Map:")

        map_label = QLabel(self.localized_api_strings.get_key_for_map(self.match.map_type))
        map_label.setFont(font_italic)
        map_label.setStyleSheet(accented_style_sheet)

        label_cur_server = QLabel("Server:")

        server_label = QLabel(None)
        server_label.setText(self.match.server)
        server_label.setFont(font_italic)
        server_label.setStyleSheet(accented_style_sheet)

        self.collapse_button = QToolButton()
        self.close_button = QToolButton()
        if not self.has_close_button:
            self.collapse_button.setHidden(True)
            self.close_button.setHidden(True)
        self.collapse_button.setMaximumSize(QSize(18, 18))
        self.collapse_button.setArrowType(Qt.DownArrow)
        self.collapse_button.clicked.connect(self.collapse_button_clicked)

        self.close_button.setMaximumSize(QSize(18, 18))
        close_icon = QIcon(os.path.dirname(__file__) + "/../img/resources/close_white_24dp.svg")
        self.close_button.setIcon(close_icon)
        self.close_button.clicked.connect(self.close_button_clicked)

        time_label = QLabel("Match Started: ")
        time_label.setFont(font_bold)

        time_match_started_label = QLabel("")
        time_match_started_label.setFont(font_italic)
        time_match_started_label.setStyleSheet(accented_style_sheet)

        # Time
        if SettingsHandler.get_saved_option_for_humanized_time():
            time_match_started_label.setText(self.match.time_started_humanized)
        else:
            time_match_started_label.setText(self.match.time_started_plain)

        self.metadata_labels = [metadata_label, label_cur_pl, leader_board_label, label_cur_size, size_label,
                                label_cur_map, map_label, label_cur_server, server_label]
        self.time_started_labels = [time_label, time_match_started_label]

        for l in self.metadata_labels:
            self.h_metadata_layout.addWidget(l, stretch=5, alignment=Qt.AlignLeft)
        for l in self.time_started_labels:
            self.h_time_started_layout.addWidget(l, stretch=5, alignment=Qt.AlignLeft)

        self.h_metadata_layout.addWidget(self.collapse_button, alignment=Qt.AlignRight)
        self.h_metadata_layout.addWidget(self.close_button, alignment=Qt.AlignRight)

        vertical_layout_top_level = QVBoxLayout()
        vertical_layout_top_level.addLayout(self.h_metadata_layout)
        vertical_layout_top_level.addLayout(self.h_time_started_layout)

        self.h_match_details_layout = QHBoxLayout()
        self.h_match_details_layout.setSpacing(4)
        v_layout_opponent = QVBoxLayout()

        self.details_items: [QWidget] = []

        for player in self.match.team_2_players:
            h_layout = QHBoxLayout()

            civ_name_label = QLabel(player.civ_name)

            bold_font = civ_name_label.font()
            bold_font.setBold(True)

            player_name_label = QLabel(f"[{player.rating}] {player.name}")
            player_name_label.setFont(bold_font)

            civ_name_label = QLabel(player.civ_name)
            item = CivAndColorItem(None, player.color, player.civ_id)

            h_layout.addWidget(item, stretch=5, alignment=Qt.AlignLeft)
            h_layout.addWidget(civ_name_label, stretch=5, alignment=Qt.AlignLeft)
            h_layout.addWidget(player_name_label, stretch=10, alignment=Qt.AlignLeft)

            v_layout_opponent.addLayout(h_layout)

            self.details_items.extend([civ_name_label, player_name_label, item])

            if player.player_won:
                # add crown
                label = QLabel()
                won_icon = QIcon(os.path.dirname(__file__) + "/../img/symbols/crown/crown-312077.svg")
                pixmap = won_icon.pixmap(QSize(30, 30))
                label.setPixmap(pixmap)
                h_layout.insertWidget(2, label, alignment=Qt.AlignRight)
                self.details_items.append(label)

        v_layout_player = QVBoxLayout()

        for player in self.match.team_1_players:
            h_layout = QHBoxLayout()

            civ_name_label = QLabel(player.civ_name)

            bold_font = civ_name_label.font()
            bold_font.setBold(True)

            player_name_label = QLabel(f"[{player.rating}] {player.name}")
            player_name_label.setFont(bold_font)

            civ_name_label = QLabel(player.civ_name)
            item = CivAndColorItem(None, player.color, player.civ_id)

            h_layout.addWidget(player_name_label, stretch=10, alignment=Qt.AlignRight)
            h_layout.addWidget(civ_name_label, stretch=5, alignment=Qt.AlignRight)
            h_layout.addWidget(item, stretch=5, alignment=Qt.AlignRight)

            v_layout_player.addLayout(h_layout)

            self.details_items.extend([civ_name_label, player_name_label, item])

            if player.player_won:
                # add crown
                label = QLabel()
                won_icon = QIcon(os.path.dirname(__file__) + "/../img/symbols/crown/crown-312077.svg")
                pixmap = won_icon.pixmap(QSize(30, 30))
                label.setPixmap(pixmap)
                h_layout.insertWidget(1, label, alignment=Qt.AlignLeft)
                self.details_items.append(label)

        self.h_match_details_layout.addLayout(v_layout_opponent)
        self.h_match_details_layout.addLayout(v_layout_player)
        vertical_layout_top_level.addLayout(self.h_match_details_layout)

        self.setLayout(vertical_layout_top_level)

    def collapse_button_clicked(self):
        if self.collapsed is False:
            self.collapsed = True
            self.collapse_button.setArrowType(Qt.ArrowType.LeftArrow)
        else:
            self.collapsed = False
            self.collapse_button.setArrowType(Qt.ArrowType.DownArrow)
        for e in self.details_items:
            e.setHidden(self.collapsed)

    def close_button_clicked(self):
        self.close()

    def paintEvent(self, e):
        painter = QPainter(self)

        width = self.size().width()
        height = self.size().height()

        color = (95, 93, 93)
        pen = mkPen(color, width=3)
        painter.setPen(pen)

        points = [QPointF(5, 5), QPointF(width - 5, 5), QPointF(width - 5, height - 5), QPointF(4, height - 5),
                  QPointF(5, 5)]
        painter.drawPolyline(points)

        painter.end()


class CivAndColorItem(QWidget):
    def __init__(self, parent: typing.Optional[QWidget], color_id, civ_id) -> None:
        super().__init__(parent=parent)

        self.setMinimumSize(50, 50)

        self.civ_image = DataHandler.get_civ_icon_for_id(civ_id)

        # Determine Color
        if color_id == 1:
            self.color = (0, 123, 255)
        elif color_id == 2:
            self.color = (226, 0, 0)
        elif color_id == 3:
            self.color = (100, 178, 26)
        elif color_id == 4:
            self.color = (246, 248, 95)
        elif color_id == 5:
            self.color = (75, 238, 241)
        elif color_id == 6:
            self.color = (229, 0, 255)
        elif color_id == 7:
            self.color = (112, 112, 112)
        elif color_id == 8:
            self.color = (255, 153, 0)
        else:
            self.color = (0, 0, 0)

    def paintEvent(self, e):
        painter = QPainter(self)

        painter.drawImage(QRect(5, 5, 40, 40), self.civ_image)

        pen = mkPen(self.color, width=3)
        painter.setPen(pen)
        points = [QPointF(2.5, 2.5), QPointF(47.5, 2.5), QPointF(47.5, 47.5), QPointF(2.5, 47.5), QPointF(2.5, 2.5)]
        painter.drawPolyline(points)

        painter.end()
