
import math

from PyQt6.QtCore       import QObject, QPointF, QTimer
from PyQt6.QtGui        import QImage, QPixmap, QPolygonF
from PyQt6.QtWidgets    import QGraphicsPolygonItem
                           
from dotsShadowWorks    import *
from dotsShared         import common
from dotsSideGig        import distance

V = common["V"]  ## the diameter of a pointItem, same as in ShadowWorks
       
### ------------------- dotsShadowMaker --------------------
''' a.k.a. fab - handles shadow, menu, and points classes '''                                                                                                                    
### -------------------------------------------------------- 
class ShadowMaker:  
### --------------------------------------------------------    
    def __init__(self, parent):
        super().__init__()
                  
        self.pixitem = parent
        self.scene   = parent.scene

        self.topLeft  = None
        self.topRight = None
        self.botLeft  = None
        self.botRight = None
        
        self.path = [] 
        self.points = []  
   
        self.ishidden = False

        self.alpha  = .50
        self.scalor = 1.0
        self.rotate =   0
        
        self.cpy     = None  ## save original grey image 
        self.outline = None  
        self.shadow  = None
        self.widget  = None
        
        ## blank to add/restore shadows, 'pass' in dotsShadows_Dummy.py to skip
        self.addRestore = ""  
       
        self.imgSize = 0,0  ## last width and height of shadow

        self.WidgetW, self.WidgetH = 330.0, 190.0
        self.viewW, self.viewH = 0,0
                                     
### --------------------------------------------------------
    def addShadow(self, w, h, viewW, viewH):  ## initial shadow       
        if self.shadow != None:
            return
                
        file, w, h = self.pixWidthHeight()      
        flop = self.pixitem.flopped 
                                                    
        img, width, height, bytesPerLine = initShadow(file, w, h, flop)
            
        image = QImage(img.data, width, height, bytesPerLine, QImage.Format.Format_ARGB32)   
        # image.smoothScaled(width, height)  ## doesn't work
        
        pixmap = QPixmap.fromImage(image)
              
        self.shadow = Shadow(self) 
        self.shadow.setPixmap(pixmap)
      
        self.cpy = img   ## save it for later  
        self.imgSize = width, height  ## ditto, fixes a funny little bug
        self.viewW, self.viewH = viewW, viewH
           
        pos = self.pixitem.pos()
        x, y = pos.x(), pos.y()
                    
        self.shadow.setX(x-50)  ## same as pixmap, add offset
        self.shadow.setY(y-15)  
            
        self.shadow.setOpacity(self.alpha)  
        self.shadow.setScale(self.scalor)
        self.shadow.setRotation(self.rotate)
                          
        self.scene.addItem(self.shadow)
        
        QTimer.singleShot(100, self.shadow.initPoints)
              
 ### --------------------------------------------------------                         
    async def restoreShadow(self):       
        for k in range(len(self.pixitem.shadow['pathX'])):
            x = self.pixitem.shadow['pathX'][k]
            y = self.pixitem.shadow['pathY'][k]
            self.path.append(QPointF(x,y))
                  
        self.viewW, self.viewH = common["ViewW"],common["ViewH"] 
            
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
        self.ishidden = self.pixitem.shadow['ishidden']
        
        # print(self.pixitem.shadow['alpha'], self.pixitem.shadow['scalor'])   
        
        self.addPoints() 
        self.updateShadow()
                
        self.shadow.setOpacity(self.alpha)                
                                                                                                                 
### --------------------------------------------------------
    def updateShadow(self):  ## everything after initial
        self.deleteOutline() 
              
        img, width, height, bytesPerLine = setPerspective(
            self.path, 
            self.imgSize[0], 
            self.imgSize[1],
            self.cpy, self.viewW, self.viewH)
       
        img = QImage(img.data, width, height, bytesPerLine, QImage.Format.Format_ARGB32)
        ## img.smoothScaled(width, height)   ## still doesn't work
      
        pixmap = QPixmap.fromImage(img) 
        opacity = self.shadow.opacity()
        
        self.removeShadow()     
          
        self.shadow = Shadow(self)      
        self.shadow.setPixmap(pixmap)    
      
        self.shadow.setOpacity(opacity)        
        self.scene.addItem(self.shadow)   
        
        self.updateOutline()  
 
