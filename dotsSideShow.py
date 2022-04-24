
import os
import json
import random

import asyncio
import time

from PyQt6.QtCore    import QTimer, QAbstractAnimation, Qt
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

from dotsPixItem     import PixItem
from dotsBkgItem     import *

# from dotsShadowWorks    import Shadow  ## adds shadows
from dotsShadow_Dummy    import Shadow  ## turns off shadows

from dotsShared      import common, paths
from dotsSideGig     import MsgBox, getPathList
from dotsSideCar     import SideCar

### ---------------------- dotsSideShow --------------------
''' dotsSideShow: functions to run, pause, stop, etc.. .play animations'''        
### --------------------------------------------------------
class SideShow:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas  = parent
        self.scene   = self.canvas.scene
        self.dots    = self.canvas.dots
        self.mapper  = self.canvas.mapper
        self.sideCar = SideCar(self.canvas)  ## additional extentions 

        self.animation = self.canvas.animation
        self.pathMaker = self.canvas.pathMaker
        
        self.locks = 0
        
### --------------------------------------------------------
    def runThis(self, file):
        if not self.scene.items():
            self.openPlay(paths["playPath"] + file)
            QTimer.singleShot(200, self.run)
    
    def keysInPlay(self, key):
        if self.canvas.pathMakerOn == False:
            if key == 'L':
                self.loadPlay()
            elif key == 'P':  ## always
                self.mapper.togglePaths()
            elif key == 'R':    
                if len(self.scene.items()) == 0:
                    self.runThis(common['runThis'])  
                else:
                    self.run()
            elif key == 'S' and self.canvas.control != '':
                self.stop()
       
    def loadPlay(self):
        if self.canvas.pathMakerOn:  ## using load in pathMaker
            self.pathMaker.sideWays.openFiles()
        else:
            Q = QFileDialog()
            file, _ = Q.getOpenFileName(self.canvas, 
                "Choose a file to open", paths["playPath"], "Files (*.play)",
                None)
            if file:
                self.openPlay(file) 
            else:
                return

    def openPlay(self, file):
        dlist = []
        self.locks = 0
        try:
            with open(file, 'r') as fp:  ## read a play file
                dlist = json.load(fp)
        except IOError:
            MsgBox("openPlay: Error loading " + file, 5)
            return
        if dlist:          
            self.mapper.clearMap()   ## just clear it   
            kix, bkz, ns = 0, 0, 0   ## number of pixitems, bkg zval, number of shadows
            lnn = len(dlist)
            lnn = lnn + self.mapper.toFront(0)  ## start at the top
            self.canvas.pixCount = self.mapper.toFront(0) 
             
            # header = []  ## save for debugging purposes 
                
            for tmp in dlist:  
              
                ## I'm including this as it makes dumping the play file easier to read
                ## just incase - up to 20 keys - current max size of the play dictionary
                # if header != list(tmp.keys())[:20]:  ## [8:20] you can also dump a range
                #     header = list(tmp.keys())[:20]   ## includes shadow data 
                #     print(','.join(header)) 
                # vals = list(tmp.values())[:20]   
                # print(','.join(str(v) for v in vals))  ## formatted for csv
                # continue
                
                ## toss no shows - no msgs or log
                if tmp['type'] == 'bkg' and tmp['fname'] != 'flat' and \
                    not path.exists(paths["bkgPath"] + tmp['fname']):       
                    continue 
                
                elif tmp['type'] == 'pix' and \
                    not path.exists(paths["spritePath"] + tmp['fname']) and \
                    not path.exists(paths["imagePath"] + tmp['fname']):
                    continue  
                
                elif 'bat' in tmp['fname']:       
                    self.sideCar.wings(tmp['x'], tmp['y'], tmp['tag'])
                    continue
                
                elif tmp['type'] == 'pix':
                    kix += 1  ## counts pixitems
                    self.canvas.pixCount += 1  ## id used by mapper            
                    pathStr = paths["spritePath"] + tmp['fname']
                    pix = PixItem(pathStr, self.canvas.pixCount, 0, 0, self.canvas) 
                    tmp['z'] = lnn  ## lnn preserves front to back relationships
                    lnn -= 1 
                    ## found a shadow - see if shadows are turned on, yes == '', no == 'pass'
                    if 'scalor' in tmp.keys() and pix.shadowMaker.addRestore == '': 
                        ns += 1
                    self.addPixToScene(pix, tmp)  ## finish unpacking tmp  
                                
                elif tmp['type'] == 'bkg': 
                    if bkz == 0:
                        bkz = common['bkgZ']  ## starts at -99.0
                    else:
                        bkz -= 1  ## could be more than one background or flat
                    tmp["z"] = bkz
                    if tmp['fname'] == 'flat':
                        self.canvas.initBkg.setBkgColor(QColor(tmp['tag']), tmp["z"])
                        continue 
                    else:
                        pix = BkgItem(paths["bkgPath"] + tmp['fname'], self.canvas, tmp["z"])
                        pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)     
                        self.addPixToScene(pix, tmp)  ## finish unpacking tmp 
 
            self.canvas.openPlayFile = file
            self.canvas.initBkg.disableBkgBtns()
            self.dots.statusBar.showMessage("Number of Pixitems: {}".format(kix),5000)  
              
            if ns > 0:
                QTimer.singleShot(200, self.addShadows)  
                MsgBox("Adding Shadows,  please wait...", int(1 + (ns * .3)))
            elif self.locks > 0:
                MsgBox("Some screen items are locked", 5)  ## seconds
                self.canvas.mapper.toggleTagItems('all')
        
 ### --------------------------------------------------------
    def addPixToScene(self, pix, tmp):
        pix.type = tmp['type']                 
        pix.x    = float("{0:.2f}".format(tmp['x']))
        pix.y    = float("{0:.2f}".format(tmp['y']))
        pix.setPos(pix.x,pix.y)
        pix.setZValue(tmp['z']),  ## use the new one
        pix.setMirrored(tmp['mirror']),
        pix.rotation = tmp['rotation']
        pix.scale    = tmp['scale']
      
        if 'tag' not in tmp.keys():  ## seriously good to know
            tmp['tag'] = ''
        pix.tag = tmp['tag'] 

        if 'alpha2' not in tmp.keys(): 
            tmp['alpha2'] = 1.0
        pix.alpha2 = tmp['alpha2'] 

        if pix.type == 'pix' and 'frame' not in pix.fileName:
            pix.locked = tmp['locked']
            if pix.locked: self.locks += 1
            pix.part = tmp['part']
            self.lookForStrays(pix)   
                                
        if 'scalor' in tmp.keys():  ## save to pix.shadow      
            pix.shadow = {
                "alpha":    tmp['alpha'],
                "scalor":   tmp['scalor'],  ## unique to shadow
                "rotate":   tmp['rotate'],
                "width":    tmp['width'],
                "height":   tmp['height'],
                "pathX":    tmp['pathX'],
                "pathY":    tmp['pathY'],
                "ishidden": tmp['ishidden'],     
            }        
     
        ## may require rotation or scaling - adds to scene items
        self.sideCar.transFormPixItem(pix, pix.rotation, pix.scale, pix.alpha2)
   
