
from PyQt6.QtCore    import Qt

### --------------------- dotsShared.py --------------------
''' dotsShared: common data shared across classes and files '''
### --------------------------------------------------------
common = {
    "factor": 0.35,
    "tagZ":   20.0,    
    "gridZ": -50.0, 
    "pathZ": -25.0,  
    "bkgZ":  -99.0,
    "DotsW":  1455,  # app width 
    "DotsH":   825,  # app height
    "ViewW":  1080,  # canvas width  30 X 36
    "ViewH":   720,  # canvas height 30 X 24
    "gridSize": 30,  # number of pixels per side
    "ScrollW": 152,  # scrollbar stuff
    "ScrollH": 685,  
    "LabelW":  133,
    "LabelH":  112,    
    "MaxW":    110,
    "MaxH":     85,  
    "Star":    .70,
    "Type":    106,
    "Margin":   13,
    "V":      12.0,
    "runThis":  "demo.play",
}
          
CanvasStr = "L,R,P,S,C,W,\",\',<,>,[,],_,+,/,-,=,;,.,lock,space,cmd,left,right,up,down,del,opt,shift,return,enter"   
PathStr = "C,D,E,F,L,N,P,R,S,T,W,V,K,{,},[,],/,!,@,;,\',,<,>,:,\",_,+,-,=,cmd,left,right,up,down,del,opt,shift,delPts"
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

RotateKeys = {
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

keyMenu = (                    ## pixitems and bkgitems
    ('A', 'Select All'),   
    ('C', 'Clear Canvas'),     
    ('D', 'Delete Selected'),
    ('F', 'Flop Selected'),
    ('G', 'Add/Hide Grid'),
    ('H', 'Hide/UnHide'),
    ('K', 'Toggle KeyList'),
    ('L', 'Load Play'),
    ('M', 'Map Selected'),
    ('O', 'Clear Outlines'),
    ('P', 'Toggle Paths'),
    ('R', 'Run Play/Demo'),
    ('S', 'Stop Play'),
    ('T', 'Toggle Tags'),
    ('U', 'UnSelect All'),
    ('W'  'Clear Widgets'), 
    ('Shift', '+H Hide Selected'), 
    ('Shift', '+L ToggleLocks'),
    ('Shift', '+R Locks All'),
    ('Shift', '+T TagSelected'),
    ('Shift', '+U Unlocks All'),
    ('Shift', '+V Pixel Ruler'),   
    ('Space', 'Show this Tag'),
    ('\'', 'Toggle this lock'),
    ('X, Q', 'Escape to Quit'),
    ('Rtn', 'Enter to Front'),
    ('/', 'Clk to Back'),
    (',', 'Clk Back One Z'),
    ('.', 'Clk Up One Z'),
    ('Del', 'Clk to Delete'),
    ('Shift', 'Clk to Flop'),  
    ('Opt', 'DbClk to Clone'),
    ('Opt', 'Drag Clones'), 
    ('Cmd', 'Drag to Select'),
    ('_/+', "Rotate 1 deg"),  
    ('-/=', "Rotate 15 deg"),
    ('[/]', 'Rotate 45 deg'),
    ('</>', 'Toggle Size'),
    ('U/D', 'Arrow Keys'),
    ('L/R', 'Arrow Keys'))

pathMenu = (
    ('C', 'Center Path'),
    ("D", "Delete Screen"), 
    ("E", "Edit Points"),
    ("F", "Files"),
    ("L", "Lasso"),
    ("N", "New Path"),
    ("P", "Path Chooser"),
    ("R", "Reverse Path"),
    ("S", "Save Path"),
    ("T", "Test"),
    ("W", "Way Points"),
    ("V", "..View Points"),
    ("Shift", "+D Delete Pts"),
    ('Shift', '+V Pixel Ruler'),
    ("cmd", "Closes Path"),
    ("/", "Path Color"),
    ('_/+', "Rotate 1 deg"),  
    ('-/=', "Rotate 15 deg"),
    ('[/]', 'Rotate 45 deg'),
    ('</>', 'Toggle Size'),
    ("} ", "Flop Path"),
    ("{ ", "Flip Path"),  
    (':/\"', "Scale X"),
    (';/\'', 'Scale Y'),
    ('U/D', 'Arrow Keys'),
    ('L/R', 'Arrow Keys'),   
    ("opt", "Add a Point"),
    ("del", "Delete a Point"),
    (">", "  Shift Pts +5%"),
    ("<", "  Shift Pts -5%"),
    ("! ","  Half Path Size"),
    ("@ ","  Redistribute Pts"),
)

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
    "YELLOW")       

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

