 
from PyQt6.QtCore       import Qt, QPointF,  QPoint
from PyQt6.QtGui        import QColor, QPen            
from PyQt6.QtWidgets    import QGraphicsRectItem, QWidget, QGraphicsView
                        
InitSet = (275, 250)  ## initial x,y settings for LoupeWidget
LW = 475


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
        
        ## qt-warning fix
        self.view.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)   
        
        self.view.scale(1.5, 1.5)
        self.view.setGeometry(0, 0, LW, LW)
        self.setStyleSheet("border: 12px solid lime;")
            
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)
         
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        ## no more two finger scrolling
        self.view.horizontalScrollBar().setDisabled(True)
        self.view.verticalScrollBar().setDisabled(True)
     
        self.setFixedSize(LW, LW) 
                             
        self.show()
                       
### --------------------------------------------------------                      
    def mousePressEvent(self, e):
        self.save = e.globalPosition() 
        e.accept()

    def mouseMoveEvent(self, e):
        self.moveThis(e)
        e.accept()
        
    def mouseReleaseEvent(self, e):
        self.moveThis(e)
        e.accept()
            
    def moveThis(self, e):
        dif = e.globalPosition() - self.save      
        self.move(self.pos() + QPoint(int(dif.x()), int(dif.y())) )
        self.save = e.globalPosition() 
        self.update()
            
    def mouseDoubleClickEvent(self, e):
        self.loupe.close()
        e.accept()
        
### --------------------------------------------------------                        
class Loupe(QWidget):  ## selection square
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
        self.rect   = None             
        self.widget = None
        self.hold   = False
        
        self.x, self.y, self.idx = 0.0, 0.0, 0
                
### -------------------------------------------------------- 
    def loupeIt(self, idx):
        if self.widget:
            self.removeRect()  ## leave widget up - also toggle for rect
        else:
            self.widget = LoupeWidget(self.spriteMaker)
            self.widget.move(self.lastX, self.lastY)           
           
        p = self.spriteMaker.pts[idx]  ## x,y is center of rect - see addRect   
        self.x, self.y, self.idx = p.x(), p.y(), idx 
           
        if not self.hold:
            self.widget.view.centerOn(QPointF(self.x, self.y))
            self.rect = self.addRect(self.x, self.y) 
            self.scene.addItem(self.rect)
            
        self.markPoint()
                                                  
### --------------------------------------------------------
    def addRect(self, x, y): 
        if self.rect: self.scene.removeItem(self.rect)
            
        if x-70 <= 0: x = 71      
        if y-70 <= 0: y = 71
        
        if x+70 >= 720: x = 649
        if y+70 >= 720: y = 649
        
        ## 'no matter where you go, there you are' -- Jim, Taxi 
        rect = QGraphicsRectItem(x-150, y-150, 300, 300)
        rect.setPen(QPen(QColor('lime'), 2.5, Qt.PenStyle.SolidLine)) 
        rect.setZValue(110)
        return rect
             
    def markPoint(self):
        self.spriteMaker.redrawPoints()  
        for p in self.scene.items():
            if p.type == 'pt' and p.idx == self.idx:
                p.setBrush(QColor('cyan'))
                break
     
    def holdIt(self):
        if self.widget:
            if not self.hold:
                self.hold = True
                self.rect.hide()  
                self.widget.setStyleSheet("border: 12px solid orangered;")
            else:
                self.hold = False
                self.rect.show()
                self.widget.setStyleSheet("border: 12px solid lime;")
        
    def closeWidget(self):
        if self.widget:
            p = self.widget.pos()
            self.lastX = p.x()
            self.lastY = p.y()
            self.widget.close()
            self.widget = None 
                       
    def nextPoint(self, key):  ## arrow up and arrow down - runs from spriteMaker 
        if self.widget:             
            i = self.idx            
            if key == 'up':
                i = i + 1
                if i == len(self.spriteMaker.pts):  
                    i = 0                            
            else: 
                i = i - 1
                if i == 0: 
                    i = len(self.spriteMaker.pts)-1                      
            self.loupeIt(i)
                              
### --------------------------------------------------------
    def removeRect(self): 
        if self.rect and not self.hold:
            self.scene.removeItem(self.rect)
            self.rect = None
        self.spriteMaker.updateOutline() 
        
    def close(self):
        self.removeRect()
        self.closeWidget()
            
    def deletePointItem(self, idx):  
        self.spriteMaker.pts.pop(idx)
        self.spriteMaker.updateOutline() 
        self.spriteMaker.redrawPoints()      
        self.loupeIt(idx-1)
        
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
        self.loupeIt(idx)
          
### ------------------- LoupeWidget.py ---------------------

