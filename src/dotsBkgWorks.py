
import math
import json

from functools          import partial

from PyQt6.QtCore       import QPoint, QTimer, QParallelAnimationGroup, QPropertyAnimation, \
                                QPointF
from PyQt6.QtGui        import QColor, QPen
from PyQt6.QtWidgets    import QGraphicsEllipseItem, QColorDialog
                       
from dotsShared         import common, paths
from dotsSideGig        import MsgBox
from dotsBkgMatte       import Matte
from dotsBkgScrollWrks  import BkgScrollWrks

from dotsAnimation      import Node

### --------------------- dotsBkgWorks --------------------- 
''' classes: BkgWorks -- mostly scrolling'''    
# ### -------------------------------------------------------- 
class BkgWorks:  
### --------------------------------------------------------
    def __init__(self, parent):  
        super().__init__()

        self.bkgItem  = parent     
        self.canvas   = self.bkgItem.canvas
        self.bkgMaker = self.bkgItem.bkgMaker
        
        self.point = None 
        self.target = None
        
        self.bkgScrollWrks = BkgScrollWrks(self.bkgItem)
     
### --------------------------------------------------------                                                                                
    def setDirection(self, key):  ## from keybooard or widget - sets 'first'    
        if math.fabs(self.bkgItem.runway) < self.bkgItem.showtime:
            self.bkgScrollWrks.notScrollable()   
            return     
        if self.bkgItem.scrollable:  ## only place where scroller is set except demos 
            
            if self.canvas.dots.Vertical:   ## no direction equals 'not scrollable'
                self.bkgItem.direction = 'vertical'
            else:
                self.bkgItem.direction = key
                
            self.bkgItem.tag = 'scroller'    
            self.bkgItem.rate = 0     
                
            if self.canvas.openPlayFile != '' and self.canvas.openPlayFile == 'snakes':    
                self.bkgItem.path = paths['demo']
            else:
                self.bkgItem.path = paths['bkgPath']
                      
            fileName = self.bkgItem.fileName               
            if self.bkgMaker.newTracker[fileName]: 
                self.bkgItem.showtime = self.bkgScrollWrks.setShowTime()
                self.bkgItem.rate = self.getScreenRate(self.bkgItem)  ## blank it's first  
                self.bkgMaker.newTracker[fileName]['showtime'] = self.bkgItem.showtime
                self.bkgMaker.newTracker[fileName]['rate'] = self.bkgItem.rate
                self.bkgMaker.newTracker[fileName]['path'] = self.bkgItem.path 
         
            if self.bkgItem.rate == 0 and self.bkgItem.useThis == '':
                return
            
            self.bkgMaker.lockBkg(self.bkgItem)  ## locks the background to begin 
     
            if self.bkgMaker.widget != None:
                self.bkgMaker.updateWidget(self.bkgItem)      
                QTimer.singleShot(100, partial(self.bkgItem.bkgMaker.resetSliders, self.bkgItem))
                                                  
### --------------------------------------------------------  
    ''' reads twice - returns 'next' rate first, returns 'first' rate next, 
        but only once per scrolling background - rates can vary in a scene '''
### --------------------------------------------------------  
    def getScreenRate(self, bkg, which =''): 
        rate = self.getThisRate(bkg) 
         
        if rate == 0:
            MsgBox(f'Error Loading Screen Rates File {bkg.useThis}', 5)
            bkg.useThis = ''
            self.bkgMaker.screenrate.clear()
            return 0  

        if which == 'first':
            rate = rate[0]   ## same for 'first'   
                
        elif bkg.rate == 0:  ## sets tracker rate for 'next'
            
            if bkg.useThis == '':  ## shouldn't happen - wasn't getting carried over
                rate = self.getThisRate(bkg)  
                 
            if bkg.direction == 'right':
                rate = rate[2]
            else:
                rate = rate[1]     
                
            erat = self.bkgScrollWrks.getTrackerRate(bkg)
            if erat > 0: rate = erat  ## fixes not carrying over rate from a file
     
            bkg.rate = rate 
            self.bkgScrollWrks.setTrackerRate(bkg)          
        return rate
    
### --------------------------------------------------------
    ## rates can vary within a scene by background width
    def getThisRate(self, bkg): 
        bkg.useThis == ''  ## set which dictionary to use  
        if common['Screen']  == '1080' and bkg.width  < 1280 or \
            common['Screen'] == '1215' and bkg.width  < 1440 or \
            common['Screen'] == '1296' and bkg.width  < 1536 or \
            common['Screen'] ==  '900' and bkg.height < 1102: 
            bkg.useThis = 'moretimes'  ## in this case 2:3 
        else:
            bkg.useThis = 'screentimes'  ## 16:9 or larger         
        try:  
            if len(self.bkgMaker.screenrate) == 0:  ## fewer reads
                with open(paths['playPath'] +  "screenrates.dict", 'r') as fp:
                    self.bkgMaker.screenrate = json.load(fp)  
            return self.bkgMaker.screenrate[bkg.useThis][common['Screen']]        
        except:
            return 0
        
