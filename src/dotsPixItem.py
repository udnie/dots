
from PyQt6.QtCore       import Qt, QTimer, QPoint, pyqtSlot, QPointF
from PyQt6.QtGui        import QImage, QColor, QPen, QPixmap
from PyQt6.QtWidgets    import QGraphicsPixmapItem

from dotsShared         import common, MoveKeys, RotateKeys, PlayKeys
from dotsPixWidget      import PixWidget, works
from dotsSideGig        import MsgBox

##from dotsShadowMaker    import ShadowMaker  ## uncomment to add shadows otherwise comment out
from dotsShadow_Dummy    import ShadowMaker  ## uncomment turns off shadows - you need to do both

import dotsAnimation  as Anime

ScaleKeys  = ("<",">")
TagKeys = (',','.','/','enter','return') 

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
        self.flopped  = mirror
    
        self.id = int(id)  ## used by mapper
        self.x  = x
        self.y  = y
        
        self.shadowMaker = ShadowMaker(self)  ## returns isActive is False if from shadow_dummy
        self.works = works(self)              ## functions and PixSizes moved from here
        
        img = QImage(self.fileName)

        if 'frame' in self.fileName: 
            newW, newH = common["ViewW"],common["ViewH"]
            self.x, self.y = 0,0
        else:  ## see pixSizes dictionary to make changes - moved to pixWidget
            newW, newH = self.works.setPixSizes(  
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
        self.part = ""  ## used by wings 
  
        self.alpha2  = 1.0  ## alpha was already being used and opacity can be a function
        self.scale   = 1.0
        self.rotation  = 0
             
        self.setZValue(self.id+100) if self.id < 100 else self.setZValue(self.id)
             
        self.isHidden = False  ## acts as toggle
        self.locked = False
        self.tag = ''
        
        self.anime  = None   
        self.shadow = None  ## holds a dictionary of shadow stuff
        self.widget = None
 
        self.dragAnchor = QPoint(0,0)
        self.initX = 0
        self.initY = 0

        self.setPos(self.x, self.y)
        self.setMirrored(mirror)
        
        self.setAcceptHoverEvents(True)
        self.setFlags(False) if 'frame' in self.fileName else self.setFlags(True)
                                       
### --------------------------------------------------------
    @pyqtSlot(str)
    def setPixKeys(self, key):
        self.key = key  
        if self.isHidden or self.isSelected() and self.locked == False:
            if key in RotateKeys:
                self.rotateThis(key)
            elif key in ScaleKeys:
                self.works.scaleThis(key)  
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
            self.toggleTagItems(self.id)   
        e.accept()
                   
    def hoverLeaveEvent(self, e):
        if self.locked:
            self.mapper.clearTagGroup()
        if self.key in TagKeys or self.mapper.tagSet: 
            self.works.clearTag() 
        e.accept()

    def setFlags(self, bool):
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, bool)  
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, bool)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemDoesntPropagateOpacityToChildren, True)
                 
        if self.locked:
            self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
    
    def mousePressEvent(self, e):    
        if self.canvas.control not in PlayKeys: 
            ## right mouse clk triggers Animation menu on selected screen items 
            if e.button() == Qt.MouseButton.RightButton:
                ## if 'pivot' in self.fileName or 'frame' in self.fileName or \                
                if 'frame' not in self.fileName and not self.scene.selectedItems():
                    self.addWidget()  ## nothing selected - ok to add
                    e.accept()
            elif self.key in RotateKeys: 
                self.rotateThis(self.key)
            elif self.key == '\'': 
                self.togglelock()  ## single tag
                self.toggleTagItems(self.id)
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
                self.toggleTagItems(self.id) 
            self.initX, self.initY = self.x, self.y  
            self.dragAnchor = self.mapToScene(e.pos())
        e.accept()

    def mouseMoveEvent(self, e):
        if 'frame' in self.fileName or self.locked:
            return
        elif self.canvas.control not in PlayKeys:
            if self.key in TagKeys or self.mapper.tagSet:
                self.works.clearTag() 
            self.updateXY(self.mapToScene(e.pos()))
            self.setPos(self.x, self.y)
            self.dragCnt +=1
            if self.key == 'opt' and self.dragCnt % 5 == 0:  
                self.cloneThis() 
        e.accept()
            
    def mouseReleaseEvent(self, e): 
        if self.key in TagKeys or self.mapper.tagSet:
            self.works.clearTag()
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
        if self.shadowMaker.isActive == True:
            if 'bat-pivot' in self.fileName:
                self.works.closeWidget()
                MsgBox("No Shadows for BatWings", 4)
                return 
            elif self.shadowMaker.shadow == None:
                self.shadowMaker.works.cleanUpShadow()
                self.shadowMaker.init()                 
                self.shadowMaker.addShadow(self.x, self.y, common["ViewW"],common["ViewH"])
                self.works.closeWidget()   
                self.shadow = self.shadowMaker.shadow   
                
    def toggleTagItems(self, id):  ## too annoying if linked
        if self.shadowMaker.shadow != None and self.shadowMaker.linked:
            return
        else:
            self.mapper.toggleTagItems(id)
                
    def addWidget(self):
        self.works.closeWidget()
        self.widget = PixWidget(self)      
        x, y = self.makeXY()     
        x = int(x - int(self.widget.WidgetW)-10)
        y = int(y - int(self.widget.WidgetH)/6)
        self.widget.setGeometry(x, y, int(self.widget.WidgetW), int(self.widget.WidgetH))
        self.works.resetSliders()
                         
    def setMirrored(self, bool): 
        self.flopped = bool
        self.setPixmap(QPixmap.fromImage(self.imgFile.mirrored(
            # horizontally=self.flopped, vertically=False)))  ## pyside6
            horizontal=self.flopped, vertical=False)))
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
      
    def animeMenu(self):
        x, y = self.makeXY()  
        self.setSelected(True)
        self.works.closeWidget()
        self.canvas.sideCar.animeMenu(QPoint(x+50, y+50), 'pix')
     
    def makeXY(self):  
        p = self.pos()
        p = self.canvas.mapToGlobal(QPoint(int(self.x), int(self.y)))
        return int(p.x()), int(p.y())
                                     
