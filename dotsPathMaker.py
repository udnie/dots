import sys
import os

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from dotsSideCar     import MsgBox
from dotsShared      import common, paths
from dotsSideWays    import SideWays, DoodleMaker

moveKeys = ("left","right","up", "down")
scaleRotateKeys = ('+','_','<','>',':','\"','=','-')
wayPtsKeys = ('<','>','R', '!')
notNewPathKeys = ('S','T','W','N')

### -------------------- dotsPathMaker ---------------------
''' dotsPathMaker: contains load, save, drawpolygon, pathchooser,
    pathlist, and path modifier functions '''
### --------------------------------------------------------
class PathMaker(QWidget):    
    def __init__(self, parent):  
        super().__init__()

        self.canvas  = parent
        self.chooser = self.canvas.chooser
        self.scene   = parent.scene
        self.view    = parent.view
        self.sliders = parent.sliders
        self.buttons = parent.buttons
   
        self.initThis()
        self.tagZ = common["pathZ"]
        self.tic = 3  ## points to move using arrow keys

        ## extends pathMaker
        self.sideWays = SideWays(self, parent.scene, parent.mapper)

        self.canvas.pathSignal[str].connect(self.pathKeys)
        self.view.viewport().installEventFilter(self)

        self.direct = {
            'F': self.openFiles,
            'C': self.centerPoly,
            'P': self.pathChooser,
            '{': self.flipPath,
            '}': self.flopPath,
        }

### --------------------------------------------------------
    def initThis(self):
        self.pts = []
        self.color = "DODGERBLUE"
        self.openPathFile = ''

        self.newPath = False
        self.polySet = False
        self.polylineSet = False
        self.wayPtsSet = False
        self.pathChooserSet = False
        self.pathTestSet = False
        
        self.ball = None
        self.polygon = None
        self.wayPath = None
                
    def eventFilter(self, source, e):  
        if self.newPath:
            if e.type() == QEvent.MouseButtonPress:      
                self.sideWays.npts = 0  
                self.sideWays.addPathPts(QPoint(e.pos()))
            elif e.type() == QEvent.MouseMove:  
                self.sideWays.addPathPts(QPoint(e.pos()))
            elif e.type() == QEvent.MouseButtonRelease: 
                self.sideWays.addPathPts(QPoint(e.pos()))
                self.sideWays.drawPolyline()  
        return QWidget.eventFilter(self, source, e)

### --------------------------------------------------------
    @pyqtSlot(str)
    def pathKeys(self, key):
        if key == 'D':  ## always
            self.delete()
            return
        elif key == '/':
            self.sideWays.changePathColor()

        ## newpath - not newpath
        if self.newPath:
            if key == 'cmd':
                self.sideWays.closePath()    
        elif key in notNewPathKeys:
            if key == 'S':
                self.savePath()
            elif key == 'T':
                self.sideWays.pathTest()
            elif key == 'W':
                self.sideWays.addWayPts()
            elif key == 'N':
                if not self.polySet and not self.wayPtsSet:
                    self.sideWays.addNewPath()
                else:
                    MsgBox("pathKeys: Can't Add with Path on Screen", 4)
                    return

        ## not waypts and not new path
        if not self.wayPtsSet and not self.newPath:
            if key in self.direct: 
                self.direct[key]()  ## OK...
            elif key in moveKeys:
                self.movePath(key)
            elif key in scaleRotateKeys: 
                self.sideWays.scaleRotate(key)

        ##  waypts only
        if self.wayPtsSet and key in wayPtsKeys:
            if key == 'R':
                self.sideWays.reverseIt()
            elif key == '!':
                self.halfPath()
            else:
                self.sideWays.shiftWayPts(key)

 ### --------------------------------------------------------
    def setPathMaker(self):
        if self.scene.items() and not self.canvas.pathMakerOn:
            MsgBox("Clear Scene First to run PathMaker")
            return
        if self.canvas.pathMakerOn:
            self.pathMakerOff()
        else:
            self.canvas.pathMakerOn = True
            self.initThis()
            if not self.sliders.pathMenuSet:
                self.sliders.toggleMenu()
            self.buttons.btnPathMaker.setStyleSheet(
                "background-color: LIGHTGREEN")

    def pathChooser(self): 
        if not self.pathChooserSet:
            self.chooser = DoodleMaker(self)  
            self.chooser.move(600,200)
            self.chooser.show()
            self.pathChooserSet = True
        else:  
            self.chooser = QWidget()
            self.pathChooserSet = False

    def getPathList(self, bool=False):  ## used by DoodleMaker
        try:                            ## also by context menu
            files = os.listdir(paths['paths'])
        except IOError:
            MsgBox("getPathList: No Path Directory Found!", 5)
            return None  
        filenames = []
        for file in files:
            if file.lower().endswith('path'): 
                if bool:    
                    file = os.path.basename(file)  ## short list
                    filenames.append(file)
                else:
                    filenames.append(paths['paths'] + file)
        if not filenames:
            MsgBox("getPathList: No Paths Found!", 5)
        return filenames
       
