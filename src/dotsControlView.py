
import os

from PyQt6.QtCore       import Qt, pyqtSignal
from PyQt6.QtGui        import QPainter
from PyQt6.QtWidgets    import QGraphicsView

from dotsSideGig        import MsgBox
from dotsShared         import singleKeys
from dotsSideCar        import SideCar
from dotsMapMaker       import MapMaker
from dotsSideGig        import Grid
from dotsShared         import ControlKeys

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
        self.grid    = Grid(self.canvas)
     
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
        ext = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
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
            self.canvas.addPixItem(fileName, e.position().x(), e.position().y(),  
                None, False)
            
    def dragLeaveEvent(self, e):
        e.accept()

### --------------------------------------------------------
    def keyPressEvent(self, e):
        key = e.key() 
        mod = e.modifiers()
     
### ------------- single keys without modifiers -------------     
        if key in (33, 64) and self.canvas.pathMakerOn:
            if key == 33:  ## special keys - may differ in another OS
                self.setKey('!')  ## half number of points
            else:
                self.setKey('@')  ## evenly redistribute points
              
        elif key in (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape):
            self.canvas.exit() 
            
        elif key in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete): 
            self.setKey('del')
                  
        elif key == Qt.Key.Key_Space and self.canvas.control != '': 
            self.sideCar.pause()  ## SpaceBar - pause/resume
                    
        elif key == Qt.Key.Key_G:
            self.grid.toggleGrid()           
                     
        elif key == Qt.Key.Key_K:  ## keysMenu for storyboard and pathMaker  
            self.sideCar.toggleKeysMenu()           
 
### -------- keys with modifiers or pathMaker flags ----------                             
        elif key == Qt.Key.Key_D:
            if mod & Qt.KeyboardModifier.ShiftModifier and self.canvas.pathMakerOn:
                self.setKey('delPts')  ## delete selected pts in pathmaker
            else: 
                self.setKey('D')
                          
        elif key == Qt.Key.Key_F:
            if self.canvas.pathMakerOn == False:  
                self.canvas.flopSelected()  ## yep
            else:
                self.setKey('F')
                                     
        elif key == Qt.Key.Key_H:  ## toggles hides/unhides selections 
            if mod & Qt.KeyboardModifier.ShiftModifier:
                self.sideCar.toggleSelections()      
            else:
                 self.setKey('H')  ## help 
                 
        elif key == Qt.Key.Key_L and \
            mod & Qt.KeyboardModifier.ShiftModifier:  ##  ## toggles sprites locked on/off
                self.sideCar.toggleSprites()  ## this lets 'L' pass
                                     
        elif key == Qt.Key.Key_O:                
            if mod & Qt.KeyboardModifier.ShiftModifier:   
                self.sideCar.clearWidgets()            
                self.sideCar.hideSelectedShadows()  ## toggles display on/off if pix is selected
                self.sideCar.toggleOutlines()
            else:
                self.setKey('O')
                   
        elif key == Qt.Key.Key_R:   ## unlink. unlock, unselect
            if mod & Qt.KeyboardModifier.ShiftModifier:  ## sprites and shadows
                self.sideCar.resetAll()  
            else:
                self.setKey('R')
                                                       
        elif key == Qt.Key.Key_S:  ## toggles shadows linked on/off
            if mod & Qt.KeyboardModifier.ShiftModifier and \
                self.canvas.control == '':
                    self.sideCar.toggleShadows()  ## does them all                            
            else:
                self.setKey('S')  
                                                          
        elif key == Qt.Key.Key_T:  ## toggles tags display on/off both link and lock
            if mod & Qt.KeyboardModifier.ShiftModifier:      
                self.mapper.toggleTagItems('all') 
            else:
                self.setKey('T')  
             
        elif key == Qt.Key.Key_U:  ## unselect for storyBoard and pathMaker
            if self.canvas.pathMakerOn:
                self.canvas.unSelect()
            else:
                self.setKey('U')  
               
        elif key == Qt.Key.Key_W:  ## yes - that's what it does
            if self.canvas.pathMakerOn:
                self.canvas.pathMaker.pathWays.addWayPtTags()   
            else:       
                self.sideCar.clearWidgets()   

        ## apple option key and cmd key - used by scroll panel to scroll tiles
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_Up) and self.canvas.pathMakerOn == False:      
            if mod & Qt.KeyboardModifier.AltModifier:  
                self.sideCar.pageDown('1') if key == Qt.Key.Key_Down else \
                    self.sideCar.pageDown('-1')  ## scroll one tile         
            elif mod & Qt.KeyboardModifier.ControlModifier:  
                self.sideCar.pageDown('down') if key == Qt.Key.Key_Down else \
                    self.sideCar.pageDown('up')  ## scroll visibile tiles minus 1       
            else:                  
                self.setKey(singleKeys[key])  ## everyone else 
                            
        elif key in singleKeys:  ## in dotsShared.py  
            self.setKey(singleKeys[key])
   
### --------------------------------------------------------         
    def setKey(self, key):  ## sending key to storyBoard
        self.key = key
        self.keysSignal[str].emit(self.key)

    def keyReleaseEvent(self, e):   
        self.keysSignal[str].emit('')
        
### ------------------ dotsControlView ---------------------



