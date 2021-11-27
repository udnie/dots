
import random
import json

from PyQt5.QtCore    import Qt, QPointF 
from PyQt5.QtGui     import QCursor, QPixmap, QPen, QColor, QGuiApplication
from PyQt5.QtWidgets import QGraphicsPixmapItem, QFileDialog, \
                            QGraphicsItemGroup, QGraphicsLineItem \
                           
from dotsShared      import common, paths
from dotsPixItem     import PixItem
from dotsSideGig     import MsgBox

PlayKeys = ('resume','pause')

### ---------------------- dotsSideCar ---------------------
''' dotsSideCar: wings, pixTest, transFormPixitem, toggleGrid plus 
    some small functions '''  
### --------------------------------------------------------
class SideCar:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
        self.scene  = self.canvas.scene
        self.mapper = self.canvas.mapper
      
        self.gridZ   = common["gridZ"] 
        self.gridGroup = None

### --------------------------------------------------------
    ''' Things to know about wings. They're brittle, don't pull on them.
    Use the bat portion to move the bat - the pivot sprite which can be 
    found in the images folder. Main thing to know, if you need to move 
    or change an animation - do so, save it, clear and reload.
    They're brittle. And it works, even better now. '''
### --------------------------------------------------------
    def wings(self, pix):
        rightWing = pix
        pathTag = pix.tag
  
        rightWing.part = 'right'
        rightWing.tag  = 'Flapper'  ## applies this animation when run
        rightWing.setZValue(rightWing.zValue() + 200)  ## reset wing zvals
        rightWing.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, False)
        rightWing.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemStacksBehindParent)
        
        self.canvas.pixCount += 1
        leftWing = PixItem(rightWing.fileName, 
            self.canvas.pixCount,
            pix.x + pix.width, pix.y, 
            self.canvas,
            True
        )  ## flop it

        leftWing.part = 'left'
        leftWing.tag  = 'Flapper'
        leftWing.setZValue(leftWing.zValue() + 200)
        leftWing.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, False) 
        leftWing.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemStacksBehindParent)
       
        self.canvas.pixCount += 1
        pivot = PixItem(paths["imagePath"] + 'bat-pivot.png', 
            self.canvas.pixCount,
            pix.x, pix.y,  
            self.canvas
        ) 

        pivot.part = 'pivot' 
        pivot.tag = pathTag 
        pivot.setZValue(pivot.zValue() + 200)
        pivot.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, True) 

        ''' magic numbers warning - results will vary - seems
            to be working for bat wings if loaded using file chooser'''    
        half = pivot.width/2     ## looking better
        height = pivot.height/5  ## good guess, close

        ## another correction -5 for y
        pivot.setPos(pivot.x - half, pivot.y - height - 5)
        pivot.setScale(.55)
        pivot.setOriginPt()

        ## center wings around pivot
        rightWing.setPos(half+10, height+2)
        leftWing.setPos(-leftWing.width+(half+5), height)

        ''' if there's a better way to bind these I'd like to know '''
        rightWing.setParentItem(pivot)  
        leftWing.setParentItem(pivot)

        self.scene.addItem(pivot) 

### --------------------------------------------------------
    def pixTest(self):
        if not self.canvas.pathMakerOn:  
            self.canvas.pixCount = self.mapper.toFront()
            for _ in range(10):
                self.canvas.pixCount += 1
                pix = PixItem(paths["spritePath"] + 'apple.png',
                        self.canvas.pixCount,
                        0, 0, 
                        self.canvas)
                x = int(constrain(
                        self.xy(common["ViewW"]),
                        pix.width, 
                        common["ViewW"], 
                        pix.width * -common["factor"]))
                y = int(constrain(
                        self.xy(common["ViewH"]),
                        pix.height, 
                        common["ViewH"],
                        pix.height * -common["factor"]))
                pix.x, pix.y = x, y
                pix.setPos(x,y)
                rotation = random.randrange(-5, 5) * 5
                scale = random.randrange(95, 105)/100.0
                self.transFormPixItem(pix, rotation, scale)
         
    def transFormPixItem(self, pix, rotation, scale):
        op = QPointF(pix.width/2, pix.height/2)
        pix.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        pix.setTransformOriginPoint(op)
        pix.scale, pix.rotation = scale, rotation
        pix.setScale(scale)
        pix.setRotation(rotation)

        if 'wings' in pix.fileName:  
            self.wings(pix)
        else:
            self.scene.addItem(pix)

    def xy(self, max):
        return random.randrange(-40, max+40)

### --------------------------------------------------------
    def toggleGrid(self):
        if self.gridGroup is not None:
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
        line.setOpacity(common["factor"])
        line.setZValue(common["gridZ"])
        line.setFlag(QGraphicsLineItem.GraphicsItemFlag.ItemIsMovable, False)
        self.gridGroup.addToGroup(line)

    def gridCount(self):  
        return sum(
            pix.type == 'grid' 
            for pix in self.canvas.scene.items()
        )

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
        if not f[0]: 
            return
        if not f[0].lower().endswith('.play'):
            MsgBox("saveToJson: Wrong file extention - use '.play'")  
            return
        else:
            try:
                with open(f[0], 'w') as fp:
                    json.dump(dlist, fp)
            except IOError:
                MsgBox("saveToJson: Error saving file")
            del dlist
            return

### --------------------------------------------------------
def mirrorSet(self, mirror):
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

def setCursor():
    QGuiApplication.primaryScreen().availableGeometry().center()

### ---------------------- dotsSideCar ---------------------


