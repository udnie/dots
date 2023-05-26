
from os import path

import json
import random
import gc

import asyncio
import time

from PyQt6.QtCore       import QTimer, QAbstractAnimation
from PyQt6.QtWidgets    import QGraphicsPolygonItem

from dotsShared         import common, paths
from dotsPixItem        import PixItem
from dotsBkgMaker       import *

from dotsSideGig        import *
from dotsSideCar        import SideCar
from dotsSidePath       import Wings

from dotsSnakes         import DemoMenu
from dotsScreens        import ScreenMenu

### ---------------------- dotsSideShow --------------------
''' class: SideShow: functions to run, pause, stop, etc.. .play animations'''        
### --------------------------------------------------------
class SideShow:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas   = parent
        self.scene    = self.canvas.scene
        self.dots     = self.canvas.dots
        self.mapper   = self.canvas.mapper
        
        self.sideCar  = SideCar(self.canvas)  ## additional extentions
        self.wings    = Wings(self.canvas)   

        self.animation = self.canvas.animation
        self.pathMaker = self.canvas.pathMaker
        self.bkgMaker  = self.canvas.bkgMaker
        
        self.demoMenu   = DemoMenu(self.canvas)
        self.screenMenu = ScreenMenu(self.canvas)
 
        self.ifBats = False
        self.locks = 0
        
### --------------------------------------------------------    
    def keysInPlay(self, key):
        if self.canvas.pathMakerOn == False:      
            if key == 'L' and self.canvas.control == '':
                self.loadPlay()
                
            elif key == 'P':  ## always
                self.mapper.togglePaths()
                
            elif len(self.scene.items()) > 0:       
                if key == 'R':                  
                    if self.canvas.openPlayFile == 'snakes' and self.bkgMaker.key != '':
                        self.bkgMaker.delSnakes()
                        self.demoMenu.run(self.bkgMaker.key)                    
                    elif self.canvas.openPlayFile != '':
                        self.run()                                      
                elif key == 'S':
                    if self.canvas.control != '':
                        self.stop()
                        
            else:  ## easier to add more single keys  
                if key == 'R':
                    self.screenMenu.closeScreenMenu()
                    self.demoMenu.openDemoMenu()  
                elif key == 'S':   
                    self.demoMenu.closeDemoMenu()
                    self.screenMenu.openScreenMenu()
        
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
            
    def runThis(self, file):  ## doesn't ask
        if not self.scene.items():
            self.openPlay(paths['playPath'] + file)  ## also adds pix to scene
            self.canvas.openPlayFile = file
            QTimer.singleShot(200, self.run) 
       
### -------------------------------------------------------- 
    def openPlay(self, file):  ## adds play file contents to screen
        if 'demo-' in file and common['Screen'] not in file:
            MsgBox('Demo file format does not match Screen Width', 7)
            return    
        try:
            dlist = []  
            with open(file, 'r') as fp:  ## read a play file
                dlist = json.load(fp)
        except IOError:
            MsgBox('openPlay: Error loading ' + file, 5)
            return
           
        self.mapper.clearMap()  ## just clear it  
        self.locks = 0
        self.ifBats = False 
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
                not path.exists(paths['imagePath'] + tmp['fname']):
                MsgBox('openPlay: Error loading ' + paths['imagePath'] + tmp['fname'], 5)     
                continue      
            
            elif 'bat' in tmp['fname']:    
                self.ifBats = True   
                self.wings.bats(tmp['x'], tmp['y'], tmp['tag'])  ## make a bat
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
    def run(self):  ## runs whatever is in scene that can be animated
        if self.canvas.openPlayFile == 'snakes': 
            self.bkgMaker.delSnakes()
            self.bkgMaker.snakes.rerun()
            return
        elif self.canvas.control != '':
            return   
        self.mapper.clearMap()
        self.clearPathsandTags()  
        self.canvas.unSelect()
        
        if not self.canvas.pathList:  ## should already exist - moved from animations
            self.canvas.pathList = getPathList(True)  
                        
        k, r = 0, 0  ## k counts all non r items (demo)
        scale = .65    
        for pix in self.scene.items():  ## sets the animation and run it <<----
            
            if type(pix) == 'dotsShadowWorks.PointItem':  ## goes with shadows for now
                continue
            if isinstance(pix, QGraphicsPolygonItem):
                continue
        
            if pix.type in ('pix', 'bkg') and pix.tag:    
                ## if random, slice to length, display actual anime if paused 
                if 'Random' in pix.tag:
                    pix.tag = pix.tag[0:len('Random')]
                if 'frame' in pix.fileName:
                    pix.tag = 'idle' 
                         
                ## set the animation using the tag
                if pix.type == 'pix':
                    pix.anime = self.animation.setAnimation(          
                        pix.tag, 
                        pix)        
                elif pix.type == 'bkg' and pix.tag == 'scroller':
                    pix.anime = pix.setScrollerPath(pix, 1)  ## from sidePath
                    pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True) 
                    
                k += 1  ## k = number of pixitems
                if pix.anime == None:  ## not animated
                    continue
                
                ## run the animation  - set scale factor if demoPath and alien
                # if pix.tag.endswith('demo-.path') and r >= 0:  
                if 'demo-' in pix.tag and r >= 0:  
                    if 'alien' in pix.fileName:  ## just to make sure you don't scale everything
                        pix.scale = scale * (67-(r*3))/100.0  ## 3 * 22 screen items
                    r += 1
                    ## delay each demo pixitems start 
                    if pix.anime == None:
                        break
                    else:
                        QTimer.singleShot(100 + (r * 50), pix.anime.start)  ## demo only
                else:            
                    pix.anime.start()  ## everyone else
                    
                ### --->> optional drop shadow <<-- ###
                # shadow = QGraphicsDropShadowEffect(blurRadius=11, xOffset=8, yOffset=8)
                # pix.setGraphicsEffect(shadow)

        if k > 0 or self.ifBats:
            self.sideCar.disablePlay()  
            self.canvas.control = 'pause'
            file = os.path.basename(self.canvas.openPlayFile)
            if "play" in file:
                self.dots.statusBar.showMessage(file + ' - ' + 'Number of Pixitems: {}'.format(k))  
                
