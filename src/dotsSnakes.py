
import os
import random

from PyQt6.QtCore       import Qt, QPointF, QTimer
from PyQt6.QtGui        import QColor, QImage, QPixmap
from PyQt6.QtWidgets    import QGraphicsPixmapItem

import dotsAnimation    as Anime

from dotsSidePath       import pathLoader, pathAnimator
from dotsShared         import paths, common
from dotsSideGig        import *
from functools          import partial
from dotsBkgMaker       import BkgItem
from dotsBatsAndHats    import getPath

### --------------------- dotsSnakes ----------------------- 
''' classes: Snake, Snakes '''               
### --------------------------------------------------------
class Snake(QGraphicsPixmapItem):  ## stripped down pixItem
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
        self.anime = Anime.reprise(self)
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
        snakes = 3  ## ## if scrolling make these many and quit
        
        if what == 'blue':  ## not scrolling
            snakes = 4  
        
        if what not in ('blue', 'left', 'vertical'):
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
            QTimer.singleShot(k * 300, partial(self.run, path))  ## leave some time between snakes
            
            if k == snakes:        
                self.canvas.showWorks.disablePlay()  ## turns off play - turns on pause/resume/stop
                if what in ('vertical', 'left'):     ## run the scrolling background
                    if self.scroller.anime: QTimer.singleShot(200, self.scroller.anime.start)                                      
                break
    
### -------------------------------------------------------- 
    def setSelection(self, what):  ## no right scrolling for snakes
        if what == 'blue':
            color  = QColor(QColor(0,84,127) )  ## ocean blue                                
            self.canvas.bkgMaker.setBkgColor(QColor(color), -99)  ## set zValue to -99
            
        if self.scroller != None:
            self.scroller.init()  
        elif what == 'left':
            self.scroller = BkgItem(paths['demo'] + 'snakes.jpg', self.canvas)
            
            self.scroller.direction = 'left' 
            self.scroller.tag = 'scroller'
            self.scroller.mirroring = True  
            self.scroller.bkgWorks.addTracker(self.scroller)
            self.scroller.bkgWorks.setDirection(self.scroller.direction)
            
            self.scroller.anime = self.scroller.setScrollerPath(self.scroller, 'first')  ## the first background 
            
        elif what == 'vertical':
            if common['Screen'] == '1102':
                self.scroller = BkgItem(paths['demo'] + 'snakes_1102.jpg', self.canvas) 
            else:
                self.scroller =  BkgItem(paths['demo'] + 'snakes_912.jpg', self.canvas)
                
            self.scroller.direction = 'vertical'   
            self.scroller.tag = 'scroller'
            
            if common['Screen'] in ('900', '912'):
                self.scroller.mirroring = False
            else:
                self.scroller.mirroring = True     
            self.scroller.bkgWorks.addTracker(self.scroller)
            self.scroller.bkgWorks.setDirection(self.scroller.direction)
            
            self.scroller.anime = self.scroller.setScrollerPath(self.scroller, 'first')  ## it's always the first - it sets the 2nd
            
            self.scroller.runway = int(common['ViewH'] - self.scroller.height)  
            self.scroller.setPos(QPointF(0, self.scroller.runway))
                      
        if what in ('vertical', 'left'): 
            self.scroller.addedScroller == False   
            self.scroller.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)   
            self.scene.addItem(self.scroller)
            
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
        node = Anime.Node(pix)  ## get pix pos property    
        pix.tag = fileName        
        pix.anime = pathAnimator(node, sync, waypts)  ## set path animation      
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
        self.scroller.bkgWorks.delTracker(self.scroller) 
        self.delSnakes()        
        self.makeSnakes(what)
              
    def delSnakes(self):
        if len(self.scene.items()) > 0:
            for pix in self.scene.items():      
                if pix.type in ('snake','bkg'):
                    self.scene.removeItem(pix)
                    del pix
                                                                                                                               
### ---------------------- dotsSnakes ----------------------     


