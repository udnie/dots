import random

from PyQt5.QtCore    import pyqtSignal, QAbstractAnimation
from PyQt5.QtWidgets import QMenu, QRubberBand, QGraphicsScene,\
                            QGraphicsItemGroup
                      
from dotsShared      import common, CanvasStr, PathStr

from dotsAnimation   import *
from dotsSideGig     import MsgBox, TagIt, getPathList
from dotsSideCar     import SideCar
from dotsControlView import ControlView
from dotsPixItem     import PixItem
from dotsMapItem     import InitMap
from dotsBkgItem     import *
from dotsSideShow    import SideShow
from dotsAnimation   import AnimeList
from dotsPathMaker   import *

Loops = ('L','R','P','S')
PlayKeys = ('resume','pause')

## -- for testing and comparison ----------------
# from pubsub  import pub      # PyPubSub - required

### -------------------- dotsDropCanvas --------------------
''' dotsDropCanvas: where everything comes together, includes context 
    menu and screen handling for selecting screen objects '''
### --------------------------------------------------------
class DropCanvas(QWidget):

    def __init__(self, parent):
        super().__init__()

        self.dots  = parent 
        self.scene = QGraphicsScene(self)
        self.view  = ControlView(self)

        self.chooser = None       ## placeholder for popup_widget   
        self.control = ''         ## shared
        self.pathMakerOn = False  ## shared
        self.openPlayFile = ''    ## shared 
        self.pathList = []        ## used by animations, updated here

        self.pathMaker = PathMaker(self)
        self.mapper    = InitMap(self) 
        self.sideCar   = SideCar(self) 

        self.animation = Animation(self)
        self.sideShow  = SideShow(self)
        self.initBkg   = InitBkg(self)
        
        self.scene.setSceneRect(0, 0,
            common["ViewW"],
            common["ViewH"])

        self.setFixedSize(common["ViewW"]+2,
            common["ViewH"]+2)

        self.key = ''
        self.pixCount = 0

        self.origin = QPoint(0,0)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
 
        self.view.viewport().installEventFilter(self)
        self.view.keysSignal[str].connect(self.setKeys)
        
### --------------------------------------------------------
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
                else:
                    self.sendPixKeys()
        elif self.key in PathStr:    ## pathMaker
            self.pathMaker.pathKeys(self.key)

        # pub.sendMessage('setKeys', key=key)  ## pypubsub solution   
        # if used - requires some work to coordinate with mapper
        # if self.mapper.mapSet: ## already in sendPixKeys
        #     self.mapper.updateMap()  ## redraw mapper

### --------------------------------------------------------
    ''' Problem: Starting a new path drawing session, typing 'N' in 
    pathMaker, will immeadiately start drawing without having to register
    a mousePress event if entered after displaying pointItems or 
    if started after either running play or pixtest. The mouse events used 
    by the newPath functions no-longer respond - it won't stop drawing. 
    Annoying but not fatal. I'm pretty sure the problem is with the eventFilter 
    though scene ownership may also be involved. I just moved the event filter to
    pathMaker and it seems to work thought not a fix. 
    The one thing the three funtions, running an animation, pixtext, and displaying
    pointItems have in common is they all add graphicsitems to the scene and delete 
    them from the scene.  Hope that helps.
    Any help would be appreciated. I may want to add additional pathMaker
    like classes later and how to share the canvas would be useful. 
    Thanks in advance ..'''
    def eventFilter(self, source, e):     
        if not self.pathMakerOn:
            if e.type() == QEvent.MouseButtonPress:
                self.origin = QPoint(e.pos())
                self.mapper.clearTagGroup()   ## chks if set
                if self.key == 'cmd':         ## only used by eventFilter
                    self.mapper.clearMap()    ## set rubberband if mapset
                    self.unSelect()
                elif self.hasHiddenPix() and self.mapper.selections:
                    if self.control not in PlayKeys:
                        self.mapper.updatePixItemPos()
            elif e.type() == QEvent.MouseMove:
                if self.key == 'cmd' and self.origin != QPoint(0,0):
                    if self.mapper.mapSet: 
                        self.mapper.removeMap()
                    self.rubberBand.show()
                    self.rubberBand.setGeometry(QRect(self.origin, 
                        e.pos()).normalized())
                elif self.mapper.mapSet and not self.scene.selectedItems():
                    self.mapper.removeMap()
                elif self.control not in PlayKeys:  ## animations running
                    self.mapper.updatePixItemPos()  ## costly but necessary 
            elif e.type() == QEvent.MouseButtonRelease:
                if self.mapper.mapSet == False:
                    self.rubberBand.hide()  ## supposes something is selected
                    self.mapper.addSelectionsFromCanvas() 
                elif self.mapper.mapSet and self.key == 'cmd':
                    self.setKeys('')
                elif self.hasHiddenPix() and self.key != 'cmd':
                    self.mapper.removeMap()
                elif self.mapper.mapSet and not self.scene.selectedItems():
                    self.mapper.removeMap()
            elif e.type() == QEvent.MouseButtonDblClick and self.key != 'cmd':
                ## to preseve selections dblclk on an selection otherwise it 
                ## will unselect all - possibly a default as it works the 
                ## same as single click outside the map area 
                if self.mapper.selections or self.hasHiddenPix():
                    if self.mapper.mapSet:
                        self.mapper.removeMap()
                        self.setKeys('noMap')  
            return False
        return QWidget.eventFilter(self, source, e)
    