### --------------------------------------------------------                                 
    def pause(self):
        self.clearPathsandTags()  
        if self.canvas.control == 'resume':
           self.resume()
        else:          
            for pix in self.scene.items():          
                if type(pix) == 'dotsShadowWorks.PointItem':
                    continue
                if isinstance(pix, QGraphicsPolygonItem):
                    continue         
                if pix.fileName in ('frame','flat'):
                    continue               
                if pix.type in ('pix', 'snake', 'bkg'):
                    if pix.anime != None and pix.anime.state() == QAbstractAnimation.State.Running:  ## running
                        pix.anime.pause() 
            self.sideCar.setPauseKey()

    def resume(self):   
        for pix in self.scene.items():   
            if type(pix) == 'dotsShadowWorks.PointItem':
                continue
            if isinstance(pix, QGraphicsPolygonItem):
                continue 
            if pix.fileName in ('frame','flat'):
                continue       
            if pix.type in ('pix', 'snake', 'bkg'):
                if pix.anime != None and pix.anime.state() == QAbstractAnimation.State.Paused:
                    pix.anime.resume()                   
        self.sideCar.setPauseKey()
        
### --------------------------------------------------------
    def stop(self, action=''):  ## action used by clear 
        self.clearPathsandTags()     
        scrolling = []
        for pix in self.scene.items():                      
            if type(pix) == 'dotsShadowWorks.PointItem':  ## shadows
                continue     
            if isinstance(pix, QGraphicsPolygonItem):  ## shadows
                continue      
            try:
                if pix.fileName in ('frame','flat'):
                    continue       
            except:
                continue
            
            if pix.type in ('pix', 'snake', 'bkg'):                   
                if pix.anime != None and pix.anime.state() != QAbstractAnimation.State.Stopped:       
                    pix.anime.stop()
                    if pix.tag == 'scroller':  ## can be more than one
                        pix.anime = None
                        scrolling.append(pix)
                               
                if pix.type in ('pix', 'snake'):
                    if pix.part in ('left','right'):  
                        continue  ## these stop when pivot stops  
                          
                    if action != 'clear':    
                        pix.reprise() 

        self.cleanUpScrollers(scrolling) 
        self.sideCar.enablePlay() 
        self.canvas.btnPause.setText( 'Pause' )
        gc
        
### --------------------------------------------------------        
    def cleanUpScrollers(self, scrolling):  
        if len(scrolling) == 0:
            return       
        f, d, s = None, '', None 
        for p in scrolling:  ## could be one on the way
            if f == None:    ## save first
                f = p.fileName
                d = p.direction
                s = p  ## save it
            else:
                self.scene.removeItem(p)
                del p       
        del scrolling 
                                   
        if f != None: 
            self.scene.removeItem(s)
            p = BkgItem(f, self.canvas)
            p.tag = 'scroller'
            p.direction = d
            if 'abstract' in p.fileName and d == 'right':
                p.setPos(QPointF(p.runway, 0))  ## offset to right         
            self.scene.addItem(p)    
            
### --------------------------------------------------------
    def savePlay(self):
        if self.canvas.openPlayFile == 'snakes':
            MsgBox("Can't Save Snakes as a Play File", 6)  ## seconds
            return        
        if self.canvas.pathMakerOn:  ## using load in pathMaker
            self.pathMaker.sideWays.savePath()
            return        
        elif len(self.scene.items()) == 0:
            return   
              
        dlist = [] 
        for pix in self.scene.items(): 
                      
            if pix.type in ('pix','bkg'): 
                if pix.fileName != 'flat' and \
                    not path.exists(pix.fileName):  ## note
                    continue   
            
            if pix.type == 'pix':   
                if pix.part in ('left','right'):  ## let pivot thru
                    continue                  
                dlist.append(savePix(pix))  ## in sideGig   
                  
            elif pix.type == 'bkg':
                if pix.fileName != 'flat':      
                    dlist.append(saveBkg(pix))  ## in sideGig
                else:
                    dlist.append(saveFlat(pix))  ## in sideGig            
        if dlist:
            try:
                self.sideCar.saveToJson(dlist)
            except FileNotFoundError:
                MsgBox('savePlay: Error saving file', 5)         
        del dlist
        
    def clearPathsandTags(self):
        self.mapper.clearTagGroup()
        self.mapper.clearPaths()  ## clears tags as well

### --------------------------------------------------------
def lookForStrays(pix):
    if pix.x < -25 or pix.x > common['ViewW'] -10:
        pix.setPos(float(random.randint(25, 100) * 2.5), pix.y)      
    if pix.y < -25 or pix.y > common['ViewH']-10:
        pix.setPos(pix.x, random.randint(25, 100) * 1.5) 
    return pix
        
### ---------------------- dotsSideShow --------------------