### --------------------------------------------------------
    def drawPolygon(self):
        self.removePolygon() 
        self.polygon = QGraphicsPolygonItem(QPolygonF(self.pts)) 
        self.polygon.setPen(QPen(QColor(self.color), 3, Qt.DashDotLine))
        self.polygon.setZValue(self.tagZ)  
        self.scene.addItem(self.polygon)
        self.polySet = True

    def delete(self):
        self.removePolygon()
        self.removeWayPts()
        self.sideWays.removePolyline()
        self.sideWays.newPathOff()
        self.removePathTest()
        self.initThis()
          
    def centerPoly(self):
        p = self.polygon.sceneBoundingRect()
        w = (common["viewW"] - p.width()) /2
        h = (common["viewH"] - p.height()) / 2
        x, y = w - p.x(), h - p.y()
        self.polygon.setPos(self.polygon.x()+x, self.polygon.y()+y)
        self.updpts(x, y)

    def flipPath(self):  
        p = self.polygon.sceneBoundingRect()
        max = p.y() + p.height()
        for i in range(0, len(self.pts)):
            pt = QPointF(self.pts[i].x(), max - self.pts[i].y() + p.y())
            self.pts[i] = pt
        self.drawPolygon()
  
    def flopPath(self): 
        p = self.polygon.sceneBoundingRect()
        max = p.x() + p.width()
        for i in range(0, len(self.pts)):
            pt = QPointF(max - self.pts[i].x() + p.x(), self.pts[i].y())
            self.pts[i] = pt
        self.drawPolygon()

    def halfPath(self):  
        tmp = []        
        for i in range(0, len(self.pts)):
            if i % 2 == 1:
                tmp.append(self.pts[i])
        self.pts = tmp
        self.removeWayPts()
        self.sideWays.updateWayPts()

    def movePath(self, key):   
        if key == 'right':
            self.polygon.setPos(
                self.polygon.x()+self.tic, self.polygon.y())
            self.updpts(self.tic, 0)
        elif key == 'left':
            self.polygon.setPos(
                self.polygon.x()-self.tic, self.polygon.y())
            self.updpts(-self.tic, 0)
        elif key == 'up':
            self.polygon.setPos(
                self.polygon.x()+0, self.polygon.y()-self.tic)
            self.updpts(0, -self.tic)
        elif key == 'down':
            self.polygon.setPos(
                self.polygon.x()+0, self.polygon.y()+self.tic)
            self.updpts(0, self.tic)
 
    def removePolygon(self):       
        if self.polySet:
            self.scene.removeItem(self.polygon)
        self.polySet = False
        self.polygon = None

    def removeWayPts(self):    
        if self.sideWays.tagGroup or self.wayPtsSet:
            self.scene.removeItem(self.sideWays.tagGroup) 
            self.sideWays.tagGroup = None
            self.wayPtsSet = False
     
    def removePathTest(self):
        if self.pathTestSet:
            self.sideWays.stopPathTest()

    def updpts(self, tx, ty):
        pt = QPoint(float(tx), float(ty))
        for p in self.pts:  ## pts on the screen 
            p += pt

    def pathMakerOff(self):
        self.delete()
        if self.sideWays.tagGroup:
            self.sideWays.tagGroup = None
        self.openPathFile = ""
        self.canvas.pathMakerOn = False
        if self.pathChooserSet:
            self.chooser = QWidget()
            self.pathChooserSet = False
        if self.sliders.pathMenuSet:
            self.sliders.toggleMenu()
        self.buttons.btnPathMaker.setStyleSheet(
            "background-color: white")
    
### --------------------------------------------------------
    def getpts(self, file, scalor=1.0, inc=0):  ## used by pathChooser
        try:
            tmp = []
            with open(file, 'r') as fp: 
                for line in fp:
                    ln = line.rstrip()  
                    ln = list(map(float, ln.split(',')))   
                    pt = QPointF(ln[0]*scalor+inc, ln[1]*scalor+inc)
                    tmp.append(pt)
            return tmp
        except IOError:
            MsgBox("getrpts: Error reading pts file")

    def openFiles(self):
        if self.pts:
            MsgBox("getrpts: Clear Scene First")
            return
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self,
            "Choose a path file to open", paths["paths"],
            "Files(*.path)")
        Q.accept()
        if file:
            self.pts = self.getpts(file)  ## read the file
            self.openPathFile = os.path.basename(file)
            self.drawPolygon()
  
    def savePath(self):
        if self.pts:
            Q = QFileDialog()
            if self.openPathFile == '':
                self.openPathFile = paths["paths"] + 'tmp.path'
            f = Q.getSaveFileName(self,
                paths["paths"],
                self.openPathFile)
            Q.accept()
            if not f[0]: 
                return
            elif not f[0].lower().endswith('.path'):
                MsgBox("savePath: Wrong file extention - use '.path'")    
            else:
                try:
                    with open(f[0], 'w') as fp:
                        for i in range(0, len(self.pts)):
                            p = self.pts[i]
                            x = str("{0:.2f}".format(p.x()))
                            y = str("{0:.2f}".format(p.y()))
                            fp.write(x + ", " + y + "\n")
                        fp.close()
                except IOError:
                    MsgBox("savePath: Error saving file")
                    return
        else:
            MsgBox("savePath: Nothing saved")
     
### -------------------- dotsPathMaker ---------------------

