
import os

from PyQt6.QtCore       import Qt, QPointF, QPropertyAnimation, pyqtSlot
from PyQt6.QtGui        import QImage, QPixmap
from PyQt6.QtWidgets    import QGraphicsPixmapItem
                 
from dotsShared         import common, paths
from dotsSideGig        import MsgBox, point
from dotsBkgWorks       import BkgWorks

import dotsAnimation    as Anime

### ---------------------- dotsBkgItem ---------------------                   
''' See StartHere.md for a detailed explanation on scrolling backgrounds '''  
### --------------------------------------------------------
screentime = {  ## based on a 1280X640 .jpg under .5MB for 16:9 background
        ##   first, next-left, next-right --- there are always two backgrounds once started
    '1080':  (10.0,  17.50,  17.45),     ## 1440px actual size when scaled 1280X640 for 16:9
    '1280':  (10.0,  18.75,  18.85),  
    '1215':  (10.0,  17.35,  17.4),     ## 1620px actual size when scaled 1280X640 for 16:9
    '1440':  (10.0,  18.7,   18.85),
    '1296':  (10.0,  17.35,  17.4),     ## 1728px actual size when scaled 1280X640 for 16:9
    '1536':  (10.0,  18.65,  18.60),  
    '1102':  (10.0,  20.9,    0.0),
    '900':   (10.0,  23.2,    0.0),
    '912':   (10.0,  20.9,   0.0),
}

moretimes = {   ## based on a 1080X640 .jpg under .5MB for 3:2 background
    '1080':  (10.0,   19.05, 19.05),   ## 1215px actual size when scaled 1080X640 for 3:2
    '1215':  (10.0,   18.88, 18.89),   ## 1367px actual size when scaled 1080X640 for 3:2
    '1296':  (10.0,   18.88, 18.87),   ## 1458px actual size when scaled 1080X640 for 3:2
    '900':   (10.0,   21.4,   0.0),    ## 1013px actual size when scaled 640X1080 for 2:3
}

showtime = {  ## trigger to add a new background based on number of pixels remaining in runway
    'snakes':   15,  ## also used by vertical 
    'left':     11, 
    'right':    15,  
    'vertical': 17,  ## trying this out 
}
        
### --------------------------------------------------------
class BkgItem(QGraphicsPixmapItem):  ## background
### --------------------------------------------------------
    def __init__(self, fileName, canvas, z=common['bkgZ'], mirror=False):
        super().__init__()

        self.canvas   = canvas
        self.dots     = self.canvas.dots
        self.scene    = self.canvas.scene
        self.bkgMaker = self.canvas.bkgMaker
        
        self.bkgWorks = BkgWorks(self)
    
        self.ViewW = common['ViewW']
        self.ViewH = common['ViewH']

        self.type = 'bkg'
        self.fileName = fileName  
           
        self.setZValue(z)      
        self.init()
                  
### --------------------------------------------------------   
    def init(self):    
        self.path = paths['bkgPath']
        self.imgFile  = None      
        self.scrollable = False
          
        if 'demo' in self.fileName: self.path = paths['demo']
        self.fileName = self.path + os.path.basename(self.fileName) 
        
        try:   ## --- sets if scrollable --- ##
            if not self.dots.Vertical: 
                self.bkgWorks.setWidthHeight(QImage(self.fileName)) 
            else:
                self.bkgWorks.setVertical(QImage(self.fileName))
        except Exception:
            MsgBox('error on loading: ' + self.fileName)
            return
                 
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
                                            
        self.id = 0  ## not used except for conisistency          
        self.flopped = False
        self.locked = False
                    
        self.width  = self.imgFile.width()
        self.height = self.imgFile.height() 
            
        if not self.dots.Vertical: 
            self.setMirrored(False)
                                                 
        self.x, self.y = 0.0, 0.0
        
        self.tag = ''  
        self.anime = None
        self.matte = None
        
        self.addedScroller = False
           
        self.direction = ''  ## direction of scroll 
        self.factor    = self.bkgMaker.factor    ## sets default    
        self.mirroring = self.bkgMaker.mirroring ## sets default - false equals continuous
        self.rate      = 0
        self.showtime  = 0  ## number of pixels before the runway ends and then it's showtime
        
        self.runway    = 0  ## what's not visible     
        self.setRunWay()  
        
        self.setPixmap(QPixmap.fromImage(self.imgFile)) 
                              
        self.ratio = self.height/9
        self.ratio = int(self.width/self.ratio)
                    
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, False)                                 
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)  ## locked
          
        self.key = ''    
        self.dragCnt = 0
        self.save = QPointF()  
              
