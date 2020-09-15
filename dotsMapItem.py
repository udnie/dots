import os

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from dotsShared      import common

### ---------------------- dotsMapItem ---------------------
''' dotsMapItem: handles the mapItem selection box.
    Includes MapItem and InitMap classes. '''
### --------------------------------------------------------
class MapItem(QGraphicsItem):

    def __init__(self, rect):
        super().__init__()

        self.rect = rect
        self.type = 'map'

        self.pen = QPen(Qt.SolidLine)
        self.pen.setColor(Qt.white)
        self.pen.setWidth(1)

        self.setFlag(QGraphicsItem.ItemIsMovable, True)

### --------------------------------------------------------
    def boundingRect(self):
        return QRectF(self.rect)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.setBrush(QColor(120,120,120,50))
        painter.drawRect(self.rect)

    def mousePressEvent(self, e):
        QGraphicsItem.mousePressEvent(self, e)

    def mouseMoveEvent(self, e):
        QGraphicsItem.mouseMoveEvent(self, e)

    def mouseReleaseEvent(self, e):
        QGraphicsItem.mouseReleaseEvent(self, e)

### ---------------------- dotsMapItem ---------------------
class InitMap(QWidget):

    def __init__(self, parent):
        super().__init__()

        self.canvas  = parent
        self.sideCar = self.canvas.sideCar

        self.gridZ   = common["gridZ"]
        self.mapRect = QRectF()
        self.mapSet  = False
        self.selections = []
      
### --------------------------------------------------------
    def addSelectionsFromCanvas(self):
        if not self.selections:
            self.mapSelections()
        if self.selections:
            self.addMapItem()

    def mapSelections(self):
        self.selections = []
        rect = QRect(self.canvas.rubberBand.geometry())
        for pix in self.canvas.scene.items():
            if pix.type == 'pix':
                p = pix.sceneBoundingRect()
                x = int(p.x() + p.width()/2)
                y = int(p.y() + p.height()/2)
                if rect.contains(x, y):
                    pix.setSelected(True)
                    self.selections.append(pix.id)
            elif pix.zValue() <= self.gridZ: 
                break
 
    def addMapItem(self):
        self.removeMapItem()
        self.mapSet = True
        self.mapRect = self.mapBoundingRects()
        self.map = MapItem(self.mapRect)
        self.map.setZValue(self.canvas.sideCar.toFront(40.0)) ## higher up than tags
        self.canvas.scene.addItem(self.map)

    def updateMap(self):
        self.updatePixItemPos()
        self.addMapItem()

    def removeMap(self):
        self.updatePixItemPos()
        self.clearMap()

    def clearMap(self):
        if self.mapSet:
            self.removeMapItem()
            self.mapRect = QRectF()
            self.selections = []
            self.mapSet = False
            self.canvas.rubberBand.setGeometry(
                QRect(self.canvas.origin, 
                QSize(0,0)))

    def removeMapItem(self):
        for pix in self.canvas.scene.items():
            if pix.type == 'map':
                pix.clearFocus()
                self.canvas.scene.removeItem(pix)
            elif pix.type != 'map':
                break

    def mapBoundingRects(self):
        tx, ty = common["viewW"], common["viewH"]
        bx, by = 0, 0
        for pix in self.canvas.scene.items():
            if pix.type == 'pix' and pix.id in self.selections:
                p = pix.sceneBoundingRect()
                x, y, w, h = p.x(), p.y(), p.width(), p.height()
                if x < tx:  ## setting top left
                    tx = x
                if y < ty:
                    ty = y
                if x + w > bx:  ## setting bottom right
                    bx = x + w
                if y + h > by:
                    by = y + h
            elif pix.zValue() <= self.gridZ:
                break
        return QRectF(tx, ty, bx-tx, by-ty)

    def updatePixItemPos(self):
        for pix in self.canvas.scene.items():
            if pix.type == 'pix':
                p = pix.pos()
                pix.x = int(p.x())
                pix.y = int(p.y())
            elif pix.zValue() <= self.gridZ:
                break

    def toggleMap(self):    
        if self.mapSet == False:
            self.selections = []
            for pix in self.canvas.scene.selectedItems():
                self.selections.append(pix.id)
            if self.selections or self.canvas.hasHiddenPix():
                self.addMapItem()
        else:
            self.removeMap()

### --------------------- dotsMapItem ----------------------

