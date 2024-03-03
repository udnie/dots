
import os
import random

import asyncio
import time

from PyQt6.QtCore       import Qt, QTimer
from PyQt6.QtWidgets    import QGraphicsPixmapItem

import dotsAnimation    as Anime

from dotsSidePath       import pathLoader, pathAnimator
from dotsShared         import paths, common
from dotsSideGig        import *
from dotsBkgMaker       import BkgItem
from dotsPixItem        import PixItem
from dotsShowWorks      import ShowWorks

backGrounds = {  ## scaled up as needed - 1280.jpg and bats_vert in demo directory
    '1080':  'montreaux.jpg', 
    '1280':  'montreaux-1280.jpg',
    '1215':  'montreaux.jpg',  
    '1440':  'montreaux-1280.jpg',
    '1296':  'montreaux.jpg',    
    '1536':  'montreaux-1280.jpg',
     '900':  'bats_vertical.jpg',  ## blue night photo
     '912':  'bats_vertical.jpg', 
    '1102':  'bats_vertical.jpg',
}
    
### ------------------- dotsAbstractBats -------------------
class Wings: 
### --------------------------------------------------------    
    ''' Wings no longer come off, only the bat can move, wings still flap '''   
### --------------------------------------------------------
    def __init__(self, parent, x, y, tag): 
        super().__init__()
 
        self.canvas = parent    
        self.scene  = self.canvas.scene     
        
        if not os.path.exists(paths['imagePath'] + 'bat-pivot.png'):
            return
    
        self.pivot     = self.pivot(paths['imagePath'] + 'bat-pivot.png', x, y, tag)
        self.rightWing = self.right(paths['imagePath'] + 'bat-wings.png', x, y)
        self.leftWing  = self.left(paths['imagePath']  + 'bat-wings.png', x, y)
                                             
        self.half   = self.pivot.width/2 
        self.height = self.pivot.height/5    

        if common['Screen'] in ('1215', '1440'):
            self.height = self.pivot.height/7  ## drops too low otherwise
        elif common['Screen'] in ('1536', '1296'):
            self.height = self.pivot.height/9  
          
        try:
            self.pivot.setPos(self.pivot.x, self.pivot.y)
            self.pivot.setScale(.60)
            self.pivot.setOriginPt() 
        except IOError:
            pass    
                
        ## center wings around pivot - some magic numbers
        self.rightWing.setPos(self.half+1, self.height-2)
        self.leftWing.setPos(-self.leftWing.width+(self.half+5), self.height-5)

        self.rightWing.setParentItem(self.pivot)  
        self.leftWing.setParentItem(self.pivot)
        
        self.scene.addItem(self.pivot)
                   
### --------------------------------------------------------
    def pivot(self, file, x, y, tag):  ## tag may be empty - used for setting path or animation
        self.canvas.pixCount += 1         
        pivot = PixItem(file, 
            self.canvas.pixCount,
            x, y,  
            self.canvas
        ) 
        pivot.part = 'pivot' 
        pivot.tag  = tag  ## path to follow - random select
  
        pivot.setZValue(self.canvas.mapper.toFront(-1))
        pivot.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, True)  
        pivot.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemDoesntPropagateOpacityToChildren, True)
                    
        return pivot
   
### --------------------------------------------------------  
    def right(self, file, x, y):            
        self.canvas.pixCount += 1
        pix = PixItem(file, self.canvas.pixCount, x-20, y, 
            self.canvas,
            False,
        )  ## don't flop it 
        return self.setWing(pix, 'right')  
            
### --------------------------------------------------------          
    def left(self, file, x, y):         
        self.canvas.pixCount += 1
        pix = PixItem(file, self.canvas.pixCount, x + self.rightWing.width, y,  ## offset to left
            self.canvas,
            True
        )  ## flop it
        return self.setWing(pix, 'left') 
   
### --------------------------------------------------------              
    def setWing(self, pix, wing):   
        pix.part = wing  ## part could be other than a wing   
        pix.tag  = 'Flapper'  ## applies this animation when run
        pix.setZValue(pix.zValue())  ## reset wing zvals
        pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, False)
        pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemStacksBehindParent)
        pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIgnoresParentOpacity, True)  ## won't disappear
        pix.setAcceptedMouseButtons(Qt.MouseButton.NoButton)  ## mouse ignored - wings can't be move       
        return pix
            
### --------------------------------------------------------
class Bats:     
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
        self.scene  = self.canvas.scene
        self.dots   = self.canvas.dots
        self.mapper = self.canvas.mapper  
                                         
        self.sideCar   = self.canvas.sideCar
        self.animation = self.canvas.animation
       
        self.showWorks = ShowWorks(self.canvas)
                                                   
