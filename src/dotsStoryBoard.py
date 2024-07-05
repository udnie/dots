
import random

from functools          import partial

from PyQt6.QtCore       import QAbstractAnimation, QTimer, QEvent, QPointF, pyqtSlot
from PyQt6.QtGui        import QTransform
from PyQt6.QtWidgets    import QWidget, QRubberBand, QGraphicsScene
                                        
from dotsShared         import common, CanvasStr, PathStr, MoveKeys, ControlKeys, PlayKeys
from dotsAnimation      import *
from dotsSideCar        import SideCar
from dotsControlView    import ControlView
from dotsPixItem        import PixItem
from dotsMapMaker       import MapMaker
from dotsBkgMaker       import *
from dotsShowBiz        import ShowBiz
from dotsShowTime       import ShowTime
from dotsPathMaker      import PathMaker
from dotsKeysPanel      import KeysPanel
from dotsScrollPanel    import ScrollPanel
from dotsDocks          import *
from dotsWings          import Wings
from dotsShowWorks      import ShowWorks
from dotsMenus          import AnimationMenu
from dotsSideGig        import MsgBox

### -------------------- dotsStoryBoard --------------------
''' class StoryBoard: program hub/canvas, includes context menu and 
    screen handling for selecting screen objects '''
### --------------------------------------------------------
class StoryBoard(QWidget):
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()

        self.dots  = parent 
        
        self.scene = QGraphicsScene(0, 0, common['ViewW'], common['ViewH'])
        self.view  = ControlView(self)
        
        self.view.setGeometry(QRect(0,0,common['ViewW']+2, common['ViewH']+2))
        self.setFixedSize(common['ViewW']+2, common['ViewH']+2)
     
        ## these variables are shared across some classes
        self.control = ''           ## shared
        self.pathMakerOn = False    ## shared
        self.openPlayFile = ''      ## shared 
        self.pathList = []          ## used by animations and animation menu
    
        self.canvas    = self
        self.sideCar   = SideCar(self)   
        
        self.keysPanel = KeysPanel(self)
        self.scroll    = ScrollPanel(self)
        self.pathMaker = PathMaker(self)

        self.mapper    = MapMaker(self) 
        self.bkgMaker  = BkgMaker(self)
     
        self.animation = Animation(self)    
                 
        self.showbiz    = ShowBiz(self)  ## reads .play files    
        self.showtime   = ShowTime(self)  ## runs anything tagged as an animation 
        self.showWorks  = ShowWorks(self) 
         
        addScrollDock(self)  ## add button groups from dotsDocks
        addKeysDock(self)
        addButtonDock(self)  

        self.key = ''
        self.origin = QPoint(0,0)
        self.pixCount = 1
        
        self.rubberBand = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.setMouseTracking(True)
              
        self.view.viewport().installEventFilter(self)
        self.view.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)  
    
        self.view.keysSignal[str].connect(self.setKeys)  
        
        if self.dots.msg != '':
            QTimer.singleShot(100, self.bkgMaker.exceedsMsg)
            self.dots.msg = ''
                
### ---------------------- send keys -----------------------
    @pyqtSlot(str)
    def setKeys(self, key):  ## managing storyboard and pathMaker
        self.key = key  
        if self.key == 'C':  ## clear canvas
            if self.pathMakerOn:
                if len(self.scene.items()) == 0:
                   self.clear()   ## really does it and returns to canvas
                else:
                    self.pathMaker.pathKeys(self.key)  ## centers path
            else:
                self.clear()  ## canvas
                
        elif not self.pathMakerOn:  ## canvas/storyboard
            if self.key in CanvasStr or self.key == '': 
                if self.key in PlayKeys:  ## empty canvas hotkeys - let 'A' and 'H' go first
                    if self.key == 'A' and len(self.scene.items()) > 0:
                        self.selectAll()
                    elif self.key == 'H' and len(self.scene.items()) > 0:
                        self.sideCar.hideSelected(),  ## patched to run hep if nothing on screen     
                    else:  ## need to slow it down after changing screen format - single key commands processed in showbiz
                        QTimer.singleShot(100, partial(self.showbiz.keysInPlay, self.key))  
                else:
                    self.sendPixKeys() 
                                 
        ## send MoveKeys to PathItem selections in PathEdits
        elif self.pathMaker.edits.pointItemsSet() == True and \
            self.pathMaker.selections and self.key in MoveKeys:  ## Keys in shared.py
                self.sendPixKeys()  ## pointItems get messaged
                          
        ## send the rest to pathMaker
        elif self.key in PathStr: 
            self.pathMaker.pathKeys(self.key)

