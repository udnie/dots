from PyQt5.QtCore    import *

### --------------------- dotsShared.py --------------------
''' dotsShared: common and paths dictionaries shared across classes and files '''
### --------------------------------------------------------
common = {
    "ViewW": 1080,  ## canvas width 
    "ViewH": 720,   ## canvas height
    "factor": 0.35,     
    "gridSize": 30,   
    "gridZ": -50.0, 
    "pathZ": -25.0,  
    "bkgZ":  -99.0,
}

MapStr = "L,O,P,S,C,:,\",<,>,{,},[,],_,+,/,cmd,left,right,up,down,del,shift,opt"   
PathStr = "F,S,C,D,N,T,P,R,W,{,},/,!,cmd,left,right,up,down,del,opt,<,>,:,\",_,+,-,="

paths = {
    "snapShot": "./",
    "bkgPath": "./backgrounds/",
    "imagePath": "./images/",
    "playPath": "./plays/",
    "paths": "./paths/",
    "spritePath": "./sprites/",
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
    ('O', 'Toggle Paths 2'),
    ('P', 'Play Tggl Paths'),
    ('S', 'Stop Play'),
    ('T', 'Toggle Tags'),
    ('U', 'UnSelect All'),
    ('X, Q', 'Escape to Quit'),
    ('', 'Clk to Front'),
    ('/', 'Clk to Back'),
    ('opt', 'Clk Back One Z'),
    ('cmd', 'Clk Up One Z'),
    ('Del', 'Clk to Delete'),
    ('Shift', 'Clk to Flop'),  
    ('Opt', 'DbClk to Clone'),
    ('Opt', 'Drag Clones'), 
    ('Cmd', 'Drag to Select'),
    ('_/+', 'Rotate 1 deg'),
    (':/"', 'Rotate 15 deg'),
    ('{/}', 'Rotate 45 deg'),
    ('</>', 'Toggle Size'),
    ('U/D', 'Arrow Keys'),
    ('L/R', 'Arrow Keys'))

pathMenu = (
    ("F", "Files"),
    ("S", "Save Path"),
    ("P", "Path Chooser"),
    ('C', 'Center Path'),
    ("D", "Delete Screen"), 
    ("N", "New Path"),
    ("T", "Test"),
    ("/", "Path Color"),
    ("cmd", "Closes Path"),
    ('_/+', "Rotate 1 deg"),
    ('<,>', 'Toggle Size'),
    ("} ", "Flop Path"),
    ("{ ", "Flip Path"),  
    (':/\"', "Scale X"),
    ('-,=', 'Scale Y'),
    ('U/D', 'Arrow Keys'),
    ('L/R', 'Arrow Keys'),
    ("W", "Way Points"),
    ("P", "Show Way Pts"),
    ("opt", "Add a Point"),
    ("del", "Delete a Point"),
    (">", "  Shift Pts +5%"),
    ("<", "  Shift Pts -5%"),
    ("R", "  Reverse Path"),
    ("! ","  Half Path Size"))

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
    Qt.Key_Up: 'up',          
    Qt.Key_Down: 'down',
    Qt.Key_Left: 'left',      
    Qt.Key_Right:'right',
    Qt.Key_Alt: 'opt',    
    Qt.Key_Shift: 'shift',
    Qt.Key_Control: 'cmd',
    Qt.Key_C: 'C',  
    Qt.Key_L: 'L',
    Qt.Key_N: 'N',   
    Qt.Key_O: 'O',  
    Qt.Key_P: 'P',
    Qt.Key_S: 'S', 
    Qt.Key_W: 'W',  
    Qt.Key_Plus: '+',         
    Qt.Key_Equal: '=',    
    Qt.Key_Minus: '-',  
    Qt.Key_Less: '<',     
    Qt.Key_Greater: '>',
    Qt.Key_Colon: ':',        
    Qt.Key_QuoteDbl: '"', 
    Qt.Key_Slash: '/',
    Qt.Key_Underscore: '_', 
    Qt.Key_BraceLeft: '{',
    Qt.Key_BraceRight: '}',   
    Qt.Key_BracketLeft: '[',
    Qt.Key_BracketRight: ']', 
}

### --------------------- dotsShared.py --------------------

