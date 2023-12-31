
import os
import math

from PyQt6.QtCore       import QRect, QPointF, QPoint
from PyQt6.QtGui        import QPixmap 
from PyQt6.QtWidgets    import QGraphicsPixmapItem

from dotsAnimation      import *  
from dotsShared         import RotateKeys, paths
from dotsSideGig        import distance, getColorStr
from dotsPathWidget     import PathWidget

ScaleRotate = ('<', '>', '+', '-')  ## sent from keyboard
ScaleUpKeys = ('>','\"','\'')
ScaleDnKeys = ('<',':',';')
     
### -------------------- dotsPathWorks ---------------------
''' no class: functions: scaleRotate, pathTest  '''                                                                                         
### --------------------------------------------------------
class PathWorks:
### --------------------------------------------------------
    def __init__(self, parent):  
        super().__init__()
        
        self.pathMaker = parent
        self.canvas    = self.pathMaker.canvas
        self.scene     = self.canvas.scene
         
        self.widget = self.pathMaker.widget
                
### -------------------------------------------------------- 
    def addWidget(self):  ## split code
        self.closeWidget()
        self.widget = PathWidget(self.pathMaker)       
        p = common['widgetXY']
        p = self.canvas.mapToGlobal(QPoint(p[0], p[1]))       
        self.widget.save = QPointF(p.x(), p.y())                          
        self.widget.setGeometry(p.x(), p.y(), \
            int(self.widget.WidgetW), int(self.widget.WidgetH))
        if self.pathMaker.addingNewPath:
            self.pathMaker.drawing.editBtn('ClosePath')
        if self.pathMaker.openPathFile != None:
            self.widget.label.setText(self.pathMaker.openPathFile)
            
    def closeWidget(self):
        if self.widget != None:
            self.widget.close()
            self.widget = None
  
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
    def changePathColor(self):
        self.pathMaker.color = getColorStr()
        if self.pathMaker.addingNewPath:
            self.pathMaker.updateNewPath()
        else:
            self.pathMaker.addPath()

    def removePoly(self):
        if self.pathMaker.poly != None:
            self.scene.removeItem(self.pathMaker.poly)
        self.pathMaker.poly = None
            
    def turnGreen(self):
        self.canvas.btnPathMaker.setStyleSheet(
            'background-color: rgb(55,240,140);\n'
            'border:  1px solid rgb(240,240,240); \n'
            'font-size: 13px;\n'
            'color:  white;')
        self.canvas.showWorks.disablePlay()
         
    def turnBlue(self):
        self.canvas.btnPathMaker.setStyleSheet(
            'background-color: rgb(200,128,255);\n'
            'border:  1px solid rgb(240,240,240); \n'
            'font-size: 13px;\n'
            'color:  white;')
                                                                                            
### -------------------- dotsPathWorks ---------------------                                                                                                                                      



                                                           