
from functools          import partial

from PyQt6.QtCore       import QTimer
from PyQt6.QtWidgets    import QMenu

from dotsSideGig        import *
from dotsShared         import screens, PlayKeys
from dotsSideGig        import MsgBox, getVuCtr, getCtr
from dotsMapMaker       import MapMaker

from dotsAnimation      import *

demos = {  ## used by demo menu
    'bats':   'Original Batwings',
    'blue':   'Snakes Blue Background',
    'left':   'Right to Left Scrolling',  
    'right':  'Left to Right Scrolling',  
    'snakes': 'Snakes Scrolling Background',    
}

helpKeys = {
    'A':    'Add a Background', 
    'B':    'Add a Background', 
    'D':    'Display the Demo Menu',
    'H':    'Canvas Help Menu',
    'J':    'JSON File Viewer',
    'L':    'Load a play file', 
    'P':    'Switch to PathMaker', 
    'R':    'Display the Demo Menu',
    'S':    'Display the Screen Menu', 
}
    
MaxWidth = 1680  ##  position dock to screen bottom for max default display width
                 ##  on my mac with dock on left side, not on bottom
MaxScreens = ('1440','1536', '1102')  ## requires 1920X1280 display size

### ---------------------- dotsMenus ----------------------- 
''' classes: AnimationMenu, DemoMenu, HelpMenu, ScreenMenu, '''
### --------------------------------------------------------     
class AnimationMenu:  
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
        self.scene  = self.canvas.scene
        self.mapper = MapMaker(self.canvas)
    
        self.menu = None 

### --------------------------------------------------------
    ## shared with canvas thru context menu and with pixitem thru pixwidget
    def animeMenu(self, pos, where=''): 
        self.closeMenu()               
       
        for pix in self.scene.items():  ## too confusing
            if pix.type == 'widget':
                return
                    
        self.menu = QMenu(self.canvas)                   
        alst = sorted(AnimeList)
        
        ## basing pathlist on what's in the directory
        self.canvas.pathList = getPathList(True)  ## names only
        if len(self.canvas.pathList) == 0:
            MsgBox('getPathList: No Paths Found!', 5)
            return 
    
        alst.extend(['Random']) ## add random to lst
        
        self.menu.addAction('Animations and Paths')
        self.menu.addSeparator()   
        
        for anime in alst:
            action = self.menu.addAction(anime)
            action.triggered.connect(
                lambda chk, anime=anime: self.setAnimationTag(anime))
            
        self.menu.addSeparator()
        anime = 'Path Menu'  ## uses pathChooser in pathMaker
        action = self.menu.addAction(anime) 
        action.triggered.connect(
            lambda chk, anime=anime: self.setAnimationTag('Path Menu'))     
         
        self.menu.addSeparator()
        anime = 'Clear Tags'
        action = self.menu.addAction(anime)
        
        action.triggered.connect(
            lambda chk, anime=anime: self.setAnimationTag(anime))
        
        if where == 'pix':
            self.menu.move(pos) 
            self.menu.show()
        else:
            self.menu.exec(pos)  ## last cursor
         
    def closeMenu(self):   
        if self.menu:
            self.menu.close()
        self.menu = None    
    
    def setAnimationTag(self, tag):
        self.closeMenu()
        if self.mapper.tagSet and tag == 'Clear Tags':
            self.mapper.clearTagGroup()        
        elif tag == 'Path Menu':  ## use pathChooser from pathMaker 
            self.canvas.pathMaker.pathChooser('Path Menu') 
            return
        
        for pix in self.scene.selectedItems(): 
            if pix.type != 'pix':
                continue
            if tag == 'Clear Tags':
                pix.tag = ''
            else:
                pix.tag = tag
            pix.anime = None        ## set by play
            pix.setSelected(False)  ## when tagged
            
        if self.mapper.isMapSet(): 
            self.mapper.removeMap()  
                            
### --------------------------------------------------------     
class DemoMenu:  
### --------------------------------------------------------
    def __init__(self, parent, showbiz):
        super().__init__()  
   
        self.canvas = parent
        self.showbiz = showbiz
        
        self.dots  = self.canvas.dots
        self.scene = self.canvas.scene
     
        self.snakes = self.showbiz.snakes   
        self.bats   = self.showbiz.bats
        self.hats   = self.showbiz.hats  ## hats and bats
       
        self.demoMenu = None
        
