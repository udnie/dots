
import os
import math

from PyQt6.QtCore    import QPointF, QTimer
from PyQt6.QtGui     import QColor
from PyQt6.QtWidgets import QFileDialog,  QGraphicsItemGroup

from dotsShared      import common, paths, RotateKeys
from dotsSideGig     import MsgBox, getPts, TagIt, distance
from dotsDrawsPaths  import DrawsPaths
 
ScaleUpKeys = ('>','\"','\'')
ScaleDnKeys = ('<',':',';')
                
### --------------------- dotsSideWays ---------------------
''' dotsSideWays: extends pathMaker. Includes path and wayPoints
    functions - scaleRotate, flopPath, reversePath, etc..'''
### --------------------------------------------------------
class SideWays:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.pathMaker = parent
        self.canvas    = self.pathMaker.canvas
        self.scene     = self.pathMaker.scene
        self.drawing   = DrawsPaths(self.pathMaker, self, self.canvas) 
        
        self.tagGroup = None  
    
### -------------------- path transforms -------------------
    def centerPath(self):
        if self.pathMaker.pathSet:
            p = self.pathMaker.path.sceneBoundingRect()
            w = (common['ViewW'] - p.width()) /2
            h = (common['ViewH'] - p.height()) / 2
            x = w - p.x()
            y = h - p.y()
            self.pathMaker.path.setPos(
                self.pathMaker.path.x()+x, 
                self.pathMaker.path.y()+y)
            self.updatePts(float(x), float(y))
            self.editingPtsSet()  
        
    def flipPath(self):         
        p = self.pathMaker.path.sceneBoundingRect()
        max = p.y() + p.height()
        for i in range(0, len(self.pathMaker.pts)):
            self.pathMaker.pts[i] = QPointF(
                self.pathMaker.pts[i].x(), 
                max - self.pathMaker.pts[i].y() + p.y())
        self.pathMaker.addPath()
        self.editingPtsSet()  
  
    def flopPath(self):  
        p = self.pathMaker.path.sceneBoundingRect()
        max = p.x() + p.width()
        for i in range(0, len(self.pathMaker.pts)):
            self.pathMaker.pts[i] = QPointF(
                max - self.pathMaker.pts[i].x() + p.x(), 
                self.pathMaker.pts[i].y())
        self.pathMaker.addPath()
        self.editingPtsSet()  

    def fullPath(self):
        self.halfPath(True)
        self.editingPtsSet()  

    def halfPath(self, full=False):
        if self.pathMaker.pathTestSet:
            self.pathMaker.stopPathTest()
        tmp = []
        if full:  ## use all the points
            lnn = len(self.pathMaker.pts)    
        else:     ## use half the points
            lnn = int(len(self.pathMaker.pts)/2) + 1       
        ## using painter path to get the pointAtPercent
        path = self.pathMaker.setPaintPath(True)  ## close subpath, uses self.pts
        vals = [p/lnn for p in range(0, lnn)]  ## evenly spaced points
        for i in vals:
            tmp.append(QPointF(path.pointAtPercent(i)))
        self.pathMaker.pts = tmp    
        del tmp
        del vals
        del path
        QTimer.singleShot(200, self.drawing.redrawPoints)

    def movePath(self, key):  ## updates one tick[key] at a time
        pos = self.pathMaker.path.pos()
        self.pathMaker.path.setPos(pos.x() + float(key[0]),
            pos.y() + float(key[1]))
        self.updatePts(float(key[0]), float(key[1]))
        self.editingPtsSet()  
   
    def updatePts(self, x, y): 
        tmp = []
        for p in self.pathMaker.pts:
            tmp.append(QPointF(p) + QPointF(x,y))
        self.pathMaker.pts = tmp
        del tmp
        
    def reversePath(self):  
        if self.pathMaker.pts:
            if self.pathMaker.pathTestSet:
                self.pathMaker.stopPathTest()      
            tmp = []    
            lnn = len(self.pathMaker.pts)-1        
            for i in range(0, len(self.pathMaker.pts)):
                tmp.append(self.pathMaker.pts[lnn - i])
            tmp.insert(0,self.pathMaker.pts[0])  ## start at zero
            self.pathMaker.pts = tmp[:-1] 
            del tmp
            self.cleanUp()
            
    def cleanUp(self):
        if self.tagCount() > 0:
            self.pathMaker.redrawPathsAndTags() 
        else: 
            self.pathMaker.addPath()    
        self.drawing.redrawPoints(self.drawing.pointItemsSet())
        
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
            else:   
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
        self.editingPtsSet()   
     
    def editingPtsSet(self):
        if self.pathMaker.editingPts == True:
            self.drawing.updatePath()
     
