from PyQt5.QtCore    import Qt

### --------------------- dotsShared.py --------------------
''' dotsShared: common and paths dictionaries shared across classes and files '''
### --------------------------------------------------------
common = {
    "factor": 0.35,
    "tagZ":   20.0,    
    "gridZ": -50.0, 
    "pathZ": -25.0,  
    "bkgZ":  -99.0,
    "DotsW":  1460,  # app width 
    "DotsH":   825,  # app height
    "ViewW":  1080,  # canvas width  30 X 36
    "ViewH":   720,  # canvas height 30 X 24
    "gridSize": 30,
    "ScrollW": 152,  
    "ScrollH": 685,  
    "LabelW":  133,
    "LabelH":  112,    
    "MaxW":    110,
    "MaxH":     85,  
    "Star":    .70,
    "Type":    106,
    "Margin":   13,
    "runThis":  "demo.play",
}
          
CanvasStr = "L,R,P,S,C,:,\",\',<,>,{,},[,],_,+,/,-,=,lock,space,cmd,left,right,up,down,del,shift,opt,return,enter"   
PathStr = "F,S,C,D,N,T,P,R,W,V,{,},/,!,;,\',,<,>,:,\",_,+,-,=,cmd,left,right,up,down,del,opt"

paths = {
    "snapShot":   "./",
    "bkgPath":    "./backgrounds/",
    "imagePath":  "./images/",
    "playPath":   "./plays/",
    "paths":      "./paths/",
    "spritePath": "./sprites/",
}

Star = ((100, 20), (112, 63), (158, 63), (122, 91), 
        (136, 133), (100, 106), (63, 132), (77, 90), 
        (41, 63), (86, 63))

keyMenu = (               ## used by pixitems and bkgitems
    ('A', 'Select All'),   
    ('C', 'Clear Canvas'),     
    ('D', 'Delete Selected'),
    ('F', 'Flop Selected'),
    ('G', 'Add/Hide Grid'),
    ('H', 'Hide/UnHide'),
    ('K', 'Toggle KeyList'),
    ('L', 'Load Play'),
    ('M', 'Map Selected'),
    ('P', 'Toggle Paths'),
    ('R', 'Run Play/Demo'),
    ('S', 'Stop Play'),
    ('T', 'Toggle Tags'),
    ('U', 'UnSelect All'),
    ('Shift', '+L ToggleLocks'),
    ('Shift', '+R Locks All'),
    ('Shift', '+T TagSelected'),
    ('Space', 'Show this Tag'),
    ('\'', 'Toggle this lock'),
    ('X, Q', 'Escape to Quit'),
    ('Rtn', 'Enter to Front'),
    ('/', 'Clk to Back'),
    ('[', 'Clk Back One Z'),
    (']', 'Clk Up One Z'),
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
    ('C', 'Center Path'),
    ("D", "Delete Screen"), 
    ("F", "Files"),
    ("N", "New Path"),
    ("P", "Path Chooser"),
    ("R", "Reverse Path"),
    ("S", "Save Path"),
    ("T", "Test"),
    ("W", "Way Points"),
    ("V", "..View Points"),
    ("/", "Path Color"),
    ("cmd", "Closes Path"),
    ('_/+', "Rotate 1 deg"),  
    ('-/=', "Rotate 15 deg"),
    ('<,>', 'Toggle Size'),
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
    Qt.Key_Enter: 'enter',
    Qt.Key_Return: 'return',
    Qt.Key_Space: 'space',             
    Qt.Key_C: 'C',  
    Qt.Key_L: 'L',   
    Qt.Key_N: 'N', 
    Qt.Key_O: 'O',  
    Qt.Key_P: 'P',
    Qt.Key_R: 'R',
    Qt.Key_S: 'S', 
    Qt.Key_T: 'T',
    Qt.Key_V: 'V', 
    Qt.Key_W: 'W',  
    Qt.Key_Plus: '+',         
    Qt.Key_Equal: '=',    
    Qt.Key_Minus: '-',  
    Qt.Key_Less: '<',     
    Qt.Key_Greater: '>',
    Qt.Key_Colon: ':',   
    Qt.Key_Semicolon: ';',  
    Qt.Key_Apostrophe: '\'',      
    Qt.Key_QuoteDbl: '"', 
    Qt.Key_Slash: '/',
    Qt.Key_Underscore: '_', 
    Qt.Key_BraceLeft: '{',
    Qt.Key_BraceRight: '}',   
    Qt.Key_BracketLeft: '[',
    Qt.Key_BracketRight: ']', 
}
### --------------------- dotsShared.py --------------------

