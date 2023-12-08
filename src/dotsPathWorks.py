
import os
import math

from PyQt6.QtCore       import Qt, QSize, QEvent, QRectF, QRect, QPointF, QPoint
from PyQt6.QtGui        import QColor, QPen, QPainter, QPen, QPolygonF, QFontMetrics, \
                               QFont, QBrush, QPixmap 
from PyQt6.QtWidgets    import QWidget, QLabel, QVBoxLayout, QPushButton, QScrollArea, \
                                QGridLayout, QVBoxLayout, QGraphicsPixmapItem

from dotsAnimation      import *  
from dotsShared         import RotateKeys, paths
from dotsSideGig        import distance
from dotsSideGig        import getPathList, getPts

ScaleRotate = ('<', '>', '+', '-')  ## sent from keyboard
ScaleUpKeys = ('>','\"','\'')
ScaleDnKeys = ('<',':',';')
     
### -------------------- dotsPathWorks ---------------------
''' class: DoddleMaker - functions: scaleRotate, pathTest  '''                                                                                         
### --------------------------------------------------------
class PathWorks:
### --------------------------------------------------------
    def __init__(self, parent):  
        super().__init__()
        
        self.pathMaker = parent
        self.canvas    = self.pathMaker.canvas
        self.scene     = self.canvas.scene
         
### --------------------------------------------------------  
    def closeWidget(self):
        if self.pathMaker.widget != None:
            self.pathMaker.widget.close()
            self.pathMaker.widget = None
  
    def deleteDoodle(self, this):  ## remove doodle and path from pathChooser widget
        os.remove(this.file)
        self.pathMaker.removePath()  
        self.pathMaker.pathChooserOff()
        self.pathMaker.pathChooser()
    
    def scaleRotate(self, key, per=0, inc=0):  ## also used by pathWidget
        if len(self.pathMaker.pts) == 0: 
            return 
        p = self.pathMaker.path.sceneBoundingRect()
                                
        centerX = p.x() + p.width() /2
        centerY = p.y() + p.height() /2 
                
        ## for each pt compute distance from center
        for i in range(0, len(self.pathMaker.pts)):    
            dist = distance(self.pathMaker.pts[i].x(), centerX, self.pathMaker.pts[i].y(), centerY)
              
            if key == 'A':  ## it's from pathWidget, scale or rotate
                xdist, ydist = dist, dist      
                xdist = dist + (dist * per)              
                ydist = xdist
            else:  ## from keyboard
                inc, xdist, ydist = 0, dist, dist  ## initialize    
                ## scale up, scale down
                if key in ScaleUpKeys:  
                    dist = dist + ( dist * .01 )         
                elif key in ScaleDnKeys:  
                    dist = dist - ( dist * .01 )
                if key in RotateKeys: 
                    inc = RotateKeys[key]       
                ## more scale stuff
                if key in('<','>'):
                    xdist = dist                
                    ydist = dist  
                elif key in(':','\"'): ## scale X
                    xdist = dist              
                elif key in(';','\''):  ## scale Y
                    ydist = dist 
                     
            ## do the math 
            deltaX = self.pathMaker.pts[i].x() - centerX
            deltaY = self.pathMaker.pts[i].y() - centerY

            angle = math.degrees(math.atan2(deltaX, deltaY))
            angle = angle + math.ceil( angle / 360) * 360

            plotX = centerX + xdist * math.sin(math.radians(angle + inc))
            plotY = centerY + ydist * math.cos(math.radians(angle + inc))
           
            self.pathMaker.pts[i] = QPointF(plotX, plotY)
                    
        self.pathMaker.addPath()    
        self.pathMaker.pathWays.editingPtsSet() 
                  
### ---------------------- pathTest ------------------------
    def pathTest(self):
        if self.pathMaker.pts and self.pathMaker.pathSet:
            if not self.pathMaker.pathTestSet:
                self.ball = QGraphicsPixmapItem(QPixmap(paths['imagePath'] + \
                    'ball.png'))
                node = Node(self.ball)
                self.ball.setZValue(self.pathMaker.drawing.findTop()+10)
       
                self.pathTestNode = QPropertyAnimation(node, b'pos')
                self.pathTestNode.setDuration(self.pathMaker.seconds * 1000)

                path = self.pathMaker.setPaintPath(True)  ## close subpath, uses    
                b = self.ball.boundingRect() 
                pt = QPointF(b.width()/2, b.height()/2)
           
                self.pathTestNode.setStartValue(path.pointAtPercent(0.0)-pt)
                for i in range(1, 99):   
                    self.pathTestNode.setKeyValueAt(
                        i/100.0, 
                        path.pointAtPercent(i/100.0)-pt
                        )
                self.pathTestNode.setEndValue(path.pointAtPercent(1.0)-pt) 
                self.pathTestNode.setLoopCount(-1) 
                del path
                self.startPathTest()
            else:
                self.stopPathTest()

    def startPathTest(self):
        self.scene.addItem(self.ball)
        self.pathTestNode.start()
        self.pathMaker.pathTestSet = True

    def stopPathTest(self): 
        if self.pathMaker.pathTestSet:  
            self.pathTestNode.stop()
            self.scene.removeItem(self.ball)
            self.ball = None
            self.pathTestNode = None
            self.pathMaker.pathTestSet = False
            self.pathMaker.drawing.redrawPoints(self.pathMaker.drawing.pointItemsSet())
   
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
            df = Doddle(self, self.pathMaker, file)
            self.gLayout.addWidget(df)
                     
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
                         
### -------------------- dotsPathWorks ---------------------                                                                                                                                      



                                                           