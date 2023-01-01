
import os
import math

from PyQt6.QtCore       import Qt, QPoint, QRectF, QPointF,QSize, QEvent
from PyQt6.QtGui        import QColor, QPen, QPainter, QPen, QPolygonF, QFontMetrics, \
                               QFont, QBrush
from PyQt6.QtWidgets    import QSlider, QWidget, QGroupBox, QDial, QLabel, QHBoxLayout,  \
                               QVBoxLayout, QPushButton,QScrollArea, QGridLayout, QVBoxLayout

from dotsSideGig        import getPathList, getPts, distance

ScaleRotate = ('<', '>', '+', '-') 

### --------------------------------------------------------        
class PathWidget(QWidget): 
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()
                                        
        self.pathMaker = parent
        self.sideWays  = self.pathMaker.sideWays 
        self.drawing   = self.pathMaker.drawing 
        
        self.type = 'widget'
        self.save = QPointF(0.0,0.0)
        
        self.WidgetW, self.WidgetH = 330.0, 215.0
        
        self.rotate = 0
        self.scale  = 1.0
        
        self.setAccessibleName('widget')
                
        hbox = QHBoxLayout()
        hbox.addWidget(self.sliderGroup())
        hbox.addSpacing(5) 
        hbox.addWidget(self.buttonGroup())
        self.setLayout(hbox)
        
        self.setFixedHeight(int(self.WidgetH))
        self.setStyleSheet("background-color: rgba(0,0,0,0)")
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
        painter.setPen(QPen(QColor(0,65,255), 5, Qt.PenStyle.SolidLine,            
            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(QColor(144,238,144))
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
        self.pathMaker.closeWidget()
        e.accept()
        
### -------------------------------------------------------- 
    def sliderGroup(self):
        groupBox = QGroupBox("Rotate        Scale ")
        
        groupBox.setFixedWidth(140)
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        groupBox.setStyleSheet("background: rgb(245, 245, 245)")
   
        self.rotateValue = QLabel("0", alignment=Qt.AlignmentFlag.AlignCenter)
        self.rotaryDial = QDial()
        self.rotaryDial.setMinimum(0)
        self.rotaryDial.setMaximum(360)
        self.rotaryDial.setValue(0)
        self.rotaryDial.setFixedWidth(60)
        self.rotaryDial.setWrapping(False)
        self.rotaryDial.setNotchesVisible(True)
        self.rotaryDial.setNotchTarget(15.0)
        self.rotaryDial.valueChanged.connect(self.Rotate)
    
        self.scaleValue = QLabel("1.00", alignment=Qt.AlignmentFlag.AlignCenter)
        self.scaleSlider = QSlider(Qt.Orientation.Vertical)   
        self.scaleSlider.setMinimum(25)
        self.scaleSlider.setMaximum(225)
        self.scaleSlider.setSingleStep(1)
        self.scaleSlider.setValue(100)
        self.scaleSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scaleSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.scaleSlider.setTickInterval(25)  
        self.scaleSlider.valueChanged.connect(self.Scale)   
                          
        sbox = QHBoxLayout()  ## sliders  
        sbox.addSpacing(-10)    
        sbox.addWidget(self.rotaryDial)  
        sbox.addSpacing(10)       
        sbox.addWidget(self.scaleSlider) 
        
        vabox = QHBoxLayout()  ## values
        vabox.addSpacing(0) 
        vabox.addWidget(self.rotateValue)        
        vabox.addSpacing(0) 
        vabox.addWidget(self.scaleValue)     
        vabox.setAlignment(Qt.AlignmentFlag.AlignBottom)
         
        vbox = QVBoxLayout()  
        vbox.addLayout(sbox)
        vbox.addLayout(vabox)
        
        groupBox.setLayout(vbox)
        return groupBox

### -------------------------------------------------------- 
    def buttonGroup(self):
        groupBox = QGroupBox("PathMaker ")
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        
        groupBox.setFixedWidth(103)
        groupBox.setStyleSheet("background: rgb(245, 245, 245)")
                     
        waysBtn = QPushButton("WayPts")                 
        saveBtn = QPushButton("Save")
        editBtn = QPushButton("Edit")
        self.newBtn  = QPushButton("New")
        filesBtn = QPushButton("Files")     
        delBtn  = QPushButton("Delete")
        quitBtn = QPushButton("Close")
    
        waysBtn.clicked.connect(self.sideWays.addWayPtTags)
        saveBtn.clicked.connect(self.sideWays.savePath)
        editBtn.clicked.connect(self.drawing.editPoints)
        self.newBtn.clicked.connect(self.drawing.toggleNewPath)
        filesBtn.clicked.connect(self.pathMaker.pathChooser)
        delBtn.clicked.connect(self.pathMaker.delete)
        quitBtn.clicked.connect(self.pathMaker.closeWidget)
    
        hbox = QVBoxLayout(self)
        hbox.addWidget(saveBtn)    
        hbox.addWidget(waysBtn)
        hbox.addWidget(editBtn)
        hbox.addWidget(self.newBtn)
        hbox.addWidget(filesBtn)      
        hbox.addWidget(delBtn)
        hbox.addWidget(quitBtn)
                
        groupBox.setLayout(hbox)
        return groupBox

    def Rotate(self, val):  ## setting rotate in shadowMaker
        self.rotatePath(val)
        self.rotateValue.setText("{:3d}".format(val))
             
    def Scale(self, val):  ## setting rotate in shadowMaker
        op = (val/100)
        self.scalePath(op)
        self.scaleValue.setText("{0:.2f}".format(op))
                
    def rotatePath(self, val): 
        inc = (val - self.rotate)
        self.rotateScale(0, -inc)
        self.rotate = val
      
    def scalePath(self, val): 
        per = (val - self.scale) / self.scale    
        self.rotateScale(per, 0)
        self.scale = val
    
    ## yet another one - they're all just a little bit different
    def rotateScale(self, per, inc):  
        if len(self.pathMaker.pts) == 0: 
            return 
        else:
            p = self.pathMaker.path.sceneBoundingRect()
    
        centerX = p.x() + p.width() /2
        centerY = p.y() + p.height() /2  
                  
        for i in range(0, len(self.pathMaker.pts)):  ## if you don't get 4 points...  
            dist = distance(self.pathMaker.pts[i].x(), centerX, self.pathMaker.pts[i].y(), centerY) 
              
            xdist, ydist = dist, dist      
            xdist = dist + (dist * per)              
            ydist = xdist
           
            deltaX = self.pathMaker.pts[i].x() - centerX
            deltaY = self.pathMaker.pts[i].y() - centerY

            angle = math.degrees(math.atan2(deltaX, deltaY))
            angle = angle + math.ceil( angle / 360) * 360

            plotX = centerX + xdist * math.sin(math.radians(angle + inc))
            plotY = centerY + ydist * math.cos(math.radians(angle + inc))
           
            self.pathMaker.pts[i] = QPointF(plotX, plotY)
            
        self.pathMaker.addPath()
        self.sideWays.gofish()
                                                                                             
### --------------------------------------------------------
class DoodleMaker(QWidget): 
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()

        self.pathMaker = parent
          
        self.type = 'widget'
        self.save = QPointF(0.0,0.0)
        
        self.rotate = 0
        self.scale  = 0
        
        self.setAccessibleName('widget')
        self.WidgetW, self.WidgetH = 530, 400
        
        self.setFixedSize(self.WidgetW, self.WidgetH)
        self.setStyleSheet("background-color: rgba(0,0,0,0)")
    
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)
              
        vbox = QVBoxLayout()
         
        vbox.addSpacing(0)
        vbox.addWidget(self.addGrid())
        vbox.addSpacing(0)
        vbox.addWidget(self.addClose(), alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(vbox)
        
  ### --------------------------------------------------------                                 
    def paintEvent(self, e): 
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)        
        rect = QRectF(4, 4, self.WidgetW-8, self.WidgetH-8)
        painter.setPen(QPen(QColor(104,255,204), 6, Qt.PenStyle.SolidLine,  ## border
            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)) 
        painter.setBrush(QColor(225,225,225)) 
        painter.drawRoundedRect(rect, 15, 15)
        
    def addClose(self): 
        quitBtn = QPushButton("Close")
        quitBtn.clicked.connect(self.closeWidget)
        quitBtn.setStyleSheet("background: rgb(245, 245, 245)")
        quitBtn.setFixedWidth(100) 
        return quitBtn 
           
    def closeWidget(self):       
        self.pathMaker.pathChooserOff()
     
    def addGrid(self):           
        widget = QWidget()
        self.gLayout = QGridLayout(widget)
        self.gLayout.setDefaultPositioning(3, Qt.Orientation.Horizontal)
        self.gLayout.setHorizontalSpacing(5)
        self.gLayout.setContentsMargins(5, 5, 5, 5)

        self.updateGrid()

        scroll = QScrollArea()
        scroll.setFixedSize(self.WidgetW-40, self.WidgetH-70)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll.setStyleSheet("background: rgb(220, 220, 220)")
        scroll.verticalScrollBar().setStyleSheet("QScrollBar:vertical {\n" 
            "background: rgb(245,245,245) }");  ## shows handle better
            
        scroll.setWidget(widget)
        return scroll
    
    def updateGrid(self):
        for file in getPathList():    
            df = Doddle(self, self.pathMaker, file)
            self.gLayout.addWidget(df)
            
    def delete(self, this):
        os.remove(this.file)
        for i in reversed(range(self.gLayout.count())):
            self.gLayout.removeItem(self.gLayout.itemAt(i))
        self.updateGrid()
        self.pathMaker.removePath()
         
### --------------------------------------------------------
class Doddle(QLabel):  
### --------------------------------------------------------
    def __init__(self, parent, path, file):
        super().__init__()

        self.doodle = parent
        self.pathMaker = path
        
        self.file = file
        scalor = .10
        self.W, self.H = 150, 100
    
        self.setStyleSheet("background: rgb(235, 235, 235)")
        
        self.font = QFont()
        self.font.setFamily("Helvetica")
        self.font.setPointSize(12)

        self.pen = QPen(QColor(0,0,0))                     
        self.pen.setWidth(1)                                       
        self.brush = QBrush(QColor(255,255,255,255)) 
        ## scale down screen drawing --  file, scalor, offset
        self.df = getPts(self.file, scalor, 10)  
  
    def minimumSizeHint(self):
        return QSize(self.W, self.H)

    def sizeHint(self):
        return self.minimumSizeHint()

    def mousePressEvent(self, e): 
        if e.type() == QEvent.Type.MouseButtonPress and \
            e.button() == Qt.MouseButton.RightButton:
            return
        elif self.pathMaker.key == 'del':
            self.doodle.delete(self)
            return
        self.pathMaker.pts = getPts(self.file)
        self.pathMaker.addPath()
        self.pathMaker.openPathFile = os.path.basename(self.file) 
        self.pathMaker.pathChooserOff() 
        e.accept()
                                   
    def paintEvent(self, event):  ## draw rthe path
        painter = QPainter(self)
        painter.setBrush(self.brush) 
        painter.setPen(QPen(QColor("DODGERBLUE"), 2, Qt.PenStyle.DashDotLine))
        painter.drawPolygon(QPolygonF(self.df))
        painter.setBrush(Qt.BrushStyle.NoBrush) 
        painter.setPen(QPen(Qt.GlobalColor.darkGray, 2)) 
        painter.drawRect(0, 0, self.W, self.H)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))

        metrics = QFontMetrics(self.font)
        txt = os.path.basename(self.file)
        m = metrics.boundingRect(txt)
        w = m.width()

        w = int((self.W - w)/2 )
        painter.drawText(w-5, self.H-10, txt)
                                                                                                                                         
### ------------------- dotsPathWidget ---------------------                               
                                  