
import random

from PyQt6.QtCore   import QPointF, pyqtProperty, QPropertyAnimation, \
                        QParallelAnimationGroup, QSequentialAnimationGroup, \
                        QEasingCurve, QObject

from dotsShared     import common

import dotsSidePath as sidePath

AnimeList = ['Vibrate', 'Pulse','Bobble','Idle']
OneOffs   = ['Rain','Spin Left','Spin Right','Stage Left','Stage Right']
Stages    = ('Stage Left', 'Stage Right')
Spins     = ('Spin Left', 'Spin Right')

AnimeList += OneOffs

### -------------------- dotsAnimation ---------------------
''' classes: Node, Animation. Many basic animations '''
### --------------------------------------------------------
class Node(QObject):
### --------------------------------------------------------
    def __init__(self, pix):
        super().__init__()
        
        self.pix = pix

    def _setPos(self, pos):
        try:
            self.pix.setPos(pos)
        except RuntimeError:
            return None

    def _setOpacity(self, opacity):
        try:
            self.pix.setOpacity(opacity)
        except RuntimeError:
            return None

    def _setScale(self, scale):
        try:     
            self.pix.setScale(scale)
        except RuntimeError:
            return None

    def _setRotate(self, rotate):
        try:
            self.pix.setRotation(rotate)
        except RuntimeError:
            return None

    pos =  pyqtProperty(QPointF, fset=_setPos)
    scale =  pyqtProperty(float, fset=_setScale) 
    rotate =  pyqtProperty(int, fset=_setRotate) 
    opacity =  pyqtProperty(float, fset=_setOpacity)

### -------------------------------------------------------- 
class Animation:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()

        self.canvas = parent 
    
        self.singleFunctions = {  ## values are objects 
            'Vibrate':  vibrate,  
            'Pulse':    pulse,
            'Bobble':   bobble,
            'Idle':     idle,
        }

### --------------------------------------------------------
    def setAnimation(self, anime, pix):
        ## pathList comes from self.canvas.pathList
        ## this function returns an animation to a pixitem
        if anime == 'Random':
            anime = self._random()   ## add the animation type to the tag
            pix.tag = pix.tag + ':' + anime 

        if anime in self.singleFunctions:  ## thanks again to Martin
            fn = self.singleFunctions[anime]  ## objects passed as functions
            return fn(pix)

        if anime == 'Rain':
            return rain(pix)
        
        elif anime in Stages:
            return stage(pix, anime)
                
        elif anime in Spins:
            return spin(pix, anime)
        
        elif anime == 'Flapper':  ## bat wings
            return sidePath.flapper(pix)
         
        elif 'demo' in anime:  ## from BatsAndHats
            return sidePath.demo(pix, anime)
        
        elif anime in self.canvas.pathList:
            return sidePath.setPaths(anime, pix)

### --------------------------------------------------------
    def _random(self):  
        random.seed()
        r = AnimeList + self.canvas.pathList 
        return r[random.randint(0,len(r)-1)]

### --------------------------------------------------------
def vibrate(pix):  
    pos = pix.pos()
    pix.setOriginPt()  
    pix.node = Node(pix)
 
    random.seed()
    sync = random.randint(130,205)
    ran  = random.randint(3,7)*2

    vibrate = QPropertyAnimation(pix.node, b'pos')
    vibrate.setDuration(int(sync))

    vibrate.setStartValue(pos)
    vibrate.setKeyValueAt(0.25, pos + QPointF(-ran, ran))  
    vibrate.setKeyValueAt(0.25, pos + QPointF(ran*1.75, ran*1.25))     
    vibrate.setKeyValueAt(0.25, pos + QPointF(-ran*1.75, -ran*1.25))              
    vibrate.setKeyValueAt(0.25, pos + QPointF(-ran, ran))      
    vibrate.setEndValue(pos)

    vibrate.setLoopCount(-1)
    vibrate.setEasingCurve(QEasingCurve.Type.InOutBack)
    
    group = QParallelAnimationGroup()
    group.addAnimation(vibrate)

    return group

### --------------------------------------------------------
def pulse(pix):   
    pix.setOriginPt()  
    pix.node = Node(pix)
  
    random.seed()
    sync = random.gauss(450, 50)

    pulse = QPropertyAnimation(pix.node, b'scale')
    pulse.setDuration(int(sync))

    pulse.setStartValue(pix.scale * random.gauss(1.25, .25))
    pulse.setEndValue(pix.scale * random.gauss(1.25, .25))

    pulse.setLoopCount(-1)

    seq = QSequentialAnimationGroup()
    seq.addAnimation(pulse)
    seq.addPause(random.randint(10,30) * 30)
  
    return seq
 
