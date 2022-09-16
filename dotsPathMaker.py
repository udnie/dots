
from PyQt6.QtCore       import Qt, QEvent, QPointF, QPoint, pyqtSlot, QPropertyAnimation
from PyQt6.QtGui        import QColor, QPen, QPixmap, QPainterPath
from PyQt6.QtWidgets    import QGraphicsPixmapItem, QWidget, QGraphicsPolygonItem 

from dotsAnimation      import Node                           
from dotsSideGig        import DoodleMaker, MsgBox, getColorStr
from dotsShared         import common, paths, MoveKeys, ScaleRotateKeys

from dotsSideWays       import SideWays
from dotsDrawsPaths     import DrawsPaths

### -------------------- dotsPathMaker ---------------------
''' dotsPathMaker: contains load, save, addPath, pathChooser,
    pathlist, and path modifier functions...'''
''' moved all scene references from sideWays to pathMaker '''
### --------------------------------------------------------
class PathMaker(QWidget):
### --------------------------------------------------------
    def __init__(self, parent):  
        super().__init__()

        self.canvas = parent  
        self.scene  = parent.scene
        self.view   = parent.view
        self.slider = parent.slider
        self.dots   = parent.dots

        self.chooser = None  ## placeholder for doodles_popup_widget 
       
        self.initThis()
           
        self.sideWays = SideWays(self)  ## extends pathMaker
        self.drawing  = DrawsPaths(self, self.sideWays, parent) 
 
        self.doFirst = {
            'D':   self.delete,
            '/':   self.changePathColor,
            'cmd': self.drawing.closeNewPath,
        }

        self.direct = {
            'F': self.sideWays.openFiles,
            'P': self.pathChooser,
            'E': self.drawing.editPoints,
            '{': self.sideWays.flipPath,
            '}': self.sideWays.flopPath,
        }

        self.editKeys = {
            'E': self.drawing.editPoints,
            'R': self.sideWays.reversePath,
            'S': self.sideWays.savePath,
            'T': self.pathTest,   
            '!': self.sideWays.halfPath,
            '@': self.sideWays.fullPath,
       'delPts': self.drawing.deleteSections,
        }

        self.noPathKeysSet = {
            'T': self.pathTest,
            'C': self.sideWays.centerPath,    
            'R': self.sideWays.reversePath,
            'S': self.sideWays.savePath,
            'W': self.sideWays.addWayPtTags,        
            'N': self.drawing.toggleNewPath,
        }

        self.WayPtsKeys = {
            '!': self.sideWays.halfPath,
            '@': self.sideWays.fullPath,
            'V': self.drawing.togglePointItems,
            '<': self.sideWays.shiftWayPtsLeft,
            '>': self.sideWays.shiftWayPtsRight,
        }

        # self.setMouseTracking(True)  ## must carry down from canvas
        self.view.viewport().installEventFilter(self)

### --------------------------------------------------------
    def initThis(self):
        self.pts = []  ## after adding a new path or from a file
        self.selections = []  ## needs to here, strongest reference
  
        self.color = "DODGERBLUE"
        
        self.key = ""
        self.openPathFile = '' 
        self.tag = ''
 
        self.npts = 0  ## used by addNewPathPts
        self.last = 0
        
        self.newPath = None
        self.addingNewPath = False

        self.pathSet = False
        self.pathChooserSet = False
       
        self.ball = None
        self.path = None                 
        self.pathTestNode = None
          
        self.editingPts = False
        self.pathTestSet = False
        
### ---------------------- key handler ---------------------
    @pyqtSlot(str)
    def pathKeys(self, key):
        self.key = key
        if key in self.doFirst:
            self.doFirst[key]()  ## run the function, value

        elif self.key == 'K':
            self.slider.toggleMenu()  ## keys
                    
        elif self.key == 'E' and self.sideWays.tagCount() > 0:
            self.sideWays.removeWayPtTags()
            if self.selections:
                self.editingPts = True
                self.drawing.updatePath()
                self.drawing.turnBlue()
            else:
                self.drawing.editPointsOff()
                self.drawing.editPoints()
            
        elif self.key == 'W' and self.editingPts == True:
            self.sideWays.addWayPtTags()

        elif self.key == 'L' and self.editingPts == True:
            self.drawing.toggleLasso()
                                                                  
        elif self.key in self.editKeys and self.editingPts == True:
            self.editKeys[self.key]()  

        elif self.key in self.noPathKeysSet:  
            self.noPathKeysSet[self.key]()  
            if self.selections:
                self.drawing.updatePath()

        elif self.sideWays.tagCount() == 0 and self.addingNewPath == False:
            if self.key in self.direct: 
                self.direct[self.key]() 

            elif len(self.pts) > 0:  ## works with edit - no points selected
                if self.key in MoveKeys and self.selections == []:
                    self.sideWays.movePath(MoveKeys[self.key])
                elif self.key in ScaleRotateKeys:
                    self.sideWays.scaleRotate(self.key)

        elif self.sideWays.tagCount() > 0 and self.key in self.WayPtsKeys:
            self.WayPtsKeys[self.key]() 

