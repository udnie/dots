
import cv2
import numpy as np

from PyQt6.QtCore       import Qt, QPointF, QRectF
from PyQt6.QtGui        import QColor, QPen
from PyQt6.QtWidgets    import QGraphicsPixmapItem, QGraphicsEllipseItem
                               
from dotsShared         import common
from dotsSideGig        import point

PathStr = ['topLeft','topRight','botRight','botLeft']
V = common['V']  ## the diameter of a pointItem, same as in ShadowWidget

### ---------------------- dotsShadow ----------------------
''' classes: Shadow, PointItem, and cv2 functions... 
    Shadow doesn't hold state as it's constantly being updated - 
    ShadowMaker's shadow is where to look '''                                                    
### --------------------------------------------------------
class Shadow(QGraphicsPixmapItem):  ## initPoints, initShadow, setPerspective
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
       
        self.maker   = parent
        self.canvas  = self.maker.canvas
        self.pixitem = self.maker.pixitem
        self.path    = self.maker.path
       
        self.anime = None 
        self.setZValue(common['shadow']) 
        
        self.tag = ''
        self.type = 'shadow' 
        self.fileName = 'shadow'
                                       
        self.dragCnt = 0
        self.save    = QPointF()
                             
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, False) 
     
### --------------------------------------------------------
    def itemChange(self, change, value):  ## continue to updatePath when animated
        if change == QGraphicsPixmapItem.GraphicsItemChange.ItemScenePositionHasChanged: 
            if self.maker.linked: 
                if self.maker.outline.isVisible() == True: self.maker.works.hideOutline()
                self.dragCnt += 1
                if self.dragCnt % 5 == 0:  
                    dif = value - self.save          
                    for i in range(4):  
                        self.maker.path[i] = self.maker.path[i] + dif
                        self.maker.updatePoints(i, self.maker.path[i].x(), self.maker.path[i].y())
                    self.save = value
        return super(QGraphicsPixmapItem, self).itemChange(change, value)

### --------------------------------------------------------
    def mousePressEvent(self, e):  
        self.save = self.mapToScene(e.pos())         
        if e.button() == Qt.MouseButton.RightButton:  
            self.maker.addWidget()  ## only place it's used
            self.maker.works.resetSliders() 
            e.accept()
            return
        elif self.maker.linked == False:
            self.updOutline(e)
        e.accept() 

    def mouseMoveEvent(self, e):
        if self.maker.linked == False:
            self.dragCnt += 1
            if self.dragCnt % 5 == 0:                     
                self.maker.updatePath(self.mapToScene(e.pos()))  
                self.maker.works.updateOutline() 
        e.accept()       
                          
    def mouseReleaseEvent(self, e): 
        self.maker.updatePath(self.mapToScene(e.pos())) 
        self.updOutline(e)
        self.maker.updateShadow()  ## cuts off shadow at 0.0y of scene if not moving
        e.accept()
 
    def updOutline(self, e):  ## so as not to be confused with updateOutline
        self.save = self.mapToScene(e.pos())    
        self.maker.addPoints() 
        self.maker.works.updateOutline()
        e.accept()
  
  ### --------------------------------------------------------                                       
    def linkShadow(self):
        b = self.pos()    
        self.maker.linked = True  
        self.setParentItem(self.pixitem)   
        ## there's a problem if the pixitem is rotated/scaled
        self.setPos(-self.pixitem.pos()+b)       
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIgnoresTransformations)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemStacksBehindParent)       
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)  
        self.maker.works.hideOutline()
        self.maker.hidden = True 
        if self.maker.widget:       
            self.maker.works.closeWidget()
        self.save = b  ## starting value
                   
    def unLinkShadow(self):
        b = self.save  ## self.pixitem.pos()+self.shadow.pos()    
        self.anime = None    
        self.maker.linked = False          
        self.setParentItem(None)    
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, False)
        self.maker.updatePath(b)  ## ending value       
        self.maker.updateShadow() 
        self.maker.addPoints() 
        self.maker.works.showOutline()       
        if self.maker.widget:
            self.maker.works.closeWidget()  
     
### --------------------------------------------------------        
    def initPoints(self):  ## initial path and points setting           
        self.path = []
        self.maker.outline = None
        
        if self.canvas.openPlayFile == 'abstract':  ## not needed 
            return      
        self.maker.setPath(self.boundingRect(), self.pos()) 
        
        self.maker.addPoints()         
        self.maker.works.updateOutline()     
    
        if self.pixitem.scale != 1.0 or self.pixitem.rotation != 0:    
            self.scaleRotateShadow()
            
    def scaleRotateShadow(self):    
        self.maker.shadow.setRotation(self.pixitem.rotation)
        self.maker.shadow.setScale(self.pixitem.scale)
    
        self.maker.setPath(self.pixitem.boundingRect(), self.pixitem.pos() + QPointF(-50,-15))
     
        if self.pixitem.rotation != 0:
            self.maker.works.rotateShadow(self.pixitem.rotation)
            self.maker.rotate = self.pixitem.rotation
                    
        if self.pixitem.scale != 1.0:   
            self.maker.works.scaleShadow(self.pixitem.scale)      
            self.maker.scalor = self.pixitem.scale

        self.maker.addPoints()     
        self.maker.works.updateOutline()         
                
        self.maker.shadow.show()
                                                                                                