### -------------------------------------------------------- 
    def makeBats(self):  ## makes aliens and bats                 
        self.canvas.openPlayFile = 'bats'

        if 'montreaux' in backGrounds[common['Screen']]:
            bkg = BkgItem(paths['bkgPath'] + backGrounds[common['Screen']], self.canvas)
        else:  
            bkg = BkgItem(paths['demo'] + backGrounds[common['Screen']], self.canvas) 
         
        bkg.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
        self.scene.addItem(bkg)
     
        self.batWings()       
        self.greys()
        self.run()
        self.showWorks.disablePlay()
                      
### --------------------------------------------------------
    def batWings(self):  ## these go to screen and wait to be run
        k = 0   
        bats = 3 
        apaths = getPathList()        
        if apaths == []:
            MsgBox('getPathList: No Paths Found!', 5)
            QTimer.singleShot(200, self.canvas.clear)    
            return 
        while k < bats:      
            x = random.randrange(200, common['ViewW']-300)
            y = random.randrange(200, common['ViewH']-300) 
            path = getPath(apaths)                               
            Wings(self.canvas, x, y, path)   
            k += 1       
     
    def runBat(self, pix, n, t):  ## run by run
        if pix.part == 'pivot':   ## adds path to follow
            node = Anime.Node(pix)  ## gets pix pos property 
            sync = random.randint(11,16) * 1000  ## sets duration 
            waypts = pathLoader(pix.tag)  ## get the path        
            pix.anime = pathAnimator(node, sync, waypts)  ## sets a path to follow     
            QTimer.singleShot(100 + (n * t), pix.anime.start)  
        elif pix.part in ('left','right'): 
            pix.anime = self.animation.setAnimation(pix.tag, pix)  ## Flapper in Wings   
            QTimer.singleShot(100 + (n * t), pix.anime.start)
                   
### --------------------------------------------------------                 
    def greys(self):  ## these go to screen and wait to be run
        greys = 23  
       
        if not os.path.exists(paths['spritePath'] + 'alien.png'):
            return
  
        pathStr = paths['spritePath'] + 'alien.png'     
        for i in range(greys):
            pix = self.oneGrey(pathStr)
            self.scene.addItem(pix)
            
    def oneGrey(self, pathStr):
        pix = PixItem(pathStr, self.canvas.pixCount, 0, 0, self.canvas)       
        pix.x = random.randrange(200, common['ViewW']-300)
        pix.y = random.randrange(200, common['ViewH']-300)
        pix.setPos(pix.x, pix.y)     
        pix.setScale(.65)   
        if common['Screen'] == '912':
            pix.tag = 'demo-' + '900' + '.path' 
        else:
            pix.tag = 'demo-' + common['Screen'] + '.path'  ## in the demo directory             
        return pix
                                       
    def runGrey(self, pix, k, scale):
        pix.setOriginPt()
        pix.scale = scale * (67-(k*3))/100.0  ## 3 * 22 screen items 
        pix.setScale(pix.scale)  
        pix.part = ''  ## follows a demo path
        pix.anime = self.animation.setAnimation(pix.tag, pix) 
        QTimer.singleShot(100 + (k * 60), pix.anime.start)
            
### --------------------------------------------------------        
    def run(self):  
        k , n = 0, 0 
        scale = .65 
        for pix in self.scene.items():
            if pix.type =='pix': 
                if 'alien' in pix.fileName:
                    self.runGrey(pix, k,  scale)
                    k += 1
                elif pix.part in pix.part in ('pivot','left','right'):
                    t = (random.randint(13, 18) * 2) - 1  ## 25 to 35.ms            
                    self.runBat(pix, n, t)
                    n +=1 
                    
 ### --------------------------------------------------------  
    def rerun(self):  ## no reason to delete     
        clearPaths(self)
        self.run()
        self.showWorks.disablePlay()
     
    def delBats(self):
        if len(self.scene.items()) > 0:
            for pix in self.scene.items():      
                if pix.type == 'pix':  ## deleting pivot deletes the wings
                    if pix.part in ('pivot') or 'alien' in pix.fileName:   
                        self.scene.removeItem(pix)
                        del pix
                                       
### --------------------------------------------------------
class Abstract:  ## hats
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent    
        self.scene  = self.canvas.scene
        self.dots   = self.canvas.dots
        self.mapper = self.canvas.mapper
        
        self.sideCar   = self.canvas.sideCar                                          
        self.animation = self.canvas.animation
        self.showWorks = ShowWorks(self.canvas)
   
        self.hats = 7
        self.shadows = False
        self.direction = ''
        
        self.viewW, self.viewH = common['ViewW'],common['ViewH'] 
        
        self.scroller = None
        
