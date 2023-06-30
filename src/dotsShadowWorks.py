
import cv2
import numpy as np

from PyQt6.QtCore       import Qt, QPointF, QPoint, QRectF
from PyQt6.QtGui        import QColor, QPen, QPainter
from PyQt6.QtWidgets    import QSlider, QWidget, QGroupBox, QGraphicsPixmapItem, \
                               QLabel, QSlider, QHBoxLayout,  QVBoxLayout, QPushButton, \
                               QGraphicsEllipseItem, QDial
                               
from dotsShared         import common

PathStr = ['topLeft','topRight','botRight','botLeft']
V = common['V']  ## the diameter of a pointItem, same as in ShadowWorks

### ------------------- dotsShadowWorks --------------------
''' classes: PointItem, ShadowWidget, Shadow, and cv2 functions '''
### --------------------------------------------------------
class PointItem(QGraphicsEllipseItem):  ## not to be confused with pathMaker's PointItem
### --------------------------------------------------------
    def __init__(self, pt, ptStr, parent):
        super().__init__()

        self.maker   = parent
        self.pixitem = self.maker.pixitem
        self.path    = self.maker.path
         
        self.ptStr = ptStr
        
        self.type  = 'point'
        self.fileName = 'point'
        self.tag = 'point'
        
        self.dragCnt = 0
          
        ## -V*.5 so it's centered on the path 
        self.x = pt.x()-V*.5
        self.y = pt.y()-V*.5
        
        self.setZValue(common['points'])      
        self.setRect(self.x, self.y, V, V)  
        
        self.setPen(QPen(QColor('gray'), 1))
        if self.ptStr in ('topLeft','topRight'):
            self.setBrush(QColor('yellow'))
        else:
            self.setBrush(QColor('lime'))
                        
 ### --------------------------------------------------------
    def mousePressEvent(self, e):  
        e.accept() 
        
    def mouseMoveEvent(self, e):
        self.dragCnt += 1
        if self.dragCnt % 5 == 0:            
            self.moveIt(e.pos()) 
            self.maker.updateShadow()                  
        e.accept()
                       
    def mouseReleaseEvent(self, e):
        self.moveIt(e.pos())
        self.maker.updateShadow()
        e.accept()
                                        
    def moveIt(self, e):     
        pos = self.mapToScene(e)
        x, y = pos.x(), pos.y()
        self.setRect(x-V*.5, y-V*.5, V,V)  ## set current point    
        if self.ptStr == 'topLeft':  ## push right
            w, y1 = self.current(0,1)            
            self.path[0] = QPointF(x,y) 
            self.path[1] = QPointF(x+w,y1)
            self.maker.topRight.setRect(x+(w-V*.5), y1-V*.5, V,V)       
        elif self.ptStr == 'botLeft':    
            w, y1 = self.current(3,2)            
            self.path[3] = QPointF(x,y) 
            self.path[2] = QPointF(x+w,y1)
            self.maker.botRight.setRect(x+(w-V*.5), y1-V*.5, V,V)          
        else:  
            i = PathStr.index(self.ptStr)  ## move only 
            self.path[i] = QPointF(x,y)                  
        
    def current(self,a,b):
        l = self.path[a].x()
        r = self.path[b].x()
        return r - l,  self.path[b].y()

### --------------------------------------------------------        
class ShadowWidget(QWidget): 
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()
                                        
        self.maker = parent
        self.pixitem = self.maker.pixitem
        
        self.type = 'widget'
        self.save = QPointF(0.0,0.0)
                
        self.setAccessibleName('widget')
        self.WidgetW, self.WidgetH = 330.0, 200.0
                
        hbox = QHBoxLayout()
        hbox.addWidget(self.sliderGroup())
        hbox.addSpacing(5) 
        hbox.addWidget(self.buttonGroup())
        self.setLayout(hbox)
        
        self.setFixedHeight(int(self.WidgetH))
        self.setStyleSheet('background-color: rgba(0,0,0,0)')
        self.setContentsMargins(0,15,0,-15)
             
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)
                                
        self.show()
                
