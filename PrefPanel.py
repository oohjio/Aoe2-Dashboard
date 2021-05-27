import json

from threading import Thread
from queue import Queue

import requests
from PySide6.QtCore import *
from PySide6.QtWidgets import *

import keys
from APIStringGenerator import APIStringGenerator


class PrefPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Preferences")

        self.pushButton = QPushButton("Save", self)
        self.pushButton.setGeometry(20, 95, 260, 34)
        self.pushButton.clicked.connect(self.saveEdit)

        self.label = QLabel("Set here your Aoe2.net Profile ID", self)
        self.label.setGeometry(20, 10, 261, 18)

        self.lineEdit = QLineEdit(self)
        self.lineEdit.setGeometry(20, 40, 260, 25)

        self.feedback_label = QLabel("Type in your ID", self)
        self.feedback_label.setGeometry(20, 70, 260, 18)

        self.busy_indicator = QProgressBar(self)
        self.busy_indicator.setGeometry(20, 135, 260, 10)
        self.busy_indicator.setTextVisible(False)
        self.busy_indicator.setMaximum(2)
        self.busy_indicator.setMinimum(0)
        self.busy_indicator.setHidden(True)

    def saveEdit(self):
        new_player_id = 0
        try:
            new_player_id = int(self.lineEdit.text())
            print(new_player_id)
        except ValueError:
            print("You have to type a number")

        if new_player_id != 0:
            self.busy_indicator.setHidden(False)
            self.busy_indicator.setValue(0)

            q = Queue()
            _sentinel = object()

            find_thread = Thread(target=self.does_player_exist, args=(new_player_id, q, _sentinel))
            find_thread.start()

            while True:
                data = q.get()

                if data is _sentinel:
                    # Terminate
                    q.put(_sentinel)
                    self.busy_indicator.setHidden(True)
                    break
                elif type(data) is str:
                    self.feedback_label.setText(data)
                    self.busy_indicator.setValue(1)
                elif type(data) is bool:
                    if data == True:
                        settings = QSettings()
                        print("settings set")
                        settings.setValue(keys._k_player_id_key, new_player_id)
                        self.busy_indicator.setValue(2)

    @staticmethod
    def does_player_exist(player_id: int, q: Queue, _sentinel):
        """This function checks whether a player_id exists on the RM 1v1 Leaderboard and then on the Team RM
        Leaderboard."""

        player_found = False
        # check if player exists on leaderboards
        # first 1v1 Leaderboard
        url_str = APIStringGenerator.get_API_string_for_rating_history(3, player_id, 1)
        try:
            response = requests.get(url_str)
            data = json.loads(response.text)
            if len(data) > 0:
                player_found = True
                q.put("Player found on 1v1 Leaderboard")
            else:
                q.put("No Player found on 1v1 Leaderboard")
        except:
            q.put("Some Error occurred")

        if not player_found:
            # check Team Leaderboard
            url_str = APIStringGenerator.get_API_string_for_rating_history(4, player_id, 1)
            try:
                response = requests.get(url_str)
                data = json.loads(response.text)
                if len(data) > 0:
                    player_found = True
                    q.put("Player found on Team Leaderboard")
                else:
                    q.put("No Player found on Team Leaderboard")
            except:
                q.put("Some Error occurred")
        if not player_found: q.put("No Player found")

        q.put(player_found)
        q.put(_sentinel)
