import math
import os

from os import path

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from dotsAnimation   import Node
from dotsShared      import common, paths
from dotsSideCar     import TagIt, PointItem
 
import dotsSidePath  as sidePath

ScaleUpKeys = ('>','\"', '=')
ScaleDnKeys = ('<',':','-')

### --------------------- dotsSideWays ---------------------
''' dotsSideWays: extends pathMaker. Includes path and
    waypoints functions - scaleRotate and pathTest '''
### -------------------------------------------------------
class SideWays():

    def __init__(self, parent, dots):
        super().__init__()
 
        self.dots = dots
        self.pathMaker = parent
        self.scene  = parent.scene
        self.mapper = parent.mapper 
         
        self.npts = 0
        self.tagZ = common["pathZ"]

        self.polyline = None
        self.tagGroup = None
 
### --------------------------------------------------------
    def addNewPath(self):
        if not self.pathMaker.newPath:
            self.pathMaker.pts = []   
            self.resetPolyline()
            self.dots.btnPathMaker.setStyleSheet(
                "background-color: rgb(255,120,90)")
            self.pathMaker.newPath = True
        else:
            self.closePath()
 
    def closePath(self):
        self.npts = 0
        self.removePolyline()  
        self.pathMaker.drawPolygon()
        self.newPathOff() 

    def addPathPts(self, pt):
        if self.npts == 0:
            self.pathMaker.pts.append(pt)
        self.npts += 1
        if self.npts % 3 == 0:
            self.pathMaker.pts.append(pt)
            self.drawPolyline()

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

    def drawPolyline(self):
        if self.pathMaker.polylineSet:
            self.scene.removeItem(self.polyline) 
        self.polyline = QGraphicsPathItem(self.setPaintPath())
        self.polyline.setPen(QPen(QColor(self.pathMaker.color), 
            3, Qt.DashDotLine))
        self.scene.addItem(self.polyline)
        self.pathMaker.polylineSet = True

    def addPts(self):
        if self.pathMaker.ptsSet:
            self.removePts()
            return
        idx = 0
        for pt in self.pathMaker.pts:
            itm = PointItem(self, pt, idx)
            self.scene.addItem(itm)
            idx += 1
        self.pathMaker.ptsSet = True

    def addPointItem(self, itm):
        idx, pt = itm.idx + 1, itm.pt
        if idx == len(self.pathMaker.pts): idx = 0     
        pt1 = self.pathMaker.pts[idx]
        pt1 = QPointF(pt1.x() - pt.x(), pt1.y() - pt.y())
        pt1 = pt + QPointF(pt1)*.5       
        self.pathMaker.pts.insert(idx, pt1)
        self.redrawPts()
   
    def deletePointItem(self, itm):
        self.pathMaker.pts.pop(itm.idx)
        self.redrawPts()

    def redrawPts(self):
        self.removePts()
        self.pathMaker.removeWayPts()
        self.pathMaker.removePolygon()
        self.pathMaker.drawPolygon()
        self.addWayPts()
        self.addPts()

    def removePts(self):
        for pts in self.scene.items():
            if pts.type == 'pt':
                self.scene.removeItem(pts)
            elif pts.zValue() <= self.tagZ:
                break
        self.pathMaker.ptsSet = False

    def removePolyline(self):    
        if self.pathMaker.polylineSet and self.polyline != None:
            self.scene.removeItem(self.polyline) 
        self.resetPolyline()

    def resetPolyline(self):
        self.pathMaker.polylineSet = False
        self.polyline = None

    def newPathOff(self):
        if self.pathMaker.newPath:
            self.dots.btnPathMaker.setStyleSheet(
                "background-color: rgba(0,255,0,100)")
            self.pathMaker.newPath = False

    def changePathColor(self):
        self.pathMaker.color = self.mapper.getColorStr()
        if self.pathMaker.newPath:
            self.drawPolyline()
        else:
            self.pathMaker.drawPolygon()

