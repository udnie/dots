
from os import path

import json
import random

import asyncio
import time

from PyQt6.QtCore    import QTimer, QAbstractAnimation, QPoint

from dotsPixItem     import PixItem
from dotsBkgMaker    import *

from dotsShared      import common, paths
from dotsSideGig     import MsgBox, getPathList, savePix, saveBkg, saveFlat, getCtr
from dotsSideCar     import SideCar
from dotsScreens     import MaxScreens
from dotsSidePath    import Wings

### ---------------------- dotsSideShow --------------------
''' dotsSideShow: functions to run, pause, stop, etc.. .play animations'''        
### --------------------------------------------------------
class SideShow:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas   = parent
        self.scene    = self.canvas.scene
        self.dots     = self.canvas.dots
        self.mapper   = self.canvas.mapper
        self.bkgMaker = self.canvas.bkgMaker
        
        self.sideCar  = SideCar(self.canvas)  ## additional extentions
        self.snakes   = self.canvas.snakes 
        self.wings    = Wings(self.canvas)   

        self.animation = self.canvas.animation
        self.pathMaker = self.canvas.pathMaker
 
        self.ifBats = False
        
        self.locks = 0
        
### --------------------------------------------------------    
    def keysInPlay(self, key):
        if self.canvas.pathMakerOn == False:
            if key == 'L' and self.canvas.control == '':
                self.loadPlay()
            elif key == 'P':  ## always
                self.mapper.togglePaths()
            elif key == 'R':    
                if len(self.scene.items()) == 0:
                    self.runThis(common['runThis'])  
                else:
                    self.run()
            elif key == 'S':
                if self.canvas.control != '':
                    self.stop()
                         
    def loadPlay(self):   
        if self.canvas.pathMakerOn:  ## using load in pathMaker
            self.pathMaker.sideWays.openFiles()
            return
        else: 
            Q = QFileDialog()
            file, _ = Q.getOpenFileName(self.canvas, 
                'Choose a file to open', paths['playPath'], 'Files (*.play)', None)
            Q.accept()      
            if file:
                self.openPlay(file) 
            else:
                return
            
    def runThis(self, file):  ## doesn't ask
        if not self.scene.items():
            self.openPlay(paths['playPath'] + file)  ## also adds pix to scene 
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
                
        kix, bkz, ns = 0, 0, 0  ## number of pixitems, bkg zval, number of shadows
        lnn = len(dlist)
        lnn = lnn + self.mapper.toFront(0)  ## start at the top
                
        for tmp in dlist:                   
            if tmp['type'] == 'bkg' and tmp['fname'] != 'flat' and \
                not path.exists(paths['bkgPath'] + tmp['fname']):    
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
                ## print(lnn, tmp['fname'], tmp['x'], tmp['width']) 
                                
            elif tmp['type'] == 'bkg':  ## could be more than one background or flat
                if bkz == 0:
                    bkz = common['bkgZ']  ## starts at -99.0
                tmp['z'] = bkz           
                if tmp['fname'] == 'flat':
                    self.canvas.bkgMaker.setBkgColor(QColor(tmp['tag']), bkz)
                else:
                    pix = BkgItem(paths['bkgPath'] + tmp['fname'], self.canvas, bkz)    
                    self.addPixToScene(pix, tmp)  ## finish unpacking tmp 
                    ## print(bkz, tmp['fname'], tmp['x'], tmp['width'])
                bkz -= 1   
            del tmp 
        ## end for loop
        del dlist
        self.canvas.openPlayFile = file
        self.canvas.bkgMaker.disableBkgBtns()
        
        file = os.path.basename(self.canvas.openPlayFile)
        self.dots.statusBar.showMessage(file + " - " + 'Number of Pixitems: {}'.format(kix)) 
                
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
        pix.setPos(pix.x,pix.y)
        pix.setZValue(tmp['z']),  ## use the new one
        pix.setMirrored(tmp['mirror']),
        pix.rotation = tmp['rotation']
        pix.scale    = tmp['scale']
              
        ## bump zVals up 100
        if pix.type == 'pix': pix.setZValue(pix.zValue() + 100)  ## not for 'bkg'
           
        if 'tag' not in tmp.keys():  ## seriously good to know
            tmp['tag'] = ''
        pix.tag = tmp['tag'] 

        if 'alpha2' not in tmp.keys(): 
            tmp['alpha2'] = 1.0
        pix.alpha2 = tmp['alpha2'] 

        if 'locked' not in tmp.keys(): 
            tmp['locked'] = False
        pix.locked = tmp['locked']

        if pix.type in('pix') and 'frame' not in pix.fileName:
            pix.locked = tmp['locked']
            if pix.locked: self.locks += 1
            pix.part = tmp['part']
            self.lookForStrays(pix)  
                                                   
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
                   
        del tmp      
                                           
        if pix.type == 'bkg':  ## you can unlock them now
            pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
            pix.locked = True                                                                          
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
    def run(self):  ## run only pixItems
        if self.canvas.openPlayFile == 'snakes': 
            self.snakes.rerun()
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
        for pix in self.scene.items():  ## set the animation and run it 
            if pix.type == 'pix' and pix.tag:
                ## if random, slice to length, display actual anime if paused 
                if 'Random' in pix.tag:
                    pix.tag = pix.tag[0:len('Random')]
                if 'frame' in pix.fileName:
                    pix.tag = 'idle' 
                ## set the animation using the tag
                pix.anime = self.animation.setAnimation(          
                    pix.tag, 
                    pix)   
                k += 1  ## k = number of pixitems
                if pix.anime == None:
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
                        QTimer.singleShot(100 + (r * 50), pix.anime.start)
                else:
                    # if pix.anime: 
                    QTimer.singleShot(98 + (k * 17), pix.anime.start)
                        # pix.anime.start()
                ### --->> optional drop shadow <<-- ###
                # shadow = QGraphicsDropShadowEffect(blurRadius=11, xOffset=8, yOffset=8)
                # pix.setGraphicsEffect(shadow)
            elif pix.zValue() <= common['pathZ']:
                break 
            
        if k > 0 or self.ifBats:
            self.sideCar.disablePlay()  
            self.canvas.control = 'pause'
            file = os.path.basename(self.canvas.openPlayFile)
            self.dots.statusBar.showMessage(file + " - " + 'Number of Pixitems: {}'.format(k))  
                                   
    def pause(self):
        self.clearPathsandTags()  
        if self.canvas.control == 'resume':
           self.resume()
        else:          
            for pix in self.scene.items():
                if pix.type in ('pix', 'snake') and pix.anime:
                    if pix.anime.state() == QAbstractAnimation.State.Running:  ## running
                        pix.anime.pause()       
                if pix.zValue() <= common['pathZ']:
                    break
            self.sideCar.setPauseKey()

    def resume(self):   
        for pix in self.scene.items():
            if pix.type in ('pix', 'snake') and pix.anime:
                if pix.anime.state() == QAbstractAnimation.State.Paused:
                    pix.anime.resume()
            if pix.zValue() <= common['pathZ']:
                break
        self.sideCar.setPauseKey()
        
    def stop(self, action=''):  ## action used by clear 
        self.clearPathsandTags()     
        for pix in self.scene.items():
            if pix.type in ('pix', 'snake'):
                if 'frame' in pix.fileName:
                    continue  
                if pix.anime:  ## stop it if running
                    pix.anime.stop()  
                if pix.part in ('left','right'):  
                    continue  ## these stop when pivot stops
                if action != 'clear':    
                    pix.reprise() 
            elif pix.zValue() <= common['pathZ']:
                break
        self.sideCar.enablePlay() 
        self.canvas.btnPause.setText( 'Pause' )
                
### --------------------------------------------------------
    def lookForStrays(self, pix):
        if pix.x < -25 or pix.x > common['ViewW'] -10:
            pix.setPos(float(random.randint(25, 100) * 2.5), pix.y)      
        if pix.y < -25 or pix.y > common['ViewH']-10:
            pix.setPos(pix.x, random.randint(25, 100) * 1.5)

    def clearPathsandTags(self):
        self.mapper.clearTagGroup()
        self.mapper.clearPaths()  ## clears tags as well

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
                    dlist.append(saveFlat(pix))  ## ditto
        if dlist:
            try:
                self.sideCar.saveToJson(dlist)
            except FileNotFoundError:
                MsgBox('savePlay: Error saving file', 5)         
        del dlist
  
### ---------------------- dotsSideShow --------------------
