
import os

from PyQt6.QtCore       import Qt, QPointF, QPoint, QSize, QEvent, QRectF, QRect
from PyQt6.QtGui        import QColor, QPen, QPainter, QPolygonF, QFontMetrics, QFont, QBrush
from PyQt6.QtWidgets    import QWidget, QVBoxLayout, QPushButton, QScrollArea, QLabel, \
                                QGridLayout, QVBoxLayout

from dotsSideGig        import getPathList, getPts 

### -------------------- dotsDoodleMaker -------------------
class DoodleMaker(QWidget): ## my file display of path files
### --------------------------------------------------------
    def __init__(self, parent, where=''):  ## can come from 'Path Menu'
        super().__init__()

        self.canvas = parent
        self.scene  = self.canvas.scene
      
        self.pathMaker = self.canvas.pathMaker
                         
        self.type = 'widget'              
        self.setAccessibleName('widget')
        
        self.save = QPointF()
                
        self.rotate = 0
        self.scale  = 0
        self.where  = where
                 
        self.WidgetW, self.WidgetH = 530, 400
        
        self.setFixedSize(self.WidgetW, self.WidgetH)
        self.setStyleSheet('background-color: rgba(0,0,0,0)')
    
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
   
    def mousePressEvent(self, e):
        self.save = e.globalPosition()  ## works the best, needs to change for PyQt6
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
        
### -------------------------------------------------------- 
    def addClose(self): 
        quitBtn = QPushButton('Close')
        quitBtn.clicked.connect(self.closeWidget)
        quitBtn.setStyleSheet('background: rgb(245, 245, 245)')
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

        scroll = QScrollArea()
        scroll.setFixedSize(self.WidgetW-40, self.WidgetH-70)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll.setStyleSheet('background: rgb(220, 220, 220)')
        scroll.verticalScrollBar().setStyleSheet('QScrollBar:vertical {\n' 
            'background: rgb(245,245,245) }');  ## shows handle better

        self.updateGrid()

        scroll.setWidget(widget)
        return scroll
      
    def updateGrid(self):
        for file in getPathList():    
            df = Doddle(self.canvas, self, file, self.canvas.scene.selectedItems())
            self.gLayout.addWidget(df)   
                    
### --------------------------------------------------------
class Doddle(QLabel):  ## small drawing of path file content with filename
### --------------------------------------------------------
    def __init__(self, parent, doodle, file, items):  ## added items to insure its reference
        super().__init__()

        self.canvas = parent
        self.scene  = self.canvas.scene
        self.mapper = self.canvas.mapper
    
        self.items  = items
    
        self.doodle = doodle
        self.pathMaker = self.canvas.pathMaker
        
        self.file = file
        scalor = .10
        self.W, self.H = 150, 100
    
        self.setStyleSheet('background: rgb(235, 235, 235)')
        
        self.font = QFont()
        self.font.setFamily('Helvetica')
        self.font.setPointSize(12)

        self.pen = QPen(QColor(0,0,0))                     
        self.pen.setWidth(1)                                       
        self.brush = QBrush(QColor(255,255,255,255)) 
        ## scale down screen drawing --  file, scalor, offset        
        self.df = getPts(self.file, scalor, 10)  
   
### --------------------------------------------------------     
    def minimumSizeHint(self):
        return QSize(self.W, self.H)

    def sizeHint(self):
        return self.minimumSizeHint()

    def mousePressEvent(self, e): 
        if e.type() == QEvent.Type.MouseButtonPress and \
            e.button() == Qt.MouseButton.RightButton:
            return      
        ## from animation menu - see menus
        if self.doodle.where == 'Path Menu':   
            for pix in self.items: 
                if pix.type == 'pix':
                    pix.tag = os.path.basename(self.file) 
                    pix.anime = None        ## set by play
                    pix.setSelected(False)  ## when tagged    
            self.pathMaker.pathChooserOff() 
            self.mapper.toggleTagItems('anime') 
            return
        elif self.pathMaker.key == 'del':
            self.pathMaker.pathWorks.deleteDoodle(self)
            return     
        ## draws the path - where .pts come from once saved as a file
        self.pathMaker.pts = getPts(self.file)  ## from sideGig
        self.pathMaker.addPath()
        self.pathMaker.openPathFile = os.path.basename(self.file) 
        self.pathMaker.pathChooserOff()        
        if self.pathMaker.widget != None:
            self.pathMaker.widget.resetSliders()    
        e.accept()
                                   
    def paintEvent(self, event):  ## draw the paths
        painter = QPainter(self)
        painter.setBrush(self.brush) 
        painter.setPen(QPen(QColor('DODGERBLUE'), 2, Qt.PenStyle.DashDotLine))
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
 
 ### ----------------- dotsDoodleMaker -----------------
                                                                                                                                                             


                                                           