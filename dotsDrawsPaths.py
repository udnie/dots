
from PyQt5.QtCore    import Qt, QPointF
from PyQt5.QtGui     import QColor, QPen, QPolygonF, QTransform
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsEllipseItem
                            
from dotsSideGig     import TagIt
from dotsShared      import common

V = 6  ## the diameter of a pointItem

### ------------------- dotsDrawsPaths ---------------------
''' dotsDrawsPaths: PointItems and DrawsPaths classes '''
### --------------------------------------------------------
class PointItem(QGraphicsEllipseItem):
### --------------------------------------------------------
    def __init__(self, drawing, parent, pt, idx, adto):
        super().__init__()

        self.canvas = parent
        self.scene  = parent.scene

        self.drawing = drawing
        self.pathMaker = drawing.pathMaker
     
        self.pt = pt
        self.idx = idx
        self.setZValue(int(idx+adto)) 

        self.type = 'pt'
        self.pointTag = ''
  
        ## -V*.5 so it's centered on the path
        self.setRect(pt.x()-V*.5, pt.y()-V*.5, V, V)
        self.setBrush(QColor("white"))
        
        self.dragCnt = 0
    
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
          
        self.setAcceptHoverEvents(True)

 ### --------------------------------------------------------
    def hoverEnterEvent(self, e):
        if self.pathMaker.editingPts == False:
            if self.pathMaker.pathSet:  
                pct = (self.idx/len(self.pathMaker.pts))*100
                tag = self.pathMaker.sideWays.makePtsTag(self.pt, self.idx, pct)
                self.pointTag = TagIt('points', tag, QColor("YELLOW"))   
                self.pointTag.setPos(self.pt+QPointF(0,-20))
                self.pointTag.setZValue(self.drawing.findTop()+5)
                self.scene.addItem(self.pointTag)
        e.accept()

    def hoverLeaveEvent(self, e):
        if self.pathMaker.editingPts == False:
            self.removePointTag()  ## used twice
        e.accept()

    def mousePressEvent(self, e):     
        self.removePointTag()  ## second time, just in case
        if self.pathMaker.key == 'del':  
            self.drawing.delPointItem(self)
        elif self.pathMaker.key == 'opt': 
            self.drawing.insertPointItem(self)
        self.pathMaker.key = ''       
        e.accept()
        
    def mouseMoveEvent(self, e):
        if self.pathMaker.editingPts == True:
            self.dragCnt += 1
            if self.dragCnt % 5 == 0:        
                pos = self.mapToScene(e.pos())
                self.setRect(pos.x()-V*.5, pos.y()-V*.5, V,V)             
                self.pathMaker.pts[self.idx] = pos 
                ## redrawing the path not the points - not fast enough 
                self.pathMaker.addPath()                                      
        e.accept()
        
    def mouseReleaseEvent(self, e):
        if self.pathMaker.editingPts == True:        
            if self.dragCnt > 0:
                self.pathMaker.pts[self.idx] = self.mapToScene(e.pos())                
                self.drawing.updatePath()  ## rewrites pointItems as well
        e.accept()
         
    def removePointTag(self):
        if self.pointTag != '':  ## there is only one
            self.scene.removeItem(self.pointTag)
            self.pointTag = ''
          
### --------------------------------------------------------
class DrawsPaths:
### --------------------------------------------------------
    def __init__(self, pathMaker, sideWays, parent):  
        super().__init__()

        self.canvas    = parent
        self.scene     = parent.scene
        self.view      = parent.view
        
        self.pathMaker = pathMaker  
        self.sideWays  = sideWays
   
