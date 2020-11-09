import random

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from dotsShared      import common

from dotsAnimation   import *
from dotsSideCar     import SideCar, MsgBox
from dotsControlView import ControlView
from dotsPixItem     import PixItem
from dotsMapItem     import InitMap
from dotsBkgItem     import *
from dotsSideShow    import SideShow
from dotsAnimation   import animeList
from dotsPathMaker   import *

## -- for testing and comparison ----------------
# from pubsub  import pub      # PyPubSub - required

pathStr = "F,S,C,D,N,T,P,R,W,{,},/,!,cmd,left,right,up,down,<,>,:,\",_,+,-,="
mapStr = ":,\",<,>,{,},[,],_,+,/,left,right,up,down,cmd,del,shift,opt"

### -------------------- dotsDropCanvas --------------------
''' dotsDropCanvas: where everything comes together, includes context 
    menu and screen handling for selecting screen objects '''
### --------------------------------------------------------
class DropCanvas(QMainWindow):

    pathSignal = pyqtSignal([str])

    def __init__(self, sliders, buttons, parent):
        QMainWindow.__init__(self)

        self.scene = QGraphicsScene(self)
        self.view  = ControlView(self.scene, self)

        self.dots    = parent
        self.sliders = sliders 
        self.buttons = buttons  
      
        self.chooser = None       ## placeholder for popup_widget
        self.pathMakerOn = False  ## shared
        self.pathList = []        ## used also by animations, updated here

        self.mapper    = InitMap(self) 
        self.sideCar   = SideCar(self) 
        self.pathMaker = PathMaker(self)

        self.animation = Animation(self)
        self.sideShow  = SideShow(self)
        self.initBkg   = InitBkg(self, MsgBox)
        
        self.scene.setSceneRect(0, 0,
            common["viewW"],
            common["viewH"])

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
            if self.key in mapStr or self.key == '':
                self.sendPixKeys()
        else:
            if self.key in pathStr:
                self.pathSignal[str].emit(self.key)
      
            # pub.sendMessage('setKeys', key=key)  ## pypubsub solution
            # if self.mapper.mapSet: ## already in sendPixKeys
            #     self.mapper.updateMap()  ## redraw mapper
    
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
        if self.pathMaker.pathChooserSet:
            del self.pathMaker.chooser
        self.sideShow.stop('stop')
        self.disableSliders()     
        self.mapper.clearMap()
        self.buttons.btnBkgFiles.setEnabled(True)
        self.pixCount = 0
        self.sideCar.gridSet = False
        self.mapper.openPlayFile = ''
        self.scene.clear()

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
                pix.deletePix()
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
        alst = sorted(animeList)
        ## basing pathlist on what's in the directory
        self.pathList = self.pathMaker.getPathList(True)  ## names only
        rlst = sorted(self.pathList)    
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
