 
from PyQt6.QtCore       import Qt, QPointF,  QPoint
from PyQt6.QtGui        import QColor, QPen            
from PyQt6.QtWidgets    import QGraphicsRectItem, QWidget, QGraphicsView
                        
InitSet = (275, 300)  ## initial x,y settings for LoupeWidget
LW = 475  ## loupeWidget
SR = 300  ## rect
XY = 60
WH = 120
NK = 150

ViewW, ViewH = 720, 720

### ---------------------- LoupeWidget  --------------------
''' classes: LoupeWidget, Loupe '''     
### --------------------------------------------------------        
class LoupeWidget(QWidget):  ## the display
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()
         
        self.spriteMaker = parent
        self.scene       = parent.scene
        self.loupe       = parent.loupe
        
        self.view = QGraphicsView(self)
        self.view.setScene(self.scene)
        
        self.view.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)   
        
        self.view.scale(1.5, 1.5)
        self.view.setGeometry(0, 0, LW, LW)
        self.setStyleSheet("border: 17px solid lightgrey;")
            
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)
         
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.view.horizontalScrollBar().setDisabled(True)
        self.view.verticalScrollBar().setDisabled(True)
     
        self.setFixedSize(LW, LW) 
        self.save = self.pos() 
                             
        self.show()
                       
### --------------------------------------------------------                      
    def mousePressEvent(self, e):
        self.save = e.globalPosition() 
        e.accept()

    def mouseMoveEvent(self, e):
        self.moveThis(e)
        e.accept()
        
    def mouseReleaseEvent(self, e):
        self.save = e.globalPosition() 
        self.moveThis(e)
        e.accept()
            
    def moveThis(self, e):
        if self.loupe.hold:
            return    
        dif = e.globalPosition() - self.save      
        self.move(self.pos() + QPoint(int(dif.x()), int(dif.y())) )
        self.save = e.globalPosition() 
        self.update()
            
    def mouseDoubleClickEvent(self, e):
        self.loupe.closeLoupe()
        e.accept()
        
### --------------------------------------------------------                        
class Loupe: 
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()
                    
        self.spriteMaker = parent
        self.scene       = parent.scene
        self.works       = parent.works
        
        self.lastX, self.lastY = InitSet[0], InitSet[1]
  
        self.init() 
                                  
### --------------------------------------------------------          
    def init(self):         
        self.hold = False 
        
        self.idx = 0
        self.x, self.y = 0.0, 0.0
        
        self.rect = None  
        self.frame = None 
        self.spriteMaker.loupeWidget = None
 
### -------------------------------------------------------- 
    def loupeit(self, idx):  ## moves the loupe by a point
        if self.spriteMaker.loupeWidget != None:
            self.removeRect()  ## leave widget up - also toggle for rect
        else:
            self.spriteMaker.loupeWidget = LoupeWidget(self.spriteMaker)
            self.spriteMaker.loupeWidget.move(self.lastX, self.lastY)       
        try:
            p = self.spriteMaker.pts[idx]  ## x,y is center of rect - see addRect  
        except: 
            idx = 0
        self.x, self.y, self.idx = p.x(), p.y(), idx       
        if not self.hold:
            self.spriteMaker.loupeWidget.view.centerOn(QPointF(self.x, self.y))
            self.rect = self.addRect(self.x, self.y) 
            if self.rect != None:
                self.scene.addItem(self.rect)              
        self.markPoint()
        self.scene.update()
                                                                     
    def markPoint(self):
        self.spriteMaker.redrawPoints()  
        for p in self.scene.items():
            if p.type == 'pt' and p.idx == self.idx:
                p.markit()
                break                                 
                                                             
    def nextPoint(self, key):
        i = self.idx        
        if key == 'next':
            i = i + 1
            if i == len(self.spriteMaker.pts):  
                i = 0                            
        else: 
            i = i - 1
            if i == -1: 
                i = len(self.spriteMaker.pts)-1                 
        self.loupeit(i)                          
                                                
