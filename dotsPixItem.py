from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import dotsQt

# from pubsub  import pub      # PyPubSub - required

incZ = .011  # increment zValue 

### --------------------- dotsPixItem ----------------------
class PixItem(QGraphicsPixmapItem):
    
    def __init__(self, imgFile, x, y, id, parent, mirror=False):
        super().__init__()

        self.shared = dotsQt.Shared()
        self.parent = parent
        self.view = parent.view
        self.fileName = imgFile
   
        self.id = id
        self.type = 'pix'

        self.x = x
        self.y = y

        img = QImage(imgFile)

        newW, newH = self.setPixSizes( 
            img.width() * self.shared.factor, 
            img.height() * self.shared.factor)

        img = img.scaled(newW, newH,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation)

        self.width = img.width()
        self.height = img.height()
        self.imgFile = img  

        self.key = ""
        self.dragCnt = 0
        self.rotation = 0
        self.scale = 1.0
        self.setZValue(0.0)
        
        self.flopped = mirror
        self.isHidden = False
 
        self.dragAnchor = QPoint(0,0)
        self.initX = 0
        self.initY = 0

        self.setPos(self.x, self.y)
        self.setMirrored(mirror)

        self.setFlag(QGraphicsPixmapItem.ItemIsMovable)
        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable)
      
        # pub.subscribe(self.setPixKeys, 'setKeys')

### --------------------------------------------------------
    @pyqtSlot(str)
    def setPixKeys(self, key):
        self.key = key  
        if self.isHidden or self.isSelected():
            if key in(":", '"', ">", "<", "{", "}"):
                self.rotateThis(key)
            elif key in("-","+"):
                self.scaleThis(key)  
            elif key in("left","right","up", "down"):
                self.moveThis(key)

    def setMirrored(self, mirror):
        self.flopped = mirror        
        self.setPixmap(QPixmap.fromImage(self.imgFile.mirrored(
            horizontal=mirror,
            vertical=False)))
        self.setTransformationMode(Qt.SmoothTransformation)

    def mousePressEvent(self, e):
        if self.key == 'shift':
            self.parent.scene.removeItem(self)
        else:      
            self.initX, self.initY = self.x, self.y
            self.dragAnchor = self.mapToScene(e.pos())
        if  self.key == 'draw':  # to back
            self.setZValue(self.parent.lastZval('pix')-.01)
        else:                    # to front
            self.setZValue(self.parent.toFront(incZ))
        e.accept()

    def mouseMoveEvent(self, e):
        pos = self.mapToScene(e.pos())     
        dragX = pos.x() - self.dragAnchor.x()
        dragY = pos.y() - self.dragAnchor.y()
        self.updateWidthHeight()
        self.x = int(dotsQt.constrain(self.initX + dragX, 
            self.width, 
            self.shared.viewW, 
            self.width * -self.shared.factor))
        self.y = int(dotsQt.constrain(self.initY + dragY,
            self.height, 
            self.shared.viewH, 
            self.height * -self.shared.factor))
        self.setPos(self.x, self.y)
        self.dragCnt +=1
        if self.key == 'clone' and self.dragCnt % 5 == 0:  
            self.cloneThis(e)
        e.accept()

    def mouseDoubleClickEvent(self, e):
        if self.key == 'clone':  
            self.cloneThis(e)
        elif self.parent.key == 'noMap': 
            ## consumed map's dblclk need to set it back 
            self.parent.setKeys('')      
            if self.isHidden == False or self.isSelected():
                self.setSelected(True) 
                return
        elif self.isHidden:   
            ## otherwise you're stuck if others are 
            ## selected as the others will become hidden 
            self.setSelected(True) 
            self.isHidden = False  
        else:
            if self.isSelected() == False:
                self.setSelected(True)  
            elif self.isSelected():
                self.setSelected(False)
            self.isHidden = False 
        e.accept()

    def cloneThis(self, e):
        self.parent.addPixItem(
            self.fileName, 
            self.x+20, 
            self.y+5,
            self,
            self.flopped)
        e.accept()

    def mouseReleaseEvent(self, e):
        if self.dragCnt > 0:
            self.dragCnt = 0   
            self.setZValue(self.parent.toFront(incZ))
        e.accept()

    def moveThis(self, key):
        self.setOriginPt()
        pts = 2        
        if key == 'right':
            self.x += pts
        elif key == 'left':
            self.x -= pts
        elif key == 'up':
            self.y -= pts
        elif key == 'down':
            self.y += pts
        self.x = int(dotsQt.constrain(self.x, 
            self.width, 
            self.shared.viewW, 
            self.width * -self.shared.factor))
        self.y = int(dotsQt.constrain(self.y, 
            self.height, 
            self.shared.viewH, 
            self.height * -self.shared.factor))
        self.setPos(self.x, self.y) 
  
    def rotateThis(self, key):
        self.setOriginPt()
        if key in ('>', '}', '"'):
            if self.rotation >= 360:  # forces back to zero
                self.rotation = 0
            if key == '>':
                angle = 15
            elif key == '}':
                angle = 45
            else:
                angle = 1
            p = self.rotation + angle
        elif key in ('<', '{', ':'):
            if self.rotation <= 0:  # forces back to 360
                self.rotation = 360
            if key == '<':
                angle = -15
            elif key == '{':
                angle = -45
            else:
                angle = -1
            p = self.rotation + angle
            if p > 360: 
                p = p - 360
            elif p < 0:
                p = p + 360
        self.rotation = p
        self.setRotation(self.rotation) 

    def scaleThis(self, key):
        self.setOriginPt()
        if key == '+':
            scale = .03
        else:
            scale = -.03
        self.scale += scale
        self.setScale(self.scale)
    
    def setOriginPt(self):
        self.updateWidthHeight()
        op = QPointF(self.width/2, self.height/2)
        self.setTransformOriginPoint(op)
        self.setTransformationMode(Qt.SmoothTransformation)

    def updateWidthHeight(self):
        brt = self.boundingRect()
        self.width = brt.width()
        self.height = brt.height()
              
    def setPixSizes(self, newW, newH):
        if newW < 100 or newH < 100:
            newW, newH = 165, 165
        elif 'can_man' in self.fileName:   ## not included
            newW, newH = 350, 425   
        elif 'michelin' in self.fileName:  ## not included
            newW, newH = 350, 500
        elif 'bosch' in self.fileName:     ## not included
            newW, newH = 275, 450
        elif 'lizard' in self.fileName:     ## not included
            newW, newH = 300, 600 
        if newW > 450 or newH > 450:
            newW, newH = 500, 500
        return newW, newH
            
### -------------------- dotsPixItem -----------------------
