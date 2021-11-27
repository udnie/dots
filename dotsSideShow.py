
import os
import json
import random

from PyQt5.QtCore    import QTimer, QAbstractAnimation, Qt
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

from dotsPixItem     import PixItem
from dotsBkgItem     import *
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
        try:
            with open(file, 'r') as fp:  ## read a play file
                dlist = json.load(fp)
        except IOError:
            MsgBox("openPlay: Error loading " + file, 5)
            return
        if dlist:
            self.mapper.clearMap()  ## just clear it
            k, b = 0, 0   ## number of pixitems, test for bkg zval
            lnn = len(dlist)
            lnn = lnn + self.mapper.toFront(0)  ## start at the top
            self.canvas.pixCount = self.mapper.toFront(0)
            for tmp in dlist:
                ## toss no shows - no msgs or log
                if tmp['type'] == 'bkg' and tmp['fname'] != 'flat' and \
                    not path.exists(paths["bkgPath"] + tmp['fname']):       
                    continue 
                elif tmp['type'] == 'pix' and \
                    not path.exists(paths["spritePath"] + tmp['fname']):       
                    continue  
                ## load and go
                if tmp['type'] == 'pix':
                    k += 1  ## counts pixitems
                    self.canvas.pixCount += 1  ## id used by mapper
                    pix = PixItem(paths["spritePath"] + tmp['fname'],
                        self.canvas.pixCount,
                        0, 0, 
                        self.canvas)  ## passing self.canvas which references self.mapper
                    tmp['z'] = lnn
                    lnn  -= 1 ## preserves front to back relationship
                    # print(tmp['type'], tmp['z'], lnn)
                elif tmp['type'] == 'bkg':  ## starts at -99.0
                    if b == 0:
                        b = common['bkgZ']
                    else:
                        b -= 1   ## could be another background or flat
                    # print(tmp['type'], tmp['z'], b)
                    tmp["z"] = b
                    if tmp['fname'] == 'flat':
                        self.canvas.initBkg.setBkgColor(QColor(tmp['tag']), tmp["z"])
                        continue 
                    else:
                        pix = BkgItem(paths["bkgPath"] + tmp['fname'], self.canvas, tmp["z"])
                        pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
                ## update pix and bkg from tmp and add to scene
                self.addPixToScene(pix, tmp)
            self.canvas.openPlayFile = file
            self.canvas.initBkg.disableBkgBtns() 
            self.dots.statusBar.showMessage("Number of Pixitems: {}".format(k),5000)
 
    def addPixToScene(self, pix, tmp):
        pix.type = tmp['type']                 
        pix.x = float("{0:.2f}".format(tmp['x']))
        pix.y = float("{0:.2f}".format(tmp['y']))
        pix.setPos(pix.x,pix.y)
        pix.setZValue(tmp['z']),  ## use the new one
        pix.setMirrored(tmp['mirror']),
        pix.rotation = tmp['rotation']
        pix.scale = float("{0:.3f}".format(tmp['scale']))

       ### ------ adding keys to an existing json file -------
        if 'tag' not in tmp.keys():  ## seriously good to know
            tmp['tag'] = ''
        else:
            pix.tag = tmp['tag'] 

        if pix.type == 'pix' and 'frame' not in pix.fileName:
            pix.locked = tmp['locked']
            pix.part = tmp['part']
            self.lookForStrays(pix)    
            
        ## may require rotation or scaling - adds to scene items
        ## and where wings are created using the 'right' wing pix
        self.sideCar.transFormPixItem(pix, pix.rotation, pix.scale)

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
                ### --- optional drop shadow -- ###
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
                if 'wings' in pix.fileName:
                    continue  ## no reprise
                if action != 'clear':    
                    pix.reprise() 
            elif pix.zValue() <= common["pathZ"]:
                break
        self.sideCar.enablePlay() 
        self.canvas.btnPause.setText( "Pause" )

    def savePlay(self):
        if self.canvas.pathMakerOn:  ## using load in pathMaker
            self.pathMaker.sideWays.savePath()
            return
        elif len(self.scene.items()) == 0:
            return
        self.savePivots()  ## saves the pivots path and xy in the right wing for later
        dlist = [] 
        for pix in self.scene.items():
            if pix.type in ("pix","bkg"):     
                if pix.fileName != 'flat' and \
                    not path.exists(pix.fileName):  ## note
                    continue   
            if pix.type == "pix": 
                if pix.part in ('left','pivot'):  ## only need the right wing
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

    def savePivots(self):
        ## save a pivots path and xy in rightWing for later
        for pix in self.scene.items(Qt.SortOrder.AscendingOrder):
            if pix.type == "pix":      
                if pix.part == 'pivot':  ## pivot comes up first
                    t = pix.tag
                    p = pix.sceneBoundingRect()
                if pix.part == 'right':  ## update the next 'right'
                    pix.tag = t
                    pix.x = p.x() + p.width()/2
                    pix.y = p.y()
     
    def savePix(self, pix):  
        tmp = {
            "fname": os.path.basename(pix.fileName),
            "type":  pix.type,
            "x":     float("{0:.2f}".format(pix.x)),
            "y":     float("{0:.2f}".format(pix.y)),
            "z":     pix.zValue(),
            "mirror":   pix.flopped,
            "rotation": pix.rotation,
            "scale":    float("{0:.2f}".format(pix.scale)),
            "tag":      pix.tag,
            "locked":   pix.locked,
            "part":     pix.part,
        }
        return tmp
    
    def saveBkg(self, pix): 
        tmp = {
            "fname": os.path.basename(pix.fileName),
            "type":  pix.type,
            "x":     float("{0:.2f}".format(pix.x)),
            "y":     float("{0:.2f}".format(pix.y)),
            "z":     pix.zValue(),
            "mirror":   pix.flopped,
            "rotation": pix.rotation,
            "scale":    float("{0:.2f}".format(pix.scale)),
        }
        return tmp

    def saveFlat(self, pix):
        tmp = {
            "fname": 'flat',
            "type":  pix.type,
            "z":     pix.zValue(),
            "tag":   pix.color.name(),
        }
        return tmp

    def lookForStrays(self, pix):
        if pix.x < -25 or pix.x > common["ViewW"] -10:
            pix.setPos(float(random.randint(25, 100) * 2.5), pix.y)      
        if pix.y < -25 or pix.y > common["ViewH"]-10:
            pix.setPos(pix.x, random.randint(25, 100) * 1.5)

    def clearPathsandTags(self):
        self.mapper.clearTagGroup()
        self.mapper.clearPaths()  ## clears tags as well
        
### ---------------------- dotsSideShow --------------------
