
from os import path

import json
import random

import asyncio
import time

from PyQt6.QtCore       import QTimer

from dotsShared         import common, paths
from dotsPixItem        import PixItem
from dotsBkgMaker       import *

from dotsShowTime       import ShowTime
from dotsSideGig        import *
from dotsSideCar        import SideCar

from dotsSnakes         import DemoMenu
from dotsScreens        import ScreenMenu

from dotsAbstractBats   import Abstract, Bats, Wings 
from dotsSnakes         import Snakes


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
        self.sideCar  = SideCar(self.canvas) 
        
        self.pathMaker = self.canvas.pathMaker
        self.bkgMaker  = self.canvas.bkgMaker
       
        self.demoAvailable = DemoAvailable()
       
        if self.demoAvailable:
            self.bats      = Bats(self.canvas)     
            self.snakes    = Snakes(self.canvas)     
            self.abstract  = Abstract(self.canvas) 
            self.demoMenu  = DemoMenu(self.canvas, self)
 
        self.showTime   = ShowTime(self.canvas)
        self.screenMenu = ScreenMenu(self.canvas)  ## in screens
 
        self.locks = 0
        
### --------------------------------------------------------    
    def keysInPlay(self, key):
        if self.canvas.pathMakerOn == False:      
            if key == 'L' and self.canvas.control == '':
                self.loadPlay()
                       
            elif len(self.scene.items()) > 0:  ## stuff on screen
                if key == 'P':  ## always
                    self.mapper.togglePaths() 
                                           
                elif key == 'R':    
                    if self.canvas.control != '':
                        return
                             
                    if self.demoAvailable and self.canvas.openPlayFile in ('snakes', 'bats', 'abstract'):
                        if self.canvas.openPlayFile == 'snakes' and self.snakes.what != '':
                            self.snakes.rerun(self.snakes.what)  
                        elif self.canvas.openPlayFile == 'abstract' and self.abstract.direction != '':
                            self.abstract.rerun(self.abstract.direction)  
                        elif self.canvas.openPlayFile == 'bats':
                            self.bats.rerun()
                    else:
                      self.showTime.run()   
                                                                   
                elif key == 'S':
                    if self.canvas.control != '':
                        self.showTime.stop()
                        
            else:  ## nothing on screen - easier to add more single keys  
                if key == 'R':   
                    self.screenMenu.closeScreenMenu()
                    if self.demoAvailable: 
                        self.demoMenu.openDemoMenu()  
                elif key == 'S':   
                    if self.demoAvailable:  
                        self.demoMenu.closeDemoMenu()
                    self.screenMenu.openScreenMenu()
                elif key == 'A':
                    self.bkgMaker.openBkgFiles()
                    
