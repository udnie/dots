
from functools          import partial

from PyQt6.QtCore       import QTimer
from PyQt6.QtWidgets    import QMenu

from dotsSideGig        import *
from dotsShared         import screens
from dotsSideGig        import MsgBox, getCtr
from dotsMapMaker       import MapMaker

from dotsAnimation      import *

demos = {  ## used by demo menu
    'bats':   'Original Batwings',
    'blue':   'Snakes Blue Background',
    'left':   'Right to Left Scrolling',  
    'right':  'Left to Right Scrolling',  
    'snakes': 'Snakes Scrolling Background',    
}

MaxWidth = 1680  ##  position dock to screen bottom for max default display width
                 ##  on my mac with dock on left side, not on bottom
MaxScreens = ('1440','1536', '1102')  ## requires 1920X1280 display size

### ---------------------- dotsMenus ----------------------- 
''' classes: AnimationMenu, DemoMenu, ScreenMenu, '''
### --------------------------------------------------------     
class AnimationMenu:  
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
        self.dots   = self.canvas.dots
        self.scene  = self.canvas.scene
        self.mapper = MapMaker(self.canvas)
    
        self.menu      = None 

### --------------------------------------------------------
    def animeMenu(self, pos, where=''): ## shared with canvas thru context menu
        self.closeMenu()                ## and with pixitem thru pixwidget
         
        self.menu = QMenu(self.canvas)                   
        alst = sorted(AnimeList)
        
        ## basing pathlist on what's in the directory
        self.canvas.pathList = getPathList(True)  ## names only
        
        rlst = sorted(self.canvas.pathList)     
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
            self.menu.exec(pos)
         
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
    def __init__(self, parent, sideShow):
        super().__init__()  
   
        self.canvas = parent
        self.sideShow = sideShow
        
        self.dots   = self.canvas.dots
        self.scene  = self.canvas.scene
        self.view   = self.canvas.view 
     
        self.snakes   = self.sideShow.snakes   
        self.bats     = self.sideShow.bats
        self.abstract = self.sideShow.abstract  ## hats and bats
       
        self.demoMenu = None
                       
    def openDemoMenu(self):
        self.closeDemoMenu()
        self.demoMenu = QMenu(self.canvas) 
        self.demoMenu.addAction('Demos Menu'.rjust(20,' '))
        self.demoMenu.addSeparator()
        for key, demo in demos.items():            
  
            if self.dots.Vertical and key in ('left', 'right'):
                continue
            else:
                action = self.demoMenu.addAction(demo)
                self.demoMenu.addSeparator()
                action.triggered.connect(lambda chk, demo=demo: self.clicked(demo))         
           
        if self.dots.Vertical:
            self.demoMenu.setFixedSize(220, 130)
            self.demoMenu.move(getCtr(-130, -255))     
        else:
            self.demoMenu.setFixedSize(220, 190)
            self.demoMenu.move(getCtr(-130, -225))   
        self.demoMenu.show()

    def clicked(self, demo):
        for key, value in demos.items():
            if value == demo:  ## singleshot needed for menu to clear
                QTimer.singleShot(200, partial(self.run, key))
                break
        self.closeDemoMenu()
        
    def closeDemoMenu(self):
        if self.demoMenu:
            self.demoMenu.close()           
        self.demoMenu = None
           
    def run(self, key):                         
        if key == 'bats':
            self.bats.makeBats()
        elif key == 'blue':
            self.runSnakes('blue') 
        elif key == 'snakes':
            self.canvas.bkgMaker.trackers = []
            if self.dots.Vertical:   
                self.runSnakes('vertical') 
            else:
                self.runSnakes('left')              
        elif key in ('left', 'right'):
            if self.dots.Vertical:     
                MsgBox('Not Implemented for Vertical Format')
                return            
            self.canvas.bkgMaker.trackers = []
            if key == 'left':  ## direction of travel
                self.abstract.makeAbstracts('left')  ## right to left 
            else: 
                self.abstract.makeAbstracts('right') ## left to right   

    def runSnakes(self, what): 
        if what in ('blue', 'snakes'): 
            self.snakes.delSnakes()    
        if what != '':
            QTimer.singleShot(100, partial(self.snakes.makeSnakes, what))           
        elif self.openPlayFile != 'snakes' and len(self.scene.items()) > 0:
            MsgBox('The Screen Needs to be Cleared inorder to Run Snakes', 6, getCtr(-225,-175))
            return 
          
 ### --------------------------------------------------------     
class ScreenMenu:  
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()  
   
        self.canvas = parent  ## all these are necessary to clear the screen
        self.dots   = self.canvas.dots
        self.scene  = self.canvas.scene
        self.view   = self.canvas.view  
        
        self.screenMenu = None
                     
    def openScreenMenu(self):
        self.closeScreenMenu()
        self.screenMenu = QMenu(self.canvas)    
        self.screenMenu.addAction(' Screen Formats')
        self.screenMenu.addSeparator()
        for screen in screens.values():
            action = self.screenMenu.addAction(screen)
            self.screenMenu.addSeparator()
            action.triggered.connect(lambda chk, screen=screen: self.clicked(screen)) 
        self.screenMenu.move(getCtr(-85,-350)) 
        self.screenMenu.setFixedSize(150, 315)
        self.screenMenu.show()
    
    def clicked(self, screen):
        for key, value in screens.items():
            if value == screen:  ## singleshot needed for menu to clear
                QTimer.singleShot(200, partial(self.displayChk, self.switchKey(key)))
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


                
