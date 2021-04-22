import math
import os

from os import path

from PyQt5.QtCore    import Qt, QPointF, QTimer, QPropertyAnimation
from PyQt5.QtGui     import QPen, QColor, QPainterPath, QPixmap
from PyQt5.QtWidgets import QFileDialog, QGraphicsPixmapItem, QGraphicsItemGroup

from dotsAnimation   import Node
from dotsShared      import common, paths
from dotsSideGig     import TagIt, MsgBox
 
import dotsSidePath  as sidePath

ScaleUpKeys = ('>','\"', '=')
ScaleDnKeys = ('<',':','-')

### --------------------- dotsSideWays ---------------------
''' dotsSideWays: extends pathMaker. Includes path and
    waypoints functions - scaleRotate and pathTest '''
### --------------------------------------------------------
class SideWays():

    def __init__(self, parent, canvas):
        super().__init__()
 
        self.pathMaker = parent
        self.canvas    = canvas
        self.scene     = canvas.scene
        self.dots      = canvas.dots
           
        self.pathBall = None
        self.tagGroup = None        

        self.pathTestSet = False
        self.wayPtsSet = False  ## appear as tags

### ----------------------- paths --------------------------
    def setNewPath(self):
        if not self.pathMaker.pathSet and not self.wayPtsSet:
            if not self.pathMaker.newPathSet: 
                self.pathMaker.delete()  
                self.closeNewPath()
                self.dots.btnPathMaker.setStyleSheet(
                    "background-color: rgb(215,165,255)")
                self.pathMaker.newPath = None
                self.pathMaker.newPathSet = True
        else:
            MsgBox("addNewPath: Can't Add Path on Screen", 4)
      
    def closeNewPath(self):  ## applies only to newPath
        self.pathMaker.removeNewPath()  
        self.pathMaker.addPath()  ## add the completed path
        self.newPathOff() 
   
    def newPathOff(self):
        if not self.pathMaker.newPath:
            self.dots.btnPathMaker.setStyleSheet(
                "background-color: LIGHTGREEN")
            self.pathMaker.newPath = None
            self.pathMaker.newPathSet = False

    def halfPath(self):  
        tmp = []        
        for i in range(0, len(self.pathMaker.pts)):
            if i % 2 == 1:
                tmp.append(self.pathMaker.pts[i])
        self.pathMaker.pts = tmp
        self.pathMaker.redrawPoints(False)  ## redraw canvas without points
        if self.pathTestSet:
            self.stopPathTest()
            QTimer.singleShot(200, self.pathTest)  ## optional

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
            if self.wayPtsSet:
                self.updateWayPts()
            if self.pathTestSet:
                self.stopPathTest()
         
    def setPaintPath(self, bool=False):  ## also used by waypts
        path = QPainterPath()
        for pt in self.pathMaker.pts:  ## pts on the screen 
            if not path.elementCount():
                path.moveTo(QPointF(pt))
            path.lineTo(QPointF(pt)) 
        if bool: path.closeSubpath()
        return path

