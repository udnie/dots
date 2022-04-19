
from PyQt5.QtCore    import Qt, pyqtSignal, QProcess
from PyQt5.QtGui     import QPainter
from PyQt5.QtWidgets import QGraphicsView

from dotsSideGig     import MsgBox
from dotsShared      import singleKeys
from dotsSideCar     import SideCar
from dotsMapItem     import InitMap

DFTKeys   = (Qt.Key.Key_D, Qt.Key.Key_F, Qt.Key.Key_T)
ExitKeys  = (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape)
FileTypes = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
LockKeys  = (Qt.Key.Key_L, Qt.Key.Key_R, Qt.Key.Key_U) 
ShiftKeys = (Qt.Key.Key_D, Qt.Key.Key_P, Qt.Key.Key_T, Qt.Key.Key_V, Qt.Key.Key_W)

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
        self.canvas.mapper = InitMap(self.canvas)  ## carry mapper to sidecar
        
        self.sideCar = SideCar(self.canvas)

        self.setObjectName('ControlView')
        self.setScene(parent.scene)
      
        self.dragOver = False
        self.p = None
    
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing | 
            QPainter.RenderHint.TextAntialiasing | 
            QPainter.RenderHint.SmoothPixmapTransform
        )

        self.setStyleSheet("border: 1px solid rgb(100,100,100)")

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setAcceptDrops(True)  
      
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

        self.grabKeyboard()  ## happy days
      
        self.direct = {
            Qt.Key.Key_A: self.canvas.selectAll,
            Qt.Key.Key_H: self.canvas.hideSelected,
            Qt.Key.Key_U: self.canvas.unSelect,
            Qt.Key.Key_Z: self.canvas.ZDump,
        }

        self.toggleKeys = {
            Qt.Key.Key_G: self.sideCar.toggleGrid,
            Qt.Key.Key_M: self.canvas.mapper.toggleMap,
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
            # self.canvas.addPixItem(imgFile, e.position().x(), e.position().y(),  ##  PyQt5
            self.canvas.addPixItem(imgFile, e.pos().x(), e.pos().y(), 
                None, False)
   
### -------------------------------------------------------
    ## best location for reading keys - especially arrow keys
    def keyPressEvent(self, e):
        key = e.key() 
        mod = e.modifiers()   
          
        ## special keys - may differ in another OS
        if e.key() == 33 and self.canvas.pathMakerOn:
            self.setKey('!')
        elif e.key() == 64 and self.canvas.pathMakerOn:
            self.setKey('@')
        elif key in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete): 
            self.setKey('del')
            
        ## handle shift keys   
        elif mod & Qt.KeyboardModifier.ShiftModifier and key in ShiftKeys:
            if key == Qt.Key.Key_D:   
                self.setKey('delPts')  ## send to pathmaker
            elif key == Qt.Key.Key_P:  ## show pix path tags
                if not self.canvas.pathMakerOn:
                    self.canvas.mapper.toggleTagItems('paths')                
            elif key == Qt.Key.Key_T:         
                self.canvas.mapper.toggleTagItems('select')     
            elif key == Qt.Key.Key_V:
                self.startProcess()
            elif key == Qt.Key.Key_W:
                self.sideCar.shadowTime()
                
        ## shift key and lock keys
        elif mod & Qt.KeyboardModifier.ShiftModifier and key in LockKeys:
            self.canvas.togglePixLocks(singleKeys[key])  
                     
        elif key in DFTKeys:
            if key == Qt.Key.Key_D:  
                self.setKey('D') 
                self.canvas.deleteSelected()
            elif key == Qt.Key.Key_F:
                self.setKey('F') 
                self.canvas.flopSelected()  
            elif key == Qt.Key.Key_T:
                if self.canvas.pathMakerOn:
                    self.setKey('T')  ## run test
                else:  
                    self.canvas.mapper.toggleTagItems('all')
                                   
        elif key in self.direct: 
            self.direct[key]()  
            
        elif key in self.toggleKeys:
            self.toggleKeys[key]()  
            
        elif key in singleKeys:  ## in dotsShared.py  
            self.setKey(singleKeys[key]) 
            
        elif e.key() in ExitKeys:
            self.canvas.exit() 

    def setKey(self, key):  ## sending key to dropCanvas
        self.key = key
        self.keysSignal[str].emit(self.key)

    def keyReleaseEvent(self, e):   
        self.keysSignal[str].emit('')

    def startProcess(self):
        if self.p is None:
            self.p = QProcess()  ## thanks to Martin Fitzpatrick
            self.p.finished.connect(self.processFinished)
            self.p.start("python3", ["vhx.py"])  ## works in vscode
            # self.p.start("/on a mac - full  path to /vhx.app")  ## using autotmator
          
    def processFinished(self):
        self.p = None

### ------------------ dotsControlView ---------------------

