
import json
import time
import asyncio
import os      

from functools          import partial

from PyQt6.QtCore       import QTimer, QPointF

from dotsShared         import common, paths, PlayKeys
from dotsPixItem        import PixItem
from dotsBkgMaker       import *

from dotsShowTime       import ShowTime
from dotsSideGig        import *
from dotsSideCar        import SideCar 
from dotsShowFiles      import ShowFiles   
from dotsPixFrameWorks  import Frame
from dotsTableMaker     import TableView

from dotsMenus          import DemoMenu, HelpMenu, ScreenMenu
from dotsSnakes         import Snakes
from dotsBatsAndHats    import *
from dotsWings          import Wings

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
        self.pathMaker = self.canvas.pathMaker
        self.bkgMaker  = self.canvas.bkgMaker
            
        self.demoAvailable = DemoAvailable()
       
        if self.demoAvailable:
            self.bats      = Bats(self.canvas)     
            self.snakes    = Snakes(self.canvas)     
            self.hats      = Hats(self.canvas) 
            self.demoMenu  = DemoMenu(self.canvas, self)
 
        self.showtime   = ShowTime(self.canvas)
        self.screenMenu = ScreenMenu(self.canvas)  ## in screens
        self.showFiles  = ShowFiles(self.canvas) 
        
        self.helpMenu   = None
        self.helpMenu   = HelpMenu(self.canvas, self)
        self.help = True
           
        self.locks = 0
        self.tableView = None 
     
           
### --------------------------------------------------------    
    def keysInPlay(self, key):
        if self.canvas.pathMakerOn == False:                
            if len(self.scene.items()) > 0:  ## stuff on screen
                if key == 'P':  ## always
                    self.mapper.tagsAndPaths.togglePaths()                               
                elif key == 'R':    
                    if self.canvas.control != '':
                        return
                    else:
                        self.runThese()                                        
                elif key == 'S':
                    if self.canvas.control != '':
                        self.showtime.stop() 
                    else:
                        self.showtime.savePlay()
                elif key == 'J':  ## view the layout of the currently opened play file 
                    if self.canvas.control == '':
                        dlist = self.openPlay(self.canvas.openPlayFile)  
                        if len(dlist) > 0:  
                            self.makeTableView(dlist, 'view')    
            ## single key command - no sceneItems
            elif self.canvas.control == '' and key in PlayKeys: 
                self.RSA(key)
   
    def RSA(self, key):
        self.closeMenus()   
        if key in ('A', 'B'):
            self.bkgMaker.openBkgFiles() 
        elif key == 'L':
            ## use QFileDialog to open a .play json file and load it to the screen
            self.loadPlay()  
        elif key in ('D','R'):  ## added 'D' thru deleteSelected if nothing there 
            self.bkgMaker.screenrate = {}
            if self.demoAvailable:     
                self.demoMenu.openDemoMenu()  ## in snakes 
        elif key == 'S':   
            if self.demoAvailable:  
                self.screenMenu.openScreenMenu() ## in screens
        elif key == 'P':  
            self.pathMaker.initPathMaker()
        elif key == 'J':              
            ## use QFileDialog to open a .play json file to view the play file contents
            self.loadPlay('table')  
        elif key == 'H':    
            if self.help == True:      
                self.helpMenu.openHelpMenu() 
                self.help = False
            else:
                self.helpMenu.closeHelpMenu() 
                self.help = True
                
    def closeMenus(self):
        self.screenMenu.closeScreenMenu()
        self.demoMenu.closeDemoMenu()
        self.helpMenu.closeHelpMenu()

### --------------------------------------------------------        
    def runThese(self):      
        if self.demoAvailable and self.canvas.openPlayFile in ('snakes', 'bats', 'hats'):
            if self.canvas.openPlayFile == 'snakes' and self.snakes.what != '':
                self.snakes.rerun(self.snakes.what)  
            elif self.canvas.openPlayFile == 'hats' and self.hats.direction != '':
                self.hats.rerunAbstract(self.hats.direction)  
            elif self.canvas.openPlayFile == 'bats':
                self.bats.rerun()
        else:
            self.showtime.run()
      
    def runThis(self, file):  ## doesn't ask - called by demo menu - runs hatss
        if len(self.scene.items()) == 0:
            self.openPlay(paths['playPath'] + file)  ## also adds pix to scene
            self.canvas.openPlayFile = file  ## give it time to load 
            QTimer.singleShot(200, self.showtime.run)
   
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
        self.canvas.bkgMaker.trackers.clear()          
        ## number of pixitems, backgrounds zval, number of shadows        
        kix, bkgz, ns = 0, 0, 0
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
                if bkgz == 0: bkgz = common['bkgZ']  ## starts at -99.0, decrements zval 
                                
                ## a flat does not rely on a bkg.file once it's saved to a play.file
                if tmp['type'] == 'flat' and QColor().isValidColor(tmp['color']):
                    pix = Flat(tmp['color'], self.bkgMaker, bkgz)  
                              
                elif tmp['type'] == 'bkg':    
                    pix = BkgItem(paths['bkgPath'] + tmp['fileName'], self.canvas, bkgz)
                    
                pix.bkgMaker.lockBkg(pix)                                         
                self.showFiles.addPixToScene(pix, tmp, bkgz)  ## finish unpacking tmp  
                bkgz -= 1           
            del tmp              
        ## end for loop   
                         
        del dlist
        self.cleanup(ns, kix)  ## add shadows
  
### --------------------------------------------------------                         
    def cleanup(self, ns, kix):
        file = os.path.basename(self.canvas.openPlayFile) 
        if 'play' in file:  ## could be something else
            if ns == 0 and self.locks == 0:
                self.dots.statusBar.showMessage(f"{file} - Number of Pixitems: {kix}")
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
                self.canvas.mapper.toggleTagItems('all')                                                  
        QTimer.singleShot(12000, partial(self.dots.statusBar.showMessage, file)) 

### --------------------------------------------------------                                                  
    def addShadows(self):  ## add shadows after adding pixitems     
        tasks = []         
        start = time.time()
        loop  = asyncio.new_event_loop() 
        ## thanks to a dev community post - it took some work to find a useful example
        for pix in self.scene.items(): 
            if pix.type == 'pix' and pix.shadowMaker.isActive == True and len(pix.shadow) > 0:
                pix.fileName = paths['spritePath'] + pix.fileName      
                tasks.append(loop.create_task(pix.shadowMaker.restoreShadow()))        
        if len(tasks) > 0:
            loop.run_until_complete(asyncio.wait(tasks))
        loop.close()           
        self.sideCar.showOutlines()  ## turns them on      
        QTimer.singleShot(3000, self.sideCar.hideOutlines)          
        str = f' Number of Shadows: {len(tasks)}   seconds: {time.time() - start:.2f}'
        self.dots.statusBar.showMessage(str, 10000)   
 
### ---------------------- dotsShowBiz --------------------


        
