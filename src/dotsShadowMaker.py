
import os
import time

from PyQt6.QtCore       import QPoint, QPointF, QTimer
from PyQt6.QtGui        import QImage, QPixmap

from dotsShared         import common, paths
from dotsShadow         import *                      
from dotsShadowWidget   import ShadowWidget
from dotsShadowWorks    import Works, PointItem
from dotsSideGig        import getCrop, point

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
      
        self.works = Works(self)  ## small functions and pointItem

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
        
        self.cpy     = None  ## saved original grey image 
        self.flopCpy  = None
        
        self.outline = None  
        self.shadow  = None
        self.widget  = None
       
        self.imgSize = 0,0  ## last width and height of shadow
        self.viewW, self.viewH = 0,0
        
        self.last = QPointF()
 
### --------------------------------------------------------
    def addShadow(self, w, h, viewW, viewH):  ## initial shadow       
        if self.shadow != None:
            return 
                 
        file, w, h = self.works.pixWidthHeight()          
        file = paths['spritePath'] + os.path.basename(file) 
                                 
        img, width, height, bytesPerLine = initShadow(file, w, h, self.pixitem.flopped)
       
        self.cpy = img   ## save it for later  
        self.flopCpy = cv2.flip(img, 1)  ## use this if shadow is flopped
                         
        image = QImage(img.data, width, height, bytesPerLine, QImage.Format.Format_ARGB32)    
        pixmap = QPixmap.fromImage(image)
                  
        self.shadow = Shadow(self)  ## from Shadow
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
        file = paths['spritePath'] + os.path.basename(file) 
      
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
        
        if self.linked == True: self.shadow.linkShadow()
        
        self.shadow.setOpacity(self.alpha)
                                                                                                                                                       
### --------------------------------------------------------
    def updateShadow(self):  ## if rotated, scaled or points moved           
        cpy = self.flopCpy if self.flopped else self.cpy  ## called by shadow and poinitem
        
        linked = self.linked     ## these 2 aren't carried over and need to be restored
        save = self.shadow.save  ## used if linked for storing current position
                          
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
        
        self.linked = linked  ## back to shadow
        self.shadow.save = save  
                            
        if linked == True and self.restore == False:
            self.shadow.setX(self.last.x())  
            self.shadow.setY(self.last.y()) 
        else:
            self.shadow.setX(x)  
            self.shadow.setY(y) 
           
        self.shadow.setOpacity(self.alpha)  
        
        self.scene.addItem(self.shadow)    
        self.works.updateOutline()
                                                                                                
### --------------------------------------------------------    
    def addWidget(self):  ## creates a shadow widget     
        self.works.closeWidget()
        self.widget = ShadowWidget(self)  
        
        if self.linked == False:  ## not linked
            self.widget.linkBtn.setText('Link') 
        else:      
            self.widget.linkBtn.setText('UnLink')  ## link == True
          
        p = self.shadow.pos()                                            
        x, y = int(p.x()), int(p.y())  
        self.last = QPointF(x,y)  ## last position   
            
        p = self.canvas.mapToGlobal(QPoint(x, y))
        x, y = int(p.x()), int(p.y())       
        x = int(x - int(self.widget.WidgetW)-10)  ## offset from shadow
        y = int(y - int(self.widget.WidgetH)/6)    
        
        self.widget.save = QPointF(x,y)  
        self.widget.setGeometry(x, y, int(self.widget.WidgetW), int(self.widget.WidgetH))   
        
        self.works.resetSliders() 
                                                
### --------------------------------------------------------
    def addPoints(self): 
        self.works.deletePoints() 
        
        if self.path == None: self.path = []
          
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
    def setPath(self, b, p):  ## boundingRect and position
        self.path = []
        self.path.append(p)  
        self.path.append(QPointF(p.x() + b.width(), p.y()))  
        self.path.append(QPointF(p.x() + b.width(), p.y() + b.height()))         
        self.path.append(QPointF(p.x(), p.y() + b.height()))
 
    def updatePath(self, val):  ## see shadow for ItemSendsScenePositionChanges
        # start = time.time()  ## curious
        dif = val - self.shadow.save        
        for i in range(4):
            self.path[i] = self.path[i] + dif
            self.updatePoints(i, self.path[i].x(), self.path[i].y())
        self.shadow.save = val   
        if self.linked == False:    ## updated by shadow
            self.shadow.setPos(self.shadow.pos()+dif)   
        else:                       ## updated by pixitem
            self.shadow.setPos(self.pixitem.pos()+self.pixitem.offset)
        # end = time.time()  ## roughly .01...
        # print(end - start)  
        
### -------------------------------------------------------- 
    def newShadow(self):  ## add shadow from shadow widget
        self.works.cleanUpShadow()
        b = self.pixitem.boundingRect()
        self.addShadow(b.width(), b.height(), self.viewW, self.viewH)      
        self.alpha, self.scalor, self.rotate = .50, 1.0, 0
                         
    def toggleLink(self): 
        if self.shadow != None:
            if self.linked == False and self.widget.linkBtn.text() == 'Link': 
                self.shadow.linkShadow()   
            elif self.linked == True and self.widget.linkBtn.text() == 'UnLink':
                self.shadow.unLinkShadow()  
                                                                                                             
### --------------------------------------------------------                                                              
    def flop(self):
        self.setMirrored(False) if self.flopped else self.setMirrored(True)
            
    def setMirrored(self, bool):
        self.flopped = bool 
        self.works.flopPath()
        self.updateShadow()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
### ------------------- dotsShadowMaker --------------------
                                                                                                                                                          
                                                                                                                                                          

          