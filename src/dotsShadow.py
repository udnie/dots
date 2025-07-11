
import cv2
import numpy as np
import os.path

from PyQt6.QtCore       import Qt, QPoint, QPointF, pyqtSlot
from PyQt6.QtGui        import QCursor, QColor
from PyQt6.QtWidgets    import QGraphicsPixmapItem, QGraphicsDropShadowEffect
                              
from dotsShared         import common, paths, ControlKeys
from dotsHelpMonkey     import SharedKeys
from dotsSideGig        import tagBkg

V = common['V']  ## the diameter of a pointItem, same as in ShadowWidget

### ---------------------- dotsShadow ----------------------
''' classes: Shadow and cv2 functions... 
    Shadow doesn't hold state as it's constantly being updated - 
    shadowMaker.shadow is where to look. pixitem.shadow is storage 
    The Shadow helpMenu and sharedkeys are in helpMonkey ''' 
### ---------------------- dotsShadow ----------------------  
class Shadow(QGraphicsPixmapItem):  ## initPoints, initShadow, setPerspective
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
       
        self.maker   = parent  ## shadowMaker
        self.canvas  = self.maker.canvas
        self.pixitem = self.maker.pixitem
        self.path    = self.maker.path
        self.mapper  = self.canvas.mapper
       
        self.setZValue(self.pixitem.zValue()-1) 
        
        self.tag = ''     
        self.type = 'shadow' 
        self.fileName = 'shadow'
     
        self.key = ''          
        self.sharedKeys = SharedKeys   
                                
        self.dragCnt = 0 
        self.save = QPointF()  ## mapToScene - used with updatePath
        
        self.scale    = self.pixitem.scale
        self.rotation = self.pixitem.rotation
        
        self.width  = self.pixitem.width
        self.height = self.pixitem.height 
                            
        ## not linked
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, False) 
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
        
        self.setOriginPt()
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setColor(QColor('220,220,220,128'))
        shadow.setOffset(0, 0)

        self.setGraphicsEffect(shadow)
         
### --------------------------------------------------------
    def itemChange(self, change, value):  ## continue to updatePath when animated
        if change == QGraphicsPixmapItem.GraphicsItemChange.ItemScenePositionHasChanged: 
            if self.maker.linked: 
                if self.maker.outline.isVisible() == True: 
                    self.maker.works.hideOutline()
                self.dragCnt += 1
                if self.dragCnt % 5 == 0:  
                    self.maker.updatePath(value)  ## and sets shadows position      
        return super(QGraphicsPixmapItem, self).itemChange(change, value)

