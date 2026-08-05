
import time

from PyQt6.QtCore       import Qt, QPoint
from PyQt6.QtGui        import QImage, QPixmap, QPen, QColor                 
from PyQt6.QtWidgets    import QGraphicsPixmapItem, QGraphicsLineItem, \
                                QGraphicsEllipseItem
                                                   
from wrapperWorks       import ViewW, ViewH

### --------------------------------------------------------
class BasicBkg(QGraphicsPixmapItem):  
### --------------------------------------------------------
    def __init__(self, parent, file):
        super().__init__()

        self.parent = parent   
        self.fileName = file
         
        self.initX = 0
        self.dragAnchor = QPoint()
   
    def mousePressEvent(self, e): 
        self.initX = self.pos().x()
        self.dragAnchor = self.mapToScene(e.pos())
        e.accept()
   
    def mouseMoveEvent(self, e):
        if self.parent.guidesOn:
            return
        self.updateXY(self.mapToScene(e.pos()))
        self.setPos(self.x, 0)
        e.accept() 
    
    def updateXY(self, pos):
        dragX = pos.x() - self.dragAnchor.x() 
        self.x = self.initX + dragX
   
### --------------------------------------------------------
class BkgItem(BasicBkg):  
### --------------------------------------------------------
    def __init__(self, parent, file, side=''):
        super().__init__(parent, file)
        
        self.parent = parent
        
        img = QImage(file)       
        img = img.scaledToHeight(ViewH,  
            Qt.TransformationMode.SmoothTransformation)

        self.imgFile = img   
        self.side = side
        
        self.x = 0 
        self.y = 0
     
        self.setPixmap(QPixmap.fromImage(self.imgFile))   
        
        if self.side == 'bkg':
            self.setPos(-1,0)
        elif self.side == 'blended':
            self.setFlag(QGraphicsLineItem.GraphicsItemFlag.ItemIsMovable)
        else:
            self.setLeft() if self.side == 'left' else self.setRight()

    def setLeft(self):
        self.start = int((ViewW/2)- self.imgFile.width())  
        self.setPos(self.start, 0)
      
    def setRight(self):
        self.start = int(ViewW/2) 
        self.setPos(self.start, 0)
   
### --------------------------------------------------------
class Handle(QGraphicsEllipseItem):  ## google query
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__(-10, -5, 20, 20, parent)  ## setting claude
        
        self.setBrush(QColor('coral'))
        self.setPen(QColor('coral'))

        self.setFlags(self.GraphicsItemFlag.ItemIsMovable | 
            self.GraphicsItemFlag.ItemSendsScenePositionChanges)

    def itemChange(self, change, value):
        if change == self.GraphicsItemChange.ItemPositionChange:
            value.setY(ViewH // 2)  ## claude
            clamped = self.parentItem().clampedX(value)  # set clamped 
            value.setX(clamped)
            self.parentItem().updateCropGuide(value)
        return super().itemChange(change, value)  # now value is clamped
                                                                                
### --------------------------------------------------------
class Guide(QGraphicsLineItem):
### --------------------------------------------------------
    def __init__(self, parent, x1, y1, x2, y2, code):
        super().__init__()
             
        self.parent = parent
        self.code = code
        self.handle = None
        
        self.initX = 0
        self.dragAnchor = QPoint()
        
        self.setLine(x1, y1, x2, y2)

        if code == 'vu2':
            pen = QPen(QColor("yellow"))
            pen.setWidth(2)   
             
        elif code == 'ctr':
            pen = QPen(QColor("dodgerblue"))
            pen.setWidth(3) 
            
        elif code == 'end':
            pen = QPen(QColor("cyan"))
            pen.setWidth(2)   
            
        else:  ## crop
            self.setFlag(QGraphicsLineItem.GraphicsItemFlag.ItemIsMovable)
            pen = QPen(QColor("coral"))
            pen.setWidth(5)
            
        pen.setStyle(Qt.PenStyle.SolidLine) 
        self.setPen(pen)    
           
        self.setZValue(400)      
     
        if code == 'crop':   
            self.handle = Handle(self)
            self.handle.setPos(x1, ViewH//2)
              
### -------------------------------------------------------- 
    def mousePressEvent(self, e): 
        if self.code == 'crop':
            self.initX = self.pos().x()
            self.dragAnchor = self.mapToScene(e.pos())
            e.accept()
        
    def mouseMoveEvent(self, e):
        if self.code == 'crop':
            p = self.mapToScene(e.pos())
            self.updateXY(p)
            self.setPos(self.x, 0)
            self.parent.works.setNewSlice(p.x())
            e.accept()
   
    def updateXY(self, pos):
        dragX = pos.x() - self.dragAnchor.x() 
        self.x = self.initX + dragX
        
    def clampedX(self, pos): 
        if self.code == 'crop':
            ns = int(ViewW//2 ) - abs(int(pos.x()))- self.parent.blendWidth//2 
            if ns < 0:
                limit = int(ViewW//2) - self.parent.blendWidth//2  ## claude
                return limit  
            return pos.x()

    def updateCropGuide(self, pos):  ## claude
        if self.code == 'crop':
            self.setLine(pos.x(), 0, pos.x(), ViewH)
            self.parent.works.setNewSlice(pos.x())
                     
### ------------------------ Guides ------------------------                                                                                                                                                                                                                                                                           
class Guides:  
### --------------------------------------------------------       
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.scene  = parent.scene
  
### --------------------------------------------------------
    def addGuides(self): 
        if self.parent.blended != None:
            save = self.parent.newSlice
            self.deleteGuides()  
            
            vu2 = ViewW//2  ## screen not blended
            self.parent.newSlice = save 
            
            for code in ['vu2','ctr','end','crop']:
                match code:
                    case 'vu2':
                        self.guide = Guide(self.parent, vu2, 0, vu2, ViewH, code)
                    case'ctr':   
                        h = self.parent.blendWidth//2
                        self.guide = Guide(self.parent, vu2-h, 0, vu2-h, ViewH, code) 
                    case'end':
                        w = self.parent.blendWidth
                        self.guide = Guide(self.parent, vu2-w, 0, vu2-w, ViewH, code) 
                    case'crop': 
                        n = self.parent.newSlice 
                        self.guide = Guide(self.parent, vu2-n, 0, vu2-n, ViewH, code) 
                try:
                    self.parent.scene.addItem(self.guide)
                except:
                    self.parent.msgbox('Error: adding Guides') 
                    return False   
                                
            self.parent.guidesOn = True
            time.sleep(.02)
            return True
    
    def deleteGuides(self):
        for p in self.parent.scene.items():
            if isinstance(p, QGraphicsLineItem):
                self.scene.removeItem(p)
                del p
        self.parent.guidesOn = False
        time.sleep(.02)
           
    def updateGuides(self):
        vu2 = ViewW//2
        for p in self.parent.scene.items():
            if isinstance(p, QGraphicsLineItem):
                if p.code == 'ctr':   
                    h = self.parent.blendWidth//2
                    p.setLine(float(vu2-h), 0, float(vu2-h),  ViewH)
                elif p.code == 'end':
                    w = self.parent.blendWidth
                    p.setLine(float(vu2-w), 0, float(vu2-w),  ViewH)
                elif p.code == 'crop': 
                    n = self.parent.newSlice 
                    p.setLine(float(vu2-n), 0, float(vu2-n),  ViewH)
       
    def toggleGuides(self):
        self.addGuides() if not self.parent.guidesOn else \
            self.deleteGuides()
                       
### --------------------- that's all -----------------------




