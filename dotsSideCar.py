import os
import sys
import json
import random

from os import path

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *

from dotsShared      import common, paths
from dotsBkgItem     import *
from dotsPixItem     import PixItem

### ---------------------- dotsSideCar ---------------------
''' dotsSideCar: handles the load, save, pixtest, and grid 
    functions as well as the MsgBox class  '''
### --------------------------------------------------------
class SideCar():

    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
        self.gridZ  = common["gridZ"] 

        self.gridSet = False
        self.openPlayFile = ''
    
### --------------------------------------------------------
    def loadPlay(self):
        dlist = []
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self.canvas,
             "Choose a file to open", paths["playPath"], "Files (*.play)")
        if file:
            try:
                with open(file, 'r') as fp:  ## read a play file
                    dlist = json.load(fp)
            except IOError:
                MsgBox("Error loading file")
                return
        if dlist:
            if self.canvas.initMap.mapSet:
                self.canvas.initMap.removeMap()
            self.canvas.pixCount = self.toFront(0.0)  
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
                self.transFormPixItem(pix, pix.rotation, pix.scale)
            self.openPlayFile = file
            self.canvas.disableSliders()

    def savePlay(self):
        dlist = []  
        for pix in self.canvas.scene.items(Qt.AscendingOrder):
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
                    "tag": pix.tag,
                }
                dlist.append(dict)
        if dlist:
            Q = QFileDialog()
            if self.openPlayFile == '':
                self.openPlayFile = paths["playPath"] + 'tmp.play'
            f = Q.getSaveFileName(self.canvas, 
                paths["playPath"],  
                self.openPlayFile)
            if not f[0]: 
                return
            elif not f[0].lower().endswith('.play'):
                MsgBox("Wrong file extention - use '.play'")    
            else:
                try:
                    with open(f[0], 'w') as fp:
                        json.dump(dlist, fp)
                        # MsgBox("Saved as " +  os.path.basename(f[0]))
                except IOError:
                        MsgBox("Error loading file")
                        return
        else:
            MsgBox("Nothing saved")

### --------------------------------------------------------
    def pixTest(self):
        self.canvas.pixCount = self.toFront(0.0)  
        for _ in range(10):
            self.canvas.pixCount += 1
            pix = PixItem(paths["spritePath"] + 'apple.png',
                    self.canvas.pixCount,
                    0, 0, 
                    self.canvas)
            x = int(constrain(
                    xy(common["viewW"]),
                    pix.width, 
                    common["viewW"], 
                    pix.width * -common["factor"]))
            y = int(constrain(
                    xy(common["viewH"]),
                    pix.height, 
                    common["viewH"],
                    pix.height * -common["factor"]))
            pix.x, pix.y = x, y
            pix.setPos(x,y)
            rotation = random.randrange(1, 24) * 15
            scale = random.randrange(50, 150)/100.0
            self.transFormPixItem(pix, rotation, scale)
         
    def transFormPixItem(self, pix, rotation, scale):
        op = QPointF(pix.width/2, pix.height/2)
        pix.setTransformationMode(Qt.SmoothTransformation)
        pix.setTransformOriginPoint(op)
        pix.scale, pix.rotation = scale, rotation
        pix.setScale(scale)
        pix.setRotation(rotation)
        self.canvas.scene.addItem(pix)
  
    def toFront(self, inc):  ## finds the highest pixitem zValue
        first = 0.0           ## returns it plus the increment
        for pix in self.canvas.scene.items():
            if pix.type == 'pix': 
                first = pix.zValue()
                break
            elif pix.zValue() <= self.gridZ:
                break
        return inc + first

    def lastZval(self, str): ## finds the lowest pix or bkg zValue
        last = 100000.0
        for itm in self.canvas.scene.items():
            if itm.type == str and itm.zValue() < last:
                last = itm.zValue()
        return last

### --------------------------------------------------------
    def initGrid(self):
        self.gridGroup = QGraphicsItemGroup()
        gs = common["gridSize"]
        pen = QPen(QColor(0,0,255))
        for i in range(int(common["viewH"]/gs)):
            self.addLines(QGraphicsLineItem(0.0, gs*i,
                float(common["viewW"]), gs*i), pen)
        for j in range(int(common["viewW"]/gs)):
            self.addLines(QGraphicsLineItem(gs*j, 0.0,
                gs*j, float(common["viewH"])), pen)
        self.gridGroup.setZValue(self.gridZ)     
        self.canvas.scene.addItem(self.gridGroup)
        self.gridSet = True

    def addLines(self, line, pen):
        line.type = 'grid'
        line.setPen(pen)
        line.setOpacity(common["factor"])
        line.setZValue(self.gridZ)
        line.setFlag(QGraphicsLineItem.ItemIsMovable, False)
        self.gridGroup.addToGroup(line)
        
    def toggleGrid(self):
        if not self.canvas.scene.items() or self.gridSet == False:
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
    # sideCar.mirrorSet(self)
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

## save for now
    # timer = QTimer()
    # timer.start(50)
    # timer.setSingleShot(True)
    # QTimer.singleShot(1000, self.hide)

### ---------------------- dotsSideCar ---------------------

