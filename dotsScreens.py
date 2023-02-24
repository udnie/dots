
from PyQt6.QtCore   import QPoint
from PyQt6.QtGui    import QGuiApplication

from datetime       import datetime
from dotsShared     import common

MaxWidth = 1680  ##  position dock to screen bottom for max default display width
                 ##  on my mac with dock on left side, not on bottom
MaxScreens = ('1350','1536','1440','1432','620')  ## requires 1920X1280 display size

### -------------------- dotsScreens -----------------------
''' dotsScreens: various screen formats and functions used
    in the title bar '''
### --------------------------------------------------------
def setCommon(format=""):
    if format == '1080':      ## 1080X720 - 3:2 same as default
        common.update(ten80)  
        common.update(seven20)  
        return screens['1080']  
    elif format == '1280':    ## 1280X720 - 16:9
        common.update(twelve80)  
        common.update(seven20) 
        return screens['1280']  
    elif format == '1350':     ## 1350X900 - 3:2
        common.update(thirteen50) 
        return screens['1350'] 
    elif format == '1536':     ## 1536X864 - 16:9
        common.update(fifteen36) 
        return screens['1536']   
    elif format == '620':    ## 1000X1100 - 9:16
        common.update(V620)              
        return screens['620']  
    elif format == '1440':   ## 1440X810 - 16:9
        common.update(fourteen40) 
        return screens['1440'] 
    elif format == '1432':   ## 1440X960 - 3:2
        common.update(fourteen32)   ## the 32 is from 3:2
        return screens['1432']    
    else:
        common.update(ten80)  ## 1080X720 - 3:2 - default
        common.update(seven20) 
        return '1080X720 - 3:2' 
  
### -------------------------------------------------------- 
screens = {  ## the keys arn't shown
    '1080': "1080X720 -  3:2",
    "1280": "1280X720 - 16:9",
    '1350': '1350X900 -  3:2',
    '1440': '1440X810 - 16:9',
    '1432': '1440X960 -  3:2',
    '1536': '1536X864 - 16:9',
     '620': '620X1102 -  9:16',
}
 
### --------------- 1080X720 - 3:2 format ------------------
seven20 = {        
    "ScrollH":  687,  
    "SliderH":  679,  
    "margin1":   15,     ## sliderpanel margins top
    "margin2":   10,     ## right
    "factor":     0.30,  ## amount to scale pixitems unless preset    
    "modLabel":   1.0,   ## amount to scale scroll label height 
    "ViewH":    720,
}

ten80 = {            
    "Screen": '1080',        ## used by both 1080 and 1280X720px 
    "DotsW":    1427,  
    "DotsH":     822,  
    "ViewW":    1080,  
    "gridSize":   30.0,       ## gridline spacing - seems to work, consistant
    "scaleX":      1.0,
    "scaleY":      1.0,       ## same as 720
    "widget":     (175,175),  ## position pix and shadow widgets using getCtr 
    "bkgrnd":    (-525,-455),
    "runThis":  "demo-1080.play",  ## default run key
}

### ------------------ 1280X720 - 16:9 ---------------------
twelve80 = {  
    "Screen": '1280',        
    "DotsW":    1628, 
    "DotsH":     822, 
    "ViewW":    1280,  
    "gridSize":   26.66,  
    "scaleX":      1.15,
    "scaleY":      1.0,  ## same as 720
    "widget":    (75,175),
    "bkgrnd":  (-625,-455),
    "runThis":  "demo-1280.play",  ## default run key
}

### ------------------ 1350X900 - 3:2 ----------------------
thirteen50 = {       
    "Screen": '1350',    
    "DotsW":    1697,
    "DotsH":    1002, 
    "ViewW":    1350,  
    "ViewH":     900,     
    "ScrollH":   806,
    "SliderH":   800,    
    "margin1":    20,
    "margin2":     3,
    "gridSize":   30, 
    "factor":      0.34,  ## scales pixitems by format
    "modLabel":    1.0,
    "scaleX":      1.175,
    "scaleY":      1.20, 
    "widget":    (25,125),
    "bkgrnd":  (-660,-510),
    "runThis":  "demo-1350.play",  ## default run key
}

### ------------------ 1440X810 - 16:9 ----------------------
fourteen40 = {  
    "Screen": '1440',         
    "DotsW":    1790,
    "DotsH":     912, 
    "ViewW":    1440,  
    "ViewH":     810,     
    "ScrollH":   772,
    "SliderH":   770,    
    "margin1":    20,
    "margin2":     3,
    "gridSize":   30, 
    "factor":      0.36,  ## scales pixitems by format
    "modLabel":    0.962,
    "scaleX":      1.175,
    "scaleY":      1.20, 
    "widget":    (0,150),
    "bkgrnd":  (-705,-485),
    "runThis":  "demo-1440.play",  ## default run key
}

### ------------------ 1440X960 - 3:2 ----------------------
fourteen32 = {  ## 1440 was taken and 32 seemed like a good choice
    "Screen":  '1432',  
    "DotsW":    1790,
    "DotsH":    1062, 
    "ViewW":    1440,  
    "ViewH":     960,          
    "ScrollH":   886,
    "SliderH":   885,    
    "margin1":    20,
    "margin2":     3,
    "gridSize":   30, 
    "factor":      0.34,  ## scales pixitems by format
    "modLabel":    0.97,
    "scaleX":      1.175,
    "scaleY":      1.20, 
    "widget":   (-5,100),
    "bkgrnd":  (-705,-530),
    "runThis":  "demo-1432.play",  ## default run key
}

### ------------------ 1536X864 - 16:9 ---------------------
fifteen36 = {      
    "Screen": '1536',   
    "DotsW":    1885,
    "DotsH":     966, 
    "ViewW":    1536,  
    "ViewH":     864,     
    "ScrollH":   804,
    "SliderH":   798,    
    "margin1":    20,
    "margin2":     0,
    "gridSize":   32,  
    "factor":      0.36,  ## scales pixitems by format 
    "modLabel":    1.0, 
    "scaleX":      1.40,
    "scaleY":      1.20,
    "widget":  (-50,150),
    "bkgrnd": (-750,-500),
    "runThis":  "demo-1536.play",  ## default run key
}

### -------------------- 620X1102 - 9:16 --------------------
V620 = {             ## 620 - must be a string not a number
    "Screen": '620',  
    "DotsW":    968,
    "DotsH":   1204, 
    "ViewW":    620,  
    "ViewH":   1102,     
    "ScrollH": 1022,
    "SliderH":  977,    
    "margin1":   15,
    "margin2":    0,
    "gridSize":  34.43, 
    "factor":     0.33, 
    "modLabel":   1.0,
    "scaleX":     0.5,
    "scaleY":     1.40,  
    "widget":  (405,75),
    "bkgrnd": (-305,-590),
    "runThis":  "demo-620.play",  ## default run key
}

### -----------------------------------------------------        
def getDate():
    d = datetime.now()
    return d.strftime("%m-%d-%Y")

def getX():  ## adjusted for app size and display
    ctr = QGuiApplication.primaryScreen().availableGeometry().center()
    return int(((ctr.x() * 2 ) - common['DotsW'])/2)

def getY():
    ctr = QGuiApplication.primaryScreen().availableGeometry().center()  
    return int((((ctr.y() * 2 ) - common['DotsH'])/2)*.65)  

### -------------------- dotsScreens -----------------------



