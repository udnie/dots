
import math
import time
 
from PyQt6.QtCore       import Qt, QPointF, QRect, QPoint, pyqtSlot
from PyQt6.QtGui        import QColor, QPen, QPixmap, QImage, QPainter, QBrush, QPainterPath                          
from PyQt6.QtWidgets    import QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsPathItem, QWidget
                                                     
from spritePoints       import PointItem, distance

Half  = 360  ## half of scene width and height
Scalor = 2.1333  ## amount to scale 150 to 320
                                                                                     
### ---------------------- spriteLoupe  --------------------
''' classes: Loupe, TimesUp '''
### --------------------------------------------------------                      
class TimesUp(QGraphicsPixmapItem):  ## 2X enlargement of selection using rect
### --------------------------------------------------------
    def __init__(self, img, x, y, parent):
        super().__init__() 
        
        self.loupe = parent     
        self.type = 'pix'
        
        self.setPixmap(QPixmap(img)) 
    
        self.x = x
        self.y = y
    
        self.dragAnchor = QPoint(0,0)
        self.initX = 0.0
        self.initY = 0.0
      
        self.setZValue(950)  
        self.setPos(QPointF(x,y)) 
        
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
 
 ### --------------------------------------------------------
    def mousePressEvent(self, e):
        self.initX, self.initY = self.x, self.y  
        self.dragAnchor = self.mapToScene(e.pos())
        e.accept()
 
    def mouseMoveEvent(self, e):
        self.updateXY(self.mapToScene(e.pos()))
        self.setPos(self.x, self.y)                                  
        e.accept()
 
    def mouseReleaseEvent(self, e):         
        self.updateXY(self.mapToScene(e.pos()))
        self.setPos(self.x, self.y)
        e.accept()
                     
    def mouseDoubleClickEvent(self, e): 
        self.loupe.removeTimes()
        e.accept()
        
    def updateXY(self, pos):
        dragX = pos.x() - self.dragAnchor.x()
        dragY = pos.y() - self.dragAnchor.y()
        self.x = float(self.initX + dragX)
        self.y = float(self.initY + dragY)
                              
### --------------------------------------------------------                        
class Loupe(QWidget):  ## 'no matter where you go, there you are' -- Jim, Taxi 
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()
                                                 
        self.spriteMaker = parent
        self.scene       = parent.scene
        self.view        = parent.view
        self.works       = parent.works
                                         
        self.init() 
        
        self.works.imgSignal[str].connect(self.imageCopy) 
                   
### --------------------------------------------------------          
    def init(self): 
        self.key = ''   
        self.img = None
        self.rect   = None   
        self.times2 = None           
        self.allPts = None  
        self.idxLst = None 
        self.path   = None
        
        self.lastX, self.lastY = 0, 0
        self.x, self.y, self.idx = 0.0, 0.0, 0
                                                                          
### --------------------------------------------------------                                                                                        
    def loupeIt(self, idx):
        if self.times2:
            self.lastX, self.lastY = self.times2.x, self.times2.y     
        if self.times2: self.removeTimes()   
                 
        start = time.time()  ## curious
           
        p = self.spriteMaker.pts[idx]    
        self.x, self.y, self.idx = p.x(), p.y(), idx 
        self.addRect(self.x, self.y)  ## x,y is center of rect - see addRect  
                
        img = self.img.copy(int(self.x+25), int(self.y+25), 150, 150)  ## includes 100px for border  
        self.times2 = TimesUp(img, 200, 200, self)  ## locate it here to use in addPoints 
        
        self.times2.setScale(Scalor)  ## make a 2X plus copy of selected area, see scaleUpPoints as well
        self.scene.addItem(self.times2)  ## I made rect smaller, 150X150, so times2 needs to scale more
        
        self.markPoint()                     
        self.scaleUpPoints()  
 
        img = self.addPoints()  ## the hat trick        
        self.times2 = TimesUp(img, self.lastX, self.lastY, self)  
   
        self.scene.addItem(self.times2)
                     
        if self.times2.isVisibleTo(self.rect) or self.times2.collidesWithItem(self.rect, mode=\
            Qt.ItemSelectionMode.IntersectsItemBoundingRect):
                self.moveTimes()
      
        end = time.time()  ## roughly .01..., 
 
        # print(end - start)
                 
