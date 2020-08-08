import os
import sys
import json
import random

from os import path

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *

import dotsQt

from dotsBkgItem      import *
from dotsPixItem      import PixItem

### ---------------------- dotsSideCar ---------------------
class SideCar():

    def __init__(self, parent):
        super().__init__()
 
        self.parent = parent
        self.shared = dotsQt.Shared()
        self.gridZ  = self.shared.gridZ
        
        self.gridSet = False
        self.openPlayFile = ''
    
### --------------------------------------------------------
    def loadPlay(self):
        dlist = []
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self.parent,
             "Choose a file to open", self.shared.playPath, "Files (*.play)")
        if file:
            try:
                with open(file, 'r') as fp:  ## read a play file
                    dlist = json.load(fp)
            except IOError:
                MsgBox("Error loading file")
                return
        if dlist:
            if self.parent.initMap.mapSet:
                self.parent.initMap.removeMap()
            self.parent.pixCount = self.parent.toFront(0.0)  
            for dict in dlist:          
                self.parent.pixCount += 1
                if dict['type'] == 'bkg':
                    if not path.exists(self.shared.bkgPath + dict['fname']):       
                        continue  
                    pix = BkgItem(self.shared.bkgPath + dict['fname'],
                        self.shared.viewW+2, 
                        self.shared.viewH+2,
                        self.parent)
                    ## lock all
                    pix.setFlag(QGraphicsPixmapItem.ItemIsMovable, False)
                else:
                    if not path.exists(self.shared.spritePath + dict['fname']):       
                        continue  
                    pix = PixItem(self.shared.spritePath + dict['fname'],
                        self.parent.pixCount,
                        0, 0, 
                        self.parent)
                ## set for both
                pix.x = dict['x']
                pix.y = dict['y']
                pix.setPos(pix.x,pix.y)
                pix.setZValue(dict['z']),  ## zval may not match id
                pix.setMirrored(dict['mirror']),
                pix.rotation = dict['rotation']
                pix.scale = dict['scale']             
                self.transFormPixItem(pix, pix.rotation, pix.scale)
            self.openPlayFile = file
            self.parent.disableSliders()

    def savePlay(self):
        dlist = []  
        for pix in self.parent.scene.items(Qt.AscendingOrder):
            if pix.type in "pix,bkg":
                if not path.exists(pix.fileName):
                    continue
                dict = {
                    "fname": os.path.basename(pix.fileName),
                    "type": pix.type,
                    "x": pix.x,
                    "y": pix.y,
                    "z": pix.zValue(),
                    "mirror": pix.flopped,
                    "rotation": pix.rotation,
                    "scale": pix.scale,
                    }
                dlist.append(dict)
        if dlist:
            Q = QFileDialog()
            if self.openPlayFile == '':
                self.openPlayFile = self.shared.playPath + 'tmp.play'
            f = Q.getSaveFileName(self.parent, self.shared.playPath,  
                self.openPlayFile)
            if not len(f[0]): 
                return
            elif not f[0].lower().endswith('.play'):
                MsgBox("Wrong file extention - use '.play'")    
            else:
                try:
                    with open(f[0], 'w') as fp:
                        json.dump(dlist, fp)
                        MsgBox("Saved as " +  os.path.basename(f[0]))
                except IOError:
                        MsgBox("Error loading file")
                        return
        else:
            MsgBox("Nothing saved")

### --------------------------------------------------------
    def pixTest(self):
        self.parent.pixCount = self.parent.toFront(0.0)  
        for _ in range(10):
            self.parent.pixCount += 1
            pix = PixItem(self.shared.spritePath + 'apple.png',
                    self.parent.pixCount,
                    0, 0, 
                    self.parent)
            x = int(constrain(
                    xy(self.shared.viewW),
                    pix.width, 
                    self.shared.viewW, 
                    pix.width * -self.shared.factor))
            y = int(constrain(
                    xy(self.shared.viewH),
                    pix.height, 
                    self.shared.viewH,
                    pix.height * -self.shared.factor))
            pix.x, pix.y = x, y
            pix.setPos(x,y)
            rotation = random.randrange(1, 24) * 15
            scale = random.randrange(50, 150) / 100
            self.transFormPixItem(pix, rotation, scale)
         
    def transFormPixItem(self, pix, rotation, scale):
        op = QPointF(pix.width/2, pix.height/2)
        pix.setTransformationMode(Qt.SmoothTransformation)
        pix.setTransformOriginPoint(op)
        pix.scale, pix.rotation = scale, rotation
        pix.setScale(scale)
        pix.setRotation(rotation)
        self.parent.scene.addItem(pix)

### --------------------------------------------------------
    def initGrid(self):
        self.gridGroup = QGraphicsItemGroup()
        gs = self.shared.gridSize
        pen = QPen(QColor(0,0,255))
        for i in range(int(self.shared.viewH/gs)):
            self.addLines(QGraphicsLineItem(0.0, gs*i,
                float(self.shared.viewW), gs*i), pen)
        for j in range(int(self.shared.viewW/gs)):
            self.addLines(QGraphicsLineItem(gs*j, 0.0,
                gs*j, float(self.shared.viewH)), pen)
        self.gridGroup.setZValue(self.gridZ)     
        self.parent.scene.addItem(self.gridGroup)
        self.gridSet = True

    def addLines(self, line, pen):
        line.type = 'grid'
        line.setPen(pen)
        line.setOpacity(.40)
        line.setZValue(self.gridZ)
        line.setFlag(QGraphicsLineItem.ItemIsMovable, False)
        self.gridGroup.addToGroup(line)
        
    def toggleGrid(self):
        if len(self.parent.scene.items()) == 0 or self.gridSet == False:
            self.initGrid()
        else: 
            if self.gridGroup.isVisible():
                self.gridGroup.setVisible(False)
            else:
                self.gridGroup.setVisible(True)

### --------------------------------------------------------
class MsgBox(QMessageBox):  ## thanks stackoverflow

    def __init__(self, text, pause=2):
        super().__init__()

        self.timeOut = pause
        self.setText("\n" + text)
        self.setStandardButtons(QMessageBox.NoButton)
       
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeContent)
        self.timer.start()

        self.exec_()

    def enterEvent(self, e):  
        self.close()

    def changeContent(self):
        self.timeOut -= 1
        if self.timeOut <= 0:
            self.close()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept() 

### --------------------------------------------------------
def mirrorSet(self, mirror):
    self.flopped = mirror   
    self.setPixmap(QPixmap.fromImage(
        self.imgFile.mirrored(
        horizontal=self.flopped,
        vertical=False)))
    self.setTransformationMode(Qt.SmoothTransformation)

def widthHeightSet(self):
    # sidecar.mirrorSet(self)
    brt = self.boundingRect()
    self.width = brt.width()
    self.height = brt.height()

def constrain(lastXY, objSize, panelSize, overlap):
    if lastXY + objSize > panelSize - overlap:
        return panelSize - (objSize + overlap)
    elif lastXY < overlap:
        return overlap
    else:
        return lastXY

def setCursor():
    cur = QCursor()
    cur.setPos(QDesktopWidget().availableGeometry().center())

def snapTag():
    return str(random.randrange(1000,9999)) + chr(random.randrange(65,90))

def xy(max):
    return random.randrange(-40, max+40)

### ---------------------- dotsSideCar ---------------------