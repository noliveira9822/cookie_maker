import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon, QPixmap


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("MainWindow.ui", self)
        self.setWindowTitle("Manual Remote Control")
        self.setWindowIcon(QIcon("ipca.png"))
        #self.camera_image.setPixmap(QPixmap("black.png"))

        # signals & slots

        # show interface
        self.show()


if __name__ == "__main__":
    print('Loading user interface...')
    QApp = QtWidgets.QApplication(sys.argv)
    QApp.setStyle("Fusion")
    window = MainWindow()
    window.show()

    # creates global threads variables to be used through whole file
    videoThread = None
    thread1 = None
    print("All initialized")

    sys.exit(QApp.exec())