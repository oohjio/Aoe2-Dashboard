import typing
import math
import arrow

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from APIStringGenerator import APIStringGenerator
from DataParser import BasicPlayerInfo


class RatingPlotWidget(pg.PlotWidget):
    """
    Plot Widget inherited by pg's PlotWidget for displaying Ratings in a timeframe
    """

    def __init__(self, player_name: str, parent=None, background='default', plotItem=None, **kargs):
        super().__init__(parent, background, plotItem,
                         axisItems={'bottom': pg.DateAxisItem()}, **kargs)

        self.player_name = player_name
        self.setBackground(None)

        self.current_hovered_point = None   # ("timestamp", "lb")
        self.curent_text_box = None
        self.registered_click_signal = None

        self.setMouseEnabled(x=False, y=False)

        left_axis: pg.AxisItem = self.getAxis("left")
        left_axis.setGrid(10)

        bottom_axis: pg.AxisItem = self.getAxis("bottom")
        bottom_axis.setGrid(10)

        self.data_team_RM_ranking = None
        self.data_1v1_RM_ranking = None

        self.data_team_EW_ranking = None
        self.data_1v1_EW_ranking = None

        left_label_str = "Rating of " + self.player_name
        self.setLabel("left", left_label_str)

        self.stored_leaderboard_ratings = np.empty(15, dtype=tuple)
        self.stored_plot_items = np.empty(15, dtype=pg.PlotDataItem)

    def plot_rating(self, rating_data, leaderboard_id):
        pen = pg.mkPen((0, 0, 0), width=2)
        if leaderboard_id == 3:
            self.data_1v1_RM_ranking = rating_data
            pen = pg.mkPen((255, 96, 62), width=2)
        elif leaderboard_id == 4:
            self.data_team_RM_ranking = rating_data
            pen = pg.mkPen((15, 153, 246), width=2)
        elif leaderboard_id == 14:
            self.data_team_EW_ranking = rating_data
            pen = pg.mkPen((82, 168, 39), width=2)
        elif leaderboard_id == 13:
            self.data_1v1_EW_ranking = rating_data
            pen = pg.mkPen((226, 185, 15), width=2)

        ratings = rating_data[0]
        timestamps = rating_data[1]

        plot: pg.PlotDataItem = self.plot()

        plot.setPen(pen)
        plot.setData(y=ratings, x=timestamps)

        self.stored_leaderboard_ratings[leaderboard_id] = rating_data
        self.stored_plot_items[leaderboard_id] = plot

    def update_displayed_plots(self, leaderboard_id, checked):
        if checked:
            ratings, timestamps = self.stored_leaderboard_ratings[leaderboard_id]
            self.stored_plot_items[leaderboard_id].setData(
                y=ratings, x=timestamps)
        else:
            self.stored_plot_items[leaderboard_id].clear()

        self.stored_plot_items[leaderboard_id].updateItems()

    def set_up_for_big_scale_display(self, show: bool):
        for _plot in self.stored_plot_items:
            if _plot is not None:
                plot: pg.PlotDataItem = _plot

                #show Symbols
                plot.setSymbolPen("w")
                plot.setSymbol("o")
                plot.setSymbolSize(5)

    def register_clicked_signal(self, clicked_signal: Signal):
        self.sceneObj.sigMouseMoved.connect(self.mouse_moved)
        self.sceneObj.sigMouseClicked.connect(self.mouse_clicked)
        self.registered_click_signal = clicked_signal

    def mouse_moved(self, evt):
        vb: pg.ViewBox = self.getViewBox()
        mouse_point = vb.mapSceneToView(evt)

        res = self.search_point(mouse_point)
        if res is None:
            if self.curent_text_box != None:
                self.removeItem(self.curent_text_box)
            return
        rating, timestamp, index, lb = res

        arrow_time = arrow.get(int(timestamp))
        time_date = arrow_time.format("YYYY-MM-DD")

        text = f"R: {rating}, D: {time_date}\nClick to see more!"
        text_box = pg.TextItem(text=text, anchor=(-0.2, 0.5), angle=0, border='w', fill=(150, 150, 150, 100))

        if self.curent_text_box != None:
            self.removeItem(self.curent_text_box)

        self.addItem(text_box)
        text_box.setPos(timestamp, rating)

        self.current_hovered_point = (timestamp, lb)
        self.curent_text_box = text_box

    def mouse_clicked(self, evt):
        # Es ist egal wo geklickt wird, es wird ein Singal an AnalyticsWindow gesendet (wird vorher übergeben)
        # Mit den Argument timestamp und leaderboard des momentanen gehoverten Datenpunkt
        # Dann wird ein Match mit dem Zeitcode gesucht und dargestellt
        if self.current_hovered_point != None:
            self.registered_click_signal.emit(self.current_hovered_point)


    # Todo: make a subfunction
    def search_point(self, mouse_point):
        mouse_timestamp = mouse_point.x()
        mouse_rating = mouse_point.y()
        # check if a datapoint is in range
        min_distance = 9999999999
        min_value = (0, 0, 0, 0)
        for index, value in enumerate(self.data_1v1_RM_ranking[0]):
            rating = value
            timestamp = self.data_1v1_RM_ranking[1][index]
            timestamp_distance = abs(mouse_timestamp - timestamp) / 1000
            rating_distance = abs(mouse_rating - rating)

            distance = math.sqrt(timestamp_distance ** 2 + rating_distance ** 2)
            if distance < min_distance:
                min_distance = distance
                min_value = (rating, timestamp, index, 3)
            if distance < 5:
                break

        if min_distance < 10:
            return min_value

        for index, value in enumerate(self.data_team_RM_ranking[0]):
            rating = value
            timestamp = self.data_team_RM_ranking[1][index]
            timestamp_distance = abs(mouse_timestamp - timestamp) / 1000
            rating_distance = abs(mouse_rating - rating)

            distance = math.sqrt(timestamp_distance ** 2 + rating_distance ** 2)
            if distance < min_distance:
                min_distance = distance
                min_value = (rating, timestamp, index, 4)
            if distance < 2:
                break

        if min_distance < 10:
            return min_value

        for index, value in enumerate(self.data_1v1_EW_ranking[0]):
            rating = value
            timestamp = self.data_1v1_EW_ranking[1][index]
            timestamp_distance = abs(mouse_timestamp - timestamp) / 1000
            rating_distance = abs(mouse_rating - rating)

            distance = math.sqrt(timestamp_distance ** 2 + rating_distance ** 2)
            if distance < min_distance:
                min_distance = distance
                min_value = (rating, timestamp, index, 13)

        if min_distance < 10:
            return min_value

        for index, value in enumerate(self.data_team_EW_ranking[0]):
            rating = value
            timestamp = self.data_team_EW_ranking[1][index]
            timestamp_distance = abs(mouse_timestamp - timestamp) / 1000
            rating_distance = abs(mouse_rating - rating)

            distance = math.sqrt(timestamp_distance ** 2 + rating_distance ** 2)
            if distance < min_distance:
                min_distance = distance
                min_value = (rating, timestamp, index, 14)


        if min_distance < 10:
            return min_value

