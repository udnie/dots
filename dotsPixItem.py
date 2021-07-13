import random

from PyQt5.QtCore     import QPoint
from PyQt5.QtGui      import QImage

from dotsShared       import common
from dotsSideCar      import *

import dotsSideCar    as sideCar
import dotsAnimation  as anima

## -- for testing and comparison ----------------
#from pubsub  import pub      # PyPubSub - required

PixFactor = .30  # beginnig size factor 
PlayKeys = ('resume','pause')
MoveKeys  = ("left","right","up", "down")
RotateKeys = ("_", '+', '"', ':', "{", "}")
ScaleKeys  = ("<",">")
TagKeys = ('[', ']','/','enter','return')

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
        self.scene  = parent.scene
        self.mapper = parent.mapper

        self.fileName = imgFile
   
        self.id = int(id)  ## used by mapper
        self.side = ""     ## used by wings
        self.locked = False

        self.x  = x
        self.y  = y

        img = QImage(imgFile)

        if 'frame' in self.fileName: 
            newW, newH = common["ViewW"],common["ViewH"]
            self.x, self.y = 0,0
        else:
            newW, newH = self.setPixSizes( 
                img.width() * PixFactor, 
                img.height() * PixFactor)

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

        if 'frame' in self.fileName:
            self.setFlags(False)
        else:
            self.setFlags(True)
  
        self.setAcceptHoverEvents(True)
        # pub.subscribe(self.setPixKeys, 'setKeys')
      
### --------------------------------------------------------
    @pyqtSlot(str)
    def setPixKeys(self, key):
        self.key = key  
        if self.isHidden or self.isSelected() and \
            self.locked == False:
            if key in RotateKeys:
                self.rotateThis(key)
            elif key in ScaleKeys:
                self.scaleThis(key)  
            elif key in MoveKeys:
                self.moveThis(key)
 
# ### --------------------------------------------------------
    def hoverLeaveEvent(self, e):
        self.mapper.clearTagGroup()
        e.accept()

    def setFlags(self, bool):
        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable, bool)  
        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, bool)
        if self.locked:
            self.setFlag(QGraphicsPixmapItem.ItemIsMovable, False)
  
    def setMirrored(self, mirror):
        sideCar.mirrorSet(self, mirror)

    def mousePressEvent(self, e):   
        if self.canvas.control not in PlayKeys: 
            if self.key == 'space' and e.button() == Qt.LeftButton:
                self.mapper.toggleTagItems(self.id)
            elif self.key == '\'': 
                self.togglelock()  ## single tag
                self.mapper.toggleTagItems(self.id)
            elif self.key == 'del':  # delete
                self.deletePix()
            elif self.key == 'shift':  # flop if selected or hidden
                if self.flopped:
                    self.setMirrored(False)
                else:
                    self.setMirrored(True)
            elif self.key in TagKeys: 
                if self.key == '/':        # send to back of pixItems
                    p = self.mapper.lastZval('pix')-1
                elif self.key in('enter','return'): # send to front
                    p = self.mapper.toFront(1)
                elif self.key == '[':
                    p = self.zValue()-1  
                else:
                    p = self.zValue()+1  
                self.setZValue(p)
                self.mapper.toggleTagItems(self.id)
            self.initX, self.initY = self.x, self.y   # set position
            self.dragAnchor = self.mapToScene(e.pos())
            e.accept()

    def reprise(self):  ## return pixitem to original position
        self.anime = None
        self.anime = anima.reprise(self)
        self.anime.start()
        self.anime.finished.connect(self.anime.stop)
        self.clearFocus()
 
    def togglelock(self):
        if self.locked == False:
            self.locked = True
            self.setFlag(QGraphicsPixmapItem.ItemIsMovable, False)
        else:
            self.locked = False
            self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
    
    def deletePix(self):
        if 'frame' in self.fileName:
            self.removeThis()
        else:
            self.anime 
            self.anime = anima.fin(self)
            self.anime.start()
            self.anime.finished.connect(self.removeThis)

    def removeThis(self):
        self.clearFocus() 
        self.setEnabled(False)
        self.scene.removeItem(self)

    def mouseMoveEvent(self, e):
        if 'frame' in self.fileName or self.locked:
            return
        if self.canvas.control not in PlayKeys:
            if self.key in TagKeys or self.mapper.tagSet:
                self.clearTag() 
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

    def clearTag(self):   ## reset canvas key to '' 
        self.mapper.clearTagGroup()
        self.canvas.setKeys('') 
             
    def mouseDoubleClickEvent(self, e):
        if 'frame' in self.fileName or \
            self.key in TagKeys or self.locked:
            return
        if self.canvas.control not in PlayKeys:
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
            newW, newH = 200, 200
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

