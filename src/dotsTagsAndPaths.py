
from PyQt6.QtCore    import Qt, QAbstractAnimation
from PyQt6.QtGui     import QColor, QPen
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItemGroup
                            
from dotsShared      import common
from dotsSideGig     import TagIt, getColorStr
from dotsSidePath    import pathLoader

### ------------------- dotsTagsAndPaths -------------------
''' dotsTagsAndPaths handles tags and paths display '''
### --------------------------------------------------------
class TagsAndPaths:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()

        self.mapper = parent
        self.scene  = self.mapper.scene
        self.canvas = self.mapper.canvas
        self.dots   = self.canvas.dots
        
### --------------------------------------------------------      
    def tagWorks(self, pid):
        k = 0
        topZVal = self.mapper.toFront()  ## only once
        self.mapper.tagSet = False
        if pid == '': 
            pid = 'all'
        alltags = ''
        ## changed order - otherwise the top tag can be hidden 
        for pix in self.scene.items(Qt.SortOrder.AscendingOrder):
            if pix.type in ('pix', 'snake', 'bkg') and pix.fileName != 'fiat':
                if 'path' in pix.tag and pid == 'paths':
                    self.tagIt('paths', pix, topZVal) 
                    k += 1
                if pid == 'all':
                    k += 1
                    if alltags != pix.tag:  ## only one per snake
                        alltags = pix.tag
                        self.tagIt('',pix, topZVal)         
                # elif pid == 'select' and pix.isSelected():
                elif pix.isSelected():
                    self.tagIt('',pix, topZVal)
                    k += 1
                elif pid == pix.id:  ## single tag
                    self.tagIt('',pix, topZVal) 
                    k = 1
                    break
        if k > 0: 
            self.mapper.tagSet = True
            self.dots.statusBar.showMessage('Number Tagged:  {}'.format(k),2500)
        else:
            self.mapper.clearTagGroup()
        
    def tagIt(self, token, pix, topZVal):  
        p = pix.sceneBoundingRect()
        x = p.x() + p.width()*.45
        y = p.y() + p.height()*.45

        tag = pix.tag
        color = ''

        if 'frame' in pix.fileName: 
            x, y = common['ViewW']*.47, common['ViewH']-35
            pix.tag = ''

        if pix.type in ('pix','bkg') and pix.locked == True:
            tag = 'Locked ' + tag 

        if pix.zValue() == topZVal:  ## set to front ZValue
            color = 'yellow'

        if token == 'paths':
            y = y - 20
        else:
            token = self.canvas.control
            
        if tag == 'UnLocked': color = 'orange'
          
        self.TagItTwo(token, tag, color, x, y, pix.zValue())
        
    def TagItTwo(self, token, tag, color, x, y, z, src=''):
        ## this way I can stretch it for backgrounds
        tag = TagIt(token, tag, color, z)
        tag.setZValue(self.mapper.toFront(45.0))
        if src == 'bkg':
            tag.setPos(x-50.0, y-30.0)
            self.scene.addItem(tag)
        else:
            tag.setPos(x,y)
            self.mapper.tagGroup.addToGroup(tag)
        self.mapper.tagSet = True
        
    def addTagGroup(self):
        self.tagZ = self.mapper.toFront(45.0)   ## otherwise it can be hidden 
        self.mapper.tagGroup = QGraphicsItemGroup()
        self.mapper.tagGroup.setZValue(self.tagZ)     
        self.scene.addItem(self.mapper.tagGroup)
      
    def removeTags(self):
        for p in self.canvas.scene.items():
            if p.type == 'tag':
                self.scene.removeItem(p)
                     
    def tagCount(self):  
        return sum( pix.type == 'tag' 
            for pix in self.scene.items())

### -------------------- mostly paths ----------------------
    def togglePaths(self):  ## use by sideShow
        if self.canvas.pathMakerOn:
            return
        if self.mapper.pathSet:
            self.mapper.clearPaths() 
            return
        if self.scene.items():
            k = 0
            self.mapper.pathSet = False  
            self.addPathGroup()
            self.addPathTagGroup()
            for pix in self.scene.items():
                if pix.type in ('pix', 'snake'):
                    if  pix.tag.endswith('.path'):
                        k += self.displayPath(pix)  ## anything displayed?
                    elif pix.anime and pix.anime.state() == QAbstractAnimation.State.Running:
                        pix.anime.pause()
                elif pix.zValue() <= common['pathZ']:
                    break
            if k > 0: 
                self.mapper.pathSet = True
            else:
                self.mapper.clearPaths()

    def addPathGroup(self):
        self.pathGroup = QGraphicsItemGroup()
        self.pathGroup.setZValue(self.mapper.toFront(35.0))    
        self.scene.addItem(self.pathGroup)
    
    def addPathTagGroup(self):   
        ## add pathTags group to keep tags separate and visible
        self.pathTagZ = self.mapper.toFront(35.0)  ## otherwise it can be hidden 
        self.pathTagGroup = QGraphicsItemGroup()
        self.pathTagGroup.setZValue(self.pathTagZ)     
        self.scene.addItem(self.pathTagGroup)

    def displayPath(self, pix):
        tag = pix.tag 
        if 'Random' in tag: tag = tag[7:]
        ## don't add duplicates - causes performance issues
        if not tag in self.mapper.paths:
            self.mapper.paths.append(tag)
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
        tag.setZValue(self.mapper.toFront(45.0))  ## use pathTagZ instead of tagZ
        self.pathTagGroup.addToGroup(tag)
                   
    def tagCount(self):  
        return sum(pix.type == 'tag' 
            for pix in self.scene.items())

### ------------------- dotsTagsAndPaths -------------------        
        

