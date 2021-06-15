import json
from queue import Queue
from threading import Thread

import requests
from PySide6.QtCore import Qt, QSettings
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QProgressBar
from PySide6.QtGui import QCloseEvent
import keys as keys
from APIStringGenerator import APIStringGenerator
import os.path

class PrefPanel(QWidget):
    """Panel that displays a field for setting a new player_id, has functions to determine if a player_id is valid"""

    def __init__(self, main_window):
        super().__init__()

        self.setWindowTitle("Preferences")
        self.main_window = main_window

        label_profile_id = QLabel("Set here your Aoe2.net Profile ID")

        font_bold = label_profile_id.font()
        font_bold.setBold(True)

        font_italic = label_profile_id.font()
        font_italic.setItalic(True)

        options_label = QLabel("App Options")
        options_label.setFont(font_bold)

        locale_opt_label = QLabel("Set the API Locale")
        self.api_locale_combo_box = QComboBox()
        self.api_locale_combo_box.setMinimumSize(260, 25)
        with open(os.path.dirname(__file__) + "/../data/api_strings/locals.csv", "r") as read_file:
            self.locals = read_file.read().split(",")
            self.api_locale_combo_box.insertItems(0, self.locals)
        self.api_locale_combo_box.setCurrentIndex(self.get_saved_locale_from_settings())

        save_options_push_button = QPushButton("Save Options")
        save_options_push_button.setMinimumSize(260, 34)
        save_options_push_button.clicked.connect(self.save_options)

        profile_id_label = QLabel("Profile ID")
        profile_id_label.setFont(font_bold)

        save_profile_id_push_button = QPushButton("Search and Save")
        save_profile_id_push_button.setMinimumSize(260, 34)
        save_profile_id_push_button.clicked.connect(self.save_player_id)

        self.profile_id_line_edit = QLineEdit()
        self.profile_id_line_edit.setMinimumSize(260, 25)

        self.feedback_label = QLabel("Type in your ID")
        self.feedback_label.setFont(font_italic)

        self.busy_indicator = QProgressBar()
        self.busy_indicator.setMinimumSize(260, 10)
        self.busy_indicator.setTextVisible(False)
        self.busy_indicator.setMaximum(2)
        self.busy_indicator.setMinimum(0)
        self.busy_indicator.setHidden(True)

        v_layout_left = QVBoxLayout()

        v_layout_left.addWidget(options_label, alignment=Qt.AlignTop)
        v_layout_left.addWidget(locale_opt_label, alignment=Qt.AlignTop)
        v_layout_left.addWidget(self.api_locale_combo_box, alignment=Qt.AlignTop)
        v_layout_left.addWidget(save_options_push_button, alignment=Qt.AlignBottom)

        v_layout_right = QVBoxLayout()

        v_layout_right.addWidget(profile_id_label)
        v_layout_right.addWidget(label_profile_id)
        v_layout_right.addWidget(self.profile_id_line_edit)
        v_layout_right.addWidget(self.feedback_label)
        v_layout_right.addWidget(self.busy_indicator)
        v_layout_right.addWidget(save_profile_id_push_button)

        h_layout = QHBoxLayout()
        h_layout.addLayout(v_layout_left)
        h_layout.addSpacing(20)
        h_layout.addLayout(v_layout_right)
        self.setLayout(h_layout)

    def save_options(self):
        # Save Locale
        self.save_player_locale_to_settings(self.api_locale_combo_box.currentIndex())
        self.main_window.update_api_locale()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.main_window.pref_panel_closed(self)



    @staticmethod
    def get_saved_locale_from_settings():
        settings = QSettings()
        if settings.contains(keys.k_set_api_locale):
            return int(settings.value(keys.k_set_api_locale))
        else:
            return 0

    @staticmethod
    def save_player_locale_to_settings(locale: int):
        settings = QSettings()
        settings.setValue(keys.k_set_api_locale, locale)

    def save_player_id(self):
        new_player_id = 0
        try:
            new_player_id = int(self.profile_id_line_edit.text())
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
                    if data is True:
                        settings = QSettings()
                        print("settings set")
                        settings.setValue(keys.k_player_id_key, new_player_id)
                        self.busy_indicator.setValue(2)

    @staticmethod
    def does_player_exist(player_id: int, q: Queue, _sentinel):
        """
        This function checks whether a player_id exists on the RM 1v1 Leaderboard and then on the Team RM Leaderboard.
        DM / EW ladder atm not supported
        Player needs to be found on one of those leaderboards in order to be a valid player_id
        Needs to be called with a Queue item and a _sentinel that returns the state of the current process
        """

        player_found = False

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
        if not player_found:
            q.put("No Player found")

        q.put(player_found)
        q.put(_sentinel)
