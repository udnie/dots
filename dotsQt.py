import sys

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

import dotsDropCanvas  as dropCanvas
import dotsScrollPanel as scrollPanel
import dotsSliderPanel as sliderPanel
import dotsSideCar     as sideCar

from datetime  import datetime

dotsW, dotsH = 1555, 850   

### ----------------------- dotsQt -------------------------
''' dotsQt: parent container for the major widget panels, 
    includes button class. See dotsShared.py for the common 
    and paths dictionaries shared across classes and files''' 
### --------------------------------------------------------
class DotsQt(QWidget):

    def __init__(self):
        super().__init__()

        self.buttons = Buttons(self)
        self.sliders = sliderPanel.SliderPanel()
    
        self.canvas = dropCanvas.DropCanvas(
            self.sliders,
            self.buttons, 
            self)

        self.scene = self.canvas.scene
        self.view = self.canvas.view

        self.resize(dotsW,dotsH)            
        self.scrollpanel = scrollPanel.ScrollPanel(self)
   
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.addMainGroup())
        mainLayout.addLayout(self.addButtonGroup())   
        self.setLayout(mainLayout)   

        self.setWindowTitle("DotsQt - " + getDate())
        self.move(getX(), 35)  # offset for app width and preferred height
        self.setStyleSheet(open('./dotsStyle.css').read())

        self.setFixedSize(dotsW,dotsH)
        self.canvas.disableSliders()
     
        ## just in case the sprite directory is missing
        QTimer.singleShot(250, self.canvas.loadSprites)

        sideCar.setCursor()
        self.show()

        # from PyQt5.Qt import PYQT_VERSION_STR 
        # print("PyQt version:", PYQT_VERSION_STR) 

### --------------------------------------------------------
    def addMainGroup(self):
        self.mainGroup = QGroupBox("")
        layout = QHBoxLayout()

        layout.addWidget(self.scrollpanel)
        layout.addWidget(self.canvas, Qt.AlignVCenter)  
        layout.addWidget(self.sliders)
  
        self.mainGroup.setLayout(layout)
        
        return self.mainGroup

### --------------------------------------------------------  
    def addButtonGroup(self):   
        hbox = QHBoxLayout()  ## added 'Btn' so there's no confusion
          
        hbox.addWidget(self.buttons.addScrollBtnGroup())
        hbox.addStretch(2) 
        hbox.addWidget(self.buttons.addPlayBtnGroup())
        hbox.addStretch(2) 
        hbox.addWidget(self.buttons.addBkgBtnGroup())
        hbox.addStretch(2) 
        hbox.addWidget(self.buttons.addCanvasBtnGroup())
 
        return hbox
        
### --------------------------------------------------------
class Buttons(QWidget):   
    ## buttons container
    def __init__(self, parent):
        super().__init__()

        self.dots = parent
        self.setFixedSize(dotsW, 60) 
 
### --------------------------------------------------------
    def addScrollBtnGroup(self):  
        self.scrollGroup = QGroupBox("Scroll Panel")
        self.scrollGroup.setFixedWidth(425)
        ## this sets the position of the title
        self.scrollGroup.setAlignment(Qt.AlignHCenter)

        self.scrollpanel = self.dots.scrollpanel

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
     
        btnAdd.clicked.connect(self.scrollpanel.star)
        btnTop.clicked.connect(self.scrollpanel.top)
        btnBottom.clicked.connect(self.scrollpanel.bottom)
        btnClear.clicked.connect(self.scrollpanel.clear)
        btnFiles.clicked.connect(self.scrollpanel.scrollFiles)
        btnLoad.clicked.connect(self.scrollpanel.loadSprites)
     
        self.scrollGroup.setLayout(layout)

        return self.scrollGroup

### -----------------------------------------------------
    def addPlayBtnGroup(self):
        self.playGroup = QGroupBox("Play")
        self.playGroup.setFixedWidth(350) 
        self.playGroup.setAlignment(Qt.AlignHCenter)

        self.sideShow = self.dots.canvas.sideShow

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

        btnLoad.clicked.connect(self.sideShow.loadPlay)
        btnSave.clicked.connect(self.sideShow.savePlay) 

        self.btnPlay.clicked.connect(self.sideShow.play)
        self.btnPause.clicked.connect(self.sideShow.pause)
        self.btnStop.clicked.connect(self.sideShow.stop)
    
        self.playGroup.setLayout(layout)

        return self.playGroup
        
### -----------------------------------------------------
    def addBkgBtnGroup(self):
        self.backgroundGroup = QGroupBox("Background")
        self.backgroundGroup.setFixedWidth(225)
        self.backgroundGroup.setAlignment(Qt.AlignHCenter)

        self.btnBkgFiles = QPushButton(" Add ")
        self.btnSetBkg = QPushButton(" Set ")      
        self.btnSave = QPushButton("Save")

        self.initBkg = self.dots.canvas.initBkg

        layout = QHBoxLayout()    
  
        layout.addWidget(self.btnBkgFiles) 
        layout.addWidget(self.btnSetBkg) 
        layout.addWidget(self.btnSave) 

        self.btnBkgFiles.clicked.connect(self.initBkg.bkgfiles)       
        self.btnSetBkg.clicked.connect(self.initBkg.setBkg)
        self.btnSave.clicked.connect(self.initBkg.saveBkg)

        self.backgroundGroup.setLayout(layout)

        return self.backgroundGroup

### -----------------------------------------------------
    def addCanvasBtnGroup(self):
        self.canvasGroup = QGroupBox("Canvas")
        self.canvasGroup.setFixedWidth(400) 
        self.canvasGroup.setAlignment(Qt.AlignHCenter)

        self.canvas = self.dots.canvas
        self.pathMaker = self.dots.canvas.pathMaker

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
        
        self.btnPathMaker.clicked.connect(self.pathMaker.setPathMaker)      
        btnClrCanvas.clicked.connect(self.canvas.clear)   
        btnSnapShot.clicked.connect(self.canvas.initBkg.snapShot)
        btnPixTest.clicked.connect(self.canvas.sideCar.pixTest)
        btnExit.clicked.connect(self.canvas.exit)

        self.canvasGroup.setLayout(layout)

        return self.canvasGroup

### --------------------------------------------------------
def getDate():
    d = datetime.now()
    return d.strftime("%m-%d-%Y")

def getX():
    ctr = QDesktopWidget().availableGeometry().center()
    return int(((ctr.x() * 2 ) - dotsW)/2)
        
### --------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    dot = DotsQt()
    sys.exit(app.exec_())

### ----------------------- dotsQt -------------------------

