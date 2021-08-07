import sys
import os

from PyQt5.QtCore    import Qt, QEvent, QObject, QTimer, QPointF, QPoint, pyqtSlot
from PyQt5.QtGui     import QColor, QPen
from PyQt5.QtWidgets import QFileDialog, QGraphicsPathItem, QWidget, QGraphicsItemGroup, \
                            QGraphicsEllipseItem
                            
from dotsSideGig     import TagIt, distance
from dotsShared      import common, paths

### ------------------- dotsDrawsPaths ---------------------
''' dotsDrawsPaths: PointItems and DrawsPaths classes '''
### --------------------------------------------------------
class PointItem(QGraphicsEllipseItem):
### --------------------------------------------------------
    def __init__(self, drawing, parent, pt, idx, adto):
        super().__init__()

        self.canvas  = parent
        self.scene   = parent.scene

        self.drawing   = drawing
        self.pathMaker = drawing.pathMaker
     
        self.pt = pt
        self.idx = idx
        self.setZValue(int(idx+adto)) 

        self.type = 'pt'
        self.pointTag = ''

        v = 6  ## so its centered
        self.setRect(pt.x() -v*.5, pt.y() -v*.5, v, v)
        self.setBrush(QColor("white"))

        self.setFlag(QGraphicsEllipseItem.ItemIsMovable, False)
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, False)
          
        self.setAcceptHoverEvents(True)

 ### --------------------------------------------------------
    def hoverEnterEvent(self, e):
        if self.pathMaker.pathSet:  
            pct = (self.idx/len(self.pathMaker.pts))*100
            tag = self.pathMaker.makePtsTag(self.pt, self.idx, pct)
            self.pointTag = TagIt('points', tag, QColor("YELLOW"))   
            self.pointTag.setPos(self.pt+QPointF(0,-20))
            self.pointTag.setZValue(self.pathMaker.findTop()+5)
            self.scene.addItem(self.pointTag)
        e.accept()

    def hoverLeaveEvent(self, e):
        self.removePointTag()  ## used twice
        e.accept()

    def mousePressEvent(self, e):    
        if self.pathMaker.key in ('del','opt'):   
            self.removePointTag()  ## second time
            if self.pathMaker.key == 'del':  
                self.drawing.delPointItem(self)
            elif self.pathMaker.key == 'opt': 
                self.drawing.insertPointItem(self)
            self.pathMaker.key = ''
        e.accept()
        
    def removePointTag(self):
        if self.pointTag != '':
            self.scene.removeItem(self.pointTag)
            self.pointTag = ''
     
### --------------------------------------------------------
class DrawsPaths():
### --------------------------------------------------------
    def __init__(self, pathMaker, parent):  
        super().__init__()

        self.canvas    = parent
        self.scene     = parent.scene
        self.view      = parent.view
        self.dots      = parent.dots
        self.pathMaker = pathMaker  

### --------------------- new path -------------------------
    def toggleNewPath(self):
        if self.pathMaker.addingNewPath: 
            self.delNewPath()  ## changed your mind
            self.pathMaker.delete()
        elif not self.pathMaker.pathSet and not self.pathMaker.wayPtsSet:
            self.addNewPath()

    def addNewPath(self):
        self.dots.btnPathMaker.setStyleSheet(
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
            self.pathMaker.addPath()

    def delNewPath(self):  ## changed your mind, doesn't save pts
        if self.pathMaker.addingNewPath:
            self.removeNewPath()
            self.pathMaker.turnGreen()
            
    def updateNewPath(self):
        if self.pathMaker.addingNewPath:  ## list of points
            self.removeNewPath()  ## clean up just in case
            self.pathMaker.newPath = QGraphicsPathItem(self.pathMaker.setPaintPath())
            self.pathMaker.newPath.setPen(QPen(QColor(self.pathMaker.color), 3, Qt.DashDotLine))
            self.pathMaker.newPath.setZValue(common['pathZ']) 
            self.scene.addItem(self.pathMaker.newPath)  ## only one - no group needed
            self.pathMaker.addingNewPath = True

    def removeNewPath(self):  ## keep self.pathMaker.pts for path
        if self.pathMaker.newPath:
            self.scene.removeItem(self.pathMaker.newPath)
            self.pathMaker.addingNewPath = False
            self.pathMaker.newPath = None
            self.pathMaker.npts = 0
        
### -------------------- pointItems ------------------------
    def togglePointItems(self):
        if self.pointItemsSet():
            self.removePointItems()
        else:
            self.addPointItems()
        if self.pathMaker.wayPtsSet:
            QTimer.singleShot(200, self.pathMaker.redrawPathsAndTags)  

    def findTop(self):
        for itm in self.scene.items():
            return itm.zValue()
        return 0

    def addPointItems(self): 
        idx = 0 
        add = self.findTop() + 10  ## added to idx to set zvalue
        for pt in self.pathMaker.pts:  
            self.scene.addItem(PointItem(self, self.canvas, pt, idx, add))
            idx += 1

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
        self.pathMaker.redrawPoints()  

    def delPointItem(self, pointItem):
        self.pathMaker.pts.pop(pointItem.idx)
        del pointItem
        self.pathMaker.redrawPoints()

### ------------------- dotsDrawsPaths ---------------------


