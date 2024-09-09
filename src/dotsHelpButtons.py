
from functools          import partial

from PyQt6.QtCore       import QTimer

from dotsSideGig        import getVuCtr, Grid
from dotsShared         import PlayKeys 
from dotsTableModel     import TableWidgetSetUp, QC, QL, QH
from dotsPathWorks      import PathHelp

canvasKeys = {
    'A':    'Add a Background', 
    'D':    'Display the Demo Menu',
    'G':    'Toggle Grid',
    'J':    'JSON File Viewer',
    'K':    'Toggle KeysPanel',
    'L':    'Load a play file', 
    'M':    'Menu Help',
    'P':    'Switch to PathMaker', 
    'S':    'Display the Screen Menu',
    'X':    'X, Q, Escape to Quit',
}

storyKeys = {
    'A':    'Select All',   
    'C':    'Clear Canvas',
    'D':    'Delete Selected',
    'J':    'JSON Play File Viewer',
    'L':    'Load Play File',
    'O':    'Toggle Shadow Outlines',
    'U':    'UnSelect All',
    'W':    'Clear Widgets',
    'Shift-T':   'Toggles Tags', 
    'R':    'Run What\'s There',
    'SpaceBar':   'Pause/Resume', 
    'S':    'Stop Animation',  
    'X':    'X, Q, Escape to Quit',
}

### ------------------- dotsHelpButtons -------------------- 
''' classes: ButtonHelp, CanvasHelp and StoryBoardHelp '''
### --------------------------------------------------------
    ## PathMaker in helpButtons and pathWorks
    ## Sprites, Backgrounds and Shadows, in helpMonkey
    ## Demos, Screens and Animation Help,in helpMenus and pixWorks
    ## Frame, Flats and Matte Help,      in flat and frames and bkgMatte
    ## Widgets for Pixitems, Backgrounds.,  in helpMaker
### --------------------------------------------------------
class ButtonHelp:  ## includes pathMaker as well - see pathWorks
### --------------------------------------------------------    
    def __init__(self, parent):
        super().__init__()
        
        self.canvas = parent 
        self.scene  = self.canvas.scene
        self.pathMaker = self.canvas.pathMaker
        
        self.canvasFlag = False
        self.storyFlag  = False
        self.pathFlag   = False
         
## --------------------------------------------------------
    def openMenus(self):   
        if self.canvas.pathMakerOn == False:
            if len(self.scene.items()) == 0:
                if self.canvasFlag == True:
                    self.canvasHelp.closeMenu() 
                else:
                    self.canvas.clear()
                    self.canvasHelp = CanvasHelp(self, self.canvas)
            else:
                if self.storyFlag == True:
                    self.storyHelp.closeMenu() 
                else:
                    self.storyHelp = StoryHelp(self, self.canvas) 
        else:
            if self.pathFlag == True:
                self.pathHelp.closeMenu() 
            else:
                self.pathHelp = PathHelp(self, self.canvas)
        self.canvas.setFocus()
    
    def closeMenus(self):  ## used by showbiz not menus
        if self.canvas.pathMakerOn == False:
            if self.canvasFlag == True:
                self.canvasHelp.closeMenu() 
            elif self.storyFlag == True:
                self.storyHelp.closeMenu() 
        else:  
            if self.pathFlag == True:
                self.pathHelp.closeMenu() 
                     
### --------------------------------------------------------
class CanvasHelp: 
### -------------------------------------------------------- 
    def __init__(self, parent, canvas, off=0, str=''):
        super().__init__()  
       
        self.canvas = parent  ## canvas
        self.canvasFlag = True
        self.scene = self.canvas.scene
        
        self.grid = Grid(self.canvas)
        
        self.canvas = canvas
        self.switch = str

        self.table = TableWidgetSetUp(50, 210, len(canvasKeys)+5)
        self.table.itemClicked.connect(self.clicked)   
        
        width, height = 266, 457
        self.table.setFixedSize(width, height)

        self.table.setRow(0, 0, f'{"   Canvas Help Menu ":<20}','',True,True,2)
        
        row = 1
        for k , val in canvasKeys.items():
            self.table.setRow(row, 0, k)
            self.table.setRow(row, 1, "  " + val,'','',True)
            row += 1
                  
        c = '"cmd"'; d = '"opt" '; e = "Or "  

        self.table.setRow(row,     0, f"{'Use Up and Down Arrow Keys + '}" + f"{c:<10}",QC,True,True,2)  
        self.table.setRow(row + 1, 0, f"{e} {d} {'to Scroll ScrollPanel Tiles':<32}",QC,True,True,2)
        self.table.setRow(row + 2, 0, f'{"Enter Key or Select From Above   "}',QH,True,True, 2) 
        self.table.setRow(row + 3, 0, f"{'Click Here to Close':<20}",'',True,True, 2)
 
        x, y = getVuCtr(canvas)    
        if off != 0: x += off
        
        self.table.move(int(x - width /2), int(y - height /2))
        self.table.show() 
       
    def clicked(self):
        if self.switch == '':
            try:
                help = self.table.item(self.table.currentRow(), 0).text().strip()
                if help in canvasKeys.keys():
                    if help in PlayKeys:
                        QTimer.singleShot(25, partial(self.canvas.showbiz.keysInPlay, help)) 
                    elif help == 'K':
                        self.canvas.sideCar.toggleKeysMenu()  
                    elif help == 'G':
                        self.grid.toggleGrid()
            except:
                None          
        self.closeMenu()
       
    def closeMenu(self):
        self.canvasFlag = False 
        self.table.close()
        if self.switch !='':
            self.canvas.setKeys('M')
    
### --------------------------------------------------------     
class StoryHelp: 
### -------------------------------------------------------- 
    def __init__(self, parent, canvas, off=0, str=''):
        super().__init__()  
     
        self.helpButton = parent  ## canvas
        self.helpButton.storyFlag = True
        
        self.canvas = canvas
        self.switch = str 
    
        self.table = TableWidgetSetUp(70, 215, len(storyKeys)+4)
        self.table.itemClicked.connect(self.clicked)    
    
        width, height = 292, 517
        self.table.setFixedSize(width, height)
     
        self.table.setRow(0, 0, f'{"   StoryBoard Help Menu":<30}','',True,True,2)
        
        row = 1
        for k , val in storyKeys.items():
            self.table.setRow(row, 0, k)
            self.table.setRow(row, 1, "  " + val,'','',True)
            row += 1
           
        self.table.setRow(row, 0,     f"{'Use Arrow Keys to Move Selected Sprites ':<15}",QC,True,True, 2)
        self.table.setRow(row + 1, 0, f'{"Enter Key or Select From Above   "}',QH,True,True, 2) 
        self.table.setRow(row + 2, 0, f"{'Click Here to Close':<25}",'',True,True, 2)
  
        x, y = getVuCtr(canvas)  
        if off != 0: x += off  
        
        self.table.move(int(x - width /2), int(y - height /2))
        self.table.show()
              
    def clicked(self):
        if self.switch == '':
            try:
                help = self.table.item(self.table.currentRow(), 0).text().strip()
                if help in storyKeys.keys() and help in PlayKeys:
                    QTimer.singleShot(25, partial(self.canvas.showbiz.keysInPlay, help))
            except:
                None    
        self.closeMenu()
       
    def closeMenu(self):
        self.helpButton.storyFlag = False  
        self.table.close()
        if self.switch !='':
            self.canvas.setKeys('M')
                
### ------------------- dotsHelpButtons -------------------- 
  
        



