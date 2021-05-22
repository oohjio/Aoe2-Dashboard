import sys
from PySide6.QtWidgets import QApplication
from MainWindow import MainWindow

app = QApplication(sys.argv)
window = MainWindow()

window.show()

window.update()

sys.exit(app.exec())
