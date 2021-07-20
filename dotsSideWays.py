import math
import os

from os import path

from PyQt5.QtCore    import Qt, QPointF, QPoint, QTimer, QPropertyAnimation
from PyQt5.QtGui     import QPen, QColor, QPainterPath, QPixmap
from PyQt5.QtWidgets import QFileDialog, QGraphicsPixmapItem, QGraphicsItemGroup

from dotsShared      import common, paths
from dotsSideGig     import TagIt, MsgBox, getPts, distance
 
ScaleUpKeys = ('>','\"', '=')
ScaleDnKeys = ('<',':','-')
Tick = 3  ## points to move using arrow keys

### --------------------- dotsSideWays ---------------------
''' dotsSideWays: extends pathMaker. Includes path and wayPoints
    functions - scaleRotate, flopPath, reversePath, etc..'''
### --------------------------------------------------------
class SideWays():
### --------------------------------------------------------
    def __init__(self, pathMaker, drawing, parent):
        super().__init__()
 
        self.pathMaker = pathMaker

        self.canvas    = parent
        self.scene     = parent.scene
        self.drawing   = drawing

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
        del tmp
        self.drawing.redrawPoints(False)  ## redraw canvas without points
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
        pt = QPoint(float(tx), float(ty)) ## either x or y, + or -
        for p in self.pathMaker.pts:  ## pts on the screen 
            p += pt  ## add pt to point 'p' in pts

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
            del tmp
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

    def openFiles(self):
        if self.pathMaker.pts:
            MsgBox("openFiles: Clear Scene First")
            return
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self.pathMaker.canvas,
            "Choose a path file to open", paths["paths"],
            "Files(*.path)")
        Q.accept()
        if file:
            self.pathMaker.pts = getPts(file)  ## read the file
            self.pathMaker.openPathFile = os.path.basename(file)
            self.pathMaker.addPath()
       
    def savePath(self):
        if self.pathMaker.pts:
            if self.pathMaker.addingNewPath != False: 
                MsgBox("savePath: Close the new path using 'cmd'")  
                return
            Q = QFileDialog()
            if self.pathMaker.openPathFile == '':
                self.pathMaker.openPathFile = paths["paths"] + 'tmp.path'
            f = Q.getSaveFileName(self.pathMaker.canvas,
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

### ---------------------- waypoints -----------------------
    def addWayPtTags(self):
        if self.pathMaker.addingNewPath:
            return
        if self.pathMaker.wayPtsSet:  ## toggle it off
            self.pathMaker.removeWayPtTags()
            self.drawing.removePointItems()
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
        s = s + "  " + str("{0:2d}".format(idx))
        return s

    def shiftWayPtsLeft(self):  
        self.shiftWayPts('<')

    def shiftWayPtsRight(self):  
        self.shiftWayPts('>')

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
        del tmp
        if self.pathMaker.wayPtsSet:
            self.updateWayPts()

    def updateWayPts(self):
        # bol = self.pathMaker.pointItemsSet()
        # if bol: self.pathMaker.removePointItems()
        self.pathMaker.removeWayPtTags()
        self.pathMaker.removePath()
        self.pathMaker.addPath()
        self.addWayPtTags()
        # if bol: self.pathMaker.addPointItems()

### --------------------- dotsSideWays ---------------------


