import random
import os

from os import path

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
from dotsPathMaker   import PathMaker

Loops = ('L','R','P','S')
PlayKeys = ('resume','pause')

## -- for testing and comparison ----------------
# from pubsub  import pub      # PyPubSub - required

### -------------------- dotsDropCanvas --------------------
''' dotsDropCanvas: where everything comes together, includes context 
    menu and screen handling for selecting screen objects '''
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
    
        self.mapper    = InitMap(self) 
        self.initBkg   = InitBkg(self)
        self.pathMaker = PathMaker(self)
   
        self.sideCar   = SideCar(self) 
        self.animation = Animation(self)    
        self.sideShow  = SideShow(self)
        
        self.scene.setSceneRect(0, 0,
            common["ViewW"],
            common["ViewH"])

        self.setFixedSize(common["ViewW"]+2,
            common["ViewH"]+2)

        self.key = ''
        self.pixCount = 0
       
        self.origin = QPoint(0,0)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
 
        self.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

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
                else:
                    self.sendPixKeys()
        elif self.key in PathStr:    ## pathMaker
            self.pathMaker.pathKeys(self.key)

        # pub.sendMessage('setKeys', key=key)  ## pypubsub solution   
        # if used - requires some work to coordinate with mapper
        # if self.mapper.mapSet: ## already in sendPixKeys
        #     self.mapper.updateMap()  ## redraw mapper

### -------------- the annoyance starts here ---------------
    ''' Problem: Starting a new path drawing session, by typing 'N' in 
    pathMaker will immeadiately start drawing without having to register a 
    mousePress event if entered after displaying pointItems or if 
    started after either running an animation or pixtest. 
        The mouse events used by the pathMaker newPath functions no-longer respond -
    it doesn't stop drawing. Annoying but not fatal. I'm pretty sure the problem 
    is with the eventFilter in DrawingWidget though scene ownership may also be 
    involved. 
        The one thing animations, pixtext, and pointItems all have in common is 
    they all add and delete graphicItems to and from the scene - which should 
    be owned by dropCanvas, at least that's the idea.  Hope that helps.
        I may want to add additional pathMaker like classes/fearures later and 
    knowing how to share the canvas would be useful - unless there's an 
    another way to do this.  Many thanks in advance ..'''
### --------------------------------------------------------
    def eventFilter(self, source, e):   ## mapper controls - this appears to work
        if not self.pathMakerOn:        ## correctly
    
            if e.type() == QEvent.MouseButtonPress:
                self.origin = QPoint(e.pos())
                self.mapper.clearTagGroup()   ## chks if set

                if self.key == 'cmd':  ## only used by eventFilter
                    self.mapper.clearMap()    ## set rubberband if mapset
                    self.unSelect()

                elif self.hasHiddenPix() or self.mapper.selections:
                    if self.control not in PlayKeys:
                        self.mapper.updatePixItemPos()

            elif e.type() == QEvent.MouseMove:
    
                if self.key == 'cmd' and self.origin != QPoint(0,0):
                    if self.mapper.isMapSet(): 
                        self.mapper.removeMap()
                    self.rubberBand.show()
                    self.rubberBand.setGeometry(QRect(self.origin, 
                        e.pos()).normalized())

                elif self.mapper.isMapSet() and not self.scene.selectedItems():
                    self.mapper.removeMap()

                elif self.control not in PlayKeys:  ## no animations running
                    self.mapper.updatePixItemPos()  ## costly but necessary 

            elif e.type() == QEvent.MouseButtonRelease:
    
                if self.mapper.isMapSet() == False:
                    self.rubberBand.hide()  ## supposes something is selected
                    self.mapper.addSelectionsFromCanvas() 

                if self.key == 'cmd'and self.mapper.isMapSet():
                    self.setKeys('')

                if self.mapper.isMapSet() and not self.scene.selectedItems():
                    self.mapper.removeMap()

                self.mapper.updatePixItemPos()  
 
            elif e.type() == QEvent.MouseButtonDblClick:
                ## to preseve selections dblclk on an selection otherwise it 
                ## will unselect all - possibly a default as it works the 
                ## same as single click outside the map area 
    
                if self.mapper.selections or self.hasHiddenPix():
                    if self.mapper.isMapSet():
                        self.mapper.removeMap()
                        self.setKeys('noMap')  
         
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
        if self.mapper.isMapSet(): 
            self.mapper.updateMap()

    def togglePixLocks(self, key):
        stub = ''
        for pix in self.scene.items(): 
            if pix.type == 'pix':
                if key == 'R': 
                    pix.locked = True
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
            del pix
        self.anySprites()  ## flip play keys

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
        if self.mapper.isMapSet(): 
            self.mapper.removeMap()

### -------------------- dotsDropCanvas --------------------
