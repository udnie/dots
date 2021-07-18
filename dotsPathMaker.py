import sys
import os

from PyQt5.QtCore    import Qt, QEvent, QObject, QTimer, QPointF, QPoint, pyqtSlot, \
                            QPropertyAnimation
from PyQt5.QtGui     import QColor, QPen, QPixmap
from PyQt5.QtWidgets import QFileDialog, QGraphicsPathItem, QGraphicsPixmapItem, \
                            QWidget, QGraphicsItemGroup 

from dotsAnimation   import Node                           
from dotsSideGig     import DoodleMaker, MsgBox, TagIt, getColorStr
from dotsShared      import common, paths
from dotsSidePath    import getOffSet

from dotsSideWays    import SideWays
from dotsDrawWidget  import DrawingWidget

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
### --------------------------------------------------------
    def __init__(self, parent):  
        super().__init__()

        self.canvas   = parent  
        self.scene    = parent.scene
        self.view     = parent.view
        self.dots     = parent.dots
   
        self.chooser  = None ## placeholder for popup_widget 
      
        self.initThis()

        self.drawing  = DrawingWidget(self, parent)  
        self.sideWays = SideWays(self, self.drawing, parent)  ## extends pathMaker

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
        self.key = ""

        self.color = "DODGERBLUE"
        self.openPathFile = '' 
        self.tag = ''
 
        self.pathSet = False
        self.addingNewPath = False
        self.pathChooserSet = False
       
        self.ball = None
        self.path = None                 
 
        self.pathTestNode = None
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
            self.changePathColor()
        elif self.addingNewPath and self.key == 'cmd':  ## note
            self.drawing.closeNewPath()   
        elif key in NotPathSetKeys:
            if self.key == 'R':
                self.sideWays.reversePath()
            elif self.key == 'S':
                self.sideWays.savePath()
            elif self.key == 'T':
                self.pathTest()
            elif self.key == 'W':
                self.sideWays.addWayPtTags()
            elif self.key == 'N':
                if self.addingNewPath:
                    self.drawing.delNewPath()  ## changed your mind
                    self.delete()
                elif not self.pathSet and not self.wayPtsSet:
                    self.drawing.addNewPath()
                    self.addPath()  ## add the completed path
        ## not waypts and not new path
        elif not self.wayPtsSet and not self.addingNewPath:
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
                self.drawing.togglePointItems()  
            elif self.key in ('<','>'):
                self.sideWays.shiftWayPts(key)

### --------------------------------------------------------
    def initPathMaker(self):  ## from docks button
        if self.scene.items() and not self.canvas.pathMakerOn:
            MsgBox("Clear Scene First to run PathMaker")
            return
        if self.canvas.pathMakerOn:
            self.pathMakerOff()
        else:
            self.canvas.clear()
            self.canvas.pathMakerOn = True 
            self.initThis()
            if not self.dots.sliderpanel.pathMenuSet:
                self.dots.sliderpanel.toggleMenu()
            self.turnGreen()
            # QTimer.singleShot(200, self.pathChooser)  ## optional

    def turnGreen(self):
        self.dots.btnPathMaker.setStyleSheet(
                "background-color: LIGHTGREEN")

    def delete(self):
        self.drawing.delNewPath()  ## turns green if nothing else
        self.stopPathTest()
        self.drawing.removePointItems()
        self.removeWayPtTags()
        self.removePath()
        self.drawing.removeNewPath()
        self.pathChooserOff() 
        self.scene.clear()
        self.initThis()
      
    def pathMakerOff(self):
        self.delete()   
        self.canvas.pathMakerOn = False
        if self.dots.sliderpanel.pathMenuSet:
            self.dots.sliderpanel.toggleMenu()
        self.dots.btnPathMaker.setStyleSheet(
            "background-color: white")

    def pathChooser(self): 
        if not self.pathChooserSet and not self.addingNewPath:
            self.chooser = DoodleMaker(self)  
            self.chooser.move(600,200)
            self.chooser.show()
            self.pathChooserSet = True
        else:  
            self.pathChooserOff()

    def pathChooserOff(self):
        self.chooser = None
        self.pathChooserSet = False
          
### -------------------- path stuff ------------------------
    def addPath(self):
        self.removePath() 
        self.path = QGraphicsPathItem(self.sideWays.setPaintPath(True))
        self.path.setPen(QPen(QColor(self.color), 3, Qt.DashDotLine))
        self.path.setZValue(common['pathZ']) 
        self.scene.addItem(self.path)
        self.pathSet = True
 
    def removePath(self):       
        if self.pathSet:
            self.scene.removeItem(self.path)
            self.pathSet = False
            self.path = None
    
    def redrawPathsAndTags(self):
        self.removeWayPtTags()
        self.removePath()
        self.addPath()
        self.sideWays.addWayPtTags()

    def findTop(self):
        for itm in self.scene.items():
            return itm.zValue()
        return 0

    def changePathColor(self):
        self.color = getColorStr()
        if self.addingNewPath:
            self.drawing.updateNewPath()
        else:
            self.addPath()

### --------------------- wayPtTags ------------------------
    def addWayPtTag(self, tag, pt):
        self.tag = TagIt('pathMaker', tag, QColor("TOMATO"))   
        self.tag.setPos(pt)
        self.tag.setZValue(common["tagZ"]+5) 
        self.tagGroup.addToGroup(self.tag)

    def addWayPtTagsGroup(self):
        self.tagGroup = QGraphicsItemGroup()
        self.scene.addItem(self.tagGroup)
        self.tagGroup.setZValue(common["tagZ"]+5)

    def removeWayPtTags(self):   
        if self.tagGroup or self.wayPtsSet:
            self.scene.removeItem(self.tagGroup) 
            self.tagGroup = None
            self.wayPtsSet = False
        
### ---------------------- pathTest ------------------------
    def pathTest(self):
        if self.pts and self.pathSet:
            if not self.pathTestSet:
                self.ball = QGraphicsPixmapItem(QPixmap(paths['imagePath'] + 'ball.png'))
                node = Node(self.ball)
                self.ball.setZValue(50)

                self.pathTestNode = QPropertyAnimation(node, b'pos')
                self.pathTestNode.setDuration(10000)  ## 10 seconds

                waypts = self.sideWays.setPaintPath(True) ## close subpath
                pt = getOffSet(self.ball)

                self.pathTestNode.setStartValue(waypts.pointAtPercent(0.0)-pt)
                for i in range(1, 99):   
                    self.pathTestNode.setKeyValueAt(i/100.0, waypts.pointAtPercent(i/100.0)-pt)
                self.pathTestNode.setEndValue(waypts.pointAtPercent(1.0)-pt)  
                self.pathTestNode.setLoopCount(-1) 
                self.startPathTest()
            else:
                self.stopPathTest()

    def startPathTest(self):
        self.scene.addItem(self.ball)
        self.pathTestNode.start()
        self.pathTestSet = True

    def stopPathTest(self): 
        if self.pathTestSet:  
            self.pathTestNode.stop()
            self.scene.removeItem(self.ball)
            self.ball = None
            self.pathTestNode = None
            self.pathTestSet = False

### -------------------- dotsPathMaker ---------------------



