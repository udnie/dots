
import math
import os

from PyQt6.QtCore       import QPointF, QTimer
from PyQt6.QtGui        import QImage, QPixmap, QPolygonF
from PyQt6.QtWidgets    import QGraphicsPolygonItem
                           
from dotsShadowWorks    import *
from dotsShared         import common
from dotsSideGig        import distance, getCrop

V = common['V']  ## the diameter of a pointItem, same as in ShadowWorks
       
### ------------------- dotsShadowMaker --------------------
''' a.k.a. maker - handles shadow, menu, and points classes '''                                                                                                                    
### -------------------------------------------------------- 
class ShadowMaker:  
### --------------------------------------------------------    
    def __init__(self, parent):
        super().__init__()
                  
        self.pixitem = parent
        self.scene   = parent.scene
        
        self.init()
      
    def init(self):
        self.topLeft  = None
        self.topRight = None
        self.botLeft  = None
        self.botRight = None
        
        self.path = [] 
        self.points = []  
   
        self.flopped   = False
        self.isHidden = False  ## just a toggle - not saved
        self.isDummy  = False

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
                  
        file, w, h = self.pixWidthHeight()                                                      
        img, width, height, bytesPerLine = initShadow(file, w, h, self.pixitem.flopped)
       
        self.cpy = img   ## save it for later  
        self.flopCpy = cv2.flip(img, 1)  ## use this if shadow is flopped
                         
        image = QImage(img.data, width, height, bytesPerLine, QImage.Format.Format_ARGB32)    
        pixmap = QPixmap.fromImage(image)
                  
        self.shadow = Shadow(self)  ## from ShadowWorks *
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
        
        if self.pixitem.scale != 1.0 or self.pixitem.rotation != 0:
            self.shadow.hide()
                                        
        self.scene.addItem(self.shadow)      
        QTimer.singleShot(100, self.shadow.initPoints)
        
### --------------------------------------------------------         
    def newShadow(self):  ## add shadow from shadow widget
        self.cleanUpShadow()
        b = self.pixitem.boundingRect()
        self.addShadow(b.width(), b.height(), self.viewW, self.viewH)      
        self.alpha, self.scalor, self.rotate = .50, 1.0, 0    
        
### --------------------------------------------------------                         
    async def restoreShadow(self):  ## reads from play file   
        for k in range(len(self.pixitem.shadow['pathX'])):
            x = self.pixitem.shadow['pathX'][k]
            y = self.pixitem.shadow['pathY'][k]
            self.path.append(QPointF(x,y))
                  
        self.viewW, self.viewH = common['ViewW'],common['ViewH'] 
                    
        file, w, h = self.pixWidthHeight()  
        flop = self.pixitem.flopped 
                    
        try:  ## without the await it takes longer 
            await self.addShadow(w, h, self.viewW, self.viewH) 
            self.cpy, _, _, _ = await initShadow(file, w, h, flop)
        except TypeError:  ## no fault error trap
            pass
                                                   
        self.imgSize  = self.pixitem.shadow['width'], self.pixitem.shadow['height']  
        self.alpha    = self.pixitem.shadow['alpha']
        self.scalor   = self.pixitem.shadow['scalor']
        self.rotate   = self.pixitem.shadow['rotate']
        self.flopped   = self.pixitem.shadow['flopped']
        
        self.tag = ''
        self.type = 'shadow'
        self.fileName = 'shadow'
                  
        self.addPoints() 
        self.updateShadow()
        
        self.shadow.setOpacity(self.alpha)
        
        if self.outline != None: 
            self.outline.hide()
            self.hidePoints()
                                                                                                                                     
### --------------------------------------------------------
    def updateShadow(self):  ## if rotated, scaled or points moved      
        cpy = self.flopCpy if self.flopped else self.cpy 
                    
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
        self.removeShadow()     
   
        self.shadow = Shadow(self)      
        self.shadow.setPixmap(pixmap)    
        
        del img
        del pixmap
         
        self.shadow.setX(x)  
        self.shadow.setY(y)  
       
        self.shadow.setOpacity(self.alpha)     
        self.scene.addItem(self.shadow)   
        
        self.updateOutline()  
 
### --------------------------------------------------------
    def addPoints(self): 
        self.deletePoints() 
          
        self.topLeft  = PointItem(self.path[0], 'topLeft', self)
        self.topRight = PointItem(self.path[1], 'topRight', self)
        self.botRight = PointItem(self.path[2], 'botRight', self)
        self.botLeft  = PointItem(self.path[3], 'botLeft', self)
              
        self.points.append(self.topLeft)  
        self.points.append(self.topRight)  
        self.points.append(self.botRight )         
        self.points.append(self.botLeft)
        
        self.addPointsToScene()
    
    def updatePoints(self, i, x, y):  ## offset for x,y of ellipse    
        if i == 0:
            self.topLeft.setRect(x-V*.5, y-V*.5, V,V) 
        elif i == 1:      
            self.topRight.setRect(x-V*.5, y-V*.5, V,V)         
        elif i == 3: 
            self.botLeft.setRect(x-V*.5, y-V*.5, V,V) 
        else:                          
            self.botRight.setRect(x-V*.5, y-V*.5, V,V)
                  
    def addPointsToScene(self):
        for p in self.points:    
            if self.isHidden:
                p.hide()                              
            self.scene.addItem(p)
   
    def deletePoints(self):  ## the path stays
        for p in self.points:  
            self.scene.removeItem(p) 
        self.points = []
        
    def pixWidthHeight(self):
        b = self.pixitem.boundingRect()
        return self.pixitem.fileName, b.width(), b.height()
            