### --------------------------------------------------------                      
    def addShadows(self):         
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
        
        str = "Number of Shadows: {0}  seconds:  {1:.2f}"  
        self.dots.statusBar.showMessage(str.format(len(tasks), time.time() - start), 10000)        
          
    def run(self):  
        if self.canvas.control != '': 
            return 
        self.mapper.clearMap()
        self.clearPathsandTags()  
        self.canvas.unSelect()
        if not self.canvas.pathList:  ## should already exist - moved from animations
            self.canvas.pathList = getPathList(True)       
        k, r = 0, 0  ## k counts all non r items (demo)
        scale = .65
        for pix in self.scene.items():
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
                k += 1
                ## set scale factor if demoPath and alien
                if pix.tag.endswith('demo.path') and r >= 0:  
                    if 'alien' in pix.fileName:  ## just to make sure you don't scale everything
                        pix.scale = scale * (67-(r*3))/100.0  ## 3 * 22 screen items
                    r += 1
                    ## delay each demo pixitems start 
                    QTimer.singleShot(100 + (r * 50), pix.anime.start)
                else:
                    if pix.anime: 
                        pix.anime.start()
                ### --->> optional drop shadow <<-- ###
                # shadow = QGraphicsDropShadowEffect(blurRadius=11, xOffset=8, yOffset=8)
                # pix.setGraphicsEffect(shadow)
            elif pix.zValue() <= common["pathZ"]:
                break 
        if k > 0:
            self.sideCar.disablePlay()  
            self.canvas.control = 'pause'
            self.dots.statusBar.showMessage("Number of Pixitems:  {}".format(k),5000)
                                   
    def pause(self):
        self.clearPathsandTags()  
        if self.canvas.control == 'resume':
           self.resume()
        else:          
            for pix in self.scene.items():
                if pix.type == 'pix' and pix.anime:
                    if pix.anime.state() == QAbstractAnimation.State.Running:  ## running
                        pix.anime.pause()       
                if pix.zValue() <= common["pathZ"]:
                    break
            self.sideCar.setPauseKey()

    def resume(self):   
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.anime:
                if pix.anime.state() == QAbstractAnimation.State.Paused:
                    pix.anime.resume()
            if pix.zValue() <= common["pathZ"]:
                break
        self.sideCar.setPauseKey()
 
    def stop(self, action=''):  ## action used by clear 
        self.clearPathsandTags()     
        for pix in self.scene.items():
            if pix.type == 'pix':
                if 'frame' in pix.fileName:
                    continue  
                if pix.anime:  ## running: 
                    pix.anime.stop()  
                if pix.part in ('left','right'):  ## let pivot thru
                    continue
                if action != 'clear':    
                    pix.reprise() 
            elif pix.zValue() <= common["pathZ"]:
                break
        self.sideCar.enablePlay() 
        self.canvas.btnPause.setText( "Pause" )
        
    def lookForStrays(self, pix):
        if pix.x < -25 or pix.x > common["ViewW"] -10:
            pix.setPos(float(random.randint(25, 100) * 2.5), pix.y)      
        if pix.y < -25 or pix.y > common["ViewH"]-10:
            pix.setPos(pix.x, random.randint(25, 100) * 1.5)

    def clearPathsandTags(self):
        self.mapper.clearTagGroup()
        self.mapper.clearPaths()  ## clears tags as well