### --------------------------------------------------------                                             
    def addPoints(self):  ## replaces 2X copy, adds points, path and border to it
        lst = []       
        x, y = self.getOffset(self.idx)                                      

        self.deletePath()
        path = QGraphicsPathItem(self.setPainterPath())
        path.setPen(QPen(QColor(self.spriteMaker.color), 3, Qt.PenStyle.SolidLine))
        path.setZValue(999)
  
        self.scene.addItem(path)
        lst.append(path)

        for i in range(0,len(self.allPts)):
            a = self.allPts[i]  
            p = PointItem(QPointF(a.x()+x, a.y()+y), i, i+1000, self.spriteMaker)                
            self.scene.addItem(p)
            lst.append(p)                     
      
        img = self.spriteMaker.view.grab(QRect(200, 200, 320, 320))
        img = img.toImage()  ## view.grab returns a qpixmap
            
        output = QImage(320, 322, QImage.Format.Format_RGB32)
        output.fill(Qt.GlobalColor.black)
        
        painter = QPainter(output) 
        painter.drawImage(QPointF(), QImage(img)) 
                   
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
                                          
        painter.setPen(QPen(QColor('lime'), 15, Qt.PenStyle.SolidLine))   
        painter.drawRect(-2, -2, 324, 324)
        painter.end()  
                                                                
        for p in lst: self.scene.removeItem(p) 
        
        self.scene.removeItem(self.times2)    
        self.times2 = None    
                             
        return output.convertToFormat(QImage.Format.Format_RGB32)
    
### --------------------------------------------------------   
    ''' imageCopy adds a 100px border to self.works.imgCopy -  final size 920X920px '''
    @pyqtSlot(str)                                                                                             
    def imageCopy(self): 
        img = self.works.imgCopy
            
        output = QImage(920, 920, QImage.Format.Format_RGB32)
        output.fill(QColor(148,113,193))  ## grape
    
        painter = QPainter(output)      
        painter.setBrush(QBrush(Qt.BrushStyle.Dense7Pattern)) 
        painter.drawRect(0,0,920,920)
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))  ## note!!!!!    
  
        painter.drawImage(QPointF(100,100), img) 
        painter.end()  
        ## write once - use it for the entire session                  
        self.img = output.convertToFormat(QImage.Format.Format_RGB32)
           
### --------------------------------------------------------     
    def addRect(self, x, y): 
        if self.rect:
            self.scene.removeItem(self.rect)
        self.rect = QGraphicsRectItem(x-75, y-75, 150, 150)
        self.rect.setPen(QPen(QColor('lime'), 2, Qt.PenStyle.SolidLine)) 
        self.rect.setZValue(901)
        self.scene.addItem(self.rect) 
                    
    def nextPoint(self, key):  ## arrow up and arrow down - runs from spriteMaker              
        i = self.idx            
        if key == 'up':
            i = i + 1
            if i == len(self.spriteMaker.pts):  
                i = 0                            
        elif key == 'down': 
            i = i - 1
            if i == 0: 
                i = len(self.spriteMaker.pts)-1                        
        self.loupeIt(i)
       
    def moveTimes(self):  ## try to move times2 out of rects way
        p = self.rect.sceneBoundingRect()
        x, y = p.x(), p.y()
        if x + p.width() < Half:
            self.times2.x = 385
        elif x + p.width() > Half:
            self.times2.x = 15        
        elif y < Half:
            self.times2.y = 385
        elif y  > Half:
            self.times2.y = 15
        self.times2.setPos(self.times2.x, self.times2.y)
                                            
    def getOffset(self, idx):  ## calculates the added diff to drawing scaled up points and path      
        p = self.allPts[idx]           
        x, y = p.x(), p.y()     
        if x > Half:
            x = -x + Half
        elif x < 0: 
            x = Half + (x * -1.0) 
        else:
            x = Half - x  
        if y > Half:
                y = -y + Half
        elif y < 0: 
            y = Half + (y * -1.0) 
        else:
            y = Half - y
        return x, y    
    
