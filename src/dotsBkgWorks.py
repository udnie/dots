
from functools          import partial

from PyQt6.QtCore       import QPoint, QTimer, QParallelAnimationGroup, \
                                QPropertyAnimation, QPointF                               
from PyQt6.QtGui        import QColor, QPen
from PyQt6.QtWidgets    import QGraphicsEllipseItem, QColorDialog
                       
from dotsShared         import common, paths
from dotsBkgMatte       import Matte
from dotsAnimation      import Node


''' These have been replaced by the settings.json file in ./plays in an effort 
    to make it easier to make any changes. Select 'Update Scolling Backgrounds'
    from the Background help menu or enter 'U' and click on a background to open
    the BkgScrollWidget - be sure to click on 'Update' for the changes to take.
    
    ShowTime = 4  ## number of pixels remaining when to add the next background 
    RWY =   40    ## now RunWay - used if vertical - modifies runWay changing its starting position
    VT5 = 1.05    ## now OffSet - used if vertical - modifies 'first' Ten value to slow it 
    '''

Ten = 10.0    ## the 'first' scrolling background rate - it's always 10
LRF = 1.00    ## modifies 'left' 'right' 'first' Ten value if necessary - not used

### --------------------- dotsBkgWorks --------------------- 
''' setDirection, getScreenRate, some scrolling and menu functions '''
### --------------------------------------------------------
class BkgWorks:  
### --------------------------------------------------------
    def __init__(self, parent):  
        super().__init__()

        self.bkgItem  = parent     
        self.canvas   = self.bkgItem.canvas
        self.bkgMaker = self.bkgItem.bkgMaker
        
        self.point = None 
        self.target = None
        
### --------------------------------------------------------                                                                                
    def setDirection(self, key):   
        if key == "" or not self.bkgItem.isScrollable():
            return  
        
        self.bkgItem.direction = 'vertical' if self.canvas.dots.Vertical else key
        self.bkgItem.rate = 0    
           
        self.bkgItem.path = paths['demo'] if self.canvas.openPlayFile != '' and \
            self.canvas.openPlayFile == 'snakes'\
                else paths['bkgPath']
                     
        fileName = self.bkgItem.fileName             
        if self.bkgMaker.newTracker[fileName]:   
            self.bkgItem.rate = self.getScreenRate(self.bkgItem)  ## blank it's first  
            self.bkgMaker.newTracker[fileName]['rate'] = self.bkgItem.rate
            self.bkgMaker.newTracker[fileName]['path'] = self.bkgItem.path 
            
        if self.bkgItem.rate == 0:
            return

        self.bkgItem.tag = 'scroller'   ## trigger needed to run scrolling bkg set here
        self.bkgMaker.lockBkg(self.bkgItem)  ## locks the background to begin 
        
        if self.bkgMaker.widget:
            self.bkgMaker.updateWidget(self.bkgItem)      
            QTimer.singleShot(100, partial(self.bkgItem.bkgMaker.resetSliders, self.bkgItem))
                                                  
### --------------------------------------------------------  
    ''' reads twice - returns 'first' and 'next' rates and only 
        once per scrolling background  '''
### --------------------------------------------------------  
    def getScreenRate(self, bkg, which =''): 
        if which == 'first':
            rate = Ten
            settings = bkg.bkgScrollWrks.getSettings()
            
            if bkg.direction == 'vertical': 
                rate = Ten * settings['OffSet']/100
            else:
                rate = Ten  ## * LRF  ## not implemented 
         
        elif bkg.rate == 0:  ## sets rate for 'next' used by tracker
            
            if bkg.direction in ('left', 'right'):
                calculated_rate = Ten * (1.0 + (common['ViewW'] / bkg.width))  
                      
            elif bkg.direction == 'vertical':
                calculated_rate = Ten * (1.0 + (bkg.height / common['ViewH'])) 
                     
            rate = round(calculated_rate, 2)           
            bkg.rate = rate      
            bkg.bkgScrollWrks.setTrackerRate(bkg)   
                  
        return rate
    
## --------------------------------------------------------        
    def setFirstPath(self, path, bkg):  ## 'first' is already filling the scene  
        fact = bkg.factor      
        bkg.node = Node(bkg)
        path = QPropertyAnimation(bkg.node, b'pos')  ## not the ../paths/
        settings = bkg.bkgScrollWrks.getSettings()
  
        if bkg.direction == 'left':
            path.setDuration(int(common['ViewW'] * (bkg.rate*fact)))  
            path.setStartValue(QPoint(0,0)) 
            path.setEndValue(QPoint(-int(bkg.width), 0))
            
        elif bkg.direction == 'right':
            path.setDuration(int(common['ViewW'] * (bkg.rate*fact)))
            path.setStartValue(QPoint(bkg.runWay, 0))
            path.setEndValue(QPoint(int(common['ViewW']), 0))
              
        elif bkg.direction == 'vertical':  ## it appears the 'First' qt scrolling vertical needs a boost to start and must slow afterwards
            path.setDuration(int(common['ViewH'] * (bkg.rate*fact)))   
            path.setStartValue(QPoint(0, bkg.runWay + settings['RunWay']))  ## RunWay shortens the number of pixels to ShowTime as
            path.setEndValue(QPoint(0, -bkg.height))                        ## bkg.runWay is a negative value
       
        group = QParallelAnimationGroup()
        group.addAnimation(path)
    
        return group

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
            path.setStartValue(QPoint(0, common['ViewH']))
            path.setEndValue(QPoint(0, -bkg.height))
            
        group = QParallelAnimationGroup()
        group.addAnimation(path)
        
        return group
     
### --------------------------------------------------------   
    def setStartingPos(self, bkg):
        if bkg.direction == 'right':  ## gets it pointed in the right direction -->>
            bkg.setPos(QPointF(bkg.runWay, 0)) 
            
        elif bkg.direction == 'left': 
            bkg.setPos(QPointF())
            
        else:
            settings = bkg.bkgScrollWrks.getSettings()
            bkg.setPos(QPointF(0.0, float(bkg.runWay + settings['RunWay'])))
                     
    def setBtns(self, bkg, widget):  ## from bkgMaker widget
        match bkg.direction:  
            case 'right': 
                widget.rightBtn.setStyleSheet(
                    'background-color: LIGHTGREY')
                widget.leftBtn.setStyleSheet(
                    'background-color: None') 
            case 'left': 
                widget.leftBtn.setStyleSheet(
                    'background-color: LIGHTGREY')
                widget.rightBtn.setStyleSheet(
                    'background-color: None')
            case 'vertical':
                widget.leftBtn.setText('Vertical')   
                widget.leftBtn.setStyleSheet(
                    'background-color: LIGHTGREY')
                                                            
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
        if self.bkgItem and self.bkgItem.type == 'bkg':  
            width = self.bkgItem.imgFile.width()
            height = self.bkgItem.imgFile.height()
            self.bkgItem.x = (common['ViewW']- width)/2
            self.bkgItem.y = (common['ViewH']- height)/2
            self.bkgItem.setPos(self.bkgItem.x, self.bkgItem.y) 
                                        
    def openMatte(self, bkg):  ## runs from bkgWidget
        self.closeWidget()  ## closes matteWidget as well
        self.bkgItem.matteWidget = Matte(bkg)
        
    def closeWidget(self):
        self.bkgMaker.closeWidget()  ## no matte
        self.bkgItem.closeMatteWidget()    
                                                                                                                                                                                                  
### --------------------- dotsBkgWorks ---------------------


        
        