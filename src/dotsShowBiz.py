
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
        self.helpMenus   = HelpMenus(self.canvas)
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
                    if self.canvas.control != '' or self.canvas.animation == True:  ## something's running
                        return
                    else:
                        self.showRunner.runThese() 
                                  
        elif len(self.scene.items()) > 0:   
### --------------------------------------------------------    
    ## animations running
### --------------------------------------------------------      
            if self.canvas.control != '' or self.canvas.animation == True:       
                if key in ('P', 'S', 'space'): 
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
            elif self.canvas.control == '' or self.canvas.animation == False:                     
                if key in ('A', 'D', 'J', 'L', 'M', 'N', 'O', 'S', 'U', 'V', 'W'):           
                    match key:
                        case 'A':            
                            self.sideCar2.selectAll()               
                        case 'D':
                            self.sideCar2.deleteSelected()              
                        case 'J':                   ## view a play file's records
                            if dlist := self.showRunner.openPlay(self.canvas.openPlayFile):  
                                self.showRunner.makeTableView(dlist, 'view')   
                        case 'L':                   ## load a .play file
                            self.showRunner.loadPlay()         
                        case 'M':
                            if self.scene.selectedItems() or self.sideCar.hasHiddenPix():
                                self.mapper.toggleMap()  
                            else:
                                self.helpButtons.openMenus()  ## shows storyboard if nothing mapped
                        case 'N':
                            self.helpMaker.menuHelp()  ## called from help menus to avoid 'M' conflicts
                        case 'O':
                            self.sideCar.clearWidgets()  
                            self.sideCar.toggleOutlines()   ## run from shadowWorks                    
                        case 'S':
                            self.showtime.savePlay()
                        case 'U':                           ## unselect for storyBoard
                            self.sideCar2.unSelect()            
                        case 'V':
                            if self.canvas.videoPlayer != None:     ## the video widget
                                self.sideCar.addVideoWidget() \
                                    if self.canvas.videoPlayer.widget == None else \
                                        self.sideCar.closeVideoWidget()
                        case 'W':              
                            self.sideCar.clearWidgets() 
    
### --------------------------------------------------------                      
    ## canvas single key commands - no screenitems
### --------------------------------------------------------  
        elif len(self.scene.items()) == 0:      
            if self.demoAvailable:  ## always clear unless deleted
                self.canvas.clear()  
            if key in ('A', 'D', 'J', 'L', 'M', 'P', 'S'):                 
                match key:
                    case 'A': 
                        self.bkgMaker.openBkgFiles() 
                    case 'D':                   ## runs demo menu in canvas
                        if self.demoAvailable:   
                            self.helpMenus.setMenu(key)
                    case 'J':                   ## view a play file's records
                        self.showRunner.loadPlay('table')  
                    case 'L':                   ## load a play file
                        self.showRunner.loadPlay()  
                    case 'M':
                        self.helpMaker.menuHelp()       ## show help menus
                    case 'P':  
                        self.pathMaker.initPathMaker()  ## switch tp pathmaker
                    case 'S':   
                        self.helpMenus.setMenu(key)     ## screen menu
                     
### ---------------------- dotsShowBiz --------------------


        
