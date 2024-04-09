
import os

from PyQt6.QtCore       import Qt, pyqtSignal
from PyQt6.QtGui        import QPainter
from PyQt6.QtWidgets    import QGraphicsView

from dotsSideGig        import MsgBox
from dotsShared         import singleKeys
from dotsSideCar        import SideCar
from dotsMapMaker       import MapMaker

ExitKeys  = (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape)
FileTypes = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
LockKeys  = (Qt.Key.Key_L, Qt.Key.Key_R, Qt.Key.Key_U) 
ShiftKeys = (Qt.Key.Key_D, Qt.Key.Key_T, Qt.Key.Key_V, Qt.Key.Key_H, \
            Qt.Key.Key_W,  Qt.Key.Key_O, Qt.Key.Key_B, Qt.Key.Key_J, \
            Qt.Key.Key_S)
UpDownKeys = (Qt.Key.Key_Down, Qt.Key.Key_Up)
DFTWKeys  = (Qt.Key.Key_D, Qt.Key.Key_F, Qt.Key.Key_T, Qt.Key.Key_W)
ToggleKeys = (Qt.Key.Key_G, Qt.Key.Key_M, Qt.Key.Key_K)
DirectKeys = (Qt.Key.Key_A, Qt.Key.Key_U, Qt.Key.Key_O)

### ------------------ dotsControlView ---------------------
''' dotsControlView: Base class to create the control view adds drag and 
    drop. Thanks to tpoveda @ https://gist.github.com/tpoveda for posting''' 
### --------------------------------------------------------
class ControlView(QGraphicsView):
### --------------------------------------------------------
    keysSignal = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        self.canvas  = parent         
        self.mapper  = MapMaker(self.canvas)  ## carry mapper to sidecar  
        self.sideCar = SideCar(self.canvas)
     
        self.setObjectName('ControlView')
        self.setScene(self.canvas.scene)
         
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing | 
            QPainter.RenderHint.TextAntialiasing | 
            QPainter.RenderHint.SmoothPixmapTransform
        )
        
        self.setStyleSheet('border: 1px solid rgb(160,160,160)')

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setAcceptDrops(True)  
      
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

        self.grabKeyboard()  ## happy days
      
### --------------------------------------------------------
    def dragMoveEvent(self, e):
        pass

    def dragEnterEvent(self, e):
        if self.canvas.pathMakerOn:  ## added for pathmaker
            e.setAccepted(False)
            MsgBox("Can't add sprites to PathMaker", 5)
            return
        ext = FileTypes
        if e.mimeData().hasUrls():
            m = e.mimeData()
            fileName = m.urls()[0].toLocalFile()
            if fileName != 'star' and fileName.lower().endswith(ext): 
                e.setAccepted(True)
                self.dragOver = True
            else:
                e.setAccepted(False)

    def dropEvent(self, e):
        m = e.mimeData()
        if m.hasUrls():
            fileName = m.urls()[0].toLocalFile()
            ## None = clone source, False = mirror right/left
            self.canvas.pixCount = self.mapper.toFront(0)
            # self.canvas.addPixItem(fileName, e.pos().x(), e.pos().y(), ### Qt5 uses pos
            self.canvas.addPixItem(fileName, e.position().x(), e.position().y(),  ### Qt6 takes position
                None, False)
            
    def dragLeaveEvent(self, e):
        e.accept()

### -------------------------------------------------------
    ## best location for reading keys - especially arrow keys
    def keyPressEvent(self, e):
        key = e.key() 
        mod = e.modifiers()
     
        ## special keys - may differ in another OS - !, @, del
        if e.key() == 33 and self.canvas.pathMakerOn:
            self.setKey('!')  ## use by pathMaker
        elif e.key() == 64 and self.canvas.pathMakerOn:
            self.setKey('@')
        elif key in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete): 
            self.setKey('del')
                        
        ##  all the shift keys 
        elif key in ShiftKeys and mod & Qt.KeyboardModifier.ShiftModifier:   
            ## keys - D, T, V, H , O, B, S        
            if key == Qt.Key.Key_D and self.canvas.pathMakerOn:
                self.setKey('delPts')  ## send to pathmaker
            elif key == Qt.Key.Key_W:  ## show waypts
                if self.canvas.pathMakerOn:  
                    self.canvas.pathMaker.pathWays.addWayPtTags()  
            elif key == Qt.Key.Key_O:         
                self.sideCar.hideOutlines()                      
            elif key == Qt.Key.Key_T:         
                self.mapper.toggleTagItems('select')  ## 'shift-T'  
            elif key == Qt.Key.Key_H:
                self.sideCar.hideSelectedShadows()
                self.sideCar.clearWidgets()
                self.sideCar.toggleOutlines()
            elif key == Qt.Key.Key_B:
                self.sideCar.dumpBkgs()
            elif key == Qt.Key.Key_S:
                self.sideCar.unlinkShadows()
                        
        # keys used in locking screen items - L, R, U
        elif key in LockKeys and mod & Qt.KeyboardModifier.ShiftModifier: 
            self.sideCar.togglePixLocks(singleKeys[key]) 
    
        ## keys to scroll scrollPanel - alt and control modifier - control first then arrow  
        elif key in UpDownKeys and self.canvas.pathMakerOn == False:      
            if mod & Qt.KeyboardModifier.AltModifier:  ## apple option key
                self.sideCar.pageDown('1') if key == Qt.Key.Key_Down else \
                    self.sideCar.pageDown('-1')            
            elif mod & Qt.KeyboardModifier.ControlModifier:  ## apple cmd key
                self.sideCar.pageDown('down') if key == Qt.Key.Key_Down else \
                    self.sideCar.pageDown('up')          
            else:                  
                self.setKey(singleKeys[key])  ## broadcast to widgets - bkgWidget
                                                                                           
        elif key in DFTWKeys:  ## set key as well - used by pathMaker
            if key == Qt.Key.Key_D:  
                self.setKey('D') 
                self.canvas.deleteSelected()
            elif key == Qt.Key.Key_F:
                self.setKey('F') 
                self.canvas.flopSelected()  
            elif key == Qt.Key.Key_T:  ## just 'T'
                self.setKey('T') if self.canvas.pathMakerOn else \
                    self.mapper.toggleTagItems('all')   
            elif key == Qt.Key.Key_W:
                self.sideCar.clearWidgets()    
                        
        elif key == Qt.Key.Key_Space and self.canvas.control != '':  ## pause/resume
            self.sideCar.pause() 
            
        elif key in ToggleKeys:  ## G,M,K
            if key == Qt.Key.Key_G:
                self.sideCar.toggleGrid()
            elif key == Qt.Key.Key_M: 
                self.mapper.toggleMap()
            elif key == Qt.Key.Key_K: 
                self.sideCar.toggleMenu()  ## skeysPanel storyboard and pathMaker keys
                                       
        elif key in DirectKeys:  ## A,U,O
            if key == Qt.Key.Key_A:  ## opens background if no sceneitems 
                self.canvas.selectAll()
            elif key == Qt.Key.Key_U:  ## shared with pathitems for selections
                self.canvas.unSelect()
            elif key == Qt.Key.Key_O: 
                 self.sideCar.toggleOutlines()
     
        elif key in singleKeys:  ## in dotsShared.py  
            self.setKey(singleKeys[key])
          
        elif e.key() in ExitKeys:
            self.canvas.exit() 

    def setKey(self, key):  ## sending key to storyBoard
        self.key = key
        self.keysSignal[str].emit(self.key)

    def keyReleaseEvent(self, e):   
        self.keysSignal[str].emit('')
        
### ------------------ dotsControlView ---------------------



