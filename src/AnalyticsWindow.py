import json

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from DataHandler import DataHandler
from DataParser import BasicPlayerInfo
from ui.ui_analytics_window import Ui_AnalyticsWindow

from AnalyticsWidgets import MatchDetailWidget

class AnalyticsWindow(QWidget, Ui_AnalyticsWindow):

    sig_player_data_loaded = Signal(tuple)
    sig_match_history_loaded = Signal(tuple)

    def __init__(self, main_window, profile_id: int):
        super().__init__()
        self.set_up_UI()

        self.main_window = main_window
        self.profile_id = profile_id
        self.player_data = None

        # SIGNALS
        self.sig_player_data_loaded.connect(self.player_data_loaded)
        self.sig_match_history_loaded.connect(self.match_history_loaded)

        # setup Data
        self.data_handler = DataHandler()
        self.data_handler.get_basic_player_data(self.profile_id, finish_signal=self.sig_player_data_loaded)

    def set_up_UI(self):
        self.setupUi(self)

        # self.setLayout(self.toplevel_v_layout)
        # image = DataHandler.get_civ_icons_for_id(10)

        # label = QLabel(self)
        # label.setPixmap(QPixmap.fromImage(image))

        # SIGNALS
        self.tab_widget.currentChanged.connect(self.tab_widget_changed_index)
        self.tab_widget_changed_index(0)

        self.mh_tab_load_more_button_4.clicked.connect(self.match_history_load_more_button_clicked)

    def tab_widget_changed_index(self, index: int):
        print(index)


    # UI Signals

    def closeEvent(self, event: QCloseEvent) -> None:
        self.main_window.analytics_window_closed(self)

    def match_history_load_more_button_clicked(self):
        self.data_handler.load_last_matches(self.profile_id, 5, self.sig_match_history_loaded)



    # show match history

    def match_history_loaded(self, data):
        print(data)
        # Display first Match
        v_layout = QVBoxLayout()
        for match in data[1]:
            match_view = MatchDetailWidget(None, match)
            v_layout.addWidget(match_view)

        self.scrollAreaWidgetContents_9.setLayout(v_layout)
    # load Player Data

    def player_data_loaded(self, data):
        if data[0] == 1:
            self.player_data: BasicPlayerInfo = data[1]
            self.player_data.profile_id = self.profile_id
            self.player_name_label.setText(str(self.player_data.profile_id))
            self.populate_player_data_bar(self.player_data)
        else:
            self.main_window.display_network_error()



    def populate_player_data_bar(self, player_data: BasicPlayerInfo):
        self.pd_rating_label.setText(str(player_data.rating))
        self.pd_wins_label.setText(str(player_data.wins))
        self.pd_losses_label.setText(str(player_data.losses))
        self.pd_winperc_label.setText(player_data.win_percentage_str)
