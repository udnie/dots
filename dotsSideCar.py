import random
import os

from os import path

from PyQt5.QtCore    import Qt, QTimer, QPointF, QPoint, QRectF,QSize, \
                            QSequentialAnimationGroup, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui     import QCursor, QPixmap, QPainter, QBrush, QFontMetrics, \
                            QPen, QPolygonF, QColor, QFont
from PyQt5.QtWidgets import QWidget, QGraphicsPixmapItem, QMessageBox, \
                            QGraphicsSimpleTextItem, QLabel, QDesktopWidget, \
                            QGraphicsItemGroup, QGraphicsLineItem, QScrollArea, \
                            QGridLayout, QVBoxLayout, QGraphicsDropShadowEffect, \
                            QGraphicsWidget, QHBoxLayout

from dotsShared      import common, paths
from dotsPixItem     import PixItem
from dotsSidePath    import getOffSet
from dotsAnimation   import Node

PlayKeys = ('resume','pause')

### ---------------------- dotsSideCar ---------------------
''' dotsSideCar: wings, pixTest, transFormPixitem, toggleGrid plus 
    some small functions '''  
### --------------------------------------------------------
class SideCar:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
        self.dots   = self.canvas.dots
        self.scene  = self.canvas.scene
        self.mapper = self.canvas.mapper
      
        self.gridZ   = common["gridZ"] 
        self.gridSet = False
        self.gridGroup = None
### --------------------------------------------------------
    ''' Things to know about wings. They're brittle, don't pull on them.
    Use the bat portion to move the bat - the pivot sprite which can be 
    found in the images folder. Main thing to know, if you need to move 
    or change an animation - do so, save it, clear and reload. Once you're 
    satified with the layout, etc. you should no longer need to resave the 
    play file. They're brittle. And it works. '''
### --------------------------------------------------------
    def wings(self, pix):
        rightWing = pix
        pathTag = pix.tag
  
        rightWing.part = 'right'
        rightWing.tag  = 'Flapper'  ## applies this animation when run
        rightWing.setZValue(rightWing.zValue() + 200)  ## reset wing zvals

        # rightWing.locked = True
        rightWing.setFlag(QGraphicsPixmapItem.ItemIsSelectable, False)
        
        self.canvas.pixCount += 1
        leftWing = PixItem(rightWing.fileName, 
            self.canvas.pixCount,
            pix.x + pix.width, pix.y, 
            self.canvas,
            True
        )  ## flop it

        leftWing.part = 'left'
        leftWing.tag  = 'Flapper'
        leftWing.setZValue(leftWing.zValue() + 200)
    
        leftWing.locked = True
        # leftWing.setFlag(QGraphicsPixmapItem.ItemIsSelectable, False) 

        self.canvas.pixCount += 1
        pivot = PixItem(paths["imagePath"] + 'bat-pivot.png', 
            self.canvas.pixCount,
            pix.x, pix.y,  
            self.canvas
        ) 

        pivot.part = 'pivot' 
        pivot.tag = pathTag 
        pivot.setZValue(pivot.zValue() + 200)

        ''' magic numbers warning - results will vary - wings seem
        to drift - this is why you don't want to resave them '''    
        half = pivot.width/2
        height = 35

        pivot.setPos(pivot.x - half, pivot.y - height)
        pivot.setScale(.55)
        pivot.setOriginPt()

        rightWing.setPos(half+10, height+2)
        leftWing.setPos(-leftWing.width+(half+5), height)

        ''' if there's a better way to bind these I'd like to know '''
        rightWing.setParentItem(pivot)  
        leftWing.setParentItem(pivot)

        self.scene.addItem(pivot) 

### --------------------------------------------------------
    def pixTest(self):
        if not self.canvas.pathMakerOn:  
            self.canvas.pixCount = self.mapper.toFront()
            for _ in range(10):
                self.canvas.pixCount += 1
                pix = PixItem(paths["spritePath"] + 'apple.png',
                        self.canvas.pixCount,
                        0, 0, 
                        self.canvas)
                x = int(constrain(
                        self.xy(common["ViewW"]),
                        pix.width, 
                        common["ViewW"], 
                        pix.width * -common["factor"]))
                y = int(constrain(
                        self.xy(common["ViewH"]),
                        pix.height, 
                        common["ViewH"],
                        pix.height * -common["factor"]))
                pix.x, pix.y = x, y
                pix.setPos(x,y)
                rotation = random.randrange(-5, 5) * 5
                scale = random.randrange(95, 105)/100.0
                self.transFormPixItem(pix, rotation, scale)
         
    def transFormPixItem(self, pix, rotation, scale):
        op = QPointF(pix.width/2, pix.height/2)
        pix.setTransformationMode(Qt.SmoothTransformation)
        pix.setTransformOriginPoint(op)
        pix.scale, pix.rotation = scale, rotation
        pix.setScale(scale)
        pix.setRotation(rotation)

        if 'wings' in pix.fileName:  
            self.wings(pix)
        else:
            self.scene.addItem(pix)

        # shadow = QGraphicsDropShadowEffect(blurRadius=10, xOffset=10, yOffset=5)
        # pix.setGraphicsEffect(shadow)

    def xy(self, max):
        return random.randrange(-40, max+40)

### --------------------------------------------------------
    def toggleGrid(self):
        if self.gridSet:
            self.scene.removeItem(self.gridGroup)
            self.gridSet = False
        else: 
            self.gridGroup = QGraphicsItemGroup()  
            self.gridGroup.setZValue(common["gridZ"])
            self.scene.addItem(self.gridGroup)
            self.gridSet = True

            gs = common["gridSize"]
            pen = QPen(QColor(0,0,255))
         
            for y in range(1, int(common["ViewH"]/gs)):
                self.addLines(QGraphicsLineItem(0.0, gs*y,
                    float(common["ViewW"]), gs*y), pen)
  
            for x in range(1, int(common["ViewW"]/gs)):
                self.addLines(QGraphicsLineItem(gs*x, 0.0,
                    gs*x, float(common["ViewH"])), pen)
        
    def addLines(self, line, pen):
        line.type = 'grid'
        line.setPen(pen)
        line.setOpacity(common["factor"])
        line.setZValue(common["gridZ"])
        line.setFlag(QGraphicsLineItem.ItemIsMovable, False)
        self.gridGroup.addToGroup(line)

    def setPauseKey(self):        
        if self.canvas.control == 'pause': 
            self.dots.btnPause.setText( "Resume" );
            self.canvas.control = 'resume'
        elif self.canvas.control == 'resume':
            self.dots.btnPause.setText( "Pause" );
            self.canvas.control = 'pause'

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

    def clearPathsandTags(self):
        self.mapper.clearTagGroup()
        self.mapper.clearPaths()  ## clears tags as well

### --------------------------------------------------------
def mirrorSet(self, mirror):
    self.flopped = mirror   
    self.setPixmap(QPixmap.fromImage(self.imgFile.mirrored(
        horizontal=self.flopped, vertical=False)))
    self.setTransformationMode(Qt.SmoothTransformation)

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

def itemsPixcount(self):   ## not used
    return sum(
        pix.type == 'pix' 
        for pix in self.canvas.scene.items()
    )

### ---------------------- dotsSideCar ---------------------




