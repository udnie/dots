
import os

from PyQt6.QtCore       import Qt, QTimer, QPoint, QPointF, QRectF, pyqtSlot
from PyQt6.QtGui        import QImage, QColor, QPen, QPixmap
from PyQt6.QtWidgets    import QGraphicsPixmapItem

from dotsShared         import common, MoveKeys, RotateKeys, PlayKeys
from dotsPixWidget      import PixWidget
from dotsSideGig        import constrain

from dotsShadowMaker    import ShadowMaker  ## add shadows
##from dotsShadow_Dummy    import ShadowMaker  ## turns off shadows

import dotsAnimation  as anima

ScaleKeys  = ("<",">")
TagKeys = (',','.','/','enter','return')  ## changed
Pct = -0.50  ## used by constrain - percent allowable off screen

PixSizes = {  ## match up on base filename
    # "apple": (650, 450),
    # 'doral': (300, 500),         
    "actor": (650, 450),
    'dorot': (300, 500),
    'can_m': (300, 400),
    'miche': (350, 375),
    'bosch': (250, 375),
    'lizar': (600, 225),
    'pivot': (150, 150),
    'mike_': (300, 500),
    'squid': (375, 375),
    'boids': (400, 500),
    "joker": (335, 455),
    "jocke": (335, 555),
    "parad": (300, 300),
    "dot":   (375, 400),
    "bug":   (350, 350),
    "manti": (350, 350), 
    "img_":  (650, 450), 
    "orang": (195, 195), 
    "trunk": (150, 600),
    "tag_":  (550, 250),
}

### --------------------- dotsPixItem ----------------------
''' dotsPixItem: primary dots screen object - like a sprite '''
### --------------------------------------------------------
class PixItem(QGraphicsPixmapItem):
### --------------------------------------------------------
    def __init__(self, fileName, id, x, y, parent, mirror=False):
        super().__init__()

        self.canvas = parent
        self.scene  = self.canvas.scene
        self.mapper = self.canvas.mapper
    
        self.fileName = fileName
   
        self.id = int(id)  ## used by mapper
        self.part = ""     ## used by wings
 
        self.x = x
        self.y = y

        img = QImage(fileName)

        if 'frame' in self.fileName: 
            newW, newH = common["ViewW"],common["ViewH"]
            self.x, self.y = 0,0
        else:
            newW, newH = self.setPixSizes( 
                img.width() * common["factor"], 
                img.height() * common["factor"])
   
        ## don't change
        img = img.scaled(int(newW), int(newH),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)

        self.width   = img.width()
        self.height  = img.height()  
        self.imgFile = img

        del img

        self.key = ""
        self.dragCnt = 0
   
        self.type = 'pix'
        self.flopped = mirror

        self.alpha2 = 1.0  ## alpha was already being used and opacity can be a function
        self.scale  = 1.0
        self.rotation = 0
             
        self.setZValue(self.id+100) if self.id < 100 else self.setZValue(self.id)
             
        self.isHidden = False  ## no reason to save it, acts as toggle
        self.locked = False
        self.tag = ''
        
        self.anime  = None   
        self.shadow = None
        self.widget = None
 
        self.dragAnchor = QPoint(0,0)
        self.initX = 0
        self.initY = 0

        self.setPos(self.x, self.y)
        self.setMirrored(mirror)
        
        self.setAcceptHoverEvents(True)
        self.setFlags(False) if 'frame' in self.fileName else self.setFlags(True)
       
        self.shadowMaker = ShadowMaker(self)  ## sets shadow_dummy True/False
               
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
    def paint(self, painter, option, widget=None):  ## this may be the source of a type error in pyside
        super().paint(painter, option, widget)  ## why is this necessary??
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
        if self.key in TagKeys or self.mapper.tagSet: 
            self.clearTag() 
        e.accept()

    def setFlags(self, bool):
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, bool)  
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, bool)
        if self.locked:
            self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
    
    def mousePressEvent(self, e):    
        if self.canvas.control not in PlayKeys: 
            if e.button() == Qt.MouseButton.RightButton:
                ## right mouse triggers animation menu if selected screen items
                if 'pivot' in self.fileName or 'frame' in self.fileName or \
                    self.scene.selectedItems():
                    return      
                else:
                    self.addWidget()  ## nothing selected - ok to add
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
        elif self.canvas.control not in PlayKeys:
            if self.key in TagKeys or self.mapper.tagSet:
                self.clearTag() 
            self.updateXY(self.mapToScene(e.pos()))
            self.setPos(self.x, self.y)
            self.dragCnt +=1
            if self.key == 'opt' and self.dragCnt % 5 == 0:  
                self.cloneThis() 
        e.accept()
            
    def mouseReleaseEvent(self, e): 
        if self.key in TagKeys or self.mapper.tagSet:
            self.clearTag()
        self.dragCnt = 0   
        self.canvas.key = ""
        self.updateXY(self.mapToScene(e.pos()))
        self.setPos(self.x, self.y)
        e.accept()
        
    def mouseDoubleClickEvent(self, e):
        if 'frame' in self.fileName or \
            self.key in TagKeys or self.locked:
            return 
        elif self.canvas.control not in PlayKeys:
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
            elif self.canvas.key not in ('opt','cmd','shift'):
                if self.isSelected() == False:
                    self.setSelected(True)  
                elif self.isSelected():
                    self.setSelected(False)
                self.isHidden = False 
        e.accept()
            
### --------------------------------------------------------
    def addShadow(self):  ## from pixwidget 
        if self.shadowMaker.isDummy == False:
            self.shadowMaker.cleanUpShadow()
            self.shadowMaker.init()
            self.shadowMaker.addShadow(self.width, self.height, common["ViewW"],common["ViewH"])
            self.closeWidget()
            self.shadow = self.shadowMaker.shadow

    def addWidget(self):
        self.closeWidget()
        self.widget = PixWidget(self)  
        p = self.pos()
        x, y = int(p.x()), int(p.y())  
        f = common['widget']  ## necessary, it drifts with changes in size
        self.widget.setGeometry(x+f[0], y+f[1], int(self.widget.WidgetW), int(self.widget.WidgetH))
        self.resetSliders()

    def resetSliders(self):
        self.widget.opacitySlider.setValue(int(self.alpha2*100))
        self.widget.scaleSlider.setValue(int(self.scale*100))
        self.widget.rotaryDial.setValue(int(self.rotation))
     
    def closeWidget(self):
        if self.widget != None:
            self.widget.close()
            self.widget = None
                     
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
        self.x = self.constrainX(self.initX + dragX)
        self.y = self.constrainY(self.initY + dragY)
                 
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
            if self.shadowMaker.isDummy == False:
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
        self.canvas.addPixItem(self.fileName, self.x+25, self.y+10,\
            (self.rotation, self.scale), self.flopped)
     
    def moveThis(self, key):
        self.setOriginPt()  ## updates width and height also
        self.x += key[0]
        self.y += key[1]
        self.x = self.constrainX(self.x)
        self.y = self.constrainY(self.y)
        self.setPos(self.x, self.y) 
  
    def constrainX(self, X):    
        return int(constrain(X, self.width, common["ViewW"], self.width * Pct))
        
    def constrainY(self, Y):
        return int(constrain(Y, self.height, common["ViewH"], self.height * Pct))
  
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
        # print(p, "{0:.2f}".format(newW), "{0:.2f}".format(newH))
        if newW < 100 or newH < 100:
            newW, newH = 200, 200 
        elif newW > 400 or newH > 400:
            newW, newH = 425, 425
        return newW, newH
    
### -------------------- dotsPixItem -----------------------

