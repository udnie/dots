
import os

from PyQt6.QtCore       import Qt, QRectF, QRect, QPointF,QPoint, QSize, QEvent, pyqtSlot
from PyQt6.QtGui        import QColor, QPen, QPainter, QPen, QPolygonF, QFontMetrics, \
                               QFont, QBrush
from PyQt6.QtWidgets    import QWidget, QLabel, QVBoxLayout, QPushButton, QScrollArea, \
                                QGridLayout, QVBoxLayout, QGraphicsEllipseItem

from dotsShared         import MoveKeys    
from dotsSideGig        import getPathList, getPts, TagIt, point, rect
        
V = 7.5  ## the diameter of a pointItem

### -------------------- dotsPathItem ----------------------
''' classes:  PathItem, DoodleMaker, Doodle  - represents a point '''                                                                                         
### --------------------------------------------------------
class PathItem(QGraphicsEllipseItem):
### --------------------------------------------------------
    def __init__(self, drawing, parent, pt, idx, adto):
        super().__init__()

        self.canvas = parent
        self.scene  = self.canvas.scene
    
        self.drawing   = drawing
        self.pathMaker = drawing.pathMaker
        self.pathWays  = drawing.pathWays
        
        self.selections = self.pathMaker.selections
     
        self.pt = pt
        self.idx = idx
        self.setZValue(int(idx+adto)) 
        
        self.pointTag = ''

        self.type = 'pt'
        self.fileName = None  ## just to make sure if referenced
     
        ## -V*.5 so it's centered on the path 
        self.x = pt.x()-V*.5
        self.y = pt.y()-V*.5
        self.setRect(self.x, self.y, V, V)  
        
        if self.selections and idx in self.selections:
            self.setBrush(QColor('lime'))
        else:
            self.setBrush(QColor('white'))   
               
        self.maptos = QPointF()
        self.dragCnt = 0
            
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, True)
          
        self.setAcceptHoverEvents(True)

 ### --------------------------------------------------------
    @pyqtSlot(str)
    def setPixKeys(self, key):
        if self.idx in self.selections and key in MoveKeys: 
            self.moveThis(MoveKeys[key])
                                    
    def hoverEnterEvent(self, e):
        if self.pathMaker.pathSet:  
            pct = (self.idx/len(self.pathMaker.pts))*100
            tag = self.pathMaker.pathWays.makePtsTag(self.pt, self.idx, pct)
            self.pointTag = TagIt('points', tag, QColor('YELLOW')) 
            self.pointTag.setPos(QPointF(self.pt)+QPointF(0.0,-20.0))
            self.pointTag.setZValue(self.drawing.findTop()+5)
            self.scene.addItem(self.pointTag)
        e.accept()

    def hoverLeaveEvent(self, e):
        self.removePointTag()  ## used twice
        e.accept()

    def mousePressEvent(self, e):     
        self.removePointTag()  ## second time, just in case 
        if self.pathMaker.key == 'del':  
            self.drawing.deletePathItem(self.idx)
        elif self.pathMaker.key == 'opt': 
            self.drawing.insertPathItem(self) 
        if self.pathMaker.key in ('del','opt'):   
            self.pathMaker.key = ''       
        e.accept() 
        
    def mouseMoveEvent(self, e):
        if self.pathWays.tagCount() == 0:
            if self.pathMaker.editingPts == True:
                self.dragCnt += 1
                if self.dragCnt % 5 == 0:        
                    pos = self.mapToScene(e.pos())
                    self.moveIt(pos.x(), pos.y())                                    
        e.accept()
           
    def mouseDoubleClickEvent(self, e):
        if self.idx not in self.selections:  ## selects/unselects
            self.maptos = self.mapToScene(e.pos())
            self.selections.append(self.idx)            
        else:        
            self.selections.remove(self.idx)  
        self.drawing.updatePath()
        e.accept()
             
    def mouseReleaseEvent(self, e):
        if self.pathMaker.editingPts == True:        
            if self.dragCnt > 0:
                self.pathMaker.pts[self.idx] = self.mapToScene(e.pos())                
                self.drawing.updatePath()  ## rewrites pointItems as well
        e.accept()
              
    def moveIt(self, x, y):
        self.setRect(x-V*.5, y-V*.5, V,V)             
        self.pathMaker.pts[self.idx] = QPointF(x,y) 
        self.pathMaker.addPath() 
          
    def moveThis(self, key):
        self.setOriginPt()  ## updates width and height        
        self.x = self.x + key[0]
        self.y = self.y + key[1]
        self.moveIt(self.x, self.y)           
                   
    def removePointTag(self):
        if self.pointTag != '':  ## there can be only one
            self.scene.removeItem(self.pointTag)
            self.pointTag = ''
            
    def setOriginPt(self):    
        b = self.boundingRect()
        op = QPointF(b.width()/2, b.height()/2)
        self.setTransformOriginPoint(op)

### --------------------------------------------------------
class DoodleMaker(QWidget): ## my file display of path files
### --------------------------------------------------------
    def __init__(self, parent, where=''):  ## can come from 'Path Menu'
        super().__init__()

        self.pathMaker = parent
                         
        self.type = 'widget'
        self.save = QPointF()
                
        self.rotate = 0
        self.scale  = 0
        self.where  = where
        
        self.setAccessibleName('widget')
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

        self.updateGrid()

        scroll = QScrollArea()
        scroll.setFixedSize(self.WidgetW-40, self.WidgetH-70)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll.setStyleSheet('background: rgb(220, 220, 220)')
        scroll.verticalScrollBar().setStyleSheet('QScrollBar:vertical {\n' 
            'background: rgb(245,245,245) }');  ## shows handle better
            
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
class Doddle(QLabel):  ## small drawing of path file content with filename
### --------------------------------------------------------
    def __init__(self, parent, path, file):
        super().__init__()

        self.doodle = parent
        self.pathMaker = path
        
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
        
    def minimumSizeHint(self):
        return QSize(self.W, self.H)

    def sizeHint(self):
        return self.minimumSizeHint()

    def mousePressEvent(self, e): 
        if e.type() == QEvent.Type.MouseButtonPress and \
            e.button() == Qt.MouseButton.RightButton:
            return
          
        if self.doodle.where == 'Path Menu':  ## from animation menu - sideCar
            for pix in self.pathMaker.canvas.scene.selectedItems(): 
                if pix.type != 'pix':
                    continue
                else:
                    pix.tag = os.path.basename(self.file) 
                    pix.anime = None        ## set by play
                    pix.setSelected(False)  ## when tagged 
            self.pathMaker.pathChooserOff() 
            return
    
        elif self.pathMaker.key == 'del':
            self.doodle.delete(self)
            return
        ## where .pts come from once saved as a file
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
   
### -------------------- dotsPathItem ----------------------                                                                                                                                      



                                                           