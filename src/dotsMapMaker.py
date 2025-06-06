
from PyQt6.QtCore    import Qt, QTimer, QSize, QRectF, QRect, QAbstractAnimation
from PyQt6.QtGui     import QColor, QPen
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsPixmapItem

from dotsShared         import common, ItemsGroup
from dotsTagsAndPaths   import TagsAndPaths

### --------------------- dotsMapMaker ---------------------
''' Classes: MapItem, MapMaker and various tags and path functions
    mainly for use by storyborad - and no overlap with pathmaker '''
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

### --------------------- dotsMapMaker ---------------------
class MapMaker:
### --------------------------------------------------------
    def __init__(self, canvas):
        super().__init__()

        self.canvas = canvas
        self.scene  = self.canvas.scene
   
        self.tagsAndPaths = TagsAndPaths(self)

        self.tagZ = 0
        self.pathTagZ = 0  ## only by paths

        self.tagSet = False
        self.pathSet = False

        self.mapRect = QRectF()
        
        self.paths = []
        self.selections = []

        self.pathGroup = None 
        self.tagGroup  = None
        self.pathTagGroup = None 
            
### --------------------------------------------------------
    def addSelectionsFromCanvas(self): ## uses rubberband to select items
        k = 0
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
                    if pix.locked:
                        pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
                    k += 1
            elif pix.zValue() <= common['pathZ']: 
                break
        if k == 0:
            self.clearMap()
        else:
            self.addMapItem()
 
    def addMapItem(self):
        self.removeMapItem()
        self.mapRect = self.mapBoundingRects()
        self.canvas.rubberBand.setGeometry(QRect(self.canvas.origin, QSize()))
        self.map = MapItem(self.mapRect, self)  
        self.map.setZValue(self.toFront(50)) ## higher up than tags
        self.scene.addItem(self.map)
        k = len(self.selections)
        self.canvas.dots.statusBar.showMessage(f'Number Selected: {k}', 5000)

    def mapBoundingRects(self):
        tx, ty = common['ViewW'], common['ViewH']
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
            elif pix.zValue() <= common['pathZ']:
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
        if self.isMapSet() == False:  ## runs directly from controlview uses 'M' key
            self.selections = []      ## not the same as in PathEdits
            for pix in self.scene.selectedItems():  ## only items selected
                self.selections.append(pix.id)
            if self.scene.selectedItems() or self.canvas.sideCar.hasHiddenPix():
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
                elif pix.zValue() <= common['pathZ']:
                    break

    def removeMapItem(self):
        if len(self.scene.items()) > 0:
            for pix in self.scene.items():
                if pix.type == 'map':
                    self.scene.removeItem(pix)
                    del pix
                    break

### ------------------- tags and paths ---------------------                        
    def clearPathsandTags(self):  ## used in showtime 
        self.clearTagGroup()
        self.clearPaths()  ## clears tags as well

    def addTagGroup(self):
        self.clearTagGroup()
        self.tagZ = self.toFront(45.0)   ## otherwise it can be hidden 
        self.tagGroup = ItemsGroup()
        self.tagGroup.setZValue(self.tagZ)     
        self.scene.addItem(self.tagGroup)

    def toggleTagItems(self, pid):  
        if self.canvas.pathMakerOn: 
            return  
        elif self.tagCount() > 0 and pid != 'anime':  ## don't clear these
            self.clearTagGroup()
            self.clearPaths() 
            return
        elif self.isMapSet():
            self.clearMap()
        if self.scene.items():  ## tag them all
            if self.pathSet:
                QTimer.singleShot(200, self.clearPaths)
            self.addTagGroup()
            self.tagsAndPaths.tagWorks(pid)
        
    def clearTagGroup(self):     
        if self.tagCount() > 0: 
            self.removeTags()
            self.tagGroup = None
            self.tagSet = False 
                  
    def clearPaths(self):  ## used by snakes, showtime, hatsbats, and tagsandspaths
        if self.pathSet:
            for pix in self.scene.items():
                if pix.type in ('pathsItem', 'text'):
                    self.scene.removeItem(pix)
                # elif isinstance(pix, QGraphicsSimpleTextItem):
                #    self.scene.removeItem(pix)
                   
            for pix in self.scene.items():
                if pix.type in ('pix', 'snake') and not pix.tag.endswith('.path'):
                    if pix.anime and pix.anime.state() ==  QAbstractAnimation.State.Paused:
                        if self.canvas.control != 'resume':
                            pix.anime.resume()
                elif pix.zValue() <= common['pathZ']:
                    break
              
        self.pathSet = False
        self.paths = []
        self.pathTagGroup = None
              
    def removeTags(self):  ## mapper only
        for p in self.canvas.scene.items():
            if p.type in ('tag', 'text', 'group'):
                self.scene.removeItem(p)  
    
    def toFront(self, inc=0):  ## finds the highest pixitem zValue - first
        first = 0               ## returns it plus the increment
        for pix in self.scene.items():
            if pix.type in ('flat', 'pix', 'shadow','snake', 'frame', 'bat'): 
                first = pix.zValue()
                break
            elif pix.zValue() <= common['pathZ']:
                break
        return inc + first
   
    def tagCount(self):  ## there's another one used by pathMaker 
        return sum(pix.type == 'tag' for pix in self.scene.items())
                 
### -------------------- dotsMapMaker ----------------------



