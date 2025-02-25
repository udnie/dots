
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

        elif key == 'G':
            self.grid.toggleGrid()           
                     
        elif key == 'K':  
            self.sideCar.toggleKeysMenu()  ## keysMenu for storyboard and pathMaker 
            
        elif key == 'R':    
            if self.canvas.control != '' or self.canvas.animation == True:  ## something's running
                return
            else:
                self.showRunner.runThese() 
                    
        elif len(self.scene.items()) > 0:   
### --------------------------------------------------------    
    ## animations running
### --------------------------------------------------------             
            if self.canvas.control != '' or self.canvas.animation == True:    
                if key == 'P': 
                    self.mapper.tagsAndPaths.togglePaths() 
                                                                                                    
                elif key == 'S':
                    self.showtime.stop() 
                                                                                                                
                elif key == 'space': ## pause/resume
                    self.sideCar.pause() 
                                                                    
### --------------------------------------------------------    
    ## no animations running
### --------------------------------------------------------  
            elif self.canvas.control == '' or self.canvas.animation == False:  
                if key == 'A':  
                    self.sideCar2.selectAll()
                                  
                elif key == 'D':
                    self.sideCar2.deleteSelected()
                                 
                elif key == 'J':  ## view the layout of the currently opened play file 
                    if dlist := self.showRunner.openPlay(self.canvas.openPlayFile):  
                        self.showRunner.makeTableView(dlist, 'view') 
                        
                elif key == 'L':  ## uses QFileDialog to open a .play file
                    self.showRunner.loadPlay()         
                    
                elif key == 'M':
                    if self.scene.selectedItems() or self.sideCar.hasHiddenPix():
                        self.mapper.toggleMap()  
                    else:
                        self.helpButtons.openMenus()  ## shows storyboard if nothing mapped
                    
                elif key == 'N':
                    self.helpMaker.menuHelp()  ## called from help menus - with no 'M' conflicts
                
                elif key == 'O':
                    self.sideCar.clearWidgets()  
                    self.sideCar.toggleOutlines()  ## run from shadowWorks
                                        
                elif key == 'S':
                    self.showtime.savePlay()
                      
                elif key == 'U':  ## unselect for storyBoard
                    self.sideCar2.unSelect()
                                
                elif key == 'V' and self.canvas.videoPlayer != None:  ## pop-up
                    self.sideCar.addVideoWidget() \
                        if self.canvas.videoPlayer.widget == None else \
                            self.sideCar.closeVideoWidget()
                              
                elif key == 'W':              
                    self.sideCar.clearWidgets() 
    
### --------------------------------------------------------                      
    ## canvas single key commands
### --------------------------------------------------------  
        elif len(self.scene.items()) == 0: 
                
            if self.demoAvailable:  ## always clear unless deleted
                self.canvas.clear()
                
            if key == 'A': 
                self.bkgMaker.openBkgFiles() 
        
            elif key == 'D':   ## runs demo menu in canvas
                if self.demoAvailable:   
                    self.helpMenus.setMenu(key)

            elif key == 'J':  ##  use QFileDialog to launch a .play file viewer 
                self.showRunner.loadPlay('table')  
                
            elif key == 'L':  ## use QFileDialog to open and display a .play file
                self.showRunner.loadPlay()  
                
            elif key == 'M':
                self.helpMaker.menuHelp()  ## show help menus
                
            elif key == 'P':  
                self.pathMaker.initPathMaker() 
                
            elif key == 'S':   
                self.helpMenus.setMenu(key)  ## screen menu
                     
### ---------------------- dotsShowBiz --------------------


        
