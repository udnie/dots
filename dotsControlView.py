import os
import sys

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from dotsShared      import common

### ------------------ dotsControlView ---------------------
''' dotsControlView: Base class to create the control view from 
    tpoveda / ControlView.py  https://gist.github.com/tpoveda ''' 
### --------------------------------------------------------
class ControlView(QGraphicsView):
    ## adds drag and drop to a QGraphicsView instance
    ## big thanks to tpoveda for posting this
    keysSignal = pyqtSignal([str])

    def __init__(self, scene, parent):

        super().__init__(parent)

        self.setObjectName('ControlView')
        self.setScene(scene)
           
        self.scene = scene
        self.canvas = parent
        self.dragOver = False

        # didn't seem to need it
        # self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
    
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
      
### --------------------------------------------------------
    def dragMoveEvent(self, e):
        pass

    def dragEnterEvent(self, e):
        ext = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
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
            x, y = e.pos().x(),  e.pos().y()
            imgFile = m.urls()[0].toLocalFile()
            ## None = clone source, False = mirror right/left
            self.canvas.addPixItem(imgFile, x, y, None, False)
   
### -------------------------------------------------------
    ## Location I found that works best for reading keys
    ## especially the arrow keys
    def keyPressEvent(self, e):
        key = e.key()  
        ## print("key event: ", QKeySequence(e.key()).toString())
        if key in (Qt.Key_Backspace, Qt.Key_Delete):  ## can vary
            self.setKey('del')
        elif key == Qt.Key_A:
            self.canvas.selectAll()
        elif key == Qt.Key_B:
            self.setKey('bak')
        elif key == Qt.Key_C:
            self.canvas.clear()
        elif key == Qt.Key_D:
            self.canvas.deleteSelected()
        elif key == Qt.Key_F:
            self.canvas.flopSelected()  
        elif key == Qt.Key_G:
            self.canvas.sideCar.toggleGrid() 
        elif key == Qt.Key_H:
            self.canvas.hideSelected() 
        elif key == Qt.Key_M:
            self.canvas.initMap.toggleMap()
        elif key == Qt.Key_P:
            self.canvas.sideShow.play()
        elif key == Qt.Key_T:
            self.canvas.sideShow.toggleTagItems()
        elif key == Qt.Key_U:
            self.canvas.unSelect()
        elif key == Qt.Key_Z:   ## out of service
            self.canvas.ZDump()
        elif key == Qt.Key_Left:
            self.setKey('left')
        elif key == Qt.Key_Right:
            self.setKey('right')
        elif key == Qt.Key_Up:
            self.setKey('up')
        elif key == Qt.Key_Down:
            self.setKey('down')
        elif key == Qt.Key_Control:
            self.setKey('cmd')    ## command key on mac
        elif key == Qt.Key_Shift:  
            self.setKey('shift')
        elif key == Qt.Key_Alt:
            self.setKey('opt')    ## option key on mac
        elif key == Qt.Key_Plus:
            self.setKey('+')  
        elif key == Qt.Key_Underscore:
            self.setKey('-')  
        elif key == Qt.Key_Less:
            self.setKey('<')
        elif key == Qt.Key_Greater:
            self.setKey('>')
        elif key == Qt.Key_BraceRight:
            self.setKey('}')
        elif key == Qt.Key_BraceLeft:
            self.setKey('{')
        elif key == Qt.Key_Colon:
            self.setKey(':')
        elif key == Qt.Key_QuoteDbl:
            self.setKey('"')
        elif e.key() in (Qt.Key_X, Qt.Key_Q, Qt.Key_Escape):
            sys.exit() 

    def setKey(self, key):  ## sending key to dropCanvas
        self.key = key
        self.keysSignal[str].emit(self.key)

    def keyReleaseEvent(self, e):   
        self.keysSignal[str].emit('')

### -------------------- dotsDropCanvas --------------------
