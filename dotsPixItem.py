
import os

from PyQt6.QtCore       import Qt, QTimer, QPoint, QPointF, pyqtSlot
from PyQt6.QtGui        import QImage, QColor, QPen, QPixmap
from PyQt6.QtWidgets    import QGraphicsPixmapItem

from dotsShared         import common, MoveKeys, RotateKeys, PlayKeys
from dotsPixWidget      import PixWidget

#from dotsShadowMaker    import ShadowMaker  ## add shadows
from dotsShadow_Dummy    import ShadowMaker  ## turns off shadows

import dotsSideCar    as sideCar
import dotsAnimation  as anima

PixFactor = .30  # beginnig size factor 
ScaleKeys  = ("<",">")
TagKeys = (',','.','/','enter','return')  ## changed

PixSizes = {  ## match up on base filename
}

### --------------------- dotsPixItem ----------------------
''' dotsPixItem: primary dots screen object - like a sprite '''
### --------------------------------------------------------
class PixItem(QGraphicsPixmapItem):
### --------------------------------------------------------
    def __init__(self, imgFile, id, x, y, parent, mirror=False):
        super().__init__()

        self.canvas = parent
        self.scene  = parent.scene
        self.mapper = parent.mapper

        self.fileName = imgFile
   
        self.id = int(id)  ## used by mapper
        self.part = ""     ## used by wings
        self.locked = False

        self.x = x
        self.y = y

        img = QImage(imgFile)

        if 'frame' in self.fileName: 
            newW, newH = common["ViewW"],common["ViewH"]
            self.x, self.y = 0,0
        else:
            newW, newH = self.setPixSizes( 
                img.width() * PixFactor, 
                img.height() * PixFactor)
   
        ## don't change
        img = img.scaled(int(newW), int(newH),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)

        self.width   = img.width()
        self.height  = img.height()  
        self.imgFile = img

        self.key = ""
        self.dragCnt = 0

        self.type = 'pix'
        self.flopped = mirror

        self.alpha2 = 1.0  ## alpha was already being used and opacity can be a function
        self.scale  = 1.0
        self.rotation = 0
           
        self.setZValue(self.id)  ## zValue may reset by loadPlay 
        
        self.isHidden = False
        self.tag = ''
        
        self.anime  = None   
        self.shadow = None
        self.widget = None
 
        self.dragAnchor = QPoint(0,0)
        self.initX = 0
        self.initY = 0

        self.setPos(self.x, self.y)
        self.setMirrored(mirror)

        self.setFlags(False) if 'frame' in self.fileName else self.setFlags(True)
  
        self.setShapeMode(QGraphicsPixmapItem.ShapeMode.BoundingRectShape)
        self.setAcceptHoverEvents(True)
        
        self.shadowMaker = ShadowMaker(self)
        
        self.WidgetW, self.WidgetH = 330.0, 210.0
      
### --------------------------------------------------------
    @pyqtSlot(str)
    def setPixKeys(self, key):
        self.key = key  
        if self.isHidden or self.isSelected() and self.locked == False:
            if key in RotateKeys:
                self.rotateThis(key)
            elif key in ScaleKeys:
                self.scaleThis(key)  
            elif key in MoveKeys:
                self.moveThis(MoveKeys[key])
 
### --------------------------------------------------------
    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.isSelected():
            pen = QPen(QColor("lime"))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())
            
    def hoverEnterEvent(self, e):
        if self.locked: 
            self.mapper.toggleTagItems(self.id)   
        e.accept()
                   
    def hoverLeaveEvent(self, e):
        if self.locked:
            self.mapper.clearTagGroup()
        e.accept()

    def setFlags(self, bool):
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, bool)  
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, bool)
        if self.locked:
            self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
    
    def mousePressEvent(self, e):    
        if self.canvas.control not in PlayKeys: 
            if e.button() == Qt.MouseButton.RightButton:
                if 'pivot' in self.fileName or 'frame' in self.fileName:
                    return
                elif not self.scene.selectedItems():
                    self.addWidget()
            elif self.key == 'space' and e.button() == Qt.LeftButton:
                self.mapper.toggleTagItems(self.id)
            elif self.key in RotateKeys:
                self.rotateThis(self.key)
            elif self.key == '\'': 
                self.togglelock()  ## single tag
                self.mapper.toggleTagItems(self.id)
            elif self.key == 'del':  # delete
                self.deletePix()     
            elif self.key == 'shift':  # flop if selected or hidden        
                self.setMirrored(False) if self.flopped else self.setMirrored(True)         
            elif self.key in TagKeys: 
                if self.key == '/':        # send to back of pixItems
                    p = self.mapper.lastZval('pix')-1
                elif self.key in('enter','return'): # send to front
                    p = self.mapper.toFront(1)
                elif self.key == ',':
                    p = self.zValue()-1  
                elif self.key == '.':
                    p = self.zValue()+1  
                self.setZValue(p)
                self.mapper.toggleTagItems(self.id)
            self.initX, self.initY = self.x, self.y  
            self.dragAnchor = self.mapToScene(e.pos())
            e.accept()

    def mouseMoveEvent(self, e):
        if 'frame' in self.fileName or self.locked:
            return
        if self.canvas.control not in PlayKeys:
            if self.key in TagKeys or self.mapper.tagSet:
                self.clearTag() 
            self.updateXY(self.mapToScene(e.pos()))
            self.setPos(self.x, self.y)
            self.dragCnt +=1
            if self.key == 'opt' and self.dragCnt % 5 == 0:  
                self.cloneThis() 
            e.accept()
            
    def mouseReleaseEvent(self, e):
        self.dragCnt = 0         
        self.updateXY(self.mapToScene(e.pos()))
        self.setPos(self.x, self.y)
        e.accept()
        
    def mouseDoubleClickEvent(self, e):
        if 'frame' in self.fileName or \
            self.key in TagKeys or self.locked:
            return 
        if self.canvas.control not in PlayKeys:
            if self.key == 'opt':  
                self.cloneThis()
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
            
