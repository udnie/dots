
import os
import os.path

from PyQt6.QtCore       import Qt, QPointF, QPropertyAnimation, pyqtSlot
from PyQt6.QtGui        import QImage, QPixmap, QCursor
from PyQt6.QtWidgets    import QGraphicsPixmapItem

from dotsShared         import common, paths
from dotsSideGig        import MsgBox
from dotsBkgWorks       import BkgWorks
from dotsBkgScrollWrks  import BkgScrollWrks, tagBkg

import dotsAnimation    as Anime

### ---------------------- dotsBkgItem ---------------------                   
''' Background Class - there can be more than one background in a scene '''
### --------------------------------------------------------
''' screentimes and moretimes are now screenrates.dict in the play directory
            also direction refers to the direction of travel
# screentimes = {  ## based on a 1280X640 .jpg under .5MB for 16:9 background
#         ##   first, next-rt<lft, next-lft>right --- there are always two backgrounds once started
#     '1080':  [10.0,  17.50,  17.45],     ## 1440px actual size when scaled 1280X640 for 16:9
#     '1280':  [10.0,  18.75,  18.85],  
#     '1215':  [10.0,  17.35,  17.4],     ## 1620px actual size when scaled 1280X640 for 16:9
#     '1440':  [10.0,  18.7,   18.85],
#     '1296':  [10.0,  17.50,  17.45],     ## 1728px actual size when scaled 1280X640 for 16:9
#     '1536':  [10.0,  18.65,  18.60],  
#     '1102':  [10.0,  20.9,    0.0],
#     '900':   [10.0,  23.2,    0.0],
#     '912':   [10.0,  20.9,   0.0],
# }
# moretimes = {   ## based on a 1080X640 .jpg under .5MB for 3:2 background
#     '1080':  [10.0,   19.05, 19.05],   ## 1215px actual size when scaled 1080X640 for 3:2
#     '1215':  [10.0,   18.88, 18.89],   ## 1367px actual size when scaled 1080X640 for 3:2
#     '1296':  [10.0,   18.88, 18.87],   ## 1458px actual size when scaled 1080X640 for 3:2
#     '900':   [10.0,   21.4,   0.0]     ## 1013px actual size when scaled 640X1080 for 2:3
# } '''
    
### --------------------------------------------------------
class BkgItem(QGraphicsPixmapItem):  ## background
### --------------------------------------------------------
    def __init__(self, fileName, canvas, z=common['bkgZ'], mirror=False, copy=None):
        super().__init__()

        self.canvas   = canvas
        self.dots     = self.canvas.dots
        self.scene    = self.canvas.scene
        self.bkgMaker = self.canvas.bkgMaker
        
        self.bkgWorks = BkgWorks(self)
        self.bkgScrollWrks = BkgScrollWrks(self)
    
        self.ViewW = common['ViewW']
        self.ViewH = common['ViewH']

        self.type = 'bkg'
        self.path = paths['bkgPath']    
        self.fileName = os.path.basename(fileName)  ## new
        
        if self.canvas.openPlayFile != '':
            if self.canvas.openPlayFile == 'snakes':      
                self.path = paths['demo']
            elif self.dots.Vertical and self.canvas.openPlayFile == 'bats':
                self.path = paths['demo']
                
        if not os.path.exists(self.path + self.fileName):
            self.type = None        
            MsgBox(f'BkgItem Error: {self.fileName} Not Found', 5)
            self.type = None
            return

        self.setZValue(z)      
        self.init(copy)
                  
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
                           
    def mousePressEvent(self, e):  ## combination
        if not self.canvas.pathMakerOn:       
            if e.button() == Qt.MouseButton.RightButton:   
                self.bkgMaker.addWidget(self)   
                if self.direction == '' or self.useThis == '':   
                    self.bkgWorks.reset(self)
                    self.bkgMaker.resetSliders(self)              
            elif self.canvas.key == 'del':    
                self.bkgMaker.deleteBkg(self)          
            elif self.canvas.key == '/':  ## to back
                self.bkgMaker.back(self)     
            elif self.canvas.key == 'shift':  ## flop it
                self.setMirrored(False) if self.flopped else self.setMirrored(True)       
            elif self.canvas.key in ('enter','return'):  ## to front  
                self.bkgMaker.front(self)             
            elif self.key == ',':  ## may only work on background with transparent spaces
                self.bkgMaker.backOne(self)  
            elif self.key == '.': 
                self.bkgMaker.upOne(self)  
            elif self.key in('opt', 'tag'):  ## show background tag
                tagBkg(self, e.scenePos())
            elif self.key == ']':   
                self.bkgWorks.spotColor(self.canvas.mapFromGlobal(QPointF(QCursor.pos())))    
            self.initX, self.initY = self.x, self.y  
            self.dragCnt = self.mapToScene(e.pos())
            self.key = ''
        e.accept()     
    
