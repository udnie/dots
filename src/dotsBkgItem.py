
import os
import os.path

from PyQt6.QtCore       import Qt, QPointF, QPoint, pyqtSlot
from PyQt6.QtGui        import QImage, QPixmap, QCursor, QTransform
from PyQt6.QtWidgets    import QGraphicsPixmapItem

from dotsShared         import common, paths
from dotsSideGig        import MsgBox, tagBkg
from dotsBkgWorks       import BkgWorks
from dotsBkgScrollWrks  import BkgScrollWrks
from dotsHelpMonkey     import BkgHelp
from dotsAnimation      import Node

BkgSharedKeys = ('B','E','F','H','M','T','del','tag','shift','enter','return', 'down', 'up') 

### ---------------------- dotsBkgItem ---------------------                   
''' Background Class - there can be more than one background in a scene '''
### --------------------------------------------------------
''' The screenrates are in the screenrates.dict in the play directory
    and demorates are in the demo directory as demorates.dict.
    See 'Rates and Background Widget Controls' in Start Here
    for details and BkgScrollWrks for examples. '''
### --------------------------------------------------------
class BkgItem(QGraphicsPixmapItem):  ## background
### --------------------------------------------------------
    def __init__(self, fileName, parent, z=common['bkgZ'], copy=None):
        super().__init__()

        self.canvas = parent
        self.dots   = self.canvas.dots
        self.scene  = self.canvas.scene
        
        self.bkgMaker = self.canvas.bkgMaker
        self.bkgWorks = BkgWorks(self)  
        self.bkgScrollWrks = BkgScrollWrks(self)
        
        self.ViewW = common['ViewW']
        self.ViewH = common['ViewH']

        self.type = 'bkg'
        self.path = paths['bkgPath']  ## default

        self.fileName = os.path.basename(fileName) 
        self.sharedKeys = BkgSharedKeys  ## shared with bkgMenu
        
        if self.canvas.openPlayFile in ('snakes', 'hats'):    
            self.path = paths['demo']
        elif self.dots.Vertical and self.canvas.openPlayFile == 'bats':
            self.path = paths['demo']
           
        if not os.path.exists(self.path + self.fileName):
            self.type = None        
            MsgBox(f'BkgItem Error: {self.fileName} Not Found', 5)
            return

        self.setZValue(z)      
        self.init(copy)  ## reuse QImage for 'next' backgrounds - self.imgFile
                   
### --------------------------------------------------------   
    def init(self, copy):    
        self.imgFile = None      
   
        if copy == None:          
            try:   ## sets the self.imgfile if not already set in copy
                if not self.dots.Vertical: 
                    self.bkgScrollWrks.setWidthHeight(QImage(self.path + self.fileName)) 
                else:
                    self.bkgScrollWrks.setVertical(QImage(self.path + self.fileName))
            except Exception:
                MsgBox('BkgItem Error on loading: ' + self.fileName)
                return
            self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        else:
            self.imgFile = copy
                    
        self.setPixmap(QPixmap.fromImage(self.imgFile)) 
                                                       
        self.flopped = False
        self.locked = False
         
        self.width  = self.imgFile.width()
        self.height = self.imgFile.height() 
            
        self.setMirrored(False)
                                                 
        self.x, self.y = 0.0, 0.0
        
        self.tag = ''  
        self.anime = None 
        self.addedScroller = False  ## used by itemChange 
        
        self.helpMenu = None
        self.matteWidget = None
        
        self.direction = ''  ## direction of travel: left <<--, right -->>
        self.mirroring = self.bkgMaker.mirroring ## sets default - false equals continuous
        self.factor    = self.bkgMaker.factor    ## sets default 
        self.showtime  = 0  ## the number of pixels to showtime before the runway goes to zero
        self.rate      = 0
        self.runway    = 0  ## what's not visible     
        self.bkgScrollWrks.setRunWay()  
                                   
        self.ratio = self.height/9
        self.ratio = int(self.width/self.ratio)
          
        self.scrollable = self.isScrollable()  ## once width and height set
                    
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, False)                                 
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)  ## locked
          
        self.key = ''    
        self.dragCnt = 0
        self.save = QPointF()  
 
        play, rot = '', 0
    
        if self.canvas.openPlayFile != '' and self.canvas.openPlayFile == 'snakes':   
            self.path = paths['demo']
        else:
            self.path = paths['bkgPath']  
            play = os.path.basename(self.canvas.openPlayFile)
         
        rot = self.width/self.height if self.width > self.height \
            else self.height/self.width
            
        fn = f'{play}   {self.fileName}   {self.width}   {self.height}   {rot:.2f}'
        self.canvas.dots.statusBar.showMessage(fn, 5000) 
             