### --------------------------------------------------------        
def initShadow(file, w, h, flop):  ## replace all colors with grey    
    img = cv2.imread(file, cv2.IMREAD_UNCHANGED)   
    if flop: img = cv2.flip(img, 1)  ## works after the read   
    rows, cols, _ = img.shape

    tmp = img.copy()  
    for i in range(rows):
        for j in range(cols):
            pixel = img[i,j]
            if pixel[-1] != 0:  ## not transparent      
                tmp[i,j] = (20,20,20,255)
                                           
    img = cv2.resize(np.array(tmp), (int(w), int(h)), interpolation = cv2.INTER_CUBIC)
    img = cv2.GaussianBlur(img,(5,5),cv2.BORDER_DEFAULT)
                                
    height, width, ch = img.shape
    bytesPerLine = ch * width  ## 4 bits of information -- alpha channel 
    
    return img, width, height, bytesPerLine

### --------------------------------------------------------          
def setPerspective(path, w, h, cpy, viewW, viewH):  ## update gray copy based on path xy's         
    p = []                      
    for i in range(4):  ## get current location of points from path
        x,y = int(path[i].x()), int(path[i].y()) 
        p.append([x,y])
            
    dst = np.float32([p[0], p[1], p[3], p[2]])        
    src = np.float32([[0,0], [w,0], [0, h], [w,h]])
        
    M = cv2.getPerspectiveTransform(src, dst)  ## compute the Matrix
    img = cv2.warpPerspective(cpy, M, (viewW, viewH))

    height, width, ch = img.shape
    bytesPerLine = ch * width  ## 4 bits of information
    
    return img, width, height, bytesPerLine   
                       
### --------------------------------------------------------
    # def paint(self, painter, option, widget=None):  ## just in case
    #     super().paint(painter, option, widget)  ## for shadow
    #     if self.isSelected():
    #         pen = QPen(QColor('lime'))
    #         pen.setWidth(2)
    #         painter.setPen(pen)
    #         painter.drawRect(self.boundingRect())
      
### --------------------------------------------------------
class PointItem(QGraphicsEllipseItem):  ## not to be confused with pathMaker's PointItem
### --------------------------------------------------------
    def __init__(self, pt, ptStr, parent):
        super().__init__()

        self.maker = parent
        self.path  = self.maker.path   
        self.ptStr = ptStr
        
        self.type    = 'point'
        self.fileName = 'point'
        self.tag     = 'point'  
        self.dragCnt = 0
          
        ## -V*.5 so it's centered on the path 
        self.x = pt.x()-V*.5
        self.y = pt.y()-V*.5
        
        self.setZValue(common['points'])      
        self.setRect(self.x, self.y, V, V)  
        
        self.setPen(QPen(QColor('gray'), 1))
        if self.ptStr in ('topLeft','topRight'):
            self.setBrush(QColor('yellow'))
        else:
            self.setBrush(QColor('lime'))
            
        self.setAcceptHoverEvents(True)
                        
 ### --------------------------------------------------------
    def hoverEnterEvent(self, e):
        p = self.rect()      
        if p.width() < V*1.5:
            self.setRect(QRectF(p.x(), p.y(), V*1.5, V*1.5))
        e.accept()
        
    def hoverLeaveEvent(self, e):  
        p = self.rect()
        self.setRect(QRectF(p.x(), p.y(), V, V))
        e.accept()

### --------------------------------------------------------
    def mousePressEvent(self, e):  
        e.accept() 
        
    def mouseMoveEvent(self, e):
        self.dragCnt += 1
        if self.dragCnt % 5 == 0:            
            self.moveIt(e.pos()) 
            self.maker.updateShadow()             
        e.accept()
                       
    def mouseReleaseEvent(self, e):
        self.moveIt(e.pos())
        self.maker.updateShadow()
        e.accept()
                                        
    def moveIt(self, e):     
        pos = self.mapToScene(e)
        x, y = pos.x(), pos.y()
        self.setRect(x-V*.5, y-V*.5, V,V)  ## set current point    
        if self.ptStr == 'topLeft':  ## push right
            self.topLeft(x, y)
        elif self.ptStr == 'botLeft':    
            self.botLeft(x, y)
        else:  
            i = PathStr.index(self.ptStr)  ## move only 
            self.path[i] = QPointF(x,y)                  
        
    def topLeft(self, x, y):
        w, y1 = self.current(0,1)            
        self.path[0] = QPointF(x,y) 
        self.path[1] = QPointF(x+w,y1)
        self.maker.topRight.setRect(x+(w-V*.5), y1-V*.5, V,V)  
        
    def botLeft(self, x, y):
        w, y1 = self.current(3,2)            
        self.path[3] = QPointF(x,y) 
        self.path[2] = QPointF(x+w,y1)
        self.maker.botRight.setRect(x+(w-V*.5), y1-V*.5, V,V)          
        
    def current(self,a,b):
        l = self.path[a].x()
        r = self.path[b].x()
        return r - l,  self.path[b].y()
                              
### ---------------------- dotsShadow ----------------------


