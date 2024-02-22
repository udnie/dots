
import os

from PyQt6.QtCore       import QPointF, pyqtSlot, QRect, QRectF
from PyQt6.QtGui        import QColor
from PyQt6.QtWidgets    import QGraphicsEllipseItem

from dotsShared         import MoveKeys    
from dotsTagsAndPaths   import TagIt
       
V = 7.5  ## the diameter of a pointItem

### -------------------- dotsPathItem ----------------------
''' classes:  PathItem - represents a point  '''                                                                                         
### --------------------------------------------------------
class PathItem(QGraphicsEllipseItem):
### --------------------------------------------------------
    def __init__(self, parent, pt, idx, adto):
        super().__init__()

        self.pathMaker = parent
        self.canvas    = self.pathMaker.canvas
        self.scene     = self.pathMaker.scene
        self.edits     = self.pathMaker.edits
          
        self.pt = pt
        self.idx = idx
        self.setZValue(int(idx+adto)) 
        
        self.selections = self.pathMaker.selections  ## less to type
        
        self.pointTag = ''

        self.type = 'pt'
        self.fileName = None  ## just to make sure if referenced
     
        ## -V*.5 so it's centered on the path 
        self.x = pt.x()-V*.5
        self.y = pt.y()-V*.5
        self.setRect(self.x, self.y, V, V)  
        
        if self.selections and idx in self.selections:
            self.setBrush(QColor('lime'))
        else:
            self.setBrush(QColor('white'))   
               
        self.maptos = QPointF()
        self.dragCnt = 0
            
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, True)
          
        self.setAcceptHoverEvents(True)

 ### --------------------------------------------------------
    @pyqtSlot(str)
    def setPixKeys(self, key):
        if self.idx in self.selections and key in MoveKeys: 
            self.moveThis(MoveKeys[key])
            
    def hoverEnterEvent(self, e):
        if self.pathMaker.pathSet:  
            pct = (self.idx/len(self.pathMaker.pts))*100
            tag = self.pathMaker.pathWays.makePtsTag(self.pt, self.idx, pct)
            self.pointTag = TagIt('points', tag, QColor('YELLOW')) 
            self.pointTag.setPos(QPointF(self.pt)+QPointF(-20.0,-30.0))
            self.pointTag.setZValue(self.pathMaker.pathWorks.findTop()+5)
            self.scene.addItem(self.pointTag)
            p = self.rect()      
            if p.width() < V*1.5:  ## make it larger
                self.setRect(QRectF(p.x(), p.y(), V*1.5, V*1.5))   
        e.accept()

    def hoverLeaveEvent(self, e):
        self.cleanUp()
        e.accept()

    def mousePressEvent(self, e):   
        if self.pathMaker.key == 'del':  
            self.edits.deletePathItem(self.idx)
        elif self.pathMaker.key == 'opt': 
            self.edits.insertPathItem(self) 
        if self.pathMaker.key in ('del','opt'):   
            self.pathMaker.key = ''       
        e.accept() 
        
    def mouseMoveEvent(self, e):
        if self.pointTag: self.removePointTag()
        if self.pathMaker.pathWays.tagCount() == 0:
            if self.pathMaker.editingPts == True:
                self.dragCnt += 1
                if self.dragCnt % 5 == 0:        
                    pos = self.mapToScene(e.pos())
                    self.moveIt(pos.x(), pos.y())                                    
        e.accept()
           
    def mouseDoubleClickEvent(self, e):
        if self.idx not in self.selections:  ## selects/unselects
            self.maptos = self.mapToScene(e.pos())
            self.selections.append(self.idx)            
        else:        
            self.selections.remove(self.idx)  
        self.edits.updatePath()
        e.accept()
             
    def mouseReleaseEvent(self, e):
        if self.pathMaker.editingPts == True:        
            if self.dragCnt > 0:
                self.pathMaker.pts[self.idx] = self.mapToScene(e.pos())                
                self.edits.updatePath()  ## rewrites pointItems as well
        e.accept()
              
    def cleanUp(self):
        p = self.rect()
        self.setRect(QRectF(p.x(), p.y(), V, V))  ## reset size
        self.removePointTag()     
              
    def moveIt(self, x, y):  ## by mouse
        self.setRect(QRectF(x-V*.5, y-V*.5, V*1.5, V*1.5))              
        self.pathMaker.pts[self.idx] = QPointF(x,y) 
        self.pathMaker.addPath() 
          
    def moveThis(self, key):
        self.setOriginPt()  ## updates width and height        
        self.x = self.x + key[0]
        self.y = self.y + key[1]
        self.moveIt(self.x, self.y) 
        self.setRect(self.x-V*.5, self.y-V*.5, V,V)            
                   
    def removePointTag(self):
        if self.pointTag != '':  ## there can be only one
            self.scene.removeItem(self.pointTag)
            self.pointTag = ''
            
    def setOriginPt(self):    
        b = self.boundingRect()
        op = QPointF(b.width()/2, b.height()/2)
        self.setTransformOriginPoint(op)
 
### -------------------- dotsPathItem ----------------------
 
 
 
 