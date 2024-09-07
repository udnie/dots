
import math

from PyQt6.QtCore       import Qt, QPointF, QRectF, QTimer
from PyQt6.QtGui        import QColor, QPen, QPolygonF
from PyQt6.QtWidgets    import QGraphicsEllipseItem, QGraphicsPolygonItem
    
from dotsShared         import common    
from dotsSideGig        import distance, getCrop

PathStr = ['topLeft','topRight','botRight','botLeft'] 
V = common['V']  ## the diameter of a pointItem, same as in ShadowWidget       
                                            
### -------------------- dotsShadowWorks -------------------
''' classes: Works and PointItem '''
### --------------------------------------------------------
class Works:  ## small functions that were in ShadowMaker
### --------------------------------------------------------
    def __init__(self, parent, switch=''):
        super().__init__()
 
        self.maker   = parent
        self.canvas  = self.maker.canvas
        self.scene   = self.maker.scene
        
        self.switch = switch
             
### --------------------------------------------------------
    def resetSliders(self): 
        self.maker.widget.opacitySlider.setValue(int(self.maker.alpha*100))
        self.maker.widget.opacityValue.setText(f'{self.maker.alpha:.2f}')
        
        self.maker.widget.scaleSlider.setValue(int(self.maker.scalor*100))
        self.maker.widget.scaleValue.setText(f'{self.maker.scalor:.2f}')
        
        self.maker.widget.rotaryDial.setValue(int(self.maker.rotate))
        self.maker.widget.rotateValue.setText(f'{self.maker.rotate:3}')
         
    def closeWidget(self):
        if self.maker.widget != None:
            self.maker.widget.close()     
            self.maker.widget = None  
            if self.switch == 'on':
                self.canvas.setKeys('M')
        
    def deleteShadow(self): 
        if self.maker.shadow != None:
            self.cleanUpShadow()
        self.maker.shadow = None
        self.maker.pixitem.shadow = None  ## using it throughout
                                                          
    def cleanUpShadow(self):  
        self.closeWidget()
        self.deletePoints()  
        self.deleteOutline()
        self.removeShadow()
   
    def removeShadow(self):
        if self.maker.shadow != None:
            self.scene.removeItem(self.maker.shadow)
            self.maker.linked = False
            self.maker.shadow = None
    
    def addPointsToScene(self, hide=True):
        for p in self.maker.points:   
            p.setZValue(self.maker.shadow.zValue())
            if self.maker.isHidden or \
                self.maker.linked == True or hide == False:
                p.hide()                          
            self.scene.addItem(p)
                             
    def deletePoints(self):  ## the path stays
        for p in self.maker.points:  
            self.scene.removeItem(p) 
            del p
        self.maker.points.clear()

### --------------------------------------------------------
    def updateOutline(self, hide=''): 
        self.deleteOutline()
        self.maker.outline = QGraphicsPolygonItem(self.makeOutline()) 
        self.maker.outline.setPen(QPen(QColor('lime'), 2, Qt.PenStyle.DotLine))
        self.maker.outline.setZValue(common['outline'])       
        if self.maker.linked == True or hide != '':  ## used throughout shadow and updateShadow
            self.hideOutline()  
            self.maker.dblclk = False
        self.maker.outline.setZValue(self.maker.shadow.zValue()-1)   
        self.scene.addItem(self.maker.outline)
        
    def toggleOutline(self):
        if self.maker.outline != None:
            if self.maker.outline.isVisible() == True:
                self.hideOutline() 
            elif self.maker.outline.isVisible() == False:
                self.showOutline()
            self.closeWidget()
  
    def deleteOutline(self): 
        if self.maker.outline != None:
            self.scene.removeItem(self.maker.outline)
        self.maker.outline = None
                      
    def makeOutline(self):  
        outline = QPolygonF()   
        for p in self.maker.path:  
            outline.append(QPointF(p))
        return outline 
                
    def hidePoints(self, hide=True): 
        for p in self.maker.points:       
            p.hide() if hide == True else p.show()  
                              
    def hideOutline(self):
        if self.maker.outline != None:
            self.maker.outline.hide()
            self.hidePoints()  ## default True       
            
    def showOutline(self):
        if self.maker.outline != None:
            self.maker.outline.setVisible(True)
            self.maker.updatePath(self.maker.shadow.save)  ## a QPointF class attr.
            self.updateOutline()
            self.maker.outline.show()
            self.hidePoints(False)      
      
