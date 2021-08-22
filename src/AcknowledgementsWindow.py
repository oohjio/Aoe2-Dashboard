from PySide2.QtGui import QCloseEvent
from PySide2.QtWidgets import QWidget

from ui.ui_acknowledgements_window import Ui_AcknowledgementsWindow


class AcknowledgementsWindow(QWidget, Ui_AcknowledgementsWindow):

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        self.setupUi(self)
        self.setMaximumSize(self.size())
        self.setMinimumSize(self.size())

        self.textBrowser.setOpenExternalLinks(True)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.main_window.active_window_closed(self)