### --------------------------------------------------------
    def addWayPts(self):
        if self.pathMaker.wayPtsSet:  ## toggle it off
            self.pathMaker.removeWayPts()
            return   ## added
        else:
            lnn = len(self.pathMaker.pts)
            if lnn:                     ## make some tags
                self.addTagGroup()
                inc = int(lnn/10)  # approximate a 10% increment
                list = (x*inc for x in range(0,10)) ## get the indexes
                for idx in list:
                    pt = self.pathMaker.pts[idx]
                    pct = (idx/lnn)*100
                    if pct == 0.0: idx = lnn
                    self.addPathTag(
                        self.makePtsTag(pt, idx, pct), 
                        pt)
                if self.pathMaker.openPathFile:  ## filename top left corner
                    self.addPathTag(self.pathMaker.openPathFile, QPointF(5.0,5.0))
                self.pathMaker.wayPtsSet = True
 
    def makePtsTag(self, pt, idx, pct):
        s = "(" + str("{:2d}".format(int(pt.x())))
        s = s + ", " + str("{:2d}".format(int(pt.y()))) + ")"
        s = s + "  " + str("{0:.2f}%".format(pct)) 
        s = s + "  " + str("{:2d}".format(idx))
        return s

    def addPathTag(self, tag, pt):
        self.tag = TagIt('pathMaker', tag, QColor("TOMATO"))   
        self.tag.setPos(pt)
        self.tag.setZValue(self.tagZ) 
        self.scene.addItem(self.tag)   ## do this as well 
        self.tagGroup.addToGroup(self.tag)

    def addPtsTag(self, tag, pt):
        self.ptsTag = TagIt('points', tag, QColor("YELLOW"))   
        p = QPointF(0,-20)
        self.ptsTag.setPos(pt+p)
        self.ptsTag.setZValue(self.tagZ+10) 
        self.scene.addItem(self.ptsTag) 

    def removePtsTag(self):
        self.scene.removeItem(self.ptsTag) 
    
    def addTagGroup(self):
        self.tagGroup = QGraphicsItemGroup()
        self.scene.addItem(self.tagGroup)
        self.tagGroup.setZValue(self.tagZ)

    def setPaintPath(self, bool=False):  ## used by waypts
        path = QPainterPath()
        for pt in self.pathMaker.pts:  ## pts on the screen 
            if not path.elementCount():
                path.moveTo(QPointF(pt))
            path.lineTo(QPointF(pt)) 
        if bool: path.closeSubpath()
        return path

    def distance(self, x1, x2, y1, y2):
        dx = x1 - x2
        dy = y1 - y2
        return math.sqrt((dx * dx ) + (dy * dy))

    def scaleRotate(self, key): 
        p = self.pathMaker.polygon.sceneBoundingRect()
        centerX = p.x() + p.width() /2
        centerY = p.y() + p.height() /2
        ## for each pt compute distance from center
        for i in range(0, len(self.pathMaker.pts)):    
            dist = self.distance(
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

        self.pathMaker.drawPolygon()

    def pathTest(self):
        if self.pathMaker.pts and self.pathMaker.polySet:
            if not self.pathMaker.pathTestSet:
                self.ball = QGraphicsPixmapItem(QPixmap(paths['imagePath'] + 
                    'ball.png'))
                node = Node(self.ball)
                self.path = QPropertyAnimation(node, b'pos')
                self.path.setDuration(10000)  ## 10 seconds

                waypts = self.setPaintPath(True) ## close subpath
                pt = sidePath.getOffset(self.ball)

                self.path.setStartValue(waypts.pointAtPercent(0.0)-pt)
                for i in range(1, 99):   
                    self.path.setKeyValueAt(i/100.0, waypts.pointAtPercent(i/100.0)-pt)
                self.path.setEndValue(waypts.pointAtPercent(1.0)-pt)  
                self.path.setLoopCount(-1) 

                self.scene.addItem(self.ball)
                self.path.start()
                self.pathMaker.pathTestSet = True
            else:
                self.stopPathTest()

    def stopPathTest(self): 
        if self.pathTest:  
            self.path.stop()
            self.scene.removeItem(self.ball)
            self.pathMaker.pathTestSet = False

    def reverseIt(self):  
        tmp = []
        l = len(self.pathMaker.pts)-1
        for i in range(0, len(self.pathMaker.pts)):
            k = l-i
            tmp.append(self.pathMaker.pts[k])
        tmp.insert(0,self.pathMaker.pts[0])   ## start at zero
        tmp = tmp[:-1]
        self.pathMaker.pts = tmp
        self.updateWayPts()

    def shiftWayPts(self, key):  
        l = int(len(self.pathMaker.pts)/20)  ## 5% solution
        tmp = []
        if key == '>':
            for i in range(l, len(self.pathMaker.pts)):
                tmp.append(self.pathMaker.pts[i])
            for i in range(0, len(self.pathMaker.pts)-len(tmp)):
                tmp.append(self.pathMaker.pts[i])
        else:
            for i in range(len(self.pathMaker.pts)-l, len(self.pathMaker.pts)):
                tmp.append(self.pathMaker.pts[i])
            for i in range(0, len(self.pathMaker.pts)-len(tmp)):
                tmp.append(self.pathMaker.pts[i])
        self.pathMaker.pts = tmp
        self.updateWayPts()

    def updateWayPts(self):
        self.pathMaker.removeWayPts()
        self.pathMaker.drawPolygon()
        self.addWayPts()
     
### --------------------- dotsSideWays ---------------------

