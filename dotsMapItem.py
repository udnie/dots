
from PyQt5.QtCore    import Qt, QTimer, QSize, QRectF, QRect, QAbstractAnimation
from PyQt5.QtGui     import QColor, QPen
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPathItem, QGraphicsItemGroup, \
                            QGraphicsPixmapItem

from dotsShared      import common
from dotsSideGig     import TagIt, getColorStr
from dotsSidePath    import pathLoader

All = -999

### ---------------------- dotsMapItem ---------------------
''' dotsMapItem: handles the mapItem, tags and paths display.
    Classes: MapItem, InitMap - uses self.parent for parent '''
### --------------------------------------------------------
class MapItem(QGraphicsItem):
### --------------------------------------------------------
    def __init__(self, rect, parent):
        super().__init__()

        self.mapper = parent
        self.rect = rect
        self.type = 'map'

        self.pen = QPen(Qt.PenStyle.SolidLine)
        self.pen.setColor(Qt.GlobalColor.white)
        self.pen.setWidth(1)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

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
        if self.mapper.tagSet: 
            self.mapper.clearTagGroup()
        QGraphicsItem.mouseMoveEvent(self, e)

    def mouseReleaseEvent(self, e):
        QGraphicsItem.mouseReleaseEvent(self, e)

### ---------------------- dotsMapItem ---------------------
class InitMap:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.scene  = parent.scene
        self.dots   = parent.dots

        self.tagZ = 0
        self.pathTagZ = 0  ## only by paths

        self.tagSet = False
        self.pathSet = False

        self.mapRect = QRectF()
        self.selections = []

        self.pathGroup = None 
        self.tagGroup  = None
        self.pathTagGroup = None 
        self.paths = []
      
### --------------------------------------------------------
    def addSelectionsFromCanvas(self): ## uses rubberband to select items
        k = 0
        self.selections = []
        rect = QRect(self.parent.rubberBand.geometry())
        for pix in self.scene.items():
            if pix.type == 'pix':
                if 'frame' in pix.fileName: 
                    continue
                p = pix.sceneBoundingRect()
                x = int(p.x() + p.width()/2)
                y = int(p.y() + p.height()/2)
                if rect.contains(x, y):  
                    pix.setSelected(True)
                    self.selections.append(pix.id)
                    if pix.locked:
                        pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
                    k += 1
            elif pix.zValue() <= common["pathZ"]: 
                break
        if k == 0:
            self.clearMap()
        else:
            self.addMapItem()
 
    def addMapItem(self):
        self.removeMapItem()
        self.mapRect = self.mapBoundingRects()
        self.parent.rubberBand.setGeometry(QRect(self.parent.origin, QSize()))
        self.map = MapItem(self.mapRect, self)  
        self.map.setZValue(self.toFront(50)) ## higher up than tags
        self.scene.addItem(self.map)
        k = len(self.selections)
        self.dots.statusBar.showMessage("Number Selected:  {}".format(k),2500)

    def mapBoundingRects(self):
        tx, ty = common["ViewW"], common["ViewH"]
        bx, by = 0, 0
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.isSelected():
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
            elif pix.zValue() <= common["pathZ"]:
                break
        return QRectF(tx, ty, bx-tx, by-ty)
      
    def isMapSet(self):
        for itm in self.scene.items():
            if itm.type == 'map':
                return True
        return False

    def clearMap(self):
        self.removeMapItem()
        self.mapRect = QRectF()

    def toggleMap(self):  ## not based on rubberband geometry
        if self.isMapSet() == False:
            self.selections = []  ## not the same as in drawsPaths
            for pix in self.scene.selectedItems():  ## only items selected
                self.selections.append(pix.id)
            if self.scene.selectedItems() or self.parent.hasHiddenPix():
                self.addMapItem()
        else:
            self.removeMap()

    def updateMap(self):
        self.updatePixItemPos()
        self.addMapItem()

    def removeMap(self):
        self.updatePixItemPos()
        self.clearMap()
        
    def updatePixItemPos(self):
        if len(self.scene.items()) > 0:
            for pix in self.scene.items():
                if pix.type == 'pix':
                    p = pix.pos()
                    pix.x = p.x()
                    pix.y = p.y()
                elif pix.zValue() <= common["pathZ"]:
                    break

    def removeMapItem(self):
        if len(self.scene.items()) > 0:
            for pix in self.scene.items():
                if pix.type == 'map':
                    self.scene.removeItem(pix)
                    del pix
                    break

