import os
import sys

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from dotsShared      import common, singleKeys

toglKeys = (Qt.Key_G, Qt.Key_K, Qt.Key_M)
mixKeys  = (Qt.Key_D, Qt.Key_F, Qt.Key_P, Qt.Key_R, Qt.Key_T)
exitKeys = (Qt.Key_X, Qt.Key_Q, Qt.Key_Escape)
fileTypes = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

### ------------------ dotsControlView ---------------------
''' dotsControlView: Base class to create the control view adds drag and 
    drop. Thanks to tpoveda @ https://gist.github.com/tpoveda for posting''' 
### --------------------------------------------------------
class ControlView(QGraphicsView):
    ## adds drag and drop to a QGraphicsView instance and 
    ## keyboard capture 
    keysSignal = pyqtSignal([str])

    def __init__(self, scene, parent):

        super().__init__(parent)

        self.setObjectName('ControlView')
        self.setScene(scene)
    
        self.canvas = parent   
        self.scene  = parent.scene
    
        self.dragOver = False
  
        # added 2px to prevent noticable screen movement - curious 
        self.setFixedSize(common["viewW"]+2, common["viewH"]+2)
  
        self.setRenderHints(QPainter.Antialiasing | 
            QPainter.TextAntialiasing | 
            QPainter.SmoothPixmapTransform)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setAcceptDrops(True)        
        self.setStyleSheet("border: 1px solid black;")

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        self.grabKeyboard()  ## happy days
      
        self.direct = {
            Qt.Key_A: self.canvas.selectAll,
            Qt.Key_H: self.canvas.hideSelected,
            Qt.Key_U: self.canvas.unSelect,
            Qt.Key_Z: self.canvas.ZDump,
        }

### --------------------------------------------------------
    def dragMoveEvent(self, e):
        pass

    def dragEnterEvent(self, e):
        ext = fileTypes
        if e.mimeData().hasUrls():
            m = e.mimeData()
            imgFile = m.urls()[0].toLocalFile()
            if self.canvas.pathMakerOn:  ## added for pathmaker
                e.setAccepted(False)
            elif imgFile != 'star' and imgFile.lower().endswith(ext): 
                e.setAccepted(True)
                self.dragOver = True
            else:
                e.setAccepted(False)

    def dropEvent(self, e):
        m = e.mimeData()
        if m.hasUrls():
            imgFile = m.urls()[0].toLocalFile()
            ## None = clone source, False = mirror right/left
            self.canvas.addPixItem(imgFile, e.pos().x(), e.pos().y(), 
                None, False)
   
### -------------------------------------------------------
    ## Location I found that works best for reading keys
    ## especially the arrow keys
    def keyPressEvent(self, e):
        key = e.key()  
        if e.key() == 33 and self.canvas.pathMakerOn:  ## '!' on a mac
            self.setKey('!')
        elif key in (Qt.Key_Backspace, Qt.Key_Delete):  ## can vary
            self.setKey('del')

        ## mix of setKey and direct run
        if key in mixKeys:
            if key == Qt.Key_D:    
                self.setKey('D') 
                self.canvas.deleteSelected()
            elif key == Qt.Key_F:
                self.setKey('F')    ## if pathMaker on
                self.canvas.flopSelected()  
            elif key == Qt.Key_P:
                if self.canvas.openPlayFile != '': 
                    self.canvas.mapper.togglePaths() 
                # self.setKey('P')  ## your choice
            elif key == Qt.Key_R:
                if self.canvas.pathMakerOn:
                    self.setKey('R') ## if pathMaker on
                else:  ## if you're testing an animation over again
                    self.canvas.sideShow.runDemo('demo.play')
            elif key == Qt.Key_T:  
                if self.canvas.openPlayFile != '':
                    self.canvas.mapper.toggleTagItems()

        if key in self.direct: 
            self.direct[key]()  ## OK...

        ## too many references
        if key in toglKeys:
            if key == Qt.Key_G:
                self.canvas.sideCar.toggleGrid() 
            elif key == Qt.Key_K:
                self.canvas.sliders.toggleMenu()
            elif key == Qt.Key_M:
                self.canvas.mapper.toggleMap()
  
        if key in singleKeys: ## in dotsShared.py
            self.setKey(singleKeys[key])
        elif e.key() in exitKeys:
            sys.exit() 

    def setKey(self, key):  ## sending key to dropCanvas
        self.key = key
        self.keysSignal[str].emit(self.key)

    def keyReleaseEvent(self, e):   
        self.keysSignal[str].emit('')

### -------------------- dotsDropCanvas --------------------
