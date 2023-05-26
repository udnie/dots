
from functools          import partial

from PyQt6.QtCore       import QTimer
from PyQt6.QtGui        import QGuiApplication
from PyQt6.QtWidgets    import QMenu

from datetime       import datetime
from dotsShared     import common
from dotsSideGig    import MsgBox, getCtr

MaxWidth = 1680  ##  position dock to screen bottom for max default display width
                 ##  on my mac with dock on left side, not on bottom
MaxScreens = ('1440','1536', '620')  ## requires 1920X1280 display size

### -------------------- dotsScreens -----------------------
''' classes: ScreenMenu and various screen formats and functions 
    used in the title bar '''
### -------------------------------------------------------- 
screens = {  ## the keys aren't shown
    '1080': '1080X720 -  3:2',
    '1280': '1280X720 - 16:9',
    '1215': '1215X810 -  3:2',
    '1440': '1440X810 - 16:9',
    '1296': '1296X864 -  3:2',
    '1536': '1536X864 - 16:9',
     '620': '620X1102 -  9:16',
}

### --------------------------------------------------------     
class ScreenMenu:  
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()  
   
        self.canvas = parent
        self.dots   = self.canvas.dots
        self.scene  = self.canvas.scene
        self.view   = self.canvas.view  
        
        self.screenMenu = None
                     
    def openScreenMenu(self):
        self.closeScreenMenu()
        self.screenMenu = QMenu(self.canvas)    
        self.screenMenu.addAction(' Screen Formats')
        self.screenMenu.addSeparator()
        for screen in screens.values():
            action = self.screenMenu.addAction(screen)
            self.screenMenu.addSeparator()
            action.triggered.connect(lambda chk, screen=screen: self.clicked(screen)) 
        self.screenMenu.move(getCtr(-85,-225)) 
        self.screenMenu.setFixedSize(150, 252)
        self.screenMenu.show()
    
    def clicked(self, screen):
        for key, value in screens.items():
            if value == screen:  ## singleshot needed for menu to clear
                QTimer.singleShot(200, partial(self.displayChk, self.switchKey(key)))
                break      
        self.closeScreenMenu()  
                    
    def closeScreenMenu(self):   
        if self.screenMenu:
            self.screenMenu.close()
        self.screenMenu = None
              
    def switchKey(self, key):                 
        if self.displayChk(key) == True:
            self.canvas.clear()       
            self.canvas.dots.switch(key) 
        else:
            return
    
    def displayChk(self, key):  ## switch screen format
        p = QGuiApplication.primaryScreen().availableGeometry()
        if key in MaxScreens and p.width() < MaxWidth:  ## current screen width < 1680
            self.exceedsMsg() 
            return False
        else:
            return True            
        
    def exceedsMsg(self):  ## in storyBoard on start       ## use getCtr with MsgBox
        MsgBox('Selected Format Exceeds Current Display Size', 8, getCtr(-200,-145)) 
     
### -------------------------------------------------------- 
def setCommon(format=''):
    if format == '1080':      ## 1080X720 - 3:2 same as default
        common.update(ten80)  
        common.update(seven20)  
        return screens['1080']  
    
    elif format == '1280':    ## 1280X720 - 16:9
        common.update(twelve80)  
        common.update(seven20) 
        return screens['1280']  
    
    elif format == '1215':     ## 1215X810 - 3:2
        common.update(twelve15) 
        common.update(eight10) 
        return screens['1215']
    
    elif format == '1440':     ## 1440X810 - 16:9
        common.update(fourteen40) 
        common.update(eight10) 
        return screens['1440'] 
    
    elif format == '1296':     ## 1296X864 - 3:2
        common.update(twelve96)  
        common.update(eight64) 
        return screens['1296']       
  
    elif format == '1536':      ## 1536X864 - 16:9
        common.update(fifteen36) 
        common.update(eight64) 
        return screens['1536']   
    
    elif format == '620':       ## 620X1100 - 9:16
        common.update(V620)              
        return screens['620'] 
     
    else:
        common.update(ten80)  ## 1080X720 - 3:2 - default
        common.update(seven20) 
        return '1080X720 - 3:2' 
   
### --------------- 1080X720 - 3:2 format ------------------
seven20 = {    
    'DotsH':     822, 
    'ViewH':     720,               
    'ScrollH':   687,  
    'SliderH':   679,  
    'margin1':    15,  ## keysMenu margins top
    'margin2':    10,  ## right
    'factor':   0.30,  ## amount to scale pixitems unless preset    
    'modLabel':  1.0,  ## amount to scale scroll label height 
    'scaleY':    1.0,  ## same as 720
    'steps':       6,  ## number of visible scroll widgets
}

