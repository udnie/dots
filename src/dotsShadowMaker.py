
import math
import os

from PyQt6.QtCore       import QPoint, QPointF, QTimer
from PyQt6.QtGui        import QImage, QPixmap

from dotsShadow         import *                      
from dotsShadowWidget   import *
from dotsShared         import common
from dotsSideGig        import distance, getCrop, point

PathStr = ['topLeft','topRight','botRight','botLeft']
V = common['V']  ## the diameter of a pointItem, same as in ShadowWidget
       
### ------------------- dotsShadowMaker --------------------
''' class: ShadowMaker - handles shadow, widget and points'''                                                                                                                    
### -------------------------------------------------------- 
class ShadowMaker:  
### --------------------------------------------------------    
    def __init__(self, parent):
        super().__init__()
                  
        self.pixitem = parent
        self.canvas  = self.pixitem.canvas
        self.scene   = self.pixitem.scene
        
        self.init()
      
        self.works = Works(self)  ## off-loaded small functions to here

    def init(self):
        self.topLeft  = None
        self.topRight = None
        self.botLeft  = None
        self.botRight = None
        
        self.path = [] 
        self.points = []  
   
        self.flopped   = False
        self.isHidden = False  ## just a toggle - not saved
        self.isActive = True   ## lets pixitem know that numpy and openCV are installed
        self.linked   = False
        self.restore  = False

        self.alpha  = .50
        self.scalor = 1.0
        self.rotate =   0
        
        self.cpy     = None  ## save original grey image 
        self.flopCpy  = None
        
        self.outline = None  
        self.shadow  = None
        self.widget  = None
       
        self.imgSize = 0,0  ## last width and height of shadow
        self.viewW, self.viewH = 0,0
 
### --------------------------------------------------------
    def addShadow(self, w, h, viewW, viewH):  ## initial shadow       
        if self.shadow != None:
            return 
                 
        file, w, h = self.works.pixWidthHeight()                                                      
        img, width, height, bytesPerLine = initShadow(file, w, h, self.pixitem.flopped)
       
        self.cpy = img   ## save it for later  
        self.flopCpy = cv2.flip(img, 1)  ## use this if shadow is flopped
                         
        image = QImage(img.data, width, height, bytesPerLine, QImage.Format.Format_ARGB32)    
        pixmap = QPixmap.fromImage(image)
                  
        self.shadow = Shadow(self)  ## from ShadowWidget *
        self.shadow.setPixmap(pixmap)
        
        del img
        del image
        del pixmap
                      
        self.imgSize = width, height  ## save for later 
        self.viewW, self.viewH = viewW, viewH
        
        pos = self.pixitem.pos()
        x, y = pos.x(), pos.y()
                                  
        self.shadow.setX(x-50)  ## same as pixitem, add offset
        self.shadow.setY(y-15)  
            
        self.shadow.setOpacity(self.alpha)                                  
        self.scene.addItem(self.shadow)  
   
        QTimer.singleShot(100, self.shadow.initPoints)  
                                                                                                                                                                   
### --------------------------------------------------------                         
    async def restoreShadow(self):  ## reads from play file   
        for k in range(4):
            x = self.pixitem.shadow['pathX'][k]
            y = self.pixitem.shadow['pathY'][k]
            self.path.append(QPointF(x,y))
                  
        self.viewW, self.viewH = common['ViewW'],common['ViewH'] 
                    
        file, w, h = self.works.pixWidthHeight()  
        flop = self.pixitem.flopped 
                    
        try:  ## without the await it takes longer 
            await self.addShadow(w, h, self.viewW, self.viewH) 
            self.cpy, _, _, _ = await initShadow(file, w, h, flop)
        except TypeError:  ## no fault error trap
            pass
                                                   
        self.imgSize = self.pixitem.shadow['width'], self.pixitem.shadow['height']  
        self.alpha   = self.pixitem.shadow['alpha']
        self.scalor  = self.pixitem.shadow['scalor']
        self.rotate  = self.pixitem.shadow['rotate']
        self.flopped  = self.pixitem.shadow['flopped']
        self.linked  = self.pixitem.shadow['linked']
        
        self.tag = ''
        self.type = 'shadow'
        self.fileName = 'shadow'
        self.restore = True
                               
        self.addPoints() 
        self.updateShadow()
        
        self.shadow.setOpacity(self.alpha)
                                                                                                                                                       
