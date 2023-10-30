
from PyQt6.QtCore       import Qt, QPoint, QPointF
from PyQt6.QtGui        import QColor, QPainter, QPainterPath, QBrush, QImage
from PyQt6.QtWidgets    import QWidget
    
from dotsShared         import common, paths

ShiftKeys = (Qt.Key.Key_R, Qt.Key.Key_P, Qt.Key.Key_S)

### -------------------- dotsBkgMatte ----------------------
''' class: Matte '''        
### --------------------------------------------------------
class Matte(QWidget):
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()

        self.bkgItem = parent 
        self.canvas  = self.bkgItem.canvas
         
        self.type = 'widget'       
        self.save = QPointF()
     
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.FramelessWindowHint|\
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.NoDropShadowWindowHint|\
            Qt.WindowType.WindowStaysOnTopHint) 

        self.setAccessibleName('widget')
        self.setStyleSheet('background-color: rgba(0,0,0,0)')
        
        p = self.canvas.mapToGlobal(QPoint())
        
        self.x = p.x()
        self.y = p.y()
    
        self.black = QBrush(QColor('black'))
        self.grey  = QBrush(QColor(250,250,250))
        self.pix   = None
        
        self.img = QImage(paths['bkgPath'] + 'abstract.jpg')  ## used as a matte
    
        self.border = 100  ## inital
        self.step   = 25
        self.stop   = 50  ## min y.() - Max Headroom
        self.brush  = self.grey  ## default   
          
        self.ratio = 1.0    
        self.altRatio = .77 ##.55 = 16:9 # .77  
        self.resize(common['ViewW']+100, common['ViewH']+100) 
        
        self.move(self.x, self.y) 
        
        self.grabKeyboard()
        
        self.show()
 
### --------------------------------------------------------
    def paintEvent(self, e):            
        qp = QPainter()
        qp.begin(self)
 
        path = QPainterPath() 
    
        viewW = int(common['ViewW']+(self.border*2))
        viewH = int(common['ViewH']+(self.border*2)*self.ratio)
    
        self.resize(viewW, viewH) 
    
        path.addRect(0, 0, viewW, viewH)  ## outer
        path.addRect(self.border+2, int(self.border*self.ratio)+2, common['ViewW']-4, int(common['ViewH'])-2)  ## inner
  
        if self.pix != None:   
            self.pix= self.img.scaled(viewW, viewH,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation)      
            self.brush = QBrush(self.pix)
      
        qp.setBrush(self.brush)  
        qp.drawPath(path)
        
        self.move(self.x-self.border, int(self.y-(self.border)*self.ratio))
                
        qp.end()
        
### --------------------------------------------------------
    def keyPressEvent(self, e):
        key = e.key()   
        mod = e.modifiers()
     
        if key in ShiftKeys and mod & Qt.KeyboardModifier.ShiftModifier:  
            if key == Qt.Key.Key_R: 
                self.canvas.showtime.run()
            elif key == Qt.Key.Key_P: 
                self.canvas.showtime.pause()
            else:
                self.canvas.showtime.stop()

        elif key == Qt.Key.Key_Greater:  ## scale up  
            self.scaleThis(key)
            if self.y-(self.border*self.ratio) <= self.stop:
                self.border -= self.step ## back it off
                
        elif key == Qt.Key.Key_Less:  ## scale down
            self.scaleThis(key)   
                   
        elif key in (Qt.Key.Key_Alt, Qt.Key.Key_X):
            self.bkgItem.matte = None
            self.close()         
            
        elif key in (Qt.Key.Key_B, Qt.Key.Key_C):  ## change color
            if self.pix != None:
                self.pix = None
                self.brush = self.grey
                
            elif key == Qt.Key.Key_B:
                self.brush = self.black
                
            elif self.brush == self.grey:
                self.brush = self.black
                
            elif self.brush == self.black:
                self.brush = self.grey      
                       
        elif key == Qt.Key.Key_P:  ## use pix 
            if self.pix == None:    
                self.pix = self.img  ## something to initialize it  
                # self.brush = QBrush(self.pix)  ## handled in painter
            else:
                self.pix = None
                self.brush = self.grey      
                        
        elif key == Qt.Key.Key_R:  ## set screen format ratio to around .61 
            if self.ratio == 1.0:  ## midway between 16:9 and 3:2 - approx .56/.66
                self.ratio = self.altRatio  ## this value works
            else:
                self.ratio = 1.0   
                 
        self.update()
        e.accept()
    
    def scaleThis(self, key):
        if key == Qt.Key.Key_Greater:
            if self.border == 5:
                self.border = 12     
            elif self.border == 12: 
                self.border = self.step  
            elif self.border >= self.step:
                self.border += self.step             
        else:    
            if self.border == self.step: 
                self.border = 12  
            elif self.border == 12:
                self.border = 5
            elif self.border > self.step:
                self.border -= self.step            
                          
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
        self.move(self.pos() + QPoint(int(dif.x()), int(dif.y())))
        self.save = e.globalPosition()

### -------------------- dotsBkgMatte ----------------------


