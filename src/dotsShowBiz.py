
import json
import time
import asyncio
import os      

from functools          import partial

from PyQt6.QtCore       import QTimer

from dotsShared         import common, paths
from dotsPixItem        import PixItem
from dotsBkgMaker       import *
from dotsFrameAndFlats  import Frame

from dotsSideGig        import *
from dotsSideCar        import SideCar 
from dotsSideCar2       import SideCar2

from dotsShowFiles      import ShowFiles   
from dotsShowTime       import ShowTime

from dotsTableMaker     import TableView
from dotsWings          import Wings

from dotsHelpMenus      import HelpMenus
from dotsHelpMaker      import HelpMaker
from dotsHelpButtons    import ButtonHelp

### ---------------------- dotsShowBiz --------------------
''' functions to load and add both demo and non demo items,
            play files, to the scene/canvas/storyboard '''    
### --------------------------------------------------------
class ShowBiz:  
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
        self.scene  = self.canvas.scene
        self.dots   = self.canvas.dots
        self.mapper = self.canvas.mapper
        
        self.sideCar   = SideCar(self.canvas)  
        self.sideCar2  = SideCar2(self.canvas) 
               
        self.pathMaker = self.canvas.pathMaker
        self.bkgMaker  = self.canvas.bkgMaker
            
        self.demoAvailable = DemoAvailable()

        self.showtime  = ShowTime(self.canvas)
        self.showFiles = ShowFiles(self.canvas) 
   
        self.helpMaker   = HelpMaker(self.canvas)
        self.helpMenus   = HelpMenus(self.canvas)
        self.helpButtons = ButtonHelp(self.canvas)
          
        self.locks = 0
        self.tableView = None 
              
### --------------------------------------------------------    
    def keysInPlay(self, key):
        if key == 'X':  ## from help menus
            self.canvas.exit()

        elif key == 'C':
            self.canvas.clear() 
    
        elif self.canvas.pathMakerOn == False:  
                                     
            if len(self.scene.items()) > 0:  ## storyboard single key commands
                
                if self.canvas.control != '' or self.canvas.animation == True:  ## animation running
                    
                    if key == 'P': 
                        self.mapper.tagsAndPaths.togglePaths() 
                                                                                                       
                    elif key == 'S':
                        self.showtime.stop() 
                                        
                    elif key == 'space': ## pause/resume
                        self.canvas.sideCar.pause()
                  
                elif self.canvas.control == '':  ## no animations running
        
                    if key == 'A':  
                        self.sideCar2.selectAll()
               
                    elif key == 'D':
                        self.sideCar2.deleteSelected()
                    
                    elif key == 'J':  ## view the layout of the currently opened play file 
                        if dlist := self.openPlay(self.canvas.openPlayFile):  
                            self.makeTableView(dlist, 'view') 
                          
                    elif key == 'L':  ## uses QFileDialog to open a .play file
                        self.loadPlay()         
                      
                    elif key == 'M':
                        if self.scene.selectedItems() or self.canvas.sideCar.hasHiddenPix():
                            self.mapper.toggleMap()  
                        else:
                            self.helpButtons.openMenus()  ## shows storyboard if nothing mapped
                      
                    elif key == 'N':
                        self.helpMaker.menuHelp()  ## help menus - no 'M' conflicts
                    
                    elif key == 'O':
                        self.sideCar.clearWidgets()  
                        self.sideCar.toggleOutlines()   
                            
                    elif key == 'R':    
                        if self.canvas.control != '':  ## something's running
                            return
                        else:
                            self.runThese()    
                       
                    elif key == 'S':
                        self.showtime.savePlay()
                                           
                    elif key == 'U':
                        self.canvas.unSelect()
       
                    elif key == 'W':
                        self.canvas.sideCar.clearWidgets()
                                                                   
            ## single key commands continued - nothing on screen
            elif len(self.scene.items()) == 0: 
                
                if self.demoAvailable:  ## always clear unless deleted
                    self.canvas.clear()
                    
                if key == 'A':
                    self.bkgMaker.openBkgFiles() 
                    
                elif key == 'D':   ## runs demo menu in canvas
                    if self.demoAvailable:   
                        self.helpMenus.setMenu(key)
    
                elif key == 'J':  ##  use QFileDialog to launch a .play file viewer 
                    self.loadPlay('table')  
                    
                elif key == 'L':  ## use QFileDialog to open and display a .play file
                    self.loadPlay()  
                    
                elif key == 'M':
                    self.helpMaker.menuHelp()  ## show help menus
                    
                elif key == 'P':  
                    self.pathMaker.initPathMaker() 
                    
                elif key == 'S':   
                    self.helpMenus.setMenu(key)  ## screen menu
                              
        elif self.canvas.pathMakerOn == True:    
            if key == 'M':
                self.helpButtons.openMenus()  ## shows storyboard if nothing mapped
       
### --------------------------------------------------------        
    def runThese(self):   
        if self.demoAvailable and self.canvas.openPlayFile in ('snakes', 'bats', 'hats'):
            self.helpMenus.demoMenu.runThese() 
        else:
            self.showtime.run()
   
    def makeTableView(self, dlist, src=''):  ## called if missing files     
        if self.tableView != None:
            self.tableView.bye()                      
        self.tableView = TableView(self, dlist, src) 
                                                            
    def openPlay(self, file):    
        try:
            with open(file, 'r') as fp: 
                dlist = json.load(fp)                 
        except IOError:
            MsgBox('openPlay: Error loading ' + file, 5)
            return '' 
        return dlist                                                            
                                                                                                                                                                                                                          
