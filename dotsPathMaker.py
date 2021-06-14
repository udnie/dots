import sys
import os

from PyQt5.QtCore    import Qt, QEvent, QObject, QTimer, QPointF, pyqtSlot
from PyQt5.QtGui     import QColor, QPen
from PyQt5.QtWidgets import QFileDialog, QGraphicsPathItem, QWidget, QGraphicsItemGroup
                            
from dotsSideGig     import DoodleMaker, MsgBox, TagIt, PointItem
from dotsShared      import common, paths
from dotsSideWays    import SideWays

MoveKeys = ("left","right","up", "down")
ScaleRotateKeys = ('+','_','<','>',':','\"','=','-')
WayPtsKeys = ('<','>','R','!','V')
NotPathSetKeys = ('R','S','T','W','N')

### -------------------- dotsPathMaker ---------------------
''' dotsPathMaker: contains load, save, addPath, pathChooser,
    pathlist, and path modifier functions...'''
''' moved all scene references from sideWays to pathMaker '''
### --------------------------------------------------------
class PathMaker(QWidget):

    def __init__(self, parent):  
        super().__init__()

        self.canvas  = parent  

        self.scene   = parent.scene
        self.chooser = parent.chooser
        self.dots    = parent.dots

        self.initThis()

        self.sliders  = self.dots.sliderpanel  ## for toggling key menu       
        self.sideWays = SideWays(self)  ## extends pathMaker
    
        self.direct = {
            'F': self.sideWays.openFiles,
            'C': self.sideWays.centerPath,
            'P': self.pathChooser,
            '{': self.sideWays.flipPath,
            '}': self.sideWays.flopPath,
        }

### --------------------------------------------------------
    def initThis(self):
        self.pts = []
        self.npts = 0 ## counter used by addNewPathPts
        self.key = ""

        self.color = "DODGERBLUE"
        self.openPathFile = ''
        self.pointTag = ""  
        self.tag = ''
 
        self.pathSet = False
        self.newPathSet = False
        self.pathChooserSet = False
       
        self.ball = None
        self.path = None                 
        self.newPath = None

        self.pathBall = None
        self.tagGroup = None        

        self.pathTestSet = False
        self.wayPtsSet = False  ## appear as tags
   
### ---------------------- key handler ---------------------
    @pyqtSlot(str)
    def pathKeys(self, key):
        self.key = key
        if self.key == 'D':  ## always
            self.delete()
        elif self.key == '/':
            self.sideWays.changePathColor()
        elif self.newPathSet and self.key == 'cmd':  ## note
            self.closeNewPath()   
        elif key in NotPathSetKeys:
            if self.key == 'R':
                self.sideWays.reversePath()
            elif self.key == 'S':
                self.sideWays.savePath()
            elif self.key == 'T':
                self.sideWays.pathTest()
            elif self.key == 'W':
                self.sideWays.addWayPtTags()
            elif self.key == 'N':
                if not self.pathSet and not self.wayPtsSet:
                    if not self.newPathSet:
                        self.addNewPath()
                    else:
                        self.newPathOff()  ## changed your mind
                        self.delete()
        ## not waypts and not new path
        elif not self.wayPtsSet and not self.newPathSet:
            if key in self.direct: 
                self.direct[key]()  ## OK..
            elif key in MoveKeys:
                self.sideWays.movePath(key)
            elif key in ScaleRotateKeys: 
                self.sideWays.scaleRotate(key)
        ##  waypts only
        elif self.wayPtsSet and key in WayPtsKeys:
            if self.key == '!':
                self.sideWays.halfPath()
            elif self.key == 'V':
                self.togglePointItems()  
            elif self.key in ('<','>'):
                self.sideWays.shiftWayPts(key)

### ----------------- event filter..not used  ---------------
    ''' PathMaker mouse events for drawing a path.
        Saving this for now - possible use in a multiple 
        window app. '''
    # def eventFilter(self, source, e):  
    #     if self.canvas.pathMakerOn and self.newPathSet:
    #         if e.type() == QEvent.MouseButtonPress:
    #             self.npts = 0  
    #             self.addNewPts(QPoint(e.pos()))
    #         elif e.type() == QEvent.MouseMove:
    #             self.addNewPts(QPoint(e.pos()))      
    #         elif e.type() == QEvent.MouseButtonRelease:
    #             self.addNewPts(QPoint(e.pos()))
    #             self.updateNewPath()    
    # #         return False
    #     return QWidget.eventFilter(self, source, e)

### --------------------------------------------------------
    def initPathMaker(self):  ## from docks button
        if self.scene.items() and not self.canvas.pathMakerOn:
            MsgBox("Clear Scene First to run PathMaker")
            return
        elif self.canvas.pathMakerOn:
            self.pathMakerOff()
        else:
            self.canvas.pathMakerOn = True
            self.initThis()
            if not self.sliders.pathMenuSet:
                self.sliders.toggleMenu()
            self.turnGreen()
            # QTimer.singleShot(200, self.pathChooser)  ## optional

    def turnGreen(self):
        self.dots.btnPathMaker.setStyleSheet(
                "background-color: LIGHTGREEN")

    def delete(self):
        self.stopPathTest()
        self.removePointItems()
        self.removePath()
        self.removeWayPtTags()
        self.removeNewPath()
        self.pathChooserOff() 
        self.initThis()
      
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

