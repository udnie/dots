
import os.path

from PyQt6.QtCore       import Qt, QEvent, QPoint, pyqtSlot
from PyQt6.QtGui        import QColor, QPen
from PyQt6.QtWidgets    import QWidget, QGraphicsPolygonItem, QGraphicsPathItem
               
from dotsSideGig        import MsgBox, distance, getCtr, getPathList
from dotsShared         import common, MoveKeys

from dotsPathWays       import PathWays
from dotsPathEdits      import PathEdits
from dotsPathWorks      import PathWorks

from dotsDoodleMaker    import DoodleMaker

ScaleRotateKeys = ('+','_','<','>',':','\"','=','-',';','\'','[',']')

### -------------------- dotsPathMaker ---------------------
''' dotsPathMaker: contains load, save, addPath, pathChooser,
    pathlist, and path modifier functions...'''
''' moved all scene references from pathWays to pathMaker '''
### --------------------------------------------------------
class PathMaker(QWidget):
### --------------------------------------------------------
    def __init__(self, parent, str=''):  
        super().__init__()

        self.canvas    = parent  
        self.scene     = self.canvas.scene
        self.view      = self.canvas.view
        self.dots      = self.canvas.dots  
         
        self.widget  = None
        self.seconds = 10  ## set how long it takes mr.ball to complete a path
     
        self.pathWorks  = PathWorks(self)             
        self.pathWays   = PathWays(self)  
        self.edits      = PathEdits(self) 
  
        self.initThis()  
               
        self.doFirst = {
            'D': self.delete,
            '/': self.pathWorks.changePathColor,
            'N': self.edits.toggleNewPath,
            'X': self.canvas.exit,
            'M': 'special case',
        }

        self.direct = {
            'P': self.pathChooser,
            'E': self.edits.editPoints,
            '{': self.pathWays.flipPath,
            '}': self.pathWays.flopPath,
        }

        self.editKeys = {
            'E': self.edits.editPoints,
            'R': self.pathWays.reversePath,
            'S': self.pathWays.savePath,
            'T': self.pathWorks.pathTest,   
            '!': self.pathWays.halfPath,
            '@': self.pathWays.fullPath,
       'delPts': self.pathWorks.deleteSelections,
        }

        self.noPathKeysSet = {
            'T': self.pathWorks.pathTest,
            'C': self.pathWays.centerPath,    
            'R': self.pathWays.reversePath,
            'S': self.pathWays.savePath,     
            'N': self.edits.toggleNewPath,
        }

        self.WayPtsKeys = {
            '!': self.pathWays.halfPath,
            '@': self.pathWays.fullPath,
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
        self.lassoOn = False
         
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
            if key == 'M':
                self.canvas.setKeys('M') 
            else:
                self.doFirst[key]()  ## run the function, value
                    
        elif self.key == 'E' and self.pathWays.tagCount() > 0:
            self.pathWays.removeWayPtTags()
            if len(self.selections) > 0:
                self.editingPts = True
                self.edits.updatePath()
                self.pathWorks.turnBlue()
            else:
                self.edits.editPointsOff()
                self.edits.editPoints()
            
        elif self.key == 'L' and self.editingPts == True:  ## turn lasso on/off
            self.edits.newLasso()if self.lassoOn == False \
                else self.edits.deleteLasso()
                                                               
        elif self.key in self.editKeys and self.editingPts == True:
            self.editKeys[self.key]()  

        elif self.key in self.noPathKeysSet:  
            self.noPathKeysSet[self.key]()  
            if len(self.selections) > 0:
                self.edits.updatePath()

        elif self.pathWays.tagCount() == 0 and self.addingNewPath == False:
            if self.key in self.direct:
                self.direct[self.key]() 

            elif len(self.pts) > 0:  ## works with edit - no points selected
                if self.key in MoveKeys and len(self.selections) == 0:
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
                    self.edits.npts = 0  
                    self.edits.last = e.pos()
                    self.addNewPathPts(QPoint(e.pos()))  

                elif e.type() == QEvent.Type.MouseMove and \
                    e.buttons() == Qt.MouseButton.LeftButton:
                    self.addNewPathPts(QPoint(e.pos()))  

                elif e.type() == QEvent.Type.MouseButtonRelease:
                    self.addNewPathPts(QPoint(e.pos()))
                    self.updateNewPath() 
               
            ## add pathWidget - right mouse click
            if e.type() == QEvent.Type.MouseButtonPress and \
                e.button() == Qt.MouseButton.RightButton:
                self.pathWorks.addWidget()

        return QWidget.eventFilter(self, source, e)

### --------------------------------------------------------
    def initPathMaker(self):  ## from docks button
        if len(self.scene.items()) > 0 and self.canvas.pathMakerOn == False:
            MsgBox('Clear Scene First to run PathMaker', 5)
            return
        if self.canvas.pathMakerOn:
            self.pathMakerOff()
        else:
            self.canvas.pathMakerOn = True 
            self.initThis()
            if not self.canvas.keysPanel.pathKeysSet:
                self.canvas.sideCar.toggleKeysMenu()
            self.pathWorks.turnGreen()
            self.pathWorks.addWidget()  ## on start up 
                                                                       
    def delete(self):
        self.pathWorks.stopPathTest()
        
        if self.canvas.animation == True:  ## turns off video as well
            self.canvas.showbiz.showtime.stop('clear') 
        elif self.canvas.video != None:  ## make sure it's stopped
            self.canvas.video.stopVideo()

        self.editingPts == False
        self.edits.deleteLasso()    ## reset cursor
        self.edits.deleteNewPath()  ## turns green if nothing else
        self.edits.removeNewPath()
        self.edits.editPointsOff()
        self.pathWays.removeWayPtTags()
        self.removePath()
        self.pathChooserOff() 
        self.scene.clear()
        self.initThis()
        if self.pathWorks.widget != None: self.pathWorks.widget.label.setText('')
        self.dots.statusBar.showMessage(self.openPathFile)  ## it's empty, clears status bar
            
    def pathMakerOff(self):
        if self.canvas.pathMakerOn:
            self.delete()   
            self.canvas.pathMakerOn = False
            self.canvas.sideCar.clearWidgets()
            if self.canvas.keysPanel.pathKeysSet:
                self.canvas.sideCar.toggleKeysMenu()
            self.canvas.btnPathMaker.setStyleSheet('background-color: white')
            self.canvas.showWorks.enablePlay()
        self.canvas.setFocus()
         
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
            self.edits.removeNewPath()  ## clean up just in case
            ## no polyline in pyqt - use open painter path instead 
            self.newPath = QGraphicsPathItem(self.pathWorks.setPaintPath())
            self.newPath.setPen(QPen(QColor(self.color), 3, Qt.PenStyle.DashDotLine))
            self.newPath.setZValue(common['pathZ']) 
            self.scene.addItem(self.newPath)  ## only one - no group needed
            self.addingNewPath = True
                    
### --------------------------------------------------------
    def pathChooser(self, where=''): 
        if not self.pathChooserSet and not self.addingNewPath:
            if not self.editingPts:
                paths = getPathList()
                if len(paths) == 0:
                    MsgBox('getPathList: No Paths Found!', 5)
                    return None
                self.chooser = DoodleMaker(self.canvas, where) 
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
        if len(self.openPathFile) > 0:  ## statusBar
            self.dots.statusBar.showMessage(
                f"{self.openPathFile} - Number of Points {len(self.pts)}")
            if self.pathWorks.widget != None:
                self.pathWorks.widget.resetSliders()
                file = os.path.basename(self.openPathFile)
                self.pathWorks.widget.label.setText(file)
                           
### -------------------- path stuff ------------------------
    def addPath(self):
        self.removePath()  ## not for animation
        self.path = QGraphicsPolygonItem(self.edits.drawPoly(self.pts))       
        self.path.setPen(QPen(QColor(self.color), 3, Qt.PenStyle.DashDotLine))
        self.path.setZValue(common['pathZ']) 
        self.scene.addItem(self.path)
        self.pathSet = True
    
    def removePath(self):       
        if self.pathSet == True:
            self.pathWays.removeWayPtTags()
            if self.path != None:
                self.scene.removeItem(self.path)
            self.pathSet = False
            self.path = None
                                        
### -------------------- dotsPathMaker ---------------------




