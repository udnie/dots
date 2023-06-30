
import random
import gc

from PyQt6.QtCore       import QAbstractAnimation, QTimer, QEvent, QPointF, pyqtSlot
from PyQt6.QtGui        import QTransform
from PyQt6.QtWidgets    import QWidget, QMenu, QRubberBand, QGraphicsScene
                                        
from dotsShared         import common, CanvasStr, PathStr, MoveKeys, PlayKeys
from dotsAnimation      import *
from dotsSideGig        import getPathList
from dotsSideCar        import SideCar
from dotsControlView    import ControlView
from dotsPixItem        import PixItem
from dotsMapItem        import InitMap
from dotsBkgMaker       import *
from dotsSideShow       import SideShow
from dotsShowTime       import ShowTime
from dotsPathMaker      import PathMaker
from dotsKeysPanel      import KeysPanel
from dotsScrollPanel    import ScrollPanel
from dotsDocks          import *
from dotsAbstractBats   import Wings 

Play = ('L','R','P','S','A')

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
     
        self.control = ''         ## shared
        self.pathMakerOn = False  ## shared
        self.openPlayFile = ''    ## shared 
        self.pathList = []        ## used by animations, updated here
    
        self.canvas    = self
        self.keysPanel = KeysPanel(self)
        self.scroll    = ScrollPanel(self)
        self.pathMaker = PathMaker(self)

        self.mapper    = InitMap(self) 
        self.bkgMaker  = BkgMaker(self)
     
        self.animation = Animation(self)    
                 
        self.sideShow  = SideShow(self)  ## reads .play files    
        self.showTime  = ShowTime(self)  ## runs anything tagged as an animation 
        self.sideCar   = SideCar(self)
           
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
                
        elif not self.pathMakerOn:  ## canvas
            if self.key in CanvasStr or self.key == '':
                if self.key in Play:  ## clear screen canvas hotkeys 
                    if self.key == 'A' and len(self.scene.items()) > 0:
                        self.canvas.selectAll()
                    else:
                        self.sideShow.keysInPlay(self.key)    
                else:
                    self.sendPixKeys()      
                             
        ## send MoveKeys to PointItem selections in PathEdits
        elif self.pathMaker.drawing.pointItemsSet() == True and \
            self.pathMaker.selections and self.key in MoveKeys:  ## Keys in shared.py
                self.sendPixKeys()  ## pointItems get messaged
                          
        ## send the rest to pathMaker
        elif self.key in PathStr: 
            self.pathMaker.pathKeys(self.key)

### --------------------- event filter ---------------------- 
    def eventFilter(self, source, e):  ## used by mapper for selecting
        if not self.pathMakerOn:     
             
            if e.type() == QEvent.Type.MouseButtonPress:
                self.origin = QPoint(e.pos())
                self.mapper.clearTagGroup()  ## chks if set
                if self.key == 'cmd':        ## only used by eventFilter
                    self.mapper.clearMap()   ## set rubberband if mapset
                    self.unSelect()      
                elif self.hasHiddenPix() or self.mapper.selections:
                    if self.control not in PlayKeys:
                        self.mapper.updatePixItemPos()  
                                          
                ## show play files on right mouse click if nothing at location       
                elif e.button() == Qt.MouseButton.RightButton:
                    if len(self.scene.items()) == 0:
                        self.sideShow.loadPlay()
                        
            elif e.type() == QEvent.Type.MouseMove:
                if self.key == 'cmd' and self.origin != QPoint(0,0):
                    if self.mapper.isMapSet(): 
                        self.mapper.removeMap()
                    self.rubberBand.show()
                    self.rubberBand.setGeometry(QRect(self.origin, e.pos()).normalized())
                elif self.mapper.isMapSet() and not self.scene.selectedItems():
                    self.mapper.removeMap()
                elif self.control not in PlayKeys:  ## no animations running
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
        if 'wings' in fileName:  ## see dotsSideCar for wings
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
            elif 'frame' in pix.fileName:  ## pin it on drag and drop
                pix.setPos(0,0)
                pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)   
            self.scene.addItem(pix)
        
    def sendPixKeys(self):  ## update pixitems and pointItems thru setPixKeys
        for itm in self.scene.items():  ## used with lasso to move selections
            if itm.type in ('pt','pix', 'bkg'):    
                if itm.type == 'pt' or itm.type == 'pix' and \
                    itm.part not in ('pivot','left','right'):  ## 06-23-23
                    itm.setPixKeys(self.key)
                elif itm.type == 'bkg':  
                    itm.setPixKeys(self.key)
            elif itm.zValue() <= common['pathZ']:
                break
        if self.mapper.isMapSet(): 
            self.mapper.updateMap()

    def togglePixLocks(self, key):
        if self.control == '': 
            return 
        stub = '' 
        for pix in self.scene.items(): 
            if pix.type == 'pix':
                if pix.anime != None and \
                    pix.anime.state() == QAbstractAnimation.State.Running:
                    return 
                if key == 'R': 
                    pix.locked = True
                    stub = 'all'
                elif key == 'U': 
                    pix.locked = False
                    stub = 'all'
                elif key == 'L' and pix.isSelected():
                    pix.togglelock()  ## wait to toggleTagItems
                    stub = 'select'
            elif pix.zValue() <= common['pathZ']:
                break
        self.mapper.clearMap()
        self.mapper.toggleTagItems(stub)
                  
    def exit(self):
        self.clear() 
        self.dots.closeAll()
        QTimer.singleShot(20, self.dots.close)   
                    
    def clear(self):  ## do this before exiting app  
        if self.control != '':
            self.showTime.stop('clear')
            
        self.mapper.clearMap()               
        self.sideCar.clearWidgets()
         
        if self.sideShow.demoAvailable:   
            self.sideShow.snakes.delSnakes()                     
            self.sideShow.demoMenu.closeDemoMenu() 
            
        self.sideShow.screenMenu.closeScreenMenu()
               
        self.pathMaker.pathMakerOff()
        self.pathMaker.pathChooserOff()
  
        if not self.dots.Vertical:
            self.bkgMaker.disableBkgBtns()   
      
        self.btnAddBkg.setEnabled(True)                  
        self.dots.statusBar.clearMessage()
        self.pixCount = 0  ## set it to match sideshow
        self.sideCar.gridGroup = None
        self.openPlayFile = ''
        self.scene.clear()
        gc
           
    def loadSprites(self):
        self.sideCar.enablePlay()
        self.scroll.loadSprites()
 
    def selectAll(self):
        for pix in self.scene.items():
            if pix.type in ('pix', 'shadow'):
                pix.setSelected(True)
                pix.isHidden = False
            elif pix.zValue() <= common['pathZ']:
                break

    def unSelect(self):
        self.mapper.clearMap()
        for itm in self.scene.items():
            if itm.zValue() <= common['pathZ']:
                break     
            itm.setSelected(False)  
            if itm.type == 'pix':
               itm.isHidden = False 
    