### --------------------------------------------------------                                                                
    def rotateShadow(self, val): 
        inc = (val - self.maker.rotate)
        self.rotateScale(0, -inc)
        self.maker.rotate = val
      
    def scaleShadow(self, val): 
        per = (val - self.maker.scalor) / self.maker.scalor    
        self.rotateScale(per, 0)
        self.maker.scalor = val
                                                                                                             
    def pixWidthHeight(self):
        b = self.maker.pixitem.boundingRect()  
        return self.maker.pixitem.fileName, b.width(), b.height() 
   
### --------------------------------------------------------  
    def flip(self):          
        self.deleteOutline() 
                        
        x, t, b = self.maker.path[0].x(), self.maker.path[0].y(), self.maker.path[3].y()
        y = b + (b - t)
        self.maker.path[0] = QPointF(x,y)  
        
        x1, t, b = self.maker.path[1].x(), self.maker.path[1].y(), self.maker.path[2].y()
        y1 = b + (b - t)
        self.maker.path[1] = QPointF(x1, y1) 
           
        self.maker.addPoints()
        self.maker.updatePoints(0, x, y)     
        self.maker.updatePoints(1, x1, y1) 
          
        QTimer.singleShot(100, self.maker.updateShadow)
        
    def flopPath(self):                                               
        x0, y0 = self.maker.path[0].x(), self.maker.path[0].y()
        x1, y1 = self.maker.path[1].x(), self.maker.path[1].y()
        d = x1 - x0

        self.maker.path[0] = QPointF(x1 - d, y1)
        self.maker.path[1] = QPointF(x0 + d, y0)

        x2, y2 = self.maker.path[2].x(), self.maker.path[2].y()
        x3, y3 = self.maker.path[3].x(), self.maker.path[3].y()
        d = x3 - x2

        self.maker.path[2] = QPointF(x3 - d,y3)
        self.maker.path[3] = QPointF(x2 + d, y2)
                 
        self.maker.addPoints() 
        x, y = self.maker.path[0].x(),  self.maker.path[0].y()
        self.maker.updatePoints(0, x, y)    
        
        x, y = self.maker.path[1].x(),  self.maker.path[1].y()
        self.maker.updatePoints(1, x, y)
        
### --------------------------------------------------------            
    def rotateScale(self, per, inc):  ## uses path rather than pts 
        self.maker.shadow.setOriginPt() 
        
        x, y, w, h = getCrop(self.maker.path)   ## uses getCrop 
        centerX, centerY = x + w/2, y + h/2
          
        self.maker.shadow.setTransformOriginPoint(centerX, centerY)
        self.maker.shadow.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
           
        for i in range(4):  ## if you don't get 4 points...  
            dist = distance(self.maker.path[i].x(), centerX, self.maker.path[i].y(), centerY) 
              
            xdist, ydist = dist, dist      
            xdist = dist + (dist * per)              
            ydist = xdist
           
            deltaX = self.maker.path[i].x() - centerX
            deltaY = self.maker.path[i].y() - centerY

            angle = math.degrees(math.atan2(deltaX, deltaY))
            angle = angle + math.ceil( angle / 360) * 360

            plotX = centerX + xdist * math.sin(math.radians(angle + inc))
            plotY = centerY + ydist * math.cos(math.radians(angle + inc))
           
            self.maker.path[i] = QPointF(plotX, plotY)
            self.maker.updatePoints(i, plotX, plotY)
                 
        self.maker.updateShadow('nope')  ## entering a string turns off the outline
           
### --------------------------------------------------------
class PointItem(QGraphicsEllipseItem): 
### --------------------------------------------------------
    def __init__(self, pt, ptStr, parent):
        super().__init__()

        self.maker = parent
        self.maker.path  = self.maker.path   
        self.ptStr = ptStr
        
        self.type = 'point'
        self.fileName = 'point'
        
        self.tag = 'point'  
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
            self.maker.path[i] = QPointF(x,y)                  
        
    def topLeft(self, x, y):
        w, y1 = self.current(0,1)            
        self.maker.path[0] = QPointF(x,y) 
        self.maker.path[1] = QPointF(x+w,y1)
        self.maker.topRight.setRect(x+(w-V*.5), y1-V*.5, V,V)  
        
    def botLeft(self, x, y):
        w, y1 = self.current(3,2)            
        self.maker.path[3] = QPointF(x,y) 
        self.maker.path[2] = QPointF(x+w,y1)
        self.maker.botRight.setRect(x+(w-V*.5), y1-V*.5, V,V)          
        
    def current(self,a,b):
        l = self.maker.path[a].x()
        r = self.maker.path[b].x()
        return r - l,  self.maker.path[b].y()
         
### -------------------- dotsShadowWorks -------------------




