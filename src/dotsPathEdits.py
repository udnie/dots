
from PyQt6.QtCore    import Qt, QPointF, QEvent, QTimer
from PyQt6.QtGui     import QBrush, QColor, QCursor, QPen, QPolygonF, QGuiApplication
from PyQt6.QtWidgets import QWidget, QGraphicsPolygonItem 
                            
from dotsShared      import common
from dotsPointItem   import PointItem

### ------------------- dotsPathEdits ---------------------
''' class: PathEdits, functions; newPath, lasso '''
### --------------------------------------------------------
class PathEdits(QWidget):
### --------------------------------------------------------
    def __init__(self, pathMaker, sideWays, parent):  
        super().__init__()

        self.canvas = parent
        self.scene  = self.canvas.scene
        self.view   = self.canvas.view
        
        self.pathMaker = pathMaker  
        self.sideWays  = sideWays
          
        self.dragCnt = 0 
        
        self.lassoSet = False
        self.polySet = False
        
        self.poly = None
        self.lasso = []
        
        self.view.viewport().installEventFilter(self)
             
### --------------------- event filter ----------------------          
    def eventFilter(self, source, e):  ## used by lasso    
        if self.canvas.pathMakerOn:
    
            if self.pathMaker.editingPts and self.lassoSet:
                if e.type() == QEvent.Type.MouseButtonPress and \
                    e.buttons() == Qt.MouseButton.LeftButton:
                    self.addLassoPts(e.pos()) 
             
                elif e.type() == QEvent.Type.MouseMove and \
                    e.buttons() == Qt.MouseButton.LeftButton:
                    self.dragCnt += 1
                    if self.dragCnt % 5 == 0:        
                        self.addLassoPts(e.pos()) 
                         
                elif e.type() == QEvent.Type.MouseButtonRelease:
                    self.finalizeSelections(e.pos())
               
        return QWidget.eventFilter(self, source, e)    
     
### ---------------------- new path ------------------------  
    def toggleNewPath(self):  ## changed - use delete instead or 'N'
        if self.pathMaker.addingNewPath: 
            if len(self.pathMaker.pts) == 0:
                self.deleteNewPath()
            else:
                self.closeNewPath()  ## if there's not a path on display or waypt tags
        elif not self.pathMaker.pathSet:
            self.addNewPath()

    def addNewPath(self):
        self.canvas.btnPathMaker.setStyleSheet(
            'background-color: rgb(215,165,255)')
        self.pathMaker.addingNewPath = True
        self.pathMaker.newPath = None
        self.pathMaker.npts = 0
        self.pathMaker.pts = []
        self.editBtn('ClosePath')
        self.pathMaker.closeWidget()
 
    def closeNewPath(self):  ## applies only to adding a path
        if self.pathMaker.addingNewPath:  ## note
            self.removeNewPath()  
            self.pathMaker.turnGreen()
            self.pathMaker.addPath()  ## draws a polygon rather than painter path
   
    def removeNewPath(self):  ## keep self.pathMaker.pts for path
        if self.pathMaker.addingNewPath:
            if self.pathMaker.newPath:            
                self.scene.removeItem(self.pathMaker.newPath)
            self.pathMaker.addingNewPath = False
            self.pathMaker.newPath = None
            self.pathMaker.npts = 0
                            
    def editBtn(self, str):
        if self.pathMaker.widget:
            self.pathMaker.widget.newBtn.setText(str)
                 
    def deleteNewPath(self):  ## changed your mind, doesn't save pts
        if self.pathMaker.addingNewPath:
            self.removeNewPath()
            self.pathMaker.turnGreen()
            self.pathMaker.pts = []
            self.pathMaker.pathSet = False
                      