### --------------------------------------------------------
    ## set in drag/drop for id and in pixitem to clone itself
    def addPixItem(self, imgFile, x, y, clone, mirror):    
        self.pixCount += 1  
        pix = PixItem(imgFile, self.pixCount, x, y, self, mirror)
        if clone != None: ## clone it
            self.sideCar.transFormPixItem(pix,
                clone.rotation,
                clone.scale * random.randrange(95, 105)/100.0)
        else:
            if 'frame' in pix.fileName: ## pin it on dnd
                pix.setPos(0,0)
                pix.setFlag(QGraphicsPixmapItem.ItemIsMovable, False)
            self.scene.addItem(pix)
        
    def sendPixKeys(self):  ## update pixitems thru setPixKeys
        for pix in self.scene.items(): 
            if pix.type == 'pix':
                pix.setPixKeys(self.key)
            elif pix.zValue() <= common["pathZ"]:
                break
        if self.mapper.mapSet: 
            self.mapper.updateMap()

    def exit(self):
        self.clear()
        self.dots.close()

    def clear(self):
        if self.pathMakerOn:
            self.pathMaker.pathMakerOff()
        self.pathMaker.pathChooserOff()
        self.sideShow.stop('clear')
        self.initBkg.disableBkgBtns()
        self.dots.statusBar.clearMessage()
        self.mapper.clearMap()
        self.dots.btnAddBkg.setEnabled(True)
        self.pixCount = 0
        self.sideCar.gridSet = False
        self.openPlayFile = ''
        self.scene.clear()

    def loadSprites(self):
        self.sideShow.enablePlay()
        self.dots.scrollpanel.loadSprites()
 
    def selectAll(self):
        for pix in self.scene.items():
            if pix.type == 'pix':
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
            elif pix.zValue() <= common["pathZ"]:
                break
    
### --------------------------------------------------------
    def deleteSelected(self):   # self.pathMakerOn equals false
        self.mapper.clearMap()
        self.mapper.clearTagGroup()
        for pix in self.scene.selectedItems():
            if pix.anime != None and \
                pix.anime.state() == QAbstractAnimation.Running:
                pix.anime.stop()  
            pix.deletePix()
        self.anySprites()

    def anySprites(self):
        for pix in self.scene.items():
            if pix.type == 'pix': ## still some left
                break
            elif pix.zValue() <= common["pathZ"]:
                self.sideShow.enablePlay()
    
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
        # if self.mapper.mapSet and self.hasHiddenPix():  
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
        for pix in self.scene.items():
            print(pix.zValue())
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
        menu.exec_(e.globalPos())
    
    def setAnimationTag(self, tag):
        if self.mapper.tagSet and tag == "Clear Tags":
            self.mapper.clearTagGroup()
        for pix in self.scene.selectedItems(): 
            if tag == "Clear Tags":
                pix.tag = ''
            else:
                pix.tag = tag
            pix.anime = None        ## set by play
            pix.setSelected(False)  ## when tagged 
        if self.mapper.mapSet: 
            self.mapper.removeMap()

### -------------------- dotsDropCanvas --------------------
