
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

SharedKeys = ('B','E','F','H','T','del','tag','shift','enter','return', 'down', 'up') 

### ---------------------- dotsBkgItem ---------------------                   
''' Background Class - there can be more than one background in a scene '''
### --------------------------------------------------------
''' The screentimes and moretimes dictionaries have been moved to screenrates.dict
    in the play directory. See 'Rates and Background Widget Controls' in Start Here
    for details. '''
### --------------------------------------------------------
class BkgItem(QGraphicsPixmapItem):  ## background
### --------------------------------------------------------
    def __init__(self, fileName, parent, z=common['bkgZ'], copy=None):
        super().__init__()

        self.canvas   = parent
        self.dots     = self.canvas.dots
        self.scene    = self.canvas.scene
        self.bkgMaker = self.canvas.bkgMaker

        self.bkgWorks       = BkgWorks(self)  
        self.bkgScrollWrks  = BkgScrollWrks(self)
        
        self.widgetOn = False  
       
        self.ViewW = common['ViewW']
        self.ViewH = common['ViewH']

        self.type = 'bkg'
        self.path = paths['bkgPath'] 
        
        self.matte = None  
        
        self.fileName = os.path.basename(fileName) 
        self.sharedKeys = SharedKeys  ## shared with bkgMenu
        
        if self.canvas.openPlayFile != '':
            if self.canvas.openPlayFile == 'snakes':      
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
        self.scrollable = False
        
        if copy == None:          
            try:   ## sets if scrollable and self.imgfile if not already set
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
        self.addedScroller = False
           
        self.direction = ''  ## direction of travel: left <<--, right -->>
        self.mirroring = self.bkgMaker.mirroring ## sets default - false equals continuous
        self.factor    = self.bkgMaker.factor    ## sets default 
        self.showtime  = 0  ## the number of pixels to showtime before the runway goes to zero
        self.useThis   = ''
        self.rate      = 0
        self.runway    = 0  ## what's not visible     
        self.bkgScrollWrks.setRunWay()  
                                   
        self.ratio = self.height/9
        self.ratio = int(self.width/self.ratio)
                    
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
         
        if  self.width > self.height:
            rot = self.width/self.height
        else:
            rot = self.height/self.width
            
        fn = f'{play}   {self.fileName}   {self.width}   {self.height}   {rot:.2f}'
        self.canvas.dots.statusBar.showMessage(fn, 12000) 
             
### --------------------------------------------------------
    @pyqtSlot(str)
    def setPixKeys(self, key):  
        self.key = key 

    def mousePressEvent(self, e): 
        if not self.canvas.pathMakerOn:       
            if e.button() == Qt.MouseButton.RightButton:   
                self.bkgMaker.addWidget(self)   
                if self.direction == '' or self.useThis == '':   
                    self.bkgMaker.bkgtrackers.resetTracker(self)
                    self.bkgMaker.resetSliders(self)  
            else: 
                if self.key in self.sharedKeys:
                    self.shared(self.key)           
            self.initX, self.initY = self.x, self.y  
            self.dragCnt = self.mapToScene(e.pos())                                
        e.accept()   
        
    def mouseReleaseEvent(self, e):
        key = ''
        e.accept()   
   
    def shared(self, key):  ## from helpMenu and keyboard
        if not self.canvas.pathMakerOn: 
            self.key = key
            if self.key == 'del':    
                self.bkgMaker.deleteBkg(self)          
            elif self.key == 'shift':  ## to the back
                if self.bkgMaker.toBack() == -100:
                    MsgBox("There's is only One", 5)
                else:
                    self.setZValue(self.bkgMaker.toBack()) 
                    self.bkgMaker.renumZvals()  
            elif self.key in ('enter','return'):  ## to front     
                self.bkgMaker.front(self)    
            elif self.key == 'tag': ## '\' <- tagKey
                self.tagThis()
            elif self.key == 'B': 
                self.bkgMaker.bkgtrackers.trackThis()
            elif self.key == 'E':   
                self.bkgWorks.spotColor(self.canvas.mapFromGlobal(QCursor.pos()))   
            elif self.key == 'F':  ## flip it
                self.setMirrored(False) if self.flopped else self.setMirrored(True)  
            elif self.key == 'H':  
                self.openMenu()
            elif self.key == 'T':     
                self.bkgMaker.lockBkg(self) if self.locked == False \
                    else self.bkgMaker.unlockBkg(self)
                self.tagThis()
        
    def tagThis(self):
        p = QCursor.pos()
        tagBkg(self, self.canvas.mapFromGlobal(QPoint(p.x(), p.y()-20))) 
          
    def openMenu(self):
        self.bkgMaker.closeWidget()    
        self.help = BkgHelp(self) 
        
### -------------------------------------------------------- 
    ''' 'first' has already set its setScrollerPath - ## value equals self.pos() '''
### -------------------------------------------------------- 
    def itemChange(self, change, value):   
        if change == QGraphicsPixmapItem.GraphicsItemChange.ItemScenePositionHasChanged: 
            if self.direction == '':
                return            
                     
            elif self.addedScroller == False:  ## check if its showtime    
                
                if self.direction  == 'left'  and int(value.x()-self.runway) <= self.showtime or\
                    self.direction == 'right' and int(value.x()) >= -self.showtime or\
                    self.direction == 'vertical' and int(value.y())-self.runway <= self.showtime:  
                    self.addNextScroller()  ## the scroller factory
                    self.addedScroller = True        
                                                       
            elif self.addedScroller == True:  ## test if nolonger in view
                
                if self.direction   == 'left'  and abs((value.x())) >= self.width or \
                    self.direction  == 'right' and abs(int(value.x())) >= common['ViewW'] or \
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
                                         
        if self.mirroring == True:
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
            
        node = Node(bkg)  ## bkg property used in animation                      
        if node == None:          ## being ignored - just for pyside
            MsgBox('setScrollerPath: Error Setting Path ...')
            return          
                
        elif bkg.direction in ('left', 'right') and bkg.width < common['ViewW'] or\
            bkg.direction == 'vertical' and bkg.height < common['ViewH']:
            self.bkgScrollWrks.notScrollable()  
            return 
   
        self.bkgWorks.setStartingPos(bkg)  ## not the scrolling position      
        bkg.rate = bkg.bkgWorks.getScreenRate(bkg, which)  ## also sets tracker rate for 'next' 
        return self.bkgWorks.setFirstPath(node, bkg)  ## sets the paths duration
                       
    def setMirrored(self, bool, switch=1):
        self.flopped = bool  
        if not self.dots.Vertical:
            if self.flopped:
                transform = QTransform().scale(-1, switch)
            else:
                transform = QTransform().scale(1, switch)
            pix = QPixmap.fromImage(self.imgFile)
            self.setPixmap(pix.transformed(transform))
            self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
                                                                                                                                                                      
### ---------------------- dotsBkgItem ---------------------



