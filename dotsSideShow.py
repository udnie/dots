import os
import sys
import json
import time

from os import path

from PyQt5.QtCore    import QTimer
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

from dotsPixItem     import PixItem
from dotsBkgItem     import *
from dotsShared      import common, paths
from dotsSideGig     import MsgBox, getPathList

### ---------------------- dotsSideShow --------------------
''' dotsSideShow: handles play, pause, stop '''
### --------------------------------------------------------
class SideShow():
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas  = parent
        self.scene   = parent.scene
        self.dots    = parent.dots
        self.mapper  = parent.mapper

        self.animation = parent.animation
        self.pathMaker = parent.pathMaker

### --------------------------------------------------------
    def runThis(self, file):
        if not self.scene.items():
            self.openPlay(paths["playPath"] + file)
            QTimer.singleShot(200, self.dummy)
            self.run()
  
    def dummy(self):
        pass
    
    def keysInPlay(self, key):
        if key == 'L':
            if self.canvas.openPlayFile == '' and \
                self.canvas.control == '':
                self.loadPlay()
                return
            else:
                pass
        elif key == 'P':  ## always
            self.mapper.togglePaths() 
            return
        elif key == 'R':    
            if len(self.scene.items()) == 0:
                self.runThis(common['runThis'])  
            else:
                self.run()
            return
        elif key == 'S' and self.canvas.control != '':
            self.stop()
        
    def loadPlay(self):
        if self.canvas.pathMakerOn:       ## using load in pathMaker
            self.pathMaker.sideWays.openFiles()
            return
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
                ## toss no shows
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
                        pix.setFlag(QGraphicsPixmapItem.ItemIsMovable, False)
                ## update pix and bkg from tmp and add to scene
                self.addPixToScene(pix, tmp)
            self.canvas.openPlayFile = file
            self.canvas.initBkg.disableBkgBtns() 
            self.dots.statusBar.showMessage("Number of Pixitems:  {}".format(k),5000)
 
    def addPixToScene(self, pix, tmp):
        pix.type = tmp['type']                 
        pix.x = float("{0:.2f}".format(tmp['x']))
        pix.y = float("{0:.2f}".format(tmp['y']))
        pix.setPos(pix.x,pix.y)
        pix.setZValue(tmp['z']),  ## use the new one
        pix.setMirrored(tmp['mirror']),
        pix.rotation = tmp['rotation']
        pix.scale = float("{0:.4f}".format(tmp['scale']))
        ## ------- adding keys to an existing json file -------
        if 'tag' not in tmp.keys():  ## seriously good to know
            tmp['tag'] = ''
        else:
            pix.tag = tmp['tag'] 
        if 'locked' not in tmp.keys():  ## pix shares with bkg
            tmp['locked'] = False
        else:
            pix.locked = tmp['locked']
        ## may require rotation or scaling - adds to scene items
        self.canvas.sideCar.transFormPixItem(pix, pix.rotation, pix.scale)

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
                ''' set scale factor if demoPath '''
                if pix.tag.endswith('demo.path') and r >= 0:  
                    pix.scale = scale * (67-(r*3))/100.0  ## 3 * 22 screen items
                pix.anime = self.animation.setAnimation(          
                    pix.tag, 
                    pix)   
                k += 1
                ''' increase the delay to start animation if demoPath  '''
                if pix.tag.endswith('demo.path'):   
                    r += 1
                    QTimer.singleShot(100 + (r * 50), pix.anime.start)
                else:
                    if pix.anime: pix.anime.start()

                # shadow = QGraphicsDropShadowEffect(blurRadius=11, xOffset=8, yOffset=8)
                # pix.setGraphicsEffect(shadow)

            elif pix.zValue() <= common["pathZ"]:
                break 
        if k > 0:
            self.disablePlay()  
            self.canvas.control = 'pause'
            self.dots.statusBar.showMessage("Number of Pixitems:  {}".format(k),5000)
   
    def pause(self):
        self.clearPathsandTags()  
        if self.canvas.control == 'resume':
           self.resume()
        else:          
            for pix in self.scene.items():
                if pix.type == 'pix' and pix.anime:
                    if pix.anime.state() == 2: ## running
                        pix.anime.pause()       
                if pix.zValue() <= common["pathZ"]:
                    break
            self.setPauseKey()

    def resume(self):   
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.anime:
                if pix.anime.state() == 1: ## paused
                    pix.anime.resume()
            if pix.zValue() <= common["pathZ"]:
                break
        self.setPauseKey()
 
    def stop(self, action=''):
        self.clearPathsandTags()  
     
        for pix in self.scene.items():
            if pix.type == 'pix':
                if pix.anime: ## running: 
                    pix.anime.stop()  
                if action != 'clear': 
                    if 'frame' in pix.fileName:
                        continue  
                    pix.reprise() 
            elif pix.zValue() <= common["pathZ"]:
                break

        self.enablePlay() 
        self.dots.btnPause.setText( "Pause" )
   
    def savePlay(self):
        if self.canvas.pathMakerOn:    ## using load in pathMaker
            self.pathMaker.sideWays.savePath()
            return
        elif len(self.scene.items()) == 0:
            return
        else:
            dlist = []  
            for pix in self.scene.items():
                if pix.type in ("pix","bkg"):     
                    if pix.fileName != 'flat' and \
                        not path.exists(pix.fileName):  ## note
                        continue   
                if pix.type == "pix":      
                    dlist.append(self.returnPixBkg(pix))
                elif pix.type == "bkg":
                    if pix.fileName != 'flat': 
                        dlist.append(self.returnPixBkg(pix))
                    else:
                        dlist.append(self.returnFlat(pix))
            if dlist:
                self.saveToJson(dlist)
            else:
                MsgBox("savePlay: Error saving file")

    def saveToJson(self, dlist):
        Q = QFileDialog()
        if self.canvas.openPlayFile == '':
            self.canvas.openPlayFile = paths["playPath"] + 'tmp.play'
        f = Q.getSaveFileName(self.canvas, 
            paths["playPath"],  
            self.canvas.openPlayFile)
        if not f[0]: 
            return
        if not f[0].lower().endswith('.play'):
            MsgBox("saveToJson: Wrong file extention - use '.play'")  
            return
        else:
            try:
                with open(f[0], 'w') as fp:
                    json.dump(dlist, fp)
            except IOError:
                MsgBox("saveToJson: Error saving file")
            return

    def returnPixBkg(self, pix):  ## used by both 
        tmp = {
            "fname": os.path.basename(pix.fileName),
            "type": pix.type,
            "x": float("{0:.2f}".format(pix.x)),
            "y": float("{0:.2f}".format(pix.y)),
            "z": pix.zValue(),
            "mirror": pix.flopped,
            "rotation": pix.rotation,
            "scale": float("{0:.4f}".format(pix.scale)),
            "tag": pix.tag,
            "locked": pix.locked,
        }
        return tmp
    
    def returnFlat(self, pix):
        tmp = {
            "fname": 'flat',
            "type": pix.type,
            "z": pix.zValue(),
            "tag": pix.color.name(),
        }
        return tmp

### -------------------------------------------------------- 
    def clearPathsandTags(self):
        self.mapper.clearTagGroup()
        self.mapper.clearPaths()  ## clears tags as well

    def enablePlay(self):
        self.canvas.control = ''
        self.dots.btnRun.setEnabled(True)
        self.dots.btnPause.setEnabled(False)
        self.dots.btnStop.setEnabled(False) 
        self.dots.btnSave.setEnabled(True) 
 
    def disablePlay(self):
        self.canvas.control = 'pause'
        self.dots.btnRun.setEnabled(False)
        self.dots.btnPause.setEnabled(True)
        self.dots.btnStop.setEnabled(True)  
        self.dots.btnSave.setEnabled(False)  

    def setPauseKey(self):        
        if self.canvas.control == 'pause': 
            self.dots.btnPause.setText( "Resume" );
            self.canvas.control = 'resume'
        elif self.canvas.control == 'resume':
            self.dots.btnPause.setText( "Pause" );
            self.canvas.control = 'pause'

### ---------------------- dotsSideShow --------------------
