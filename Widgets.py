from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from pyqtgraph import *
import numpy as np
import time
from DataParser import BasicPlayerInfo


class RatingPlotWidget(PlotWidget):
    def __init__(self, data_team_ranking, player_name: str, parent=None, background='default', plotItem=None, **kargs):
        super().__init__(parent, background, plotItem, **kargs)
        self.data_team_ranking = data_team_ranking
        self.player_name = player_name

        ratings_team = self.data_team_ranking[0]
        timestamps_team = self.data_team_ranking[1]

        self.setBackground(None)
        left_label_str = "Team Rating of " + self.player_name
        self.setLabel("left", left_label_str)
        # self.setLabel("bottom", "Time")
        self.setMouseEnabled(x=False, y=False)

        left_axis: AxisItem = self.getAxis("left")
        left_axis.setGrid(10)

        bottom_axis: AxisItem = self.getAxis("bottom")
        bottom_axis.setGrid(10)

        plot_team: PlotDataItem = self.plot()

        pen = mkPen((15, 153, 246), width=2)
        plot_team.setPen(pen)
        plot_team.setData(y=ratings_team, x=timestamps_team)

        y_max_val = ratings_team[ratings_team.argmax()]
        y_min_val = ratings_team[ratings_team.argmin()]

        self.setYRange(y_min_val, y_max_val, padding=0.02)
        self.setLimits(yMax=y_max_val, yMin=y_min_val)

        x_max_val = time.time()
        x_min_val = timestamps_team[timestamps_team.argmin()]
        self.setXRange(x_min_val, x_max_val)
        self.setLimits(xMax=x_max_val)

        rating_mean = ratings_team.mean()
        mean_x = [0, x_max_val]
        mean_y = [rating_mean, rating_mean]
        plot_team_mean: PlotDataItem = self.plot()
        pen = mkPen((223, 178, 21), width=1)
        plot_team_mean.setPen(pen)
        plot_team_mean.setData(y=mean_y, x=mean_x)


class TeamTableWidget(TableWidget):
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

        self.player_data = np.zeros(4, dtype=[('Name', object), ('Civ', object), ('Rating', int), ('Win %', float)])

        for x in range(0, self.numbers_of_players):
            player_name = "Player " + str(x + 1)
            self.player_data[x] = (player_name, 'Civ', 0, 0)

        self.setData(self.player_data)

    def update_team(self, team: [BasicPlayerInfo]):
        for index, player in enumerate(team):
            self.update_player(index, player)

        self.player_data = numpy.resize(self.player_data, len(team))
        self.setData(self.player_data)
        self.resize(300, 20 + len(team) * 25)

        self.setCurrentIndex(self.model().createIndex(0, 0))

    def update_player(self, player_nr: int, data: BasicPlayerInfo):
        self.player_data[player_nr][0] = data.name
        self.player_data[player_nr][1] = data.civ_name
        self.player_data[player_nr][2] = data.rating
        self.player_data[player_nr][3] = data.win_percentage

        self.setData(self.player_data)

    def selec_changed(self):
        row = self.currentIndex().row()
        self.parent().player_selection_changed(self.team, row)




