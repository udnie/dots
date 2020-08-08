import sys

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

import dotsDropCanvas  as dropCanvas
import dotsScrollPanel as scrollPanel
import dotsSliderPanel as sliderPanel
import dotsSideCar     as sidecar

from datetime  import datetime

dotsW, dotsH = 1555, 850
# dotsW, dotsH = 1460, 820 

### ----------------------- dotsQt -------------------------
class Shared(): 
    ## set paths and global settings here - treat as static ##
    def __init__(self):
        super().__init__()
    
        self.factor = .40     
        self.gridSize = 32 
        self.gridZ = -33.0

        self.viewW = 1056  ## canvas width
        self.viewH = 704   ## canvas height
   
        # self.viewW = 960  ## canvas width
        # self.viewH = 640   ## canvas height

        self.snapShot = "./" 
        self.bkgPath = "./backgrounds/" 
        self.imagePath = "./images/"
        self.playPath = "./plays/"
        self.spritePath = "./sprites/"
            
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
        self.move(getX(), 35)  # offset for app width and preferred height
        self.setStyleSheet(open('./dotsStyle.css').read())

        self.setFixedSize(dotsW,dotsH)
        self.canvas.disableSliders()        

        ## wait till the app shows then load sprites 
        QTimer.singleShot(500, self.scrollpanel.loadSprites)

        sidecar.setCursor()
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

        ## comment this out for 640
        layout.addWidget(self.canvas, Qt.AlignVCenter)  
        ## comment this out for 640

        layout.addWidget(self.sliders)
  
        self.mainGroup.setLayout(layout)
        
        return self.mainGroup

### --------------------------------------------------------  
    def addButtonGroup(self):   
        hbox = QHBoxLayout()  ## added 'Btn' so there's no confusion
          
        hbox.addWidget(self.buttons.addScrollBtnGroup())
        hbox.addStretch()
        hbox.addWidget(self.buttons.addPlayBtnGroup())
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
        self.scrollGroup.setFixedWidth(525)
        ## this sets the position of the title
        self.scrollGroup.setAlignment(Qt.AlignHCenter)

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
    def addPlayBtnGroup(self):
        self.playGroup = QGroupBox("Play")
        self.playGroup.setFixedWidth(200) 
        self.playGroup.setAlignment(Qt.AlignHCenter)

        btnLoad = QPushButton("Load")
        btnSave = QPushButton("Save")

        layout = QHBoxLayout()    

        layout.addWidget(btnLoad)  
        layout.addWidget(btnSave)

        btnLoad.clicked.connect(self.parent.canvas.sideCar.loadPlay)
        btnSave.clicked.connect(self.parent.canvas.sideCar.savePlay)

        self.playGroup.setLayout(layout)

        return self.playGroup
        
### -----------------------------------------------------
    def addBkgBtnGroup(self):
        self.backgroundGroup = QGroupBox("Background")
        self.backgroundGroup.setFixedWidth(275)
        self.backgroundGroup.setAlignment(Qt.AlignHCenter)

        self.btnBkgFiles = QPushButton(" Add ")
        self.btnSetBkg = QPushButton(" Set ")      
        self.btnSave = QPushButton("Save")

        layout = QHBoxLayout()    
  
        layout.addWidget(self.btnBkgFiles) 
        layout.addWidget(self.btnSetBkg) 
        layout.addWidget(self.btnSave) 

        self.btnBkgFiles.clicked.connect(self.parent.canvas.initBkg.bkgfiles)       
        self.btnSetBkg.clicked.connect(self.parent.canvas.initBkg.setBkg)
        self.btnSave.clicked.connect(self.parent.canvas.initBkg.saveBkg)

        self.backgroundGroup.setLayout(layout)

        return self.backgroundGroup

### -----------------------------------------------------
    def addCanvasBtnGroup(self):
        self.canvasGroup = QGroupBox("Canvas")
        self.canvasGroup.setFixedWidth(375) 
        self.canvasGroup.setAlignment(Qt.AlignHCenter)

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
        btnPixTest.clicked.connect(self.parent.canvas.sideCar.pixTest)
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
        
### --------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    dot = DotsQt()
    sys.exit(app.exec_())

### ----------------------- dotsQt -------------------------