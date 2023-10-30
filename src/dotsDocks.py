
from PyQt6.QtCore       import Qt
from PyQt6.QtWidgets    import QWidget, QDockWidget, QPushButton, \
                               QGroupBox, QHBoxLayout, QVBoxLayout, QLayout
                       
docks = {
    "fixedHgt":     82, 
    "scrollGrp":  350,  
    "playGrp":    345,
    "backGrp":    250,
    "canvasGrp":  355,
    "spacer":      10,  ## forces buttons closer together
}

newWidths = {     ## if vertical
    "scrollGrp":  270,  
    "playGrp":    270,
    "canvasGrp":  345,
}

### ---------------------- dotsDocks -----------------------
''' no classes: dockwidgets and buttons groups '''
### -------------------------------------------------------- 
def addButtonDock(self):  
    self.buttonDock = QDockWidget(self)
    self.dots.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.buttonDock)
    self.dockedWidget = QWidget(self)

    self.buttonDock.setTitleBarWidget(QWidget(self))
    self.buttonDock.setWidget(self.dockedWidget)
    
    self.dockedWidget.setLayout(QHBoxLayout())

    hbox = self.dockedWidget.layout() 
    hbox.addStretch(docks['spacer'])     
    hbox.addWidget(addScrollBtnGroup(self))
    hbox.addStretch(2) 
    hbox.addWidget(addPlayBtnGroup(self))
    hbox.addStretch(2) 
    if not self.dots.Vertical:
        hbox.addWidget(addBkgBtnGroup(self))
        hbox.addStretch(2) 
    hbox.addWidget(addCanvasBtnGroup(self))
    hbox.addStretch(docks['spacer']) 

    self.dockedWidget.setFixedHeight(docks['fixedHgt'])
    self.dockedWidget.setStyleSheet("border: 1px solid rgb(170,170,170)")
    self.dockedWidget.setContentsMargins(0,0,0,0) 
    
    return self.dockedWidget
    
### -------------------------------------------------------- 
def addScrollDock(self):
    self.scrollDock = QDockWidget(self)
    self.dots.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.scrollDock)
    self.dockedWidget = QWidget(self)

    self.scrollDock.setTitleBarWidget(QWidget(self))
    self.scrollDock.setWidget(self.dockedWidget)  

    layout = QVBoxLayout()      
    layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)  # fixed size - stopped movement
    self.dockedWidget.setLayout(layout)

    scrollDock = self.dockedWidget.layout() 
    scrollDock.addWidget(self.scroll)  ## comes from storyboard
    
    return scrollDock

### --------------------------------------------------------
def addKeysDock(self):
    self.keysDock = QDockWidget(self)
    self.dots.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.keysDock)
    self.dockedWidget = QWidget(self)

    self.keysDock.setTitleBarWidget(QWidget(self))
    self.keysDock.setWidget(self.dockedWidget)  

    layout = QVBoxLayout()      
    layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)  # fixed size - stopped movement
    self.dockedWidget.setLayout(layout)

    keysDock = self.dockedWidget.layout() 
    keysDock.addWidget(self.keysPanel)
    
    return keysDock

### --------------------------------------------------------  
def addScrollBtnGroup(self):  
    self.scrollGroup = QGroupBox("Scroll Panel")

    if not self.dots.Vertical:
        self.scrollGroup.setFixedWidth(docks['scrollGrp'])
    else:
        self.scrollGroup.setFixedWidth(newWidths['scrollGrp'])
    ## sets the position of the title
    self.scrollGroup.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    btnAdd = QPushButton("Star")
    btnTop = QPushButton("Top")
    btnBottom = QPushButton("Bottom")
    btnClear = QPushButton("Clear")
    btnLoad = QPushButton("Sprites")

    layout = QHBoxLayout()

    layout.addWidget(btnAdd)
    layout.addWidget(btnTop)
    layout.addWidget(btnBottom)
    layout.addWidget(btnClear)
    layout.addWidget(btnLoad)
    
    panel = self.scroll  ## make it easier to type

    btnAdd.clicked.connect(panel.Star)
    btnTop.clicked.connect(panel.top)
    btnBottom.clicked.connect(panel.bottom)
    btnClear.clicked.connect(panel.clear)
    btnLoad.clicked.connect(panel.loadSprites)
    
    self.scrollGroup.setLayout(layout)

    return  self.scrollGroup

