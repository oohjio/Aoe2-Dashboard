from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import json
import requests

_k_player_id_key = "player/player_id"

class PrefPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Preferences")

        self.pushButton = QPushButton("Save", self)
        self.pushButton.setGeometry(QRect(20, 100, 260, 34))
        self.pushButton.clicked.connect(self.saveEdit)

        self.label = QLabel("Set here your Aoe2.net Profile ID", self)
        self.label.setGeometry(QRect(20, 10, 261, 18))

        self.lineEdit = QLineEdit(self)
        self.lineEdit.setGeometry(QRect(20, 40, 261, 25))

    def saveEdit(self):
        new_player_id = 0
        try:
            new_player_id = int(self.lineEdit.text())
            print(new_player_id)
        except ValueError:
            print("You have to type a number")

        if new_player_id != 0:
            if self.does_player_exist(new_player_id):
                # set new setting
                settings = QSettings()
                settings.setValue(_k_player_id_key, new_player_id)


    def does_player_exist(self, player_id: int) -> bool:
        player_found = False
        # check if player exists on leaderboards
        # first 1v1 Leaderboard
        url_str = "https://aoe2.net/api/player/ratinghistory?game=aoe2de&leaderboard_id=3&profile_id=" \
                  + str(player_id) + "&count=1"
        try:
            response = requests.get(url_str)
            data = json.loads(response.text)
            if len(data) > 0:
                player_found = True
                print("Player found on 1v1 Leaderboard")
            else:
                print("No Player found on 1v1 Leaderboard")
        except:
            print("Some Error occurred")

        if not player_found:
            # check Team Leaderboard
            url_str = "https://aoe2.net/api/player/ratinghistory?game=aoe2de&leaderboard_id=4&profile_id=" \
                      + str(player_id) + "&count=1"
            try:
                response = requests.get(url_str)
                data = json.loads(response.text)
                if len(data) > 0:
                    player_found = True
                    print("Player found on Team Leaderboard")
                else:
                    print("No Player found on Team Leaderboard")
            except:
                print("Some Error occurred")

        return player_found