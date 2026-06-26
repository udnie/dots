
from dotsSideGig        import Grid, DemoAvailable

from dotsSideCar        import SideCar 
from dotsSideCar2       import SideCar2
 
from dotsShowTime       import ShowTime

from dotsHelpMenus      import HelpMenus
from dotsHelpMaker      import HelpMaker
from dotsHelpButtons    import ButtonHelp

from dotsShowRunner     import ShowRunner

### ---------------------- dotsShowBiz --------------------
''' single key functions to load and add both demo and non demo 
    items, play files, to the scene/canvas/storyboard '''    
### --------------------------------------------------------
class ShowBiz:  
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
        self.scene  = self.canvas.scene
        self.dots   = self.canvas.dots
        self.mapper = self.canvas.mapper
    
        self.pathMaker = self.canvas.pathMaker
        self.bkgMaker  = self.canvas.bkgMaker
    
        self.sideCar   = SideCar(self.canvas)  
        self.sideCar2  = SideCar2(self.canvas) 
                 
        self.demoAvailable = DemoAvailable()

        self.showtime   = ShowTime(self.canvas)
        self.showRunner = ShowRunner(self.canvas, self)
   
        self.helpMaker   = HelpMaker(self.canvas)
        self.helpMenus   = HelpMenus(self.canvas)  ## can be demo or screens
        self.helpButtons = ButtonHelp(self.canvas)
        
        self.grid = Grid(self.canvas)
        
        self.locks = 0
        self.tableView = None 

### --------------------------------------------------------
    ## do these first
### -------------------------------------------------------- 
    def keysInPlay(self, key):
        if key == 'X':  ## from help menus
            self.canvas.exit()    

        if key in ('G', 'K', 'R'):
            match key:
                case'G':
                    self.grid.toggleGrid()                 
                case'K':  
                    self.canvas.keysPanel.toggleKeysMenu()
                case'R':    
                    if self.canvas.control != '' or self.canvas.animationRunning:  ## something's running
                        return
                    else:
                        self.showRunner.runThese() 
                                  
        elif len(self.scene.items()) > 0:   
### --------------------------------------------------------    
    ## animations running
### --------------------------------------------------------               
            if key in ('P', 'S', 'space') and self.canvas.control != '' or self.canvas.animationRunning: 
                match key:
                    case 'P': 
                        self.mapper.tagsAndPaths.togglePaths()                                                                                    
                    case 'S':
                        self.showtime.stop()                                                                                               
                    case 'space': ## pause/resume
                        self.sideCar.pause() 
                                                  
### --------------------------------------------------------    
    ## no animations running - from storyboard menu
### --------------------------------------------------------  
            elif self.canvas.control == '' or not self.canvas.animationRunning:                     
                if key in ('A', 'D', 'I', 'J', 'L', 'M', 'N', 'O', 'S','T', 'U', 'V', 'W', 'del'):          
                    match key:
                        case 'A':            
                            self.sideCar2.unSelect() if self.scene.selectedItems() else \
                                self.sideCar2.selectAll()    
                        case 'D'|'del':
                            if self.scene.selectedItems():
                                self.sideCar2.deleteSelected() 
                            elif len(self.scene.items()) > 0:
                                self.sideCar2.sendPixKeys('del')   
                        case 'I':                 
                            self.sideCar2.aye()            
                        case 'J':                   ## view a play file's records
                            if dlist := self.showRunner.openPlay(self.canvas.openPlayFile):  
                                self.showRunner.makeTableView(dlist, 'view')   
                        case 'L':                   ## load a .play file
                            self.showRunner.loadPlay()         
                        case 'M':
                            self.mapper.toggleMap() if self.scene.selectedItems() or self.sideCar.hasHiddenPix() \
                                else self.helpButtons.openMenus()  ## shows storyboard if nothing mapped
                        case 'N':
                            self.helpMaker.menuHelp()  ## called from help menus to avoid 'M' conflicts
                        case 'O':
                            self.sideCar.clearWidgets()  
                            self.sideCar.toggleOutlines()   ## run from shadowWorks                    
                        case 'S':
                            self.showtime.savePlay()
                        case 'T':
                            self.mapper.toggleSelectedSceneItems()    
                        case 'U':                           ## unselect for storyBoard
                            self.sideCar2.unSelect()            
                        case 'V':
                            if self.canvas.videoPlayer != None:     ## delete video
                                self.canvas.videoPlayer.ask2deleteVideo() 
                        case 'W':              
                            self.sideCar.clearWidgets() 
                            
### --------------------------------------------------------                      
    ## canvas single key commands - no screenitems
### --------------------------------------------------------  
        elif len(self.scene.items()) == 0:    
            if self.demoAvailable:  ## does the demo directory exist 
                self.canvas.clear()  
            if key in ('A', 'D', 'J', 'L', 'M', 'P', 'S'):                 
                match key:
                    case 'A': 
                        self.bkgMaker.openBkgFiles() 
                    case 'D':                   
                        if self.demoAvailable:  ## displays demo menu in canvas
                            self.helpMenus.setMenu(key)
                    case 'J':                   ## view a play file's records
                        self.showRunner.loadPlay('table')  
                    case 'L':                   ## load a play file
                        self.showRunner.loadPlay()  
                    case 'M':
                        self.helpMaker.menuHelp()       ## show help menus(all)
                    case 'P':  
                        self.pathMaker.initPathMaker()  ## switch to pathmaker
                    case 'S':   
                        self.helpMenus.setMenu(key)     ## displays screen menu in canvas
                     
### ---------------------- dotsShowBiz --------------------


        
