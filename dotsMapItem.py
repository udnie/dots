import os
import random

from os import path

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from dotsShared      import common, pathcolors

import dotsSidePath  as sidePath

### ---------------------- dotsMapItem ---------------------
''' dotsMapItem: handles the mapItem, tags and paths display.
    Includes MapItem, InitMap and TagIt classes'''
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

        self.canvas = parent
        self.scene  = parent.scene
  
        self.tagZ  = 0
        self.pathZ = common["pathZ"]
        self.pathTagZ = 0  ## only by paths

        self.mapSet = False
        self.tagSet = False
        self.pathsSet = False

        self.control = ''
        self.mapRect = QRectF()
        self.selections = []
        self.openPlayFile = ''    ## shared 

        self.pathGroup = None 
        self.tagGroup  = None
        self.pathTagGroup = None 
        self.paths = []
      
### --------------------------------------------------------
    def addSelectionsFromCanvas(self):
        if not self.selections:
            self.mapSelections()
        if self.selections:
            self.addMapItem()

    def mapSelections(self):
        self.selections = []
        rect = QRect(self.canvas.rubberBand.geometry())
        for pix in self.scene.items():
            if pix.type == 'pix':
                p = pix.sceneBoundingRect()
                x = int(p.x() + p.width()/2)
                y = int(p.y() + p.height()/2)
                if rect.contains(x, y):
                    pix.setSelected(True)
                    self.selections.append(pix.id)
            elif pix.zValue() <= self.pathZ: 
                break
 
    def addMapItem(self):
        self.removeMapItem()
        self.mapSet = True
        self.mapRect = self.mapBoundingRects()
        self.map = MapItem(self.mapRect)
        self.map.setZValue(self.toFront(50.0)) ## higher up than tags
        self.scene.addItem(self.map)

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
        for pix in self.scene.items():
            if pix.type == 'map':
                self.scene.removeItem(pix)
            elif pix.type != 'map':
                break

    def mapBoundingRects(self):
        tx, ty = common["viewW"], common["viewH"]
        bx, by = 0, 0
        for pix in self.scene.items():
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
            elif pix.zValue() <= self.pathZ:
                break
        return QRectF(tx, ty, bx-tx, by-ty)
        selections = []

    def updatePixItemPos(self):
        for pix in self.scene.items():
            if pix.type == 'pix':
                p = pix.pos()
                pix.x = int(p.x())
                pix.y = int(p.y())
            elif pix.zValue() <= self.pathZ:
                break

    def toggleMap(self):    
        if self.mapSet == False:
            self.selections = []
            for pix in self.scene.selectedItems():
                self.selections.append(pix.id)
            if self.selections or self.canvas.hasHiddenPix():
                self.addMapItem()
        else:
            self.removeMap()

### --------------------------------------------------------
    def toggleTagItems(self):  
        if self.canvas.pathMakerOn:
            return
        if self.tagSet: 
            self.clearTagGroup() 
            return
        else: 
            if self.scene.items():
                k = 0
                QTimer.singleShot(200, self.clearPaths)
                self.addTagGroup()
                for pix in self.scene.items():
                    if pix.type == 'pix' and pix.tag:  
                        self.tagIt(pix) 
                        k += 1
                    elif pix.zValue() <= self.pathZ:
                        break
                if k > 0: 
                    self.tagSet = True
                else:
                    self.clearTagGroup()

    def addTagGroup(self):
        self.tagZ = self.toFront(20.0)     
        self.tagGroup = QGraphicsItemGroup()
        self.tagGroup.setZValue(self.tagZ)     
        self.scene.addItem(self.tagGroup)
   
    def clearTagGroup(self):
        if self.tagSet:
            self.scene.removeItem(self.tagGroup)
            self.tagSet = False  

    def tagIt(self, pix):  
        p = pix.sceneBoundingRect()
        x = int(p.x() + p.width()*.25)
        y = int(p.y() + p.height()*.30)
        if  p.width() + p.height() < 30: ## too small??
            return
        tag = TagIt(self.control, pix.tag, '')
        tag.setPos(x,y)
        self.tagGroup.addToGroup(tag)

