import os
import sys
import json
import time

from os import path

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from dotsPixItem     import PixItem
from dotsBkgItem     import *
from dotsShared      import common, paths
from dotsSideCar     import MsgBox

### ---------------------- dotsSideShow --------------------
''' dotsSideShow: handles play, pause, stop '''
### --------------------------------------------------------
class SideShow():

    def __init__(self, parent):
        super().__init__()
 
        self.canvas  = parent
        self.scene   = parent.scene
        self.dots    = parent.dots
        self.mapper  = parent.mapper

        self.animation = parent.animation
        self.pathMaker = parent.pathMaker

        self.runThis = 'demo.path'
        self.pathZ = common["pathZ"]
 
### --------------------------------------------------------
    def runDemo(self, file):
        if not self.scene.items():
            self.openPlay(paths["playPath"] + file)
            QTimer.singleShot(250, self.dummy)
            self.play()
            return
        else:
            MsgBox("RunDemo: Clear Screen First")

    def dummy(self):
        pass

    def keysInPlay(self, key):
        if key == 'L':
            if self.canvas.openPlayFile == '' and \
                self.canvas.control == '':
                self.loadPlay()
                return
        elif key == 'O':  ## always
            self.mapper.togglePaths() 
            return
        elif key == 'P' and self.canvas.control == '':  
            self.play()   ## show paths once its running
            return
        elif key == 'S' and self.canvas.control != '':
            self.stop()
        
    def loadPlay(self):
        if self.canvas.pathMakerOn:
            self.pathMaker.openFiles()
            return
        else:
            dlist = []
            Q = QFileDialog()
            options = Q.Options()
            options |= Q.DontUseNativeDialog  ## used to work without it
            file, _ = Q.getOpenFileName(self.canvas,  ## only way to delete
                "Choose a file to open", paths["playPath"], "Files (*.play)",
                None, options)

            if file:
                self.openPlay(file)   
            else:
                return

    def openPlay(self, file):
        try:
            with open(file, 'r') as fp:  ## read a play file
                dlist = json.load(fp)
        except IOError:
            MsgBox("openPlay: Error loading file")
            return
        if dlist:
            if self.mapper.mapSet:
                self.mapper.removeMap()
            k = 0
            self.canvas.pixCount = self.mapper.toFront(0.0)  
            for tmp in dlist:          
                self.canvas.pixCount += 1
                if tmp['type'] == 'bkg':
                    if not path.exists(paths["bkgPath"] + tmp['fname']):       
                        continue  
                    pix = BkgItem(paths["bkgPath"] + tmp['fname'],
                        self.canvas)
                    ## lock all
                    pix.setFlag(QGraphicsPixmapItem.ItemIsMovable, False)
                else:
                    if not path.exists(paths["spritePath"] + tmp['fname']):       
                        continue  ## could be outside of paths or deleted
                    k += 1
                    pix = PixItem(paths["spritePath"] + tmp['fname'],
                        self.canvas.pixCount,
                        0, 0, 
                        self.canvas)  ## passing self.canvas which references self.mapper
                ## set for both
                pix.x = tmp['x']
                pix.y = tmp['y']
                pix.setPos(pix.x,pix.y)
                if tmp['type'] == 'bkg':
                    pix.setZValue(tmp['z']),  ## zval may not match id
                pix.setMirrored(tmp['mirror']),
                pix.rotation = tmp['rotation']
                pix.scale = tmp['scale'] 
                if 'tag' not in tmp.keys():  ## seriously good to know
                    tmp['tag'] = ''
                else:
                    pix.tag = tmp['tag']        
                ## may require rotation or scaling 
                self.canvas.sideCar.transFormPixItem(pix, pix.rotation, pix.scale)
            self.canvas.openPlayFile = file
            self.canvas.initBkg.disableSliders()
            self.dots.statusBar.showMessage("Number of Pixitems:  {}".format(k),5000)
 
    def play(self):  
        if self.canvas.control != '': 
            return
        if self.mapper.mapSet:   
            self.mapper.clearMap()
        self.clearPathsandTags()  
        self.canvas.unSelect()
        if not self.canvas.pathList:  ## should already exist - moved from animations
            self.canvas.pathList = self.pathMaker.getPathList(True)       
        k, r = 0, 0  ## k counts all non r items (demo)
        scale = .65
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.tag:
                ## if random, slice to length, display actual anime if paused 
                if 'Random' in pix.tag:
                    pix.tag = pix.tag[0:len('Random')]
                if pix.tag.endswith(self.runThis) and r >= 0:  
                    pix.scale = scale * (67-(r*3))/100.0  ## 3 * 22 screen items
                pix.anime = self.animation.setAnimation(          
                    pix.tag, 
                    pix)   
                k += 1
                if pix.tag.endswith(self.runThis):  ## increase the delay to start  
                    r += 1
                    QTimer.singleShot(100 + (r * 50), pix.anime.start)
                else:
                    if pix.anime: pix.anime.start()
            elif pix.zValue() <= self.pathZ:
                break 
        if k > 0:
            self.disablePlay()  
            self.canvas.control = 'pause'
   
    def pause(self):
        self.clearPathsandTags()  
        if self.canvas.control == 'resume':
           self.resume()
        else:          
            for pix in self.scene.items():
                if pix.type == 'pix' and pix.anime:
                    if pix.anime.state() == 2: ## running
                        pix.anime.pause()
                if pix.zValue() <= self.pathZ:
                    break
            self.setPauseKey()

    def resume(self):   
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.anime:
                if pix.anime.state() == 1: ## paused
                    pix.anime.resume()
            if pix.zValue() <= self.pathZ:
                break
        self.setPauseKey()
 
    def stop(self, clear=''):
        self.clearPathsandTags()    
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.anime:
                pix.anime.stop()
                ## reprise not run if clearing screen 
                if not clear: pix.reprise() 
            elif pix.zValue() <= self.pathZ:
                break
        self.enablePlay() 
      
    def savePlay(self):
        if self.canvas.pathMakerOn:
            self.pathMaker.savePath()
            return
        else:
            dlist = []  
            for pix in self.scene.items(Qt.AscendingOrder):
                if pix.type in ("pix","bkg"):
                    if not path.exists(pix.fileName):
                        next
                    tmp = {
                        "fname": os.path.basename(pix.fileName),
                        "type": pix.type,
                        "x": pix.x,
                        "y": pix.y,
                        "z": pix.zValue(),
                        "mirror": pix.flopped,
                        "rotation": pix.rotation,
                        "scale": pix.scale,
                        "tag": pix.tag,
                    }
                    dlist.append(tmp)
            if dlist:
                Q = QFileDialog()
                if self.canvas.openPlayFile == '':
                    self.canvas.openPlayFile = paths["playPath"] + 'tmp.play'
                f = Q.getSaveFileName(self.canvas, 
                    paths["playPath"],  
                    self.canvas.openPlayFile)
                if not f[0]: 
                    return
                if not f[0].lower().endswith('.play'):
                    MsgBox("savePlay: Wrong file extention - use '.play'")  
                    return
                else:
                    try:
                        with open(f[0], 'w') as fp:
                            json.dump(dlist, fp)
                    except IOError:
                            MsgBox("savePlay: Error saving file")
                            return

### -------------------------------------------------------- 
    def clearPathsandTags(self):
        if self.mapper.pathsSet: 
            self.mapper.clearPaths()
        if self.mapper.tagSet:   
            self.mapper.clearTagGroup()

    def enablePlay(self):
        self.canvas.control = ''
        self.dots.btnPlay.setEnabled(True)
        self.dots.btnPause.setEnabled(False)
        self.dots.btnStop.setEnabled(False) 
 
    def disablePlay(self):
        self.canvas.control = 'pause'
        self.dots.btnPlay.setEnabled(False)
        self.dots.btnPause.setEnabled(True)
        self.dots.btnStop.setEnabled(True)  

    def setPauseKey(self):        
        if self.canvas.control == 'pause': 
            self.dots.btnPause.setText( "Resume" );
            self.canvas.control = 'resume'
        elif self.canvas.control == 'resume':
            self.dots.btnPause.setText( "Pause" );
            self.canvas.control = 'pause'

### ---------------------- dotsSideShow --------------------
