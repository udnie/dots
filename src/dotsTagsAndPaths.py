
from PyQt6.QtCore       import Qt, QAbstractAnimation, QRectF
from PyQt6.QtGui        import QColor, QPen, QPainter, QBrush, QFontMetrics, QColor, QFont
from PyQt6.QtWidgets    import QGraphicsPathItem
                            
from dotsShared         import common, ControlKeys, ItemsGroup, PathsItem, TextItem
from dotsSideGig        import getColorStr
from dotsSidePath       import pathLoader
from dotsAnimation      import AnimeList

### ------------------- dotsTagsAndPaths -------------------
''' classes: TagIt, TagsAndPaths  - TagIt is used by PathItem and PathWays 
    directly and is managed by them. TagsAndPaths also uses TagIt but is
    mainly managed thru mapper. - another project awaits '''
### --------------------------------------------------------
class TagIt(TextItem):  ## called in pathItem, pathWays and this
### --------------------------------------------------------   
    def __init__(self, token, tag, color, zval=None):
        super().__init__()
  
        self.type = 'tag'
  
        if token == 'paths':
            color = 'lime'
            if 'Locked Random' in tag:
                tag = tag[14:] 
            elif 'Random' in tag:
                tag = tag[7:]
            n = tag.find('path') + 5
            tag = tag[0:n]
            
        elif token in ControlKeys and 'Random' in tag:
            tag = tag[7:]
            self.color = QColor(0,255,127)
            
        elif token == 'pathMaker':
            if ' 0.00%' in tag:
                color = QColor('LIGHTSEAGREEN')
            if len(tag.strip()) > 0: self.color = QColor(color)
            
        elif token == 'points':
            self.color = QColor(color)
            
        else:
            self.color = QColor(255,165,0)
            if type(tag) == str and len(tag) > 0: 
                if 'Locked Random' in tag:
                    tag = tag[0:13] 
                elif 'Random' in tag:
                    tag = tag[0:6] 
                     
        if color in ('orange', 'yellow') and tag[0] == 'd':
            tag = tag[2:]
                    
        if color:
            self.color = QColor(color)

        if zval != None and token != 'paths':
            if type(tag) == str and len(tag) > 0:  
                tag = tag + ': ' + str(zval)
            else:
                tag = str(zval)
    
        if token == 'points':
            self.type = 'ptTag'  ## changed from 'pt'

        self.text = tag   
     
        self.font = QFont()
        self.font.setFamily('Helvetica')
        self.font.setPointSize(12)
        
        if token in ('bkg', 'points', 'pathMaker'):
            self.font.setPointSize(14)
        
        metrics = QFontMetrics(self.font)
        p = metrics.boundingRect(self.text)
        p = p.width()
 
        self.rect = QRectF(0, 0, p+13, 19)
        self.waypt = 0
            
    def boundingRect(self):
        return self.rect
    
### --------------------------------------------------------
    def paint(self, painter, option, widget): 
        brush = QBrush()
        brush.setColor(self.color)
        brush.setStyle(Qt.BrushStyle.SolidPattern)

        painter.fillRect(self.boundingRect(), brush)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(Qt.GlobalColor.black)
        painter.setFont(self.font)
        painter.drawText(self.boundingRect(), 
            Qt.AlignmentFlag.AlignCenter, self.text)
        
### --------------------------------------------------------
class TagsAndPaths: ## handles more than one request
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()

        self.mapper = parent
        self.scene  = self.mapper.scene
        self.canvas = self.mapper.canvas
     
### --------------------------------------------------------  
    def tagWorks(self, pid):  ## this if more than one
        k = 0
        alltags = ''
        self.mapper.tagSet = False
        self.alst = sorted(AnimeList); self.alst.extend(['Random'])   
        if pid == '':  ## pid can also equal the pixitem.id - using tagBkg in sideCar2 for singles
            pid = 'all'
        ## changed order - otherwise the top tag can be hidden 
        for pix in self.scene.items(Qt.SortOrder.AscendingOrder):
            if pix.type in ( 'frame', 'pix', 'snake', 'bkg', 'shadow'):
                
                if pid == 'paths' and 'path' in str(pix.tag):  
                    self.tagThis('paths', pix) 
                    k += 1
                    
                elif pid == 'anime' and pix.type == 'pix' and pix.tag in self.alst \
                    or 'path' in pix.tag:  
                    self.tagThis('',pix) 
                    k += 1   
                            
                elif pid == 'all':
                    if alltags != pix.tag:  ## only one per snake
                        alltags = pix.tag
                        self.tagThis('',pix) 
                        k += 1    
                            
                elif pid == 'select' and pix.isSelected():
                    self.tagThis('', pix)
                    k += 1
                    
                elif pix.type == 'frame':  ## single tag  
                    self.tagThis('', pix) 
                    k = 1
                    break   
                   
        if k > 0: 
            self.mapper.tagSet = True
            self.canvas.dots.statusBar.showMessage(f"Number Tagged: {k}", 5000)
        else:
            self.mapper.clearTagGroup()
 