### --------------------------------------------------------                            
    def loadPlay(self, src=''):   
        if self.canvas.pathMakerOn:  ## use pathChooser - was loader once but now you can see them
            return
        Q = QFileDialog()
        Q.Option.DontUseNativeDialog
        which = 'Files (*.play *.tmp)' if src == 'table' else  'Files (*.play *.tmp)'  
        file, _ = Q.getOpenFileName(self.canvas, 
            'Choose a file to open', paths['playPath'], which, None)
        Q.accept()           
        if file:
            dlist = []
            self.canvas.openPlayFile = file  ## good idea
            try:       
                dlist = self.openPlay(file) 
            except IOError:
                self.canvas.openPlayFile = ''
                MsgBox('loadPlay ' + file + 'Not Found')              
            if len(dlist) > 0: 
                self.makeTableView(dlist, src)  ## display any missing files or what's there if 'table'
                if src == 'table':  ## show tableview when run from canvas when typing 'j'
                    return  
                self.updateStoryBoard(dlist) 
            else:
                return
              
### -------------------------------------------------------- 
    def updateStoryBoard(self, dlist):  ## turn the contents of the .play file into scene items            
        self.mapper.clearMap() 
        self.locks = 0
        self.canvas.pixCount = self.mapper.toFront(0) 
        self.canvas.bkgMaker.newTracker.clear()        
        ## number of pixitems, backgrounds zval, number of shadows        
        kix, ns, bkgz = 0, 0, common['bkgZ'] 
        lnn = len(dlist)  ## decrement top to bottom - preserves front to back relationships
        lnn = lnn + self.mapper.toFront(0) + 100  ## start at the top  for sprites and frames                               
      
        for tmp in dlist:                                 
            if self.showFiles.fileNotFound(tmp):  ## the reason missing files don't get saved - works with dictionaries
                continue                
     
            if tmp['type'] == 'frame' or 'frame' in tmp['fileName']:        
                frame = Frame(paths['spritePath'] + tmp['fileName'], self.canvas, lnn)
                self.showFiles.addPixToScene(frame, tmp, lnn)  ## finish unpacking tmp                 
                lnn -= 1 
  
            elif tmp['type'] == 'pix' and 'bat' not in tmp['fileName']:
                kix += 1  ## counts pixitems               
                pix = PixItem( paths['spritePath'] + tmp['fileName'], self.canvas.pixCount, \
                    0, 0, self.canvas) 
                self.showFiles.addPixToScene(pix, tmp, lnn)  ## finish unpacking tmp 
                lnn -= 1            
                ## found a shadow - see if shadows are turned on, yes == '', no == 'pass'
                if pix.shadowMaker.isActive == True and 'scalor' in tmp.keys(): 
                    ns += 1                        
            
            elif 'bat' in tmp['fileName']:  ## make a bat - not from demoMenu, adds self to scene
                Wings(self.canvas, tmp['x'], tmp['y'], tmp['tag'])  ## tag holds animation/path
                lnn -= 1  
                continue        
                   
            ## can be more than one background or flat                    
            elif tmp['type'] in ('bkg', 'flat'):                          
                ## a flat does not rely on a bkg.file once it's saved to a play.file
                if tmp['type'] == 'flat' and QColor().isValidColor(tmp['color']):
                    pix = Flat(tmp['color'], self.bkgMaker, bkgz)  
                    self.showFiles.addPixToScene(pix, tmp, bkgz )  
                              
                elif tmp['type'] == 'bkg':    
                    pix = BkgItem(paths['bkgPath'] + tmp['fileName'], self.canvas, bkgz)
                    self.showFiles.addPixToScene(pix, tmp, bkgz )  
             
                pix.bkgMaker.lockBkg(pix)                                         
                bkgz -= 1     
            del tmp              
        ## end for loop   
                         
        del dlist
        self.cleanup(ns, kix)  ## add shadows
  
### --------------------------------------------------------                         
    def cleanup(self, ns, kix):
        fileName = os.path.basename(self.canvas.openPlayFile) 
        if 'play' in fileName:  ## could be something else
            self.canvas.showWorks.enablePlay() 
            if ns == 0 and self.locks == 0:
                self.dots.statusBar.showMessage(f"{fileName} - Number of Pixitems: {kix}")
            elif ns > 0:  ## there must be shadows
                QTimer.singleShot(200, self.addShadows)
                t = int(1 + (ns * .25))
                if self.showFiles.errorOnShadows == True:  ## will try and add if shadowMaker is on
                    MsgBox('Error Loading some Shadows...', 5)
                    self.showFiles.errorOnShadows = False  ## may need it again
                else:
                    MsgBox('Adding Shadows, please wait...', t)              
            elif self.locks > 0:
                MsgBox('Some screen items are locked', 5)  ## seconds
                self.mapper.toggleTagItems('all')                                                      
        QTimer.singleShot(17000, partial(self.dots.statusBar.showMessage, fileName)) 

### --------------------------------------------------------                                                  
    def addShadows(self):  ## add shadows after adding pixitems     
        tasks = []         
        start = time.time()
        loop  = asyncio.new_event_loop() 
        for pix in self.scene.items():  ## thanks to a dev community post - it took some work to find a useful example
            if pix.type == 'pix' and pix.shadowMaker != None and pix.shadow != None:
                    pix.fileName = paths['spritePath'] + pix.fileName      
                    tasks.append(loop.create_task(pix.shadowMaker.restoreShadow()))        
        if len(tasks) > 0:
            loop.run_until_complete(asyncio.wait(tasks))        
        loop.close()              
        self.sideCar.showOutlines()  ## turns them on      
        QTimer.singleShot(2000, self.sideCar.hideOutlines)          
        str = f' Number of Shadows: {len(tasks)}   seconds: {time.time() - start:.2f}'
        self.dots.statusBar.showMessage(str, 10000)   

### ---------------------- dotsShowBiz --------------------


        
