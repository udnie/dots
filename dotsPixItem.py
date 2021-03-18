import random

from PyQt5.QtCore     import *
from PyQt5.QtGui      import *
from PyQt5.QtWidgets  import *

from dotsShared       import common

import dotsSideCar    as sideCar 
import dotsAnimation  as anima

## -- for testing and comparison ----------------
#from pubsub  import pub      # PyPubSub - required

IncZ = 1.0      # increment zValue
Pixfactor = .30  # beginnig size factor 

MoveKeys = ("left","right","up", "down")
RotateKeys = ("_", '+', '"', ':', "{", "}")
ScaleKeys  = ("<",">")

RotationVals = {
    '}': 45,
    '"': +15,
    '+': 1,
    '_': -1,
    ':': -15,
    '{': -45,
}

### --------------------- dotsPixItem ----------------------
''' dotsPixItem: primary dots screen object - like a sprite '''
### --------------------------------------------------------
class PixItem(QGraphicsPixmapItem):
    
    def __init__(self, imgFile, id, x, y, parent, mirror=False):
        super().__init__()

        self.canvas = parent
        self.mapper = parent.mapper

        self.fileName = imgFile
   
        self.id = id  ## used by mapper
        self.x  = x
        self.y  = y

        img = QImage(imgFile)

        if 'frame' in self.fileName: 
            newW, newH = common["ViewW"],common["ViewH"]
            self.x, self.y = 0,0
        else:
            newW, newH = self.setPixSizes( 
                img.width() * Pixfactor, 
                img.height() * Pixfactor)

        ## don't change
        img = img.scaled(newW, newH,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation)

        self.width   = img.width()
        self.height  = img.height()  
        self.imgFile = img

        self.key = ""
        self.dragCnt = 0

        self.type = 'pix'
        self.flopped = mirror

        self.rotation = 0
        self.scale = 1.0
        ## zValue may reset by loadPlay
        self.setZValue(self.id)  
        
        self.isHidden = False
        self.anime = None
        self.tag = ''
 
        self.dragAnchor = QPoint(0,0)
        self.initX = 0
        self.initY = 0

        self.setPos(self.x, self.y)
        self.setMirrored(mirror)

        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable)
  
        # pub.subscribe(self.setPixKeys, 'setKeys')
        
