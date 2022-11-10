
import sys
import platform
import os

from PyQt6.QtCore     import QTimer
from PyQt6.QtWidgets  import QApplication, QStatusBar, QMainWindow

from dotsShared       import common
from dotsDocks        import *

import dotsStoryBoard as canvas

### ----------------------- dotsQt -------------------------
''' dotsQt: parent container for the major widget panels, and
    buttons. See dotsShared.py for the common and paths dictionaries 
    shared across classes and files''' 
### --------------------------------------------------------
class DotsQt(QMainWindow):
### --------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__()

        self.canvas = canvas.StoryBoard(self)
        self.setCentralWidget(self.canvas)    

        self.setWindowTitle("DotsQt - " + os.path.basename(os.getcwd()) + " ~ " + getDate())
  
        self.move(getX(), 35)  # offset for app width and preferred height
        self.setStyleSheet(open('./dotsStyle.css').read())
      
        self.setFixedSize(common['DotsW'], common['DotsH'])
        self.canvas.bkgMaker.disableBkgBtns()  ## toggles bkg sliders off as well

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        ## can't all happen at once
        QTimer.singleShot(200, self.canvas.loadSprites)

        self.show()

      
        # print(platform.python_version())
            
### --------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('QtCurve') 
    dots = DotsQt()
    sys.exit(app.exec())

### ------------------------- dotsQt -----------------------




