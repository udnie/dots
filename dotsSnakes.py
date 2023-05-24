
import os
import random

from PyQt6.QtCore       import Qt, QPointF, QTimer
from PyQt6.QtGui        import QColor, QImage, QPixmap
from PyQt6.QtWidgets    import QGraphicsPixmapItem

import dotsAnimation    as Anime

from dotsSideCar        import SideCar
from dotsSidePath       import pathLoader, pathWorks
from dotsShared         import paths, common
from dotsSideGig        import *
from functools          import partial
from dotsBkgMaker       import BkgItem

### ---------------------- dotsSidePath --------------------
''' dotsPaths is used by animations and pathmaker and contains 
    demo, setPath, getOffSet and pathLoader '''
    
### --------------------------------------------------------
class Snake(QGraphicsPixmapItem):
### --------------------------------------------------------
    def __init__(self, fileName, id, x, y, parent):
        super().__init__()

        self.canvas  = parent       
        self.fileName = fileName
          
        self.id = int(id) 
        self.setZValue(id)
        
        img = QImage(fileName)

        w = img.width() * common['factor']
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
        self.type = 'snake'
        
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
     
    def reprise(self):  ## return pixitem to original position
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
 
        self.canvas  = parent
        self.scene   = self.canvas.scene
        self.mapper   = self.canvas.mapper
                                    
        self.sideCar = SideCar(self.canvas)
        self.PathsToClear = []
                                              
### -------------------------------------------------------- 
    def setSnakePaths(self, what):            
        apaths = getPathList()               
        random.shuffle(apaths) 
           
        self.waypts  = None     
        self.canvas.openPlayFile = 'snakes'
        
        pic = {
            1: 'cactus-5.png',
            2: 'cactus-7.png',
            3: 'cactus-1.png',
        }
      
        scroll = None  
        snakes = 3  ## make these many and quit   
        
        if what not in ('blue', 'left', 'vertical'):
            MsgBox('Something wrong with Snakes')
               
        if what == 'blue':
            snakes = 4  ## make these many and quit
            color  = QColor(QColor(0,84,127) )  ## ocean blue                                
            self.canvas.bkgMaker.setBkgColor(QColor(color), -99)  ## set zValue to -99 
            
        elif what == 'left':
            scroll = BkgItem(paths['imagePath'] + 'snakes.jpg', self.canvas)
            scroll.direction = 'left' 
            scroll.tag = 'scroller'
            scroll.anime = scroll.setScrollerPath(scroll, 1)   
            
        elif what == 'vertical':
            scroll = BkgItem(paths['imagePath'] + 'snakes_vertical.jpg', self.canvas) 
            scroll.direction = 'vertical'   
            scroll.tag = 'scroller'
            scroll.anime = scroll.setScrollerPath(scroll, 1)
       
            scroll.runway = int(common['ViewH'] - scroll.height) + scroll.showtime  
            scroll.setPos(QPointF(0, scroll.runway))
            
        if what in ('vertical', 'left'): 
            scroll.addedScroller == False   
            scroll.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)   
            self.scene.addItem(scroll)
                         
        MsgBox('Processing...' + '  ', 2, getCtr(-100,-175))
 
        k = 0  ## outside counter - number of paths - quit at 3
        plist  = ['twigs.path', 'demo-', 'black-forest']  ## reject
        self.canvas.pixCount = 400  ## nothing else on the screen except background
      
        for p in apaths:                 
            if any(ele in p for ele in plist):  ## if any <-------
                 continue
            
            fileName = os.path.basename(p)    
            waypts = pathLoader(fileName)
            
            if not waypts: 
                return
                  
            idx    = 0  ## snake counter
            steps  = 0  ## a counter used in scaling down snake body
            
            length = (random.randint(22,27)*2) -1  ## number of segments
            sync   = random.randint(11,16) * 1000  ## duration
            scale  = (random.randint(18,25) * 4.0) / 100.0  ## body size  
        
            if (random.randint(1,3)) == 3:  ## just to make things interesting
                waypts = waypts.toReversed()
                                               
            a = pic[random.randint(1,len(pic))]  ## choose a pic             
            b = pic[random.randint(1,len(pic))] 
                                                                                                                                                               
            for _ in range(length): 
                                     
                if idx % 3 != 0:
                    pix = Snake(paths['imagePath'] + a, self.canvas.pixCount, 0, 0, self.canvas)
                else:
                    pix = Snake(paths['imagePath'] + b, self.canvas.pixCount, 0, 0, self.canvas)
                          
                pix.x = int(constrain(xy(common['ViewW']), pix.width, common['ViewW'], 
                        pix.width * -common['factor']))
                pix.y = int(constrain(xy(common['ViewH']), pix.height, common['ViewH'],
                        pix.height * -common['factor']))
                      
                pix.setPos(pix.x, pix.y) 
                 
                idx += 1    
                skale = scale  ## sounds the same and avoids a possible conflict
                
                if idx >= int(length * .65) - 1:  ## slim it down a tiny bit
                    steps += 1
                    skale = scale - ((steps * .75)/100.0)
                                                               
                rotation = (random.randint(-8, 8) * 3)    
                pix.setRotation(rotation)
   
                node = Anime.Node(pix)  ## get pix pos property    
                pix.tag = fileName        
                pix.anime = pathWorks(node, sync, waypts)  ## set path animation
                
                self.sideCar.transFormPixItem(pix, rotation, skale, 1.0)  ## adds it to screen 
                self.canvas.pixCount -= 1  ## start at the highest zvalue, runs from front to back
      
            k += 1
            QTimer.singleShot(k * 600, partial(self.run, fileName))
            if k == snakes:        
                self.sideCar.disablePlay()  
                if what in ('vertical', 'left'): 
                    if scroll.anime: QTimer.singleShot(200, scroll.anime.start)                  
                break
          
    def run(self, p):
        n = 0  ## counter * wait time 
        t = (random.randint(13, 18) * 2) - 1  ## 25 to 35.ms
        for pix in self.scene.items():  
            if pix.type == 'snake' and p in pix.tag:
                n += 1
                pix.tag = pix.tag
                QTimer.singleShot(100 + (n * t), pix.anime.start)
                                 
    def rerun(self):         
        self.clearPaths()
        self.bkgMaker.delSnakes()
        QTimer.singleShot(200, self.setSnakePaths)
       
    def clearPaths(self):  
        self.mapper.clearTagGroup()
        self.mapper.clearPaths()    
        for pix in self.scene.items():
            if pix.type == 'snake': self.scene.removeItem(pix)
        for p in self.PathsToClear:
            p.clear()
        self.PathsToClear = []
        
  ### --------------------------------------------------------      
        
        
        
