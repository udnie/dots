
import os
import time

from PyQt6.QtCore       import QPoint, QPointF, QTimer
from PyQt6.QtGui        import QImage, QPixmap

from dotsShared         import common, paths
from dotsShadow         import *                  
from dotsShadowWidget   import ShadowWidget
from dotsShadowWorks    import Works, PointItem
from dotsSideGig        import getCrop
from dotsHelpMonkey     import ShadowHelp

V = common['V']  ## the diameter of a pointItem, same as in ShadowWidget

### ------------------- dotsShadowMaker --------------------
''' class: ShadowMaker - handles shadow, widget and points'''                                                                                                                    
### -------------------------------------------------------- 
class ShadowMaker:  
### --------------------------------------------------------    
    def __init__(self, parent, switch=''):
        super().__init__()
            
        self.switch = switch          
        
        self.pixitem = parent
        self.canvas  = self.pixitem.canvas
        self.scene   = self.pixitem.scene                          

        self.works = Works(self, self.switch)  ## small functions and pointItem

        self.init()    
 
### --------------------------------------------------------
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
        self.dblclk   = False

        self.alpha  = .50
        self.scalor = 1.0
        self.rotate =   0
        
        self.cpy     = None  ## saved original grey image 
        self.flopCpy  = None
        
        self.outline = None  
        self.shadow  = None
        self.widget  = None
       
        self.width = 0
        self.height = 0
       
        self.viewW, self.viewH = 0,0
        
        self.last = QPointF()
 
### --------------------------------------------------------
    def addShadow(self, w, h, viewW, viewH):  ## from scatch      
        if self.shadow != None:
            return        
        file, w, h = self.works.pixWidthHeight()  ## returns file as well as width and height      
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
                              
        self.width, self.height = width, height  ## save for later 
        self.viewW, self.viewH = viewW, viewH
        
        pos = self.pixitem.pos()
        x, y = pos.x(), pos.y()
                                                                                          
        self.shadow.setZValue(self.pixitem.zValue()-1) 
                                                               
        self.shadow.setX(x-50)  ## same as pixitem, add offset
        self.shadow.setY(y-15)  
       
        self.shadow.setOpacity(self.alpha)                                  
        self.scene.addItem(self.shadow)  
   
        QTimer.singleShot(100, self.shadow.initPoints)  ## sets outline on open
                                                                                                                                                    
### --------------------------------------------------------                         
    async def restoreShadow(self):  ## reads from pixitem.shadow, a copy of the shadow data from the .play file
        if self.pixitem.shadow == None:
            return
        
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
                                         
        self.width   = self.pixitem.shadow['width']
        self.height  = self.pixitem.shadow['height']  
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
    ## if rotated, scaled or points moved or loaded from a play file   
    def updateShadow(self, what=''):    
        if self.path != None and len(self.path) == 0:
            return
                    
        cpy = self.flopCpy if self.flopped else self.cpy  ## called by shadow and poinitem
        
        linked = self.linked       ## these 2 aren't carried over and need to be restored
        save   = self.shadow.save  ## used if linked for storing current position
                  
        img, width, height, bytesPerLine = setPerspective(
            self.path, 
            self.width, 
            self.height,
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
                     
        self.works.updateOutline(what)  ## to turn off outline
                                                                                
### --------------------------------------------------------    
    def addWidget(self, shadow, switch=''):  ## creates a shadow widget   
        if switch == '':  
            self.works.closeWidget()
        self.widget = ShadowWidget(self, self.shadow, self.switch)  
        
        if self.linked == False:  ## not linked
            self.widget.linkBtn.setText('Link') 
        else:      
            self.widget.linkBtn.setText('UnLink')  ## link == True
               
        if self.path != None and len(self.path) > 0:       
            p = self.shadow.sceneBoundingRect()     
                                           
            x, y = int(p.x()), int(p.y())  
            self.last = QPointF(x,y)  ## last position   
                
            p = self.canvas.mapToGlobal(QPoint(x, y))
            x, y = int(p.x()), int(p.y())       
            x = int(x - int(self.widget.WidgetW)-10)  ## offset from shadow
            y = int(y - int(self.widget.WidgetH)*.15)    
            
            self.widget.save = QPointF(x,y)  
            self.widget.setGeometry(x, y, int(self.widget.WidgetW), int(self.widget.WidgetH))   
            
        self.works.resetSliders()
        return self.widget 
                                                
### --------------------------------------------------------
    def addPoints(self, hide=True): 
        self.works.deletePoints()  ## cleared points

        if len(self.path) == 0:
            for i in range(4): 
                self.path.append(QPointF())
   
        self.topLeft  = PointItem(self.path[0], 'topLeft', self)
        self.topRight = PointItem(self.path[1], 'topRight', self)
        self.botRight = PointItem(self.path[2], 'botRight', self)
        self.botLeft  = PointItem(self.path[3], 'botLeft', self)
                
        self.points.append(self.topLeft)  
        self.points.append(self.topRight)  
        self.points.append(self.botRight )         
        self.points.append(self.botLeft) 
        
        self.works.addPointsToScene(hide)                   
       
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
        self.path.clear()
        self.path.append(p)  
        self.path.append(QPointF(p.x() + b.width(), p.y()))  
        self.path.append(QPointF(p.x() + b.width(), p.y() + b.height()))         
        self.path.append(QPointF(p.x(), p.y() + b.height()))
 
    def updatePath(self, val):  ## see shadow for ItemSendsScenePositionChanges 
        if self.path != None and len(self.path) > 0:    
            dif = val - self.shadow.save          
            for i in range(4):
                self.path[i] = self.path[i] + dif
                self.updatePoints(i, self.path[i].x(), self.path[i].y())              
            self.shadow.save = val      
            if self.linked == False:    ## updated by shadow
                self.shadow.setPos(self.shadow.pos()+dif) 
                if self.dblclk == True: ## turns on outline and points    
                    self.works.updateOutline()    
                else:
                    self.works.hideOutline()  ## hides points as well
            else:                             ## updated by pixitem
                self.shadow.setPos(self.pixitem.pos()+self.pixitem.offset)
      
### --------------------------------------------------------   
    def openMenu(self):
        self.works.closeWidget()  
        self.help = ShadowHelp(self,0,'pix')  
    
    def getXY(self):  ## there's a makeXY in pixworks but this one is for shadows
        p = self.shadow.pos()
        p = self.canvas.mapToGlobal(QPoint(int(p.x()), int(p.y())))
        return int(p.x()), int(p.y())
    
    def newShadow(self):  ## 'new' from shadow widget
        self.works.cleanUpShadow()
        b = self.pixitem.boundingRect()
        self.addShadow(b.width(), b.height(), self.viewW, self.viewH)      
        self.alpha, self.scalor, self.rotate = .50, 1.0, 0
                         
    def toggleWidgetLink(self): 
        if self.shadow != None:
            if self.linked == False and self.widget.linkBtn.text() == 'Link': 
                self.shadow.linkShadow()   
            elif self.linked == True and self.widget.linkBtn.text() == 'UnLink':
                self.shadow.unlinkShadow()  
                                                                                                             
### --------------------------------------------------------                                                              
    def flop(self):
        self.setMirrored(False) if self.flopped else self.setMirrored(True)
            
    def setMirrored(self, bool):
        self.flopped = bool 
        self.works.flopPath()
        self.updateShadow()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
### ------------------- dotsShadowMaker --------------------
                                                                                                                                                          
                                                                                                                                                          

          