### --------------------------------------------------------                                                  
    def flip(self):          
        self.deleteOutline()
                    
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
                       
    def setPath(self, b, p):
        self.path = []
        self.path.append(p)  
        self.path.append(QPointF(p.x() + b.width(), p.y()))  
        self.path.append(QPointF(p.x() + b.width(), p.y() + b.height()))         
        self.path.append(QPointF(p.x(), p.y() + b.height()))
                                            
    def updatePath(self, val):   
        dif = val - self.shadow.save
        self.shadow.setPos(self.shadow.pos()+dif)         
        for i in range(4):  
            self.path[i] = self.path[i] + dif
            self.updatePoints(i, self.path[i].x(), self.path[i].y())
        self.shadow.save = val
        
### --------------------------------------------------------    
    def addWidget(self):
        self.closeWidget()
        self.widget = ShadowWidget(self)
        p = self.shadow.pos()
        x, y = int(p.x()), int(p.y())  
        f = common['widget']  ## necessary, it drifts with changes in size
        x1, y1 = int(f[0]), int(f[1])     
        self.widget.setGeometry(x+x1, y+y1, int(self.widget.WidgetW), int(self.widget.WidgetH))
        self.resetSliders()
                   
### --------------------------------------------------------           
    def cleanUpShadow(self):   
        self.closeWidget()
        self.removeShadow()  
        self.deleteOutline()
        self.deletePoints()
             
    def closeWidget(self):
        if self.widget != None:
            self.widget.close()
            self.widget = None
                  
    def deleteOutline(self): 
        if self.outline != None:
            self.scene.removeItem(self.outline)
            self.outline = None
                 
    def deleteShadow(self): 
        if self.shadow != None:
            self.cleanUpShadow()
            self.pixitem.shadow = None
                         
    def removeShadow(self):
        if self.shadow != None:
            self.scene.removeItem(self.shadow)
            self.shadow = None   
                   
    def resetSliders(self):       
        self.widget.opacitySlider.setValue(int(self.alpha*100))
        self.widget.scaleSlider.setValue(int(self.scalor*100))
        self.widget.rotaryDial.setValue(int(self.rotate))

### --------------------------------------------------------                
    def updateOutline(self): 
        self.deleteOutline()
        self.outline = QGraphicsPolygonItem(self.addOutline()) 
        self.outline.setPen(QPen(QColor('lime'), 2, Qt.PenStyle.DotLine))
        self.outline.setZValue(common['outline'])  
        if self.isHidden:
            self.outline.hide()    
        self.scene.addItem(self.outline)
        
    def toggleOutline(self):
        if self.outline != None:
            if self.outline.isVisible():
                self.outline.hide()
                self.hidePoints(True)
            else:
                self.outline.show()
                self.hidePoints(False)
        
    def addOutline(self):  
        outline = QPolygonF()   
        for p in self.path:  
            outline.append(QPointF(p))
        return outline 
      
### --------------------------------------------------------    
    def hideAll(self):
        if self.isHidden == False:
            self.isHidden = True
            if self.outline != None:
                self.outline.hide()
            self.hidePoints()  
        elif self.isHidden == True: 
            self.isHidden = False    
            self.updateOutline()
            self.hidePoints(False) 
                                                          
    def hidePoints(self, hide=True): 
        for p in self.points:       
            p.hide() if hide == True else p.show()         
  
### --------------------------------------------------------               
    def rotateShadow(self, val): 
        inc = (val - self.rotate)
        self.rotateScale(0, -inc)
        self.rotate = val
      
    def scaleShadow(self, val): 
        per = (val - self.scalor) / self.scalor    
        self.rotateScale(per, 0)
        self.scalor = val
            
    def rotateScale(self, per, inc):  ## uses path rather than pts
        x, y, w, h = getCrop(self.path)   ## uses getCrop 
        centerX, centerY = x + w/2, y + h/2
        
        self.shadow.setTransformOriginPoint(centerX, centerY)
        self.shadow.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
           
        for i in range(0, len(self.path)):  ## if you don't get 4 points...  
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
    
        self.updateShadow()  ## updates shadow 
                                                                  
### ------------------- dotsShadowMaker --------------------
                                                                                                                                                          
