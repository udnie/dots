import random

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from dotsShared      import common

import dotsAnimation as anima

from dotsSideCar     import SideCar, MsgBox
from dotsControlView import ControlView
from dotsPixItem     import PixItem
from dotsMapItem     import InitMap
from dotsBkgItem     import *
from dotsSideShow    import SideShow
from dotsAnimation   import animeList, pathList

## -- for testing and comparison ----------------
# from pubsub  import pub      # PyPubSub - required

mapStr = ":,\",<,>,{,},-,+,bak,left,right,up,down,cmd,del,shift,opt"

### -------------------- dotsDropCanvas --------------------
''' dotsDropCanvas: where everything comes together, includes context 
    menu and screen handling for selecting screen objects '''
### --------------------------------------------------------
class DropCanvas(QMainWindow):

    def __init__(self, sliders, buttons, parent):
        QMainWindow.__init__(self)

        self.scene = QGraphicsScene(self)
        self.view = ControlView(self.scene, self)

        self.dots    = parent
        self.sliders = sliders 
        self.buttons = buttons

        self.sideCar  = SideCar(self)  
        self.initMap  = InitMap(self)  

        self.initBkg  = InitBkg(self)
        self.sideShow = SideShow(self)
        self.MsgBox   = MsgBox

        self.scene.setSceneRect(0, 0,
            common["viewW"],
            common["viewH"])
      
        self.gridZ = common["gridZ"]
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
        if self.key in mapStr or self.key == '':
            self.sendPixKeys()
            # pub.sendMessage('setKeys', key=key)  ## pypubsub solution
            # if self.initMap.mapSet: ## already in sendPixKeys
            #     self.initMap.updateMap()  ## redraw mapper

    def eventFilter(self, source, e): ## handles mostly mapping selections
        if source is self.view.viewport():
            self.scene.clearFocus()
            if e.type() == QEvent.MouseButtonPress: 
                self.origin = QPoint(e.pos())
                self.sideShow.clearTagItems()
                if self.key == 'cmd':
                    self.initMap.updatePixItemPos()
                    self.initMap.clearMap() ## set rubberband if mapset
                    self.unSelect()
                elif self.hasHiddenPix() and self.initMap.selections:
                    self.initMap.updatePixItemPos()
            elif e.type() == QEvent.MouseMove:
                if self.key == 'cmd' and self.origin != QPoint(0,0):
                    if self.initMap.mapSet: self.initMap.removeMap()
                    self.rubberBand.show()
                    self.rubberBand.setGeometry(QRect(self.origin, 
                        e.pos()).normalized())
                elif self.initMap.mapSet and not self.scene.selectedItems():
                    self.initMap.removeMap()
                else:
                    self.initMap.updatePixItemPos()  ## costly but necessary
            elif e.type() == QEvent.MouseButtonRelease:
                if self.initMap.mapSet == False:
                    self.rubberBand.hide()
                    self.initMap.addSelectionsFromCanvas()
                elif self.initMap.mapSet and self.key == 'cmd':
                    self.setKeys('')
                elif self.hasHiddenPix() and self.key != 'cmd':
                    self.initMap.removeMap()
                elif self.initMap.mapSet and not self.scene.selectedItems():
                    self.initMap.removeMap()
            elif e.type() == QEvent.MouseButtonDblClick and self.key != 'cmd':
                ## to preseve selections dblclk on an selection otherwise it 
                ## will unselect all - possibly a default as it works the 
                ## same as single click outside the map area 
                if self.initMap.selections or self.hasHiddenPix():
                    if self.initMap.mapSet:
                        self.initMap.removeMap()
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
                clone.scale * random.randrange(80, 120)/100.0)
        else:
            self.scene.addItem(pix)

    def sendPixKeys(self):  ## update pixitems thru setPixKeys
        for pix in self.scene.items(): 
            if pix.type == 'pix':
                pix.setPixKeys(self.key)
            elif pix.zValue() <= self.gridZ:
                break
        if self.initMap.mapSet: 
            self.initMap.updateMap()

    def clear(self):
        if self.scene.items():
            self.selectAll()
            self.sideShow.stop('clear')
            self.initMap.clearMap()
            self.scene.clear()
            self.pixCount = 0
            self.disableSliders()
            self.buttons.btnBkgFiles.setEnabled(True)
            self.sideCar.gridSet = False
            self.sideCar.openPlayFile = ''

    def disableSliders(self):
        self.sliders.enableSliders(False)
        self.buttons.btnSetBkg.setEnabled(False)
        self.buttons.btnSave.setEnabled(False)

    def loadSprites(self):
        self.sideShow.enablePlay()
        self.dots.scrollpanel.loadSprites()
 
    def selectAll(self):
        for pix in self.scene.items():
            if pix.type == 'pix':
                pix.setSelected(True)
                pix.isHidden = False
            elif pix.zValue() <= self.gridZ:
                break

    def unSelect(self):
        self.initMap.clearMap()
        for pix in self.scene.items():
            if pix.type == 'pix':
                pix.isHidden = False
                pix.setSelected(False)
                pix.clearFocus()
            elif pix.zValue() <= self.gridZ:
                break
       
    def deleteSelected(self):
        self.initMap.clearMap()
        for pix in self.scene.selectedItems():
            pix.deletePix()
    
    def flopSelected(self):    
        for pix in self.scene.items():
            if pix.type == 'pix':
                if pix.isSelected() or pix.isHidden:
                    if pix.flopped:
                        pix.setMirrored(False)
                    else:
                        pix.setMirrored(True)
            elif pix.zValue() <= self.gridZ:
                break

    ## added dlbclk if hidden to re-select ##
    def hideSelected(self): 
        # if self.initMap.mapSet and self.hasHiddenPix():  
        self.initMap.removeMap()  ## also updates pix.pos()
        for pix in self.scene.items():
            if pix.type == 'pix':
                if pix.isSelected():
                    pix.setSelected(False)
                    pix.isHidden = True
                elif pix.isHidden:
                    pix.setSelected(True)
                    pix.isHidden = False
            elif pix.zValue() <= self.gridZ:
                break

    def hasHiddenPix(self):
        for pix in self.scene.items():
            if pix.type == 'pix':
                if pix.isHidden: 
                    return True  ## found one
            elif pix.zValue() <= self.gridZ:
                break
        return False

    def itemsPixcount(self):
        return sum(
            pix.type == 'pix' 
            for pix in self.scene.items()
        )

    def ZDump(self):
        for pix in self.scene.items():
            if pix.zValue() != self.gridZ:  ## skip grid zvalue
                print(pix.type + "  " + str(pix.zValue()))
        print("bkg: " + str(self.initBkg.hasBackGround()))

    def contextMenuEvent(self, e):
        if not self.scene.selectedItems():
            return
        menu = QMenu(self)
        menu.setStyleSheet("QMenu {\n"
            "font-size: 14px;\n"
            "border: 1.5px solid rgb(125,125,125);\n"
            "}")
        alst = sorted(animeList)
        rlst = sorted(pathList)    
        alst.extend(["Random"])
        for anime in alst:
            action = menu.addAction(anime)
            action.triggered.connect(
                lambda chk, anime=anime: self.sideShow.setAction(anime))
        menu.addSeparator()
        for anime in rlst:
            action = menu.addAction(anime)
            action.triggered.connect(
                lambda chk, anime=anime: self.sideShow.setAction(anime))
        menu.addSeparator()
        anime = "Clear Tags"
        action = menu.addAction(anime)
        action.triggered.connect(
            lambda chk, anime=anime: self.sideShow.setAction(anime))
        menu.exec_(e.globalPos())
    
### -------------------- dotsDropCanvas --------------------
