
from PyQt6.QtCore       import Qt, QEvent, QPointF, QPoint, pyqtSlot
from PyQt6.QtGui        import QColor, QPen, QPainterPath
from PyQt6.QtWidgets    import QWidget, QGraphicsPolygonItem, \
                                QGraphicsPathItem

from dotsAnimation      import *                          
from dotsSideGig        import MsgBox, getColorStr, distance, getCtr
from dotsShared         import common, MoveKeys, ScaleRotateKeys
from dotsSideCar        import SideCar
from dotsPathWays       import PathWays
from dotsPathEdits      import PathEdits
from dotsPathItem       import DoodleMaker
from dotsPathWorks      import PathWorks
from dotsPathWidget     import PathWidget

### -------------------- dotsPathMaker ---------------------
''' dotsPathMaker: contains load, save, addPath, pathChooser,
    pathlist, and path modifier functions...'''
''' moved all scene references from pathWays to pathMaker '''
### --------------------------------------------------------
class PathMaker(QWidget):
### --------------------------------------------------------
    def __init__(self, parent):  
        super().__init__()

        self.canvas    = parent  
        self.scene     = self.canvas.scene
        self.view      = self.canvas.view
        self.keysPanel = self.canvas.keysPanel
        self.dots      = self.canvas.dots  
         
        self.animation = Animation(self.canvas) 
        self.sideCar   = SideCar(self.canvas) 
       
        self.widget    = None  ## main pathMaker widget 
        self.seconds   = 10  ## set how long it takes mr.ball to complete a path
     
        self.pathWorks = PathWorks(self)          
        self.pathWays  = PathWays(self)  ## extends pathMaker
        self.drawing   = PathEdits(self, self.pathWays) 
               
        self.initThis()
             
        self.doFirst = {
            'D':   self.delete,
            '/':   self.changePathColor,
            'cmd': self.drawing.closeNewPath,
        }

        self.direct = {
            'F': self.pathWays.openFiles,
            'P': self.pathChooser,
            'E': self.drawing.editPoints,
            '{': self.pathWays.flipPath,
            '}': self.pathWays.flopPath,
        }

        self.editKeys = {
            'E': self.drawing.editPoints,
            'R': self.pathWays.reversePath,
            'S': self.pathWays.savePath,
            'T': self.pathWorks.pathTest,   
            '!': self.pathWays.halfPath,
            '@': self.pathWays.fullPath,
       'delPts': self.drawing.deleteSections,
        }

        self.noPathKeysSet = {
            'T': self.pathWorks.pathTest,
            'C': self.pathWays.centerPath,    
            'R': self.pathWays.reversePath,
            'S': self.pathWays.savePath,     
            'N': self.drawing.toggleNewPath,
        }

        self.WayPtsKeys = {
            '!': self.pathWays.halfPath,
            '@': self.pathWays.fullPath,
            'V': self.drawing.togglePathItems,
            '<': self.pathWays.shiftWayPtsLeft,
            '>': self.pathWays.shiftWayPtsRight,
        }

        self.view.viewport().installEventFilter(self)

### --------------------------------------------------------
    def initThis(self):
        self.pts = []  ## after adding a new path or from a file
        self.selections = []  ## needs to here, strongest reference
  
        self.color = 'DODGERBLUE'
           
        self.key = ''
        self.openPathFile = '' 
        self.tag = ''
 
        self.npts = 0  ## used by addNewPathPts
        self.last = 0
             
        self.addingNewPath = False
        self.pathSet = False
        self.pathChooserSet = False
        
        self.editingPts = False
        self.pathTestSet = False
         
        self.ball = None
        self.path = None                 
        self.poly = None
        
        self.chooser = None
        self.newPath = None 
        self.pathTestNode = None
                     
### ---------------------- key handler ---------------------
    @pyqtSlot(str)  ## there's no signal - using the decorator to speed things up
    def pathKeys(self, key):
        self.key = key
        if key in self.doFirst:
            self.doFirst[key]()  ## run the function, value
                    
        elif self.key == 'E' and self.pathWays.tagCount() > 0:
            self.pathWays.removeWayPtTags()
            if self.selections:
                self.editingPts = True
                self.drawing.updatePath()
                self.drawing.turnBlue()
            else:
                self.drawing.editPointsOff()
                self.drawing.editPoints()
            
        elif self.key == 'L' and self.editingPts == True:
            self.drawing.toggleLasso()
                                                                  
        elif self.key in self.editKeys and self.editingPts == True:
            self.editKeys[self.key]()  

        elif self.key in self.noPathKeysSet:  
            self.noPathKeysSet[self.key]()  
            if self.selections:
                self.drawing.updatePath()

        elif self.pathWays.tagCount() == 0 and self.addingNewPath == False:
            if self.key in self.direct: 
                self.direct[self.key]() 

            elif len(self.pts) > 0:  ## works with edit - no points selected
                if self.key in MoveKeys and self.selections == []:
                    self.pathWays.movePath(MoveKeys[self.key])
                elif self.key in ScaleRotateKeys:
                    self.pathWorks.scaleRotate(self.key)

        elif self.pathWays.tagCount() > 0 and self.key in self.WayPtsKeys:
            self.WayPtsKeys[self.key]() 

