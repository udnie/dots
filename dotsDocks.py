from PyQt5.QtCore        import Qt, QTimer
from PyQt5.QtWidgets     import QWidget, QDockWidget, QPushButton, \
                                QGroupBox, QHBoxLayout, QVBoxLayout, \
                                QDesktopWidget
 
from dotsShared     import common
from datetime       import datetime

### ---------------------- dotsDocks -----------------------
''' dotsDocks: dockwidgets and buttons groups '''
### --------------------------------------------------------
def addScrollDock(self):
    self.ldocked = QDockWidget(None, self)
    self.addDockWidget(Qt.LeftDockWidgetArea, self.ldocked)
    self.dockedWidget = QWidget(self)

    self.ldocked.setTitleBarWidget(QWidget(self))
    self.ldocked.setWidget(self.dockedWidget)  

    layout = QVBoxLayout()      
    layout.setSizeConstraint(3)  # fixed size - stopped movement
    self.dockedWidget.setLayout(layout)

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

    layout = QVBoxLayout()      
    layout.setSizeConstraint(3)  # fixed size - stopped movement
    self.dockedWidget.setLayout(layout)

    vbox = self.dockedWidget.layout() 
    vbox.addWidget(self.sliderPanel)
    
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
    hbox.addWidget(addScrollBtnGroup(self))
    hbox.addStretch(2) 
    hbox.addWidget(addPlayBtnGroup(self))
    hbox.addStretch(2) 
    hbox.addWidget(addBkgBtnGroup(self))
    hbox.addStretch(2) 
    hbox.addWidget(addCanvasBtnGroup(self))

    return hbox

### --------------------------------------------------------
def addScrollBtnGroup(self):  
    self.scrollGroup = QGroupBox("Scroll Panel")

    self.scrollGroup.setFixedWidth(400)
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
    
    panel = self.scrollpanel

    btnAdd.clicked.connect(panel.Star)
    btnTop.clicked.connect(panel.top)
    btnBottom.clicked.connect(panel.bottom)
    btnClear.clicked.connect(panel.clear)
    btnFiles.clicked.connect(panel.scrollFiles)
    btnLoad.clicked.connect(panel.loadSprites)
    
    self.scrollGroup.setLayout(layout)

    return  self.scrollGroup

### -----------------------------------------------------
def addPlayBtnGroup(self):
    self.playGroup = QGroupBox("Play")

    self.playGroup.setFixedWidth(325) 
    self.playGroup.setAlignment(Qt.AlignHCenter)

    btnLoad = QPushButton("Load")
    self.btnRun = QPushButton("Run")  
    self.btnPause = QPushButton("Pause")
    self.btnStop = QPushButton("Stop")
    self.btnSave = QPushButton("Save")

    layout = QHBoxLayout()    

    layout.addWidget(btnLoad)  
    layout.addWidget(self.btnRun)      
    layout.addWidget(self.btnPause)
    layout.addWidget(self.btnStop)
    layout.addWidget(self.btnSave)

    sideShow = self.canvas.sideShow

    btnLoad.clicked.connect(sideShow.loadPlay)
    self.btnSave.clicked.connect(sideShow.savePlay) 
    self.btnRun.clicked.connect(lambda: sideShow.keysInPlay('R'))
    self.btnPause.clicked.connect(sideShow.pause)
    self.btnStop.clicked.connect(sideShow.stop)

    self.playGroup.setLayout(layout)

    return self.playGroup
        
### -----------------------------------------------------
def addBkgBtnGroup(self):
    bkgGroup = QGroupBox("Background")

    bkgGroup.setFixedWidth(275)
    bkgGroup.setAlignment(Qt.AlignHCenter)

    self.btnAddBkg  = QPushButton(" Add ")
    self.btnSetBkg  = QPushButton(" Set ")      
    self.btnSaveBkg = QPushButton("Save")
    self.btnBkgColor = QPushButton("Color")

    layout = QHBoxLayout()    

    layout.addWidget(self.btnAddBkg) 
    layout.addWidget(self.btnSetBkg) 
    layout.addWidget(self.btnSaveBkg) 
    layout.addWidget(self.btnBkgColor)

    bkg = self.canvas.initBkg

    self.btnAddBkg.clicked.connect(bkg.openBkgFiles)       
    self.btnSetBkg.clicked.connect(bkg.setBkg)
    self.btnSaveBkg.clicked.connect(bkg.saveBkg)
    self.btnBkgColor.clicked.connect(bkg.bkgColor)

    bkgGroup.setLayout(layout)

    return bkgGroup

### -----------------------------------------------------
def addCanvasBtnGroup(self):
    canvasGroup = QGroupBox("Canvas")
    canvasGroup.setFixedWidth(375) 
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

    self.btnPathMaker.clicked.connect(pathMaker.initPathMaker)      
    btnClrCanvas.clicked.connect(canvas.clear)   
    btnSnapShot.clicked.connect(canvas.initBkg.snapShot)
    btnPixTest.clicked.connect(canvas.sideCar.pixTest)
    btnExit.clicked.connect(canvas.exit)

    canvasGroup.setLayout(layout)

    return canvasGroup

### -----------------------------------------------------
def getDate():
    d = datetime.now()
    return d.strftime("%m-%d-%Y")

def getX():
    ctr = QDesktopWidget().availableGeometry().center()
    return int(((ctr.x() * 2 ) - common['DotsW'])/2)

### -------------------- dotsDocks ----------------------

