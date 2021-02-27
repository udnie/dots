import sys
import platform

from PyQt5.QtCore       import *
from PyQt5.QtGui        import *
from PyQt5.QtWidgets    import *

import dotsDropCanvas   as dropCanvas
import dotsScrollPanel  as scrollPanel
import dotsSliderPanel  as sliderPanel
import dotsSideCar      as sideCar

from datetime       import datetime
from dotsShared     import common

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

        self.addScrollDock()
        self.addSliderDock()
        self.addButtonDock()         

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
    def addScrollDock(self):
        self.ldocked = QDockWidget(None, self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.ldocked)
        self.dockedWidget = QWidget(self)

        self.ldocked.setTitleBarWidget(QWidget(self))
        self.ldocked.setWidget(self.dockedWidget)  
        self.dockedWidget.setLayout(QVBoxLayout())
       
        vbox = self.dockedWidget.layout() 
        vbox.addWidget(self.scrollpanel)
        
        return vbox

### --------------------------------------------------------
    def addSliderDock(self):
        self.rdocked = QDockWidget(None, self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.rdocked)
        self.dockedWidget = QWidget(self)

        self.rdocked.setTitleBarWidget(QWidget(self))
        self.rdocked.setWidget(self.dockedWidget)  
        self.dockedWidget.setLayout(QVBoxLayout())
       
        vbox = self.dockedWidget.layout() 
        vbox.addWidget(self.sliderpanel)
        
        return vbox

### --------------------------------------------------------  
    def addButtonDock(self):  
        self.bdocked = QDockWidget(None, self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bdocked)
        self.dockedWidget = QWidget(self)

        self.bdocked.setTitleBarWidget(QWidget(self))
        self.bdocked.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(QHBoxLayout())
       
        hbox = self.dockedWidget.layout()          
        hbox.addWidget(self.addScrollBtnGroup())
        hbox.addStretch(2) 
        hbox.addWidget(self.addPlayBtnGroup())
        hbox.addStretch(2) 
        hbox.addWidget(self.addBkgBtnGroup())
        hbox.addStretch(2) 
        hbox.addWidget(self.addCanvasBtnGroup())
 
        return hbox

### --------------------------------------------------------
    def addScrollBtnGroup(self):  
        groupBox = QGroupBox("Scroll Panel")

        groupBox.setFixedWidth(425)
        ## this sets the position of the title
        groupBox.setAlignment(Qt.AlignHCenter)

        btnAdd = QPushButton("Star")
        btnTop = QPushButton("Top")
        btnBottom = QPushButton("Bottom")
        btnClear = QPushButton("Clear")
        btnFiles = QPushButton("Files")
        btnLoad = QPushButton("Sprites")
 
        layout = QHBoxLayout()

        layout.addWidget(btnAdd)
        layout.addWidget(btnTop)
        layout.addWidget(btnBottom)
        layout.addWidget(btnClear)
        layout.addWidget(btnFiles)
        layout.addWidget(btnLoad)
     
        panel = self.scrollpanel

        btnAdd.clicked.connect(panel.Star)
        btnTop.clicked.connect(panel.top)
        btnBottom.clicked.connect(panel.bottom)
        btnClear.clicked.connect(panel.clear)
        btnFiles.clicked.connect(panel.scrollFiles)
        btnLoad.clicked.connect(panel.loadSprites)
     
        groupBox.setLayout(layout)

        return groupBox

### -----------------------------------------------------
    def addPlayBtnGroup(self):
        playGroup = QGroupBox("Play")

        playGroup.setFixedWidth(350) 
        playGroup.setAlignment(Qt.AlignHCenter)

        btnLoad = QPushButton("Load")
        self.btnPlay = QPushButton("Play")  
        self.btnPause = QPushButton("Pause")
        self.btnStop = QPushButton("Stop")
        btnSave = QPushButton("Save")

        layout = QHBoxLayout()    

        layout.addWidget(btnLoad)  
        layout.addWidget(self.btnPlay)      
        layout.addWidget(self.btnPause)
        layout.addWidget(self.btnStop)
        layout.addWidget(btnSave)

        sideShow = self.canvas.sideShow

        btnLoad.clicked.connect(sideShow.loadPlay)
        btnSave.clicked.connect(sideShow.savePlay) 

        self.btnPlay.clicked.connect(sideShow.play)
        self.btnPause.clicked.connect(sideShow.pause)
        self.btnStop.clicked.connect(sideShow.stop)
    
        playGroup.setLayout(layout)

        return playGroup
        
### -----------------------------------------------------
    def addBkgBtnGroup(self):
        bkgGroup = QGroupBox("Background")
        bkgGroup.setFixedWidth(225)
        bkgGroup.setAlignment(Qt.AlignHCenter)

        self.btnBkgFiles = QPushButton(" Add ")
        self.btnSetBkg = QPushButton(" Set ")      
        self.btnSave = QPushButton("Save")

        layout = QHBoxLayout()    
  
        layout.addWidget(self.btnBkgFiles) 
        layout.addWidget(self.btnSetBkg) 
        layout.addWidget(self.btnSave) 

        bkg = self.canvas.initBkg

        self.btnBkgFiles.clicked.connect(bkg.bkgfiles)       
        self.btnSetBkg.clicked.connect(bkg.setBkg)
        self.btnSave.clicked.connect(bkg.saveBkg)

        bkgGroup.setLayout(layout)

        return bkgGroup

### -----------------------------------------------------
    def addCanvasBtnGroup(self):
        canvasGroup = QGroupBox("Canvas")
        canvasGroup.setFixedWidth(400) 
        canvasGroup.setAlignment(Qt.AlignHCenter)
  
        btnClrCanvas = QPushButton("Clear")
        self.btnPathMaker = QPushButton("Path Maker")
        btnSnapShot = QPushButton("Shapshot")  
        btnPixTest = QPushButton("Pix Test")
        btnExit = QPushButton("Exit")

        layout = QHBoxLayout()    

        layout.addWidget(btnClrCanvas) 
        layout.addWidget(self.btnPathMaker)  
        layout.addWidget(btnSnapShot)      
        layout.addWidget(btnPixTest)
        layout.addWidget(btnExit)
        
        canvas = self.canvas
        pathMaker = self.canvas.pathMaker

        self.btnPathMaker.clicked.connect(pathMaker.setPathMaker)      
        btnClrCanvas.clicked.connect(canvas.clear)   
        btnSnapShot.clicked.connect(canvas.initBkg.snapShot)
        btnPixTest.clicked.connect(canvas.sideCar.pixTest)
        btnExit.clicked.connect(canvas.exit)

        canvasGroup.setLayout(layout)

        return canvasGroup

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

