import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import dotsDropCanvas  as dropCanvas
import dotsScrollPanel as scrollPanel
import dotsSliderPanel as sliderPanel

from datetime import datetime

dotsW, dotsH = 1555, 850
# dotsW, dotsH = 1460, 820 

### ----------------------- dotsQt -------------------------
class Shared(): 
    ## set paths and global settings here - treat as static ##
    def __init__(self):
        super().__init__()
    
        self.factor = .35     
        self.gridSize = 32 

        self.viewW = 1056  ## canvas width
        self.viewH = 704   ## canvas height
   
        # self.viewW = 960  ## canvas width
        # self.viewH = 640   ## canvas height

        # self.snapShot = "./" 
        # self.bkgPath = "./backgrounds/" 
        # self.imagePath = "./images/"
        # self.spritePath = "./sprites/"

        self.snapShot = "/users/melt/Desktop/"    
        self.bkgPath = "/users/melt/python/qt5/wrks/backgrounds/"
        self.imagePath = "/users/melt/python/qt5/wrks/images/"
        self.spritePath = "/users/melt/python/qt5/wrks/sprites/"
            
### --------------------------------------------------------
class DotsQt(QWidget):
    ## the parent container
    def __init__(self):
        super().__init__()

        self.sliders = sliderPanel.SliderPanel(self)
        self.buttons = Buttons(self)

        self.canvas = dropCanvas.DropCanvas(
            self.sliders,
            self.buttons, 
            self)

        self.scene = self.canvas.scene
        self.view = self.canvas.view
            
        self.scrollpanel = scrollPanel.ScrollPanel(self)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.addMainGroup())
        mainLayout.addLayout(self.addButtonGroup())   
        self.setLayout(mainLayout)   

        self.setWindowTitle("DotsQt - " + getDate())
        self.move(getX() -0, 30)  # offset -> system tray on left   
        self.setStyleSheet(open('./dotsStyle.css').read())

        self.setFixedSize(dotsW,dotsH)
        self.canvas.disableSliders()

        setCursor()
        self.show()

    def enterEvent(self, e):
        self.view.setFocus()

### --------------------------------------------------------
    def addMainGroup(self):
        self.mainGroup = QGroupBox("")
        layout = QHBoxLayout()
        layout.addWidget(self.scrollpanel)

        ## uncomment for 640 height
        # vbox = QVBoxLayout()  
        # vbox.setSpacing(0)
        # vbox.setContentsMargins(0, 20, 0, 0) 
        # vbox.addWidget(self.canvas, Qt.AlignVCenter)    
        # layout.addLayout(vbox)
        ## uncomment for 640 height

        # comment this out for 640
        layout.addWidget(self.canvas, Qt.AlignVCenter)  
        # comment this out for 640

        layout.addWidget(self.sliders)
  
        self.mainGroup.setLayout(layout)
        
        return self.mainGroup

### --------------------------------------------------------  
    def addButtonGroup(self):   
        hbox = QHBoxLayout()  
          
        hbox.addWidget(self.buttons.addScrollBtnGroup())
        hbox.addStretch()
        hbox.addWidget(self.buttons.addBkgBtnGroup())
        hbox.addStretch()
        hbox.addWidget(self.buttons.addCanvasBtnGroup())

        return hbox
        
### --------------------------------------------------------
class Buttons(QWidget):   
    ## buttons container
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.setFixedSize(dotsW, 60) 
 
### --------------------------------------------------------
    def addScrollBtnGroup(self):  
        self.scrollGroup = QGroupBox("Scroll Panel")
        self.scrollGroup.setFixedWidth(550)

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
     
        btnAdd.clicked.connect(self.parent.scrollpanel.star)
        btnTop.clicked.connect(self.parent.scrollpanel.top)
        btnBottom.clicked.connect(self.parent.scrollpanel.bottom)
        btnClear.clicked.connect(self.parent.scrollpanel.clear)
        btnFiles.clicked.connect(self.parent.scrollpanel.scrollFiles)
        btnLoad.clicked.connect(self.parent.scrollpanel.loadSprites)
     
        self.scrollGroup.setLayout(layout)

        return self.scrollGroup

### -----------------------------------------------------
    def addBkgBtnGroup(self):
        self.backgroundGroup = QGroupBox("Background")
        self.backgroundGroup.setFixedWidth(300)

        btnBkgFiles = QPushButton("Files")
        self.btnSetBkg = QPushButton(" Set Background ")      
        self.btnSave = QPushButton("Save")

        layout = QHBoxLayout()    
  
        layout.addWidget(btnBkgFiles) 
        layout.addWidget(self.btnSetBkg) 
        layout.addWidget(self.btnSave) 

        btnBkgFiles.clicked.connect(self.parent.canvas.initBkg.bkgfiles)       
        self.btnSetBkg.clicked.connect(self.parent.canvas.initBkg.setBackground)
        self.btnSave.clicked.connect(self.parent.canvas.initBkg.saveBkg)

        self.backgroundGroup.setLayout(layout)

        return self.backgroundGroup

### -----------------------------------------------------
    def addCanvasBtnGroup(self):
        self.canvasGroup = QGroupBox("Canvas")
        self.canvasGroup.setFixedWidth(400) 

        btnClrCanvas = QPushButton("Clear")
        btnSnapShot = QPushButton("Shapshot")  
        btnPixTest = QPushButton("Pix Test")
        btnExit = QPushButton("Exit")

        layout = QHBoxLayout()    

        layout.addWidget(btnClrCanvas)  
        layout.addWidget(btnSnapShot)      
        layout.addWidget(btnPixTest)
        layout.addWidget(btnExit)
        
        btnClrCanvas.clicked.connect(self.parent.canvas.clear)        
        btnSnapShot.clicked.connect(self.parent.canvas.initBkg.snapShot)
        btnPixTest.clicked.connect(self.parent.canvas.pixTest)
        btnExit.clicked.connect(self.parent.close)

        self.canvasGroup.setLayout(layout)

        return self.canvasGroup

### --------------------------------------------------------
def getDate():
    d = datetime.now()
    return d.strftime("%m-%d-%Y")

def getX():
    ctr = QDesktopWidget().availableGeometry().center()
    return int(((ctr.x() * 2 ) - dotsW)/2)
        
def constrain(lastXY, objSize, panelSize, overlap):
    if lastXY + objSize > panelSize - overlap:
        return panelSize - (objSize + overlap)
    elif lastXY < overlap:
        return overlap
    else:
        return lastXY

def setCursor():
    cur = QCursor()
    cur.setPos(QDesktopWidget().availableGeometry().center())

### --------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    dot = DotsQt()
    sys.exit(app.exec_())

### ----------------------- dotsQt -------------------------