### --------------------------------------------------------             
    def setPainterPath(self):  ## draw it all - you can't see it for the time it's there
        x, y = self.getOffset(self.idx) 
        path = QPainterPath()
        for i in range(0,len(self.allPts)):
            pt = self.allPts[i]   
            if not path.elementCount():
                path.moveTo(QPointF(pt.x()+x, pt.y()+y))
            path.lineTo(QPointF(pt.x()+x, pt.y()+y))
        path.closeSubpath()
        return path
                         
    def deletePath(self): 
        if self.path:
            self.scene.removeItem(self.path)
            self.path = None 
                                                                                                   
    def markPoint(self):
        self.spriteMaker.redrawPoints()  
        for p in self.scene.items():
            if p.type == 'pt' and p.idx == self.idx:
                p.setBrush(QColor('cyan'))
                                                                      
    def scaleUpPoints(self):
        per, inc = Scalor - 1, 0
        self.allPts, lst = [], []  
           
        p = self.spriteMaker.outline.sceneBoundingRect()
        centerX = p.x() + p.width()/2
        centerY = p.y() + p.height()/2  
                                                                                                                                                                
        for i in range(0, len(self.spriteMaker.pts)):                        
            p = QPointF(self.spriteMaker.pts[i])
            
            if self.rect.contains(p):  
                lst.append(i)
                                 
            dist = distance(
                self.spriteMaker.pts[i].x(), centerX, 
                self.spriteMaker.pts[i].y(), centerY)    
                
            xdist, ydist = dist, dist             
            xdist = dist + (dist * per)              
            ydist = xdist
        
            deltaX = self.spriteMaker.pts[i].x() - centerX
            deltaY = self.spriteMaker.pts[i].y() - centerY

            angle = math.degrees(math.atan2(deltaX, deltaY))
            angle = angle + math.ceil(angle/360) * 360

            plotX = centerX + xdist * math.sin(math.radians(angle + inc))
            plotY = centerY + ydist * math.cos(math.radians(angle + inc))
                                                    
            self.allPts.append(QPointF(plotX, plotY))
                         
        self.idxLst = lst
    
### --------------------------------------------------------
    def removeTimes(self): 
        self.deletePath()
        if self.times2:
            self.scene.removeItem(self.times2)
            self.times2 = None   
        if self.rect:
            self.scene.removeItem(self.rect)
            self.rect = None
        self.ibid()
                                                                                                   
    def deletePointItem(self, idx):  
        self.spriteMaker.pts.pop(idx) 
        self.ibid()
        self.loupeIt(idx-1)
        
    def insertPointItem(self, pointItem):  ## halfway between points        
        idx, pt = pointItem.idx + 1, pointItem.pt  ## idx, the next point
        if idx == len(self.spriteMaker.pts): 
            idx = 0    
        pt1 = self.spriteMaker.pts[idx]  ## calculate new x,y
        pt1 = QPointF(pt1.x() - pt.x(), pt1.y() - pt.y())
        pt1 = QPointF(pt) + pt1*.5      
        self.spriteMaker.pts.insert(idx, pt1)
        self.ibid()
        self.loupeIt(idx)
        
    def ibid(self):
        self.spriteMaker.updateOutline() 
        self.spriteMaker.redrawPoints()   
                                                                                                                                                                                                             
### ------------------- spriteLoupe.py ---------------------

