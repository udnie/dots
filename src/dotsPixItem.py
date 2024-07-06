

from PyQt6.QtCore       import Qt, QTimer, QPoint, pyqtSlot, QPointF
from PyQt6.QtGui        import QImage, QPen, QPixmap, QColor
from PyQt6.QtWidgets    import QGraphicsPixmapItem

from dotsShared         import common, MoveKeys, RotateKeys, ControlKeys
from dotsPixWorks       import Works
from dotsPixWidget      import PixWidget
from dotsSideGig        import MsgBox
from dotsBkgScrollWrks  import tagBkg

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
    
        self.type = 'pix'
        self.fileName = fileName
        
        self.flopped = mirror
        self.id = int(id)  ## used by mapper
              
        self.x = x 
        self.y = y
        
        self.shadow = None  ## a dictionary to maintain shadow data if there is one
        self.shadowMaker = ShadowMaker(self)  ## returns isActive equals False if from shadow_dummy
        
        self.works = Works(self)  ## functions and PixSizes moved from here
        
        img = None
        img = QImage(self.fileName)

        ## see pixSizes dictionary to make changes - moved to pixWorks
        newW, newH = self.works.setPixSizes(  
        img.width() * common["factor"],  ## from screens
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
        
        self.part = ""  ## used by wings 
  
        self.alpha2  = 1.0  ## alpha was already being used and opacity can be a function
        self.scale   = 1.0
        self.rotation  = 0
             
        self.setZValue(self.id+100) if self.id < 100 else self.setZValue(self.id)
             
        self.isHidden = False  ## acts as toggle
        self.locked = False
        self.tag = ''
        
        self.anime  = None   
        self.widget = None
 
        self.dragAnchor = QPoint()
        self.offset = QPointF()  ## difference in x,y between pixitem and shadow when linked
        
        self.initX = 0
        self.initY = 0

        self.setPos(self.x, self.y)
        self.setMirrored(mirror)
        
        self.setAcceptHoverEvents(True)
        self.setFlags(True)
                                       
### --------------------------------------------------------
    @pyqtSlot(str)  ## updated by storyboard
    def setPixKeys(self, key):
        self.key = key  
 
        if self.isHidden or self.isSelected() and self.locked == False:
            if key in RotateKeys:
                self.works.rotateThis(key)
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
                   
    def hoverLeaveEvent(self, e):
        if self.locked:
            self.mapper.clearTagGroup()
        if self.key in TagKeys or self.mapper.tagSet: 
            self.works.clearTag() 
        e.accept()

    def setFlags(self, bool):
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, bool)  
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, bool)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, False)          
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemDoesntPropagateOpacityToChildren, True)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsGeometryChanges, False)      
        if self.locked:
            self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
     
