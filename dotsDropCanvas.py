
import random
import os
import gc

from PyQt6.QtCore    import QAbstractAnimation, QTimer, QEvent, QPointF
from PyQt6.QtGui     import QTransform
from PyQt6.QtWidgets import QWidget, QMenu, QRubberBand, QGraphicsScene, \
                            QApplication
                       
from dotsShared      import common, CanvasStr, PathStr, MoveKeys, PlayKeys
from dotsAnimation   import *
from dotsSideGig     import getPathList
from dotsSideCar     import SideCar
from dotsControlView import ControlView
from dotsPixItem     import PixItem
from dotsMapItem     import InitMap
from dotsBkgItem     import *
from dotsSideShow    import SideShow
from dotsPathMaker   import PathMaker
from dotsSliderPanel import SliderPanel
from dotsScrollPanel import ScrollPanel
from dotsDocks       import *

Loops = ('L','R','P','S')

### -------------------- dotsDropCanvas --------------------
''' dotsDropCanvas: program hub/canvas, includes context menu and 
    screen handling for selecting screen objects '''
### --------------------------------------------------------
class DropCanvas(QWidget):
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()

        self.dots  = parent 
        self.scene = QGraphicsScene(self)
        self.view  = ControlView(self)

        self.control = ''         ## shared
        self.pathMakerOn = False  ## shared
        self.openPlayFile = ''    ## shared 
        self.pathList = []        ## used by animations, updated here
    
        self.slider    = SliderPanel(self)
        self.scroll    = ScrollPanel(self)
        self.pathMaker = PathMaker(self)

        self.mapper    = InitMap(self) 
        self.initBkg   = InitBkg(self)
     
        self.animation = Animation(self)    
        self.sideShow  = SideShow(self)  ## additional extentions 
        self.sideCar   = SideCar(self) 
         
        addScrollDock(self)  ## add button groups from dotsDocks
        addSliderDock(self)
        addButtonDock(self)  

        self.scene.setSceneRect(0, 0,
            common["ViewW"],
            common["ViewH"])

        self.setFixedSize(common["ViewW"]+2,
            common["ViewH"]+2)

        self.key = ''
        self.pixCount = 0
       
        self.origin = QPoint(0,0)
        self.rubberBand = QRubberBand(QRubberBand.Shape.Rectangle, self)

        self.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)
        self.view.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False) 
    
        self.view.keysSignal[str].connect(self.setKeys)    

### ---------------------- send keys -----------------------
    @pyqtSlot(str)
    def setKeys(self, key):
        self.key = key
        if self.pathMakerOn and self.key == 'C' and \
            len(self.scene.items()) == 0:
            self.clear()
            return
        if not self.pathMakerOn:  ## canvas
            if self.key in CanvasStr or self.key == '':
                if self.key in Loops:  ## canvas hotkeys
                    self.sideShow.keysInPlay(self.key)        
                elif self.key == 'C':
                    self.clear()
                elif self.key == 'K':
                    self.slider.toggleMenu()
                else:
                    self.sendPixKeys()
        ## send move keys to selected pointItems 
        elif self.pathMaker.drawing.pointItemsSet() == True and \
            self.pathMaker.selections and self.key in MoveKeys:
                self.sendPixKeys()
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
    def addPixItem(self, imgFile, x, y, clone, mirror):  
        if 'wings' in imgFile:  ## see dotsSideCar for wings
            self.sideCar.wings(x, y, '')        
        else:
            self.pixCount += 1  
            pix = PixItem(imgFile, self.pixCount, x, y, self, mirror)
                
            if clone != None:  ## clone it                    
                self.sideCar.transFormPixItem(pix,
                    clone[0],
                    clone[1] * random.randrange(95, 105)/100.0,
                    pix.alpha2)
                return
        
            elif 'frame' in pix.fileName:  ## pin it on dnd
                pix.setPos(0,0)
                pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
            
            self.scene.addItem(pix)
        
    def sendPixKeys(self):  ## update pixitems and pointItems thru setPixKeys
        for itm in self.scene.items(): 
            if itm.type in ('pt','pix'): 
                itm.setPixKeys(self.key)
            elif itm.zValue() <= common["pathZ"]:
                break
        if self.mapper.isMapSet(): 
            self.mapper.updateMap()

    def togglePixLocks(self, key):
        stub = ''
        for pix in self.scene.items(): 
            if pix.type == 'pix':
                if key == 'R': 
                    pix.locked = True
                    stub = 'all'
                elif key == 'U': 
                    pix.locked = False
                    stub = 'all'
                elif key == 'L' and pix.isSelected():
                    pix.togglelock()  ## wait to toggleTagItems
                    stub = 'select'
            elif pix.zValue() <= common["pathZ"]:
                break
        self.mapper.clearMap()
        self.mapper.toggleTagItems(stub)

    def exit(self):
        self.clear()     
        QTimer.singleShot(250, self.dots.close)

    def clear(self):  ## do this before exiting app
        self.pathMaker.pathMakerOff()
        self.pathMaker.pathChooserOff()
        self.sideCar.clearWidgets()
        self.sideShow.stop('clear')
        self.initBkg.disableBkgBtns()
        self.dots.statusBar.clearMessage()
        self.mapper.clearMap()
        self.btnAddBkg.setEnabled(True)
        self.pixCount = 0
        self.sideCar.gridGroup = None
        self.openPlayFile = ''
        self.scene.clear()
      
    def loadSprites(self):
        self.sideCar.enablePlay()
        self.scroll.loadSprites()
 
    def selectAll(self):
        for pix in self.scene.items():
            if pix.type in ('pix', 'shadow'):
                pix.setSelected(True)
                pix.isHidden = False
            elif pix.zValue() <= common["pathZ"]:
                break

    def unSelect(self):
        self.mapper.clearMap()
        for pix in self.scene.items():
            if pix.type == 'pix':
                pix.isHidden = False
                pix.setSelected(False)
            elif pix.type == 'pt':
                pix.setSelected(False)   
            elif pix.zValue() <= common["pathZ"]:
                break
    