### --------------------------------------------------------
    def updateShadow(self):  ## if rotated, scaled or points moved           
        cpy = self.flopCpy if self.flopped else self.cpy 
        
        linked = self.linked
                            
        img, width, height, bytesPerLine = setPerspective(
            self.path, 
            self.imgSize[0], 
            self.imgSize[1],
            cpy, 
            self.viewW, self.viewH)
         
        img = QImage(img.data, width, height, bytesPerLine, QImage.Format.Format_ARGB32) 
        
        x, y, w, h = getCrop(self.path)   
        img = img.copy(x, y, w, h)      
        
        pixmap = QPixmap.fromImage(img)     
        self.works.removeShadow()
          
        self.shadow = Shadow(self)      
        self.shadow.setPixmap(pixmap)    
        
        del img
        del pixmap
         
        self.shadow.setX(x)  
        self.shadow.setY(y)  
        
        self.linked = linked   
        self.shadow.setOpacity(self.alpha) 
        
        self.scene.addItem(self.shadow) 
        
        self.works.updateOutline()
          
        if self.linked == True:     
            self.shadow.setParentItem(self.pixitem)
            self.shadow.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemStacksBehindParent)   
            self.shadow.setPos(-self.pixitem.pos()+self.shadow.pos())
                                                                                         
### --------------------------------------------------------    
    def addWidget(self):  ## creates a shadow widget 
        self.works.closeWidget()
        self.widget = ShadowWidget(self)  
                             
        linked = self.linked  
              
        if self.linked:  
            p = self.pixitem.pos()+self.shadow.pos()               
            self.shadow.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
            self.widget.linkBtn.setText('UnLink')
            self.works.hideOutline()       
        else:
            p = self.shadow.pos()  ## this works 
            self.widget.linkBtn.setText('Link') 
                                               
        x, y = int(p.x()), int(p.y())
        p = self.canvas.mapToGlobal(QPoint(x, y))
                                    
        x, y = int(p.x()), int(p.y())   
        x = int(x - int(self.widget.WidgetW)-10)
        y = int(y - int(self.widget.WidgetH)/6)    
 
        self.linked = linked 
        
        self.widget.setGeometry(x, y, int(self.widget.WidgetW), int(self.widget.WidgetH))   
            
### --------------------------------------------------------
    def addPoints(self): 
        self.works.deletePoints() 
          
        self.topLeft  = PointItem(self.path[0], 'topLeft', self)
        self.topRight = PointItem(self.path[1], 'topRight', self)
        self.botRight = PointItem(self.path[2], 'botRight', self)
        self.botLeft  = PointItem(self.path[3], 'botLeft', self)
                
        self.points.append(self.topLeft)  
        self.points.append(self.topRight)  
        self.points.append(self.botRight )         
        self.points.append(self.botLeft) 
        
        self.works.addPointsToScene()                   
       
    def updatePoints(self, i, x, y):  ## offset for x,y of ellipse    
        if i == 0:
            self.topLeft.setRect(x-V*.5, y-V*.5, V,V) 
        elif i == 1:      
            self.topRight.setRect(x-V*.5, y-V*.5, V,V)         
        elif i == 3: 
            self.botLeft.setRect(x-V*.5, y-V*.5, V,V) 
        else:                          
            self.botRight.setRect(x-V*.5, y-V*.5, V,V)

