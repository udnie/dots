
from PyQt6.QtCore       import Qt, QTimer, QPoint, pyqtSlot, QPointF
from PyQt6.QtGui        import QImage, QPen, QPixmap, QColor, QCursor
from PyQt6.QtWidgets    import QGraphicsPixmapItem

from dotsShared         import common, MoveKeys, RotateKeys, ControlKeys
from dotsPixWorks       import Works
from dotsPixWidget      import PixWidget
from dotsSideGig        import MsgBox
from dotsBkgScrollWrks  import tagBkg
from dotsHelpMonkey     import PixHelp

##from dotsShadowMaker    import ShadowMaker  ## uncomment to add shadows otherwise comment out
from dotsShadow_Dummy    import ShadowMaker  ## uncomment turns off shadows - you need to do both

from dotsAnimation      import fin

TagKeys = ('/','enter','return') 
SharedKeys = ('F','H','T','del','tag','shift','enter','return')

### --------------------- dotsPixItem ----------------------
''' dotsPixItem: primary dots screen object - like a sprite 
                    helpMenu in HelpDeck '''
### --------------------------------------------------------
class PixItem(QGraphicsPixmapItem):
### --------------------------------------------------------
    def __init__(self, fileName, id, x, y, parent, mirror=False, str=''):
        super().__init__()

        self.canvas = parent
        self.scene  = self.canvas.scene
        self.mapper = self.canvas.mapper
        
        self.type = 'pix'
        self.fileName = fileName
  
        self.widgetOn = False   
        self.flopped = mirror
        self.id = int(id)  ## used by mapper

        self.x = x 
        self.y = y
        
        self.shadow = None  ## a dictionary to maintain shadow data if there is one
        self.shadowMaker = ShadowMaker(self)  ## returns isActive equals False if from shadow_dummy
        
        self.works = Works(self.canvas, self)  ## functions and PixSizes moved from here
        self.help = None
          
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
        self.sharedKeys = SharedKeys
  
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
    @pyqtSlot(str)  ## updated by storyboard directly 
    def setPixKeys(self, key):  ## the decorator is suppose to get a better response
        self.key = key  
 
        if self.isHidden or self.isSelected():
            if self.locked == False:
                if key in RotateKeys:
                    self.works.rotateThis(key)
                elif key in ("<",">"):
                    self.works.scaleThis(key)  
                elif key in MoveKeys:
                    self.moveThis(MoveKeys[key])
                    
    def mousePressEvent(self, e):    
        if self.canvas.animation == False:  ## 'resume', 'pause' - animation running
            ## right mouse clk triggers Animation menu (context menu) on selected screen items
            if e.button() == Qt.MouseButton.RightButton:
                if len(self.scene.selectedItems()) == 0:
                    self.addWidget()  ## nothing selected - add pixWidget
                    e.accept()
            elif self.key in self.sharedKeys:
                self.shared(self.key)                  
            self.initX, self.initY = self.x, self.y  
            self.dragAnchor = self.mapToScene(e.pos())
        e.accept()

    def shared(self, key):  ## with help menu
        self.key = key
        if self.key == 'del':    
            self.deletePix()        
        elif self.key == 'shift': 
            self.setZValue(self.pix.zValue()-1)      
        elif self.key in('enter','return'): # send to front
            self.setZValue(self.mapper.toFront(1))
        elif self.key == 'tag': ## '\' backslash
            self.tagThis()            
        elif self.key == 'F':  ## flop it
            self.setMirrored(False) if self.flopped else self.setMirrored(True)  
        elif self.key == 'H':  
            self.openMenu()     
        elif self.key == 'T':     
            self.togglelock()
  
    def tagThis(self):
        p = QCursor.pos()
        tagBkg(self, self.canvas.mapFromGlobal(QPoint(p.x(), p.y()-20)))
    
    def openMenu(self):
        self.works.closeWidget()
        x, y = self.works.makeXY()  
        self.help = PixHelp(self, x, 'pix')
            
### --------------------------------------------------------
    def mouseMoveEvent(self, e):
        if 'frame' in self.fileName or self.locked:
            return
        if self.canvas.control not in ControlKeys:  ## 'resume', 'pause' - animation running
            if self.key in TagKeys or self.mapper.tagSet:
                self.works.clearTag() 
            self.works.updateXY(self.mapToScene(e.pos()))
            self.setPos(self.x, self.y)
            self.dragCnt +=1
            if self.key == 'opt' and self.dragCnt % 10 == 0:  
                self.works.cloneThis() 
        e.accept()
            
    def mouseReleaseEvent(self, e): 
        self.key = ''
        self.dragCnt = 0   
        self.works.updateXY(self.mapToScene(e.pos()))
        self.setPos(self.x, self.y)  
        e.accept()
        
    def mouseDoubleClickEvent(self, e):
        if self.canvas.control not in ControlKeys:  ## 'resume', 'pause' - animation running
            if self.canvas.key == 'noMap':   ## consumed map's dblclk need to set it back 
                self.canvas.setKeys('')      
                if self.isHidden == False or self.isSelected():
                    self.setSelected(True) 
                    return      
            if self.locked == True:
                self.tagThis()      
            if self.isHidden:  ## otherwise you're stuck if others are selected as the others will become hidden
                self.setSelected(True) 
                self.isHidden = False  
            elif self.canvas.key not in self.sharedKeys:
                if self.isSelected() == False:
                    self.setSelected(True)  
                elif self.isSelected():
                    self.setSelected(False)
                self.isHidden = False 
        e.accept()

### --------------------------------------------------------
    def itemChange(self, change, value):  ## continue to updatePath when animated
        if self.shadowMaker != None and self.shadowMaker.isActive and self.shadowMaker.linked == True:
            if change == QGraphicsPixmapItem.GraphicsItemChange.ItemScenePositionHasChanged: 
                self.shadowMaker.shadow.setPos(self.pos()+ self.offset)      
        return super(QGraphicsPixmapItem, self).itemChange(change, value)

### --------------------------------------------------------
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
            self.mapper.toggleTagItems(id)  ## display
                                         
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
            self.lockSprite()
        else:
            self.unlockSprite()
        tagBkg(self, self.pos())
        QTimer.singleShot(3000, self.mapper.clearTagGroup)
        
    def lockSprite(self):
        self.locked = True     
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
        
    def unlockSprite(self):
        self.locked = False
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True) 
   
    def deletePix(self):
        if self.shadowMaker != None and self.shadowMaker.isActive == True:
            self.shadowMaker.works.deleteShadow()
        self.works.closeWidget()
        self.anime 
        self.anime = fin(self)
        self.anime.start()
        self.anime.finished.connect(self.works.removeThis)
                
### -------------------- dotsPixItem -----------------------


     # elif change == QGraphicsPixmapItem.GraphicsItemChange.ItemRotationChange:  ## experiment
            #     self.shadowMaker.shadow.setRotation(value)
            # elif change == QGraphicsPixmapItem.GraphicsItemChange.ItemScaleChange:
            #     self.shadowMaker.shadow.setScale(value)      
            # elif change == QGraphicsPixmapItem.GraphicsItemChange.ItemOpacityChange:
            #     self.shadowMaker.shadow.setOpacity(value-.50) 
            
         