### --------------------------------------------------------
    def addWidget(self):
        self.closeWidget()
        self.widget = PixWidget(self)
        p = self.pos()
        x, y = int(p.x()), int(p.y())         
        self.widget.setGeometry(x-20, y+50, int(self.WidgetW), int(self.WidgetH))
        self.resetSliders()
  
    def resetSliders(self):
        self.widget.opacitySlider.setValue(int(self.alpha2*100))
        self.widget.scaleSlider.setValue(int(self.scale*100))
        self.widget.rotaryDial.setValue(int(self.rotation))
     
    def closeWidget(self):
        if self.widget != None:
            self.widget.close()
            self.widget = None
            
    def addShadow(self):
        self.shadowMaker.addShadow(self.width, self.height, common["ViewW"],common["ViewH"])
        self.closeWidget()
        self.shadow = self.shadowMaker.shadow
         
    def setMirrored(self, bool): 
        self.flopped = bool
        self.setPixmap(QPixmap.fromImage(self.imgFile.mirrored(
            # horizontally=self.flopped, vertically=False)))  ## pyside6
            horizontal=self.flopped, vertical=False)))
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
    
    def flopIt(self):
        self.setMirrored(False) if self.flopped else self.setMirrored(True) 
      
### --------------------------------------------------------
    def updateXY(self, pos):
        dragX = pos.x() - self.dragAnchor.x()
        dragY = pos.y() - self.dragAnchor.y()     
        b = self.boundingRect()
        self.width, self.height = b.width(), b.height()
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
     
    def reprise(self):  ## return pixitem to original position
        if self.tag == '':  ## you're done
            return
        self.anime = None
        self.anime = anima.reprise(self)
        self.anime.start()
        self.anime.finished.connect(self.anime.stop)
        self.clearFocus()
 
    def togglelock(self):
        if self.locked == False:
            self.locked = True
            self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
            self.mapper.toggleTagItems(self.id)  
            QTimer.singleShot(2000, self.mapper.clearTagGroup)  ## the other tag
        else:
            self.locked = False
            self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
            self.tag = 'UnLocked'
            self.mapper.toggleTagItems(self.id) 
            QTimer.singleShot(2000, self.mapper.clearTagGroup)
            self.tag = ''
            
    def deletePix(self):
        if 'frame' in self.fileName:
            self.removeThis()
        else:
            self.shadowMaker.deleteShadow()
            self.closeWidget()
            self.anime 
            self.anime = anima.fin(self)
            self.anime.start()
            self.anime.finished.connect(self.removeThis)

    def removeThis(self):
        self.clearFocus() 
        self.setEnabled(False)
        self.scene.removeItem(self)

    def clearTag(self):  ## reset canvas key to '' 
        self.mapper.clearTagGroup()
        self.canvas.setKeys('') 
             
    def cloneThis(self):
        self.canvas.addPixItem(
            self.fileName, 
            self.x+25, 
            self.y+10,
            (self.rotation, self.scale),
            self.flopped)
     
    def moveThis(self, key):
        self.setOriginPt()  ## updates width and height also
        self.x += key[0]
        self.y += key[1]
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
        angle = RotateKeys[key]    ## thanks Martin
        p = self.rotation - angle  ## necessary to match scaleRotate in sideways
        if p > 360:                ## now only one source and one set of keys 
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
        b = self.boundingRect()
        op = QPointF(b.width()/2, b.height()/2)
        self.setTransformOriginPoint(op)
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
                                    
    def setPixSizes(self, newW, newH):  
        p = os.path.basename(self.fileName)     
        for key in PixSizes:
            if key in p:
                val = PixSizes.get(key)
                return val[0], val[1]
        if newW < 100 or newH < 100:
            newW, newH = 200, 200 
        elif newW > 400 or newH > 400:
            newW, newH = 425, 425
        return newW, newH
    
### -------------------- dotsPixItem -----------------------