### ------------------------ lasso ------------------------- 
    def toggleLasso(self):
        if self.lassoSet:
            self.deleteLasso()
        else:
            self.newLasso()
  
    def newLasso(self): 
        self.lassoSet = True 
        self.lasso = []  
        if self.pathMaker.widget != None:
            self.pathMaker.widget.close()
        QGuiApplication.setOverrideCursor(QCursor(Qt.CursorShape.CrossCursor))
 
    def deleteLasso(self):
        self.lassoSet = False
        self.lasso = []
        QGuiApplication.restoreOverrideCursor()
               
    def addLassoPts(self, p):
        self.lasso.append(QPointF(p))
        self.drawLasso()
                  
    def drawPoly(self, pts):  ## returns polygon used by qgraphicspolygonitem
        poly = QPolygonF()    ## not used by newPath or for animation
        for p in pts:   ## pts can either be from lasso or pathMaker
            poly.append(QPointF(p))
        return poly               
                                
    def drawLasso(self): 
        if self.polySet:
            self.scene.removeItem(self.poly)    
        self.poly = QGraphicsPolygonItem(self.drawPoly(self.lasso)) 
        self.poly.setBrush(QBrush(QColor(125,125,125,50)))
        self.poly.setPen(QPen(QColor('lime'), 2, Qt.PenStyle.DotLine))
        self.poly.setZValue(common['pathZ']) 
        self.scene.addItem(self.poly)
        self.polySet = True
 
    def removePoly(self): 
        if self.polySet:
            self.scene.removeItem(self.poly)  
            self.polySet = False
            self.poly = None
                                      
