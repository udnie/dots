
import sys
import platform
import os

from PyQt6.QtCore     import QTimer
from PyQt6.QtWidgets  import QApplication, QStatusBar, QMainWindow

from dotsShared       import *
from dotsDocks        import getX, getY

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

        self.setCommon()  ## default - 1080X720

        self.setStyleSheet(open('./dotsStyle.css').read())   
        self.setFixedSize(common['DotsW'], common['DotsH'])
                
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar) 
           
        self.canvas = canvas.StoryBoard(self)
        self.setCentralWidget(self.canvas)  
        
        self.move(getX(), getY())
        ## can't all happen at once
        QTimer.singleShot(100, self.canvas.loadSprites)
        
        self.show()

        # print(platform.python_version())
               
    def setCommon(self, format=""):
        if format == '1280':
            common.update(twelve80)  
            common.update(seven20) 
        elif format == '854':
            common.update(eight54)  
        else:
            common.update(ten80)    
            common.update(seven20)    
                  
### --------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('QtCurve') 
    dots = DotsQt()
    sys.exit(app.exec())

### ------------------------- dotsQt ----------------------






