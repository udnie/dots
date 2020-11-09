import random

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from dotsShared      import common, paths
from dotsPixItem     import PixItem

### ---------------------- dotsSideCar ---------------------
''' dotsSideCar: handles pixtest, transformpixitem, togglegrid
    and MsgBox and some small functions '''
### --------------------------------------------------------
class SideCar():

    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
        self.scene  = parent.scene
        self.mapper = parent.mapper   
        
        self.gridZ   = common["gridZ"] 
        self.gridSet = False
        self.gridGroup = None

### --------------------------------------------------------
    def pixTest(self):
        if not self.canvas.pathMakerOn:
            self.canvas.pixCount = self.mapper.toFront(0.0)  
            for _ in range(10):
                self.canvas.pixCount += 1
                pix = PixItem(paths["spritePath"] + 'apple.png',
                        self.canvas.pixCount,
                        0, 0, 
                        self.canvas)
                x = int(constrain(
                        self.xy(common["viewW"]),
                        pix.width, 
                        common["viewW"], 
                        pix.width * -common["factor"]))
                y = int(constrain(
                        self.xy(common["viewH"]),
                        pix.height, 
                        common["viewH"],
                        pix.height * -common["factor"]))
                pix.x, pix.y = x, y
                pix.setPos(x,y)
                rotation = random.randrange(-5, 5) * 5
                scale = random.randrange(95, 105)/100.0
                self.transFormPixItem(pix, rotation, scale)
         
    def transFormPixItem(self, pix, rotation, scale):
        op = QPointF(pix.width/2, pix.height/2)
        pix.setTransformationMode(Qt.SmoothTransformation)
        pix.setTransformOriginPoint(op)
        pix.scale, pix.rotation = scale, rotation
        pix.setScale(scale)
        pix.setRotation(rotation)
        self.scene.addItem(pix)
  
    def xy(self, max):
        return random.randrange(-40, max+40)

### --------------------------------------------------------
    def toggleGrid(self):
        if self.gridSet:
            self.scene.removeItem(self.gridGroup)
            self.gridSet = False
        else: 
            self.gridGroup = QGraphicsItemGroup()  
            self.gridGroup.setZValue(common["gridZ"])
            self.scene.addItem(self.gridGroup)
            self.gridSet = True

            gs = common["gridSize"]
            pen = QPen(QColor(0,0,255))

            for i in range(int(common["viewH"]/gs)):
                self.addLines(QGraphicsLineItem(0.0, gs*i,
                    float(common["viewW"]), gs*i), pen)
            for j in range(int(common["viewW"]/gs)):
                self.addLines(QGraphicsLineItem(gs*j, 0.0,
                    gs*j, float(common["viewH"])), pen)
        
    def addLines(self, line, pen):
        line.type = 'grid'
        line.setPen(pen)
        line.setOpacity(common["factor"])
        line.setZValue(common["gridZ"])
        line.setFlag(QGraphicsLineItem.ItemIsMovable, False)
        self.gridGroup.addToGroup(line)

### --------------------------------------------------------
class MsgBox(QMessageBox):  ## thanks stackoverflow

    def __init__(self, text, pause=2):
        super().__init__()

        self.timeOut = pause
        self.setText("\n" + text)
        self.setStandardButtons(QMessageBox.NoButton)
       
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeContent)
        self.timer.start()

        self.exec_()

    def enterEvent(self, e):  
        self.close()

    def changeContent(self):
        self.timeOut -= 1
        if self.timeOut <= 0:
            self.close()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept() 

### --------------------------------------------------------
def mirrorSet(self, mirror):
    self.flopped = mirror   
    self.setPixmap(QPixmap.fromImage(
        self.imgFile.mirrored(
        horizontal=self.flopped,
        vertical=False)))
    self.setTransformationMode(Qt.SmoothTransformation)

def constrain(lastXY, objSize, panelSize, overlap):
    if lastXY + objSize > panelSize - overlap:
        return panelSize - (objSize + overlap)
    elif lastXY < overlap:
        return overlap
    else:
        return lastXY

def setCursor():
    cur = QCursor()
    cur.setPos(QDesktopWidget().availableGeometry().center())

### ---------------------- dotsSideCar ---------------------

