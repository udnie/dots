
import os
import os.path
import random
import json

from PyQt6.QtCore       import Qt, QPointF, QPoint, QSize, QRect, QTimer, QProcess
from PyQt6.QtGui        import QPixmap, QPen, QColor, QGuiApplication
from PyQt6.QtWidgets    import QGraphicsPixmapItem, QFileDialog, \
                                QGraphicsItemGroup, QGraphicsLineItem, \
                                QApplication, QMenu
                                                 
from dotsAnimation   import *   
from dotsShared      import common, paths
from dotsPixItem     import PixItem
from dotsSideGig     import MsgBox, getCtr
from dotsMapItem     import InitMap
from dotsScreens     import *

from vhx             import VHX

from functools       import partial

### ---------------------- dotsSideCar ---------------------
''' dotsSideCar: wings, pixTest, transFormPixitem, snapShot, 
    toggleGrid, screenMenu, and assorted small functions '''  
### --------------------------------------------------------
class SideCar:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
        self.dots = self.canvas.dots
        
        self.scene  = self.canvas.scene
        self.mapper = InitMap(self.canvas) 
  
        self.animation = Animation(self.canvas)
      
        self.gridZ = common["gridZ"] 
        self.gridGroup = None
        self.proc = None

### --------------------------------------------------------
    ''' Things to know about wings. They're brittle, don't pull on them.
    Use the bat portion to move the bat - the pivot sprite and the wing 
    are in the images folder. Main thing to know, if you need to move 
    or change an animation - do so, save it, clear and reload.
    They're still brittle but it works, even better now. '''
### --------------------------------------------------------
    def wings(self, x, y, tag):
        self.canvas.pixCount += 1         
        pivot = PixItem(paths["imagePath"] + 'bat-pivot.png', 
            self.canvas.pixCount,
            x, y,  
            self.canvas
        ) 
        pivot.part = 'pivot' 
        pivot.tag  = tag
        pivot.setZValue(pivot.zValue() + 200)
        pivot.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, True) 
        ''' magic numbers warning - results will vary - seems
            to be working for bat wings if loaded using file chooser'''    
        half = pivot.width/2     ## looking better
        height = pivot.height/5  ## good guess, close
        try:
            ## another correction -5 for y
            # pivot.setPos(pivot.x - half, pivot.y - height - 5)
            pivot.setScale(.57)
            pivot.setOriginPt() 
        except IOError:
            pass  
          
        self.canvas.pixCount += 1
        rightWing = PixItem(paths["imagePath"] + 'bat-wings.png', 
            self.canvas.pixCount,
            x-20, y-20, 
            self.canvas,
            False,
        )  ## flop it
 
        rightWing.part = 'right'
        rightWing.tag  = 'Flapper'  ## applies this animation when run
        rightWing.setZValue(rightWing.zValue() + 200)  ## reset wing zvals
        rightWing.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, False)
        rightWing.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemStacksBehindParent)
              
        self.canvas.pixCount += 1
        leftWing = PixItem(paths["imagePath"] + 'bat-wings.png', 
            self.canvas.pixCount,
            x + rightWing.width, y, 
            self.canvas,
            True
        )  ## flop it

        leftWing.part = 'left'
        leftWing.tag  = 'Flapper'
        leftWing.setZValue(leftWing.zValue() + 200)
        leftWing.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, False) 
        leftWing.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemStacksBehindParent)
       
        ## center wings around pivot
        rightWing.setPos(half+1, height-2)
        leftWing.setPos(-leftWing.width+(half+5), height)

        ''' if there's a better way to bind these I'd like to know '''
        rightWing.setParentItem(pivot)  
        leftWing.setParentItem(pivot)

        self.scene.addItem(pivot) 

### --------------------- end wings ------------------------
    def transFormPixItem(self, pix, rotation, scale, alpha2):         
        op = QPointF(pix.width/2, pix.height/2)  
        pix.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        pix.setTransformOriginPoint(op)
              
        pix.rotation = rotation
        pix.scale    = scale 
        pix.alpha2   = alpha2
        
        pix.setRotation(pix.rotation)         
        pix.setScale(pix.scale)     
        pix.setOpacity(pix.alpha2)
                                                      
        self.scene.addItem(pix)
            
