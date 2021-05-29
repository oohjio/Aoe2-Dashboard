from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from pyqtgraph import *
import numpy as np
import time
from DataParser import BasicPlayerInfo


class RatingPlotWidget(PlotWidget):
    """
    Plot Widget inherited by pyqtgraph's PlotWidget for displaying Ratings in a timeframe
    """

    def __init__(self, player_name: str, parent=None, background='default', plotItem=None, **kargs):
        super().__init__(parent, background, plotItem,
                         axisItems={'bottom': DateAxisItem()}, **kargs)

        self.player_name = player_name
        self.setBackground(None)
        # self.setLabel("bottom", "Time")

        self.setMouseEnabled(x=False, y=False)

        left_axis: AxisItem = self.getAxis("left")
        left_axis.setGrid(10)

        bottom_axis: AxisItem = self.getAxis("bottom")
        bottom_axis.setGrid(10)

        self.data_team_ranking = None
        self.data_1v1_ranking = None

        left_label_str = "Rating of " + self.player_name
        self.setLabel("left", left_label_str)

    def plot_rating(self, ratingdata, leaderboard_id):
        pen = mkPen((0, 0, 0), width=2)
        if leaderboard_id == 3:
            self.data_1v1_ranking = ratingdata
            pen = mkPen((255, 96, 62), width=2)
        elif leaderboard_id == 4:
            self.data_team_ranking = ratingdata
            pen = mkPen((15, 153, 246), width=2)

        ratings = ratingdata[0]
        timestamps = ratingdata[1]

        plot: PlotDataItem = self.plot()
        
        plot.setPen(pen)
        plot.setData(y=ratings, x=timestamps)

    def set_min_max_values(self):
        """I think this function is obsolete"""
        # set y Range
        y_min_vals = []
        y_max_vals = []

        if self.data_1v1_ranking is not None and len(self.data_1v1_ranking[0]) > 0:
            ratings = self.data_1v1_ranking[0]
            y_max_vals.append(ratings[ratings.argmax()])
            y_min_vals.append(ratings[ratings.argmin()])

        if self.data_team_ranking is not None and len(self.data_team_ranking[0]) > 0:
            ratings = self.data_team_ranking[0]
            y_max_vals.append(ratings[ratings.argmax()])
            y_min_vals.append(ratings[ratings.argmin()])

        y_min_vals.sort()
        y_min_val = y_min_vals[0]
        y_max_vals.sort(reverse=True)
        y_max_val = y_max_vals[0]
        print(y_min_vals, y_min_val)
        print(y_max_vals, y_max_val)

        self.setYRange(y_min_val, y_max_val)
        self.setLimits(yMax=y_max_val, yMin=y_min_val)

        # x_max_val = time.time()
        # x_min_val = timestamps_team[timestamps_team.argmin()]
        # self.setXRange(x_min_val, x_max_val)
        # self.setLimits(xMax=x_max_val)


class TeamTableWidget(TableWidget):
    """Widget for displaying player infos. Inherits from pygtgraphs's TableWidget. Mostly has functions of a QtTableWidget except for the setData function"""

    def __init__(self, team, number_of_players, parent=None, *args, **kwds):
        super().__init__(parent, *args, **kwds)

        self.numbers_of_players = number_of_players
        self.team = team

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSortingEnabled(False)

        self.itemSelectionChanged.connect(self.selec_changed)

        self.player_data = np.zeros(
            4, dtype=[('Name', object), ('Civ', object), ('Rating', int), ('Win %', float)])

        for x in range(0, self.numbers_of_players):
            player_name = "Player " + str(x + 1)
            self.player_data[x] = (player_name, 'Civ', 0, 0)

        self.setData(self.player_data)

    def update_team(self, team: list[BasicPlayerInfo]):
        self.numbers_of_players = len(team)
        self.player_data = numpy.resize(self.player_data, len(team))

        for index, player in enumerate(team):
            self.update_player(index, player)

        self.setData(self.player_data)
        self.resize(300, 20 + len(team) * 25)

        self.setCurrentIndex(self.model().createIndex(0, 0))
        self.setHidden(False)

    def update_player(self, player_nr: int, data: BasicPlayerInfo):
        self.player_data[player_nr][0] = data.name
        self.player_data[player_nr][1] = data.civ_name
        self.player_data[player_nr][2] = data.rating
        self.player_data[player_nr][3] = data.win_percentage

        self.setData(self.player_data)

    def selec_changed(self):
        row = self.currentIndex().row()
        self.parent().player_selection_changed(self.team, row)
