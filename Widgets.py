from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from pyqtgraph import *
import numpy as np
import time
from DataParser import BasicPlayerInfo


class RatingPlotWidget(PlotWidget):
    def __init__(self, data1v1, parent=None, background='default', plotItem=None, **kargs):
        super().__init__(parent, background, plotItem, **kargs)
        self.data1v1 = data1v1
        ratings1v1 = self.data1v1[0]
        timestamps1v1 = self.data1v1[1]

        self.setBackground(None)
        # self.setLabel("left", "Rating")
        # self.setLabel("bottom", "Time")
        self.setMouseEnabled(x=False, y=False)

        left_axis: AxisItem = self.getAxis("left")
        left_axis.setGrid(10)

        bottom_axis: AxisItem = self.getAxis("bottom")
        bottom_axis.setGrid(10)

        plot_1v1: PlotDataItem = self.plot()

        pen = mkPen((15, 153, 246), width=2)
        plot_1v1.setPen(pen)
        plot_1v1.setData(y=ratings1v1, x=timestamps1v1)

        y_max_val = ratings1v1[ratings1v1.argmax()]
        y_min_val = ratings1v1[ratings1v1.argmin()]
        print(y_max_val, y_min_val)

        self.setYRange(y_min_val, y_max_val, padding=0.02)
        self.setLimits(yMax=y_max_val, yMin=y_min_val)

        x_max_val = time.time()
        x_min_val = timestamps1v1[timestamps1v1.argmin()]
        self.setXRange(x_min_val, x_max_val)
        self.setLimits(xMax=x_max_val)

        rating_mean = ratings1v1.mean()
        mean_x = [0, x_max_val]
        mean_y = [rating_mean, rating_mean]
        plot_1v1_mean: PlotDataItem = self.plot()
        pen = mkPen((223, 178, 21), width=1)
        plot_1v1_mean.setPen(pen)
        plot_1v1_mean.setData(y=mean_y, x=mean_x)


class TeamTableWidget(TableWidget):
    def __init__(self, number_of_players, parent=None, *args, **kwds):
        super().__init__(parent, *args, **kwds)

        self.numbers_of_players = number_of_players

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        self.player_data = np.zeros(4, dtype=[('Name', object), ('Civ', object), ('Rating', int), ('Percentage', float)])

        for x in range(0, self.numbers_of_players):
            player_name = "Player " + str(x + 1)
            self.player_data[x] = (player_name, 'Civ', 0, 0)

        self.setData(self.player_data)

    def update_player(self, player_nr: int, data: BasicPlayerInfo):
        self.player_data[player_nr][2] = data.rating
        self.player_data[player_nr][3] = data.win_percentage

        self.setData(self.player_data)