### --------------------------------------------------------
    def pixTest(self):
        if not self.canvas.pathMakerOn:  
            self.canvas.pixCount = self.mapper.toFront()
            for _ in range(10):
                self.canvas.pixCount += 1
                pix = PixItem(paths["spritePath"] + 'apple.png', self.canvas.pixCount, 0, 0, 
                        self.canvas)
                x = int(constrain(self.xy(common["ViewW"]), pix.width, common["ViewW"], 
                        pix.width * -common["factor"]))
                y = int(constrain(self.xy(common["ViewH"]), pix.height, common["ViewH"],
                        pix.height * -common["factor"]))
                pix.x, pix.y = x, y
                pix.setPos(x,y)
                rotation = random.randrange(-5, 5) * 5
                scale = random.randrange(90, 110)/100.0
                self.transFormPixItem(pix, rotation, scale, 1.0)
                             
### --------------------------------------------------------                       
    def screenMenu(self):
        menu = QMenu(self.canvas)    
        menu.addAction(' Screen Formats')
        menu.addSeparator()
        for screen in screens.values():
            action = menu.addAction(screen)
            menu.addSeparator()
            action.triggered.connect(lambda chk, screen=screen: self.clicked(screen)) 
        menu.move(getCtr(-125,-115)) 
        menu.setFixedSize(150, 252)
        menu.show()
    
    def clicked(self, screen):
        for key, value in screens.items():
            if value == screen:  ## singleshot needed for menu to clear
                QTimer.singleShot(200, partial(self.displayChk, key))
                break
            
    def displayChk(self, key):
        p = QGuiApplication.primaryScreen().availableGeometry()
        if key in MaxScreens and p.width() < MaxWidth:  ## current screen width < 1680
            self.exceedsMsg() 
            return               
        self.canvas.clear()       
        self.canvas.dots.switch(key)
        
    def exceedsMsg(self):  ## in storyBoard on start       ## use getCtr with MsgBox
        MsgBox('Selected Format Exceeds Current Display Size', 8, getCtr(-200,-145)) 
 
### -------------------------------------------------------- 
    def startProcess(self):
        if self.proc is None:
            pass
            # self.proc = QProcess()  ## thanks to Martin Fitzpatrick
            # self.proc.finished.connect(self.processFinished)
            # self.proc.start("python3", ["vhx.py"])  ## works in vscode
            ## doesn't work- easier to pin vhx.app to the Desktop dock
            ## self.proc.start('python3', ['/full-path..../vhx.app']) 
          
    def processFinished(self):
        pass
        # self.proc.close()
        # self.proc = None
        
### --------------------------------------------------------      
    def snapShot(self):
        if self.hasBackGround() or self.scene.items():
            self.canvas.unSelect()  ## turn off any select borders
            if self.canvas.pathMakerOn == False:
                if self.mapper.isMapSet():
                    self.mapper.removeMap()
            if self.canvas.openPlayFile == '':
                snap = "dots_" + self.snapTag() + ".jpg"
            else:
                snap = os.path.basename(self.canvas.openPlayFile)
                snap = snap[:-5] + ".jpg"
                
            if snap[:4] != "dots":  ## always ask unless
                Q = QFileDialog()
                f = Q.getSaveFileName(self.canvas, paths["snapShot"],
                    paths["snapShot"] + snap)
                Q.accept()
        
                if not f[0]:
                    return
                elif not f[0].lower().endswith('.jpg'):
                    MsgBox("Wrong file extention - use '.jpg'", 5)
                    return
                snap = os.path.basename(f[0])
            pix = self.canvas.view.grab(QRect(QPoint(0,0), QSize()))
            pix.save(paths["snapShot"] + snap,
                format='jpg',
                quality=100)        
            MsgBox("Saved as " + snap, 3)
        
    def hasBackGround(self):
        for itm in self.scene.items(Qt.SortOrder.AscendingOrder):
            if itm.type == 'bkg':
                return True
        return False
    
    def snapTag(self):
        return str(random.randrange(1000,9999)) + chr(random.randrange(65,90))
                             