### -------------------- pointItems ------------------------    
    def togglePointItems(self):
        if self.lassoSet: 
            self.deleteLasso()
        if self.pointItemsSet():
            self.removePointItems()
        else:
            self.addPointItems()

    def addPointItems(self): 
        idx = 0 
        add = self.findTop() + 10  ## added to idx to set zvalue
        for pt in self.pathMaker.pts:  
            self.scene.addItem(PointItem(self, self.canvas, pt, idx, add))
            idx += 1

    def editPoints(self):
        if not self.pathMaker.pts:
            return
        if self.pathMaker.editingPts == False:
            self.pathMaker.editingPts = True
            self.pathMaker.selections = []  
            self.addPointItems()
            self.turnBlue()
        else:
            self.editPointsOff()

    def editPointsOff(self):
        self.pathMaker.editingPts = False
        self.pathMaker.selections = []
        self.removePointItems()
        self.pathMaker.turnGreen()
                   
    def removePointItems(self):   
        for ptr in self.scene.items():
            if ptr.type in ('pt','ptTag'):
                self.scene.removeItem(ptr)
                del ptr

    def pointItemsSet(self):
        for itm in self.scene.items():
            if itm.type == 'pt':
                return True
        return False

    def insertPointItem(self, pointItem):  ## halfway between points
        idx, pt = pointItem.idx + 1, pointItem.pt  ## idx, the next point
        if idx == len(self.pathMaker.pts): 
            idx = 0   
        if self.pathMaker.selections:
            self.insertSelection(pointItem.idx)  
        pt1 = self.pathMaker.pts[idx]  ## calculate new x,y
        pt1 = QPointF(pt1.x() - pt.x(), pt1.y() - pt.y())
        pt1 = pt + QPointF(pt1)*.5       
        self.pathMaker.pts.insert(idx, pt1)
        self.redrawPoints()  
            
    def deletePointItem(self, idx):  
        self.removeSelection(idx)
        self.pathMaker.pts.pop(idx) 
        self.redrawPoints()
       
    def redrawPoints(self, bool=True):  ## pointItems - non-edit
        self.removePointItems()
        if self.sideWays.tagCount() > 0:
            self.pathMaker.redrawPathsAndTags()
        else:
            self.pathMaker.addPath()
        if bool: self.addPointItems()

    def updatePath(self):  ## pointItem responding to mouse events
        self.removePointItems()      
        self.pathMaker.addPath() 
        self.addPointItems()   
   
    def finalizeSelections(self, pt): 
        self.lasso.append(QPointF(pt))
        poly = self.drawPoly(self.lasso)  ## return a polygon
        for i in range(0, len(self.pathMaker.pts)):  
            p = QPointF(self.pathMaker.pts[i])
            if poly.containsPoint(p, Qt.FillRule.WindingFill):  ## match 
                if self.pathMaker.selections and i in self.pathMaker.selections:  ## unselect 
                    idx = self.pathMaker.selections.index(i)
                    # print('a ', i, idx, self.pathMaker.selections)
                    self.pathMaker.selections.pop(idx)
                else:
                    self.pathMaker.selections.append(i)  ## save pts index 
                    # print('b ', i, self.pathMaker.selections)
        self.deleteLasso()
        self.removePoly()
        if self.pathMaker.selections:
            self.pathMaker.selections.sort()
        QTimer.singleShot(200, self.updatePath)  ## it works better this way
                      
    def deleteSections(self):  ## selected with lasso
        if self.pathMaker.selections: 
            self.pathMaker.selections.sort()  ## works better this way
            sel = self.pathMaker.selections[::-1]  ## reverse list 
            for i in sel:
                self.pathMaker.pts.pop(i)  
            self.pathMaker.selections = []
            del sel
            self.redrawPoints()
       
    def insertSelection(self, idx):  ## used only by pointItems 
        if self.pathMaker.selections:       
            self.pathMaker.selections.sort()  
            if idx < self.pathMaker.selections[0]:  ## if first
                for i in range(0, len(self.pathMaker.selections)):  
                    self.pathMaker.selections[i] += 1 
            elif idx > self.pathMaker.selections[-1]:  ## if last
                return
            else:
                self.insertIntoSelection(idx)
            
    def insertIntoSelection(self, idx):      
        if idx in self.pathMaker.selections:      
            # print('j-insert: ', idx, self.pathMaker.selections)
            j = self.pathMaker.selections.index(idx) + 1  ## use the index        
            for k in range(j, len(self.pathMaker.selections)):
                self.pathMaker.selections[k] += 1         
        else:
            for i in range(0, len(self.pathMaker.selections)): 
                if idx > self.pathMaker.selections[i] and idx < self.pathMaker.selections[i+1]:
                    # print('k-insert: ', idx, self.pathMaker.selections[i])
                    for k in range(i+1, len(self.pathMaker.selections)):
                        self.pathMaker.selections[k] += 1  
                    self.pathMaker.selections[i] == idx  
                    break
        # print('n-insert', self.pathMaker.selections, '\n')
   
    def removeSelection(self, idx):  ## used only by pointItems          
        if self.pathMaker.selections:
            self.pathMaker.selections.sort() 
            # print('a-delete: ', idx, self.pathMaker.selections)  
            if idx <= self.pathMaker.selections[0]:  ## test for first
                if idx == self.pathMaker.selections[0]: 
                    self.pathMaker.selections.pop(0)  
                for i in range(0, len(self.pathMaker.selections)):
                    self.pathMaker.selections[i] += -1  
            elif idx >= self.pathMaker.selections[-1]:
                if idx == self.pathMaker.selections[-1]:
                    del self.pathMaker.selections[-1]
                else:
                    return
            else:  
                self.removeFromSelections(idx)
                                
    def removeFromSelections(self, idx):            
        if idx in self.pathMaker.selections:  ## remove and renumber
            # print('b-delete: ', idx, self.pathMaker.selections)  
            idx = self.pathMaker.selections.index(idx)  ## use the index        
            self.pathMaker.selections.pop(idx)  
            for i in range(idx, len(self.pathMaker.selections)):  ## only returns index
                self.pathMaker.selections[i] += -1  ## from this point on  
        else:             
            for i in range(0, len(self.pathMaker.selections)):  ## just renumber
                # print('c-delete: ', idx, self.pathMaker.selections[i])              
                if idx > self.pathMaker.selections[i] and idx < self.pathMaker.selections[i+1]:
                    for k in range(i+1, len(self.pathMaker.selections)):
                        # print('c-renum: ', k, idx, self.pathMaker.selections[k]) 
                        self.pathMaker.selections[k] += -1       
                    break
        # print('d-delete: ', self.pathMaker.selections, '\n')
                
    def findTop(self):
        ## save
        #  self.setZValue(self.parent.scene.items()[0].zValue() + 1)    
        for itm in self.scene.items():
            return itm.zValue()
        return 0
    
    def turnBlue(self):
        self.canvas.btnPathMaker.setStyleSheet(
        'background-color: rgb(118,214,255)')
       
### ------------------- dotsPathEdits ---------------------

