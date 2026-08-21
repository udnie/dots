
import os
import random
import random

from PyQt6.QtCore       import Qt, QPointF, QTimer
from PyQt6.QtGui        import QImage, QPixmap
from PyQt6.QtWidgets    import QGraphicsPixmapItem

from dotsAnimation      import reprise

from dotsSidePath       import pathLoader, pathAnimator
from dotsShared         import paths, common
from dotsSideGig        import *
from functools          import partial
from dotsBkgMaker       import BkgItem
from dotsBatsAndHats    import getPath

### --------------------- dotsSnakes ----------------------- 
''' classes: Snake, Snakes '''               
### --------------------------------------------------------
class Snake(QGraphicsPixmapItem):  ## stripped down pixitem
### --------------------------------------------------------
    def __init__(self, fileName, id, x, y, parent):
        super().__init__()

        self.canvas = parent   
        
        self.type = 'snake'            
        self.fileName = fileName
          
        self.id = int(id) 
        self.setZValue(id)
        
        img = QImage(fileName)

        w = img.width() * common['factor']  ## from screens
        h = img.height() * common['factor']
   
        img = img.scaled(int(w), int(h),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)

        self.width   = img.width()
        self.height  = img.height()  
        
        self.imgFile = img
        self.setPixmap(QPixmap(img))
 
        del img
  
        self.tag  = ''  
        self.part = 'segment'    
        
        self.x = 0
        self.y = 0
        
        self.alpha2 = 1.0  
        self.scale  = 1.0
        self.rotation = 1
    
        self.anime = None  
           
    def setOriginPt(self): 
        b = self.boundingRect()
        op = QPointF(b.width()/2, b.height()/2)
        self.setTransformOriginPoint(op)
     
    def reprise(self):  
        self.anime = None
        self.anime = reprise(self)
        self.anime.start()
        self.anime.finished.connect(self.anime.stop)
        self.clearFocus()
    
### --------------------------------------------------------
class Snakes:    
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas   = parent
        self.scene    = self.canvas.scene
        self.dots     = self.canvas.dots
        self.mapper   = self.canvas.mapper
        self.bkgMaker = self.canvas.bkgMaker 
                           
        self.what = ''
                                                      
### -------------------------------------------------------- 
    def makeSnakes(self, what):                                   
        self.what = what  
        self.waypts = None 
            
        self.canvas.openPlayFile = 'snakes'
        
        pic = {
            1: 'cactus-5.png',
            2: 'cactus-7.png',
            3: 'cactus-1.png',
        }
      
        self.scroller = None  
        self.scroller2 = None  
        
        snakes = 3  ## ## if scrolling make these many and quit
     
        if what not in ('left', 'vertical'):
            MsgBox('Something wrong with Snakes')
            return
               
        self.setSelection(what)
                      
        MsgBox('Processing...' + '  ', 2, getCtr(-100,-175))
     
### -------------------------------------------------------- 
        k = 0  ## outside counter - number of paths - quit at 3
        self.canvas.pixCount = 400  ## nothing else on the screen except background
        apaths = getPathList()  
        if apaths == []: 
            MsgBox('getPathList: No Paths Found!', 5)
            QTimer.singleShot(200, self.canvas.clear)   
            return 
                          
        while k <= snakes:
            path = getPath(apaths) 
            waypts = pathLoader(path)  
                
            if not waypts: 
                MsgBox(path + ' Not found')
                return
                  
            idx    = 0  ## segment counter
            steps  = 0  ## a counter used in scaling down snake body   
            length = (random.randint(22,27)*2) -1  ## number of segments
            sync   = random.randint(11,16) * 1000  ## duration
            scale  = (random.randint(18,25) * 4.0) / 100.0  ## body size  
        
            if (random.randint(1,3)) == 3:  ## just to make things interesting
                waypts = waypts.toReversed()
                                               
            for _ in range(length):  ## make the segments   
                self.a = pic[random.randint(1,len(pic))]  ## choose a pic             
                self.b = pic[random.randint(1,len(pic))]  
                                  
                skale = scale  ## sounds the same and avoids a possible conflict 
                
                if idx >= int(length * .65) - 1:  ## slim it down a tiny bit
                    steps += 1
                    skale = scale - ((steps * .75)/100.0)
                    
                pix = self.addSnakes(idx, path, waypts, sync)    
                rotation = (random.randint(-8, 8) * 3)  
                    
                self.canvas.sideCar.transFormPixItem(pix, rotation, skale, 1.0)  ## adds it to screen 
                self.canvas.pixCount -= 1  ## start at the highest zvalue, runs from front to back  
                idx += 1   
                     
            k += 1    
            QTimer.singleShot(k * 150, partial(self.run, path))  ## leave some time between snakes
            
            if k == snakes:        
                self.canvas.showWorks.disablePlay()  ## turns off play - turns on pause/resume/stop
                
                if what ==  'left':     ## run the scrolling background
                    if self.scroller.anime: QTimer.singleShot(200, self.scroller.anime.start)
                       
                elif self.scroller2.direction == 'vertical':  
                     
                    if self.scroller.anime: QTimer.singleShot(200, self.scroller.anime.start)  
                    if self.scroller2.anime: QTimer.singleShot(180, self.scroller2.anime.start)                                   
                break
    
