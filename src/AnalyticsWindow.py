import json

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from DataHandler import DataHandler
from DataParser import BasicPlayerInfo
from ui.ui_analytics_window import Ui_AnalyticsWindow

from AnalyticsWidgets import MatchDetailWidget

class AnalyticsWindow(QWidget, Ui_AnalyticsWindow):

    # SIGNALS
    # return type is a tuple where [0] is either 0 or 1 for success and [1] is the data

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

        self.matches = []
        self.matches_loaded = 0
        self.is_currently_loading_matches = False


    def set_up_UI(self):
        self.setupUi(self)

        # self.setLayout(self.toplevel_v_layout)

        # SIGNALS
        self.tab_widget.currentChanged.connect(self.tab_widget_changed_index)
        self.tab_widget_changed_index(0)

        self.mh_tab_scroll_area.verticalScrollBar().actionTriggered.connect(self.scrollbarAction)
        self.mh_tab_load_more_button.clicked.connect(self.match_history_load_more_button_clicked)

    # UI Signals

    def closeEvent(self, event: QCloseEvent) -> None:
        self.main_window.analytics_window_closed(self)

    def match_history_load_more_button_clicked(self):
        self.is_currently_loading_matches = True

        load_matches = 0
        try:
            load_matches = int(self.mh_tab_load_line_edit.text())
        except ValueError:
            if self.mh_tab_load_line_edit.placeholderText() != "":
                load_matches = int(self.mh_tab_load_line_edit.placeholderText())
                self.mh_tab_load_line_edit.setPlaceholderText("")
        else:
            if load_matches > 50:
                load_matches = 50

        self.mh_tab_load_line_edit.setText(str(load_matches))

        if load_matches > 0:
            self.data_handler.load_last_matches(self.profile_id, load_matches, self.matches_loaded,
                                                self.sig_match_history_loaded)

    def scrollbarAction(self, action: int):
        slider = self.mh_tab_scroll_area.verticalScrollBar()

        max = slider.maximum()
        current = slider.sliderPosition()
        state = float(current) / float(max)

        if state > 0.99:
            pass
            # load new Data
            # if not self.is_currently_loading_matches:
            #    self.data_handler.load_last_matches(self.profile_id, 5, self.matches_loaded, self.sig_match_history_loaded)

    def tab_widget_changed_index(self, index: int):
        print(index)

    # show match history

    def match_history_loaded(self, data):

        v_layout = QVBoxLayout()
        if self.mh_tab_scroll_area_content.layout() is not None:
            v_layout = self.mh_tab_scroll_area_content.layout()
        for match in data[1]:
            match_view = MatchDetailWidget(None, match)
            v_layout.addWidget(match_view, alignment=Qt.AlignTop)
            self.matches_loaded += 1

        if self.mh_tab_scroll_area_content.layout() is None:
            self.mh_tab_scroll_area_content.setLayout(v_layout)

        self.is_currently_loading_matches = False

        print(f"{self.matches_loaded = }")

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