### --------------------------------------------------------           
    def toggleMenu(self):
        self.canvas.slider.toggleMenu()  ## no direct path from controlView
                                                                                           
    def clearWidgets(self):                             
        for widget in QApplication.allWidgets():  ## note!!
            if widget.accessibleName() == 'widget':  ## shadow and pixitems widgets
                widget.close()
        if self.canvas.pathMakerOn: self.canvas.pathMaker.pathChooserOff()
        
    def clearOutlines(self):
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.shadow:
                pix.shadowMaker.outline.hide()
                pix.shadowMaker.hidePoints() 
                                                                                                            
    def toggleOutlines(self):  ## runs from shift-H
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.shadow:
                pix.shadowMaker.toggleOutline()
                                                                                                                                 
    def hideSelected(self):  ## with shadows
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.shadow: 
                if pix.isSelected():
                    pix.hide() 
                elif not pix.isVisible():
                    pix.show()       
                    pix.setSelected(True)
                                                                               
### --------------------------------------------------------
    def toggleGrid(self):
        if self.gridGroup:
            self.scene.removeItem(self.gridGroup)
            self.gridGroup = None
        else: 
            self.gridGroup = QGraphicsItemGroup()  
            self.gridGroup.setZValue(common["gridZ"])
            self.scene.addItem(self.gridGroup)
           
            gs = common["gridSize"]
            pen = QPen(QColor(0,0,255))
         
            for y in range(1, int(common["ViewH"]/gs)):
                self.addLines(QGraphicsLineItem(0.0, gs*y,
                    float(common["ViewW"]), gs*y), pen)
  
            for x in range(1, int(common["ViewW"]/gs)):
                self.addLines(QGraphicsLineItem(gs*x, 0.0,
                    gs*x, float(common["ViewH"])), pen)
        
    def addLines(self, line, pen):
        line.type = 'grid'
        line.setPen(pen)
        line.setOpacity(.30)
        line.setZValue(common["gridZ"])
        line.setFlag(QGraphicsLineItem.GraphicsItemFlag.ItemIsMovable, False)
        self.gridGroup.addToGroup(line)

    def gridCount(self):  
        return sum(pix.type == 'grid' 
            for pix in self.canvas.scene.items())
        
    def xy(self, max):
        return random.randrange(-40, max+40)

### ------------------ moved from sideShow -----------------
    def setPauseKey(self):        
        if self.canvas.control == 'pause': 
            self.canvas.btnPause.setText( "Resume" );
            self.canvas.control = 'resume'
        elif self.canvas.control == 'resume':
            self.canvas.btnPause.setText( "Pause" );
            self.canvas.control = 'pause'

    def enablePlay(self):
        self.canvas.control = ''
        self.canvas.btnRun.setEnabled(True)
        self.canvas.btnPause.setEnabled(False)
        self.canvas.btnStop.setEnabled(False) 
        self.canvas.btnSave.setEnabled(True) 
 
    def disablePlay(self):
        self.canvas.control = 'pause'
        self.canvas.btnRun.setEnabled(False)
        self.canvas.btnPause.setEnabled(True)
        self.canvas.btnStop.setEnabled(True)  
        self.canvas.btnSave.setEnabled(False)  

    def saveToJson(self, dlist):
        Q = QFileDialog()
        if self.canvas.openPlayFile == '':
            self.canvas.openPlayFile = paths["playPath"] + 'tmp.play'
        f = Q.getSaveFileName(self.canvas, 
            paths["playPath"],  
            self.canvas.openPlayFile)
        Q.accept()
        
        if not f[0]: 
            return
        if not f[0].lower().endswith('.play'):
            MsgBox("saveToJson: Wrong file extention - use '.play'", 5)  
            return
        else:
            try:
                with open(f[0], 'w') as fp:
                    json.dump(dlist, fp)
            except IOError:
                MsgBox("saveToJson: Error saving file", 5)
        del dlist

### --------------------------------------------------------
def setMirror(self, mirror):
    self.flopped = mirror   
    self.setPixmap(QPixmap.fromImage(self.imgFile.mirrored(
        horizontal=self.flopped, vertical=False)))
    self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

def constrain(lastXY, objSize, panelSize, overlap):
    if lastXY + objSize > panelSize - overlap:
        return panelSize - (objSize + overlap)
    elif lastXY < overlap:
        return overlap
    else:
        return lastXY

# def setCursor():
#     QGuiApplication.primaryScreen().availableGeometry().center()

### ---------------------- dotsSideCar ---------------------


