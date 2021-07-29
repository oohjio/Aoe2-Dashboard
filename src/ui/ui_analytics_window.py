# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analytics_windowtyEynp.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_AnalyticsWindow(object):
    def setupUi(self, AnalyticsWindow):
        if not AnalyticsWindow.objectName():
            AnalyticsWindow.setObjectName(u"AnalyticsWindow")
        AnalyticsWindow.resize(850, 590)
        AnalyticsWindow.setMinimumSize(QSize(850, 560))
        self.layoutWidget = QWidget(AnalyticsWindow)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 20, 827, 572))
        self.toplevel_v_layout = QVBoxLayout(self.layoutWidget)
        self.toplevel_v_layout.setObjectName(u"toplevel_v_layout")
        self.toplevel_v_layout.setContentsMargins(0, 0, 0, 0)
        self.player_name_h_layout = QHBoxLayout()
        self.player_name_h_layout.setObjectName(u"player_name_h_layout")
        self.play_displ_label = QLabel(self.layoutWidget)
        self.play_displ_label.setObjectName(u"play_displ_label")

        self.player_name_h_layout.addWidget(self.play_displ_label)

        self.player_name_label = QLabel(self.layoutWidget)
        self.player_name_label.setObjectName(u"player_name_label")

        self.player_name_h_layout.addWidget(self.player_name_label)

        self.h_layout_ladder_buttons = QHBoxLayout()
        self.h_layout_ladder_buttons.setObjectName(u"h_layout_ladder_buttons")
        self.button_1v1_RM = QToolButton(self.layoutWidget)
        self.button_1v1_RM.setObjectName(u"button_1v1_RM")
        self.button_1v1_RM.setEnabled(True)
        self.button_1v1_RM.setMaximumSize(QSize(55, 18))
        self.button_1v1_RM.setCheckable(True)
        self.button_1v1_RM.setChecked(True)
        self.button_1v1_RM.setAutoExclusive(True)
        self.button_1v1_RM.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.button_1v1_RM.setArrowType(Qt.NoArrow)

        self.h_layout_ladder_buttons.addWidget(self.button_1v1_RM)

        self.button_1v1_EW = QToolButton(self.layoutWidget)
        self.button_1v1_EW.setObjectName(u"button_1v1_EW")
        self.button_1v1_EW.setMaximumSize(QSize(55, 18))
        self.button_1v1_EW.setCheckable(True)
        self.button_1v1_EW.setAutoExclusive(True)
        self.button_1v1_EW.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.button_1v1_EW.setArrowType(Qt.NoArrow)

        self.h_layout_ladder_buttons.addWidget(self.button_1v1_EW)

        self.button_team_RM = QToolButton(self.layoutWidget)
        self.button_team_RM.setObjectName(u"button_team_RM")
        self.button_team_RM.setMaximumSize(QSize(65, 18))
        self.button_team_RM.setCheckable(True)
        self.button_team_RM.setAutoExclusive(True)
        self.button_team_RM.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.button_team_RM.setArrowType(Qt.NoArrow)

        self.h_layout_ladder_buttons.addWidget(self.button_team_RM)

        self.button_team_EW = QToolButton(self.layoutWidget)
        self.button_team_EW.setObjectName(u"button_team_EW")
        self.button_team_EW.setMaximumSize(QSize(65, 20))
        self.button_team_EW.setCheckable(True)
        self.button_team_EW.setAutoExclusive(True)
        self.button_team_EW.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.button_team_EW.setArrowType(Qt.NoArrow)

        self.h_layout_ladder_buttons.addWidget(self.button_team_EW)


        self.player_name_h_layout.addLayout(self.h_layout_ladder_buttons)


        self.toplevel_v_layout.addLayout(self.player_name_h_layout)

        self.player_data_h_layout = QHBoxLayout()
        self.player_data_h_layout.setObjectName(u"player_data_h_layout")
        self.pd_displ_rating_label = QLabel(self.layoutWidget)
        self.pd_displ_rating_label.setObjectName(u"pd_displ_rating_label")
        self.pd_displ_rating_label.setMinimumSize(QSize(98, 0))

        self.player_data_h_layout.addWidget(self.pd_displ_rating_label)

        self.pd_rating_label = QLabel(self.layoutWidget)
        self.pd_rating_label.setObjectName(u"pd_rating_label")

        self.player_data_h_layout.addWidget(self.pd_rating_label)

        self.pd_displ_wins_label = QLabel(self.layoutWidget)
        self.pd_displ_wins_label.setObjectName(u"pd_displ_wins_label")

        self.player_data_h_layout.addWidget(self.pd_displ_wins_label, 0, Qt.AlignLeft)

        self.pd_wins_label = QLabel(self.layoutWidget)
        self.pd_wins_label.setObjectName(u"pd_wins_label")

        self.player_data_h_layout.addWidget(self.pd_wins_label)

        self.pd_displ_losses_label = QLabel(self.layoutWidget)
        self.pd_displ_losses_label.setObjectName(u"pd_displ_losses_label")

        self.player_data_h_layout.addWidget(self.pd_displ_losses_label)

        self.pd_losses_label = QLabel(self.layoutWidget)
        self.pd_losses_label.setObjectName(u"pd_losses_label")

        self.player_data_h_layout.addWidget(self.pd_losses_label)

        self.pd_displ_winperc_label = QLabel(self.layoutWidget)
        self.pd_displ_winperc_label.setObjectName(u"pd_displ_winperc_label")

        self.player_data_h_layout.addWidget(self.pd_displ_winperc_label)

        self.pd_winperc_label = QLabel(self.layoutWidget)
        self.pd_winperc_label.setObjectName(u"pd_winperc_label")

        self.player_data_h_layout.addWidget(self.pd_winperc_label)


        self.toplevel_v_layout.addLayout(self.player_data_h_layout)

        self.tab_widget = QTabWidget(self.layoutWidget)
        self.tab_widget.setObjectName(u"tab_widget")
        self.tab_widget.setMinimumSize(QSize(825, 500))
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.match_history_tab = QWidget()
        self.match_history_tab.setObjectName(u"match_history_tab")
        self.layoutWidget_3 = QWidget(self.match_history_tab)
        self.layoutWidget_3.setObjectName(u"layoutWidget_3")
        self.layoutWidget_3.setGeometry(QRect(10, 10, 802, 444))
        self.mh_tab_v_layout = QVBoxLayout(self.layoutWidget_3)
        self.mh_tab_v_layout.setObjectName(u"mh_tab_v_layout")
        self.mh_tab_v_layout.setContentsMargins(0, 0, 0, 0)
        self.mh_tab_bar_h_layout = QHBoxLayout()
        self.mh_tab_bar_h_layout.setObjectName(u"mh_tab_bar_h_layout")
        self.mh_tab_bar_h_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.mh_tab_bar_h_layout.setContentsMargins(0, -1, -1, -1)
        self.mh_tab_info_label = QLabel(self.layoutWidget_3)
        self.mh_tab_info_label.setObjectName(u"mh_tab_info_label")
        font = QFont()
        font.setItalic(True)
        self.mh_tab_info_label.setFont(font)

        self.mh_tab_bar_h_layout.addWidget(self.mh_tab_info_label)

        self.mh_tab_load_line_edit = QLineEdit(self.layoutWidget_3)
        self.mh_tab_load_line_edit.setObjectName(u"mh_tab_load_line_edit")
        self.mh_tab_load_line_edit.setMaximumSize(QSize(40, 16777215))

        self.mh_tab_bar_h_layout.addWidget(self.mh_tab_load_line_edit, 0, Qt.AlignRight)

        self.mh_tab_bar_spacer = QSpacerItem(15, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.mh_tab_bar_h_layout.addItem(self.mh_tab_bar_spacer)

        self.mh_tab_load_more_button = QPushButton(self.layoutWidget_3)
        self.mh_tab_load_more_button.setObjectName(u"mh_tab_load_more_button")
        self.mh_tab_load_more_button.setMaximumSize(QSize(100, 16777215))
        self.mh_tab_load_more_button.setCheckable(False)
        self.mh_tab_load_more_button.setChecked(False)
        self.mh_tab_load_more_button.setFlat(False)

        self.mh_tab_bar_h_layout.addWidget(self.mh_tab_load_more_button)


        self.mh_tab_v_layout.addLayout(self.mh_tab_bar_h_layout)

        self.mh_tab_scroll_area = QScrollArea(self.layoutWidget_3)
        self.mh_tab_scroll_area.setObjectName(u"mh_tab_scroll_area")
        self.mh_tab_scroll_area.setMinimumSize(QSize(800, 400))
        self.mh_tab_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.mh_tab_scroll_area.setWidgetResizable(True)
        self.mh_tab_scroll_area_content = QWidget()
        self.mh_tab_scroll_area_content.setObjectName(u"mh_tab_scroll_area_content")
        self.mh_tab_scroll_area_content.setGeometry(QRect(0, 0, 796, 396))
        self.mh_tab_scroll_area.setWidget(self.mh_tab_scroll_area_content)

        self.mh_tab_v_layout.addWidget(self.mh_tab_scroll_area)

        self.tab_widget.addTab(self.match_history_tab, "")
        self.rating_history_tab = QWidget()
        self.rating_history_tab.setObjectName(u"rating_history_tab")
        self.layoutWidget_2 = QWidget(self.rating_history_tab)
        self.layoutWidget_2.setObjectName(u"layoutWidget_2")
        self.layoutWidget_2.setGeometry(QRect(10, 10, 802, 452))
        self.rh_tab_v_layout = QVBoxLayout(self.layoutWidget_2)
        self.rh_tab_v_layout.setObjectName(u"rh_tab_v_layout")
        self.rh_tab_v_layout.setContentsMargins(0, 0, 0, 0)
        self.rh_tab_bar_h_layout = QHBoxLayout()
        self.rh_tab_bar_h_layout.setObjectName(u"rh_tab_bar_h_layout")
        self.rh_tab_bar_h_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.rh_tab_bar_h_layout.setContentsMargins(0, -1, -1, -1)
        self.rh_info_label = QLabel(self.layoutWidget_2)
        self.rh_info_label.setObjectName(u"rh_info_label")
        self.rh_info_label.setFont(font)

        self.rh_tab_bar_h_layout.addWidget(self.rh_info_label)

        self.rh_tab_bar_spacer = QSpacerItem(15, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.rh_tab_bar_h_layout.addItem(self.rh_tab_bar_spacer)

        self.rh_tab_load_more_button = QPushButton(self.layoutWidget_2)
        self.rh_tab_load_more_button.setObjectName(u"rh_tab_load_more_button")
        self.rh_tab_load_more_button.setMaximumSize(QSize(100, 16777215))

        self.rh_tab_bar_h_layout.addWidget(self.rh_tab_load_more_button)


        self.rh_tab_v_layout.addLayout(self.rh_tab_bar_h_layout)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")

        self.rh_tab_v_layout.addLayout(self.verticalLayout)

        self.mh_tab_graphics_view = QGraphicsView(self.layoutWidget_2)
        self.mh_tab_graphics_view.setObjectName(u"mh_tab_graphics_view")
        self.mh_tab_graphics_view.setMinimumSize(QSize(800, 400))

        self.rh_tab_v_layout.addWidget(self.mh_tab_graphics_view)

        self.tab_widget.addTab(self.rating_history_tab, "")

        self.toplevel_v_layout.addWidget(self.tab_widget)


        self.retranslateUi(AnalyticsWindow)

        self.tab_widget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(AnalyticsWindow)
    # setupUi

    def retranslateUi(self, AnalyticsWindow):
        AnalyticsWindow.setWindowTitle(QCoreApplication.translate("AnalyticsWindow", u"Analytics", None))
        self.play_displ_label.setText(QCoreApplication.translate("AnalyticsWindow", u"Analytics of", None))
        self.player_name_label.setText(QCoreApplication.translate("AnalyticsWindow", u"TextLabel", None))
        self.button_1v1_RM.setText(QCoreApplication.translate("AnalyticsWindow", u"1v1 RM", None))
        self.button_1v1_EW.setText(QCoreApplication.translate("AnalyticsWindow", u"1v1 EW", None))
        self.button_team_RM.setText(QCoreApplication.translate("AnalyticsWindow", u"Team RM", None))
        self.button_team_EW.setText(QCoreApplication.translate("AnalyticsWindow", u"Team EW", None))
        self.pd_displ_rating_label.setText(QCoreApplication.translate("AnalyticsWindow", u"Rating", None))
        self.pd_rating_label.setText(QCoreApplication.translate("AnalyticsWindow", u"None", None))
        self.pd_displ_wins_label.setText(QCoreApplication.translate("AnalyticsWindow", u"Wins", None))
        self.pd_wins_label.setText(QCoreApplication.translate("AnalyticsWindow", u"None", None))
        self.pd_displ_losses_label.setText(QCoreApplication.translate("AnalyticsWindow", u"Losses", None))
        self.pd_losses_label.setText(QCoreApplication.translate("AnalyticsWindow", u"None", None))
        self.pd_displ_winperc_label.setText(QCoreApplication.translate("AnalyticsWindow", u"Win Percentage", None))
        self.pd_winperc_label.setText(QCoreApplication.translate("AnalyticsWindow", u"None", None))
        self.mh_tab_info_label.setText(QCoreApplication.translate("AnalyticsWindow", u"Load matches with clicking the button. Max 1000 matches at a time!", None))
        self.mh_tab_load_line_edit.setInputMask("")
        self.mh_tab_load_line_edit.setText("")
        self.mh_tab_load_line_edit.setPlaceholderText(QCoreApplication.translate("AnalyticsWindow", u"1000", None))
        self.mh_tab_load_more_button.setText(QCoreApplication.translate("AnalyticsWindow", u"Load More", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.match_history_tab), QCoreApplication.translate("AnalyticsWindow", u"Match History", None))
        self.rh_info_label.setText(QCoreApplication.translate("AnalyticsWindow", u"Load rating for all Leaderboards with clicking the button", None))
        self.rh_tab_load_more_button.setText(QCoreApplication.translate("AnalyticsWindow", u"Load", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.rating_history_tab), QCoreApplication.translate("AnalyticsWindow", u"Rating History", None))
    # retranslateUi