### -----------------------------------------------------
def addPlayBtnGroup(self):
    self.playGroup = QGroupBox("Play")

    if not self.dots.Vertical:  ## nothing changes but the width
        self.playGroup.setFixedWidth(docks['playGrp'])
    else:
        self.playGroup.setFixedWidth(newWidths['playGrp'])
        
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
    showtime = self.showtime

    btnLoad.clicked.connect(sideShow.loadPlay)
    self.btnSave.clicked.connect(showtime.savePlay) 
    self.btnRun.clicked.connect(lambda: sideShow.keysInPlay('R'))
    self.btnPause.clicked.connect(showtime.pause)
    self.btnStop.clicked.connect(showtime.stop)

    self.playGroup.setLayout(layout)

    return self.playGroup
        
### -----------------------------------------------------
def addBkgBtnGroup(self):
    bkgGroup = QGroupBox("Background")  ## skipped if vertical

    bkgGroup.setFixedWidth(docks['backGrp'])
    bkgGroup.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    self.btnAddBkg  = QPushButton(" Add ")
    self.btnSetBkg  = QPushButton(" Set ")      
    self.btnBkgColor = QPushButton("Color")
    self.btnSaveBkg = QPushButton("Save")

    layout = QHBoxLayout()    

    layout.addWidget(self.btnAddBkg) 
    layout.addWidget(self.btnSetBkg) 
    layout.addWidget(self.btnBkgColor)
    layout.addWidget(self.btnSaveBkg) 

    bkg  = self.bkgMaker

    self.btnAddBkg.clicked.connect(bkg.openBkgFiles)       
    self.btnSetBkg.clicked.connect(bkg.setBkg)
    self.btnSaveBkg.clicked.connect(bkg.saveBkg)
    self.btnBkgColor.clicked.connect(bkg.bkgColor)

    bkgGroup.setLayout(layout)

    return bkgGroup

### -----------------------------------------------------
def addCanvasBtnGroup(self):
    self.canvasGroup = QGroupBox("Canvas")
    
    if not self.dots.Vertical:
        self.canvasGroup.setFixedWidth(docks['canvasGrp'])
    else:
        self.canvasGroup.setFixedWidth(newWidths['canvasGrp'])
     
    self.canvasGroup.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    if not self.dots.Vertical:
        btnClrCanvas = QPushButton("Clear")
        self.btnPathMaker = QPushButton("PathMaker")
        btnSnapShot = QPushButton("Shapshot")  
        btnPixTest = QPushButton("PixTest")
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
        
        self.canvasGroup.setLayout(layout)
    else:
        btnClrCanvas = QPushButton("Clear")  ## add background, remove pixtext   
        self.btnAddBkg  = QPushButton("BackGround")
        self.btnPathMaker = QPushButton("PathMaker")  
        btnSnapShot = QPushButton("Shapshot")  
        btnExit = QPushButton("Exit")

        layout = QHBoxLayout()    

        layout.addWidget(btnClrCanvas) 
        layout.addWidget(self.btnAddBkg) 
        layout.addWidget(self.btnPathMaker) 
        layout.addWidget(btnSnapShot)      
        layout.addWidget(btnExit)
        
        canvas = self
        pathMaker = self.pathMaker
        bkg = self.bkgMaker

        btnClrCanvas.clicked.connect(canvas.clear) 
        self.btnAddBkg.clicked.connect(bkg.openBkgFiles)
        self.btnPathMaker.clicked.connect(pathMaker.initPathMaker)        
        btnSnapShot.clicked.connect(canvas.sideCar.snapShot)
        btnExit.clicked.connect(canvas.exit)
        
        self.canvasGroup.setLayout(layout)

    return self.canvasGroup

### -------------------- dotsDocks ----------------------

