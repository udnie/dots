
from functools          import partial

from PyQt6.QtCore       import QTimer
from PyQt6.QtGui        import QGuiApplication

from dotsShared         import screens
from dotsSideGig        import MsgBox, getVuCtr, getCtr

from dotsTableModel     import TableWidgetSetUp, QL, QC

from dotsSnakes         import Snakes
from dotsBatsAndHats    import Bats, Hats

demoKeys = {  
    'bats':   'Original BatWings',
    'blue':   'Snakes Blue Background',
    'left':   'Right to Left Scrolling',  
    'right':  'Left to Right Scrolling',  
    'snakes': 'Snakes Scrolling Background',    
}

MaxWidth = 1680  ##  position dock to screen bottom for max default display width
                 ##  on my mac with dock on left side, not on bottom
MaxScreens = ('1440','1536', '1102')  ## requires 1920X1280 display size

### ---------------------- dotsMenus ----------------------- 
''' classes: HelpMenus, DemoHelp, ScreenHelp '''
### --------------------------------------------------------
    ## Canvas and StoryBoard Menus in helpButtons
    ## Demos, Screens Menus in helpMenus
    ## Sprites, Background and Shadow Menus in helpMonkey
    ## Widgets for Pixitems, Backgrounds., in helpMaker
    ## Animation Menu in pixWork
    ## Frames and Flats Menu in frames and flats
    ## Matte Menu in bkgMatte    
    ## PathMaker Menu in pathWorks
### --------------------------------------------------------    
class HelpMenus:  ## demos and snakes
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent

    def setMenu(self, key):
        if key == 'D':
            self.demoMenu = DemoHelp(self.canvas) 
        elif key == 'S':
             self.screenMenu = ScreenHelp(self.canvas)  ## in screens 
          
### --------------------------------------------------------     
class DemoHelp:  
### --------------------------------------------------------
    def __init__(self, parent, off=0, str=''):
        super().__init__()  
   
        self.canvas = parent
        self.switch = str

        self.dots  = self.canvas.dots
        self.scene = self.canvas.scene
        
        self.snakes = Snakes(self.canvas)
        self.bats   = Bats(self.canvas)
        self.hats   = Hats(self.canvas)
    
### --------------------------------------------------------   
        rows = len(demoKeys)
        if self.dots.Vertical: rows = len(demoKeys)-2

        self.table = TableWidgetSetUp(0, 215, rows+3)
        self.table.itemClicked.connect(self.clicked)   
        
        self.table.setRow(0, 0, f'{"Demos Menu":<13}','',True,True,2)

        row = 1; self.fix = [] 
        for k, val in demoKeys.items():
            if self.dots.Vertical and k in ('left', 'right'):  ## wings follow pivots
                continue
            else:
                self.fix.append(k)
                self.table.setRow(row, 0, "  " + val,'',False,True, 2)
            row += 1
   
        self.table.setRow(row, 0,f'{"Select From Above":<23}',QL,True,True, 2)
        self.table.setRow(row + 1, 0,f'{"Click Here to Close Menu":<27}','',True,True, 2)
    
        x, y = getVuCtr(self.canvas)  
        if off != 0: x += off
            
        if self.dots.Vertical:
            self.table.setFixedSize(222, 189) 
        else:
            self.table.setFixedSize(222, 246)
        self.table.move(x-110, y-100)     
              
        self.table.show()

    def clicked(self):
        if self.switch == '':
            try:
                p = self.table.currentRow() - 1 
                if p+1 <= len(demoKeys): 
                    QTimer.singleShot(25, partial(self.run, self.fix[p]))
            except:
                None
        self.closeMenu()
        
    def closeMenu(self):
        self.table.close()
        if self.switch !='':
            self.canvas.setKeys('M')
    
    def run(self, key):                           
        if key == 'blue':
            self.runSnakes('blue') 
            
        elif key == 'snakes':
            self.canvas.bkgMaker.newTracker.clear()
            if self.dots.Vertical:   
                self.runSnakes('vertical') 
            else:
                self.runSnakes('left')   
                    
        elif key == 'bats':
            if self.bats.makeBats() == None:
                self.closeMenu() 
           
        elif key in ('left', 'right'):
            if self.dots.Vertical:     
                MsgBox('Not Implemented for Vertical Format')
                return            
            self.canvas.bkgMaker.newTracker.clear()
            if key == 'left':  ## direction of travel
                self.hats.makeHatsDemo('left')  ## right to left 
            else: 
                self.hats.makeHatsDemo('right') ## left to right   
      
    def runSnakes(self, what): 
        if what in ('blue', 'snakes'): 
            self.snakes.delSnakes()   
        if what != '': 
            self.snakes.makeSnakes(what)
        elif self.openPlayFile != 'snakes' and len(self.scene.items()) > 0:
            MsgBox('The Screen Needs to be Cleared to Run Snakes', 6, getCtr(-225,-175))
            return
    
    def runThese(self):
        if self.canvas.openPlayFile == 'snakes' and self.snakes.what != '':
            self.snakes.rerun(self.snakes.what)  
            
        elif self.canvas.openPlayFile == 'hats' and self.hats.direction != '':
            self.hats.rerunAbstract(self.hats.direction)
              
        elif self.canvas.openPlayFile == 'bats':
            self.bats.rerun()

### --------------------------------------------------------     
class ScreenHelp:  
### -------------------------------------------------------- 
    def __init__(self, parent, off=0, str=''):
        super().__init__()  
   
        self.canvas = parent  
        self.switch = str
       
  ### --------------------------------------------------------   
        self.table = TableWidgetSetUp(60, 95, 60, len(screens)+3)
        self.table.itemClicked.connect(self.clicked)   
        
        width, height = 222, 396
        self.table.setFixedSize(width, height)
        
        self.table.setRow(0, 0, f'{"Screen Formats":<14}','',True,True,3)
        row = 1
        for k , val in screens.items():
            self.table.setRow(row, 0, f'{k}'.rjust(7),'',True, True)
            self.table.setRow(row, 1,  f'{val[0]}'.rjust(13), '','', True)
            self.table.setRow(row, 2,  f'{val[1]}','',True, True)
            row += 1
      
        self.table.setRow(row, 0,f'{"Select From Above":<18}',QL,True,True, 3)
        self.table.setRow(row + 1, 0,f'{"Click Here to Close Menu":<22}','',True,True, 3)

        x, y = getVuCtr(self.canvas)  
        if off != 0: x += off
        
        self.table.move(int(x - width /2), int(y - height /2))
        self.table.show()
    
    def clicked(self):
        if self.switch == '':
            try:
                help = self.table.item(self.table.currentRow(), 0).text().strip()
                if help in screens: 
                    QTimer.singleShot(25, partial(self.displayChk, self.switchKey(help)))
            except:
                None
        self.closeMenu()     
 
    def closeMenu(self):
        self.table.close()
        if self.switch !='':
            self.canvas.setKeys('M')
      
    def switchKey(self, key):           
        if self.displayChk(key) == True:
            self.canvas.clear()   
            self.canvas.dots.switch(key) 
        else:
            return
    
    def displayChk(self, key):  ## switch screen format
        p = QGuiApplication.primaryScreen().availableGeometry()
        if key in MaxScreens and p.width() < MaxWidth:  ## current screen width < 1680
            self.exceedsMsg() 
            return False
        else:
            return True            
        
    def exceedsMsg(self):  ## in storyBoard on start       ## use getCtr with MsgBox
        MsgBox('Selected Format Exceeds Current Display Size', 8, getCtr(-200,-145)) 
     
### ---------------------- dotsMenus -----------------------              


                