### --------------------------------------------------------
def bobble(pix):  
    pos = pix.pos()
    pix.setOriginPt()  
    pix.node = Node(pix)

    sync = random.randint(4,9) * 400
    up   = random.randint(5, 12)
    left = random.randint(5, 9)

    if random.randint(0, 1): up = up * -1
    if random.randint(0, 1): left = left * -1

    bobble = QPropertyAnimation(pix.node, b'pos')
    bobble.setDuration(int(sync))
  
    bobble.setStartValue(pos)
    bobble.setKeyValueAt(0.25, pos + QPointF(-left, -up*1.75))  
    bobble.setKeyValueAt(0.35, pos + QPointF(-left*1.35, 0))              
    bobble.setKeyValueAt(0.45, pos + QPointF(0, up*1.65))  
    bobble.setKeyValueAt(0.55, pos + QPointF(left*1.35, 0))
    bobble.setKeyValueAt(0.65, pos + QPointF(left, -up*1.75))       
    bobble.setEndValue(pos)

    bobble.setLoopCount(-1)
    bobble.setEasingCurve(QEasingCurve.Type.InOutCubic)
    
    group = QParallelAnimationGroup()
    group.addAnimation(bobble)

    return group

### --------------------------------------------------------
def fin(pix):  ## delete pixitem 
    pix.setOriginPt()  
    pix.node = Node(pix)

    sync = random.randint(6,10) * 75
    rot = 270 
    
    if not random.randint(0,1): rot = -270
    
    rotate = QPropertyAnimation(pix.node, b'rotate')
    rotate.setDuration(int(sync))
    rotate.setStartValue(pix.rotation)
    rotate.setEndValue(rot+pix.rotation)

    opacity = QPropertyAnimation(pix.node, b'opacity')  ## fade out
    opacity.setDuration(int(sync))
    opacity.setStartValue(pix.opacity())
    opacity.setEndValue(0)

    scale = QPropertyAnimation(pix.node, b'scale')
    scale.setDuration(int(sync))
        
    scale.setStartValue(pix.scale)
    scale.setEndValue(pix.scale*.25)

    group = QParallelAnimationGroup()

    group.addAnimation(rotate)
    group.addAnimation(opacity)
    group.addAnimation(scale)

    group.setLoopCount(1)

    return group

### --------------------------------------------------------
def reprise(pix):  ## reposition pixitems to starting x,y, etc.
    pix.setOriginPt()  
    pix.node = Node(pix)
    
    sync = 1000

    if pix.type == 'pix' and  pix.part in ('left','right'): 
        return
        
    reprise = QPropertyAnimation(pix.node, b'pos') 
    reprise.setDuration(int(sync))
    reprise.setStartValue(pix.pos())
    reprise.setEndValue(QPointF(pix.x, pix.y))
    
    if pix.type == 'pix' and pix.part == "pivot":
        return reprise

    spin = QPropertyAnimation(pix.node, b'rotate')
    spin.setDuration(int(sync))
    spin.setStartValue(pix.rotation)
    spin.setKeyValueAt(0.50, pix.rotation+random.randint(15, 45))
    spin.setEndValue(pix.rotation)

    scale = QPropertyAnimation(pix.node, b'scale')
    scale.setDuration(int(sync))
                  
    scale.setStartValue(pix.scale)
    if pix.canvas.openPlayFile == 'hats' and \
        pix.shadowMaker.isActive == True:
        scale.setEndValue(1.0)   
    else:    
        scale.setEndValue(pix.scale)

    opacity = QPropertyAnimation(pix.node, b'opacity')
    opacity.setDuration(int(sync))
    opacity.setStartValue(pix.opacity())  ## reset to 1.0
    
    if pix.canvas.openPlayFile == 'hats' and \
        pix.shadowMaker.isActive == True:
        opacity.setEndValue(.001)
    else:
        opacity.setEndValue(pix.opacity())
        
    group = QParallelAnimationGroup()

    group.addAnimation(reprise)
    group.addAnimation(spin)
    group.addAnimation(scale)  
    group.addAnimation(opacity)     

    return group

### --------------------------------------------------------
def idle(pix):      
    pix.setOriginPt()  
    pix.node = Node(pix)
    
    pos  = pix.pos()
    sync = 1000

    idle = QPropertyAnimation(pix.node, b'pos')
    idle.setDuration(int(sync))
    idle.setStartValue(pos)
    idle.setEndValue(pos)

    idle.setLoopCount(-1)
    
    group = QParallelAnimationGroup()
    group.addAnimation(idle)

    return group

