
import os

from PyQt6.QtCore       import QPointF, QTimer
from PyQt6.QtGui        import QColor
from PyQt6.QtWidgets    import QFileDialog,  QGraphicsItemGroup

from dotsAnimation      import *  
from dotsShared         import common, paths
from dotsSideGig        import MsgBox, getPts
from dotsTagsAndPaths   import TagIt
                                 
### --------------------- dotsPathWays ---------------------
''' class PathWays: extends pathMaker. Includes path and wayPoints
    functions - flopPath, reversePathetc..'''
### --------------------------------------------------------
class PathWays:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.pathMaker = parent
        self.canvas    = self.pathMaker.canvas
        self.scene     = self.canvas.scene
            
        self.tagGroup = None  
    
### -------------------- path transforms -------------------
    def centerPath(self):
        if self.pathMaker.pathSet and self.pathMaker.path != None:
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
        if self.pathMaker.path != None:      
            p = self.pathMaker.path.sceneBoundingRect()
            max = p.y() + p.height()
            for i in range(len(self.pathMaker.pts)):
                self.pathMaker.pts[i] = QPointF(
                    self.pathMaker.pts[i].x(), 
                    max - self.pathMaker.pts[i].y() + p.y())
            self.pathMaker.addPath()
            self.editingPtsSet()  
  
    def flopPath(self): 
        if self.pathMaker.path != None: 
            p = self.pathMaker.path.sceneBoundingRect()
            max = p.x() + p.width()
            for i in range(len(self.pathMaker.pts)):
                self.pathMaker.pts[i] = QPointF(
                    max - self.pathMaker.pts[i].x() + p.x(), 
                    self.pathMaker.pts[i].y())
            self.pathMaker.addPath()
            self.editingPtsSet()  

    def fullPath(self):
        self.halfPath(True)
        self.editingPtsSet()  

    def halfPath(self, full=False):  ## reduces number of points in half
        if self.pathMaker.pathTestSet == True:
            self.pathMaker.pathWorks.stopPathTest()
        tmp = []
        lnn = len(self.pathMaker.pts) if full else int(len(self.pathMaker.pts)/2) + 1       
        ## using painter path to get the pointAtPercent
        path = self.pathMaker.pathWorks.setPaintPath(True)  ## close subpath, uses self.pts
        vals = [p/lnn for p in range(lnn)]  ## evenly spaced points
        for i in vals:
            tmp.append(QPointF(path.pointAtPercent(i)))
        self.pathMaker.pts = tmp    
        del tmp
        del vals
        del path
        QTimer.singleShot(200, self.pathMaker.edits.redrawPoints)

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
        if len(self.pathMaker.pts) > 0:
            if self.pathMaker.pathTestSet:
                self.pathMaker.pathWorks.stopPathTest()      
            tmp = []    
            lnn = len(self.pathMaker.pts)-1        
            for i in range(len(self.pathMaker.pts)):
                tmp.append(self.pathMaker.pts[lnn - i])
            tmp.insert(0,self.pathMaker.pts[0])  ## start at zero
            self.pathMaker.pts = tmp[:-1] 
            del tmp
            self.cleanUp()
            
    def cleanUp(self):
        self.redrawTagsAndPaths() if self.tagCount() > 0 else self.pathMaker.addPath()
        self.pathMaker.edits.redrawPoints(self.pathMaker.edits.pointItemsSet())
         
    def editingPtsSet(self):
        if self.pathMaker.editingPts == True:
            self.pathMaker.edits.updatePath()
                            
### ----------------- load and save paths ------------------
    def openFiles(self):
        if self.pathMaker.pts:
            MsgBox('openFiles: Clear Scene First', 5)
            return
        Q = QFileDialog()
        Q.Option.DontUseNativeDialog
        Q.setDirectory(paths['paths'])
        file, _ = Q.getOpenFileName(self.canvas,
            'Choose a path file to open', paths['paths'], 'Files(*.path)')
        Q.accept()
        if file:
            self.pathMaker.pts = getPts(file)  ## in sideGig  
            self.pathMaker.openPathFile = os.path.basename(file)
            self.pathMaker.addPath()
         
    def savePath(self):
        if len(self.pathMaker.pts) > 0:
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
                paths['paths'] + self.pathMaker.openPathFile,  
                'Files(*.path)')  ## <--- note
            Q.accept()                                                  
            if not f[0]: 
                return
            if not f[0].lower().endswith('.path'):
                MsgBox("savePath: Missing or Wrong file extention - use '.path'", 5)   
                return       
            try:
                with open(f[0], 'w') as fp:
                    for i in range(len(self.pathMaker.pts)):
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
            for i in range(len(self.pathMaker.pts)-len(tmp)):
                tmp.append(self.pathMaker.pts[i])
        else:
            for i in range(len(self.pathMaker.pts)-lnn, len(self.pathMaker.pts)):
                tmp.append(self.pathMaker.pts[i])
            for i in range(len(self.pathMaker.pts)-len(tmp)):
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
        list = (x*inc for x in range(10))  ## get the indexes
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
        self.tag.setZValue((common['pathZ'])+35) 
        self.tagGroup.addToGroup(self.tag)
           
    def addWayPtTagsGroup(self):
        self.tagGroup = QGraphicsItemGroup()
        self.tagGroup.setZValue((common['pathZ'])+35)
        self.scene.addItem(self.tagGroup)
                 
    def redrawTagsAndPaths(self):
        self.removeWayPtTags()
        self.pathMaker.removePath()
        self.pathMaker.addPath()
        self.addWayPtTags()
             
    def removeWayPtTags(self):   
        if self.tagCount() > 0:  ## don't change
            self.scene.removeItem(self.tagGroup) 
            self.tagGroup = None
                   
    def makePtsTag(self, pt, idx, pct):  ## used by pointItem as well
        return f"({pt.x():.2f}, {pt.y():.2f})  %{pct:.2f}   {idx}"
    
    def tagCount(self):  ## shared among path modules - there's one in mapper as well
        return sum(pix.type == 'tag' 
            for pix in self.scene.items())
                         
### --------------------- dotsPathWays ---------------------