### --------------------------------------------------------
    def reprise(self):  ## return pixitem to its original position
        if self.tag == '':  ## you're done
            return
        self.anime = None
        self.anime = Anime.reprise(self)
        self.anime.start()
        self.anime.finished.connect(self.anime.stop)
        self.clearFocus()
        
    def moveThis(self, key):
        self.setOriginPt()  ## updates width and height also
        self.x += key[0]
        self.y += key[1]
        self.x = self.works.constrainX(self.x)
        self.y = self.works.constrainY(self.y)
        self.setPos(self.x, self.y) 
 
    def setOriginPt(self):    
        b = self.boundingRect()
        op = QPointF(b.width()/2, b.height()/2)
        self.setTransformOriginPoint(op)
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
               
    def togglelock(self):
        if self.locked == False:
            self.locked = True
            self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
            self.toggleTagItems(self.id)  
            QTimer.singleShot(2000, self.mapper.clearTagGroup)  ## the other tag
        else:
            self.locked = False
            self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
            self.tag = 'UnLocked'
            self.toggleTagItems(self.id) 
            QTimer.singleShot(2000, self.mapper.clearTagGroup)
            self.tag = ''
            
    def deletePix(self):
        if 'frame' in self.fileName:
            self.works.removeThis()
        else:
            if self.shadowMaker.isActive == True:
                self.shadowMaker.works.deleteShadow()
            self.works.closeWidget()
            self.anime 
            self.anime = Anime.fin(self)
            self.anime.start()
            self.anime.finished.connect(self.works.removeThis)
             
    def cloneThis(self):
        self.canvas.addPixItem(self.fileName, self.x+25, self.y+10,\
            (self.rotation, self.scale), self.flopped)
    
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

    def updateXY(self, pos):
        dragX = pos.x() - self.dragAnchor.x()
        dragY = pos.y() - self.dragAnchor.y()     
        b = self.boundingRect()
        self.width, self.height = b.width(), b.height()   
        self.x = self.works.constrainX(self.initX + dragX)
        self.y = self.works.constrainY(self.initY + dragY)
        
### -------------------- dotsPixItem -----------------------