### --------------------------------------------------------                            
    def loadPlay(self):   
        if self.canvas.pathMakerOn:  ## using load in pathMaker
            self.pathMaker.sideWays.openFiles()
            return
        else: 
            Q = QFileDialog()
            Q.Option.DontUseNativeDialog
            file, _ = Q.getOpenFileName(self.canvas, 
                'Choose a file to open', paths['playPath'], 'Files (*.play)', None)
            Q.accept()      
            if file:
                self.openPlay(file) 
                self.canvas.openPlayFile = file
            else:
                return
            
    def runThis(self, file):  ## doesn't ask - called by demo menu - runs abstracts
        if not self.scene.items():
            self.openPlay(paths['playPath'] + file)  ## also adds pix to scene
            self.canvas.openPlayFile = file  ## give it time to load
            QTimer.singleShot(200, self.showTime.run) 
       
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
         
        ## number of pixitems, bkg zval, number of shadows, scrollers 
              
        kix, bkz, ns, scr, f = 0, 0, 0, 0, '' 
        lnn = len(dlist)
        lnn = lnn + self.mapper.toFront(0)  ## start at the top
        plist  = ['abstract', 'snakes']  ## demo pic are in images
                            
        for tmp in dlist:                  
            if tmp['type'] == 'bkg' and tmp['fname'] != 'flat' and \
                not path.exists(paths['bkgPath'] + tmp['fname']) and\
                not path.exists(paths['imagePath'] + tmp['fname']):    
                MsgBox('openPlay: Error loading ' + paths['bkgPath'] + tmp['fname'], 5)  
                continue 
                
            elif tmp['type'] == 'pix' and \
                not path.exists(paths['spritePath'] + tmp['fname']) and \
                not path.exists(paths['imagePath']  + tmp['fname']):
                MsgBox('openPlay: Error loading ' + paths['imagePath'] + tmp['fname'], 5)     
                continue      
                 
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
                if 'scalor' in tmp.keys() and pix.shadowMaker.isDummy == False:
                    ns += 1
                self.addPixToScene(pix, tmp)  ## finish unpacking tmp                 
                lnn -= 1 
                                 
            elif tmp['type'] == 'bkg':  ## could be more than one background or flat
                if bkz == 0:
                    bkz = common['bkgZ']  ## starts at -99.0
                tmp['z'] = bkz                
                if tmp['fname'] == 'flat': 
                    self.bkgMaker.setBkgColor(QColor(tmp['tag']), bkz)           
                else:              
                    if any(thing in tmp['fname'] for thing in plist):  ## demos are in images dir
                        pix = BkgItem(paths['imagePath'] + tmp['fname'], self.canvas, bkz)  
                    else:
                        pix = BkgItem(paths['bkgPath'] + tmp['fname'], self.canvas, bkz)  
                    self.addPixToScene(pix, tmp)  ## finish unpacking tmp 
                bkz -= 1   
            del tmp 
        ## end for loop
        
        del dlist
        self.bkgMaker.disableBkgBtns()
        
        file = os.path.basename(self.canvas.openPlayFile)
        if 'play' in file:
            self.dots.statusBar.showMessage(file + ' - ' + 'Number of Pixitems: {}'.format(kix)) 
                
        if ns > 0:  ## there must be shadows
            QTimer.singleShot(200, self.addShadows) 
            MsgBox('Adding Shadows,  please wait...', int(1 + (ns * .25)))
        elif self.locks > 0:
            MsgBox('Some screen items are locked', 5)  ## seconds
            self.canvas.mapper.toggleTagItems('all')
        
 ### --------------------------------------------------------
    def addPixToScene(self, pix, tmp):
        pix.type = tmp['type']                 
        pix.x = float('{0:.2f}'.format(tmp['x']))
        pix.y = float('{0:.2f}'.format(tmp['y']))
        pix.setZValue(tmp['z']),  ## use the new one
        pix.setMirrored(tmp['mirror']),
        pix.rotation = tmp['rotation']
        pix.scale    = tmp['scale']
                            
        ## bump zVals up 100
        if pix.type == 'pix': 
            pix.setZValue(pix.zValue() + 100)  ## not for 'bkg'
            pix.setPos(pix.x, pix.y)
           
        if 'tag' not in tmp.keys():  ## seriously good to know
            tmp['tag'] = ''
        pix.tag = tmp['tag'] 

        if 'alpha2' not in tmp.keys():  ## for shadows
            tmp['alpha2'] = 1.0
        pix.alpha2 = tmp['alpha2'] 

        if 'locked' not in tmp.keys(): 
            tmp['locked'] = False
        pix.locked = tmp['locked']

        if pix.type in('pix') and 'frame' not in pix.fileName:
            pix.locked = tmp['locked']
            if pix.locked: self.locks += 1
            pix.part = tmp['part']
            pix = lookForStrays(pix)  
                                                   
        if 'scalor' in tmp.keys():  ## save to pix.shadow      
            pix.shadow = {
                'alpha':    tmp['alpha'],
                'scalor':   tmp['scalor'],  ## unique to shadow
                'rotate':   tmp['rotate'],
                'width':    tmp['width'],
                'height':   tmp['height'],
                'pathX':    tmp['pathX'],
                'pathY':    tmp['pathY'],  
            }  
            if 'flopped' not in tmp.keys():      
                pix.shadow['flopped'] = None
            else:
                pix.shadow['flopped'] = tmp['flopped']
            if 'fileName' not in tmp.keys(): 
                pix.shadow['fileName'] = 'shadow' 
                                                          
        if pix.type == 'bkg':  ## you can unlock them now
              
            if 'scrollable' not in tmp.keys(): 
                tmp['scrollable'] = False
            pix.scrollable = tmp['scrollable']
             
            if 'direction' not in tmp.keys(): 
                tmp['direction'] = 'left'
            pix.direction = tmp['direction']
            
            if 'anime' not in tmp.keys(): 
                tmp['anime'] = None
            pix.anime = tmp['anime']
                                  
        del tmp 

        if pix.type == 'bkg' and pix.direction == '':
            pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
                                                                                           
        ## may require rotation or scaling - adds to scene items
        self.sideCar.transFormPixItem(pix, pix.rotation, pix.scale, pix.alpha2)
   
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
        
        str = 'Number of Shadows: {0}  seconds:  {1:.2f}'  
        self.dots.statusBar.showMessage(str.format(len(tasks), time.time() - start), 10000)        
   
### --------------------------------------------------------
def lookForStrays(pix):
    if pix.x < -25 or pix.x > common['ViewW'] -10:
        pix.setPos(float(random.randint(25, 100) * 2.5), pix.y)      
    if pix.y < -25 or pix.y > common['ViewH']-10:
        pix.setPos(pix.x, random.randint(25, 100) * 1.5) 
    return pix
        
### ---------------------- dotsSideShow --------------------