### --------------------------------------------------------
    @pyqtSlot(str)  ## updated by storyboard
    def setPixKeys(self, key):
        self.key = key  
        
    def mousePressEvent(self, e): 
        self.save = self.mapToScene(e.pos())
        if e.button() == Qt.MouseButton.RightButton: 
            self.maker.addWidget(self)  ## only place it's used 
        elif self.key in self.sharedKeys:
            self.shared(self.key)  
        e.accept() 

    def shared(self, key):  ## with help menuu
        match key:
            case 'del':    
                self.delete()      
            case 'shift':       ## send back 3 - otherwise it still covers the sprite
                self.setZValue(self.zValue()-3)
            case 'enter' | 'return':    # send to front
                self.setZValue(self.mapper.toFront(1))  
            case 'tag':                  ## '\' backslash
                self.tagThis()
            case 'H':  
                self.maker.openMenu() 
            case 'T':     
                self.linkShadow() if self.maker.linked == False \
                    else self.unlinkShadow()
                self.tagThis() 
            case '/':  ## fixes cut off shadow if partial offscreen
                self.maker.updateShadow('nope') 
            case 'dblclk':
                self.maker.works.toggleOutline()
        
    def tagThis(self):  
        p = QCursor.pos()
        tagBkg(self, self.canvas.mapFromGlobal(QPoint(p.x(), p.y()-20))) 
         
    def mouseMoveEvent(self, e):
        if self.maker.linked == False:
            self.dragCnt += 1
            if self.dragCnt % 5 == 0:  ## updatePath handles dblclk           
                self.maker.updatePath(self.mapToScene(e.pos()))  
        e.accept()       
                          
    def mouseReleaseEvent(self, e): 
        self.key = '' 
        if self.maker.linked == False:  
            self.maker.updatePath(self.mapToScene(e.pos()))            
            if self.maker.dblclk == False:  
                self.maker.works.hideOutline()                
        e.accept()
   
    def mouseDoubleClickEvent(self, e):  ## if 'resume', 'pause', animation running
        if self.canvas.control not in ControlKeys and \
            self.key not in self.sharedKeys:    
            if self.maker.linked == False:
                self.maker.works.toggleOutline()
            else:
                self.tagThis()
        e.accept()
                
    def delete(self):  
        self.maker.works.deleteShadow()
  
    def updOutline(self):  ## so as not to be confused with updateOutline
        self.maker.addPoints() 
        self.maker.works.updateOutline()
    
  ### --------------------------------------------------------                    
    def linkShadow(self):
        b = self.pos()
        if self.maker.widget != None:
            self.maker.widget.linkBtn.setText('Link') 
        self.maker.linked = True         
        self.pixitem.offset = self.pos()-self.pixitem.pos()  ## may change
        self.setZValue(self.pixitem.zValue()-1)  
        self.setOriginPt()
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)  
        self.pixitem.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)  
        # self.pixitem.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsGeometryChanges, True) 
        # self.pixitem.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemDoesntPropagateOpacityToChildren, False)    
        self.maker.works.hideOutline()
        self.maker.hidden = True    
        if self.maker.widget != None:
            self.maker.works.closeWidget()      
        self.save = b
               
    def unlinkShadow(self):  
        b = self.save    
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, False)
        self.pixitem.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, False) 
        # self.pixitem.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsGeometryChanges, False)  
        # self.pixitem.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemDoesntPropagateOpacityToChildren, True)   
        self.setPos(self.pixitem.pos()+self.pixitem.offset)
        self.maker.linked = False 
        self.maker.updatePath(b)  ## ending value 
        self.maker.dblclk = False  
        self.maker.updateShadow()  
        self.maker.addPoints() 
        self.maker.works.hideOutline()  ## was showOutline()
        if self.maker.widget != None:
            self.maker.widget.linkBtn.setText('Link')  ## keep it open  
            self.maker.works.resetSliders() 
  
### --------------------------------------------------------        
    def initPoints(self):  ## initial path and points setting from maker.addShadow         
        self.path = []
        self.maker.outline = None
        
        if self.canvas.openPlayFile == 'hats':  ## not needed 
            return    
          
        self.maker.setPath(self.boundingRect(), self.pos())  ## sets outline open
        self.maker.addPoints()      
        self.maker.works.updateOutline() 
        self.maker.dblclk = True
      
        if self.pixitem.scale != 1.0 or self.pixitem.rotation != 0:    
            self.scaleRotateShadow()
            
    def scaleRotateShadow(self):  ## only if new    
        self.setOriginPt()
        self.maker.shadow.setRotation(self.pixitem.rotation)
        self.maker.setPath(self.pixitem.boundingRect(), self.pixitem.pos() + QPointF(-50,-15))
     
        if self.pixitem.rotation != 0:
            self.maker.works.rotateShadow(self.pixitem.rotation)
            self.maker.rotate = self.pixitem.rotation
                    
        if self.pixitem.scale != 1.0:   
            self.maker.works.scaleShadow(self.pixitem.scale)      
            self.maker.scalor = self.pixitem.scale

        self.maker.addPoints()      
        self.maker.updateShadow()
           
    def setOriginPt(self):    
        b = self.boundingRect()
        op = QPointF(b.width()/2, b.height()/2)
        self.setTransformOriginPoint(op)
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
                                                                                                  
### --------------------------------------------------------        
def initShadow(file, w, h, flop):  ## replace all colors with grey  
    file = paths['spritePath'] + os.path.basename(file)         
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
                                                               
### ---------------------- dotsShadow ----------------------


    
