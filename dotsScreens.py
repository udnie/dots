
from PyQt6.QtCore   import QPoint
from PyQt6.QtGui    import QGuiApplication

from datetime       import datetime
from dotsShared     import common

MaxWidth = 1680  ##  position dock to screen bottom for max default display width
                 ##  on my mac with dock on left side, not on bottom
MaxScreens = ('1440','1536', '620')  ## requires 1920X1280 display size

### -------------------- dotsScreens -----------------------
''' dotsScreens: various screen formats and functions used
    in the title bar '''
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
  
### -------------------------------------------------------- 
screens = {  ## the keys arn't shown
    '1080': '1080X720 -  3:2',
    '1280': '1280X720 - 16:9',
    '1215': '1215X810 -  3:2',
    '1440': '1440X810 - 16:9',
    '1296': '1296X864 -  3:2',
    '1536': '1536X864 - 16:9',
     '620': '620X1102 -  9:16',
}
 
### --------------- 1080X720 - 3:2 format ------------------
seven20 = {    
    'DotsH':     822, 
    'ViewH':     720,               
    'ScrollH':   687,  
    'SliderH':   679,  
    'margin1':    15,  ## sliderpanel margins top
    'margin2':    10,  ## right
    'factor':   0.30,  ## amount to scale pixitems unless preset    
    'modLabel':  1.0,  ## amount to scale scroll label height 
    'scaleY':    1.0,  ## same as 720
    'steps':       6,  ## number of visible scroll widgets
}

ten80 = {            
    'Screen':   '1080',        ## used by both 1080 and 1280X720px 
    'DotsW':      1427,  
    'ViewW':      1080,  
    'gridSize':   30.0,       ## gridline spacing - seems to work, consistant
    'scaleX':      1.0,
    'widget':   (175,175),  ## position pix and shadow widgets using getCtr 
    'bkgrnd': (-525,-455),
    'runThis':  'demo-1080.play',  ## default run key
}

### ------------------ 1280X720 - 16:9 ---------------------
twelve80 = {  
    'Screen': '1280',        
    'DotsW':    1628, 
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
    'DotsW':    1563,   
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
    'DotsW':    1787,
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
    'steps':       9, 
}

### ------------------ 1264X864 - 3:2 ----------------------
twelve96 = {  
    'Screen':  '1296',  
    'DotsW':    1643,
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
    'DotsW':    1885, 
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
    'DotsW':    968,
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



