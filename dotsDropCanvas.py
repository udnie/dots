import os
import sys
import random

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

import dotsQt

from dotsControlView  import ControlView
from dotsPixItem      import PixItem
from dotsMapItem      import InitMap
from dotsBkgItem      import InitBkg

# from pubsub           import pub      # PyPubSub - required

mapStr = ":,\",<,>,{,},-,+,left,right,up,down,draw,shift,clone"
bkgZ   = -99.0
gridZ  = -33.0
pixZ   =  -5.0

### -------------------- dotsDropCanvas --------------------
class DropCanvas(QMainWindow):

    def __init__(self, sliders, buttons, parent):
        QMainWindow.__init__(self)

        self.parent = parent
        self.sliders = sliders 
        self.buttons = buttons

        self.scene = QGraphicsScene(self)
        self.view = ControlView(self.scene, self)

        self.shared = dotsQt.Shared()

        self.initBkg = InitBkg(self)
        self.initMap = InitMap(self)

        self.scene.setSceneRect(0, 0,
            self.shared.viewW,
            self.shared.viewH)

        self.mapSet = False
        self.gridSet = False

        self.key = ''
        self.pixCount = 0
      
        self.origin = QPoint(0,0)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)

        self.view.viewport().installEventFilter(self)
        self.view.keysSignal[str].connect(self.setKeys)

    def enterEvent(self, e):
        self.view.setFocus()

### --------------------------------------------------------
    @pyqtSlot(str)
    def setKeys(self, key):
        self.key = key
        if self.key in mapStr:
            self.sendPixKeys()
            # pub.sendMessage('setKeys', key=key)  ## pypubsub solution
            # if self.mapSet: ## already in sendPixKeys
            #     self.initMap.updateMap()  ## redraw mapper
  
    def eventFilter(self, source, e): ## mostly handles mapping selections
        if source is self.view.viewport():
            if e.type() == QEvent.MouseButtonPress:
                if self.key == 'draw':
                    self.initMap.updatePixItemPos()
                    self.initMap.clearMap()
                    self.unSelect()
                    self.origin = QPoint(e.pos())
                    self.rubberBand.show()
                elif self.hasHiddenPix() and len(self.initMap.selections) > 0:
                    self.initMap.updatePixItemPos()
            elif e.type() == QEvent.MouseMove:
                if self.key == 'draw' and self.origin != QPoint(0,0):
                    self.rubberBand.setGeometry(QRect(self.origin, 
                        e.pos()).normalized())
                elif self.mapSet and len(self.scene.selectedItems()) == 0:
                    self.initMap.removeMap()
                else:
                    self.initMap.updatePixItemPos()  ## costly but necessary
            elif e.type() == QEvent.MouseButtonRelease:
                if self.mapSet == False:
                    self.rubberBand.hide()
                    self.initMap.addMapSelections()
                elif self.mapSet and self.key == 'draw':
                    self.setKeys('')
                elif self.hasHiddenPix() and self.key != 'draw':
                    self.initMap.removeMap()
                elif self.mapSet and len(self.scene.selectedItems()) == 0:
                    self.initMap.removeMap()
            elif e.type() == QEvent.MouseButtonDblClick and self.key != 'draw':
                ## to preseve selections dblclk on an selection otherwise it 
                ## will unselect all - possibly a default as it works the 
                ## same as single click outside the map area 
                if len(self.initMap.selections) > 0 or self.hasHiddenPix():
                    if self.mapSet:
                        self.initMap.removeMap()
                        self.setKeys('noMap')
        return QWidget.eventFilter(self, source, e)
        
