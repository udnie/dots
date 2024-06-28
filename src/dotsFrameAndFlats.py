

from PyQt6.QtCore       import Qt, QPointF, pyqtSlot
from PyQt6.QtGui        import QColor, QPixmap, QImage, QCursor
from PyQt6.QtWidgets    import QGraphicsPixmapItem

from dotsShared         import common
from dotsTagsAndPaths   import TagsAndPaths
from dotsBkgScrollWrks  import tagBkg

### ------------------ dotsFrameAndFlats.py ----------------
''' classes: Frame and Flat '''
### --------------------------------------------------------
class Frame(QGraphicsPixmapItem):  ## stripped down pixItem - that's why it's here, sort of
### --------------------------------------------------------
    def __init__(self, fileName, parent, z):  
        super().__init__()

        self.canvas = parent  
        self.mapper = self.canvas.mapper
        
        self.tagsAndPaths = TagsAndPaths(self)
              
        self.fileName = fileName  ## needs to contain 'frame'
        self.type = 'frame'  
          
        self.x, self.y = 0, 0  
        self.setZValue(z)
        
        self.tag = ''  
        self.locked = True
        
        self.id = self.canvas.pixCount ## used by mapper
        self.key = ''
    
        img = QImage(fileName)
        
        w = common["ViewW"]  ## from screens
        h = common["ViewH"] 

        img = img.scaled(int(w), int(h),
            Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation)
        
        self.setPixmap(QPixmap(img))
        self.setPos(QPointF(0,0))
        
        del img
        
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False) 
         
  ### --------------------------------------------------------
    @pyqtSlot(str)  ## updated by storyboard
    def setPixKeys(self, key):
        self.key = key  
            
    def hoverLeaveEvent(self, e):
        self.mapper.clearTagGroup()
        e.accept()
           
    def mousePressEvent(self, e):     
        if self.canvas.pathMakerOn == False:      
            if self.key == 'del':     
                self.canvas.showWorks.deleteFrame(self)  
            elif self.key in ('enter','return'):  
                if self.locked:
                    self.locked = False
                self.setZValue(self.canvas.mapper.toFront(1)) 
                self.locked = True
            elif self.key in ('opt', 'tag'): 
                tagBkg(self, self.pos())
            e.accept()
      
    def mouseReleaseEvent(self, e):
        if self.canvas.pathMakerOn == False:
            self.key = '' 
            e.accept()
                        
### -------------------------------------------------------- 
class Flat(QGraphicsPixmapItem):
### -------------------------------------------------------- 
    def __init__(self, color, parent, z=common['bkgZ']):
        super().__init__()

        self.bkgMaker = parent
        self.canvas   = self.bkgMaker.canvas 
        self.scene    = self.bkgMaker.scene
            
        self.fileName = 'flat'
        self.type    = 'flat'
        
        self.color = QColor(color)
        self.tag   = QColor(color)

        self.locked = True
        self.setZValue(z)
        
        self.key = ''
        self.x, self.y = 0, 0

        p = QPixmap(common['ViewW'],common['ViewH'])
        p.fill(self.color)
        
        self.setPixmap(p)      
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
        
### --------------------------------------------------------
    @pyqtSlot(str)  ## updated by storyboard
    def setPixKeys(self, key):
        self.key = key  

    def mousePressEvent(self, e):      
        if not self.canvas.pathMakerOn:     
            if self.key == 'del':     
                self.delete()
            elif self.key == '/':  ## to back
                self.bkgMaker.back(self)
            elif self.key in ('enter','return'):  
                self.setZValue(self.canvas.mapper.toFront()) 
            elif self.key in ('opt', 'tag'): 
                p = self.canvas.mapFromGlobal(QPointF(QCursor.pos()))
                tagBkg(self, QPointF(p.x(), p.y()-20 )  )
            elif self.key == ',':
                self.setZValue(self.zValue()-1)
            elif self.key == '.':
                self.setZValue(self.zValue()+1 )                       
        e.accept()
      
    def mouseReleaseEvent(self, e):
        if not self.canvas.pathMakerOn:
            self.key = ''       
        e.accept()
     
    def delete(self):  ## also called by widget
        self.bkgMaker.deleteBkg(self)
              
### ------------------ dotsFrameAndFlats.py ---------------- 


   
                      