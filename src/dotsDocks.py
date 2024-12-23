
from PyQt6.QtCore       import Qt
from PyQt6.QtWidgets    import QWidget, QDockWidget, QPushButton, \
                               QGroupBox, QHBoxLayout, QVBoxLayout, QLayout
                  
from dotsShared         import common 
   
docks = {
    "fixedHgt":     82, 
    "scrollGrp":  320,  
    "playGrp":    320,
    "backGrp":    195,
    "canvasGrp":  325,
    "spacer":      10,  ## forces buttons closer together
}

newWidths = {     ## if vertical 1102, 912, 1024
    "fixedHgt":     70, 
    "scrollGrp":  200,  
    "playGrp":    350,
    "canvasGrp":  300,
    "spacer":      7,  ## forces buttons closer together
}

vert900 = {   ## vertical 900
    "fixedHgt":     70, 
    "scrollGrp":   85,  
    "playGrp":    175,
    "canvasGrp":  275,
    "spacer":       5,  ## forces buttons closer together       
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
    keysDock.addWidget(self.canvas.keysPanel)
    
    return keysDock

### --------------------------------------------------------  
def addScrollBtnGroup(self):  
    self.scrollGroup = QGroupBox("Scroll Panel")
    
    self.scrollGroup.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    self.scrollGroup.setFixedWidth(docks['scrollGrp']) 

    if self.dots.Vertical == False:  ## set in dotsQt    
        btnTop = QPushButton("Top")
        btnBottom = QPushButton("Bottom")
        btnClear = QPushButton("Clear")
        btnLoad = QPushButton("Sprites")
        btnStar = QPushButton("Star")

        layout = QHBoxLayout()
            
        layout.addWidget(btnTop)
        layout.addWidget(btnBottom)
        layout.addWidget(btnClear)
        layout.addWidget(btnLoad)
        layout.addWidget(btnStar)
        
        panel = self.scroll  ## make it easier to type
            
        btnTop.clicked.connect(panel.top)
        btnBottom.clicked.connect(panel.bottom)
        btnClear.clicked.connect(panel.clear)
        btnLoad.clicked.connect(panel.loadSprites)
        btnStar.clicked.connect(panel.Star)
    
        self.scrollGroup.setLayout(layout)
    else:
        if common['Screen'] != '912': 
            self.scrollGroup.setFixedWidth(newWidths['scrollGrp'])  ## 1024,1102 ... 
        else:
            self.scrollGroup.setFixedWidth(vert900['scrollGrp']) 
 
        btnTop = QPushButton("Top")
        btnBottom = QPushButton("Bottom")
        btnStar = QPushButton("Star")

        layout = QHBoxLayout()
            
        layout.addWidget(btnTop)
        layout.addWidget(btnBottom)
        layout.addWidget(btnStar)
        
        panel = self.scroll  ## make it easier to type
            
        btnTop.clicked.connect(panel.top)
        btnBottom.clicked.connect(panel.bottom)
        btnStar.clicked.connect(panel.Star)
    
        self.scrollGroup.setLayout(layout)
 
    return  self.scrollGroup

### -----------------------------------------------------
def addPlayBtnGroup(self):
    self.playGroup = QGroupBox("Play")
    self.playGroup.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    if not self.dots.Vertical:  ## nothing changes but the width
        self.playGroup.setFixedWidth(docks['playGrp'])
    elif common['Screen'] != '912':
        self.playGroup.setFixedWidth(newWidths['playGrp'])
    else:
        self.scrollGroup.setFixedWidth(vert900['playGrp']) 
               
    btnLoad  = QPushButton("Load")
    self.btnRun = QPushButton("Run")  
    self.btnPause = QPushButton("Pause")
    self.btnStop = QPushButton("Stop")
    self.btnSave = QPushButton("Save")
    self.btnHelp = QPushButton("Help") 

    layout = QHBoxLayout()    

    layout.addWidget(btnLoad)  
    layout.addWidget(self.btnRun)      
    layout.addWidget(self.btnPause)
    layout.addWidget(self.btnStop)
    layout.addWidget(self.btnSave)
    layout.addWidget(self.btnHelp)

    showbiz  = self.canvas.showbiz
    showtime = self.showbiz.showtime
    helpBtn  = self.helpButton
  
    btnLoad.clicked.connect(showbiz.showRunner.loadPlay)
    self.btnRun.clicked.connect(lambda: self.canvas.setKeys('R'))
    self.btnPause.clicked.connect(showtime.pause)
    self.btnStop.clicked.connect(showtime.stop)
    self.btnSave.clicked.connect(showtime.savePlay) 
    self.btnHelp.clicked.connect(helpBtn.openMenus) 
  
    self.playGroup.setLayout(layout)

    return self.playGroup
                   
### -----------------------------------------------------
def addBkgBtnGroup(self):
    bkgGroup = QGroupBox("Background")  ## skipped if vertical

    bkgGroup.setFixedWidth(docks['backGrp'])
    bkgGroup.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    self.btnAddBkg    = QPushButton(" Add ")    
    self.btnBkgColor  = QPushButton("Color")
    self.btnSaveFlat = QPushButton("Save")

    layout = QHBoxLayout()    

    layout.addWidget(self.btnAddBkg) 
    layout.addWidget(self.btnBkgColor)
    layout.addWidget(self.btnSaveFlat) 

    bkg  = self.bkgMaker

    self.btnAddBkg.clicked.connect(bkg.openBkgFiles)       
    self.btnSaveFlat.clicked.connect(bkg.saveFlat)
    self.btnBkgColor.clicked.connect(bkg.bkgColor)

    bkgGroup.setLayout(layout)

    return bkgGroup

### -----------------------------------------------------
def addCanvasBtnGroup(self):
    self.canvasGroup = QGroupBox("Canvas")
        
    self.canvasGroup.setFixedWidth(docks['canvasGrp'])     
    self.canvasGroup.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    
    canvas = self
    bkg = self.bkgMaker
    pathMaker = self.pathMaker

    if self.dots.Vertical == False:
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
  
        self.btnPathMaker.clicked.connect(pathMaker.initPathMaker)      
        btnClrCanvas.clicked.connect(canvas.clear)   
        btnSnapShot.clicked.connect(lambda: self.canvas.sideCar2.snapShot(pathMaker))
        btnPixTest.clicked.connect(canvas.sideCar.pixTest)
        btnExit.clicked.connect(canvas.exit)
        
        self.canvasGroup.setLayout(layout)         
    else:
        if common['Screen'] != '912' and common['Screen'] != '1024':
            self.canvasGroup.setFixedWidth(newWidths['canvasGrp'])
        else:
            self.canvasGroup.setFixedWidth(vert900['canvasGrp'])
        
        btnClrCanvas = QPushButton("Clear")  ## add background, remove pixtext   
        self.btnAddBkg  = QPushButton("BackGround")
        self.btnPathMaker = QPushButton("PathMaker") 
        btnExit = QPushButton("Exit")
         
        layout = QHBoxLayout()  
    
        layout.addWidget(btnClrCanvas) 
        layout.addWidget(self.btnAddBkg) 
        layout.addWidget(self.btnPathMaker) 
        layout.addWidget(btnExit)
        
        btnClrCanvas.clicked.connect(self.clear) 
        self.btnAddBkg.clicked.connect(bkg.openBkgFiles)
        self.btnPathMaker.clicked.connect(pathMaker.initPathMaker)        
        btnExit.clicked.connect(self.exit)
        
        self.canvasGroup.setLayout(layout)

    return self.canvasGroup

### -------------------- dotsDocks ----------------------

