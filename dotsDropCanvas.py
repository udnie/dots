from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

import dotsQt

from dotsSideCar      import SideCar, MsgBox
from dotsControlView  import ControlView
from dotsPixItem      import PixItem
from dotsMapItem      import InitMap
from dotsBkgItem      import *

## ----- for testing and comparison
# from pubsub  import pub      # PyPubSub - required

mapStr = ":,\",<,>,{,},-,+,left,right,up,down,cmd,shift,retn,opt"

### -------------------- dotsDropCanvas --------------------
class DropCanvas(QMainWindow):

    def __init__(self, sliders, buttons, parent):
        QMainWindow.__init__(self)

        self.parent = parent
        self.sliders = sliders 
        self.buttons = buttons

        self.initMap = InitMap(self)
        self.sideCar = SideCar(self)
        self.initBkg = InitBkg(self)
        self.MsgBox  = MsgBox

        self.scene = QGraphicsScene(self)
        self.view = ControlView(self.scene, self)

        self.shared = dotsQt.Shared()
        self.gridZ = self.shared.gridZ

        self.scene.setSceneRect(0, 0,
            self.shared.viewW,
            self.shared.viewH)
      
        self.key = ''
        self.pixCount = 0
 
        self.origin = QPoint(0,0)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)

        self.view.viewport().installEventFilter(self)
        self.view.keysSignal[str].connect(self.setKeys)

    def enterEvent(self, e):
        self.view.setFocus()

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
            if e.type() == QEvent.MouseButtonPress:
                if self.key == 'cmd':
                    self.initMap.updatePixItemPos()
                    self.initMap.clearMap()
                    self.unSelect()
                    self.origin = QPoint(e.pos())
                    self.rubberBand.show()
                elif self.hasHiddenPix() and len(self.initMap.selections) > 0:
                    self.initMap.updatePixItemPos()
            elif e.type() == QEvent.MouseMove:
                if self.key == 'cmd' and self.origin != QPoint(0,0):
                    self.rubberBand.setGeometry(QRect(self.origin, 
                        e.pos()).normalized())
                elif self.initMap.mapSet and len(self.scene.selectedItems()) == 0:
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
                elif self.initMap.mapSet and len(self.scene.selectedItems()) == 0:
                    self.initMap.removeMap()
            elif e.type() == QEvent.MouseButtonDblClick and self.key != 'cmd':
                ## to preseve selections dblclk on an selection otherwise it 
                ## will unselect all - possibly a default as it works the 
                ## same as single click outside the map area 
                if len(self.initMap.selections) > 0 or self.hasHiddenPix():
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
                clone.scale * 1.0)
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
 
    def selectAll(self):
        for pix in self.scene.items():
            if pix.type == 'pix':
                pix.setSelected(True)
                pix.isHidden = False
            elif pix.zValue() <= self.gridZ:
                break

    def unSelect(self):
        for pix in self.scene.items():
            if pix.type == 'pix':
                pix.isHidden = False
                pix.setSelected(False)
            elif pix.zValue() <= self.gridZ:
                break
        self.initMap.clearMap()

    def deleteSelected(self):
        for pix in self.scene.selectedItems():
            if pix.type == 'pix':
                self.scene.removeItem(pix)
            elif pix.zValue() <= self.gridZ:
                break
        self.initMap.clearMap()

    def flopSelected(self): 
        if self.hasHiddenPix() or self.scene.selectedItems():    
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
        if self.initMap.mapSet and self.hasHiddenPix():        
            self.initMap.removeMap()

    def hasHiddenPix(self):
        for pix in self.scene.items():
            if pix.type == 'pix':
                if pix.isHidden: 
                    return True  ## found one
            elif pix.zValue() <= self.gridZ:
                break
        return False

    def toFront(self, inc): ## used in setting zValue for pix and map 
        first = 0.0 
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.zValue() > first:
                first = pix.zValue()
                break
            elif pix.zValue() <= self.gridZ:
                break
        return inc + first

    def lastZval(self, str):
        last = 100000.0
        for itm in self.scene.items():
            if itm.type == str and itm.zValue() < last:
                last = itm.zValue()
        return last

    def ZDump(self):
        for pix in self.scene.items(Qt.AscendingOrder):
            if pix.zValue() != self.gridZ:  ## skip grid zvalue
                print(pix.type + "  " + str(pix.zValue()))
        print("bkg: " + str(self.initBkg.hasBackGround()))

### -------------------- dotsDropCanvas --------------------