### --------------------------------------------------------      
    def makeAbstracts(self, direction):
        self.direction = direction
        self.canvas.openPlayFile = 'abstract'     
                       
        self.setBackGround()
        self.setHats()        
        
        if self.shadows:
            MsgBox('Adding Shadows,  please wait...', int(1 + (self.hats * .25)))
            self.addShadows()
                   
        QTimer.singleShot(200, self.scroller.anime.start)  ## run scrolling background  
        self.run()  
        self.showWorks.disablePlay()

### --------------------------------------------------------            
    def setBackGround(self):
        if self.scroller != None:
            self.scroller.init()
        else:
            self.scroller = BkgItem(paths['demo'] + 'abstract.jpg', self.canvas)
   
        self.scroller.direction = self.direction       
        self.scroller.tag = 'scroller'
        self.scroller.mirroring = True      
        self.scroller.bkgWorks.addTracker(self.scroller)  

        self.scroller.anime = self.scroller.setScrollerPath(self.scroller, 'first')  
  
        if self.direction == 'right':
            self.scroller.setPos(QPointF(self.scroller.runway, 0))  ## offset to right    
  
        self.scroller.addedScroller == False   
        self.scroller.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)        
        self.scene.addItem(self.scroller)  
  
    def setHats(self): 
        apaths = getPathList()  ## from sideGig  
        if apaths == []:
            MsgBox('getPathList: No Paths Found!', 5)
            QTimer.singleShot(200, self.canvas.clear)     
            return 
        for i in range(self.hats):  
            path = getPath(apaths)                                           
            self.makeHats(path)
  
    def makeHats(self, path):      
        if not os.path.exists(paths['spritePath'] + 'doral.png'):
            return   
        pathStr = paths['spritePath'] + 'doral.png'
        pix = PixItem(pathStr, self.canvas.pixCount, 0, 0, self.canvas)        
        pix.x = random.randrange(200, common['ViewW']-300)
        pix.y = random.randrange(200, common['ViewH']-300)
        pix.setPos(pix.x, pix.y)  
        pix.setScale(1.0)   
        pix.tag = path    
        if pix.shadowMaker.isActive == True:
            self.shadows = True
            pix.setOpacity(0.001) 
        self.scene.addItem(pix)
           
### --------------------------------------------------------             
    def addShadows(self):  ## add shadows after adding pixitems     
        tasks = []        
        start = time.time()
        loop  = asyncio.new_event_loop() 
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.shadowMaker.isActive == True: 
                tasks.append(loop.create_task(self.newShadow(pix))) 
        if len(tasks) > 0:
            loop.run_until_complete(asyncio.wait(tasks))
        loop.close()  
        self.dots.statusBar.showMessage(
            f"Number of Shadows: {len(tasks)}   seconds: {time.time() - start:.2f}", 10000)                            
 
    async def newShadow(self, pix): 
        pix.addShadow() 
        pix.shadowMaker.shadow.setPos(self.setXY(), self.setXY())
        pix.shadowMaker.shadow.setParentItem(pix) 
              
    def setXY(self):
        return random.randint(-7,7)*5
           
 ## --------------------------------------------------------         
    def run(self): 
        k = 0  
        for pix in self.scene.items():
            if pix.type =='pix' and 'doral' in pix.fileName:
                node = Anime.Node(pix)  ## get pix pos property 
                sync   = random.randint(11,16) * 1000  ## duration   
                waypts = pathLoader(pix.tag)
                pix.anime = pathAnimator(node, sync, waypts)  ## set path animation 
                QTimer.singleShot(100 + (k * 60), pix.anime.start)
                k += 1
       
### --------------------------------------------------------                                                
    def rerunAbstract(self, direction):       
        clearPaths(self)
        self.delHats() 
        self.scroller.bkgWorks.delTracker(self.scroller) 
        self.makeAbstracts(direction) 
      
    def delHats(self):
        if len(self.scene.items()) > 0:
            for pix in self.scene.items():      
                if pix.type == 'pix' and 'doral' in pix.fileName:
                    self.scene.removeItem(pix)
                    del pix
                elif pix.type == 'bkg':
                    self.scene.removeItem(pix)
                    del pix
                    
### -------------------------------------------------------- 
def clearPaths(self):  
    self.mapper.clearTagGroup()
    self.mapper.clearPaths()    
  
def getPath(apaths):
    plist  = ['twigs.path', 'demo-', 'black-forest']  ## reject these paths
    random.shuffle(apaths) 
    for p in apaths:                 
        if any(ele in p for ele in plist): 
            continue   
        return os.path.basename(p)
         
### ------------------- dotsAbstractBats -------------------