### --------------------------------------------------------        
    def tagThis(self, token, pix):  ## used by tagWorks
        
        if pix.type != 'shadow': 
            p = pix.sceneBoundingRect()
            x = p.x() + p.width()*.45
            y = p.y() + p.height()*.45
        else:
            p = pix.maker.shadow.sceneBoundingRect()
            x = p.x() + 50.0
            y = p.y() + 50.0
            
        topZVal = self.mapper.toFront()

        tag = pix.tag
        color = ''
        
        if pix.type in ('pix','bkg','frame'):

            if pix.locked == True:
                tag = 'Locked ' + tag 
            else:
                tag = 'UnLocked ' + tag 
    
            color = 'orange'
            zval = pix.zValue()
          
            if pix.type == 'bkg':
                if pix.direction == ' left':
                    tag = tag + ' Left'
                elif pix.direction == 'right': 
                    tag = tag + ' Right'
                tag = tag + ' ' + pix.useThis  
                color = 'AQUA'
                x, y = 250, 150
                
        elif pix.type == 'flat':
            color = 'AQUA'
           
        elif pix.type == 'shadow':
            color = 'lightgreen'
            if pix.maker.linked == True:
                tag = 'Linked ' + tag
            else:
                tag = 'UnLinked ' + tag
            zval = pix.zValue()
   
        if token == 'paths':
            y = y - 20
        else:
            token = self.canvas.control
          
        if pix.zValue() == topZVal:  ## set to front ZValue
            color = 'yellow'
             
        if 'frame' in pix.fileName: 
            x, y = common['ViewW']*.47, common['ViewH']-35
               
        self.TagItTwo(token, tag, color, x, y, zval)
        
### --------------------------------------------------------       
    ## this way I can stretch it for backgrounds and pixitems
    def TagItTwo(self, token, tag, color, x, y, z, src=''):
        tag = TagIt(token, tag, color, z)         
        tag.setZValue(self.mapper.toFront(45.0))
        
        if src in ('bkg', 'pix'):  ## single selections
            tag.setPos(x-50.0, y-10.0)  ## position it near cursor
            self.scene.addItem(tag)
        else:
            tag.setPos(x,y)
            self.mapper.tagGroup.addToGroup(tag)
        self.mapper.tagSet = True

### -------------------- mostly paths ----------------------
    def togglePaths(self):  ## use by showbiz
        if self.canvas.pathMakerOn:
            return 
        if self.mapper.pathSet:
            self.mapper.clearPaths() 
            return
        k = 0
        self.mapper.pathSet = False  
        self.addPathGroup()
        self.addPathTagGroup()
        for pix in self.scene.items():
            if pix.type in ('pix', 'snake'):
                if  pix.tag.endswith('.path'): 
                    k += self.displayPath(pix)  
                    if k > 7: break  ## good plan 
                elif pix.anime and pix.anime.state() == QAbstractAnimation.State.Running:
                    pix.anime.pause()
            elif pix.zValue() <= common['pathZ']:
                break
        if k > 0: 
            self.mapper.pathSet = True
        else:
            self.mapper.clearPaths()

    def displayPath(self, pix):
        tag = pix.tag 
        if 'Random' in tag: tag = tag[7:]
        ## don't add duplicate paths - causes performance issues
        if not tag in self.mapper.paths:
            path = self.addPainterPath(tag)
            if path != None:
                self.mapper.paths.append(tag)
            return 1
        else:
            return 0

    def addPainterPath(self, tag):
        color = getColorStr()
        path = pathLoader(tag)  ## return painter path  
        if path == None:
            return None   
        pathPt = path.pointAtPercent(0.0)  ## so its consistent
        ## use painter path
        pathItem = PathsItem(path)        
        pathItem.setPen(QPen(QColor(color), 3, Qt.PenStyle.DashDotLine))
        pathItem.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsMovable, False)
        self.pathGroup.addToGroup(pathItem)
        self.addTag(tag, color, pathPt)      

    def addPathGroup(self):
        self.pathGroup = ItemsGroup()
        self.pathGroup.setZValue(self.mapper.toFront(35.0))    
        self.scene.addItem(self.pathGroup)
    
    def addPathTagGroup(self):   
        ## add pathTags group to keep tags separate and visible
        self.pathTagZ = self.mapper.toFront(35.0)  ## otherwise it can be hidden 
        self.pathTagGroup = ItemsGroup()
        self.pathTagGroup.setZValue(self.pathTagZ)     
        self.scene.addItem(self.pathTagGroup)

    def addTag(self, tag, color, pt):  ## use same offsets and color as path     
        tag = TagIt('', tag, color)   
        tag.setPos(pt)
        tag.setZValue(self.mapper.toFront(45.0))  ## use pathTagZ instead of tagZ
        self.pathTagGroup.addToGroup(tag)

### ------------------- dotsTagsAndPaths -------------------        
        

