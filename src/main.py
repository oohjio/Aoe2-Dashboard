#  Copyright (C)  2021 oohjio, https://github.com/oohjio
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License v3 as published by the Free Software Foundation.

import sys

from PySide2.QtWidgets import QApplication

from MainWindow import MainWindow

import qtmodern.styles
import qtmodern.windows

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()

    qtmodern.styles.dark(app)
    mw = qtmodern.windows.ModernWindow(window)
    mw.show()

    sys.exit(app.exec_())
