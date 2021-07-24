import sys
import os

from PyQt5.QtCore    import Qt, QEvent, QObject, QTimer, QPointF, QPoint, pyqtSlot, \
                            QPropertyAnimation
from PyQt5.QtGui     import QColor, QPen, QPixmap, QPainterPath
from PyQt5.QtWidgets import QFileDialog, QGraphicsPathItem, QGraphicsPixmapItem, \
                            QWidget, QGraphicsItemGroup 

from dotsAnimation   import Node                           
from dotsSideGig     import DoodleMaker, MsgBox, TagIt, getColorStr
from dotsShared      import common, paths
from dotsSidePath    import getOffSet

from dotsSideWays    import SideWays
from dotsDrawWidget  import DrawingWidget

ScaleRotateKeys = ('+','_','<','>',':','\"','=','-')
Tick = 3  ## points to move using arrow keys

### -------------------- dotsPathMaker ---------------------
''' dotsPathMaker: contains load, save, addPath, pathChooser,
    pathlist, and path modifier functions...'''
''' moved all scene references from sideWays to pathMaker '''
### --------------------------------------------------------
class PathMaker(QWidget):
### --------------------------------------------------------
    def __init__(self, parent):  
        super().__init__()

        self.scene    = parent.scene
        self.canvas = parent  
        self.scene  = parent.scene
        self.view   = parent.view
        self.dots   = parent.dots  ## connection to sliderpanel

        self.chooser = None  ## placeholder for popup_widget 
      
        self.initThis()
 
        self.sideWays = SideWays(self)  ## extends pathMaker
        self.drawing  = DrawingWidget(self, parent) 

        self.doFirst = {
            'D':   self.delete,
            '/':   self.changePathColor,
            'cmd': self.drawing.closeNewPath,
        }

        self.direct = {
            'F': self.sideWays.openFiles,
            'C': self.sideWays.centerPath,
            'P': self.pathChooser,
            '{': self.sideWays.flipPath,
            '}': self.sideWays.flopPath,
        }

        self.noPathKeysSet = {
            'R': self.sideWays.reversePath,
            'S': self.sideWays.savePath,
            'T': self.pathTest,
            'W': self.addWayPtTags,
            'N': self.drawing.toggleNewPath,
        }

        self.WayPtsKeys = {
            '!': self.sideWays.halfPath,
            'V': self.drawing.togglePointItems,
            '<': self.sideWays.shiftWayPtsLeft,
            '>': self.sideWays.shiftWayPtsRight,
        }

        self.moveKeys = {
            "right": (Tick, 0),
            "left":  (-Tick, 0),
            "up":    (0, -Tick),
            "down":  (0, Tick),
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
        if key in self.doFirst:
            self.doFirst[key]()  ## run the function
        elif key in self.noPathKeysSet:
            self.noPathKeysSet[key]()  
        elif not self.wayPtsSet and not self.addingNewPath:
            if key in self.direct: 
                self.direct[key]()  
            elif len(self.pts) > 0:
                if key in self.moveKeys: 
                    self.sideWays.movePath(self.moveKeys[key])
                elif key in ScaleRotateKeys:
                    self.sideWays.scaleRotate(key)
        elif self.wayPtsSet and key in self.WayPtsKeys:
            self.WayPtsKeys[key]() 

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
        self.path = QGraphicsPathItem(self.setPaintPath(True))
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
        self.addWayPtTags()

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

    def setPaintPath(self, bool=False):  ## also used by waypts
        path = QPainterPath()
        for pt in self.pts:  ## pts on the screen 
            if not path.elementCount():
                path.moveTo(QPointF(pt))
            path.lineTo(QPointF(pt)) 
        if bool: path.closeSubpath()
        return path

    def redrawPoints(self, bool=True):  ## pointItems points
        self.drawing.removePointItems()
        self.redrawPathsAndTags()
        if bool: self.drawing.addPointItems()

### --------------------- wayPtTags ------------------------
    def addWayPtTags(self):
        if self.addingNewPath:
            return
        if self.wayPtsSet:  ## toggle it off
            self.removeWayPtTags()
            self.drawing.removePointItems()
            return  ## added
        lnn = len(self.pts)
        if lnn:                ## make some tags
            self.addWayPtTagsGroup()
            inc = int(lnn/10)  ## approximate a 10% increment
            list = (x*inc for x in range(0,10))  ## get the indexes
            for idx in list:
                pt = self.pts[idx]
                pct = (idx/lnn)*100
                if pct == 0.0: idx = lnn
                self.addWayPtTag(
                    self.makePtsTag(pt, idx, pct), 
                    pt
                    )
            if self.openPathFile:  ## filename top left corner
                self.addWayPtTag(
                    self.openPathFile, 
                    QPointF(5.0,5.0)
                    )
            self.wayPtsSet = True

    def addWayPtTag(self, tag, pt):
        self.tag = TagIt('pathMaker', tag, QColor("TOMATO"))   
        self.tag.setPos(pt)
        self.tag.setZValue(common["tagZ"]+5) 
        self.tagGroup.addToGroup(self.tag)

    def addWayPtTagsGroup(self):
        self.tagGroup = QGraphicsItemGroup()
        self.tagGroup.setZValue(common["tagZ"]+5)
        self.scene.addItem(self.tagGroup)

    def removeWayPtTags(self):   
        if self.tagGroup or self.wayPtsSet:
            self.scene.removeItem(self.tagGroup) 
            self.tagGroup = None
            self.wayPtsSet = False
        
    def makePtsTag(self, pt, idx, pct):  ## used by pointItem as well
        s = "(" + str("{:2d}".format(int(pt.x())))
        s = s + ", " + str("{:2d}".format(int(pt.y()))) + ")"
        s = s + "  " + str("{0:.2f}%".format(pct)) 
        s = s + "  " + str("{0:2d}".format(idx))
        return s

### ---------------------- pathTest ------------------------
    def pathTest(self):
        if self.pts and self.pathSet:
            if not self.pathTestSet:
                self.ball = QGraphicsPixmapItem(QPixmap(paths['imagePath'] + 'ball.png'))
                node = Node(self.ball)
                self.ball.setZValue(self.findTop()+10)
       
                self.pathTestNode = QPropertyAnimation(node, b'pos')
                self.pathTestNode.setDuration(10000)  ## 10 seconds

                waypts = self.setPaintPath(True)  ## close subpath
                pt = getOffSet(self.ball)

                self.pathTestNode.setStartValue(waypts.pointAtPercent(0.0)-pt)
                for i in range(1, 99):   
                    self.pathTestNode.setKeyValueAt(
                        i/100.0, 
                        waypts.pointAtPercent(i/100.0)-pt
                        )
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