### --------------------------------------------------------
    def deleteSelected(self):  ## self.pathMakerOn equals false
        self.mapper.clearMap()
        self.mapper.clearTagGroup()
        for pix in self.scene.selectedItems():       
            if pix.type == 'pix':  ## could be something else
                if pix.anime != None and \
                    pix.anime.state() == QAbstractAnimation.State.Running:
                    pix.anime.stop()  
                pix.setSelected(False)
                pix.deletePix()  ## deletes shadow as well 
                del pix
        self.sideCar.enablePlay()  ## stop it - otherwise it's hung
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
                elif pix.zValue() <= common["pathZ"]:
                    break

    def hasHiddenPix(self):
        for pix in self.scene.items():
            if pix.type == 'pix':
                if pix.isHidden: 
                    return True  ## found one
            elif pix.zValue() <= common["pathZ"]:
                break
        return False

    ## added dlbclk if hidden to re-select ##
    def hideSelected(self): 
        ## if self.mapper.mapSet and self.hasHiddenPix():  
        self.mapper.removeMap()  ## also updates pix.pos()
        for pix in self.scene.items():
            if pix.type == 'pix':
                if pix.isSelected():
                    pix.setSelected(False)
                    pix.isHidden = True
                elif pix.isHidden:
                    pix.setSelected(True)
                    pix.isHidden = False
            elif pix.zValue() <= common["pathZ"]:
                break

    def ZDump(self):
        return
        for pix in self.scene.items():
            print(os.path.basename(pix.fileName), pix.id, pix.zValue())
        print("bkg: " + str(self.initBkg.hasBackGround()))

### --------------------------------------------------------
    def contextMenuEvent(self, e):
        if not self.scene.selectedItems():
            return
        menu = QMenu(self)
        menu.setStyleSheet("QMenu {\n"
            "font-size: 14px;\n"
            "border: 1px solid rgb(125,125,125);\n"
            "}")
        alst = sorted(AnimeList)
        ## basing pathlist on what's in the directory
        self.pathList = getPathList(True)  ## names only
        rlst = sorted(self.pathList)    
        alst.extend(["Random"])
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
        anime = "Clear Tags"
        action = menu.addAction(anime)
        action.triggered.connect(
            lambda chk, anime=anime: self.setAnimationTag(anime))
        menu.exec(e.globalPos())
    
    def setAnimationTag(self, tag):
        if self.mapper.tagSet and tag == "Clear Tags":
            self.mapper.clearTagGroup()
        for pix in self.scene.selectedItems(): 
            if pix.type != 'pix':
                continue
            if tag == "Clear Tags":
                pix.tag = ''
            else:
                pix.tag = tag
            pix.anime = None        ## set by play
            pix.setSelected(False)  ## when tagged 
        if self.mapper.isMapSet(): 
            self.mapper.removeMap()

### -------------------- dotsDropCanvas --------------------


