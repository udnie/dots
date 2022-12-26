
from PyQt6.QtCore       import Qt
from PyQt6.QtGui        import QGuiApplication 
from PyQt6.QtWidgets    import QWidget, QDockWidget, QPushButton, \
                               QGroupBox, QHBoxLayout, QVBoxLayout, QLayout
                       
from dotsShared     import common
from datetime       import datetime

docks = {
    "fixedHgt":     72, 
    "scrollGrp":  375,  
    "playGrp":    350,
    "backGrp":    275,
    "canvasGrp":  360,
}

### ---------------------- dotsDocks -----------------------
''' dotsDocks: dockwidgets and buttons groups '''
### --------------------------------------------------------
def addScrollDock(self):
    self.ldocked = QDockWidget(self)
    self.dots.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.ldocked)
    self.dockedWidget = QWidget(self)

    self.ldocked.setTitleBarWidget(QWidget(self))
    self.ldocked.setWidget(self.dockedWidget)  

    layout = QVBoxLayout()      
    layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)  # fixed size - stopped movement
    self.dockedWidget.setLayout(layout)

    vbox = self.dockedWidget.layout() 
    vbox.addWidget(self.scroll)  ## comes from storyboard
    
    return vbox

### --------------------------------------------------------
def addSliderDock(self):
    self.rdocked = QDockWidget(self)
    self.dots.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.rdocked)
    self.dockedWidget = QWidget(self)

    self.rdocked.setTitleBarWidget(QWidget(self))
    self.rdocked.setWidget(self.dockedWidget)  

    layout = QVBoxLayout()      
    layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)  # fixed size - stopped movement
    self.dockedWidget.setLayout(layout)

    vbox = self.dockedWidget.layout() 
    vbox.addWidget(self.slider)
    
    return vbox

### --------------------------------------------------------  
def addButtonDock(self):  
    self.bdocked = QDockWidget(self)
    self.dots.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.bdocked)
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

    self.dockedWidget.setFixedHeight(docks['fixedHgt'])
    self.dockedWidget.setStyleSheet("border: 1px solid rgb(135,135,135)")
    self.dockedWidget.setContentsMargins(0,0,0,0) 
        
### --------------------------------------------------------
def addScrollBtnGroup(self):  
    self.scrollGroup = QGroupBox("Scroll Panel")

    self.scrollGroup.setFixedWidth(docks['scrollGrp'])
    ## this sets the position of the title
    self.scrollGroup.setAlignment(Qt.AlignmentFlag.AlignHCenter)

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
    
    panel = self.scroll

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

    self.playGroup.setFixedWidth(docks['playGrp']) 
    self.playGroup.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    btnLoad  = QPushButton("Load")
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

    sideShow = self.sideShow

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

    bkgGroup.setFixedWidth(docks['backGrp'])
    bkgGroup.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    self.btnAddBkg  = QPushButton(" Add ")
    self.btnSetBkg  = QPushButton(" Set ")      
    self.btnSaveBkg = QPushButton("Save")
    self.btnBkgColor = QPushButton("Color")

    layout = QHBoxLayout()    

    layout.addWidget(self.btnAddBkg) 
    layout.addWidget(self.btnSetBkg) 
    layout.addWidget(self.btnSaveBkg) 
    layout.addWidget(self.btnBkgColor)

    bkg = self.bkgMaker

    self.btnAddBkg.clicked.connect(bkg.openBkgFiles)       
    self.btnSetBkg.clicked.connect(bkg.setBkg)
    self.btnSaveBkg.clicked.connect(bkg.saveBkg)
    self.btnBkgColor.clicked.connect(bkg.bkgColor)

    bkgGroup.setLayout(layout)

    return bkgGroup

### -----------------------------------------------------
def addCanvasBtnGroup(self):
    canvasGroup = QGroupBox("Canvas")
    canvasGroup.setFixedWidth(docks["canvasGrp"]) 
    canvasGroup.setAlignment(Qt.AlignmentFlag.AlignHCenter)

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
    
    canvas = self
    pathMaker = self.pathMaker

    self.btnPathMaker.clicked.connect(pathMaker.initPathMaker)      
    btnClrCanvas.clicked.connect(canvas.clear)   
    btnSnapShot.clicked.connect(canvas.sideCar.snapShot)
    btnPixTest.clicked.connect(canvas.sideCar.pixTest)
    btnExit.clicked.connect(canvas.exit)

    canvasGroup.setLayout(layout)

    return canvasGroup

### -----------------------------------------------------
def getDate():
    d = datetime.now()
    return d.strftime("%m-%d-%Y")

def getX():
    ctr = QGuiApplication.primaryScreen().availableGeometry().center()
    return int(((ctr.x() * 2 ) - common['DotsW'])/2)

def getY():
    ctr = QGuiApplication.primaryScreen().availableGeometry().center()  
    return int((((ctr.y() * 2 ) - common['DotsH'])/2)*.65)  

### -------------------- dotsDocks ----------------------

