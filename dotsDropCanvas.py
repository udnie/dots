import random

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from dotsShared      import common, MapStr, PathStr

from dotsAnimation   import *
from dotsSideCar     import SideCar, MsgBox
from dotsControlView import ControlView
from dotsPixItem     import PixItem
from dotsMapItem     import InitMap
from dotsBkgItem     import *
from dotsSideShow    import SideShow
from dotsAnimation   import AnimeList
from dotsPathMaker   import *

## -- for testing and comparison ----------------
#from pubsub  import pub      # PyPubSub - required

### -------------------- dotsDropCanvas --------------------
''' dotsDropCanvas: where everything comes together, includes context 
    menu and screen handling for selecting screen objects '''
### --------------------------------------------------------
class DropCanvas(QWidget):

    pathMakerSignal = pyqtSignal([str])

    def __init__(self, parent):
        QMainWindow.__init__(self)

        self.scene = QGraphicsScene(self)
        self.view  = ControlView(self.scene, self)

        self.dots = parent
        self.sliders = self.dots.sliderpanel
       
        self.chooser = None       ## placeholder for popup_widget
        
        self.control = ''         ## shared
        self.pathMakerOn = False  ## shared
        self.openPlayFile = ''    ## shared 

        self.pathList = []        ## used also by animations, updated here

        self.mapper    = InitMap(self) 
        self.sideCar   = SideCar(self) 
        self.pathMaker = PathMaker(self, self.sliders)

        self.animation = Animation(self)
        self.sideShow  = SideShow(self)
        self.initBkg   = InitBkg(self, MsgBox)
        
        self.scene.setSceneRect(0, 0,
            common["ViewW"],
            common["ViewH"])

        self.pathZ = common["pathZ"]
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
        if not self.pathMakerOn:
            if self.key in MapStr or self.key == '':
                if self.key in ('L','O','P', 'S'):  ## this can change
                    self.sideShow.keysInPlay(self.key)
                elif self.key == 'C':
                    self.clear()
                else:
                    self.sendPixKeys()

            # pub.sendMessage('setKeys', key=key)  ## pypubsub solution   
            # if used - requires some work to coordinate with mapper
            # if self.mapper.mapSet: ## already in sendPixKeys
            #     self.mapper.updateMap()  ## redraw mapper

        elif self.key in PathStr:
            self.pathMakerSignal[str].emit(self.key)

### --------------------------------------------------------
    def eventFilter(self, source, e): ## handles mostly mapping selections
        if source is self.view.viewport():
            self.scene.clearFocus()
            if e.type() == QEvent.MouseButtonPress: 
                self.origin = QPoint(e.pos())
                self.mapper.clearTagGroup()
                if self.key == 'cmd':   ## only used by eventFilter
                    if not self.pathMakerOn:  ## otherwise shows in pathmaker  
                        self.mapper.updatePixItemPos()
                        self.mapper.clearMap() ## set rubberband if mapset
                        self.unSelect()
                elif self.hasHiddenPix() and self.mapper.selections:
                    self.mapper.updatePixItemPos()
            elif e.type() == QEvent.MouseMove:
                if self.key == 'cmd' and self.origin != QPoint(0,0):
                    if not self.pathMakerOn: ## ditto
                        if self.mapper.mapSet: self.mapper.removeMap()
                        self.rubberBand.show()
                        self.rubberBand.setGeometry(QRect(self.origin, 
                            e.pos()).normalized())
                elif self.mapper.mapSet and not self.scene.selectedItems():
                    self.mapper.removeMap()
                else:
                    self.mapper.updatePixItemPos()  ## costly but necessary
            elif e.type() == QEvent.MouseButtonRelease:
                if self.mapper.mapSet == False:
                    self.rubberBand.hide()
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
        return QWidget.eventFilter(self, source, e)

### --------------------------------------------------------
    ## set in drag/drop for id and in pixitem to clone itself
    def addPixItem(self, imgFile, x, y, clone, mirror):    
        self.pixCount += 1  
        pix = PixItem(imgFile, self.pixCount, x, y, self, mirror)
        if clone != None: 
            self.sideCar.transFormPixItem(pix,
                clone.rotation,
                clone.scale * random.randrange(95, 105)/100.0)
        else:
            self.scene.addItem(pix)

    def sendPixKeys(self):  ## update pixitems thru setPixKeys
        for pix in self.scene.items(): 
            if pix.type == 'pix':
                pix.setPixKeys(self.key)
            elif pix.zValue() <= self.pathZ:
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
        self.sideShow.stop('stop')
        self.initBkg.disableSliders()
        self.dots.statusBar.clearMessage()
        self.mapper.clearMap()
        self.dots.btnBkgFiles.setEnabled(True)
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
            elif pix.zValue() <= self.pathZ:
                break

    def unSelect(self):
        self.mapper.clearMap()
        for pix in self.scene.items():
            if pix.type == 'pix':
                pix.isHidden = False
                pix.setSelected(False)
            elif pix.zValue() <= self.pathZ:
                break
       
    def deleteSelected(self):
        if not self.pathMakerOn:
            self.mapper.clearMap()
        for pix in self.scene.selectedItems():
            if pix.anime != None and \
                pix.anime.state() == QAbstractAnimation.Running:
                continue
            else:
                pix.deletePix()
        self.anySprites()

    def anySprites(self):
        for pix in self.scene.items():
            if pix.type == 'pix': ## still some left
                break
            elif pix.zValue() <= self.pathZ:
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
                elif pix.zValue() <= self.pathZ:
                    break

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
            elif pix.zValue() <= self.pathZ:
                break

    def hasHiddenPix(self):
        for pix in self.scene.items():
            if pix.type == 'pix':
                if pix.isHidden: 
                    return True  ## found one
            elif pix.zValue() <= self.pathZ:
                break
        return False

    def itemsPixcount(self):   ## may not be used
        return sum(
            pix.type == 'pix' 
            for pix in self.scene.items()
        )

    def ZDump(self):
        for pix in self.scene.items():
            # if pix.zValue() != self.pathZ:  ## skip grid zvalue
            print(pix.zValue())
        print("bkg: " + str(self.initBkg.hasBackGround()))

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
        self.pathList = self.pathMaker.getPathList(True)  ## names only
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
                if pix.anime != None and \
                    pix.anime.state() != QAbstractAnimation.Running:
                    pix.tag = ''
            else:
                pix.tag = tag
            pix.anime = None        ## set by play
            pix.setSelected(False)  ## when tagged 
        if self.mapper.mapSet: 
            self.mapper.removeMap()

### -------------------- dotsDropCanvas --------------------