class TeamTableWidget(pg.TableWidget):
    """
    Widget for displaying player infos. Inherits from pygtgraphs's TableWidget. Mostly has functions of a
    QtTableWidget except for the setData function
    """

    def __init__(self, team, number_of_players, parent=None, *args, **kwds):
        super().__init__(parent, *args, **kwds)

        self.number_of_players = number_of_players
        self.team = team
        self.team_data = []

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSortingEnabled(False)

        self.set_size_policy(self.number_of_players)

        self.itemSelectionChanged.connect(self.selec_changed)
        self.cellDoubleClicked.connect(self.cell_double_clicked)

        self.player_data = np.zeros(
            4, dtype=[('Name', object), ('Civ', object), ('Rating', int), ('Win %', float)])

        self.players = np.empty(number_of_players, dtype=BasicPlayerInfo)

        for x in range(0, self.number_of_players):
            player_name = "Player " + str(x + 1)
            self.player_data[x] = (player_name, 'Civ', 0, 0)

        self.setData(self.player_data)

    def set_size_policy(self, number_of_players):
        self.setMinimumSize(300, 25 + number_of_players * 30)
        self.setMaximumSize(3000, 25 + number_of_players * 30)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def update_team(self, team: list[BasicPlayerInfo]):
        self.number_of_players = len(team)
        self.player_data = np.resize(self.player_data, len(team))
        self.team_data = team

        for index, player in enumerate(team):
            self.update_player(index, player)

        self.setData(self.player_data)
        self.resize(300, 20 + len(team) * 25)

        self.setCurrentIndex(self.model().createIndex(0, 0))

        self.set_size_policy(self.number_of_players)

    def update_player(self, player_nr: int, data: BasicPlayerInfo):
        self.player_data[player_nr][0] = data.name
        self.player_data[player_nr][1] = data.civ_name
        self.player_data[player_nr][2] = data.rating
        self.player_data[player_nr][3] = data.win_percentage

        self.players[player_nr] = data

    def selec_changed(self):
        row = self.currentIndex().row()
        self.parent().player_selection_changed(self.team, row)

    def cell_double_clicked(self, row: int):
        import webbrowser
        profile_id = self.players[row].profile_id
        webbrowser.open(APIStringGenerator.get_AoE2_net_link_for_profile_id(profile_id), new=2)

    def update_civ_names(self):
        if len(self.team_data) > 0:
            self.update_team(self.team_data)


class LegendItem(QWidget):
    """Only draws a line to display as legend item in Main Menu"""

    def __init__(self, parent: typing.Optional[QWidget], color) -> None:
        super().__init__(parent=parent)

        self.setMinimumSize(30, 10)
        self.color = color

    def paintEvent(self, e):
        painter = QPainter(self)

        # Team Rating Line
        pen_team = pg.mkPen(self.color, width=2)
        painter.setPen(pen_team)
        line = QLineF(0, self.height() / 2, self.width() - self.width() / 10, self.height() / 2)
        painter.drawLine(line)
        painter.end()
