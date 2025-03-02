
from PyQt6.QtCore       import Qt, QPointF, pyqtProperty
from PyQt6.QtGui        import QImage, QPixmap


from PyQt6.QtWidgets    import QGraphicsPathItem, QGraphicsItemGroup, \
                            QGraphicsPolygonItem, QGraphicsPixmapItem

### --------------------- dotsShared.py --------------------
''' classes:  Ball, Outline, PathsItem, ItemsGroup and data 
                shared across classes and files ''' 
### --------------------------------------------------------
class Ball(QGraphicsPixmapItem):  ## added type to track it better
### --------------------------------------------------------
    def __init__(self, img, parent=''):
        super().__init__()          
      
        self.canvas = parent
        
        self.type = 'ball'
        self.setPixmap(QPixmap(img))
   
   
    def mouseDoubleClickEvent(self, e):
        if self.canvas != '':
            self.canvas.sideCar.delbackdrp()
    
### --------------------------------------------------------
class Outline(QGraphicsPolygonItem):  
### --------------------------------------------------------
     def __init__(self, path):
          super().__init__()          
         
          self.type = 'poly'
          self.setPolygon(path)

### --------------------------------------------------------
class PathsItem(QGraphicsPathItem): 
### --------------------------------------------------------
    def __init__(self, path):
        super().__init__()          
      
        self.type = 'pathsItem'
        self.setPath(path)
        
### --------------------------------------------------------
class ItemsGroup(QGraphicsItemGroup): 
### --------------------------------------------------------
    def __init__(self):
        super().__init__()          
       
        self.type = 'group'
        
### --------------------------------------------------------

common = {  ## wherever it's needed
    'tagZ':      20.0,    ## Zvalues settings 
    'pathZ':    -25.0, 
    'gridZ':    -50.0, 
    'bkgZ':     -99.0, 
    
    'shadow':    50.0,    ## Zvalue for points in shadows
    'points':    40.0,    ## Zvalue for points in shadows
    'outline':   30.0,    ## Zvalue for outline in shadows
    
    'SliderW':      127,  ## used by keysPanel
    'OffSet':         0,  ## keysPanel width, used to set fixed size 
    'fix':            23,  ## keysPanel height, used to set fixed size 
    'V':           12.0,  ## diameter of pointItems in shadows
    'widgetXY': (25,25),  ## position pathWidget and BkgWidget 
} 
 
### --------------------------------------------------------
CanvasStr = "A,B,C,D,E,F,H,J,L,M,P,R,S,T,W,\",<,>,[,],{,},_,+,/,-,=,;,.,,lock,space,cmd,left,right,up,down,del,opt,shift,return,enter,tag"   

PathStr = "B,C,D,E,H,L,N,M,P,R,S,T,U,V,W,{,},[,],/,!,@,;,\',,<,>,:,\",_,+,-,=,cmd,left,right,up,down,del,opt,shift,delPts"

PlayKeys = ('A','D','G','J','K','L','M','N','O','P','R','S','U','V','W','Y','X','space') 

## use this and make sure your editor points to the right directory
paths = {          
    'snapShot':     './',    ## src directory for now - add yours
    'bkgPath':      './../backgrounds/',
    'imagePath':    './../images/',
    'playPath':     './../plays/',
    'spritePath':   './../sprites/',
    'paths':        './../paths/',
    'txy':          './../txy/',
    'demo':         './../demo/',
}

Tick = 3.0

ControlKeys = ('resume','pause')

MoveKeys = {
    'right': (Tick, 0.0),
    'left':  (-Tick, 0.0),
    'up':    (0.0, -Tick),
    'down':  (0.0, Tick),
}

RotateKeys = {  ## works in reverse
    '+':  -1.0,
    '_':   1.0,
    '-':  15.0,   
    '=': -15.0,
    ']': -45.0,   
    '[':  45.0,
    '}': -90.0,   
    '{':  90.0,
}

Star = ((100, 20), (112, 63), (158, 63), (122, 91), 
        (136, 133), (100, 106), (63, 132), (77, 90), 
        (41, 63), (86, 63))

pathcolors = (
    'DODGERBLUE',    
    'AQUAMARINE', 
    'CORAL',         
    'CYAN',        
    'DEEPSKYBLUE',   
    'LAWNGREEN', 
    'GREEN',    
    'HOTPINK',  
    'WHITESMOKE',
    'LIGHTCORAL', 
    'LIGHTGREEN',    
    'LIGHTSALMON', 
    'LIGHTSKYBLUE',
    'LIGHTSEAGREEN', 
    'MAGENTA',     
    'TOMATO',
    'ORANGERED', 
    'RED',    
    'YELLOW',
    )       

singleKeys = {  ## wish I had done this earlier
    Qt.Key.Key_Up:           'up',          
    Qt.Key.Key_Down:       'down',
    Qt.Key.Key_Left:       'left',      
    Qt.Key.Key_Right:     'right',
    Qt.Key.Key_Alt:         'opt',    
    Qt.Key.Key_Shift:     'shift',
    Qt.Key.Key_Control:     'cmd',
    Qt.Key.Key_Enter:     'enter',
    Qt.Key.Key_Return:   'return',
    Qt.Key.Key_Space:     'space',  
    Qt.Key.Key_Backslash:   'tag',   
    Qt.Key.Key_A: 'A',   
    Qt.Key.Key_B: 'B',     
    Qt.Key.Key_C: 'C',
    Qt.Key.Key_E: 'E',  
    Qt.Key.Key_F: 'F',
    Qt.Key.Key_G: 'G',
    Qt.Key.Key_H: 'H', 
    Qt.Key.Key_J: 'J', 
    Qt.Key.Key_K: 'K',  
    Qt.Key.Key_L: 'L',   
    Qt.Key.Key_M: 'M', 
    Qt.Key.Key_N: 'N', 
    Qt.Key.Key_O: 'O',  
    Qt.Key.Key_P: 'P',
    Qt.Key.Key_R: 'R',
    Qt.Key.Key_S: 'S', 
    Qt.Key.Key_T: 'T',
    Qt.Key.Key_U: 'U',
    Qt.Key.Key_V: 'V', 
    Qt.Key.Key_W: 'W',  
    Qt.Key.Key_Y: 'Y',  
    Qt.Key.Key_Comma:  ',', 
    Qt.Key.Key_Period: '.',     
    Qt.Key.Key_Plus:   '+',         
    Qt.Key.Key_Equal:  '=',    
    Qt.Key.Key_Minus:  '-',  
    Qt.Key.Key_Less:   '<',     
    Qt.Key.Key_Greater:      '>',
    Qt.Key.Key_Colon:        ':',   
    Qt.Key.Key_Semicolon:    ';',  
    Qt.Key.Key_Apostrophe:  '\'',      
    Qt.Key.Key_QuoteDbl:    '\"', 
    Qt.Key.Key_Slash:        '/',
    Qt.Key.Key_Underscore:   '_', 
    Qt.Key.Key_BraceLeft:    '{',
    Qt.Key.Key_BraceRight:   '}',   
    Qt.Key.Key_BracketLeft:  '[',
    Qt.Key.Key_BracketRight: ']', 
}

### --------------------- dotsShared.py --------------------