### --------------------------------------------------------
    def togglePaths(self):
        if self.canvas.pathMakerOn:
            return
        if self.pathsSet:
            self.clearPaths()
            return
        else:
            if self.scene.items():
                k = 0
                self.pathsSet = False  ## force clearPaths if fails
                QTimer.singleShot(200, self.clearTagGroup)  ## the other tags
                self.addPathGroup()
                self.addPathTagGroup()
                for pix in self.scene.items():
                    if pix.type == 'pix':
                        if  pix.tag.endswith('.path'):
                            k += self.displayPath(pix)
                        elif pix.anime and pix.anime.state() == 2: ## running
                            pix.anime.pause()
                    elif pix.zValue() <= self.pathZ:
                        break
                if k > 0: 
                    self.pathsSet = True
                else:
                    self.clearPaths()

    def addPathGroup(self):
        self.pathGroup = QGraphicsItemGroup()
        self.pathGroup.setZValue(self.pathZ)     
        self.canvas.scene.addItem(self.pathGroup)
    
    def addPathTagGroup(self):
        ## add pathTags group to keep tags separate and visible
        self.pathTagZ = self.toFront(25.0)     
        self.pathTagGroup = QGraphicsItemGroup()
        self.pathTagGroup.setZValue(self.pathTagZ)     
        self.canvas.scene.addItem(self.pathTagGroup)
        return self.pathTagZ

    def clearPaths(self):
        if self.pathGroup:     
            self.scene.removeItem(self.pathGroup)
        if self.pathTagGroup:  
            self.scene.removeItem(self.pathTagGroup)
        if self.pathsSet:
            for pix in self.scene.items():
                if pix.type == 'pix' and not pix.tag.endswith('.path'):
                    if pix.anime and pix.anime.state() == 1:  ## paused
                        if self.control != 'resume':
                            pix.anime.resume()
                elif pix.zValue() <= self.pathZ:
                    break
        self.pathsSet = False
        self.paths = []

    def displayPath(self, pix):
        tag = pix.tag 
        if 'Random' in tag: tag = tag[7:]
        ## don't add duplicates - causes performance issues
        if not tag in self.paths:
            self.paths.append(tag)
            self.addPainterPath(tag)
            return 1
        else:
            return 0

    def getColorStr(self):  
        random.seed()
        p = pathcolors
        return p[random.randint(0,len(p)-1)]

    def addPainterPath(self, tag):
        color = self.getColorStr()
        path = sidePath.pathLoader(tag) 
        pathPt = path.pointAtPercent(0.0)  ## so its consistent
        ## use painter path
        pathItem = QGraphicsPathItem(path)
        pathItem.setPen(QPen(QColor(color), 3, Qt.DashDotLine))
        pathItem.setFlag(QGraphicsPathItem.ItemIsMovable, False)
        self.pathGroup.addToGroup(pathItem)
        self.addTag(tag, color, pathPt)

    def addTag(self, tag, color, pt): ## use same offsets and color as path     
        tag = TagIt('', tag, color)   
        tag.setPos(pt)
        tag.setZValue(self.pathTagZ)  ## use pathTagZ instead of tagZ
        self.pathTagGroup.addToGroup(tag)

    def toFront(self, inc):  ## finds the highest pixitem zValue
        first = 0.0           ## returns it plus the increment
        for pix in self.scene.items():
            if pix.type == 'pix': 
                first = pix.zValue()
                break
            elif pix.zValue() <= self.pathZ:
                break
        return inc + first

    def lastZval(self, str): ## finds the lowest pix or bkg zValue
        last = 100000.0
        for itm in self.scene.items():
            if itm.type == str and itm.zValue() < last:
                last = itm.zValue()
        return last

    def setOriginPt(self, pix):
        self.updateWidthHeight(pix)
        op = QPointF(pix.width/2, pix.height/2)
        pix.setTransformOriginPoint(op)
   
    def updateWidthHeight(self, pix):
        brt = pix.boundingRect()
        pix.width = brt.width()
        pix.height = brt.height()

### --------------------------------------------------------
class TagIt(QGraphicsSimpleTextItem):

    def __init__(self, control, tag, color):
        super().__init__()

        if control in ['pause','resume'] and "Random" in tag:
            tag = tag[7:]
            self.color = QColor(0,255,127)
        elif control == 'pathMaker':
            if " 0%" in tag:
                color = QColor("LIGHTSEAGREEN")
            if len(tag.strip()) > 0: self.color = QColor(color)
        else:
            self.color = QColor(255,165,0)
            if "Random" in tag: tag = tag[0:6] 
        if color:
            self.color = QColor(color)

        self.type = 'tag'
        self.text = tag   
        self.font = QFont('Modern', 12)
        metrics   = QFontMetrics(self.font)
        self.rect = QRectF(0, 0, metrics.width(self.text)+13, 19)
        self.waypt = 0

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget): 
        brush = QBrush()
        brush.setColor(self.color)
        brush.setStyle(Qt.SolidPattern)

        painter.fillRect(self.boundingRect(), brush)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(Qt.black)
        painter.setFont(self.font)
        painter.drawText(self.boundingRect(), Qt.AlignCenter, self.text)

### --------------------- dotsMapItem ----------------------