### --------------------------------------------------------
    def addPoints(self):  ## gets called alot
        self.deletePoints() 
          
        self.topLeft  = PointItem(self.path[0], "topLeft", self)
        self.topRight = PointItem(self.path[1], "topRight", self)
        self.botRight = PointItem(self.path[2], "botRight", self)
        self.botLeft  = PointItem(self.path[3], "botLeft", self)
              
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
            if self.ishidden:
                p.hide()                              
            self.scene.addItem(p)
   
    def deletePoints(self):  ## the path stays
        for p in self.points:  
            self.scene.removeItem(p) 
        self.points = []
                                                       
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
    
    def pixWidthHeight(self):
        b = self.pixitem.sceneBoundingRect()
        return self.pixitem.fileName, b.width(), b.height()
        
### --------------------------------------------------------    
    def addWidget(self):
        self.closeWidget()
        self.widget = ShadowWidget(self)
        p = self.path[0]
        x, y = int(p.x()), int(p.y()+50)  ## safer here       
        if y > self.path[3].y():
            y = int(self.path[3].y())     
        self.widget.setGeometry(x-20, y, int(self.WidgetW), int(self.WidgetH))
        self.resetSliders()
       
    def closeWidget(self):
        if self.widget != None:
            self.widget.close()
            self.widget = None
        
### --------------------------------------------------------
    def deleteShadow(self): 
        if self.shadow != None:
            self.closeWidget()
            self.deleteOutline()
            self.deletePoints()
            self.removeShadow()
            self.shadow = None
                      
    def newShadow(self):
        self.closeWidget()
        self.deleteOutline()
        self.deletePoints()  
   
        b = self.pixitem.sceneBoundingRect()

        width  = b.width()
        height = b.height()
        viewW  = self.viewW
        viewH  = self.viewH
        
        self.removeShadow()   
        self.shadow = None 
        
        self.addShadow(width, height, viewW, viewH)        
        self.alpha, self.scalor, self.rotate, self.ishidden = .50, 1.0, 0, False
   
    def removeShadow(self):
        self.scene.removeItem(self.shadow)   
          
    def resetSliders(self):       
        self.widget.opacitySlider.setValue(int(self.alpha*100))
        self.widget.scaleSlider.setValue(int(self.scalor*100))
        self.widget.rotaryDial.setValue(int(self.rotate))

### --------------------------------------------------------                
    def updateOutline(self): 
        self.deleteOutline()
        self.outline = QGraphicsPolygonItem(self.addOutline()) 
        self.outline.setPen(QPen(QColor("lime"), 2, Qt.PenStyle.DotLine))
        self.outline.setZValue(25) 
        if self.ishidden:
            self.outline.hide()    
        self.scene.addItem(self.outline)
    
    def addOutline(self):  
        outline = QPolygonF()   
        for p in self.path:  
            outline.append(QPointF(p))
        return outline 
    
    def deleteOutline(self): 
        if self.outline != None:
            self.scene.removeItem(self.outline)
            self.outline = None
            
### --------------------------------------------------------
    def hideAll(self):
        if self.ishidden == False:
            self.ishidden = True
            if self.outline != None:
                self.outline.hide()
            self.hidePoints()  
        elif self.ishidden == True: 
            self.ishidden = False    
            self.updateOutline()
            self.hidePoints(False) 
                                                          
    def hidePoints(self, hide=True): 
        for p in self.points:       
            p.hide() if hide == True else p.show()         
      
    def rotateShadow(self, val): 
        inc = (val - self.rotate)
        self.rotateScale(0, -inc)
        self.rotate = val
      
    def scaleShadow(self, val): 
        per = (val - self.scalor) / self.scalor    
        self.rotateScale(per, 0)
        self.scalor = val
            
    def rotateScale(self, per, inc):
        self.deleteOutline()         
        centerX, centerY = self.centerXY()
        
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
    
        self.updateShadow() 
                   
    def centerXY(self): 
        self.addPoints()         
        x = self.path[2].x() - self.path[0].x() 
        x = self.path[0].x() + ( x / 2 )
        y = self.path[3].y() - self.path[1].y() 
        y = self.path[1].y() + ( y / 2 )
        return x, y
                                                  
### ------------------- dotsShadowMaker --------------------
                                                                                                                                                          
