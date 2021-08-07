import os
import sys

from PyQt5.QtCore    import Qt, pyqtSignal
from PyQt5.QtGui     import QPainter
from PyQt5.QtWidgets import QGraphicsView

from dotsSideGig     import MsgBox
from dotsShared      import common, singleKeys
from dotsSideCar     import SideCar
from dotsMapItem     import InitMap

MixKeys   = (Qt.Key_D, Qt.Key_F, Qt.Key_T)
ExitKeys  = (Qt.Key_X, Qt.Key_Q, Qt.Key_Escape)
FileTypes = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

### ------------------ dotsControlView ---------------------
''' dotsControlView: Base class to create the control view adds drag and 
    drop. Thanks to tpoveda @ https://gist.github.com/tpoveda for posting''' 
### --------------------------------------------------------
class ControlView(QGraphicsView):
### --------------------------------------------------------
    ## adds drag and drop to a QGraphicsView instance and 
    ## keyboard capture 
    keysSignal = pyqtSignal([str])

    def __init__(self, parent):
        super().__init__(parent)

        self.canvas = parent       
        self.dots   = parent.dots

        self.canvas.mapper = InitMap(self.canvas)
        self.sideCar = SideCar(self.canvas)

        self.setObjectName('ControlView')
        self.setScene(parent.scene)
      
        self.dragOver = False
    
        self.setRenderHints(QPainter.Antialiasing | 
            QPainter.TextAntialiasing | 
            QPainter.SmoothPixmapTransform)

        self.setStyleSheet("border: 1px solid rgb(100,100,100)")

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setAcceptDrops(True)  
      
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        self.grabKeyboard()  ## happy days
      
        self.direct = {
            Qt.Key_A: self.canvas.selectAll,
            Qt.Key_H: self.canvas.hideSelected,
            Qt.Key_U: self.canvas.unSelect,
            Qt.Key_Z: self.canvas.ZDump,
        }

        self.ToggleKeys = {
            Qt.Key_G: self.sideCar.toggleGrid,
            Qt.Key_K: self.dots.sliderpanel.toggleMenu,
            Qt.Key_M: self.canvas.mapper.toggleMap,
        }

### --------------------------------------------------------
    def dragMoveEvent(self, e):
        pass

    def dragEnterEvent(self, e):
        if self.canvas.pathMakerOn:  ## added for pathmaker
            e.setAccepted(False)
            MsgBox("Can't add sprites to PathMaker")
            return
        ext = FileTypes
        if e.mimeData().hasUrls():
            m = e.mimeData()
            imgFile = m.urls()[0].toLocalFile()
            if imgFile != 'star' and imgFile.lower().endswith(ext): 
                e.setAccepted(True)
                self.dragOver = True
            else:
                e.setAccepted(False)

    def dropEvent(self, e):
        m = e.mimeData()
        if m.hasUrls():
            imgFile = m.urls()[0].toLocalFile()
            ## None = clone source, False = mirror right/left
            self.canvas.pixCount = self.canvas.mapper.toFront(0)
            self.canvas.addPixItem(imgFile, e.pos().x(), e.pos().y(), 
                None, False)
   
### -------------------------------------------------------
    ## best location for reading keys - especially arrow keys
    def keyPressEvent(self, e):
        key = e.key() 
        mod = e.modifiers()
        if e.key() == 33 and self.canvas.pathMakerOn:  ## '!' on a mac
            self.setKey('!')
        elif key in (Qt.Key_Backspace, Qt.Key_Delete):  ## can vary
            self.setKey('del')
        ## mix of setKey and direct run
        elif key in MixKeys:
            if key == Qt.Key_D:    
                self.setKey('D') 
                self.canvas.deleteSelected()
            elif key == Qt.Key_F:
                self.setKey('F')    ## if pathMaker on
                self.canvas.flopSelected()  
            elif key == Qt.Key_P:
                self.canvas.mapper.togglePaths() 
                self.setKey('P')
            elif key == Qt.Key_T:
                if self.canvas.pathMakerOn:
                    self.setKey('T')      ## run test if pathMaker on
                elif mod & Qt.ShiftModifier:
                    self.canvas.mapper.toggleTagItems('select')
                else:  
                    self.canvas.mapper.toggleTagItems('all')
        elif key in self.direct: 
            self.direct[key]()  
        elif key in self.ToggleKeys:
            self.ToggleKeys[key]()  
        elif key in singleKeys: ## in dotsShared.py   
            if key in (Qt.Key_L, Qt.Key_R) and mod & Qt.ShiftModifier:
                self.canvas.togglePixLocks(singleKeys[key])
            else:
                self.setKey(singleKeys[key]) 
        elif e.key() in ExitKeys:
            self.canvas.exit() 

    def setKey(self, key):  ## sending key to dropCanvas
        self.key = key
        self.keysSignal[str].emit(self.key)

    def keyReleaseEvent(self, e):   
        self.keysSignal[str].emit('')

### ------------------ dotsControlView ---------------------

