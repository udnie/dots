
import json
import asyncio
import time

from os                 import path
from functools          import partial

from PyQt6.QtCore       import QTimer, QPointF

from dotsShared         import common, paths
from dotsPixItem        import PixItem
from dotsBkgMaker       import *

from dotsShowTime       import ShowTime
from dotsSideGig        import *
from dotsSideCar        import SideCar 
from dotsShowWorks      import ShowWorks

from dotsMenus          import DemoMenu, ScreenMenu
from dotsSnakes         import Snakes
from dotsAbstractBats   import Abstract, Bats, Wings

### ---------------------- dotsSideShow --------------------
''' class: SideShow: functions to load and add items to scene/canvas '''        
### --------------------------------------------------------
class SideShow:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas   = parent
        self.scene    = self.canvas.scene
        self.dots     = self.canvas.dots
        self.mapper   = self.canvas.mapper
        
        self.sideCar   = SideCar(self.canvas) 
        self.showWorks = ShowWorks(self.canvas) 
        
        self.pathMaker = self.canvas.pathMaker
        self.bkgMaker  = self.canvas.bkgMaker
       
        self.demoAvailable = DemoAvailable()
       
        if self.demoAvailable:
            self.bats      = Bats(self.canvas)     
            self.snakes    = Snakes(self.canvas)     
            self.abstract  = Abstract(self.canvas) 
            self.demoMenu  = DemoMenu(self.canvas, self)
 
        self.showtime   = ShowTime(self.canvas)
        self.screenMenu = ScreenMenu(self.canvas)  ## in screens
 
        self.locks = 0
        
### --------------------------------------------------------    
    def keysInPlay(self, key):
        if self.canvas.pathMakerOn == False:                    
            if len(self.scene.items()) > 0:  ## stuff on screen
                if key == 'P':  ## always
                    self.mapper.pathsAndTags.togglePaths()                               
                elif key == 'R':    
                    if self.canvas.control != '':
                        return
                    else:
                        self.runThese()                                        
                elif key == 'S':
                    if self.canvas.control != '':
                        self.showtime.stop()   
            ## single key command - no sceneItems
            elif self.canvas.control == '' and key in ('L', 'R', 'S', 'A', 'P'): 
                self.RSA(key)
                
### --------------------------------------------------------            
    def runThese(self):      
        if self.demoAvailable and self.canvas.openPlayFile in ('snakes', 'bats', 'abstract'):
            if self.canvas.openPlayFile == 'snakes' and self.snakes.what != '':
                self.snakes.rerun(self.snakes.what)  
            elif self.canvas.openPlayFile == 'abstract' and self.abstract.direction != '':
                self.abstract.rerunAbstract(self.abstract.direction)  
            elif self.canvas.openPlayFile == 'bats':
                self.bats.rerun()
        else:
            self.showtime.run()
               
    def RSA(self, key):
        if key == 'L':
            self.loadPlay()  
        elif key == 'R':   
            self.screenMenu.closeScreenMenu()
            if self.demoAvailable: 
                self.demoMenu.openDemoMenu()  ## in snakes 
        elif key == 'S':   
            if self.demoAvailable:  
                self.demoMenu.closeDemoMenu()
                self.screenMenu.openScreenMenu() ## in screens
        elif key == 'A':
            self.bkgMaker.openBkgFiles()   
        elif key == 'P':
            self.pathMaker.initPathMaker()       
                                   
### --------------------------------------------------------                            
    def loadPlay(self):   
        if self.canvas.pathMakerOn:  ## use pathChooser - was loader once but now you can see them
            return

        Q = QFileDialog()
        Q.Option.DontUseNativeDialog
        file, _ = Q.getOpenFileName(self.canvas, 
            'Choose a file to open', paths['playPath'], 'Files (*.play)', None)
        Q.accept()      
        if file:
            try:
                self.openPlay(file) 
                self.canvas.openPlayFile = file
            except IOError:
                MsgBox('loadPlay ' + file + 'Not Found')
        else:
            return
            
    def runThis(self, file):  ## doesn't ask - called by demo menu - runs abstracts
        if not self.scene.items():
            self.openPlay(paths['playPath'] + file)  ## also adds pix to scene
            self.canvas.openPlayFile = file  ## give it time to load
            QTimer.singleShot(200, self.showtime.run) 
       
