
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
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
     
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
        self.sideCar = SideCar(self.canvas)
        self.mapper  = self.canvas.mapper
                     
        self.PathsToClear = []
                                              
### -------------------------------------------------------- 
    def setSnakePaths(self):            
        apaths = getPathList()               
        random.shuffle(apaths) 
                      
        self.waypts  = None     
        self.canvas.openPlayFile = 'snakes'
        
        pic = {
            1: 'cactus-5.png',
            2: 'cactus-7.png',
            3: 'cactus-1.png',
        }
 
        color  = QColor(QColor(0,84,127) )  ## ocean blue                                
        self.canvas.bkgMaker.setBkgColor(QColor(color), -99)  ## set zValue to -99 

        MsgBox('Processing...' + '  ', 2, getCtr(-100,-175))
 
        k = 0  ## outside counter - number of paths - quit at 4
        plist  = ['twigs.path', 'demo-', 'black-forest']  ## reject
        self.canvas.pixCount = 400  ## nothing else on the screen except background
           
        for p in apaths:                 
            if any(ele in p for ele in plist):  ## if any <-------
                 continue
            
            p = os.path.basename(p)
            
            waypts = pathLoader(p)
            if not waypts: 
                return
            
            length = (random.randint(22,27)*2) -1
            sync   = random.randint(11,16) * 1000  ## duration
            scale  = (random.randint(18,25) * 4.0) / 100.0      
            snakes = 4
            idx    = 0  ## snake counter
            steps  = 0
                   
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
                
                skale = scale
                
                if idx >= int(length * .65) - 1:  ## slim it down a tiny bit
                    steps += 1
                    skale = scale - ((steps * .75)/100.0)
                                                               
                rotation = (random.randint(-8, 8) * 3)    
                pix.setRotation(rotation)
   
                node = Anime.Node(pix)  ## get pix pos property    
                pix.tag = p         
                pix.anime = pathWorks(node, sync, waypts)  ## set path animation
                
                self.sideCar.transFormPixItem(pix, rotation, skale, 1.0)  ## adds it to screen 
                self.canvas.pixCount -= 1  ## start at the highest zvalue, runs from front to back
      
            k += 1
            QTimer.singleShot(k * 600, partial(self.run, p))
            if k == snakes:
                self.sideCar.disablePlay()           
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
        
        
        
