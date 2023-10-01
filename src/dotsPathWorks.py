
import os
import math

from PyQt6.QtCore       import QPointF, QPoint
from PyQt6.QtGui        import QPixmap 
from PyQt6.QtWidgets    import QGraphicsPixmapItem

from dotsAnimation      import *  
from dotsShared         import RotateKeys, paths
from dotsSideGig        import distance

ScaleRotate = ('<', '>', '+', '-')  ## sent from keyboard
ScaleUpKeys = ('>','\"','\'')
ScaleDnKeys = ('<',':',';')
     
### -------------------- dotsPathWorks ---------------------
''' functions: scaleRotate, pathTest  '''                                                                                         
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
   
   
### -------------------- dotsPathWorks ---------------------                                                                                                                                      



                                                           