### -------------------------------------------------------- 
    @pyqtSlot(str)
    def setPixKeys(self, key):
        self.key = key 
                           
    def mousePressEvent(self, e):
        if not self.canvas.pathMakerOn:       
            if e.button() == Qt.MouseButton.RightButton:
                self.bkgMaker.addWidget(self)                    
            elif self.canvas.key == 'del':    
                self.delete()          
            elif self.canvas.key == '/':  ## to back
                self.bkgMaker.back(self)     
            elif self.canvas.key == 'shift':  ## flop it
                self.flopped = not self.flopped 
                self.setMirrored(self.flopped)     
            elif self.canvas.key in ('enter','return'):  ## to front  
                self.bkgMaker.front(self)             
            elif self.key == ',':  ## probably will only work on background with transparent spaces
                self.bkgMaker.backOne(self)  
            elif self.key == '.': 
                self.bkgMaker.upOne(self)  
            elif self.key == 'opt':  ## show background tag
                self.bkgWorks.tagBkg(self, e.scenePos())
            self.initX, self.initY = self.x, self.y  
            self.dragCnt = self.mapToScene(e.pos())
            self.canvas.key = ''
        e.accept()     

### -------------------------------------------------------- 
    def itemChange(self, change, value):
        if change == QGraphicsPixmapItem.GraphicsItemChange.ItemScenePositionHasChanged: 
            if self.direction == '':
                return            
            ## 'first' has already set its setScrollerPath                 
            elif self.addedScroller == False:  ## check if its showtime                      
                if self.direction  == 'left'  and int(value.x()-self.runway) <= self.showtime or\
                    self.direction == 'right' and int(value.x()) >= -self.showtime or\
                    self.direction == 'vertical' and int(value.y())-self.runway <= self.showtime:  
                    self.addNextScroller() 
                    self.addedScroller = True                                           
            elif self.addedScroller == True:  ## test if nolonger in view
                if self.direction   == 'left'  and abs((value.x())) >= self.width or \
                    self.direction  == 'right' and abs(int(value.x())) >= common['ViewW'] or \
                    self.direction  == 'vertical' and int(value.y()) >= self.height:
                    self.anime.stop()
                    self.bkgMaker.deleteBkg(self)  ## deleteBkg()   
                                                    
        return super(QGraphicsPixmapItem, self).itemChange(change, value)
 
### --------------------------------------------------------                       
    def addNextScroller(self):  ## add and scroll the next background    
        self.fileName = self.path + os.path.basename(self.fileName)      
        item = BkgItem(self.fileName, self.canvas, common['bkgZ']) 
                   
        if self.mirroring == False:  ## continuous
            item.setMirrored(False)
        elif self.ratio <= 27 or self.dots.Vertical == False:  ## 27:9 = 3:1 
            item.setMirrored(False) if self.flopped else item.setMirrored(True) 
        else:
            item.setMirrored(False)
                               
        item.tag = 'scroller'
        item.setZValue(self.zValue())  
        item.showtime = self.showtime   
             
        self.bkgWorks.restoreFromTrackers(item, 'addnxt')  ## gets set to default   
        item.anime = self.setScrollerPath(item, 'next')  ## txt for debugging      
  
        item.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)         
        self.scene.addItem(item)   
           
        item.anime.start()
                               