### --------------------------------------------------------
    def deleteSelected(self):  ## self.pathMakerOn equals false
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
        if k > 0: self.sideCar.enablePlay()  ## stop it - otherwise it's hung
        gc.collect()
    
    def flopSelected(self):    
        if not self.pathMakerOn:
            for pix in self.scene.items():
                if pix.type == 'pix':
                    if pix.isSelected() or pix.isHidden:
                        if pix.flopped:
                            pix.setMirrored(False)
                        else:
                            pix.setMirrored(True)
                elif pix.zValue() <= common['pathZ']:
                    break

    def hasHiddenPix(self):
        for pix in self.scene.items():
            if pix.type == 'pix'and pix.part not in ('pivot', 'left','right'):
                if pix.isHidden: 
                    return True  ## found one
            elif pix.zValue() <= common['pathZ']:
                break
        return False

    ## added dlbclk if hidden to re-select ##
    def hideSelected(self): 
        ## if self.mapper.mapSet and self.hasHiddenPix():  
        self.mapper.removeMap()  ## also updates pix.pos()
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.part not in ('pivot', 'left','right'):
                if pix.isSelected():
                    pix.setSelected(False)
                    pix.isHidden = True
                elif pix.isHidden:
                    pix.setSelected(True)
                    pix.isHidden = False
            elif pix.zValue() <= common['pathZ']:
                break
                       
### --------------------------------------------------------
    def contextMenuEvent(self, e):
        if not self.scene.selectedItems():
            return
        menu = QMenu(self)               
        alst = sorted(AnimeList)
        
        ## basing pathlist on what's in the directory
        self.pathList = getPathList(True)  ## names only
        rlst = sorted(self.pathList)     
        alst.extend(['Random'])  
              
        menu.addAction('Animations and Paths')
        menu.addSeparator()   
        
        for anime in alst:
            action = menu.addAction(anime)
            action.triggered.connect(
                lambda chk, anime=anime: self.setAnimationTag(anime))
        menu.addSeparator()
        for anime in rlst:
            action = menu.addAction(anime)
            action.triggered.connect(
                lambda chk, anime=anime: self.setAnimationTag(anime))
        menu.addSeparator()
        anime = 'Clear Tags'
        action = menu.addAction(anime)
        action.triggered.connect(
            lambda chk, anime=anime: self.setAnimationTag(anime))
        menu.exec(e.globalPos())  ## except for pyside
    
    def setAnimationTag(self, tag):
        if self.mapper.tagSet and tag == 'Clear Tags':
            self.mapper.clearTagGroup()
        for pix in self.scene.selectedItems(): 
            if pix.type != 'pix':
                continue
            if tag == 'Clear Tags':
                pix.tag = ''
            else:
                pix.tag = tag
            pix.anime = None        ## set by play
            pix.setSelected(False)  ## when tagged 
        if self.mapper.isMapSet(): 
            self.mapper.removeMap()

### -------------------- dotsStoryBoard --------------------


