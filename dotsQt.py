
import sys
import platform
import os

from PyQt6.QtCore     import QTimer
from PyQt6.QtWidgets  import QApplication, QStatusBar, QMainWindow

from dotsShared       import common
from dotsDocks        import *

import dotsDropCanvas as canvas

### ----------------------- dotsQt -------------------------
''' dotsQt: parent container for the major widget panels, and
    buttons. See dotsShared.py for the common and paths dictionaries 
    shared across classes and files''' 
### --------------------------------------------------------
class DotsQt(QMainWindow):
### --------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__()

        self.canvas = canvas.DropCanvas(self)
        self.setCentralWidget(self.canvas)    

        self.setWindowTitle("DotsQt - " + os.path.basename(os.getcwd()) + " ~ " + getDate())
  
        self.move(getX(), 35)  # offset for app width and preferred height
        self.setStyleSheet(open('./dotsStyle.css').read())
      
        self.setFixedSize(common['DotsW'], common['DotsH'])
        self.canvas.initBkg.disableBkgBtns()  ## toggles bkg sliders off as well

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        ## just in case the sprite directory is missing
        QTimer.singleShot(200, self.canvas.loadSprites)

        self.show()

        from PyQt6.QtCore import QT_VERSION_STR
        from PyQt6.QtCore import PYQT_VERSION_STR

        # print( PySide6.__version__ )
        # print("PyQt version:", PYQT_VERSION_STR) 
        # print("Python version:", QT_VERSION_STR)
        # print(platform.python_version())
            
### --------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('QtCurve') 
    dots = DotsQt()
    sys.exit(app.exec())

### ------------------------- dotsQt -----------------------