### ----------------- load and save paths ------------------
    def openFiles(self):
        if self.pathMaker.pts:
            MsgBox('openFiles: Clear Scene First', 5)
            return
        Q = QFileDialog()
        Q.Option.DontUseNativeDialog
        Q.setDirectory(paths['paths'])
        file, _ = Q.getOpenFileName(self.canvas,
            'Choose a path file to open', paths['paths'],
            'Files(*.path)')
        Q.accept()
        if file:
            self.pathMaker.pts = getPts(file)  ## in sideGig  
            self.pathMaker.openPathFile = os.path.basename(file)
            self.pathMaker.addPath()
       
    def savePath(self):
        if self.pathMaker.pts:
            if self.pathMaker.addingNewPath != False: 
                MsgBox("savePath: Close the new path using 'cmd'", 5)  
                return  
            
            if self.pathMaker.openPathFile == '':
                self.pathMaker.openPathFile = paths['paths'] + 'tmp.path' 
                     
            ##  self.pathMaker.openPathFile has no path attached to it            
            Q = QFileDialog()
            Q.Option.DontUseNativeDialog
            Q.setDirectory(paths['paths'])
            f = Q.getSaveFileName(self.canvas, paths['paths'],
                paths['paths'] + self.pathMaker.openPathFile)  ## note
            Q.accept()  
                  
            if not f[0]: 
                return
            elif not f[0].lower().endswith('.path'):
                MsgBox("savePath: Wrong file extention - use '.path'", 5)   
                return 
            else:
                try:
                    with open(f[0], 'w') as fp:
                        for i in range(0, len(self.pathMaker.pts)):
                            p = self.pathMaker.pts[i]
                            x = '{0:.2f}'.format(p.x())
                            y = '{0:.2f}'.format(p.y())
                            fp.write(x + ', ' + y + '\n')
                        fp.close()
                except IOError:
                    MsgBox('savePath: Error saving file', 5)
                    return
        else:
            MsgBox('savePath: Nothing saved', 5)

### ---------------------- waypoints ----------------------- 
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
        self.cleanUp()
        
### --------------------- wayPtTags ------------------------
    def addWayPtTags(self):
        if self.pathMaker.addingNewPath:
            return
        if not self.pathMaker.pts:
            return
        if self.tagCount() > 0: 
            self.removeWayPtTags()
            return
        self.pathMaker.addPath()  ## refresh path
        if lnn := len(self.pathMaker.pts):
            self.makeTags(lnn)
            
    def makeTags(self, lnn):
        self.addWayPtTagsGroup()
        inc = int(lnn/10)  ## approximate a 10% increment
        list = (x*inc for x in range(0,10))  ## get the indexes
        for idx in list:
            pt = QPointF(self.pathMaker.pts[idx])
            pct = (idx/lnn)*100
            if pct == 0.0:  ## first and last, wraps
                idx = lnn
            tag = self.makePtsTag(pt, idx, pct)
            self.addWayPtTag(tag, pt)
        del list
                       
    def addWayPtTag(self, tag, pt):
        self.tag = TagIt('pathMaker', tag, QColor('TOMATO'))   
        self.tag.setPos(QPointF(pt))
        self.tag.setZValue(common['tagZ']+5) 
        self.tagGroup.addToGroup(self.tag)
           
    def addWayPtTagsGroup(self):
        self.tagGroup = QGraphicsItemGroup()
        self.tagGroup.setZValue(common['tagZ']+5)
        self.scene.addItem(self.tagGroup)
         
    def removeWayPtTags(self):   
        if self.tagCount() > 0:  ## don't change
            self.scene.removeItem(self.tagGroup) 
            self.tagGroup = None
                   
    def makePtsTag(self, pt, idx, pct):  ## used by pointItem as well
        s = '(' + '{:2d}'.format(int(pt.x()))
        s = s + ', ' + '{:2d}'.format(int(pt.y())) + ')'
        s = s + '  ' + '{0:.2f}%'.format(pct)
        s = s + '  ' + '{0:2d}'.format(idx)
        return s
        
    def pixCount(self):  
        return sum(pix.type == 'pix' 
            for pix in self.scene.items())
        
    def tagCount(self):  
        return sum(pix.type == 'tag' 
            for pix in self.scene.items())
                
### --------------------- dotsSideWays ---------------------


