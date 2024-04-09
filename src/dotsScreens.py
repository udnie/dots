
from datetime           import datetime
from PyQt6.QtGui        import QGuiApplication

from dotsShared         import common, screens

### -------------------- dotsScreens -----------------------
''' no class: screen formats and functions '''     
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
         
    elif format == '1102':       ## 620X1102 - 9:16
        common.update(vert)
        common.update(six20)              
        return screens['1102'] 
    
    elif format == '900':       ## 600X900 - 2:3
        common.update(vert)
        common.update(six30)              
        return screens['900'] 
    
    elif format == '912':       ## 513X912 - 9:16
        common.update(vert)
        common.update(nine12)              
        return screens['912'] 
     
    else:
        common.update(ten80)  ## 1080X720 - 3:2 - default
        common.update(seven20) 
        return '1080X720 - 3:2' 
   
##  -------------- 1080X720 - 3:2 and 1280X720 - 16:9 ----------------
seven20 = {     ## used by both 1080X720 and 1280X720px     
    'DotsH':     822, 
    'ViewH':     720,       
    'ScrollH':   682,  
    'SliderH':   679,  
    'margin1':    15,  ## keysMenu margins top
    'margin2':    10,  ## right
    'factor':   0.30,  ## amount to scale pixitems unless preset    
    'scaleY':    1.0,  ## same as 720
    'steps':       7,  ## number of visible scroll widgets
}

ten80 = {   ## 1080X720 - 3:2        
    'Screen':   '1080',     
    'DotsW':      1382,  
    'ViewW':      1080,  
    'gridSize':   30.0,       ## gridline spacing - seems to work, consistant
    'scaleX':      1.0,
}

twelve80 = {    ## 1280X720 - 16:9
    'Screen':   '1280',        
    'DotsW':      1583, 
    'ViewW':      1280,  
    'gridSize':  26.66,  
    'scaleX':     1.15,
}

## -------------- 1215X810 - 3:2 and 1440X810 - 16:9 ----------------
eight10 = {  ## used by both 1215X810 and 140X810px
    'DotsH':     912, 
    'ViewH':     810,     
    'ScrollH':   775,  ## scroll panel height
    'SliderH':   770,    
    'margin1':    13,  ## scroll panel top margin
    'margin2':     3,
    'scaleY':   1.15, 
    'factor':   0.35,  ## scales pixitems by format
    'steps':       8, 
}

twelve15 = {    ## 1215X810 - 3:2 format
    'Screen':   '1215',  
    'DotsW':      1518,   
    'ViewW':      1215,    
    'gridSize': 28.925, 
    'scaleX':     1.05,
}
    
fourteen40 = {  ## 1440X810 - 16:9 
    'Screen':  '1440',         
    'DotsW':     1743,
    'ViewW':     1440,
    'gridSize':    30, 
    'scaleX':    1.30,
}

### ---------- used by both 1296X864 and 1536X864px -------- 
eight64 = { 
    'DotsH':     966,     
    'ViewH':     864,    
    'ScrollH':   787,  ## scroll panel height
    'SliderH':   803,    
    'margin1':    23,  ## scroll panel top margin
    'margin2':     0,
    'scaleY':   1.15,
    'factor':   0.38,  ## scales pixitems by format
    'steps':       8, 
}

### ------------------ 1264X864 - 3:2 ----------------------
twelve96 = {  
    'Screen':   '1296',  
    'DotsW':     1597,
    'ViewW':     1296,  
    'gridSize':    30, 
    'scaleX':   1.123,
}

### ------------------ 1536X864 - 16:9 ---------------------
fifteen36 = {      
    'Screen':  '1536',   ## think about 1560X878 in 1920X1080
    'DotsW':     1837, 
    'ViewW':     1536,      
    'gridSize':    32,  
    'scaleX':    1.40,
}

### ---------------------------------------------------------
###                         verticals
### ---------- used by both 600X900px and 620X1102px -------- 
vert = {  
    'factor':    0.33, 
    'scaleX':     0.5,
    'scaleY':    1.40,  
    'steps':       10, 
}

### -------------------- 620X1102 - 9:16 --------------------
six20 = {   ## 1102 - must be a string not a number
    'Screen':   '1102',  
    'DotsW':      927,
    'DotsH':     1204, 
    'ViewW':      620, 
    'ViewH':     1102,  
    'margin1':     22,   
    'margin2':     -5,       
    'ScrollH':    977,
    'SliderH':    977, 
    'gridSize': 34.43,
}

six30 = {  ## 900X600
    'Screen':   '900',  
    'DotsW':      940,
    'DotsH':     1002,  
    'ViewW':      600, 
    'ViewH':      900,   
    'margin1':     10,    
    'ScrollH':    867,
    'SliderH':    862, 
    'gridSize':  30.0,
}

nine12 = {  ## 912X513
    'Screen':    '912',  
    'DotsW':      838,
    'DotsH':     1015,  
    'ViewW':      513, 
    'ViewH':      912,   
    'margin1':     10,    
    'ScrollH':    867,
    'SliderH':    862, 
    'gridSize':  28.5,
}

### -----------------------------------------------------        
def getDate():  ## these 3 used by DotsQt.py - piggie-backing on screens
    d = datetime.now()
    return d.strftime('%m-%d-%Y')

def getCtr():  ## adjusted for app size and display
    ctr = QGuiApplication.primaryScreen().availableGeometry().center()
    return ctr

def getX():  ## adjusted for app size and display
    ctr = QGuiApplication.primaryScreen().availableGeometry().center()
    return int(((ctr.x() * 2 ) - common['DotsW'])/2)

def getY():
    ctr = QGuiApplication.primaryScreen().availableGeometry().center()  
    if common['Screen'] in ('1102','900', '912'):    
        return 0  ## gets set to 50
    else:
        return int((((ctr.y() * 2 ) - common['DotsH'])/2)*.45)   
   
### -------------------- dotsScreens -----------------------



