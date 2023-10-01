
import os
import random

from PyQt6.QtCore       import Qt, QPointF, QTimer
from PyQt6.QtGui        import QColor, QImage, QPixmap
from PyQt6.QtWidgets    import QGraphicsPixmapItem, QMenu

import dotsAnimation    as Anime

from dotsSideCar        import SideCar
from dotsSidePath       import pathLoader, pathWorks
from dotsShared         import paths, common
from dotsSideGig        import *
from functools          import partial
from dotsBkgMaker       import BkgItem
from dotsAbstractBats   import getPath

demos = {  ## used by demo menu
    'bats':   'Original Batwings',
    'blue':   'Snakes Blue Background',
    'left':   'Right to Left Scrolling',  
    'right':  'Left to Right Scrolling',  
    'snakes': 'Snakes Scrolling Background',    
}

### --------------------- dotsSnakes ----------------------- 
''' classes: DemoMenu, Snake, Snakes '''
### --------------------------------------------------------     
class DemoMenu:  
### --------------------------------------------------------
    def __init__(self, parent, sideShow):
        super().__init__()  
   
        self.canvas = parent
        self.sideShow = sideShow
        
        self.dots   = self.canvas.dots
        self.scene  = self.canvas.scene
        self.view   = self.canvas.view 
     
        self.snakes   = self.sideShow.snakes   
        self.bats     = self.sideShow.bats
        self.abstract = self.sideShow.abstract  ## hats and bats
       
        self.demoMenu = None
                       
    def openDemoMenu(self):
        self.closeDemoMenu()
        self.demoMenu = QMenu(self.canvas) 
        self.demoMenu.addAction('Demos Menu'.rjust(20,' '))
        self.demoMenu.addSeparator()
        for demo in demos.values():
            action = self.demoMenu.addAction(demo)
            self.demoMenu.addSeparator()
            action.triggered.connect(lambda chk, demo=demo: self.clicked(demo))            
        self.demoMenu.setFixedSize(220, 190)
        self.demoMenu.move(getCtr(-130, -225))   
        self.demoMenu.show()

    def clicked(self, demo):
        for key, value in demos.items():
            if value == demo:  ## singleshot needed for menu to clear
                QTimer.singleShot(200, partial(self.run, key))
                break
        self.closeDemoMenu()
        
    def closeDemoMenu(self):
        if self.demoMenu:
            self.demoMenu.close()           
        self.demoMenu = None
           
    def run(self, key):                         
        if key == 'bats':
            self.bats.makeBats()
        elif key == 'blue':
            self.runSnakes('blue') 
        elif key == 'snakes':
            if self.dots.Vertical:   
                self.runSnakes('vertical') 
            else:
                self.runSnakes('left')              
        elif key in ('left', 'right'):
            if self.dots.Vertical:     
                MsgBox('Not Implemented for Vertical Format')
                return             
            if key == 'left':  ## direction of travel
                self.abstract.makeAbstracts('left')  ## right to left 
            else: 
                self.abstract.makeAbstracts('right') ## left to right   

    def runSnakes(self, what): 
        if what in ('blue', 'snakes'): 
            self.snakes.delSnakes()    
        if what != '':
            QTimer.singleShot(100, partial(self.snakes.makeSnakes, what))           
        elif self.openPlayFile != 'snakes' and len(self.scene.items()) > 0:
            MsgBox('The Screen Needs to be Cleared inorder to Run Snakes', 6, getCtr(-225,-175))
            return 
                    
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
        self.mapper   = self.canvas.mapper
        self.bkgMaker = self.canvas.bkgMaker              
        self.sideCar  = SideCar(self.canvas)
        
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
      
        scroll = None  
        snakes = 3  ## if scrolling  
        
        if what not in ('blue', 'left', 'vertical'):
            MsgBox('Something wrong with Snakes')
            return
               
        if what == 'blue':
            snakes = 4  ## make these many and quit
            color  = QColor(QColor(0,84,127) )  ## ocean blue                                
            self.canvas.bkgMaker.setBkgColor(QColor(color), -99)  ## set zValue to -99 
            
        elif what == 'left':
            scroll = BkgItem(paths['demo'] + 'snakes.jpg', self.canvas)
            scroll.direction = 'left' 
            scroll.tag = 'scroller'
            scroll.anime = scroll.setScrollerPath(scroll, 'first')  ## the first background 
            
        elif what == 'vertical':
            scroll = BkgItem(paths['demo'] + 'snakes_vertical.jpg', self.canvas) 
            scroll.direction = 'vertical'   
            scroll.tag = 'scroller'
            scroll.anime = scroll.setScrollerPath(scroll, 'first')  ## it's always the first - it sets the 2nd
            scroll.runway = int(common['ViewH'] - scroll.height) + scroll.showtime  
            scroll.setPos(QPointF(0, scroll.runway))
            
        if what in ('vertical', 'left'): 
            scroll.addedScroller == False   
            scroll.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)   
            self.scene.addItem(scroll)
                         
        MsgBox('Processing...' + '  ', 2, getCtr(-100,-175))
     
### -------------------------------------------------------- 
        k = 0  ## outside counter - number of paths - quit at 3
        self.canvas.pixCount = 400  ## nothing else on the screen except background
        apaths = getPathList()   
                                   
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
                    
                self.sideCar.transFormPixItem(pix, rotation, skale, 1.0)  ## adds it to screen 
                self.canvas.pixCount -= 1  ## start at the highest zvalue, runs from front to back  
                idx += 1   
                     
            k += 1    
            QTimer.singleShot(k * 300, partial(self.run, path))  ## leave some time between snakes
            
            if k == snakes:        
                self.sideCar.disablePlay()  ## turns on pause/resume/stop
                if what in ('vertical', 'left'): 
                    if scroll.anime: QTimer.singleShot(200, scroll.anime.start)                                      
                break
    
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
        pix.anime = pathWorks(node, sync, waypts)  ## set path animation      
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
        self.delSnakes()
        self.makeSnakes(what)
              
    def delSnakes(self):
        if len(self.canvas.scene.items()) > 0:
            for pix in self.canvas.scene.items():      
                if pix.type == 'snake':
                    self.canvas.scene.removeItem(pix)
                    del pix
                                                                                                                   
### ---------------------- dotsSnakes ----------------------     