### -------------------------------------------------------- 
    def setSelection(self, what):  ## no right scrolling for snakes  
        if self.scroller != None:
            self.scroller = BkgItem('snakes-43-wrp.jpg', self.canvas)
            
        elif what == 'left':
            self.scroller = BkgItem('snakes-43-wrp.jpg', self.canvas)
            
            self.scroller.direction = 'left' 
            self.scroller.path = paths['demo']  
            self.scroller.tag = 'scroller'
            self.scroller.mirroring = False
        
            self.canvas.bkgMaker.bkgTrackers.addTracker(self.scroller)
            self.scroller.bkgWorks.setDirection(self.scroller.direction)
            
            self.scroller.anime = self.scroller.setScrollerPath(self.scroller, 'first')  ## the first background 
            
        elif what == 'vertical':    
            # color = QColor(0,60,125)   ## ocean blue                                
            # self.canvas.bkgMaker.setBkgColor(QColor(color))  
       
            self.scroller = BkgItem('bubbles-wrp.jpg', self.canvas)    
            self.scroller.direction = 'vertical'   
            self.scroller.path = paths['demo'] 
            self.scroller.tag = 'scroller'
            self.scroller.factor = .90
            
            self.scroller.mirroring = False ###  if common['Screen'] in ('800','900') else True
                
            self.canvas.bkgMaker.bkgTrackers.addTracker(self.scroller)
            self.scroller.bkgWorks.setDirection(self.scroller.direction)
            
            self.scroller.anime = self.scroller.setScrollerPath(self.scroller, 'first')  ## it's always the first - it sets the 2nd
            
            self.scroller.runWay = int(common['ViewH'] - self.scroller.height)  
            self.scroller.setPos(QPointF(0, self.scroller.runWay))
                      
        if what in ('vertical', 'left'): 
            self.scroller.addedScroller = False   
            self.scroller.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)   
            self.scene.addItem(self.scroller)
            
            if what == 'vertical':
                self.scroller2 = self.addBubblesPng()   
                self.scroller2.addedScroller = False    
                self.scroller2.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)   
                self.scene.addItem(self.scroller2)
              
    def addBubblesPng(self):
        self.scroller2 = BkgItem('bubbles-scaled.png', self.canvas)    
        self.scroller2.direction = 'vertical'   
        self.scroller2.path = paths['demo'] 
        self.scroller2.tag = 'scroller'
        
        self.scroller2.setZValue(500)
        self.scroller2.factor = .65
        self.scroller2.mirroring = False
     
        self.canvas.bkgMaker.bkgTrackers.addTracker(self.scroller2)
        self.scroller2.bkgWorks.setDirection(self.scroller2.direction)
        
        self.scroller2.anime = self.scroller2.setScrollerPath(self.scroller2, 'first')  ## it's always the first - it sets the 2nd
        
        self.scroller2.runWay = int(common['ViewH'] - self.scroller2.height)  
        self.scroller2.setPos(QPointF(0, self.scroller2.runWay))
    
        return self.scroller2
            
 ### -------------------------------------------------------- 
    def addSnakes(self, idx, fileName, waypts, sync):                                                                                  
        if idx % 3 != 0:  ## vary the segments
            pix = Snake(paths['demo'] + self.a, self.canvas.pixCount, 0, 0, self.canvas)
        else:
            pix = Snake(paths['demo'] + self.b, self.canvas.pixCount, 0, 0, self.canvas) 
                        
        pix.x = int(constrain(xy(common['ViewW']), pix.width, common['ViewW'], 
                pix.width * -common['factor']))
        
        pix.y = int(constrain(xy(common['ViewH']), pix.height, common['ViewH'],
                pix.height * -common['factor'])) 
             
        pix.setPos(pix.x, pix.y)                                                   
        pix.tag = fileName      
        pix.path = paths['demo']   
        pix.anime = pathAnimator(pix, sync, waypts)  ## set path animation      
        return pix
        
    def run(self, p):
        n = 0  ## counter * wait time 
        t = (random.randint(13, 18) * 2) - 1  ## 25 to 35.ms
        for pix in self.scene.items():  
            if pix.type == 'snake' and p in pix.tag:
                n += 1
                pix.tag = pix.tag
                QTimer.singleShot(100 + (n * t), pix.anime.start)
                                 
    def rerun(self, what): 
        self.mapper.clearTagGroup()
        self.mapper.clearPaths()
        self.canvas.bkgMaker.bkgTrackers.delTracker(self.scroller) 
        self.canvas.bkgMaker.bkgTrackers.delTracker(self.scroller2) 
        self.delSnakes()      
        self.makeSnakes(what)
              
    def delSnakes(self):
        if len(self.scene.items()) > 0:
            for pix in self.scene.items():      
                if pix.type in ('snake','bkg'):
                    self.scene.removeItem(pix)
                    del pix
                                                                                                                               
### ---------------------- dotsSnakes ----------------------     