### --------------------- event filter ---------------------- 
    def eventFilter(self, source, e):  ## used by mapper for selecting
        if not self.pathMakerOn:           
            if e.type() == QEvent.Type.MouseButtonPress:
                if e.button() == Qt.MouseButton.RightButton and len(self.scene.items()) == 0:
                    self.showbiz.helpMenu.openHelpMenu()   
                  
                else:       
                    self.origin = QPoint(e.pos())
                    self.mapper.clearTagGroup()  ## chks if set
                    ## 'cmd' also used in pathMaker but for editing
                if self.key == 'cmd':  
                    self.mapper.clearMap()   ## set rubberband if mapset
                    self.unSelect()              
                elif self.sideCar.hasHiddenPix() or self.mapper.selections:
                    if self.control not in ControlKeys:
                        self.mapper.updatePixItemPos()   
                                        
            ##  enter 'cmd' before you move the mouse and the rubberband kicks in, but not after
            elif e.type() == QEvent.Type.MouseMove:  
                if self.key == 'cmd' and self.origin != QPoint(0,0):
                    if self.mapper.isMapSet(): 
                        self.mapper.removeMap()
                    self.rubberBand.show()
                    self.rubberBand.setGeometry(QRect(self.origin, e.pos()).normalized())          
                elif self.mapper.isMapSet() and not self.scene.selectedItems():
                    self.mapper.removeMap()
                elif self.control not in ControlKeys:  ## no animations running
                    self.mapper.updatePixItemPos()  ## costly but necessary    
                               
            elif e.type() == QEvent.Type.MouseButtonRelease:
                if self.mapper.isMapSet() == False:
                    self.rubberBand.hide()  ## supposes something is selected
                    self.mapper.addSelectionsFromCanvas()           
                if self.key == 'cmd'and self.mapper.isMapSet():
                    self.setKeys('')           
                if self.mapper.isMapSet() and not self.scene.selectedItems():
                    self.mapper.removeMap()
                self.mapper.updatePixItemPos()    
                       
            elif e.type() == QEvent.Type.MouseButtonDblClick:
                ## to preseve selections dblclk on an selection otherwise it 
                ## will unselect all - possibly a default as it works the 
                ## same as single click outside the map area 
                ## do this if nothing at location
                if p := self.scene.itemAt(QPointF(e.pos()), QTransform()):
                    if p != None and p.type != 'pix' and self.mapper.isMapSet():
                        self.mapper.removeMap()
                        self.setKeys('noMap')    
                                  
        return QWidget.eventFilter(self, source, e)
    