### --------------------------------------------------------   
    def newShadow(self):  ## add shadow from shadow widget
        self.works.cleanUpShadow()
        b = self.pixitem.boundingRect()
        self.addShadow(b.width(), b.height(), self.viewW, self.viewH)      
        self.alpha, self.scalor, self.rotate = .50, 1.0, 0
                         
    def toggleLink(self):  ## unlinks as well
        if self.shadow != None:
            if self.linked == False and self.widget.linkBtn.text() == 'Link': 
                self.shadow.linkShadow()   
            elif self.linked == True and self.widget.linkBtn.text() == 'UnLink':
                self.shadow.unLinkShadow()  
             
    def rotateScale(self, per, inc):  ## uses path rather than pts
        x, y, w, h = getCrop(self.path)   ## uses getCrop 
        centerX, centerY = x + w/2, y + h/2
        
        linked = self.linked
        
        self.shadow.setTransformOriginPoint(centerX, centerY)
        self.shadow.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
           
        for i in range(4):  ## if you don't get 4 points...  
            dist = distance(self.path[i].x(), centerX, self.path[i].y(), centerY) 
              
            xdist, ydist = dist, dist      
            xdist = dist + (dist * per)              
            ydist = xdist
           
            deltaX = self.path[i].x() - centerX
            deltaY = self.path[i].y() - centerY

            angle = math.degrees(math.atan2(deltaX, deltaY))
            angle = angle + math.ceil( angle / 360) * 360

            plotX = centerX + xdist * math.sin(math.radians(angle + inc))
            plotY = centerY + ydist * math.cos(math.radians(angle + inc))
           
            self.path[i] = QPointF(plotX, plotY)
            self.updatePoints(i, plotX, plotY)
        
        self.linked = linked            
        self.updateShadow()    
   
### --------------------------------------------------------
    def setPath(self, b, p):  ## boundingRect and position
        self.path = []
        self.path.append(p)  
        self.path.append(QPointF(p.x() + b.width(), p.y()))  
        self.path.append(QPointF(p.x() + b.width(), p.y() + b.height()))         
        self.path.append(QPointF(p.x(), p.y() + b.height()))
 
    def updatePath(self, val):  ## see shadowWidget for ItemSendsScenePositionChanges
        dif = val - self.shadow.save    
        self.shadow.setPos(self.shadow.pos()+dif)         
        for i in range(4):  
            self.path[i] = self.path[i] + dif
            self.updatePoints(i, self.path[i].x(), self.path[i].y())
        self.shadow.save = val
                                                                                                
### --------------------------------------------------------                                                  
    def flip(self):          
        self.works.deleteOutline()
                    
        x, t, b = self.path[0].x(), self.path[0].y(), self.path[3].y()
        y = b + (b - t)
        self.path[0] = QPointF(x,y)  
        
        x1, t, b = self.path[1].x(), self.path[1].y(), self.path[2].y()
        y1 = b + (b - t)
        self.path[1] = QPointF(x1, y1) 
           
        self.addPoints()
        self.updatePoints(0, x, y)     
        self.updatePoints(1, x1, y1)   
        QTimer.singleShot(100, self.updateShadow)
            
    def flop(self):
        self.setMirrored(False) if self.flopped else self.setMirrored(True)
            
    def setMirrored(self, bool):
        self.flopped = bool 
        self.flopPath()
        self.updateShadow()
        
    def flopPath(self):                                               
        x0, y0 = self.path[0].x(), self.path[0].y()
        x1, y1 = self.path[1].x(), self.path[1].y()
        d = x1 - x0

        self.path[0] = QPointF(x1 - d, y1)
        self.path[1] = QPointF(x0 + d, y0)

        x2, y2 = self.path[2].x(), self.path[2].y()
        x3, y3 = self.path[3].x(), self.path[3].y()
        d = x3 - x2

        self.path[2] = QPointF(x3 - d,y3)
        self.path[3] = QPointF(x2 + d, y2)
                 
        self.addPoints() 
        x, y = self.path[0].x(),  self.path[0].y()
        self.updatePoints(0, x, y)    
        
        x, y = self.path[1].x(),  self.path[1].y()
        self.updatePoints(1, x, y)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
### ------------------- dotsShadowMaker --------------------
                                                                                                                                                          



          