### --------------------------------------------------------
    ## rate times screen long side = milliseconds needed to clear the scene end to end
    def setNextPath(self, bkg):  
        fact = bkg.factor      
        
        bkg.node = Node(bkg)
        path = QPropertyAnimation(bkg.node, b'pos')
        
        if bkg.direction == 'left':   
            path.setDuration(int(common['ViewW'] * (bkg.rate*fact)))    
            path.setStartValue(QPoint(common['ViewW'], 0))
            path.setEndValue(QPoint(int(-bkg.width), 0))
            
        elif bkg.direction == 'right':
            path.setDuration(int(common['ViewW'] * (bkg.rate*fact)))  
            path.setStartValue(QPoint(-bkg.width, 0))
            path.setEndValue(QPoint(int(common['ViewW']), 0))
            
        elif bkg.direction == 'vertical':
            path.setDuration(int(common['ViewH'] * (bkg.rate*fact))) 
            ## current kludge advances background into scene before starting - verticals seem to take longer to start
            path.setStartValue(QPoint(0, common['ViewH']-int(bkg.showtime*.75)))
            path.setEndValue(QPoint(0, -bkg.height))
                  
        group = QParallelAnimationGroup()
        group.addAnimation(path)

        return group
          
    def setFirstPath(self, path, bkg):  ## 'first' is already filling the scene  
        fact = bkg.factor  
        
        bkg.node = Node(bkg)
        path = QPropertyAnimation(bkg.node, b'pos')
        
        if bkg.direction == 'left':
            path.setDuration(int(common['ViewW'] * (bkg.rate*fact))) 
            path.setStartValue(QPoint(0,0)) 
            path.setEndValue(QPoint(-int(bkg.width), 0))
            
        elif bkg.direction == 'right':
            path.setDuration(int(common['ViewW'] * (bkg.rate*fact)))
            path.setStartValue(QPoint(bkg.runway, 0))
            path.setEndValue(QPoint(int(common['ViewW']), 0))
            
        elif bkg.direction == 'vertical':   
            path.setDuration(int(common['ViewH'] * (bkg.rate*fact)))  ## rate time equals time to clear   
            path.setStartValue(QPoint(0, bkg.runway))
            path.setEndValue(QPoint(0, -bkg.height)) 
            
        group = QParallelAnimationGroup()
        group.addAnimation(path)

        return group
    
    def setStartingPos(self, bkg):
        if bkg.direction == 'right':  ## gets it pointed in the right direction -->>
            bkg.setPos(QPointF(bkg.runway, 0)) 
        elif bkg.direction == 'left':  ## <<--
            bkg.setPos(QPointF())
        else:
            bkg.setPos(QPointF(0.0, float(bkg.runway)))
                     
### -------------------------------------------------------- 
    def spotColor(self, p):
        x, y = int(p.x()), int(p.y())                   
             
        self.target = QGraphicsEllipseItem()
        self.target.setPen(QPen(QColor('white'), 2))
   
        self.target.setRect(x-25, y-25, 50, 50) 
        self.bkgItem.scene.addItem(self.target) 
        
        dialog = QColorDialog()  
        color = dialog.getColor() 
         
        if color.isValid():
            self.point = QGraphicsEllipseItem()
            self.point.setPen(QPen(QColor('white'), 1))
            self.point.setBrush(QColor(color)) 
            self.point.setRect(x-15, y-15, 30, 30) 
            self.point.setZValue(300)
            self.bkgItem.scene.addItem(self.point)   
            QTimer.singleShot(4000, partial(self.bkgItem.scene.removeItem, self.point))
             
        self.bkgItem.scene.removeItem(self.target)
        dialog.close()
  
    def centerBkg(self):
        if self.bkgItem != None and self.bkgItem.type == 'bkg':  
            width = self.bkgItem.imgFile.width()
            height = self.bkgItem.imgFile.height()
            self.bkgItem.x = (common['ViewW']- width)/2
            self.bkgItem.y = (common['ViewH']- height)/2
            self.bkgItem.setPos(self.bkgItem.x, self.bkgItem.y) 

    def setMirroring(self):
        if self.bkgItem.scrollable:                                  
            if self.bkgItem.mirroring == True: 
                self.bkgItem.mirroring = False ## continuous
            else:
                self.bkgItem.mirroring = True  ## mirrored                                    
        fileName = self.bkgItem.fileName         
             
        if self.bkgMaker.newTracker[fileName]:  
            self.bkgMaker.newTracker[fileName]['mirroring'] = self.bkgItem.mirroring                            
            self.canvas.sideCar2.setMirrorBtnText(self.bkgItem, self.bkgMaker.widget) 
         
    def openMatte(self):  ## runs from bkgWidget - starts here
        self.bkgItem.widget = False
        self.bkgMaker.closeWidget()
        if self.bkgItem.matte != None:
            self.bkgItem.matte.close()
        self.bkgItem.matte = Matte(self.bkgItem)
                                                                                                                                                 
### --------------------- dotsBkgWorks ---------------------


        
        