### ---------------------- waypoints -----------------------
    def addWayPtTags(self):
        self.pathMaker.removePoints()
        if self.pathMaker.newPathSet:
            return
        if self.wayPtsSet:  ## toggle it off
            self.removeWayPtTags()
            return   ## added
        lnn = len(self.pathMaker.pts)
        if lnn:                     ## make some tags
            self.addWayPtTagsGroup()
            inc = int(lnn/10)  # approximate a 10% increment
            list = (x*inc for x in range(0,10)) ## get the indexes
            for idx in list:
                pt = self.pathMaker.pts[idx]
                pct = (idx/lnn)*100
                if pct == 0.0: idx = lnn
                self.addWayPtTag(
                    self.makePtsTag(pt, idx, pct), 
                    pt)
            if self.pathMaker.openPathFile:  ## filename top left corner
                self.addWayPtTag(self.pathMaker.openPathFile, QPointF(5.0,5.0))
            self.wayPtsSet = True
 
    def addWayPtTagsGroup(self):
        self.tagGroup = QGraphicsItemGroup()
        self.scene.addItem(self.tagGroup)
        self.tagGroup.setZValue(common["pathZ"]+5)

    def addWayPtTag(self, tag, pt):
        self.tag = TagIt('pathMaker', tag, QColor("TOMATO"))   
        self.tag.setPos(pt)
        self.tag.setZValue(common["pathZ"]+5) 
        self.tagGroup.addToGroup(self.tag)
 
    def removeWayPtTags(self):   
        if self.tagGroup or self.wayPtsSet:
            self.scene.removeItem(self.tagGroup) 
            self.tagGroup = None
            self.wayPtsSet = False

    def makePtsTag(self, pt, idx, pct):  ## used by pointItem as well
        s = "(" + str("{:2d}".format(int(pt.x())))
        s = s + ", " + str("{:2d}".format(int(pt.y()))) + ")"
        s = s + "  " + str("{0:.2f}%".format(pct)) 
        s = s + "  " + str("{:2d}".format(idx))
        return s

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
        if self.wayPtsSet:
            self.updateWayPts()

    def updateWayPts(self):
        self.removeWayPtTags()
        self.pathMaker.addPath()
        self.addWayPtTags()

### --------------------------------------------------------
    def pathTest(self):
        if self.pathMaker.pts and self.pathMaker.pathSet:
            if not self.pathTestSet:
                self.ball = QGraphicsPixmapItem(QPixmap(paths['imagePath'] + 
                    'ball.png'))
                node = Node(self.ball)
                self.ball.setZValue(50)

                self.pathBall = QPropertyAnimation(node, b'pos')
                self.pathBall.setDuration(10000)  ## 10 seconds

                waypts = self.setPaintPath(True) ## close subpath
                pt = sidePath.getOffset(self.ball)

                self.pathBall.setStartValue(waypts.pointAtPercent(0.0)-pt)
                for i in range(1, 99):   
                    self.pathBall.setKeyValueAt(i/100.0, waypts.pointAtPercent(i/100.0)-pt)
                self.pathBall.setEndValue(waypts.pointAtPercent(1.0)-pt)  
                self.pathBall.setLoopCount(-1) 

                self.scene.addItem(self.ball)
                self.pathBall.start()
                self.pathTestSet = True
            else:
                self.stopPathTest()

    def stopPathTest(self): 
        if self.pathTestSet:  
            self.pathBall.stop()
            self.scene.removeItem(self.ball)
            self.pathBall = None
            self.pathTestSet = False

### --------------------------------------------------------
    def distance(self, x1, x2, y1, y2):
        dx = x1 - x2
        dy = y1 - y2
        return math.sqrt((dx * dx ) + (dy * dy))

    def getPathList(self, bool=False):  ## used by DoodleMaker
        try:                            ## also by context menu
            files = os.listdir(paths['paths'])
        except IOError:
            MsgBox("getPathList: No Path Directory Found!", 5)
            return None  
        filenames = []
        for file in files:
            if file.lower().endswith('path'): 
                if bool:    
                    file = os.path.basename(file)  ## short list
                    filenames.append(file)
                else:
                    filenames.append(paths['paths'] + file)
        if not filenames:
            MsgBox("getPathList: No Paths Found!", 5)
        return filenames

    def scaleRotate(self, key): 
        p = self.pathMaker.path.sceneBoundingRect()
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

        self.pathMaker.addPath()

### --------------------------------------------------------
    def getPts(self, file, scalor=1.0, inc=0):  ## also used by pathChooser
        try:
            tmp = []
            with open(file, 'r') as fp: 
                for line in fp:
                    ln = line.rstrip()  
                    ln = list(map(float, ln.split(',')))   
                    tmp.append(QPointF(ln[0]*scalor+inc, ln[1]*scalor+inc))
            return tmp
        except IOError:
            MsgBox("getPts: Error reading pts file")

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
            self.pathMaker.pts = self.getPts(file)  ## read the file
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

