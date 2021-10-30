import sys
import platform
import os

from PyQt5.QtWidgets import QApplication, QStatusBar, QMainWindow

import dotsDropCanvas   as dropCanvas
import dotsScrollPanel  as scrollPanel
import dotsSliderPanel  as sliderPanel

from dotsSideCar    import setCursor
from dotsShared     import common
from dotsDocks      import *
 
### ----------------------- dotsQt -------------------------
''' dotsQt: parent container for the major widget panels, and
    buttons. See dotsShared.py for the common and paths dictionaries 
    shared across classes and files''' 
### --------------------------------------------------------
class DotsQt(QMainWindow):
### --------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__()

        ## the sliderpanel needs to be referenced before canvas
        self.sliderPanel = sliderPanel.SliderPanel(self)
        self.canvas = dropCanvas.DropCanvas(self)
      
        self.setCentralWidget(self.canvas)    
        self.scrollpanel = scrollPanel.ScrollPanel(self)

        ## add groups from dotsDocks  
        addScrollDock(self)
        addSliderDock(self)
        addButtonDock(self)       

        self.setWindowTitle("DotsQt - " + os.path.basename(os.getcwd()) + " - " + getDate())
  
        self.move(getX(), 35)  # offset for app width and preferred height
        self.setStyleSheet(open('./dotsStyle.css').read())

        self.setFixedSize(common['DotsW'], common['DotsH'])
        self.canvas.initBkg.disableBkgBtns()  ## toggles bkg sliders off as well
  
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        # self.statusBar.showMessage(os.getcwd(),4000)

        ## just in case the sprite directory is missing
        QTimer.singleShot(200, self.canvas.loadSprites)
        setCursor()  
        self.show()

        # from PyQt5.Qt import PYQT_VERSION_STR 
        # print("PyQt version:", PYQT_VERSION_STR) 
        # print("Python version:",platform.python_version())
             
### --------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('QtCurve') 
    dots = DotsQt()
    sys.exit(app.exec())

### ----------------------- dotsQt ----------------------