### --------------------- event filter ----------------------   
    def eventFilter(self, source, e):     
        if self.canvas.pathMakerOn:
    
            if self.addingNewPath:  ## draws path
                if e.type() == QEvent.Type.MouseButtonPress and \
                    e.buttons() == Qt.MouseButton.LeftButton:
                    self.drawing.npts = 0  
                    self.drawing.last = e.pos()
                    self.addNewPathPts(QPoint(e.pos()))  

                elif e.type() == QEvent.Type.MouseMove and \
                    e.buttons() == Qt.MouseButton.LeftButton:
                    self.addNewPathPts(QPoint(e.pos()))  

                elif e.type() == QEvent.Type.MouseButtonRelease:
                    self.addNewPathPts(QPoint(e.pos()))
                    self.updateNewPath() 
               
            if e.type() == QEvent.Type.MouseButtonPress and \
                e.button() == Qt.MouseButton.RightButton:
                self.addWidget()

        return QWidget.eventFilter(self, source, e)

### --------------------------------------------------------
    def initPathMaker(self):  ## from docks button
        if self.pathWays.pixCount() > 0 and not self.canvas.pathMakerOn:
            MsgBox('Clear Scene First to run PathMaker', 5)
            return
        if self.canvas.pathMakerOn:
            self.pathMakerOff()
        else:
            self.canvas.pathMakerOn = True 
            self.initThis()
            if not self.keysPanel.pathMenuSet:
                self.keysPanel.toggleMenu()
            self.turnGreen()
            self.addWidget()  ## on start up 
                    
    def addWidget(self):
        self.pathWorks.closeWidget()
        self.widget = PathWidget(self)       
        p = common['widgetXY']
        p = self.canvas.mapToGlobal(QPoint(p[0], p[1]))       
        self.widget.save = QPointF(p.x(), p.y())                          
        self.widget.setGeometry(p.x(), p.y(), \
            int(self.widget.WidgetW), int(self.widget.WidgetH))
        if self.addingNewPath:
            self.drawing.editBtn('ClosePath')
            
    def turnGreen(self):
        self.canvas.btnPathMaker.setStyleSheet(
            'background-color: LIGHTGREEN')
        if self.widget: self.widget.newBtn.setText('NewPath')  ## just to be sure
         
    def delete(self):
        self.pathWorks.stopPathTest()
        self.drawing.deleteLasso()    ## reset cursor
        self.drawing.deleteNewPath()  ## turns green if nothing else
        self.drawing.removeNewPath()
        self.drawing.editPointsOff()
        self.pathWays.removeWayPtTags()
        self.removePath()
        self.pathChooserOff() 
        self.scene.clear()
        self.initThis()
        self.canvas.bkgMaker.disableSetBkg() 
        self.dots.statusBar.showMessage(self.openPathFile)  ## it's empty, clears status bar
            
    def pathMakerOff(self):
        if self.canvas.pathMakerOn:
            self.delete()   
            self.canvas.pathMakerOn = False
            self.canvas.bkgMaker.disableSetBkg() 
            self.canvas.sideCar.clearWidgets()
            if self.keysPanel.pathMenuSet:
                self.keysPanel.toggleMenu()
            self.canvas.btnPathMaker.setStyleSheet(
                'background-color: white')
         
    def addNewPathPts(self, pt):
        if self.npts == 0:
            self.pts.append(pt)
            self.last = pt      
        self.npts += 1
        if self.npts % 5 == 0:    
            if distance(pt.x(),self.last.x(), pt.y(), self.last.y()) > 15.0:
                self.last = pt     
                self.pts.append(pt)
                self.updateNewPath()   
           
    def updateNewPath(self):
        if self.addingNewPath:  ## list of points
            self.drawing.removeNewPath()  ## clean up just in case
            ## no polyline in pyqt - use open painter path instead 
            self.newPath = QGraphicsPathItem(self.setPaintPath())
            self.newPath.setPen(QPen(QColor(self.color), 3, Qt.PenStyle.DashDotLine))
            self.newPath.setZValue(common['pathZ']) 
            self.scene.addItem(self.newPath)  ## only one - no group needed
            self.addingNewPath = True
   
    def removePoly(self):
        if self.poly != None:
            self.scene.removeItem(self.poly)
        self.poly = None
                    
### --------------------------------------------------------
    def pathChooser(self, where=''): 
        if not self.pathChooserSet and not self.addingNewPath:
            if not self.editingPts:
                self.chooser = DoodleMaker(self, where) 
                if where == 'Path Menu':  ## from animation menu
                    b = getCtr(-270,-385) 
                else:
                    b = getCtr(-270,-265)      
                self.chooser.move(int(b.x()), int(b.y()))
                self.chooser.show()
                self.pathChooserSet = True
        else:  
            self.pathChooserOff()

    def pathChooserOff(self):
        if self.chooser: self.chooser.close()
        self.chooser = None
        self.pathChooserSet = False 
        if self.openPathFile:  ## statusBar
            self.dots.statusBar.showMessage(self.openPathFile + \
                ' - Number of Points ' + str(len(self.pts)))
                    
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
            self.pathWays.removeWayPtTags()
            if self.path != None:
                self.scene.removeItem(self.path)
            self.pathSet = False
            self.path = None
      
    def redrawTagsAndPaths(self):
        self.pathWays.removeWayPtTags()
        self.removePath()
        self.addPath()
        self.pathWays.addWayPtTags()

    def changePathColor(self):
        self.color = getColorStr()
        if self.addingNewPath:
            self.updateNewPath()
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
    
### -------------------- dotsPathMaker ---------------------


