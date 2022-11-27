import os
import sys

from PyQt5.QtWidgets import QApplication

from main_admin_logic import MyMainWindow

if __name__ == '__main__':
    tasks = os.popen('tasklist').read()

    app = QApplication(sys.argv)
    w = MyMainWindow()
    w.show()
    sys.exit(app.exec_())