### ------------------- tags and paths ---------------------
    def toggleTagItems(self, pid):  
        if self.parent.pathMakerOn:
            return
        if self.tagSet: 
            self.clearTagGroup()
            self.clearPaths()  
            return
        if self.isMapSet():
            self.clearMap()
        if self.scene.items():
            if self.pathSet:
                QTimer.singleShot(200, self.clearPaths)
            self.addTagGroup()
            self.tagWorks(pid)

    def tagWorks(self, pid):
        k = 0
        tf = self.toFront()  ## only once
        self.tagSet = False
        if pid == '': 
            pid = 'all'
        ## changed order - otherwise the top tag can be hidden 
        for pix in self.scene.items(Qt.SortOrder.AscendingOrder):
            if pix.type == 'pix':  
                if 'path' in pix.tag and pid == 'paths':
                    self.tagIt('paths', pix, tf) 
                    k += 1
                if pid == 'all':
                    self.tagIt('',pix, tf) 
                    k += 1
                # elif pid == 'select' and pix.isSelected():
                elif pix.isSelected():
                    self.tagIt('',pix, tf)
                    k += 1
                elif pid == pix.id:  ## single tag
                    self.tagIt('',pix, tf) 
                    k = 1
                    break
        if k > 0: 
            self.tagSet = True
            self.dots.statusBar.showMessage("Number Tagged:  {}".format(k),2500)
        else:
            self.clearTagGroup()

    def addTagGroup(self):
        self.tagZ = self.toFront(20.0)   ## otherwise it can be hidden  
        self.tagGroup = QGraphicsItemGroup()
        self.tagGroup.setZValue(self.tagZ)     
        self.scene.addItem(self.tagGroup)

    def clearTagGroup(self):
        if self.tagSet:
            self.scene.removeItem(self.tagGroup)
            self.tagGroup = None
            self.tagSet = False  

    def tagIt(self, token, pix, tf):  
        p = pix.sceneBoundingRect()
        x = p.x() + p.width()*.45
        y = p.y() + p.height()*.45

        tag = pix.tag
        color = ''

        if 'frame' in pix.fileName: 
            x, y = common["ViewW"]*.47, common["ViewH"]-35
            pix.tag = ""

        if pix.locked == True:
            tag = "Locked " + tag 

        if pix.zValue() == tf: 
            color = 'yellow'

        if token == 'paths':
            y = y - 20
        else:
            token = self.parent.control

        tag = TagIt(token, tag, color, pix.zValue())
        tag.setPos(x,y)
        tag.setZValue(self.tagZ) 
        self.tagGroup.addToGroup(tag)
        self.tagSet = True

### -------------------- mostly paths ----------------------
    def togglePaths(self):
        if self.parent.pathMakerOn:
            return
        if self.pathSet:
            self.clearPaths()
            return
        if self.scene.items():
            k = 0
            self.pathSet = False  ## force clearPaths if fails
            QTimer.singleShot(200, self.clearTagGroup)  ## the other tags
            self.addPathGroup()
            self.addPathTagGroup()
            for pix in self.scene.items():
                if pix.type == 'pix':
                    if  pix.tag.endswith('.path'):
                        k += self.displayPath(pix)
                    elif pix.anime and pix.anime.state() == QAbstractAnimation.State.Running:
                        pix.anime.pause()
                elif pix.zValue() <= common["pathZ"]:
                    break
            if k > 0: 
                self.pathSet = True
            else:
                self.clearPaths()
     
    def addPathGroup(self):
        self.pathGroup = QGraphicsItemGroup()
        self.pathGroup.setZValue(common["pathZ"])     
        self.scene.addItem(self.pathGroup)
    
    def addPathTagGroup(self):
        ## add pathTags group to keep tags separate and visible
        self.pathTagZ = self.toFront(25.0)  ## otherwise it can be hidden 
        self.pathTagGroup = QGraphicsItemGroup()
        self.pathTagGroup.setZValue(self.pathTagZ)     
        self.scene.addItem(self.pathTagGroup)

    def clearPaths(self):
        if self.pathSet:
            if self.pathGroup:     
                self.scene.removeItem(self.pathGroup)
            if self.pathTagGroup:  
                self.scene.removeItem(self.pathTagGroup)
            for pix in self.scene.items():
                if pix.type == 'pix' and not pix.tag.endswith('.path'):
                    if pix.anime and pix.anime.state() ==  QAbstractAnimation.State.Paused:
                        if self.parent.control != 'resume':
                            pix.anime.resume()
                elif pix.zValue() <= common["pathZ"]:
                    break
        self.pathSet = False
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

    def addPainterPath(self, tag):
        color = getColorStr()
        path = pathLoader(tag)  ## return painter path
        pathPt = path.pointAtPercent(0.0)  ## so its consistent
        ## use painter path
        pathItem = QGraphicsPathItem(path)
        pathItem.setPen(QPen(QColor(color), 3, Qt.PenStyle.DashDotLine))
        pathItem.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsMovable, False)
        self.pathGroup.addToGroup(pathItem)
        self.addTag(tag, color, pathPt)

    def addTag(self, tag, color, pt):  ## use same offsets and color as path     
        tag = TagIt('', tag, color)   
        tag.setPos(pt)
        tag.setZValue(self.pathTagZ)   ## use pathTagZ instead of tagZ
        self.pathTagGroup.addToGroup(tag)

    def lastZval(self, str):  ## finds the lowest pix or bkg zValue
        last = 100000.0
        for itm in self.scene.items():
            if itm.type == str and itm.zValue() < last:
                last = itm.zValue()
        return last

    def toFront(self, inc=0):  ## finds the highest pixitem zValue
        first = 0               ## returns it plus the increment
        for pix in self.scene.items():
            if pix.type == 'pix': 
                first = pix.zValue()
                break
            elif pix.zValue() <= common["pathZ"]:
                break
        return inc + first

### --------------------- dotsMapItem ----------------------

