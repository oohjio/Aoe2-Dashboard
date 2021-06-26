import typing

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

from DataParser import Match
from DataHandler import DataHandler

class MatchDetailWidget(QWidget):
    def __init__(self, parent: typing.Optional[QWidget], match: Match) -> None:
        super().__init__(parent=parent)

        # Size
        self.setMinimumSize(QSize(700, 200))
        self.match = match

        # Set Up UI
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(4)

        # Opp
        for index, player in enumerate(match.team_2_players):
            item = CivAndColorItem(None, player.color, player.civ_id)
            grid_layout.addWidget(item, index, 0, Qt.AlignLeft)

            civ_name_label = QLabel(player.civ_name)
            grid_layout.addWidget(civ_name_label, index, 1, Qt.AlignLeft)

            bold_font = civ_name_label.font()
            bold_font.setBold(True)

            player_name_label = QLabel(player.name)
            player_name_label.setFont(bold_font)
            grid_layout.addWidget(player_name_label, index, 2, Qt.AlignLeft)

        # Player
        for index, player in enumerate(match.team_1_players):
            item = CivAndColorItem(None, player.color, player.civ_id)
            grid_layout.addWidget(item, index, 5, Qt.AlignRight)

            civ_name_label = QLabel(player.civ_name)
            grid_layout.addWidget(civ_name_label, index, 4, Qt.AlignRight)

            bold_font = civ_name_label.font()
            bold_font.setBold(True)

            player_name_label = QLabel(player.name)
            player_name_label.setFont(bold_font)
            grid_layout.addWidget(player_name_label, index, 3, Qt.AlignRight)


        self.setLayout(grid_layout)


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

        from pyqtgraph import mkPen
        pen = mkPen(self.color, width=3)
        painter.setPen(pen)
        points = [QPointF(2.5, 2.5), QPointF(47.5, 2.5), QPointF(47.5, 47.5), QPointF(2.5, 47.5), QPointF(2.5, 2.5)]
        painter.drawPolyline(points)

        painter.end()