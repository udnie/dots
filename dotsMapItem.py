import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import dotsQt

### ---------------------- dotsMapItem ---------------------
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

        self.parent = parent
        self.mapRect = None

        self.shared = dotsQt.Shared()
        self.gridZ = self.shared.gridZ

        self.selections = []
        self.mapSet = False

### --------------------------------------------------------
    def addSelectionsFromCanvas(self):
        if len(self.selections) == 0:
            self.mapSelections()
        if len(self.selections) > 0:
            self.addMapItem()

    def mapSelections(self):
        self.selections = []
        rect = QRect(self.parent.rubberBand.geometry())
        for pix in self.parent.scene.items():
            if pix.zValue() > self.gridZ and pix.type == 'pix':
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
        self.map.setZValue(self.parent.toFront(10.0))
        self.parent.scene.addItem(self.map)

    def updateMap(self):
        self.updatePixItemPos()
        self.addMapItem()

    def removeMap(self):
        self.updatePixItemPos()
        self.clearMap()

    def clearMap(self):
        self.removeMapItem()
        self.origin = QPoint(0,0)
        self.mapRect = None
        self.selections = []
        self.mapSet = False
        self.parent.rubberBand.setGeometry(QRect(self.origin, QSize()))

    def removeMapItem(self):
        for pix in self.parent.scene.items():
            if pix.zValue() > self.gridZ  and pix.type == 'map':
                self.parent.scene.removeItem(pix)
            elif pix.type != 'map': 
                break

    def mapBoundingRects(self):
        tx, ty = self.shared.viewW, self.shared.viewH
        bx, by = 0, 0
        for pix in self.parent.scene.items():
            if pix.type == 'pix':
                if pix.id in self.selections:
                    p = pix.sceneBoundingRect()
                    x, y, w, h = p.x(), p.y(), p.width(), p.height()
                    if x < tx:
                        tx = x
                    if y < ty:
                        ty = y
                    if x + w > bx:
                        bx = x + w
                    if y + h > by:
                        by = y + h
            elif pix.zValue() <= self.gridZ:
                break
        return QRectF(tx, ty, bx-tx, by-ty)

    def updatePixItemPos(self):
        for pix in self.parent.scene.items():
            if pix.type == 'pix':
                if pix.id in self.selections or pix.isSelected():
                    p = pix.pos()
                    pix.x = int(p.x())
                    pix.y = int(p.y())
                    pix.setPos(pix.x, pix.y)
            elif pix.zValue() <= self.gridZ:
                break

    def toggleMap(self):    
        if self.mapSet == False:
            self.selections = []
            for pix in self.parent.scene.selectedItems():
                self.selections.append(pix.id)
            if len(self.selections) > 0 or self.parent.hasHiddenPix():
                self.addMapItem()
        else:
            self.removeMap()

### --------------------- dotsMapItem ----------------------