### --------------------- event filter ----------------------   
    def eventFilter(self, source, e):     
        if self.canvas.pathMakerOn:
    
            if self.addingNewPath:
                if e.type() == QEvent.Type.MouseButtonPress and \
                    e.buttons() == Qt.MouseButton.LeftButton:
                    self.drawing.npts = 0  
                    self.drawing.last = e.pos()
                    self.drawing.addNewPathPts(QPoint(e.pos()))  

                elif e.type() == QEvent.Type.MouseMove and \
                    e.buttons() == Qt.MouseButton.LeftButton:
                    self.drawing.addNewPathPts(QPoint(e.pos()))  

                elif e.type() == QEvent.Type.MouseButtonRelease:
                    self.drawing.addNewPathPts(QPoint(e.pos()))
                    self.drawing.updateNewPath() 
               
            if e.type() == QEvent.Type.MouseButtonPress and \
                e.button() == Qt.MouseButton.RightButton:
                self.pathChooser()

        return QWidget.eventFilter(self, source, e)

### --------------------------------------------------------
    def initPathMaker(self):  ## from docks button
        if self.sideWays.pixCount() > 0 and not self.canvas.pathMakerOn:
            MsgBox("Clear Scene First to run PathMaker")
            return
        if self.canvas.pathMakerOn:
            self.pathMakerOff()
        else:
            # self.canvas.clear()  ## leave it messy, backgrounds and flats
            self.canvas.pathMakerOn = True 
            self.initThis()
            if not self.slider.pathMenuSet:
                self.slider.toggleMenu()
            self.turnGreen()
            # QTimer.singleShot(200, self.pathChooser)  ## optional

    def turnGreen(self):
        self.canvas.btnPathMaker.setStyleSheet(
            "background-color: LIGHTGREEN")
         
    def delete(self):
        self.stopPathTest()
        self.drawing.deleteLasso()    ## reset cursor
        self.drawing.deleteNewPath()  ## turns green if nothing else
        self.drawing.removeNewPath()
        self.drawing.editPointsOff()
        self.sideWays.removeWayPtTags()
        self.removePath()
        self.pathChooserOff() 
        self.scene.clear()
        self.initThis()
        self.dots.statusBar.showMessage(self.openPathFile)  ## it's empty, clears status bar
            
    def pathMakerOff(self):
        if self.canvas.pathMakerOn:
            self.delete()   
            self.canvas.pathMakerOn = False
            self.canvas.initBkg.disableSetBkg() 
            self.slider.enableSliders(False)
            if self.slider.pathMenuSet:
                self.slider.toggleMenu()
            self.canvas.btnPathMaker.setStyleSheet(
                "background-color: white")

    def pathChooser(self): 
        if not self.pathChooserSet and not self.addingNewPath:
            if not self.editingPts:
                self.chooser = DoodleMaker(self)  
                self.chooser.move(600,200)
                self.chooser.show()
                self.pathChooserSet = True
        else:  
            self.pathChooserOff()

    def pathChooserOff(self):
        self.chooser = None
        self.pathChooserSet = False
        if self.openPathFile:  ## filename top left corner
            self.dots.statusBar.showMessage(self.openPathFile)
        
### -------------------- path stuff ------------------------
    def addPath(self):
        self.removePath()  ## not for animation
        self.path = QGraphicsPolygonItem(self.drawing.drawPoly(self.pts))       
        self.path.setPen(QPen(QColor(self.color), 3, Qt.PenStyle.DashDotLine))
        self.path.setZValue(common['pathZ']) 
        self.scene.addItem(self.path)
        self.pathSet = True
  
    def removePath(self):       
        if self.pathSet:
            self.sideWays.removeWayPtTags()  
            self.scene.removeItem(self.path)
            self.pathSet = False
            self.path = None
      
    def redrawPathsAndTags(self):
        self.sideWays.removeWayPtTags()
        self.removePath()
        self.addPath()
        self.sideWays.addWayPtTags()

    def changePathColor(self):
        self.color = getColorStr()
        if self.addingNewPath:
            self.drawing.updateNewPath()
        else:
            self.addPath()
                                    
    def setPaintPath(self, bool=False):  ## used for animation and newPath
        path = QPainterPath()       
        for pt in self.pts:  ## pts on the screen 
            if path.elementCount() == 0:  ## first point always moveto
                path.moveTo(QPointF(pt))
            path.lineTo(QPointF(pt)) 
        if bool: path.closeSubpath()
        return path

### ---------------------- pathTest ------------------------
    def pathTest(self):
        if self.pts and self.pathSet:
            if not self.pathTestSet:
                self.ball = QGraphicsPixmapItem(QPixmap(paths['imagePath'] + \
                    'ball.png'))
                node = Node(self.ball)
                self.ball.setZValue(self.drawing.findTop()+10)
       
                self.pathTestNode = QPropertyAnimation(node, b'pos')
                self.pathTestNode.setDuration(10000)  ## 10 seconds

                path = self.setPaintPath(True)  ## close subpath, uses    
                b = self.ball.boundingRect() 
                pt = QPointF(b.width()/2, b.height()/2)
           
                self.pathTestNode.setStartValue(path.pointAtPercent(0.0)-pt)
                for i in range(1, 99):   
                    self.pathTestNode.setKeyValueAt(
                        i/100.0, 
                        path.pointAtPercent(i/100.0)-pt
                        )
                self.pathTestNode.setEndValue(path.pointAtPercent(1.0)-pt) 
                self.pathTestNode.setLoopCount(-1) 
                del path
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
            self.drawing.redrawPoints(self.drawing.pointItemsSet())

### -------------------- dotsPathMaker ---------------------