### --------------------------------------------------------                     
    def openDemoMenu(self):
        self.closeDemoMenu()
        self.demoMenu = QMenu(self.canvas) 
        self.demoMenu.addAction('Demos Menu  '.rjust(23,' '))
        self.demoMenu.addSeparator()
        
        for key, demo in demos.items():            
            if self.dots.Vertical and key in ('left', 'right'):  ## wings follow pivots
                continue
            else:
                action = self.demoMenu.addAction(demo)
                self.demoMenu.addSeparator()
                action.triggered.connect(lambda chk, demo=demo: self.clicked(demo))   

        self.demoMenu.addAction("Use 'C' to Close Menu  ".rjust(27,' '))

        x, y = getVuCtr(self)
            
        if self.dots.Vertical:
            self.demoMenu.setFixedSize(220, 160)
            self.demoMenu.move(x-110, y-160)     
        else:
            self.demoMenu.setFixedSize(220, 220)
            self.demoMenu.move(x-110, y-100)     
              
        self.demoMenu.show()

    def clicked(self, demo):
        for key, value in demos.items():
            if value == demo:  ## singleshot needed for menu to clear
                QTimer.singleShot(25, partial(self.run, key))
                break
        self.closeDemoMenu()
        
    def closeDemoMenu(self):
        if self.demoMenu:
            self.demoMenu.close()           
        self.demoMenu = None
           
    def run(self, key):                          
        if key == 'bats':
            if self.bats.makeBats() == None:
                self.closeDemoMenu()   
        elif key == 'blue':
            self.runSnakes('blue') 
        elif key == 'snakes':
            self.canvas.bkgMaker.newTracker.clear()
            if self.dots.Vertical:   
                self.runSnakes('vertical') 
            else:
                self.runSnakes('left')              
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
            QTimer.singleShot(25, partial(self.snakes.makeSnakes, what))           
        elif self.openPlayFile != 'snakes' and len(self.scene.items()) > 0:
            MsgBox('The Screen Needs to be Cleared inorder to Run Snakes', 6, getCtr(-225,-175))
            return 
      
### --------------------------------------------------------     
class HelpMenu:  ## for canvas - one key commands
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()  
   
        self.showbiz = parent  ## all these are necessary to clear the screen     
        self.canvas  = self.showbiz.canvas
         
        self.helpMenu = self.showbiz.helpMenu
                 
### --------------------------------------------------------                     
    def openHelpMenu(self):
        self.closeHelpMenu()    
        self.helpMenu = QMenu(self.canvas)    
        self.helpMenu.addAction('Canvas KeyBoard Help'.rjust(27,' '))
        self.helpMenu.addSeparator()
        
        for help, demo in helpKeys.items():   
            action = self.helpMenu.addAction(f'{help:<3}- {demo:<14}')
            self.helpMenu.addSeparator()
            action.triggered.connect(lambda chk, help=help: self.clicked(help)) 
       
        self.helpMenu.addAction("Use 'H' to Close Menu  ".rjust(30,' '))
         
        x, y = getVuCtr(self)
        
        self.helpMenu.setFixedSize(250, 343)       
        self.helpMenu.move(x-125, y-170)  
        
        self.helpMenu.show()  
        self.showbiz.help = True
    
    def clicked(self, help):
        if help in PlayKeys:
            QTimer.singleShot(25, partial(self.showbiz.keysInPlay, help)) 

    def closeHelpMenu(self):   
        if self.helpMenu:
            self.helpMenu.close()
        self.helpMenu = None
        self.showbiz.help = False
                
 ### --------------------------------------------------------     
class ScreenMenu:  
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()  
   
        self.canvas = parent  ## all these are necessary to clear the screen        
        self.screenMenu = None
 
### --------------------------------------------------------                     
    def openScreenMenu(self):
        self.closeScreenMenu()
        self.screenMenu = QMenu(self.canvas)    
        self.screenMenu.addAction('Screen Formats'.rjust(22, ' '))
        self.screenMenu.addSeparator()
        
        for screen, desc in screens.items():
            action = self.screenMenu.addAction(f'{screen:>5} - {desc:>12}')
            self.screenMenu.addSeparator()
            action.triggered.connect(lambda chk, screen=screen: self.clicked(screen))

        self.screenMenu.addAction("Use 'C' to Close Menu ".rjust(24,' '))

        x, y = getVuCtr(self)

        self.screenMenu.setFixedSize(200, 345)
        self.screenMenu.move(x-100, y-170)
        
        self.screenMenu.show()
    
    def clicked(self, screen):
        for key in screens:
            if key == screen:  ## singleshot needed for menu to clear
                QTimer.singleShot(25, partial(self.displayChk, self.switchKey(key)))
                break      
        self.closeScreenMenu()  
                    
    def closeScreenMenu(self):   
        if self.screenMenu:
            self.screenMenu.close()
        self.screenMenu = None
              
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


                
