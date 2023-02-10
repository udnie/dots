
from PyQt6.QtCore    import Qt

### --------------------- dotsShared.py --------------------
''' dotsShared: common data shared across classes and files '''
### --------------------------------------------------------

common = {
    "tagZ":      20.0,    
    "pathZ":    -25.0, 
    "gridZ":    -50.0, 
    "bkgZ":     -99.0, 
    "shadow":    50.0,
    "points":    40.0,
    "outline":   30.0,
    "ScrollW":    138,  ## used by both 1080 and 1280X720 px
    "SliderW":    170,    
    "OffSet":       0,  ## sliderpanel width, used to set fixed size 
    "fix":          23,  ## sliderpanel height, used to set fixed size 
    "V":         12.0,  ## diameter of pointItems in shadows
} 
      
### --------------------------------------------------------
             
CanvasStr = "L,R,P,S,C,W,\",\',<,>,[,],_,+,/,-,=,;,.,lock,space,cmd,left,right,up,down,del,opt,shift,return,enter"   
PathStr = "C,D,E,F,L,N,P,R,S,T,V,K,W,{,},[,],/,!,@,;,\',,<,>,:,\",_,+,-,=,cmd,left,right,up,down,del,opt,shift,delPts"
ScaleRotateKeys = ('+','_','<','>',':','\"','=','-',';','\'','[',']')

paths = {
    "snapShot":   "./",
    "bkgPath":    "./backgrounds/",
    "imagePath":  "./images/",
    "playPath":   "./plays/",
    "paths":      "./paths/",
    "spritePath": "./sprites/",
    "txy":        "./txy/",
}

Tick = 2.0

MoveKeys = {
    "right": (Tick, 0.0),
    "left":  (-Tick, 0.0),
    "up":    (0.0, -Tick),
    "down":  (0.0, Tick),
}

PlayKeys = ('resume','pause')

RotateKeys = {  ## works in reverse
    '+':  -1.0,
    '_':   1.0,
    '-':  15.0,   
    '=': -15.0,
    ']': -45.0,   
    '[':  45.0,
}

Star = ((100, 20), (112, 63), (158, 63), (122, 91), 
        (136, 133), (100, 106), (63, 132), (77, 90), 
        (41, 63), (86, 63))

pathcolors = (
    "DODGERBLUE",    
    "AQUAMARINE", 
    "CORAL",         
    "CYAN",        
    "DEEPSKYBLUE",   
    "LAWNGREEN", 
    "GREEN",    
    "HOTPINK",  
    "WHITESMOKE",
    "LIGHTCORAL", 
    "LIGHTGREEN",    
    "LIGHTSALMON", 
    "LIGHTSKYBLUE",
    "LIGHTSEAGREEN", 
    "MAGENTA",     
    "TOMATO",
    "ORANGERED", 
    "RED",    
    "YELLOW",
    )       

singleKeys = {  ## wish I had done this earlier
    Qt.Key.Key_Up: 'up',          
    Qt.Key.Key_Down: 'down',
    Qt.Key.Key_Left: 'left',      
    Qt.Key.Key_Right:'right',
    Qt.Key.Key_Alt: 'opt',    
    Qt.Key.Key_Shift: 'shift',
    Qt.Key.Key_Control: 'cmd',
    Qt.Key.Key_Enter: 'enter',
    Qt.Key.Key_Return: 'return',
    Qt.Key.Key_Space: 'space',  
    Qt.Key.Key_Backslash: 'front',           
    Qt.Key.Key_C: 'C',
    Qt.Key.Key_E: 'E',  
    Qt.Key.Key_K: 'K',  
    Qt.Key.Key_L: 'L',   
    Qt.Key.Key_N: 'N', 
    Qt.Key.Key_O: 'O',  
    Qt.Key.Key_P: 'P',
    Qt.Key.Key_R: 'R',
    Qt.Key.Key_S: 'S', 
    Qt.Key.Key_T: 'T',
    Qt.Key.Key_U: 'U',
    Qt.Key.Key_V: 'V', 
    Qt.Key.Key_W: 'W',  
    Qt.Key.Key_Comma: ',', 
    Qt.Key.Key_Period: '.',     
    Qt.Key.Key_Plus: '+',         
    Qt.Key.Key_Equal: '=',    
    Qt.Key.Key_Minus: '-',  
    Qt.Key.Key_Less: '<',     
    Qt.Key.Key_Greater: '>',
    Qt.Key.Key_Colon: ':',   
    Qt.Key.Key_Semicolon: ';',  
    Qt.Key.Key_Apostrophe: '\'',      
    Qt.Key.Key_QuoteDbl: '"', 
    Qt.Key.Key_Slash: '/',
    Qt.Key.Key_Underscore: '_', 
    Qt.Key.Key_BraceLeft: '{',
    Qt.Key.Key_BraceRight: '}',   
    Qt.Key.Key_BracketLeft: '[',
    Qt.Key.Key_BracketRight: ']', 
}

### --------------------- dotsShared.py --------------------

