import sys
import os

from PyQt5.QtCore    import Qt, QEvent, QObject, QTimer, QPointF, QPoint, pyqtSlot
from PyQt5.QtGui     import QColor, QPen
from PyQt5.QtWidgets import QFileDialog, QGraphicsPathItem, QWidget
                            
from dotsSideGig     import DoodleMaker, MsgBox, TagIt, PointItem
from dotsShared      import common, paths
from dotsSideWays    import SideWays

MoveKeys = ("left","right","up", "down")
ScaleRotateKeys = ('+','_','<','>',':','\"','=','-')
WayPtsKeys = ('<','>','R', '!', 'P')
NotPathSetKeys = ('R','S','T','W','N')
Tick = 3  ## points to move using arrow keys

### -------------------- dotsPathMaker ---------------------
''' dotsPathMaker: contains load, save, addPath, pathchooser,
    pathlist, and path modifier functions '''
### --------------------------------------------------------
class PathMaker(QWidget):

    def __init__(self, parent):  
        super().__init__()

        self.canvas = parent  
        self.scene  = parent.scene

        self.chooser = parent.chooser
        self.mapper  = parent.mapper
        self.dots    = parent.dots

        self.sliders = self.dots.sliderpanel  ## for toggling key menu
    
        self.key = ""
        self.pts = []
        self.npts = 0

        self.color = "DODGERBLUE"
        self.openPathFile = ''
        self.pointTag = ""  
        self.tag = ''
        
        self.sideWays = SideWays(self, self.canvas)  ## extends canvas

        self.direct = {
            'F': self.sideWays.openFiles,
            'C': self.centerPath,
            'P': self.pathChooser,
            '{': self.flipPath,
            '}': self.flopPath,
        }

        self.pathSet = False
        self.newPathSet = False
        self.pathChooserSet = False
        self.pointsSet = False 
      
        self.ball = None
        self.path = None                 
        self.newPath = None
        
### --------------------------------------------------------
    def initThis(self):
        self.pts = []
        self.npts = 0
        self.key = ""
        self.color = "DODGERBLUE"
        self.openPathFile = ''
        self.pointTag = ""  
        self.tag = ''
 
        self.pathSet = False
        self.newPathSet = False
        self.pathChooserSet = False
        self.pointsSet = False 
       
        self.ball = None
        self.path = None                 
        self.newPath = None
 
    def delete(self):
        self.sideWays.stopPathTest()
        self.removePath()
        self.sideWays.removeWayPtTags()
        self.removeNewPath()
        self.sideWays.newPathOff()
        self.removePoints()
        self.pathChooserOff() 
        self.initThis()
   
### --------------------------------------------------------
    @pyqtSlot(str)
    def pathKeys(self, key):
        self.key = key
        if self.key == 'D':  ## always
            self.delete()
        elif self.key == '/':
            self.changePathColor()
        elif self.newPathSet and self.key == 'cmd':  ## note
            self.sideWays.closeNewPath()   

        if key in NotPathSetKeys:
            if self.key == 'R':
                self.sideWays.reversePath()
            elif self.key == 'S':
                self.sideWays.savePath()
            elif self.key == 'T':
                self.sideWays.pathTest()
            elif self.key == 'W':
                self.sideWays.addWayPtTags()
            elif self.key == 'N': 
                if not self.pathSet and not self.sideWays.wayPtsSet:
                    self.delete()
                    self.sideWays.setNewPath()
                else:
                    self.delete()
               
        ## not waypts and not new path
        if not self.sideWays.wayPtsSet and not self.newPathSet:
            if key in self.direct: 
                self.direct[key]()  ## OK..
            elif key in MoveKeys:
                self.movePath(key)
            elif key in ScaleRotateKeys: 
                self.sideWays.scaleRotate(key)

        ##  waypts only
        if self.sideWays.wayPtsSet and key in WayPtsKeys:
            if self.key == '!':
                self.sideWays.halfPath()
            elif self.key == 'P':
                self.togglePoints()
            elif self.key in ('<', '>'):
                self.sideWays.shiftWayPts(key)

    ## pathMaker mouse events for drawing a path
    # def eventFilter(self, source, e):  
    #     if self.canvas.pathMakerOn and self.newPathSet:
    #         if e.type() == QEvent.MouseButtonPress:
    #             self.npts = 0  
    #             self.addNewPts(QPoint(e.pos()))
    #         elif e.type() == QEvent.MouseMove:
    #             self.addNewPts(QPoint(e.pos()))      
    #         elif e.type() == QEvent.MouseButtonRelease:
    #             self.addNewPts(QPoint(e.pos()))
    #             self.addNewPath()    
    #         return False

### --------------------------------------------------------
    def initPathMaker(self):  ## from docks button
        if self.canvas.scene.items() and not self.canvas.pathMakerOn:
            MsgBox("Clear Scene First to run PathMaker")
            return
        if self.canvas.pathMakerOn:
            self.pathMakerOff()
        else:
            self.canvas.pathMakerOn = True
            self.initThis()
            if not self.sliders.pathMenuSet:
                self.sliders.toggleMenu()
            self.dots.btnPathMaker.setStyleSheet(
                "background-color: LIGHTGREEN")
            # QTimer.singleShot(200, self.pathChooser)  ## optional

    def pathMakerOff(self):
        self.delete()   
        self.canvas.pathMakerOn = False
        if self.sliders.pathMenuSet:
            self.sliders.toggleMenu()
        self.dots.btnPathMaker.setStyleSheet(
            "background-color: white")

    def pathChooser(self): 
        if not self.pathChooserSet and not self.newPathSet:
            self.chooser = DoodleMaker(self)  
            self.chooser.move(600,200)
            self.chooser.show()
            self.pathChooserSet = True
        else:  
            self.pathChooserOff()

    def pathChooserOff(self):
        self.chooser = None
        self.pathChooserSet = False