### --------------------------------------------------------
    def addRect(self, x, y): 
        if self.rect != None: 
            self.scene.removeItem(self.rect)
            self.rect = None
     
        ## more work than necessary - maps from global - settled on scene
        xmap, ymap, flag = x-NK, y-NK, False
        mfs = self.spriteMaker.view.mapFromScene(self.x, self.y)   
        ctr = self.spriteMaker.view.viewport().mapToGlobal(mfs)
        upl = self.spriteMaker.view.viewport().mapToGlobal(QPoint(0,0))
        uplx, uply = upl.x(), upl.y() 
    
        if  ctr.x()-NK < uplx:             
            xmap = 0   
        elif ctr.y()-NK < uply:   
            ymap = 0  
        elif ctr.x()+NK > uplx+ViewW:
            xmap = ViewW-SR      
        elif ctr.y()+NK > uply+ViewH:
            ymap = ViewH-SR
    
        rect = QGraphicsRectItem(xmap, ymap, SR, SR)
        rect.setPen(QPen(QColor('lime'), 2.5, Qt.PenStyle.SolidLine)) 
        
        rect.setZValue(110)
        return rect
    
    def removeRect(self): 
        if not self.hold and self.rect != None:
            try:
                self.scene.removeItem(self.rect)
                self.rect = None
            except:
                None
        self.spriteMaker.updateOutline() 
  
    def addFrame(self):
        self.removeFrame()
        self.frame = QGraphicsRectItem(XY, XY, ViewW-WH, ViewH-WH)
        self.frame.setPen(QPen(QColor('lime'), 2, Qt.PenStyle.DotLine)) 
        self.frame.setZValue(300)
        self.scene.addItem(self.frame)
        
    def removeFrame(self):
        if self.frame != None:
            self.scene.removeItem(self.frame)
            self.frame = None
        
### --------------------------------------------------------     
    def holdIt(self):
        if self.spriteMaker.loupeWidget != None:
            if not self.hold:
                self.hold = True
                try:
                    if self.rect != None:
                        self.scene.removeItem(self.rect)
                        self.rect = None
                except:
                    None
                self.spriteMaker.loupeWidget.setStyleSheet("border: 17px solid rgb(150,150,150);")
            else:
                self.setHoldOff()
                    
    def setHoldOff(self):
        self.hold = False
        try:
            self.addRect(self.lastX, self.lastY)
        except:
            None
        self.spriteMaker.loupeWidget.setStyleSheet("border: 17px solid lightgrey;")
        self.loupeit(self.idx)
     
### --------------------------------------------------------        
    def closeLoupe(self):  ## from loupeWidget
        self.removeRect()
        self.closeWidget()
        
    def closeWidget(self):
        if self.spriteMaker.loupeWidget != None:
            p = self.spriteMaker.loupeWidget.pos()
            self.lastX = p.x()
            self.lastY = p.y()
            self.spriteMaker.loupeWidget.close()
            self.spriteMaker.loupeWidget = None
            
    def deletePointItem(self, idx):  
        self.spriteMaker.pts.pop(idx)
        self.spriteMaker.updateOutline() 
        self.spriteMaker.redrawPoints()      
        self.loupeit(idx-1)    
        self.works.redrawSprite()
        
    def insertPointItem(self, pointItem):  ## halfway between points        
        idx, pt = pointItem.idx + 1, pointItem.pt  ## idx, the next point
        if idx == len(self.spriteMaker.pts): 
            idx = 0    
        pt1 = self.spriteMaker.pts[idx]  ## calculate new x,y
        pt1 = QPointF(pt1.x() - pt.x(), pt1.y() - pt.y())
        pt1 = QPointF(pt) + pt1*.5      
        self.spriteMaker.pts.insert(idx, pt1)
        self.spriteMaker.updateOutline() 
        self.spriteMaker.redrawPoints()   
        self.loupeit(idx)
          
### ------------------- LoupeWidget.py ---------------------