### --------------------------------------------------------                                   
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)   
        rect = QRectF(2, 2, self.WidgetW-4, self.WidgetH-4)                   
        painter.setPen(QPen(QColor(0,80,255), 5, Qt.PenStyle.SolidLine,            
            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(QColor(0,150,245,255))
        painter.drawRoundedRect(rect, 15, 15)
              
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
        
    def mouseDoubleClickEvent(self, e):
        self.maker.closeWidget()
        e.accept()
        
### -------------------------------------------------------- 
    def sliderGroup(self):
        groupBox = QGroupBox('Rotate     Scale   Opacity   ')
        
        groupBox.setFixedWidth(170)
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
   
        self.rotateValue = QLabel('0', alignment=Qt.AlignmentFlag.AlignCenter)
        self.rotaryDial = QDial()
        self.rotaryDial.setMinimum(0)
        self.rotaryDial.setMaximum(360)
        self.rotaryDial.setValue(0)
        self.rotaryDial.setFixedWidth(60)
        self.rotaryDial.setWrapping(False)
        self.rotaryDial.setNotchesVisible(True)
        self.rotaryDial.setNotchTarget(15.0)
        self.rotaryDial.valueChanged.connect(self.Rotate)
    
        self.scaleValue = QLabel('1.00')
        self.scaleSlider = QSlider(Qt.Orientation.Vertical)   
        self.scaleSlider.setMinimum(25)
        self.scaleSlider.setMaximum(225)
        self.scaleSlider.setSingleStep(1)
        self.scaleSlider.setValue(100)
        self.scaleSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scaleSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.scaleSlider.setTickInterval(25)  
        self.scaleSlider.valueChanged.connect(self.Scale)   
        
        self.opacityValue = QLabel('.50')
        self.opacitySlider = QSlider(Qt.Orientation.Vertical)   
        self.opacitySlider.setMinimum(0)
        self.opacitySlider.setMaximum(100)
        self.opacitySlider.setSingleStep(1)
        self.opacitySlider.setValue(50) 
        self.opacitySlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.opacitySlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.opacitySlider.setTickInterval(16)  
        self.opacitySlider.valueChanged.connect(self.Opacity)
                  
        sbox = QHBoxLayout()  ## sliders  
        sbox.addSpacing(-10)    
        sbox.addWidget(self.rotaryDial)  
        sbox.addSpacing(10)       
        sbox.addWidget(self.scaleSlider) 
        sbox.addSpacing(10)                
        sbox.addWidget(self.opacitySlider) 
        
        vabox = QHBoxLayout()  ## values
        vabox.addSpacing(0) 
        vabox.addWidget(self.rotateValue)        
        vabox.addSpacing(0) 
        vabox.addWidget(self.scaleValue)     
        vabox.addSpacing(0) 
        vabox.addWidget(self.opacityValue)  
        vabox.setAlignment(Qt.AlignmentFlag.AlignBottom)
         
        vbox = QVBoxLayout()  
        vbox.addLayout(sbox)
        vbox.addLayout(vabox)
        
        groupBox.setLayout(vbox)
        return groupBox

    def buttonGroup(self):
        groupBox = QGroupBox(' Shadow')
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        
        groupBox.setFixedWidth(103)
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
                     
        hideBtn = QPushButton('Hide')
        flipBtn  = QPushButton('Flip')
        flopBtn  = QPushButton('Flop')
        newBtn  = QPushButton('New')
        delBtn  = QPushButton('Delete')
        quitBtn = QPushButton('Close')
    
        hideBtn.clicked.connect(self.maker.hideAll)
        flipBtn.clicked.connect(self.maker.flip)
        flopBtn.clicked.connect(self.maker.flop)
        newBtn.clicked.connect(self.maker.newShadow)
        delBtn.clicked.connect(self.maker.deleteShadow)
        quitBtn.clicked.connect(self.maker.closeWidget)
    
        hbox = QVBoxLayout(self)
        hbox.addWidget(hideBtn)
        hbox.addWidget(flipBtn)
        hbox.addWidget(flopBtn)
        hbox.addWidget(newBtn)
        hbox.addWidget(delBtn)
        hbox.addWidget(quitBtn)
                
        groupBox.setLayout(hbox)
        return groupBox
    
    def Rotate(self, val):  ## setting rotate in shadowMaker
        self.maker.rotateShadow(val)
        self.rotateValue.setText('{:3d}'.format(val))
             
    def Scale(self, val):  ## setting rotate in shadowMaker
        op = (val/100)
        self.maker.scaleShadow(op)
        self.scaleValue.setText('{0:.2f}'.format(op))
           
    def Opacity(self, val):
        op = (val/100)
        self.maker.shadow.setOpacity(op)
        self.maker.alpha = op
        self.opacityValue.setText('{0:.2f}'.format(op)) 
                                                        
### --------------------------------------------------------
class Shadow(QGraphicsPixmapItem):  ## initPoints, initShadow, setPerspective
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
       
        self.maker   = parent
        self.pixitem = self.maker.pixitem
        self.path    = self.maker.path
       
        self.anime = None 
        self.setZValue(common['shadow']) 
        
        self.tag = ''
        self.type = 'shadow' 
        self.fileName = 'shadow'
                                       
        self.dragCnt = 0
        self.save    = QPointF(0.0,0.0)
        self.skip    = False
                           
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
        # self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, True)
          
### --------------------------------------------------------
    # def paint(self, painter, option, widget=None):  ## turn off for now
    #     super().paint(painter, option, widget)
    #     if self.isSelected():
    #         pen = QPen(QColor('lime'))
    #         pen.setWidth(2)
    #         painter.setPen(pen)
    #         painter.drawRect(self.boundingRect())

    def mousePressEvent(self, e): 
        self.save = self.mapToScene(e.pos())    
        self.maker.addPoints()  
        if e.button() == Qt.MouseButton.RightButton:
            self.skip = True      
            self.maker.addWidget()
        e.accept() 
        
    def mouseMoveEvent(self, e):
        self.dragCnt += 1
        if self.dragCnt % 5 == 0:                     
            self.maker.updatePath(self.mapToScene(e.pos()))  
            self.maker.updateOutline()
        e.accept()
                       
    def mouseReleaseEvent(self, e): 
        self.maker.updatePath(self.mapToScene(e.pos())) 
        if self.skip:
            self.skip = False  ## skip updating shadow as ran widget 
        else: 
            self.maker.updateOutline()
            self.maker.updateShadow()  ## cuts off shadow at 0.0y of scene if not moving
        e.accept()
 
 ### --------------------------------------------------------   
    def initPoints(self):  ## initial path and points setting           
        self.path = []
        self.maker.outline = None
         
        self.maker.setPath(self.boundingRect(), self.maker.shadow.pos())
        
        self.maker.updateOutline()     
        self.maker.addPoints() 
    
        if self.pixitem.scale == 1.0 and self.pixitem.rotation == 0:    
            return
                     
        self.maker.hideAll()  ## pixitem rotated or scaled 
           
        self.maker.shadow.setRotation(self.pixitem.rotation)
        self.maker.shadow.setScale(self.pixitem.scale)
    
        self.maker.setPath(self.pixitem.boundingRect(), self.pixitem.pos() + QPointF(-50,-15))
     
        if self.pixitem.rotation != 0:
            self.maker.rotateShadow(self.pixitem.rotation)
            self.maker.rotate = self.pixitem.rotation
                    
        if self.pixitem.scale != 1.0:   
            self.maker.scaleShadow(self.pixitem.scale)      
            self.maker.scalor = self.pixitem.scale
   
        self.maker.updateOutline()         
        self.maker.addPoints()                
      
        self.maker.hideAll()  ## call again to unhide       
        self.maker.shadow.show()
                                                        
### --------------------------------------------------------        
def initShadow(file, w, h, flop):  ## replace all colors with grey    
    img = cv2.imread(file, cv2.IMREAD_UNCHANGED)   
    if flop: img = cv2.flip(img, 1)  ## works after the read   
    rows, cols, _ = img.shape

    tmp = img.copy()  
    for i in range(rows):
        for j in range(cols):
            pixel = img[i,j]
            if pixel[-1] != 0:  ## not transparent      
                tmp[i,j] = (20,20,20,255)
                                           
    img = cv2.resize(np.array(tmp), (int(w), int(h)), interpolation = cv2.INTER_CUBIC)
    img = cv2.GaussianBlur(img,(5,5),cv2.BORDER_DEFAULT)
                                
    height, width, ch = img.shape
    bytesPerLine = ch * width  ## 4 bits of information -- alpha channel 
    
    return img, width, height, bytesPerLine

### --------------------------------------------------------          
def setPerspective(path, w, h, cpy, viewW, viewH):  ## update gray copy based on path xy's         
    p = []                      
    for i in range(4):  ## get current location of points from path
        x,y = int(path[i].x()), int(path[i].y()) 
        p.append([x,y])
            
    dst = np.float32([p[0], p[1], p[3], p[2]])        
    src = np.float32([[0,0], [w,0], [0, h], [w,h]])
        
    M = cv2.getPerspectiveTransform(src, dst)  ## compute the Matrix
    img = cv2.warpPerspective(cpy, M, (viewW, viewH))

    height, width, ch = img.shape
    bytesPerLine = ch * width  ## 4 bits of information
    
    return img, width, height, bytesPerLine   
                                                   
### ------------------- dotsShadowWorks --------------------