### --------------------------------------------------------
    def itemChange(self, change, value):  ## continue to updatePath when animated
        if self.shadowMaker != None and self.shadowMaker.isActive and self.shadowMaker.linked == True:
            if change == QGraphicsPixmapItem.GraphicsItemChange.ItemScenePositionHasChanged: 
                self.shadowMaker.shadow.setPos(self.pos()+ self.offset)
            # elif change == QGraphicsPixmapItem.GraphicsItemChange.ItemRotationChange:
            #     self.shadowMaker.shadow.setRotation(value)
            # elif change == QGraphicsPixmapItem.GraphicsItemChange.ItemScaleChange:
            #     self.shadowMaker.shadow.setScale(value)      
            # elif change == QGraphicsPixmapItem.GraphicsItemChange.ItemOpacityChange:
            #     self.shadowMaker.shadow.setOpacity(value-.50)       
        return super(QGraphicsPixmapItem, self).itemChange(change, value)
                            
    def mousePressEvent(self, e):    
        if self.canvas.control not in ControlKeys:  ## ('resume', 'pause') - animation running
            ## right mouse clk triggers Animation menu on selected screen items 
            if e.button() == Qt.MouseButton.RightButton:
                ## if 'pivot' in self.fileName or 'frame' in self.fileName or \                
                if 'frame' not in self.fileName and not self.scene.selectedItems():
                    self.addWidget()  ## nothing selected - ok to add
                    e.accept()
            elif self.key in RotateKeys: 
                self.works.rotateThis(self.key)
            elif self.key == 'del':  # delete
                self.deletePix()     
            elif self.key == 'shift':  ## flop if selected or hidden        
                self.setMirrored(False) if self.flopped else self.setMirrored(True)                                      
            elif self.key in TagKeys: 
                if self.key == '/':  ## send to back of pixItems
                    p = self.mapper.lastZval('pix')-1
                elif self.key in('enter','return'): # send to front
                    p = self.mapper.toFront(1)
                elif self.key == ',':
                    p = self.zValue()-1  
                elif self.key == '.':
                    p = self.zValue()+1   
                self.setZValue(p)                       
            if self.key == 'tag' or self.key in TagKeys: 
                tagBkg(self, self.pos())
            self.initX, self.initY = self.x, self.y  
            self.dragAnchor = self.mapToScene(e.pos())
            self.key = ''
        e.accept()

    def mouseMoveEvent(self, e):
        if 'frame' in self.fileName or self.locked:
            return
        if self.canvas.control not in ControlKeys:
            if self.key in TagKeys or self.mapper.tagSet:
                self.works.clearTag() 
            self.works.updateXY(self.mapToScene(e.pos()))
            self.setPos(self.x, self.y)
            self.dragCnt +=1
            if self.key == 'opt' and self.dragCnt % 5 == 0:  
                self.works.cloneThis() 
        e.accept()
            
    def mouseReleaseEvent(self, e): 
        self.key = ''
        self.dragCnt = 0   
        self.works.updateXY(self.mapToScene(e.pos()))
        self.setPos(self.x, self.y)  
        e.accept()
        
    def mouseDoubleClickEvent(self, e):
        if 'frame' in self.fileName or self.key in TagKeys:
            return 
        if self.canvas.control not in ControlKeys:  ##  (',', '.', '/', 'enter', 'return')
            if self.key == 'opt':  
                self.works.cloneThis()
            elif self.canvas.key == 'noMap':   ## consumed map's dblclk need to set it back 
                self.canvas.setKeys('')      
                if self.isHidden == False or self.isSelected():
                    self.setSelected(True) 
                    return            
            elif self.isHidden:  ## otherwise you're stuck if others are selected as the others will become hidden
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
        if self.shadowMaker != None and self.shadowMaker.isActive == True:
            if 'bat-pivot' in self.fileName:
                self.works.closeWidget()
                MsgBox("No Shadows for BatWings", 4)
                return 
            if self.shadowMaker.shadow == None:
                self.shadowMaker.works.cleanUpShadow()
                self.shadowMaker.init()  ## this holds much of the shadows state              
                self.shadowMaker.addShadow(self.x, self.y, common["ViewW"],common["ViewH"])
                self.works.closeWidget()   
                self.shadow = self.shadowMaker.shadow  
                
    def toggleThisTag(self, id):
        if self.shadowMaker.shadow != None and self.shadowMaker.linked:
            return
        else:
            self.mapper.toggleTagItems(id)
                
    def addWidget(self):  ## won't work in works 
        self.works.closeWidget()
        self.widget = PixWidget(self)      
        x, y = self.works.makeXY()     
        x = int(x - int(self.widget.WidgetW)-20)
        y = int(y - int(self.widget.WidgetH)*.20)
        self.widget.save = QPointF(x,y)
        self.widget.setGeometry(x, y, int(self.widget.WidgetW), int(self.widget.WidgetH))
        self.works.resetSliders()
        self.setLockBtnText()
                         
    def setMirrored(self, bool): 
        self.flopped = bool
        self.setPixmap(QPixmap.fromImage(self.imgFile.mirrored(
            horizontal=self.flopped, vertical=False)))
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

### --------------------------------------------------------       
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
     
    def setLockBtnText(self):
        if self.widget != None:
            if self.locked == False:
                self.widget.lockBtn.setText('Lock')  ## keep it open  
            else:
                self.widget.lockBtn.setText('UnLock')  ## keep it open  
                
    def togglelock(self):
        if self.locked == False:
            self.locked = True     
            self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
        else:
            self.locked = False
            self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True) 
        tagBkg(self, self.pos())
        QTimer.singleShot(3000, self.mapper.clearTagGroup)
   
    def deletePix(self):
        if self.shadowMaker != None and self.shadowMaker.isActive == True:
            self.shadowMaker.works.deleteShadow()
        self.works.closeWidget()
        self.anime 
        self.anime = Anime.fin(self)
        self.anime.start()
        self.anime.finished.connect(self.works.removeThis)
                
### -------------------- dotsPixItem -----------------------


         
