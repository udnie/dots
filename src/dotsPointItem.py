
from PyQt6.QtCore    import QPointF, pyqtSlot, QPoint
from PyQt6.QtGui     import QColor
from PyQt6.QtWidgets import QGraphicsEllipseItem
   
from dotsShared      import MoveKeys                         
from dotsSideGig     import TagIt

V = 7.5     ## the diameter of a pointItem

### ------------------- dotsPointItem ----------------------
''' dotsPointItems class, used in dotsPathEdits '''
### --------------------------------------------------------
class PointItem(QGraphicsEllipseItem):
### --------------------------------------------------------
    def __init__(self, drawing, parent, pt, idx, adto):
        super().__init__()

        self.canvas = parent
        self.scene  = self.canvas.scene
    
        self.drawing   = drawing
        self.pathMaker = drawing.pathMaker
        self.sideWays  = drawing.sideWays
        
        self.selections = self.pathMaker.selections
     
        self.pt = pt
        self.idx = idx
        self.setZValue(int(idx+adto)) 

        self.type = 'pt'
        self.pointTag = ''
     
        ## -V*.5 so it's centered on the path 
        self.x = pt.x()-V*.5
        self.y = pt.y()-V*.5
        self.setRect(self.x, self.y, V, V)  
        
        if self.selections and idx in self.selections:
            self.setBrush(QColor('lime'))
        else:
            self.setBrush(QColor('white'))   
               
        self.maptos = (0.0,0.0)
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
            tag = self.pathMaker.sideWays.makePtsTag(self.pt, self.idx, pct)
            self.pointTag = TagIt('points', tag, QColor('YELLOW')) 
            self.pointTag.setPos(QPointF(self.pt)+QPointF(0.0,-20.0))
            self.pointTag.setZValue(self.drawing.findTop()+5)
            self.scene.addItem(self.pointTag)
        e.accept()

    def hoverLeaveEvent(self, e):
        self.removePointTag()  ## used twice
        e.accept()

    def mousePressEvent(self, e):     
        self.removePointTag()  ## second time, just in case 
        if self.pathMaker.key == 'del':  
            self.drawing.deletePointItem(self.idx)
        elif self.pathMaker.key == 'opt': 
            self.drawing.insertPointItem(self) 
        if self.pathMaker.key in ('del','opt'):   
            self.pathMaker.key = ''       
        e.accept() 
        
    def mouseMoveEvent(self, e):
        if self.sideWays.tagCount() == 0:
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
        self.drawing.updatePath()
        e.accept()
             
    def mouseReleaseEvent(self, e):
        if self.pathMaker.editingPts == True:        
            if self.dragCnt > 0:
                self.pathMaker.pts[self.idx] = self.mapToScene(e.pos())                
                self.drawing.updatePath()  ## rewrites pointItems as well
        e.accept()
              
    def moveIt(self, x, y):
        self.setRect(x-V*.5, y-V*.5, V,V)             
        self.pathMaker.pts[self.idx] = QPointF(x,y) 
        self.pathMaker.addPath() 
          
    def moveThis(self, key):
        self.setOriginPt()  ## updates width and height        
        self.x = self.x + key[0]
        self.y = self.y + key[1]
        self.moveIt(self.x, self.y)           
                   
    def removePointTag(self):
        if self.pointTag != '':  ## there can be only one
            self.scene.removeItem(self.pointTag)
            self.pointTag = ''
            
    def setOriginPt(self):    
        b = self.boundingRect()
        op = QPointF(b.width()/2, b.height()/2)
        self.setTransformOriginPoint(op)
        
### ------------------- dotsPointItem ----------------------
        
        
        