### --------------------------------------------------------
    def savePlay(self):
        if self.canvas.pathMakerOn:  ## using load in pathMaker
            self.pathMaker.sideWays.savePath()
            return
        elif len(self.scene.items()) == 0:
            return         
        dlist = [] 
        for pix in self.scene.items():
            if pix.type in ("pix","bkg"):     
                if pix.fileName != 'flat' and \
                    not path.exists(pix.fileName):  ## note
                    continue   
            if pix.type == "pix":   
                if pix.part in ('left','right'):  ## let pivot thru
                    continue          
                dlist.append(self.savePix(pix))
            elif pix.type == "bkg":
                if pix.fileName != 'flat': 
                    dlist.append(self.saveBkg(pix))
                else:
                    dlist.append(self.saveFlat(pix))
        if dlist:
            self.sideCar.saveToJson(dlist)
        else:
            MsgBox("savePlay: Error saving file")
 
    def savePix(self, pix): 
        p = pix.pos() 
        tmp = {
            "fname":    os.path.basename(pix.fileName),
            "type":    "pix",
            "x":        float("{0:.2f}".format(p.x())),
            "y":        float("{0:.2f}".format(p.y())),
            "z":        pix.zValue(),
            "mirror":   pix.flopped,
            "rotation": pix.rotation,
            "scale":    float("{0:.2f}".format(pix.scale)),
            "tag":      pix.tag,
            "alpha2":   float("{0:.2f}".format(pix.alpha2)), 
            "locked":   pix.locked,
            "part":     pix.part,
        }               
            
        if pix.shadowMaker.shadow != None:   
            shadow = {
                "alpha":    float("{0:.2f}".format(pix.shadowMaker.alpha)),
                "scalor":   float("{0:.2f}".format(pix.shadowMaker.scalor)),
                "rotate":   pix.shadowMaker.rotate,
                "width":    pix.shadowMaker.imgSize[0],
                "height":   pix.shadowMaker.imgSize[1],
                "pathX":    [float("{0:.2f}".format(pix.shadowMaker.path[k].x()))
                                for k in range(len(pix.shadowMaker.path))],
                "pathY":    [float("{0:.2f}".format(pix.shadowMaker.path[k].y()))
                                for k in range(len(pix.shadowMaker.path))],
                "ishidden": pix.shadowMaker.ishidden,
            }
            tmp.update(shadow)
          
        return tmp
    
    def saveBkg(self, pix): 
        tmp = {
            "fname":    os.path.basename(pix.fileName),
            "type":    "bkg",
            "x":        float("{0:.2f}".format(pix.x)),
            "y":        float("{0:.2f}".format(pix.y)),
            "z":        pix.zValue(),
            "mirror":   pix.flopped,
            "rotation": pix.rotation,
            "scale":    float("{0:.2f}".format(pix.scale)),
        }
        return tmp

    def saveFlat(self, pix):
        tmp = {
            "fname": 'flat',
            "type":  "bkg",
            "z":      pix.zValue(),
            "tag":    pix.color.name(),
        }
        return tmp
                
### ---------------------- dotsSideShow --------------------