### -------------------------------------------------------- 
    def openPlay(self, file):  ## adds play file contents to screen    
        dlist = []  
        try:
            with open(file, 'r') as fp:  ## read a play file
                dlist = json.load(fp)
        except IOError:
            MsgBox('openPlay: Error loading ' + file, 5)
            return   
                     
        self.mapper.clearMap()  ## just clear it
        self.locks = 0
        self.canvas.pixCount = self.mapper.toFront(0) 
        self.canvas.bkgMaker.trackers = []
                 
        ## number of pixitems, bkg zval, number of shadows, scrollers            
        kix, bkz, ns, scr, f = 0, 0, 0, 0, '' 
        lnn = len(dlist)
        lnn = lnn + self.mapper.toFront(0)  ## start at the top
        plist  = ['abstract', 'snakes']  ## demo pic are in images
                            
        for tmp in dlist:     
            ##  check if there            
            if tmp['type'] == 'bkg' and \
                not path.exists(paths['bkgPath']   + tmp['fname']) and\
                not path.exists(paths['imagePath'] + tmp['fname']):    
                MsgBox('openPlay: Error loading '  + paths['bkgPath'] + tmp['fname'], 5)  
                return 
                
            elif tmp['type'] == 'pix' and \
                not path.exists(paths['spritePath'] + tmp['fname']) and \
                not path.exists(paths['imagePath']  + tmp['fname']):
                MsgBox('openPlay: Error loading '   + paths['imagePath'] + tmp['fname'], 5)     
                return      
                 
            elif 'bat' in tmp['fname']:  ## make a bat - not from demoMenu 
                Wings(self.canvas, tmp['x'], tmp['y'], tmp['tag'])  ## added self to scene
                continue
               
            elif tmp['type'] == 'pix':
                kix += 1  ## counts pixitems
                self.canvas.pixCount += 1  ## id used by mapper            
                pathStr = paths['spritePath'] + tmp['fname']
                pix = PixItem(pathStr, self.canvas.pixCount, 0, 0, self.canvas) 
                tmp['z'] = lnn  ## lnn preserves front to back relationships 
                ## found a shadow - see if shadows are turned on, yes == '', no == 'pass'
                if 'scalor' in tmp.keys() and pix.shadowMaker.isActive == True:
                    ns += 1
                self.addPixToScene(pix, tmp)  ## finish unpacking tmp                 
                lnn -= 1 
                                 
            elif tmp['type'] in ('bkg', 'flat'):  ## could be more than one background or flat
                if bkz == 0:
                    bkz = common['bkgZ']  ## starts at -99.0
                tmp['z'] = bkz                
                if tmp['type'] == 'flat':  ## does not rely on a bkg.file once it's saved to a play.file
                    self.bkgMaker.setBkgColor(QColor(tmp['tag']), bkz)  ## sets flat to scene as well 
                else:          
                    if any(thing in tmp['fname'] for thing in plist):  ## demos are in images dir
                        if not os.path.exists(paths['bkgPath'] + tmp['fname']):
                            MsgBox(paths['bkgPath'] + tmp['fname'] + ' Not Found', 5)
                            return
                        else:
                            pix = BkgItem(paths['imagePath'] + tmp['fname'], self.canvas, bkz)  
                    else:
                        if not os.path.exists(paths['bkgPath'] + tmp['fname']):
                            MsgBox( paths['bkgPath'] + tmp['fname'] + ' Not Found', 5)
                            return
                        else:
                            pix = BkgItem(paths['bkgPath'] + tmp['fname'], self.canvas, bkz)
                            pix.bkgMaker.lockBkg(pix) 
                                         
                    self.addPixToScene(pix, tmp)  ## finish unpacking tmp 
                bkz -= 1   
            del tmp 
        ## end for loop
        
        del dlist
        
        file = os.path.basename(self.canvas.openPlayFile)
        
        if 'play' in file and ns == 0 and self.locks == 0:
            self.dots.statusBar.showMessage(file + ' - ' + 'Number of Pixitems: {}'.format(kix)) 
                
        elif ns > 0:  ## there must be shadows
            QTimer.singleShot(200, self.addShadows)
            MsgBox('Adding Shadows,  please wait...', int(1 + (ns * .25)))
            
        elif self.locks > 0:
            MsgBox('Some screen items are locked', 5)  ## seconds
            self.canvas.mapper.toggleTagItems('all')
                
### --------------------------------------------------------             
    def addShadows(self):  ## add shadows after adding pixitems     
        tasks = []         
        start = time.time()
        loop  = asyncio.new_event_loop() 
        ## thanks to a dev community post - it took some work to 
        ## eventually find an example that illustrated how to process
        ## a group of class functions using asyncio
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.shadow != None:
                tasks.append(loop.create_task(pix.shadowMaker.restoreShadow()))        
        if len(tasks) > 0:
            loop.run_until_complete(asyncio.wait(tasks))
        loop.close()        
        self.sideCar.hideOutlines()  ## turns them off               
        str = 'Number of Shadows: {0}  seconds:  {1:.2f}'  
        self.dots.statusBar.showMessage(str.format(len(tasks), time.time() - start), 10000)        
                       
 ### --------------------------------------------------------
    def addPixToScene(self, pix, tmp):  ## fills in the blanks and treats shadow as a pix 
        pix = self.showWorks.setAll(pix, tmp)  
                          
        if pix.type == 'pix': 
            pix = self.showWorks.setPixitem(pix, tmp)

        if 'tag' not in tmp.keys():     ## pix and bkg
            tmp['tag'] = ''
        if 'alpha2' not in tmp.keys():  ## for shadows
            tmp['alpha2'] = 1.0     
        if 'locked' not in tmp.keys():  ## pix and bkg
            tmp['locked'] = False     
                    
        pix.tag    = tmp['tag'] 
        pix.alpha2 = tmp['alpha2']
        pix.locked = tmp['locked']  
                    
        if 'scalor' in tmp.keys():   
            pix = self.showWorks.setShadow(pix, tmp)  
            
        elif pix.type == 'bkg':  ## adding the rest of it
            pix = self.showWorks.setBackGround(pix, tmp)  ## checking if a dupe
            if pix != None:
                self.scene.addItem(pix)     
                if pix.tag == 'scroller':  ## replace transformPix.. action
                    if pix.direction == 'right':
                        pix.setPos(QPointF(pix.runway, 0))  ## offset to right 
                    elif pix.direction == 'vertical':
                        pix.setPos(QPointF(0.0, float(pix.runway)))                             
        del tmp 
                                                                                                 
        ## adds pix to the scene and performs any transforms - used by other classes
        if pix != None and pix.type == 'pix': 
            self.sideCar.transFormPixItem(pix, pix.rotation, pix.scale, pix.alpha2)

        del pix
        
### ---------------------- dotsSideShow --------------------





