import sys
import platform

from PyQt5.QtCore       import *
from PyQt5.QtGui        import *

import dotsDropCanvas   as dropCanvas
import dotsScrollPanel  as scrollPanel
import dotsSliderPanel  as sliderPanel
import dotsSideCar      as sideCar

from datetime       import datetime
from dotsShared     import common
from dotsDocks      import *

DotsW, DotsH = 1518, 810
 
### ----------------------- dotsQt -------------------------
''' dotsQt: parent container for the major widget panels, and
    buttons. See dotsShared.py for the common and paths dictionaries 
    shared across classes and files''' 
### --------------------------------------------------------
class DotsQt(QMainWindow):

    def __init__(self):
        super().__init__()

        self.sliderpanel = sliderPanel.SliderPanel(self)
        self.canvas = dropCanvas.DropCanvas(self)
      
        self.scene = self.canvas.scene
        self.view = self.canvas.view

        self.setCentralWidget(self.canvas)    
        self.scrollpanel = scrollPanel.ScrollPanel(self)

        ## from dotsDocks  
        addScrollDock(self)
        addSliderDock(self)
        addButtonDock(self)       

        self.setWindowTitle("DotsQt - " + getDate())
        self.move(getX(), 35)  # offset for app width and preferred height
        self.setStyleSheet(open('./dotsStyle.css').read())

        self.setFixedSize(DotsW,DotsH)
        self.canvas.initBkg.disableSliders()
  
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
     
        ## just in case the sprite directory is missing
        QTimer.singleShot(250, self.canvas.loadSprites)

        sideCar.setCursor()
        self.show()

        # from PyQt5.Qt import PYQT_VERSION_STR 
        # print("PyQt version:", PYQT_VERSION_STR) 
        # print("Python version:",platform.python_version())
     
### --------------------------------------------------------
def getDate():
    d = datetime.now()
    return d.strftime("%m-%d-%Y")

def getX():
    ctr = QDesktopWidget().availableGeometry().center()
    return int(((ctr.x() * 2 ) - DotsW)/2)
        
### --------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('QtCurve') 
    dots = DotsQt()
    sys.exit(app.exec_())

### ----------------------- dotsQt -------------------------