ten80 = {            
    'Screen':   '1080',        ## used by both 1080 and 1280X720px 
    'DotsW':      1431,  
    'ViewW':      1080,  
    'gridSize':   30.0,       ## gridline spacing - seems to work, consistant
    'scaleX':      1.0,
    'widget':   (175,175),    ## position pix and shadow widgets using getCtr 
    'bkgrnd': (-525,-455),
    'runThis':  'demo-1080.play',  ## default run key
}

### ------------------ 1280X720 - 16:9 ---------------------
twelve80 = {  
    'Screen': '1280',        
    'DotsW':    1631, 
    'ViewW':    1280,  
    'gridSize':   26.66,  
    'scaleX':      1.15,
    'widget':    (75,175),
    'bkgrnd':  (-625,-455),
    'runThis':  'demo-1280.play',  ## default run key
}

### --------------- 810 - 16:9/3:2 format ------------------
eight10 = {
    'DotsH':     912, 
    'ViewH':     810,     
    'ScrollH':   772,
    'SliderH':   770,    
    'margin1':    20,
    'margin2':     3,
    'scaleY':      1.15, 
    'modLabel':    0.962,
    'factor':      0.36,  ## scales pixitems by format
    'steps':       7, 
}

### --------------- 1215X810 - 3:2 format -------------------
twelve15 = {
    'Screen': '1215',  
    'DotsW':    1567,   
    'ViewW':    1215,    
    'gridSize':   28.925, 
    'scaleX':      1.05,
    'widget':   (100,160),
    'bkgrnd':  (-595,-485),
    'runThis':  'demo-1215.play',  ## default run key
}
    
### ------------------ 1440X810 - 16:9 ----------------------
fourteen40 = {  
    'Screen': '1440',         
    'DotsW':    1791,
    'ViewW':    1440,
    'gridSize':   30, 
    'scaleX':      1.30,
    'widget':     (0,150),
    'bkgrnd':  (-705,-485),
    'runThis':  'demo-1440.play',  ## default run key
}

### --------------- 864 - 16:9/3:2 format ------------------
eight64 = {
    'DotsH':     966,     
    'ViewH':     864,  
    'ScrollH':   804,
    'SliderH':   798,    
    'margin1':    20,
    'margin2':     0,
    'scaleY':      1.15,
    'modLabel':    1.0,
    'factor':      0.36,  ## scales pixitems by format
    'steps':       7, 
}

### ------------------ 1264X864 - 3:2 ----------------------
twelve96 = {  
    'Screen':  '1296',  
    'DotsW':    1647,
    'ViewW':    1296,  
    'gridSize':   30, 
    'scaleX':      1.123,
    'widget':    (-5,100),
    'bkgrnd':  (-705,-530),
    'runThis':  'demo-1296.play',  ## default run key
}

### ------------------ 1536X864 - 16:9 ---------------------
fifteen36 = {      
    'Screen': '1536',   
    'DotsW':    1889, 
    'ViewW':    1536,      
    'gridSize':   32,  
    'scaleX':      1.40,
    'widget':   (-50,150),
    'bkgrnd':  (-750,-500),
    'runThis':  'demo-1536.play',  ## default run key
}

### -------------------- 620X1102 - 9:16 --------------------
V620 = {             ## 620 - must be a string not a number
    'Screen': '620',  
    'DotsW':    971,
    'DotsH':   1204, 
    'ViewW':    620,  
    'ViewH':   1102,     
    'ScrollH': 1022,
    'SliderH':  977,    
    'margin1':   15,
    'margin2':    0,
    'gridSize':  34.43, 
    'factor':     0.33, 
    'modLabel':   1.0,
    'scaleX':     0.5,
    'scaleY':     1.40,  
    'widget':  (405,75),
    'bkgrnd': (-305,-590),
    'steps':       9, 
    'runThis':  'demo-620.play',  ## default run key
}

### -----------------------------------------------------        
def getDate():  ## these 3 used by DotsQt.py - piggie-backing on screens
    d = datetime.now()
    return d.strftime('%m-%d-%Y')

def getX():  ## adjusted for app size and display
    ctr = QGuiApplication.primaryScreen().availableGeometry().center()
    return int(((ctr.x() * 2 ) - common['DotsW'])/2)

def getY():
    ctr = QGuiApplication.primaryScreen().availableGeometry().center()  
    return int((((ctr.y() * 2 ) - common['DotsH'])/2)*.65)  

### -------------------- dotsScreens -----------------------