### --------------------------------------------------------
    ## set in drag/drop for id and in pixitem to clone itself
    def addPixItem(self, fileName, x, y, clone, mirror):  
        if 'wings' in fileName:  ## makes a bat
            Wings(self, x, y, '')       
        else:
            self.pixCount += 1  
            pix = PixItem(fileName, self.pixCount, x, y, self, mirror)            
            if clone != None:  ## clone it                    
                self.sideCar.transFormPixItem(pix,
                    clone[0],
                    clone[1] * random.randrange(95, 105)/100.0,
                    pix.alpha2)
                return   
            elif 'frame' in pix.fileName: 
                self.showWorks.addFrame(pix.fileName)  ## pin it on drag and drop
            else:
                self.scene.addItem(pix)
        
    def sendPixKeys(self):  ## update pixitems and pointItems thru setPixKeys
        for itm in self.scene.items():  ## used with lasso to move selections
            if itm.type in ('pt','pix', 'bkg', 'frame', 'flat'):   
                if itm.type == 'pt' or itm.type == 'pix' and \
                    itm.part not in ('pivot','left','right'):  ## 06-23-23
                    itm.setPixKeys(self.key)
                elif itm.type in ('bkg', 'frame', 'flat'):  
                    itm.setPixKeys(self.key)     
        if self.mapper.isMapSet(): 
            self.mapper.updateMap()
                  
    def exit(self):
        self.clear() 
        self.dots.closeAll()
        QTimer.singleShot(20, self.dots.close)   
                
    def clearSceneItems(self):
        for p in self.scene.items():      
            if p.type == 'pix' and p.part in ('left', 'right'):
                continue
            try:
                self.scene.removeItem(p) 
            except Exception:
                continue
               
    def clear(self):  ## do this before exiting app as well 
        if self.canvas.pathMakerOn:
            self.pathMaker.pathMakerOff()                   
        self.sideCar.clearWidgets()    
        self.showtime.stop('clear')   
        self.showWorks.cleanupMenus(self.showbiz)     
        self.clearSceneItems()          
        self.mapper.clearMap()    
        self.scene.clear()       
        self.btnAddBkg.setEnabled(True)   
        if self.dots.statusBar: self.dots.statusBar.clearMessage()
        self.pixCount = 0  ## set it to match showbiz
        self.sideCar.gridGroup = None
        self.openPlayFile = ''
        self.bkgMaker.init()
        self.view.grabKeyboard()
         
    def loadSprites(self):
        self.showWorks.enablePlay()
        self.scroll.loadSprites()
 
    def selectAll(self):
        if len(self.scene.items()) == 0:  ## if 'A' 
            self.bkgMaker.openBkgFiles() 
            return
        for pix in self.scene.items():
            if pix.type in ('pix', 'shadow'):
                pix.setSelected(True)
                pix.isHidden = False
            elif pix.zValue() <= common['pathZ']:
                break

    def unSelect(self):  ## sharing the 'U' with pathMaker for unselect
        self.mapper.clearMap()  
        for itm in self.scene.items():  
            if itm.type == 'pix':
                itm.isHidden = False 
                itm.setSelected(False)  
            elif itm.type == 'pt' and self.pathMaker.selections and \
                itm.idx in self.pathMaker.selections:
                    idx = self.pathMaker.selections.index(itm.idx)  ## use the index        
                    self.pathMaker.selections.pop(idx)  
                    itm.setBrush(QColor('white'))   
            if itm.zValue() <= common['pathZ']:
                break          
      
### --------------------------------------------------------
    def deleteSelected(self):  ## self.pathMakerOn equals false   
        if len( self.scene.items()) == 0:
            self.showbiz.keysInPlay('D')
        
        self.mapper.clearMap()
        self.mapper.clearTagGroup()
        k = 0
        for pix in self.scene.selectedItems():      
            if pix.type == 'pix':  ## could be something else
                if pix.anime != None and \
                    pix.anime.state() == QAbstractAnimation.State.Running:
                    pix.anime.stop()  
                pix.setSelected(False)
                pix.deletePix()  ## deletes shadow as well 
                del pix
                k += 1
        if k > 0: self.showWorks.enablePlay()  ## stop it - otherwise it's hung
    
    def flopSelected(self):    
        if self.pathMakerOn == False:
            for pix in self.scene.items():
                if pix.type == 'pix':
                    if pix.isSelected() or pix.isHidden:
                        if pix.flopped:
                            pix.setMirrored(False)
                        else:
                            pix.setMirrored(True)
                elif pix.zValue() <= common['pathZ']:
                    break
                       
### --------------------------------------------------------
    def contextMenuEvent(self, e):  ## needs to stay here - pix popup menu for animations and paths
        if len(self.scene.selectedItems()) > 0:
            menu = AnimationMenu(self)
            menu.animeMenu(e.globalPos())  ## only place its used
        
### -------------------- dotsStoryBoard --------------------


