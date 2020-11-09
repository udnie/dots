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
        self.buttons = parent.buttons
        self.mapper  = parent.mapper

        self.animation = parent.animation
        self.pathMaker = parent.pathMaker

        self.pathZ = common["pathZ"]
 
### --------------------------------------------------------
    def setAction(self, tag):
        if self.mapper.tagSet and tag == "Clear Tags":
            self.mapper.clearTagGroup()
        for pix in self.scene.selectedItems():
            if tag == "Clear Tags":
                pix.tag = ''
            else:
                pix.tag = tag
            pix.anime = None        ## set by play
            pix.setSelected(False)  ## when tagged 
        if self.mapper.mapSet: 
            self.mapper.removeMap()

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

    def loadPlay(self):
        if self.canvas.pathMakerOn:
            self.pathMaker.openFiles()
            return
        else:
            dlist = []
            Q = QFileDialog()
            file, _ = Q.getOpenFileName(self.canvas,
                "Choose a file to open", paths["playPath"], "Files (*.play)")
            if file:
                self.openPlay(file)   
            else:
                MsgBox("loadPlay: Error loading: " + file)
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
            self.canvas.pixCount = self.mapper.toFront(0.0)  
            for dict in dlist:          
                self.canvas.pixCount += 1
                if dict['type'] == 'bkg':
                    if not path.exists(paths["bkgPath"] + dict['fname']):       
                        continue  
                    pix = BkgItem(paths["bkgPath"] + dict['fname'],
                        self.canvas)
                    ## lock all
                    pix.setFlag(QGraphicsPixmapItem.ItemIsMovable, False)
                else:
                    if not path.exists(paths["spritePath"] + dict['fname']):       
                        continue  ## could be outside of paths or deleted
                    pix = PixItem(paths["spritePath"] + dict['fname'],
                        self.canvas.pixCount,
                        0, 0, 
                        self.canvas)
                ## set for both
                pix.x = dict['x']
                pix.y = dict['y']
                pix.setPos(pix.x,pix.y)
                if dict['type'] == 'bkg':
                    pix.setZValue(dict['z']),  ## zval may not match id
                pix.setMirrored(dict['mirror']),
                pix.rotation = dict['rotation']
                pix.scale = dict['scale'] 
                if 'tag' not in dict.keys():  ## seriously good to know
                    dict['tag'] = ''
                else:
                    pix.tag = dict['tag']        
                ## may require rotation or scaling 
                self.canvas.sideCar.transFormPixItem(pix, pix.rotation, pix.scale)
            self.mapper.openPlayFile = file
            self.canvas.disableSliders()

    def play(self):   
        if self.mapper.control != '': 
            return
        if self.mapper.mapSet:   
            self.mapper.clearMap()
        self.clearPathsandTags()  
        self.canvas.unSelect()
        if not self.canvas.pathList:  ## moved from animations
            self.canvas.pathList = self.pathMaker.getPathList(True)       
        k = 0
        scale = .65
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.tag:
                ## if random, slice to length, display actual anime if paused 
                if 'Random' in pix.tag:
                    pix.tag = pix.tag[0:len('Random')]
                if pix.tag.endswith('demo.path') and k >= 0:  
                    pix.scale = (67-(k*3))/ 100.0  ## 3 * 22 screen items
                pix.anime = self.animation.setAnimation(          
                    pix.tag, 
                    pix)   
                k += 1
                if pix.tag.endswith('demo.path'):  ## increase the delay to start  
                    QTimer.singleShot(100 + (k * 50), pix.anime.start)
                else:
                    if pix.anime: pix.anime.start()
            elif pix.zValue() <= self.pathZ:
                break 
        if k > 0:
            self.disablePlay()  
            self.mapper.control = 'pause'

    def pause(self):
        self.clearPathsandTags()  
        if self.mapper.control == 'resume':
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
                if pix.type in ["pix","bkg"]:
                    if not path.exists(pix.fileName):
                        next
                    dict = {
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
                    dlist.append(dict)
            if dlist:
                Q = QFileDialog()
                if self.mapper.openPlayFile == '':
                    self.mapper.openPlayFile = paths["playPath"] + 'tmp.play'
                f = Q.getSaveFileName(self.canvas, 
                    paths["playPath"],  
                    self.mapper.openPlayFile)
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
            else:
                MsgBox("savePlay: Nothing saved")

### -------------------------------------------------------- 
    def clearPathsandTags(self):
        if self.mapper.pathsSet: 
            self.mapper.clearPaths()
        if self.mapper.tagSet:   
            self.mapper.clearTagGroup()

    def enablePlay(self):
        self.mapper.control = ''
        self.buttons.btnPlay.setEnabled(True)
        self.buttons.btnPause.setEnabled(False)
        self.buttons.btnStop.setEnabled(False) 
 
    def disablePlay(self):
        self.mapper.control = 'pause'
        self.buttons.btnPlay.setEnabled(False)
        self.buttons.btnPause.setEnabled(True)
        self.buttons.btnStop.setEnabled(True)  

    def setPauseKey(self):        
        if self.mapper.control == 'pause': 
            self.buttons.btnPause.setText( "Resume" );
            self.mapper.control = 'resume'
        elif self.mapper.control == 'resume':
            self.buttons.btnPause.setText( "Pause" );
            self.mapper.control = 'pause'

### ---------------------- dotsSideShow --------------------
