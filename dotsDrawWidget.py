import sys
import os

from PyQt5.QtCore    import Qt, QEvent, QObject, QTimer, QPointF, QPoint, pyqtSlot
from PyQt5.QtGui     import QColor, QPen
from PyQt5.QtWidgets import QFileDialog, QGraphicsPathItem, QWidget, QGraphicsItemGroup, \
                            QGraphicsEllipseItem
                            
from dotsSideGig     import TagIt
from dotsShared      import common, paths
from dotsSideWays    import SideWays

### -------------------- dotsPathMaker ---------------------
''' dotsPathMaker: contains load, save, addPath, pathChooser,
    pathlist, and path modifier functions...'''
### --------------------------------------------------------
class PointItem(QGraphicsEllipseItem):
### --------------------------------------------------------
    def __init__(self, drawing, pathMaker, parent, pt, idx, add):
        super().__init__()

        self.drawing   = drawing
        self.pathMaker = pathMaker

        self.canvas    = parent
        self.scene     = parent.scene

        self.sideWays  = pathMaker.sideWays

        self.pt = pt
        self.idx = idx
        self.setZValue(int(idx+add)) 

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
            tag = self.sideWays.makePtsTag(self.pt, self.idx, pct)
            self.pointTag = TagIt('points', tag, QColor("YELLOW"))   
            p = QPointF(0,-20)
            self.pointTag.setPos(self.pt+p)
            self.pointTag.setZValue(self.pathMaker.findTop()+5)
            self.scene.addItem(self.pointTag)
        e.accept()

    def hoverLeaveEvent(self, e):
        self.removePointTag()
        e.accept()

    def mousePressEvent(self, e):    
        if self.pathMaker.key in ('del','opt'):   
            self.removePointTag()
            if self.pathMaker.key == 'del':  
                self.drawing.delPointItem(self)
            elif self.pathMaker.key == 'opt': 
                self.drawing.insertPointItem(self)
            self.pathMaker.key = ''
        e.accept()
        
    def removePointTag(self):
        if self.pointTag:
            self.scene.removeItem(self.pointTag)
            self.pointTag = ''
     
 ### --------------------------------------------------------
class DrawingWidget(QWidget):
### --------------------------------------------------------
    def __init__(self, pathMaker, parent):  
        super().__init__()

        self.pathMaker = pathMaker  

        self.canvas    = parent
        self.scene     = parent.scene
        self.view      = parent.view
        self.dots      = parent.dots

        self.sideWays  = SideWays(self.pathMaker, self, parent) 

        self.npts = 0 ## counter used by addNewPathPts
        self.newPath = None

        self.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

### -------------- the annoyance starts here ---------------
    ''' Problem: Starting a new path drawing session, by typing 'N' in 
    pathMaker will immeadiately start drawing without having to register a 
    mousePress event if entered after displaying pointItems or if 
    started after either running an animation or pixtest. 
        The mouse events used by the pathMaker newPath functions no-longer respond -
    it doesn't stop drawing. Annoying but not fatal. I'm pretty sure the problem 
    is with the eventFilter in DrawingWidget though scene ownership may also be 
    involved. 
        The one thing animations, pixtext, and pointItems all have in common is 
    they all add and delete graphicItems to and from the scene - which should 
    be owned by dropCanvas, at least that's the idea.  Hope that helps.
        I may want to add additional pathMaker like classes/fearures later and 
    knowing how to share the canvas would be useful - unless there's an 
    another way to do this.  Many thanks in advance ..'''
### --------------------- event filter ----------------------                
    def eventFilter(self, source, e):  
        if self.canvas.pathMakerOn: 
            
            if self.pathMaker.addingNewPath:
    
                if e.type() == QEvent.MouseButtonPress:
                    self.npts = 0  
                    self.addNewPathPts(QPoint(e.pos()))
               
                elif e.type() == QEvent.MouseMove:
                    self.addNewPathPts(QPoint(e.pos()))    
               
                elif e.type() == QEvent.MouseButtonRelease:
                    self.addNewPathPts(QPoint(e.pos()))
                    self.updateNewPath()  
 
        return QWidget.eventFilter(self, source, e)
           
### --------------------- new path -------------------------
    def toggleNewPath(self):
        if self.pathMaker.addingNewPath:
            self.delNewPath()  ## changed your mind
            self.pathMaker.delete()
        elif not self.pathMaker.pathSet and not self.pathMaker.wayPtsSet:
            self.addNewPath()
            self.pathMaker.addPath()  ## add the completed path

    def addNewPathPts(self, pt): 
        if self.npts == 0:
            self.pathMaker.pts.append(pt)
        self.npts += 1
        if self.npts % 3 == 0:
            self.pathMaker.pts.append(pt)
            self.updateNewPath()

    def addNewPath(self):
        self.dots.btnPathMaker.setStyleSheet(
            "background-color: rgb(215,165,255)")
        self.pathMaker.addingNewPath = True
        self.newPath = None
        self.npts = 0
        self.pathMaker.pts = []
 
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
            self.removeNewPath() ## clean up just in case
            self.newPath = QGraphicsPathItem(self.sideWays.setPaintPath())
            self.newPath.setPen(QPen(QColor(self.pathMaker.color), 3, Qt.DashDotLine))
            self.newPath.setZValue(common['pathZ']) 
            self.scene.addItem(self.newPath)  ## only one - no group needed
            self.pathMaker.addingNewPath = True

    def removeNewPath(self):   ## keep self.pathMaker.pts  
        if self.newPath:
            self.scene.removeItem(self.newPath)
            self.pathMaker.addingNewPath = False
            self.newPath = None
            self.npts = 0
        
### -------------------- pointItems ------------------------
    def togglePointItems(self):
        if self.pointItemsSet():
            self.removePointItems()
        else:
            self.addPointItems()
        if self.pathMaker.wayPtsSet:
            QTimer.singleShot(200, self.redrawPathsAndTags)  

    def redrawPathsAndTags(self):
        self.pathMaker.removeWayPtTags()
        self.pathMaker.removePath()
        self.pathMaker.addPath()
        self.sideWays.addWayPtTags()

    def findTop(self):
        for itm in self.scene.items():
            return itm.zValue()
        return 0

    def addPointItems(self): 
        idx = 0 
        add = self.findTop() + 10 ## added to idx to set zvalue
        for pt in self.pathMaker.pts:  
            self.scene.addItem(PointItem(
                self, 
                self.pathMaker,
                self.canvas, 
                pt, idx, add))
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

    def insertPointItem(self, pointItem):
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

    def redrawPoints(self, bool=True):     ## pointItems points
        self.removePointItems()
        self.pathMaker.removeWayPtTags()
        self.pathMaker.removePath()
        self.pathMaker.addPath()
        self.sideWays.addWayPtTags()
        if bool: self.addPointItems()

### ------------------ dotsDrawWidget -----------------------


    #### save for now ########################
    # lnn = len(self.pathMaker.pts)
    # last = QPointF(0.0, 0.0)  ## save for now
    # for pt in self.pathMaker.pts:
    #     itm = PointItem(self, pt, idx, lnn)
    #     self.scene.addItem(itm)
    #     idx += 1
        # if last != QPointF(0.0, 0.0):   ## save for now
        #     print(int(self.distance(pt.x(), last.x(), 
        #         pt.y(), last.y())))
        # last = pt
    #### save for now ########################