### --------------------------------------------------------   
    ''' sets scroller animation - runs directly from demos as well '''
### --------------------------------------------------------        
    def setScrollerPath(self, bkg, which): ## which = first/next 
        if bkg.direction == '':   
            return      

        path = self.setNode(bkg)         
        if path == None:
            MsgBox('setScrollerPath: error setting scroller path...')
            return
                
        if bkg.direction in ('left', 'right') and bkg.width < common['ViewW'] or\
            bkg.direction == 'vertical' and bkg.height < common['ViewH']:
            self.bkgWorks.notScrollable()  
            return 
 
        if bkg.direction == 'right':  ## gets it pointed in the right direction
            bkg.setPos(QPointF(bkg.runway, 0)) 
        elif bkg.direction == 'left':  
            bkg.setPos(QPointF())
        else:
            bkg.setPos(QPointF(0.0, float(bkg.runway)))
                        
        bkg.rate = bkg.setRate(which)  ## always to make sure     
        bkg.showtime = bkg.setShowTime(which)   
                                    
        if which == 'next':            
            return self.bkgWorks.setNextPath(path, bkg)  
        else:
            return self.bkgWorks.setFirstPath(path, bkg) 

### --------------------------------------------------------
    def setRunWay(self):      
        if not self.dots.Vertical:             
            self.runway = int(common['ViewW'] - self.width)  ## pixels outside of view
        else:
            self.runway = int(common['ViewH'] - self.height) 
  
### --------------------------------------------------------                  
    def setShowTime(self, which=''): 
        ## snakes need more time - the rest vary to build and position and comes before vertical 
        if 'snakes' in self.fileName and self.direction != 'vertical':
            show = showtime['snakes']   
        elif self.direction == 'vertical':  ## see vertical in bkgWorks - there's a kludge
            show = showtime['vertical']       
        elif self.direction == 'left':   
            show = showtime['left']
        elif self.direction == 'right':  
            show = showtime['right'] 
                                
        if which == 'next':
            val = self.bkgWorks.getShowtimeFromTrackers(self)  
            if val != 0:
                show = val                   
        return show
  
### --------------------------------------------------------  
    def setRate(self, which =''):
        rate = self.getRate()   
                   
        if which == 'first':
            rate = rate[0]    
            
        elif self.rate == 0:  ## needs to be 0
            if self.direction == 'right':
                rate = rate[2]
            else:
                rate = rate[1]      
            self.rate = rate  ## good idea 
 
        if which == 'next':
            val = self.bkgWorks.getRateFromTrackers(self)  
            if val != 0:
                rate = val   
                               
        return rate
    
### --------------------------------------------------------
    def getRate(self):
        if common['Screen'] == '1080' and self.width < 1315:  ## 1080X640 3:2 format else use 16:9
            rate = moretimes[common['Screen']]
        elif common['Screen'] == '1215' and self.width < 1467:
            rate = moretimes[common['Screen']]
        elif common['Screen'] == '1296' and self.width < 1558:
            rate = moretimes[common['Screen']]       
        elif common['Screen'] == '900'  and self.height < 1115:  ##dd in this case 2:3
            rate = moretimes[common['Screen']]    
        else:   
            rate = screentime[common['Screen']]  ## 16:9 format 
        return rate
                                                   
### --------------------------------------------------------  
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
                       
    def delete(self):  ## also called by widget
        self.bkgMaker.deleteBkg(self)
   
    def setMirrored(self, bool):
        self.flopped = bool  
        if not self.dots.Vertical:
            self.setPixmap(QPixmap.fromImage(self.imgFile.mirrored(
                # horizontally=self.flopped, vertically=False)))  ## pyside6
                horizontal=self.flopped, vertical=False)))
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def setOrigin(self):  
        b = self.boundingRect()
        op = QPointF(b.width()/2, b.height()/2)
        self.setTransformOriginPoint(op)
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
                                                                                                                                                                      
### ---------------------- dotsBkgItem ---------------------


        