### --------------------------------------------------------
    def addPath(self):
        self.removePath() 
        self.path = QGraphicsPathItem(self.sideWays.setPaintPath(True))
        self.path.setPen(QPen(QColor(self.color), 3, Qt.DashDotLine))
        self.path.setZValue(common['pathZ']) 
        self.scene.addItem(self.path)
        self.pathSet = True

    def centerPath(self):
        if self.pathSet:
            p = self.path.sceneBoundingRect()
            w = (common["ViewW"] - p.width()) /2
            h = (common["ViewH"] - p.height()) / 2
            x, y = w - p.x(), h - p.y()
            self.path.setPos(self.path.x()+x, self.path.y()+y)
            self.updPts(x, y)

    def flipPath(self):  
        p = self.path.sceneBoundingRect()
        max = p.y() + p.height()
        for i in range(0, len(self.pts)):
            self.pts[i] = QPointF(self.pts[i].x(), max - self.pts[i].y() + p.y())
        self.addPath()
  
    def flopPath(self): 
        p = self.path.sceneBoundingRect()
        max = p.x() + p.width()
        for i in range(0, len(self.pts)):
            self.pts[i] = QPointF(max - self.pts[i].x() + p.x(), self.pts[i].y())
        self.addPath()

    def movePath(self, key):   
        if key == 'right':
            self.path.setPos(
                self.path.x()+Tick, self.path.y())
            self.updPts(Tick, 0)
        elif key == 'left':
            self.path.setPos(
                self.path.x()-Tick, self.path.y())
            self.updPts(-Tick, 0)
        elif key == 'up':
            self.path.setPos(
                self.path.x()+0, self.path.y()-Tick)
            self.updPts(0, -Tick)
        elif key == 'down':
            self.path.setPos(
                self.path.x()+0, self.path.y()+Tick)
            self.updPts(0, Tick)
 
    def removePath(self):       
        if  self.path:
            self.scene.removeItem(self.path)
        self.pathSet = False
        self.path = None

    def updPts(self, tx, ty):    ## used by movePath
        pt = QPoint(float(tx), float(ty))
        for p in self.pts:  ## pts on the screen 
            p += pt         ## increment by this

    def changePathColor(self):
        self.color = self.mapper.getColorStr()
        if self.newPathSet:
            self.addNewPath()
        else:
            self.addPath()

### -------------------------------------------------------
    def addNewPts(self, pt):  
        if self.npts == 0:
            self.pts.append(pt)
        self.npts += 1
        if self.npts % 3 == 0:
            self.pts.append(pt)
            self.addNewPath()

    def addNewPath(self):
        if self.pts:  ## list of points
            self.removeNewPath() ## clean up just in case
            self.newPath = QGraphicsPathItem(self.sideWays.setPaintPath())
            self.newPath.setPen(QPen(QColor(self.color), 3, Qt.DashDotLine))
            self.newPath.setZValue(common['pathZ']) 
            self.scene.addItem(self.newPath)  ## only one - no group needed
            self.newPathSet = True

    def removeNewPath(self):    
        if self.newPath:
            self.scene.removeItem(self.newPath)
        self.newPathSet = False
        self.newPath = None
    
### --------------------- pointItems -----------------------
    def addPoints(self): 
        idx = 0
        for pt in self.pts:   ## all 'pt' points
            self.scene.addItem(PointItem(self, pt, idx))
            idx += 1
        self.pointsSet = True

    def removePoints(self):   ## all 'pt' points including tag
        for pt in self.canvas.scene.items():
            if pt.type == 'pt':
                self.scene.removeItem(pt)
        self.pointsSet = False 

    def togglePoints(self):  ## all 'pt' pointItems
        if self.pts:
            if self.pointsSet:  
                self.removePoints()
                return
            else:
                self.addPoints()

    def addPointItem(self, pointItem):
        idx, pt = pointItem.idx + 1, pointItem.pt
        if idx == len(self.pts): idx = 0     
        pt1 = self.pts[idx]
        pt1 = QPointF(pt1.x() - pt.x(), pt1.y() - pt.y())
        pt1 = pt + QPointF(pt1)*.5       
        self.pts.insert(idx, pt1)
        self.redrawPoints()  

    def delPointItem(self, pointItem):
        self.pts.pop(pointItem.idx)
        self.redrawPoints()

    def redrawPoints(self, bool=True):     ## pointItems points
        self.removePoints()
        self.sideWays.removeWayPtTags()
        self.removePath()
        self.addPath()
        self.sideWays.addWayPtTags()
        if bool: self.addPoints()

    def addPointTag(self, pnt):  ## single tag
        pct = (pnt.idx/len(self.pts))*100
        tag = self.sideWays.makePtsTag(pnt.pt, pnt.idx, pct)
        self.pointTag = TagIt('points', tag, QColor("YELLOW"))   
        p = QPointF(0,-20)
        self.pointTag.setPos(pnt.pt+p)
        self.pointTag.setZValue(len(self.pts)*.5)
        self.scene.addItem(self.pointTag)

    def removePointTag(self):  ## single tag
        if self.pointTag:
            self.scene.removeItem(self.pointTag)
            self.pointTag = ''
          
### -------------------- dotsPathMaker ---------------------

