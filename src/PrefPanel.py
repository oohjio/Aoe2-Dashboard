import json
import os.path
from threading import Thread

import requests
from PySide6.QtCore import Qt, QSettings, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import *

import keys as keys
from APIStringGenerator import APIStringGenerator


# noinspection PyUnresolvedReferences
class PrefPanel(QWidget):
    """Panel that displays a field for setting a new profile_id, has functions to determine if a profile_id is valid"""

    # tuple should return an int for leaderboard_id and a return status as a bool (True = success), and the profile_id
    sig_leaderboard_checked = Signal(tuple)
    # tuple with a int indicator (1 for general options, 2 for profile_id, and a bool for success
    sig_save_successfully = Signal(tuple)

    def __init__(self, main_window):
        super().__init__()

        self.setWindowTitle("Preferences")
        self.main_window = main_window

        # SIGNAL
        self.sig_leaderboard_checked.connect(self.leaderboard_checked)
        self.sig_save_successfully.connect(self.saved_successfully_to_settings)

        self.player_found_on_leaderboard = False
        self.player_leaderboard_feedback_count = 0

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
        save_profile_id_push_button.clicked.connect(self.save_profile_id_button_pressed)

        self.profile_id_line_edit = QLineEdit()
        self.profile_id_line_edit.setMinimumSize(260, 25)

        self.feedback_label = QLabel("Type in your ID")
        self.feedback_label.setFont(font_italic)

        self.busy_indicator = QProgressBar()
        self.busy_indicator.setMinimumSize(260, 10)
        self.busy_indicator.setTextVisible(False)
        self.busy_indicator.setMaximum(0)
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

    def save_profile_id_button_pressed(self):
        try:
            new_profile_id = int(self.profile_id_line_edit.text())
        except ValueError:
            self.feedback_label.setText("You have to type a number")
        else:
            self.check_profile_id(new_profile_id, self.sig_leaderboard_checked)
            self.busy_indicator.setHidden(False)
            self.player_found_on_leaderboard = False
            self.player_leaderboard_feedback_count = 0

    def leaderboard_checked(self, data):
        print(data)
        if data[1] == True:
            print("Player found")
            self.player_found_on_leaderboard = True
            self.busy_indicator.setHidden(True)
            self.feedback_label.setText("Player found on Leaderboard {}".format(data[0]))
            save_thread = Thread(target=self.save_profile_id_to_settings, args=(data[2], self.sig_save_successfully))
            save_thread.start()
        else:
            if self.player_found_on_leaderboard:
                return
            else:
                self.feedback_label.setText("Player not yet found")
                self.player_leaderboard_feedback_count += 1
                if self.player_leaderboard_feedback_count == 4:
                    self.feedback_label.setText("Player not fond at all")
                    PrefPanel.display_player_not_found_nessage()
                    self.busy_indicator.setHidden(True)

    def saved_successfully_to_settings(self, data):
        if data[0] == 2 and data[1] == True:
            self.feedback_label.setText("Profile ID successfully saved")

    @staticmethod
    def save_profile_id_to_settings(profile_id: int, feedback_signal: Signal):
        try:
            settings = QSettings()
        except:
            return_value = (2, True)
            feedback_signal.emit(return_value)
        else:
            settings.setValue(keys.k_profile_id_key, profile_id)
            return_value = (2, True)
            feedback_signal.emit(return_value)

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

    @staticmethod
    def check_profile_id(profile_id: int, feedback_signal: Signal):
        """
        This function checks whether a profile_id exists on the 4 existing leaderboards
        Therefore 4 threads were simultaneously created to search for the player
        Player needs to be found on one of those leaderboards in order to be a valid profile_id
        """
        for n in range(1, 5):
            thread = Thread(target=PrefPanel.check_player_on_leaderboard, args=(profile_id, n, feedback_signal))
            thread.start()

    @staticmethod
    def check_player_on_leaderboard(profile_id: int, leaderboard_id: int, feedback_signal: Signal):
        api_str = APIStringGenerator.get_API_string_for_rating_history(leaderboard_id, profile_id, 1)
        try:
            response = requests.get(api_str)
            data = json.loads(response.text)
        except:
            # from MainWindow import MainWindow
            # MainWindow.display_network_error()
            return_value = (leaderboard_id, False, profile_id)
            feedback_signal.emit(return_value)
        else:
            if len(data) > 0:
                return_value = (leaderboard_id, True, profile_id)
                feedback_signal.emit(return_value)
            else:
                return_value = (leaderboard_id, False, profile_id)
                feedback_signal.emit(return_value)

    @staticmethod
    def display_player_not_found_nessage():
        message_box = QMessageBox()
        message_box.setText("Your Player ID was not on found on one of the leaderboards.")
        message_box.setInformativeText(
            "This is either due to networking problems or you not having at least 10 matches on of the ladders.")
        message_box.setStandardButtons(QMessageBox.Ok)

        message_box.exec()
