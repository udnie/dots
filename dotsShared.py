from PyQt5.QtCore    import *

### --------------------- dotsShared.py --------------------
''' dotsShared: common and paths dictionaries shared across classes and files '''
### --------------------------------------------------------
common = {
    "viewW": 1056,  ## canvas width
    "viewH": 704,   ## canvas height
    "factor": 0.35,     
    "gridSize": 32,
    "gridZ": -50.0, 
    "pathZ": -25.0,     
}
     
paths = {
    "snapShot": "./",
    "bkgPath": "./backgrounds/",
    "imagePath": "./images/",
    "playPath": "./plays/",
    "paths": "./paths/",
    "spritePath": "./sprites/",
}

keyMenu = [                     ## pixitems and bkgitems
    ('A', 'Select All'),   
    ('C', 'Clear Canvas'),     
    ('D', 'Delete Selected'),
    ('F', 'Flop Selected'),
    ('G', 'Add/Hide Grid'),
    ('H', 'Hide/UnHide'),
    ('K', 'Toggle KeyList'),
    ('L', 'Load Play'),
    ('M', 'Map Selected'),
    ('P', 'Play Tggl Paths'),
    ('S', 'Stop Play'),
    ('T', 'Toggle Tags'),
    ('U', 'UnSelect All'),
    ('X, Q', 'Escape to Quit'),
    ('', 'Clk to Front'),
    ('/', 'Clk to Back'),
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
    ('L/R', 'Arrow Keys')]

pathMenu = [
    ("F", "Files"),
    ("S", "Save Path"),
    ("P", "Path Chooser"),
    ('C', 'Center Path'),
    ("D", "Delete Screen"), 
    ("N", "New Path"),
    ("/", "Path Color"),
    ("cmd", "Closes Path"),
    ("T", "Test"),
    ("W", "Way Points"),
    (">", "  Shift Pts +5%"),
    ("<", "  Shift Pts -5%"),
    ("R", "  Reverse Path"),
    ("! ","  Half Path Size"),
    ('_/+', "Rotate 1 deg"),
    ('<,>', 'Toggle Size'),
    ("} ", "Flop Path"),
    ("{ ", "Flip Path"),  
    (':/\"', "Scale X"),
    ('-,=', 'Scale Y'),
    ('U/D', 'Arrow Keys'),
    ('L/R', 'Arrow Keys')]

pathcolors = [
    "DODGERBLUE",    
    "AQUAMARINE", 
    "CORAL",         
    "CYAN",        
    "DEEPSKYBLUE",   
    "LAWNGREEN",     
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
    "YELLOW"]        

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