### --------------------------------------------------------
    @pyqtSlot(str)
    def setPixKeys(self, key):
        self.key = key  
        if self.isHidden or self.isSelected():
            if key in RotateKeys:
                self.rotateThis(key)
            elif key in ScaleKeys:
                self.scaleThis(key)  
            elif key in MoveKeys:
                self.moveThis(key)

    def setMirrored(self, mirror):
        sideCar.mirrorSet(self, mirror)

    def mousePressEvent(self, e):           
        if e.button() == Qt.RightButton:
            self.ungrabMouse()   
        if self.key == 'del':  # delete
            self.deletePix()
        if self.key == '/': # send to back of pixItems
            self.setZValue(self.mapper.lastZval('pix')-1)
        elif self.key == 'opt':  # send it back one Z
            p = self.zValue()-1  # so as not to confuse things
            self.setZValue(p)
        elif self.key == 'cmd': # send it forward one Z
            p = self.zValue()+1  
            self.setZValue(p)
        else:                   # single click to front
            self.setZValue(self.mapper.toFront(IncZ))
        if 'frame' not in self.fileName:
            self.initX, self.initY = self.x, self.y   # set position
            self.dragAnchor = self.mapToScene(e.pos())
            if self.key == 'shift':  # flop if selected or hidden
                if self.flopped:
                    self.setMirrored(False)
                else:
                    self.setMirrored(True)
        e.accept()

    def reprise(self):  ## return pixitem to original position
        self.anime = None
        self.anime = anima.reprise(self)
        self.anime.start()
        self.anime.finished.connect(self.anime.stop)
        self.clearFocus()
 
    def deletePix(self):
        if 'frame' in self.fileName:
            self.removeThis()
        else:
            self.anime 
            self.anime = anima.fin(self)
            self.anime.start()
            self.anime.finished.connect(self.removeThis)

    def removeThis(self):
        self.canvas.scene.removeItem(self)

    def mouseMoveEvent(self, e):
        if 'frame' in self.fileName:
            return
        pos = self.mapToScene(e.pos())     
        dragX = pos.x() - self.dragAnchor.x()
        dragY = pos.y() - self.dragAnchor.y()
        self.mapper.updateWidthHeight(self)
        self.x = int(sideCar.constrain(
            self.initX + dragX, 
            self.width, 
            common["ViewW"], 
            self.width * -common["factor"]))
        self.y = int(sideCar.constrain(
            self.initY + dragY,
            self.height, 
            common["ViewH"], 
            self.height * -common["factor"]))
        self.setPos(self.x, self.y)
        self.dragCnt +=1
        if self.key == 'opt' and self.dragCnt % 5 == 0:  
            self.cloneThis(e) 
        e.accept()

    def mouseDoubleClickEvent(self, e):
        if 'frame' in self.fileName:
            return
        if self.key == 'opt':  
            self.cloneThis(e)
        elif self.canvas.key == 'noMap': 
            ## consumed map's dblclk need to set it back 
            self.canvas.setKeys('')      
            if self.isHidden == False or self.isSelected():
                self.setSelected(True) 
                return
        elif self.isHidden:   
            ## otherwise you're stuck if others are 
            ## selected as the others will become hidden 
            self.setSelected(True) 
            self.isHidden = False  
        elif not self.canvas.key in ('opt','cmd','shift'):
            if self.isSelected() == False:
                self.setSelected(True)  
            elif self.isSelected():
                self.setSelected(False)
            self.isHidden = False 
        e.accept()

    def cloneThis(self, e):
        self.canvas.addPixItem(
            self.fileName, 
            self.x+25, 
            self.y+10,
            self,
            self.flopped)
        e.accept()

    def pixVals(self):
        tmp = {
            "x": self.x,
            "y": self.y,
            "mirror": self.flopped,
            "rotation": self.rotation,
            "scale": self.scale,
            "tag": self.tag
        }
        return tmp

    def mouseReleaseEvent(self, e):
        if self.dragCnt > 0:
            self.dragCnt = 0   
            self.setZValue(self.mapper.toFront(IncZ))
        e.accept()

    def moveThis(self, key):
        self.setOriginPt()  ## updates width and height also
        pts = 2        
        if key == 'right':
            self.x += pts
        elif key == 'left':
            self.x -= pts
        elif key == 'up':
            self.y -= pts
        elif key == 'down':
            self.y += pts
        self.x = int(sideCar.constrain(self.x, 
            self.width, 
            common["ViewW"], 
            self.width * -common["factor"]))
        self.y = int(sideCar.constrain(self.y, 
            self.height, 
            common["ViewH"], 
            self.height * -common["factor"]))
        self.setPos(self.x, self.y) 
  
    def rotateThis(self, key):
        self.setOriginPt() 
        angle = RotationVals[key]  ## thanks Martin
        p = self.rotation + angle
        if p > 360: 
            p = p - 360
        elif p < 0:
            p = p + 360
        self.rotation = p
        self.setRotation(self.rotation) 

    def scaleThis(self, key):
        self.setOriginPt()
        if key == '>':
            scale = .03
        elif key == '<':
            scale = -.03
        self.scale += scale
        self.setScale(self.scale)
    
    def setOriginPt(self):
        self.mapper.setOriginPt(self)
        self.setTransformationMode(Qt.SmoothTransformation)
              
    def setPixSizes(self, newW, newH):
        if newW < 100 or newH < 100:
            newW, newH = 165, 165
        elif 'can_man' in self.fileName:   ## not included
            newW, newH = 300, 375   
        elif 'michelin' in self.fileName:  ## not included
            newW, newH = 350, 375
        elif 'bosch' in self.fileName:     ## not included
            newW, newH = 250, 375
        elif 'lizard' in self.fileName:    ## not included
            newW, newH = 300, 600 
        if newW > 400 or newH > 400:
            newW, newH = 425, 425
        return newW, newH
            
### -------------------- dotsPixItem -----------------------