### --------------------------------------------------------
    def addPixItem(self, imgFile, x, y, clone, mirror):
        self.pixCount += 1
        pix = PixItem(imgFile, x, y, self.pixCount, self, mirror)
        if clone != None:
            self.transFormPixItem(pix,
                clone.rotation,
                clone.scale * 1.0)
        else:
            self.scene.addItem(pix)

    def sendPixKeys(self):
        for pix in self.scene.items(): 
            if pix.zValue() > pixZ and pix.type == 'pix':
                pix.setPixKeys(self.key)
            elif pix.zValue() < pixZ: 
                break
        if self.mapSet: 
            self.initMap.updateMap()
              
    def clear(self):
        if len(self.scene.items()) > 0:
            self.initMap.clearMap()
            self.scene.clear()
            self.pixCount = 0
            self.disableSliders()
            self.gridSet = False

    def disableSliders(self):
        self.sliders.enableSliders(False)
        self.buttons.btnSetBkg.setEnabled(False)
        self.buttons.btnSave.setEnabled(False)
 
    def selectAll(self):
        for pix in self.scene.items():
            if pix.zValue() > pixZ and pix.type == 'pix':
                pix.setSelected(True)
                pix.isHidden = False
            elif pix.zValue() < pixZ: 
                break

    def unSelect(self):
        for pix in self.scene.items():
            if pix.zValue() > pixZ and pix.type == 'pix':
                pix.isHidden = False
                pix.setSelected(False)
            elif pix.zValue() < pixZ: 
                break
        self.initMap.clearMap()

    def deleteSelected(self):
        for pix in self.scene.selectedItems():
            if pix.type == 'pix':
                self.scene.removeItem(pix)
        self.initMap.clearMap()

    def flopSelected(self):
        for pix in self.scene.items():
            if pix.zValue() > pixZ and pix.type == 'pix':
                if pix.isSelected() or pix.isHidden:
                    if pix.flopped:
                        pix.setMirrored(False)
                    else:
                        pix.setMirrored(True)
            elif pix.zValue() < pixZ: 
                break

    def toFront(self, inc): # handles pix and map
        first = 0.0 
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.zValue() > first:
                first = pix.zValue()
        return inc + first

    def lastZval(self, str):
        last = 100000.0
        for itm in self.scene.items():
            if itm.type == str and itm.zValue() < last:
                last = itm.zValue()
        return last

    def ZDump(self):
        for pix in self.scene.items(Qt.AscendingOrder):
            if pix.zValue() != -33.0:  ## skip grid zvalue
                print(pix.type + "  " + str(pix.zValue()))
        print("bkg: " + str(self.hasBackGround()))

    def hasBackGround(self):
        k = 0
        for pix in self.scene.items(Qt.AscendingOrder):
            if pix.zValue() <= bkgZ and pix.type == 'bkg':
                k += 1
            elif pix.zValue() > bkgZ:  
                break
        return k

    def hasHiddenPix(self):
        for pix in self.scene.items():
            if pix.zValue() > pixZ and pix.type == 'pix':
                if pix.isHidden: return True  ## found one
        return False

    ## added dlbclk if hidden to re-select ##
    def hideSelected(self): 
        for pix in self.scene.items():
            if pix.zValue() > pixZ and pix.type == 'pix':
                if pix.isSelected():
                    pix.setSelected(False)
                    pix.isHidden = True
                elif pix.isHidden:
                    pix.setSelected(True)
                    pix.isHidden = False
        if self.mapSet and self.hasHiddenPix():        
            self.initMap.removeMap()
        
### --------------------------------------------------------
    def pixTest(self):
        for _ in range(10):
            self.pixCount += 1
            pix = PixItem(self.shared.imagePath + 'image.png',
                    0, 0, 
                    self.pixCount, self)
            x = int(dotsQt.constrain(
                    xy(self.shared.viewW),
                    pix.width, 
                    self.shared.viewW, 
                    pix.width * -self.shared.factor))
            y = int(dotsQt.constrain(
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
        self.scene.addItem(pix)
   
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
        self.gridGroup.setZValue(gridZ)     
        self.scene.addItem(self.gridGroup)
        self.gridSet = True

    def addLines(self, line, pen):
        line.type = 'grid'
        line.setPen(pen)
        line.setOpacity(.40)
        line.setZValue(gridZ)
        line.setFlag(QGraphicsLineItem.ItemIsMovable, False)
        self.gridGroup.addToGroup(line)
        
    def toggleGrid(self):
        if len(self.scene.items()) == 0 or self.gridSet == False:
            self.initGrid()
        else: 
            if self.gridGroup.isVisible():
                self.gridGroup.setVisible(False)
            else:
                self.gridGroup.setVisible(True)

def xy(max):
    return random.randrange(-65, max-65)

### -------------------- dotsDropCanvas --------------------
