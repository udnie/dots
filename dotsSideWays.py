import math
import os

from os import path

from PyQt5.QtCore    import Qt, QPointF, QPoint, QTimer, QPropertyAnimation
from PyQt5.QtGui     import QPen, QColor, QPainterPath, QPixmap
from PyQt5.QtWidgets import QFileDialog, QGraphicsPixmapItem, QGraphicsItemGroup

from dotsAnimation   import Node
from dotsShared      import common, paths
from dotsSideGig     import TagIt, MsgBox, getColorStr, getPts, distance
 
import dotsSidePath  as sidePath

ScaleUpKeys = ('>','\"', '=')
ScaleDnKeys = ('<',':','-')
Tick = 3  ## points to move using arrow keys

### --------------------- dotsSideWays ---------------------
''' dotsSideWays: extends pathMaker. Includes path and
    waypoints functions - scaleRotate and pathTest...'''
''' moved all scene references to pathMaker '''
### --------------------------------------------------------
class SideWays():

    def __init__(self, parent):
        super().__init__()
 
        self.pathMaker = parent
           
### ----------------------- paths --------------------------
    def centerPath(self):
        if self.pathMaker.pathSet:
            p = self.pathMaker.path.sceneBoundingRect()
            w = (common["ViewW"] - p.width()) /2
            h = (common["ViewH"] - p.height()) / 2
            x, y = w - p.x(), h - p.y()
            self.pathMaker.path.setPos(
                self.pathMaker.path.x()+x, 
                self.pathMaker.path.y()+y)
            self.updPts(x, y)

    def flipPath(self):  
        p = self.pathMaker.path.sceneBoundingRect()
        max = p.y() + p.height()
        for i in range(0, len(self.pathMaker.pts)):
            self.pathMaker.pts[i] = QPointF(
                self.pathMaker.pts[i].x(), 
                max - self.pathMaker.pts[i].y() + p.y())
        self.pathMaker.addPath()
  
    def flopPath(self): 
        p = self.pathMaker.path.sceneBoundingRect()
        max = p.x() + p.width()
        for i in range(0, len(self.pathMaker.pts)):
            self.pathMaker.pts[i] = QPointF(
                max - self.pathMaker.pts[i].x() + p.x(), 
                self.pathMaker.pts[i].y())
        self.pathMaker.addPath()

    def halfPath(self):  
        tmp = []        
        for i in range(0, len(self.pathMaker.pts)):
            if i % 2 == 1:
                tmp.append(self.pathMaker.pts[i])
        self.pathMaker.pts = tmp
        self.pathMaker.redrawPoints(False)  ## redraw canvas without points
        if self.pathMaker.pathTestSet:
            self.pathMaker.stopPathTest()
            QTimer.singleShot(200, self.pathTest)  ## optional

    def movePath(self, key):   
        if key == 'right':
            self.pathMaker.path.setPos(
                self.pathMaker.path.x()+Tick, 
                self.pathMaker.path.y())
            self.updPts(Tick, 0)
        elif key == 'left':
            self.pathMaker.path.setPos(
                self.pathMaker.path.x()-Tick, 
                self.pathMaker.path.y())
            self.updPts(-Tick, 0)
        elif key == 'up':
            self.pathMaker.path.setPos(
                self.pathMaker.path.x()+0, 
                self.pathMaker.path.y()-Tick)
            self.updPts(0, -Tick)
        elif key == 'down':
            self.pathMaker.path.setPos(
                self.pathMaker.path.x()+0, 
                self.pathMaker.path.y()+Tick)
            self.updPts(0, Tick)

    def updPts(self, tx, ty):    ## used by movePath
        pt = QPoint(float(tx), float(ty))
        for p in self.pathMaker.pts:  ## pts on the screen 
            p += pt     

    def reversePath(self):  
        if self.pathMaker.pts:
            tmp = []
            lnn = len(self.pathMaker.pts)-1
            for i in range(0, len(self.pathMaker.pts)):
                # k = lnn - i
                tmp.append(self.pathMaker.pts[lnn - i])
            tmp.insert(0,self.pathMaker.pts[0])   ## start at zero
            tmp = tmp[:-1]
            self.pathMaker.pts = tmp
            if self.pathMaker.wayPtsSet:
                self.updateWayPts()
            if self.pathMaker.pathTestSet:
                self.pathMaker.stopPathTest()
         
    def setPaintPath(self, bool=False):  ## also used by waypts
        path = QPainterPath()
        for pt in self.pathMaker.pts:  ## pts on the screen 
            if not path.elementCount():
                path.moveTo(QPointF(pt))
            path.lineTo(QPointF(pt)) 
        if bool: path.closeSubpath()
        return path

    def changePathColor(self):
        self.pathMaker.color = getColorStr()
        if self.pathMaker.newPathSet:
            self.pathMaker.updateNewPath()
        else:
            self.pathMaker.addPath()

