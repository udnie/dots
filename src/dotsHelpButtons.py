
from functools          import partial

from PyQt6.QtCore       import QTimer

from dotsSideGig        import getVuCtr
from dotsShared         import PlayKeys 
from dotsTableModel     import TableWidgetSetUp, QC, QL, QH
from dotsPathWorks      import PathHelp
from dotsHelpDesk       import StoryHelp2

canvasKeys = {
    'A':    'Add a Background', 
    'D':    'Display the Demo Menu',
    'G':    'Toggle Grid',
    'H':    'This Help Menu',
    'J':    'JSON File Viewer',
    'K':    'Toggle KeysPanel',
    'L':    'Load a play file', 
    'Menus':'Help Menus',
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
    'M':    'This Help Menu',
    'Menu': 'StoryBoard Help Menu 2',
    'Menus':'Help Menus',
    'O':    'Toggle Shadow Outlines', 
    'S':    'Save Play File',    
    'U':    'UnSelect All Sprites',
    'V':    'Video Widget',
    'W':    'Clear Widgets',
    'X':    'X, Q, Escape to Quit',
    'R':    'Run What\'s There',
    'SpaceBar': 'Pause/Resume', 
    'S ':    'Stop Animation',        
}

### ------------------- dotsHelpButtons -------------------- 
''' classes: ButtonHelp, CanvasHelp and StoryBoardHelp '''
### --------------------------------------------------------
    ## Animation Menu in pixWork
    ## Canvas and StoryBoard Menus in helpButtons
    ## Demos, Screens Menus in helpMenus 
    ## Frames and Flats Menu in frames and flats
    ## Matte Menu in bkgMatte    
    ## PathMaker Menu in pathWorks
    ## StoryHelp2 in helpDesk    
    ## Sprites, Background and Shadow Menus in helpMonkey
    ## Widgets for Pixitems, Backgrounds., in helpMaker 
### --------------------------------------------------------
class ButtonHelp:  ## includes pathMaker as well - see pathWorks
### --------------------------------------------------------    
    def __init__(self, parent):
        super().__init__()
        
        self.canvas = parent 
        self.scene  = self.canvas.scene
       
        self.canvasFlag = False
        self.storyFlag  = False
        self.pathFlag   = False
         
## --------------------------------------------------------
    def openMenus(self):   
        if self.canvas.pathMakerOn == False:
  
            if self.canvas.openPlayFile == 'menu':  ##  left over 
                if sum(pix.type == 'flat' for pix in self.scene.items()) == 1 and \
                    len(self.scene.items()) == 1:
                        self.canvas.clear()
                        
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
    
    def closeMenus(self,):  ## used by showbiz not menus
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
    def __init__(self, parent, canvas, off=0, switch=''):
        super().__init__()  
   
        self.helpButton = parent  ## canvas
        self.helpButton.canvasFlag = True
            
        self.canvas = canvas
        self.scene = self.canvas.scene
    
        self.switch = switch

        self.table = TableWidgetSetUp(50, 190, len(canvasKeys)+5)
        self.table.itemClicked.connect(self.clicked)   
        
        width, height = 246, 487
        self.table.setFixedSize(width, height)

        self.table.setRow(0, 0, f'{"   Canvas Help Menu ":<20}',QL,True,True,2)
        
        row = 1
        for k , val in canvasKeys.items():
            self.table.setRow(row, 0, k,'',True,True)
            self.table.setRow(row, 1, "  " + val,'','',True)
            row += 1
                  
        c = '"cmd"'; d = '"opt" '; e = "or "  ## for quotes

        self.table.setRow(row,     0, f"{'Use Up and Down Arrow Keys + '}" + f"{c:<10}",QC,True,True,2)  
        self.table.setRow(row + 1, 0, f"{e} {d} {'to Scroll ScrollPanel Tiles  ':<22}",QC,True,True,2)
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
                    if help == 'Menus': help = 'M'
                    if help in PlayKeys:
                        QTimer.singleShot(10, partial(self.canvas.setKeys, help))   
            except:
                None          
        self.closeMenu()
       
    def closeMenu(self):
        self.helpButton.canvasFlag = False 
        self.table.close()
        if self.switch != '':
            self.canvas.setKeys('N')
    
### --------------------------------------------------------     
class StoryHelp:  ## storyboard help goes directly to showbiz
### -------------------------------------------------------- 
    def __init__(self, parent, canvas, off=0, switch=''):
        super().__init__()  
     
        self.helpButton = parent  ## canvas
        self.helpButton.storyFlag = True
          
        self.canvas = canvas
        self.switch = switch
        
        self.storyHelp2 = None
    
        self.table = TableWidgetSetUp(70, 190, len(storyKeys)+5,0, 27)
        self.table.itemClicked.connect(self.clicked)    
    
        width, height = 267, 603
        self.table.setFixedSize(width, height)
     
        self.table.setRow(0, 0, f'{"   StoryBoard Help Menu":<30}',QL, True,True,2)
    
        row = 1
        for k, val in storyKeys.items():
            if row < 15:
                self.table.setRow(row, 0, k, '', True,True)
                self.table.setRow(row, 1, "  " + val, '', '',True)      
                row += 1
            else:
                if row == 15:
                    self.table.setRow(row, 0, f"{' Keys for Running an Animation':<32}",QC,True,True,2)
                    row = 16
                self.table.setRow(row, 0, k, QL, True,True)  ## highlight
                self.table.setRow(row, 1, "  " + val, QL, False, True)                 
                row += 1
    
        self.table.setRow(row, 0,     f"{' Use Arrow Keys to Move Selected Sprites ':<15}",QC,True,True, 2)
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
                match help:
                    case 'Menus': 
                        QTimer.singleShot(10, self.canvas.showbiz.helpMaker.menuHelp) 
                        self.canvas.clear()
                    case 'Menu':  
                        self.storyHelp2 = StoryHelp2(self.canvas)      
                    case 'SpaceBar': 
                        help = 'space'                 
                if help in PlayKeys:  ## in Shared
                    QTimer.singleShot(10, partial(self.canvas.setKeys, help))
                self.table.close()  
            except:
                None    
        self.closeMenu()
       
    def closeMenu(self):
        self.helpButton.storyFlag = False  
        self.table.close()
        if self.switch != '':
            self.canvas.setKeys('N')
                
### ------------------- dotsHelpButtons -------------------- 
  
        