### --------------------------------------------------------
def stage(pix, which):  ## left or right      
    pos = pix.pos()
    pix.setOriginPt()
    pix.node = Node(pix)
              
    x = int(pos.x())
    ViewW = common["ViewW"]

    left = x+pix.width*3
    right = ViewW+pix.width*3

    if which.endswith('Left'):
        stage1, stage2 = stageLeft(pix.node, pos, left, right)
    else:
        stage1, stage2 = stageRight(pix.node, pos, left, right)
   
    stage = QSequentialAnimationGroup()
    stage.addAnimation(stage1)
    stage.addAnimation(stage2)

    stage.setLoopCount(-1) 

    return stage

### --------------------------------------------------------
def stageLeft(node, pos, left, right):    
    stage1 = QPropertyAnimation(node, b'pos')
    stage1.setDuration(random.randint(16, 23) * 110)
    val = (random.randint(7, 13) * 5) / 125
    stage1.setStartValue(pos)
    stage1.setKeyValueAt(val, pos + QPointF(-left/2, 0))
    stage1.setEndValue(pos + QPointF(-left, 0))

    stage2 = QPropertyAnimation(node, b'pos')
    stage2.setDuration(random.randint(16, 23) * 100)
    val = (random.randint(7, 13) * 5) / 125
    stage2.setStartValue(QPointF(right, 0))
    stage2.setKeyValueAt(val, pos + QPointF(right/2, 0))
    stage2.setEndValue(pos) 
    
    return stage1, stage2

### --------------------------------------------------------
def stageRight(node, pos, left, right):   
    stage1 = QPropertyAnimation(node, b'pos')
    stage1.setDuration(random.randint(14, 23) * 75)
    val = (random.randint(7, 13) * 5) / 100
    stage1.setStartValue(pos)
    stage1.setKeyValueAt(val, pos + QPointF(right/2, 0))
    stage1.setEndValue(pos + QPointF(right, 0))

    stage2 = QPropertyAnimation(node, b'pos')
    stage2.setDuration(random.randint(14, 23) * 75)
    val = (random.randint(7, 13) * 5) / 100
    stage2.setStartValue(pos + QPointF(-left, 0))
    stage2.setKeyValueAt(val, pos + QPointF(-left/2, 0))
    stage2.setEndValue(pos)

    return stage1, stage2

### --------------------------------------------------------
def spin(pix, anime):  ## rotate
    pix.setOriginPt()  
    pix.node = Node(pix)
   
    sync = random.randint(14, 23) * 50
    rot  = 360 

    if anime.endswith('Left'): rot = -360

    spin = QPropertyAnimation(pix.node, b'rotate')
    
    spin.setDuration(int(sync))
    spin.setStartValue(pix.rotation)
    spin.setEndValue(pix.rotation+rot)

    spin.setLoopCount(-1)  
    
    group = QParallelAnimationGroup()
    group.addAnimation(spin)

    return group

### --------------------------------------------------------
def rain(pix):      
    pos = pix.pos()
    pix.setOriginPt()  
    pix.node = Node(pix)

    sync = random.randint(17, 31) * 50

    y = int(pos.y())
    ViewH  = common["ViewH"]
    bottom = y+ViewH+pix.height*2
    top    = y+pix.height*2

    rain1 = QPropertyAnimation(pix.node, b'pos')
    rain1.setDuration(int(sync))
    rain1.setStartValue(pos)
    rain1.setEndValue(pos+QPointF(0, bottom))

    opacity1 = QPropertyAnimation(pix.node, b'opacity')
    opacity1.setDuration(int(sync))
    opacity1.setStartValue(pix.opacity())
    opacity1.setKeyValueAt(.10, .50)
    opacity1.setEndValue(0)

    par1 = QParallelAnimationGroup()
    par1.addAnimation(rain1)
    par1.addAnimation(opacity1)

    rain2 = QPropertyAnimation(pix.node, b'pos')
    rain2.setDuration(int(sync))
    rain2.setStartValue(pos+QPointF(0, -top))
    rain2.setEndValue(pos)

    opacity2 = QPropertyAnimation(pix.node, b'opacity')
    opacity2.setDuration(int(sync))
    opacity2.setStartValue(pix.opacity())
    opacity2.setEndValue(.85)

    par2 = QParallelAnimationGroup()
    par2.addAnimation(rain2)
    par2.addAnimation(opacity2)

    rain = QSequentialAnimationGroup()
    rain.addAnimation(par1)
    rain.addAnimation(par2)

    rain.setLoopCount(-1)  

    return rain

### -------------------- dotsAnimation ---------------------

