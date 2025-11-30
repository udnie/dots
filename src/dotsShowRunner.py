
import json
import time
import asyncio
import os      

from functools          import partial
from PyQt6.QtCore       import QTimer

from dotsShared         import common, paths
from dotsSideGig        import MsgBox

from dotsBkgMaker       import *
from dotsFrameAndFlats  import Frame
from dotsPixItem        import PixItem
from dotsSideCar        import SideCar 
from dotsShowFiles      import ShowFiles   
from dotsShowTime       import ShowTime
from dotsTableMaker     import TableView
from dotsWings          import Wings

### ---------------------- dotsShowBiz --------------------
''' functions to load and add both demo and non demo items,
            play files, to the scene/canvas/storyboard '''    
### --------------------------------------------------------
class ShowRunner:  
### --------------------------------------------------------
    def __init__(self, parent, showbiz):
        super().__init__()
 
        self.canvas  = parent
        self.showbiz = showbiz
        
        self.scene  = self.canvas.scene
        self.dots   = self.canvas.dots
        self.mapper = self.canvas.mapper
                
        self.pathMaker = self.canvas.pathMaker
        self.bkgMaker  = self.canvas.bkgMaker
            
        self.sideCar   = SideCar(self.canvas)  
        self.showtime  = ShowTime(self.canvas)
        self.showFiles = ShowFiles(self.canvas) 
   
        self.locks = 0
       
### --------------------------------------------------------          
    def runThese(self):   
        if self.showbiz.demoAvailable and self.canvas.openPlayFile in ('snakes', 'bats', 'hats'): 
            if self.showbiz.helpMenus.demoHelp != None:
                self.showbiz.helpMenus.demoHelp.runThese() 
        else:
            self.showtime.run()
        
    def makeTableView(self, dlist, src=''):  ## called if missing files     
        if self.showbiz.tableView != None:
            self.showbiz.tableView.bye()                      
        self.showbiz.tableView = TableView(self, dlist, src)  ## show it
                                                            
    def openPlay(self, file):    
        try:
            with open(file, 'r') as fp: 
                dlist = json.load(fp)                 
        except IOError:
            MsgBox('openPlay: Error loading ' + file, 5)
            return '' 
        return dlist                                                            
                                                                                                                                                                                                                          
### --------------------------------------------------------                            
    def loadPlay(self, src=''):  ## scr='table' launch play file viewer
        if self.canvas.pathMakerOn:  
            return    
        elif self.canvas.videoPlayer != None:
            MsgBox('Delete the Video and Reload it as the Last Screen Item', 6)
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
                try:
                    self.makeTableView(dlist, src)  ## display any missing files or what's there if 'table'
                    ## src = 'table' if run from canvas when typing 'j'
                    if self.showbiz.tableView.loadingError == True or src == 'table':
                        return
                    self.updateStoryBoard(dlist) 
                except:
                    MsgBox('showRunner: error on making tableview')
            else:
                return
              
### -------------------------------------------------------- 
    def updateStoryBoard(self, dlist):  ## turn the contents of the .play file into scene items            
        self.mapper.clearMap() 
        self.locks = 0
        
        self.addedVideo = False  
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
                   
            elif tmp['type'] == 'video':  ## needs to happen before shadows
                self.sideCar.addVideo(paths['bkgPath'] + tmp['fileName'], 'open', tmp['loops'])
                bkgz = -101  ## takes two 
                self.addedVideo = True
                   
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
                if self.addedVideo == True:  ## first frame capture in progress
                    time.sleep(.10)  
                    
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


        