### -------------------------------------------------------- 
    ''' 'first' has already set its setScrollerPath - ## value equals self.pos() '''
### -------------------------------------------------------- 
    def itemChange(self, change, value):   
        if change == QGraphicsPixmapItem.GraphicsItemChange.ItemScenePositionHasChanged: 
            if self.direction == '':
                return            
                     
            elif self.addedScroller == False:  ## check if its showtime    
                
                # if self.direction  == 'left'  and int(value.x()) == int(common['ViewW']/2):
                #     print(f"{int(value.x())} {int(common['ViewW']/2)}")
                #     self.canvas.showtime.pause()
                
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
        item = BkgItem(self.fileName, self.canvas, common['bkgZ'],self.mirroring, self.imgFile) 
                                         
        if self.mirroring == True:
            item.setMirrored(False) if self.flopped else item.setMirrored(True)   
                               
        item.tag = 'scroller'
        item.setZValue(self.zValue())  
                                    
        self.bkgWorks.restoreFromTrackers(item)  
    
        node = self.setNode(item)  ## sets property used in animation        
        item.anime = self.bkgWorks.setNextPath(node, item) 

        item.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)        
        self.scene.addItem(item)   
        
        item.anime.start()
                           
### --------------------------------------------------------   
    ''' used by 'first' to set its path and rates - rates set for 'next' as well '''
### --------------------------------------------------------   
    def setScrollerPath(self, bkg, which): ## which = first
        if bkg.direction == '':   
            return  
            
        node = self.setNode(bkg)  ## bkg property used in animation                      
        if node == None:
            MsgBox('setScrollerPath: Error Setting Path ...')
            return          
                
        elif bkg.direction in ('left', 'right') and bkg.width < common['ViewW'] or\
            bkg.direction == 'vertical' and bkg.height < common['ViewH']:
            self.bkgScrollWrks.notScrollable()  
            return 
   
        self.setStartingPos(bkg)  ## not the scrolling position      
        bkg.rate = bkg.bkgWorks.getScreenRate(bkg, which)  ## also sets tracker rate for 'next' 
        return self.bkgWorks.setFirstPath(node, bkg)  ## sets the paths duration
               
### --------------------------------------------------------  
    def setStartingPos(self, bkg):
        if bkg.direction == 'right':  ## gets it pointed in the right direction -->>
            bkg.setPos(QPointF(bkg.runway, 0)) 
        elif bkg.direction == 'left':  ## <<--
            bkg.setPos(QPointF())
        else:
            bkg.setPos(QPointF(0.0, float(bkg.runway)))

    def updateXY(self, pos):
        dragX = pos.x() - self.dragCnt.x()
        dragY = pos.y() - self.dragCnt.y()      
        self.x = self.initX + dragX
        self.y = self.initY + dragY
        
    def scaleThis(self, key):
        self.setOrigin()
        if key == '>':
            scale = .01
        elif key == '<':
            scale = -.01
        self.scale += scale
        self.setScale(self.scale)
    
    def setNode(self, bkg):     
        try:  
            node = Anime.Node(bkg)       
            return QPropertyAnimation(node, b'pos') 
        except RuntimeError:
            return None
   
    def setMirrored(self, bool):
        self.flopped = bool  
        if not self.dots.Vertical:
            self.setPixmap(QPixmap.fromImage(self.imgFile.mirrored(
                horizontal=self.flopped, vertical=False)))
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def setOrigin(self):  
        b = self.boundingRect()
        op = QPointF(b.width()/2, b.height()/2)
        self.setTransformOriginPoint(op)
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
                                                                                                                                                                      
### ---------------------- dotsBkgItem ---------------------


        