import random
import os

from os import path

from PyQt5.QtCore    import Qt, QTimer, QPointF, QPoint, pyqtSlot, QRectF,QSize
from PyQt5.QtGui     import QCursor, QPixmap, QPainter, QBrush, QFontMetrics, \
                            QPen, QPolygonF, QColor, QFont
from PyQt5.QtWidgets import QWidget, QGraphicsPixmapItem, QMessageBox, \
                            QGraphicsSimpleTextItem, QLabel, QDesktopWidget, \
                            QGraphicsItemGroup, QGraphicsLineItem, QScrollArea, \
                            QGridLayout, QVBoxLayout, QGraphicsDropShadowEffect, \
                            QGraphicsWidget

from dotsShared      import common, paths
from dotsPixItem     import PixItem

PlayKeys = ('resume','pause')

### ---------------------- dotsSideCar ---------------------
''' dotsSideCar: DoodleMaker, Pointitem, Doodle, and TagIt classes 
    used by pathMaker and pathMaker also pixTest, transFormPixitem, 
    toggleGrid and MsgBox plus some small functions '''
### --------------------------------------------------------
class SideCar():
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.parent = parent
        self.scene  = parent.scene
        self.mapper = parent.mapper
      
        self.gridZ   = common["gridZ"] 
        self.gridSet = False
        self.gridGroup = None

### --------------------------------------------------------
    def pixTest(self):
        if not self.parent.pathMakerOn:  
            self.parent.pixCount = self.mapper.toFront()
            for _ in range(10):
                self.parent.pixCount += 1
                pix = PixItem(paths["spritePath"] + 'apple.png',
                        self.parent.pixCount,
                        0, 0, 
                        self.parent)
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
        self.scene.addItem(pix)

        #     shadow = QGraphicsDropShadowEffect(blurRadius=10, xOffset=10, yOffset=5)
        #     pix.setGraphicsEffect(shadow)

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
         
            for i in range(1, int(common["ViewH"]/gs)):
                self.addLines(QGraphicsLineItem(0.0, gs*i,
                    float(common["ViewW"]), gs*i), pen)
  
            for j in range(1, int(common["ViewW"]/gs)):
                self.addLines(QGraphicsLineItem(gs*j, 0.0,
                    gs*j, float(common["ViewH"])), pen)
        
    def addLines(self, line, pen):
        line.type = 'grid'
        line.setPen(pen)
        line.setOpacity(common["factor"])
        line.setZValue(common["gridZ"])
        line.setFlag(QGraphicsLineItem.ItemIsMovable, False)
        self.gridGroup.addToGroup(line)

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
        for pix in self.parent.scene.items()
    )

### ---------------------- dotsSideCar ---------------------

