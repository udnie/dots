
import os
import time

from PyQt6.QtCore       import Qt, pyqtSignal, QTimer
from PyQt6.QtGui        import QPainter
from PyQt6.QtWidgets    import QGraphicsView

from dotsSideGig        import MsgBox
from dotsShared         import singleKeys
from dotsSideCar        import SideCar
from dotsSideCar2       import SideCar2
from dotsMapMaker       import MapMaker

### ------------------ dotsControlView ---------------------
''' dotsControlView: Base class to create the control view adds drag and 
    drop. Thanks to tpoveda @ https://gist.github.com/tpoveda for posting''' 
### --------------------------------------------------------
class ControlView(QGraphicsView):
### --------------------------------------------------------
    keysSignal = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        self.canvas   = parent         
        self.mapper   = MapMaker(self.canvas)  ## carry mapper to sidecar  
        self.sideCar  = SideCar(self.canvas)
        self.sideCar2 = SideCar2(self.canvas)

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
        if e.mimeData().hasUrls():
      
            if self.canvas.control != '' or self.canvas.animation == True: 
                e.setAccepted(False)
                return
            
            m = e.mimeData()
            fileName = m.urls()[0].toLocalFile()       
            ext = fileName[fileName.rfind('.'):].lower()
    
            if ext in ('.mov', '.mp4', '.caf', '.mp3', '.m4a', '.ogg', '.wav'):
                if  self.canvas.videoPlayer != None:
                    self.canvas.videoPlayer.stopVideo()
                    time.sleep(.10)
                self.canvas.sideCar.addVideo(fileName, "dnd")
                    
            elif ext in ('.png', '.jpg', '.jpeg', '.bmp', '.gif') and fileName != 'star':
                if self.canvas.pathMakerOn:  
                    e.setAccepted(False)
                    MsgBox("Can't add sprites to PathMaker", 5)
                    return    
                else:             
                    e.setAccepted(True)
                    self.dragOver = True
            else:
                e.setAccepted(False)

    def dropEvent(self, e):
        m = e.mimeData()  ## works for sprites
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
        self.sendIt(key, mod)
        
    def sendIt(self, key, mod):

### --------------------------------------------------------
    ## single keys without modifiers
### --------------------------------------------------------     
        if key in (33, 64) and self.canvas.pathMakerOn:
            if key == 33:  ## special keys - may differ in another OS
                self.setKey('!')  ## half number of points        
            else:
                self.setKey('@')  ## evenly redistribute points

        elif key in (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape):
                self.canvas.exit() 
             
        elif key in (Qt.Key.Key_C, Qt.Key.Key_F, Qt.Key.Key_Backspace, Qt.Key.Key_Delete, Qt.Key.Key_Space):
             
            if key == Qt.Key.Key_C: 
                self.setKey('C')  ## clear canvas and storyboard, pathmaker if no edits
            
            elif key == Qt.Key.Key_F:
                if self.canvas.pathMakerOn == False:  
                    self.sideCar2.flopSelected()         
                else:
                    self.canvas.sideCar2.sendPixKeys('F')
                            
            elif key in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete): 
                self.setKey('del')
                    
            elif key == Qt.Key.Key_Space:
                if self.canvas.control != '' or self.canvas.animation == True or self.canvas.videoPlayer != None:
                    self.sideCar.pause()  ## SpaceBar - pause/resume
                                
### --------------------------------------------------------                                                        
    ## keys with modifiers
### -------------------------------------------------------- 
        elif key in (Qt.Key.Key_B, Qt.Key.Key_D, Qt.Key.Key_H, Qt.Key.Key_L):
           
            if key == Qt.Key.Key_B:
                if not self.canvas.pathMakerOn:
                    if mod & Qt.KeyboardModifier.ShiftModifier:
                        self.sideCar2.mirrorBkg(1) 
                        
                    elif mod & Qt.KeyboardModifier.AltModifier:
                        self.sideCar2.mirrorBkg(-1) 
                                                        
                    else:
                        self.sideCar2.bkgStuff()
                                                            
            elif key == Qt.Key.Key_D:
                if mod & Qt.KeyboardModifier.ShiftModifier and self.canvas.pathMakerOn:
                    self.setKey('delPts')  ## delete selected pts in pathmaker
                    
                else: 
                    self.setKey('D')
                                                        
            elif key == Qt.Key.Key_H:  ## toggles hides/unhides selections 
                self.sideCar.toggleSelections() if mod & Qt.KeyboardModifier.ShiftModifier else\
                    self.setKey('H')  ## help 
                    
            elif key == Qt.Key.Key_L:
                if mod & Qt.KeyboardModifier.ShiftModifier:  ##  ## toggles sprites locked on/off
                    self.sideCar.toggleSpriteLocks()  ## this lets 'L' pass  
                else:
                    self.setKey('L')  ## used by pathmaker to toggle lasso 
           
        elif key in (Qt.Key.Key_M, Qt.Key.Key_R, Qt.Key.Key_S, Qt.Key.Key_T, Qt.Key.Key_U):       
           
            if key == Qt.Key.Key_M:
                if mod & Qt.KeyboardModifier.ShiftModifier:  
                    self.sideCar.dump()   
                else:
                    self.setKey('M')
                    
            elif key == Qt.Key.Key_R:   ## unlink. unlock, unselect - sprites and shadowsand bkgs
                self.sideCar.resetAll() if mod & Qt.KeyboardModifier.ShiftModifier else\
                    self.setKey('R')
                                                       
            elif key == Qt.Key.Key_S:  ## toggles shadows linked on/off        
                if mod & Qt.KeyboardModifier.ShiftModifier and \
                    self.canvas.control == '':
                        self.sideCar.toggleShadowLinks()  ## does them all                       
                else:
                    self.setKey('S')  
                                                            
            elif key == Qt.Key.Key_T:  ## toggles tags both link and lock
                if self.canvas.pathMakerOn == True:
                    self.setKey('T')
                    
                elif mod & Qt.KeyboardModifier.ShiftModifier or self.canvas.control !='':
                    self.mapper.toggleTagItems('all')       
                else:
                    self.canvas.sideCar2.sendPixKeys('T') 

            elif key == Qt.Key.Key_U:  ## unlocks all sceneItems     
                if mod & Qt.KeyboardModifier.ShiftModifier:
                    self.canvas.sideCar2.unlockAll()  
                else:
                    self.setKey('U')  

        ## apple option key and cmd key - used by scroll panel to scroll tiles
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_Up) and \
            self.canvas.pathMakerOn == False:
                
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
    ## send key to storyBoard    
### --------------------------------------------------------         
    def setKey(self, key):  
        self.key = key
        self.keysSignal[str].emit(self.key)

    def keyReleaseEvent(self, e):   
        self.keysSignal[str].emit('')
        
### ------------------ dotsControlView ---------------------