### --------------------------------------------------------
    @pyqtSlot(str)
    def setPixKeys(self, key):  
        self.key = key 

    def mousePressEvent(self, e): 
        if not self.canvas.pathMakerOn:       
            if e.button() == Qt.MouseButton.RightButton: 
                
                if self.matteWidget != None:
                    self.matteWidget.shared('H')
                    return
             
                if self.helpMenu != None:
                    self.closeMenu()
                    
                self.bkgMaker.addWidget(self)   
                
                if self.direction == '':
                    self.bkgMaker.bkgtrackers.resetTracker(self)
                    self.bkgMaker.resetSliders(self)  
                    
            elif self.key in self.sharedKeys:
                self.shared(self.key) 
                
            self.initX, self.initY = self.x, self.y  
            self.dragCnt = self.mapToScene(e.pos())                               
        e.accept()   
        
    def mouseReleaseEvent(self, e):
        self.key = ''
        e.accept()   
                
    def shared(self, key):  ## from helpMenu and keyboard
        if not self.canvas.pathMakerOn: 
            match key: 
                case 'del':    
                    self.bkgMaker.deleteBkg(self)          
                case 'shift':           ## to the back
                    if self.bkgMaker.toBack() == -100:
                        MsgBox("There's is only One", 5)
                    else:
                        self.setZValue(self.bkgMaker.toBack()) 
                        self.bkgMaker.renumZvals()  
                case  'enter' | 'return':   ## to front     
                    self.bkgMaker.front(self)           
                case  'tag':     
                    self.tagThis()    
                case  'B': 
                    self.bkgMaker.bkgtrackers.trackThis()
                case  'E':   
                    self.bkgWorks.spotColor(self.canvas.mapFromGlobal(QCursor.pos()))   
                case  'F':          ## flip it
                    self.setMirrored(False) if self.flopped else self.setMirrored(True)  
                case  'H':  
                    self.openMenu()                           
                case 'M':
                    self.bkgWorks.openMatte(self)      
                case  'T':     
                    self.bkgMaker.lockBkg(self) if not self.locked else \
                        self.bkgMaker.unlockBkg(self)
                    self.tagThis()
                 
    def tagThis(self):
        p = QCursor.pos()
        tagBkg(self, self.canvas.mapFromGlobal(QPoint(p.x(), p.y()-20))) 
          
    def openMenu(self):
        self.bkgMaker.closeWidget()    
        self.helpMenu = BkgHelp(self) 
        
    def closeMenu(self):
        if self.helpMenu != None:
            self.helpMenu.closeMenu()
            self.helpMenu = None
    
    def closeMatteWidget(self):
        if self.matteWidget != None:   
            if self.matteWidget.skynet != None:
                self.matteWidget.skynet.close()        
                self.matteWidget.skynet = None
            self.matteWidget.close() 
            self.matteWidget = None
            self.bkgMaker.view.grabKeyboard()
        
### -------------------------------------------------------- 
    ''' first' has already set its setScrollerPath - ## value equals self.pos() 
        itemChange drives the scrolling background '''
### -------------------------------------------------------- 
    def itemChange(self, change, value):   
        if change == QGraphicsPixmapItem.GraphicsItemChange.ItemScenePositionHasChanged: 
            if self.direction == '':
                return            
                     
            elif not self.addedScroller:  ## check on the distance to showtime
                
                if self.direction  == 'left'     and int(value.x()-self.runway) <= self.showtime or\
                    self.direction == 'right'    and int(value.x()) >= -self.showtime or\
                    self.direction == 'vertical' and int(value.y())-self.runway <= self.showtime:  
                    self.addNextScroller()  ## the scroller factory
                    self.addedScroller = True        
                                                       
            elif self.addedScroller:  ## test if nolonger in view
                
                if self.direction   == 'left'     and abs((value.x())) >= self.width or \
                    self.direction  == 'right'    and abs(int(value.x())) >= common['ViewW'] or \
                    self.direction  == 'vertical' and int(value.y()) >= self.height:
                    self.anime.stop()
                    self.bkgMaker.deleteBkg(self, 'nope')  ## don't delete tracker
                                                    
        return super(QGraphicsPixmapItem, self).itemChange(change, value)
 
### -------------------------------------------------------- 
    ''' add the 'next' scrolling background - passing on the imgFile means 
        no longer needing to re-read the .jpg/.png file  '''       
### -------------------------------------------------------- 
    def addNextScroller(self): 
        item = BkgItem(self.fileName, self.canvas, common['bkgZ'], self.imgFile) 
                                         
        if self.mirroring:
            item.setMirrored(False) if self.flopped else item.setMirrored(True)   
                               
        item.tag = 'scroller'
        item.setZValue(self.zValue())  
                                    
        self.bkgMaker.bkgtrackers.restoreFromTrackers(item)  
    
        item.node = Node(item)  ## sets property used in animation        
        item.anime = self.bkgWorks.setNextPath(item) 

        item.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)        
        self.scene.addItem(item)   
        
        item.anime.start()
                           
### --------------------------------------------------------   
    ''' used by 'first' to set its path and rates - rates set for 'next' as well '''
### --------------------------------------------------------   
    def setScrollerPath(self, bkg, which): ## which = first
        if bkg.direction == '':   
            return  
        
        elif not bkg.isScrollable():
            bkg.bkgScrollWrks.clearBkgScrolling()
            return None

        node = Node(bkg)  ## bkg property used in animation                      
        if node == None:  ## being ignored - just for pyside
            MsgBox('setScrollerPath: Error Setting Path ...')
            return  

        bkg.bkgWorks.setStartingPos(bkg)  ## not the scrolling position   
        bkg.rate = bkg.bkgWorks.getScreenRate(bkg, which)  ## also sets tracker rate for 'next' 
    
        return bkg.bkgWorks.setFirstPath(node, bkg)  ## sets the paths duration
     
    def isScrollable(self):  ## once screen height and width are set 
        if self.canvas.dots.Vertical and self.height > (common['ViewH'] + 10) or \
            self.width > (common['ViewW'] + 10):
            return True
        return False
    
    def notScrollable(self):
        MsgBox('Not Scrollable and Unable to Fulfill your Request...', 6) 
        self.bkgScrollWrks.clearBkgScrolling()
                  
    def setMirrored(self, bool, switch=1):  ## mirrors this background not text
        self.flopped = bool  
        
        if not self.dots.Vertical:
            if switch < 2:
                if self.flopped:
                    transform = QTransform().scale(-1, switch)
                else:
                    transform = QTransform().scale(1, switch)
            else:
                transform = QTransform().scale(1, 1)
            
            pix = QPixmap.fromImage(self.imgFile)
            self.setPixmap(pix.transformed(transform))
            self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)                                                                                                                                                                

### ---------------------- dotsBkgItem ---------------------