### ---------------------- waypoints -----------------------
    def addWayPtTags(self):
        if self.pathMaker.newPathSet:
            return
        if self.pathMaker.wayPtsSet:  ## toggle it off
            self.pathMaker.removeWayPtTags()
            return   ## added
        lnn = len(self.pathMaker.pts)
        if lnn:                     ## make some tags
            self.pathMaker.addWayPtTagsGroup()
            inc = int(lnn/10)  # approximate a 10% increment
            list = (x*inc for x in range(0,10)) ## get the indexes
            for idx in list:
                pt = self.pathMaker.pts[idx]
                pct = (idx/lnn)*100
                if pct == 0.0: idx = lnn
                self.pathMaker.addWayPtTag(
                    self.makePtsTag(pt, idx, pct), 
                    pt)
            if self.pathMaker.openPathFile:  ## filename top left corner
                self.pathMaker.addWayPtTag(
                    self.pathMaker.openPathFile, 
                    QPointF(5.0,5.0))
            self.pathMaker.wayPtsSet = True
 
    def makePtsTag(self, pt, idx, pct):  ## used by pointItem as well
        s = "(" + str("{:2d}".format(int(pt.x())))
        s = s + ", " + str("{:2d}".format(int(pt.y()))) + ")"
        s = s + "  " + str("{0:.2f}%".format(pct)) 
        s = s + "  " + str("{:2d}".format(idx))
        return s

    def shiftWayPts(self, key):  
        lnn = int(len(self.pathMaker.pts)/20)  ## 5% solution
        tmp = []
        if key == '>':
            for i in range(lnn, len(self.pathMaker.pts)):
                tmp.append(self.pathMaker.pts[i])
            for i in range(0, len(self.pathMaker.pts)-len(tmp)):
                tmp.append(self.pathMaker.pts[i])
        else:
            for i in range(len(self.pathMaker.pts)-lnn, len(self.pathMaker.pts)):
                tmp.append(self.pathMaker.pts[i])
            for i in range(0, len(self.pathMaker.pts)-len(tmp)):
                tmp.append(self.pathMaker.pts[i])
        self.pathMaker.pts = tmp
        if self.pathMaker.wayPtsSet:
            self.updateWayPts()

    def updateWayPts(self):
        self.pathMaker.removeWayPtTags()
        self.pathMaker.addPath()
        self.addWayPtTags()

### --------------------------------------------------------
    def pathTest(self):
        if self.pathMaker.pts and self.pathMaker.pathSet:
            if not self.pathMaker.pathTestSet:
                self.pathMaker.ball = QGraphicsPixmapItem(QPixmap(paths['imagePath'] + 
                    'ball.png'))
                node = Node(self.pathMaker.ball)
                self.pathMaker.ball.setZValue(50)

                self.pathMaker.pathBall = QPropertyAnimation(node, b'pos')
                self.pathMaker.pathBall.setDuration(10000)  ## 10 seconds

                waypts = self.setPaintPath(True) ## close subpath
                pt = sidePath.getOffset(self.pathMaker.ball)

                self.pathMaker.pathBall.setStartValue(waypts.pointAtPercent(0.0)-pt)
                for i in range(1, 99):   
                    self.pathMaker.pathBall.setKeyValueAt(i/100.0, waypts.pointAtPercent(i/100.0)-pt)
                self.pathMaker.pathBall.setEndValue(waypts.pointAtPercent(1.0)-pt)  
                self.pathMaker.pathBall.setLoopCount(-1) 

                self.pathMaker.startPathTest()
            else:
                self.pathMaker.stopPathTest()

### --------------------------------------------------------
    def scaleRotate(self, key): 
        p = self.pathMaker.path.sceneBoundingRect()
        centerX = p.x() + p.width() /2
        centerY = p.y() + p.height() /2
        ## for each pt compute distance from center
        for i in range(0, len(self.pathMaker.pts)):    
            dist = distance(
                    self.pathMaker.pts[i].x(), centerX, 
                    self.pathMaker.pts[i].y(), centerY)
            inc, xdist, ydist = 0, dist, dist
            ## scale up, scale down
            if key in ScaleUpKeys:  
                dist = dist + ( dist * .01 )         
            elif key in ScaleDnKeys:  
                dist = dist - ( dist * .01 )
            ## rotate 1 degree
            if key == '+':  
                inc = -1.0   
            elif key == '_': 
                inc = 1.0      
            ## more scale stuff
            if key in('<','>'):
                xdist = dist                
                ydist = dist  
            elif key in(':','\"'): ## scale X
                xdist = dist              
            elif key in('-','='):  ## scale Y
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

### --------------------------------------------------------
    def openFiles(self):
        if self.pathMaker.pts:
            MsgBox("openFiles: Clear Scene First")
            return
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self.pathMaker,
            "Choose a path file to open", paths["paths"],
            "Files(*.path)")
        Q.accept()
        if file:
            self.pathMaker.pts = getPts(file)  ## read the file
            self.pathMaker.openPathFile = os.path.basename(file)
            self.pathMaker.addPath()
       
    def savePath(self):
        if self.pathMaker.pts:
            Q = QFileDialog()
            if self.pathMaker.openPathFile == '':
                self.pathMaker.openPathFile = paths["paths"] + 'tmp.path'
            f = Q.getSaveFileName(self.pathMaker,
                paths["paths"],
                self.pathMaker.openPathFile)
            Q.accept()
            if not f[0]: 
                return
            elif not f[0].lower().endswith('.path'):
                MsgBox("savePath: Wrong file extention - use '.path'")    
            else:
                try:
                    with open(f[0], 'w') as fp:
                        for i in range(0, len(self.pathMaker.pts)):
                            p = self.pathMaker.pts[i]
                            x = str("{0:.2f}".format(p.x()))
                            y = str("{0:.2f}".format(p.y()))
                            fp.write(x + ", " + y + "\n")
                        fp.close()
                except IOError:
                    MsgBox("savePath: Error saving file")
                    return
        else:
            MsgBox("savePath: Nothing saved")

### --------------------- dotsSideWays ---------------------

        #### save for now ########################
        # lnn = len(self.pathMaker.pts)
        # last = QPointF(0.0, 0.0)  ## save for now
        # for pt in self.pathMaker.pts:
        #     itm = PointItem(self, pt, idx, lnn)
        #     self.scene.addItem(itm)
        #     idx += 1
            # if last != QPointF(0.0, 0.0):   ## save for now
            #     print(int(self.distance(pt.x(), last.x(), 
            #         pt.y(), last.y())))
            # last = pt
        #### save for now ########################