### -------------------- new path -------------------------
    def addNewPathPts(self, pt):  ## called by dropCanvas eventfilter
        if self.npts == 0:
            self.pts.append(pt)
        self.npts += 1
        if self.npts % 3 == 0:
            self.pts.append(pt)
            self.updateNewPath()

    def addNewPath(self):
        self.dots.btnPathMaker.setStyleSheet(
            "background-color: rgb(215,165,255)")
        self.initNewPath(True)
 
    def initNewPath(self, bool):
        self.newPath = None
        self.newPathSet = bool
        self.pts = []
        self.npts = 0

    def closeNewPath(self):  ## applies only to newPath
        self.removeNewPath()  
        self.addPath()  ## add the completed path
        self.turnGreen()

    def newPathOff(self):
        if self.newPathSet:
            if self.newPath:
                self.scene.removeItem(self.newPath)
            self.initNewPath(False)
            self.turnGreen()
            
    def updateNewPath(self):
        if self.pts:  ## list of points
            self.removeNewPath() ## clean up just in case
            self.newPath = QGraphicsPathItem(self.sideWays.setPaintPath())
            self.newPath.setPen(QPen(QColor(self.color), 3, Qt.DashDotLine))
            self.newPath.setZValue(common['pathZ']) 
            self.scene.addItem(self.newPath)  ## only one - no group needed
            self.newPathSet = True

    def removeNewPath(self):   ## keep self.pts  
        if self.newPath:
            self.scene.removeItem(self.newPath)
            self.newPathSet = False
            self.newPath = None
           
### -------------------- path stuff ------------------------
    def addPath(self):
        self.removePath() 
        self.path = QGraphicsPathItem(self.sideWays.setPaintPath(True))
        self.path.setPen(QPen(QColor(self.color), 3, Qt.DashDotLine))
        self.path.setZValue(common['pathZ']) 
        self.scene.addItem(self.path)
        self.pathSet = True
 
    def removePath(self):       
        if  self.path:
            self.scene.removeItem(self.path)
            self.pathSet = False
            self.path = None

### --------------- pointItems and tags --------------------
    def togglePointItems(self):
        if self.pointItemsSet():
            self.removePointItems()
        else:
            self.addPointItems()
        QTimer.singleShot(200, self.redrawPathsAndTags)  

    def redrawPathsAndTags(self):
        self.removeWayPtTags()
        self.removePath()
        self.addPath()
        self.sideWays.addWayPtTags()

    def addPointItems(self): 
        idx = 0
        for pt in self.pts:  
            self.scene.addItem(PointItem(self, pt, idx))
            idx += 1

    def removePointItems(self):   
        for pt in self.scene.items():
            if pt.type == 'pt':
                self.scene.removeItem(pt)

    def pointItemsSet(self):
        for itm in self.scene.items():
            if itm.type == 'pt':
                return True
        return False

    def insertPointItem(self, pointItem):
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
        self.removePointItems()
        self.removeWayPtTags()
        self.removePath()
        self.addPath()
        self.sideWays.addWayPtTags()
        if bool: self.addPointItems()

    def addPointTag(self, pnt):  ## single tag
        pct = (pnt.idx/len(self.pts))*100
        tag = self.sideWays.makePtsTag(pnt.pt, pnt.idx, pct)
        self.pointTag = TagIt('points', tag, QColor("YELLOW"))   
        p = QPointF(0,-20)
        self.pointTag.setPos(pnt.pt+p)
        # self.pointTag.setZValue(len(self.pts)*.5)
        self.pointTag.setZValue(common['tagZ'])
        self.scene.addItem(self.pointTag)

    def removePointTag(self):  ## single tag
        if self.pointTag:
            self.scene.removeItem(self.pointTag)
            self.pointTag = ''

    def addWayPtTagsGroup(self):
        self.tagGroup = QGraphicsItemGroup()
        self.scene.addItem(self.tagGroup)
        self.tagGroup.setZValue(common["tagZ"]+5)

    def addWayPtTag(self, tag, pt):
        self.tag = TagIt('pathMaker', tag, QColor("TOMATO"))   
        self.tag.setPos(pt)
        self.tag.setZValue(common["tagZ"]+5) 
        self.tagGroup.addToGroup(self.tag)

    def removeWayPtTags(self):   
        if self.tagGroup or self.wayPtsSet:
            self.scene.removeItem(self.tagGroup) 
            self.tagGroup = None
            self.wayPtsSet = False

    def startPathTest(self):
        self.scene.addItem(self.ball)
        self.pathBall.start()
        self.pathTestSet = True

    def stopPathTest(self): 
        if self.pathTestSet:  
            self.pathBall.stop()
            self.scene.removeItem(self.ball)
            self.pathBall = None
            self.pathTestSet = False

### -------------------- dotsPathMaker ---------------------