### --------------------- new path -------------------------
    def toggleNewPath(self):
        if self.pathMaker.addingNewPath: 
            self.delNewPath()  ## changed your mind
            self.pathMaker.delete()
        elif not self.pathMaker.pathSet and self.sideWays.tagCount() == 0:
            self.addNewPath()

    def addNewPath(self):
        self.canvas.btnPathMaker.setStyleSheet(
            "background-color: rgb(215,165,255)")
        self.pathMaker.addingNewPath = True
        self.pathMaker.newPath = None
        self.pathMaker.npts = 0
        self.pathMaker.pts = []

    def addNewPathPts(self, pt): 
        if self.pathMaker.npts == 0:
            self.pathMaker.pts.append(pt)
        self.pathMaker.npts += 1
        if self.pathMaker.npts % 3 == 0:
            self.pathMaker.pts.append(pt)
            self.updateNewPath()
 
    def closeNewPath(self):  ## applies only to adding a path
        if self.pathMaker.addingNewPath:  ## note
            self.removeNewPath()  
            self.pathMaker.turnGreen()
            self.pathMaker.addPath()  ## draws a polygon rather than painter path

    def delNewPath(self):  ## changed your mind, doesn't save pts
        if self.pathMaker.addingNewPath:
            self.removeNewPath()
            self.pathMaker.turnGreen()
            
    def updateNewPath(self):
        if self.pathMaker.addingNewPath:  ## list of points
            self.removeNewPath()  ## clean up just in case
            ## no polyline in pyqt - use open painter path instead 
            self.pathMaker.newPath = QGraphicsPathItem(self.pathMaker.setPaintPath())
            self.pathMaker.newPath.setPen(QPen(QColor(self.pathMaker.color), 3, Qt.PenStyle.DashDotLine))
            self.pathMaker.newPath.setZValue(common['pathZ']) 
            self.scene.addItem(self.pathMaker.newPath)  ## only one - no group needed
            self.pathMaker.addingNewPath = True

    def removeNewPath(self):  ## keep self.pathMaker.pts for path
        if self.pathMaker.newPath:
            self.scene.removeItem(self.pathMaker.newPath)
            self.pathMaker.addingNewPath = False
            self.pathMaker.newPath = None
            self.pathMaker.npts = 0
    
    def drawPath(self):  ## simple path graphic, not for animation
        poly = QPolygonF()  ## and not used by newPath
        for p in self.pathMaker.pts:
            poly.append(QPointF(p))
        return poly
 
    def updatePath(self):
        self.removePointItems()
        self.pathMaker.addPath() 
        self.addPointItems() 
               
### -------------------- pointItems ------------------------
    def togglePointItems(self):
        if self.pointItemsSet():
            self.removePointItems()
        else:
            self.addPointItems()

    def addPointItems(self): 
        idx = 0 
        add = self.findTop() + 10  ## added to idx to set zvalue
        for pt in self.pathMaker.pts:  
            self.scene.addItem(PointItem(self, self.canvas, pt, idx, add))
            idx += 1

    def editPoints(self):
        if self.pathMaker.editingPts == False:
            self.pathMaker.editingPts = True
            self.addPointItems()
            self.turnBlue()
        else:
            self.editPointsOff()

    def editPointsOff(self):
        self.pathMaker.editingPts = False
        self.removePointItems()
        self.pathMaker.turnGreen()
        
    def removePointItems(self):   
        for pt in self.scene.items():
            if pt.type == 'pt':
                self.scene.removeItem(pt)
                del pt

    def pointItemsSet(self):
        for itm in self.scene.items():
            if itm.type == 'pt':
                return True
        return False

    def insertPointItem(self, pointItem):  ## halfway between points
        idx, pt = pointItem.idx + 1, pointItem.pt
        if idx == len(self.pathMaker.pts): idx = 0     
        pt1 = self.pathMaker.pts[idx]
        pt1 = QPointF(pt1.x() - pt.x(), pt1.y() - pt.y())
        pt1 = pt + QPointF(pt1)*.5       
        self.pathMaker.pts.insert(idx, pt1)
        self.redrawPoints()  
        
    def delPointItem(self, pointItem):    
        self.pathMaker.pts.pop(pointItem.idx)
        del pointItem   
        self.redrawPoints()
       
    def redrawPoints(self, bool=True):  ## pointItems points
        self.removePointItems()
        if self.pathMaker.editingPts == False:
            self.pathMaker.redrawPathsAndTags()
        else:
            self.pathMaker.addPath()
        if bool: self.addPointItems()
        
    def findTop(self):
        for itm in self.scene.items():
            return itm.zValue()
        return 0
    
    def turnBlue(self):
        self.canvas.btnPathMaker.setStyleSheet(
        "background-color: rgb(118,214,255)")
        
### ------------------- dotsDrawsPaths ---------------------


