import sys
from PyQt5.QtWidgets import QApplication
from system import SCADA_System

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SCADA_System()
    window.show()
    sys.exit(app.exec_())