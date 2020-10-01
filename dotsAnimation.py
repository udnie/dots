import sys
import random
import time

from PyQt5.QtCore  import *
from PyQt5.QtGui   import *

from dotsShared    import common, paths
from dotsSideCar   import MsgBox

animeList = ['Vibrate', 'Pulse','Bobble','Idle','Rain','Spin Left',
        'Spin Right','Stage Left','Stage Right']

pathList = ['11.path', 'a-12.path', 'ort.path']

### -------------------- dotsAnimation ---------------------
''' dotsAnimation: contains many the dotsFx basic animations,
    pathLoader and the Node class - just like in java '''
### --------------------------------------------------------
class Node(QObject):

    def __init__(self, pix):
        super().__init__()
        
        self.pix = pix

    def _setPos(self, pos):
        self.pix.setPos(pos)

    def _setOpacity(self, opacity):
        self.pix.setOpacity(opacity)

    def _setScale(self, scale):
        self.pix.setScale(scale)

    def _setRotate(self, rotate):
        self.pix.setRotation(rotate)

    pos = pyqtProperty(QPointF, fset=_setPos)
    scale = pyqtProperty(float, fset=_setScale) 
    rotate = pyqtProperty(int, fset=_setRotate) 
    opacity = pyqtProperty(float, fset=_setOpacity) 


### --------------------------------------------------------

def setAnimation(anime, pix):
    if anime == 'Random':
        anime = _random()
        pix.tag = pix.tag + ',' + anime
    
    _animation_operations = {
    'Vibrate': vibrate,
    'Pulse': pulse,
    'Bobble': bobble,
    'Idle': idle,
    'Reprise': reprise
}

    if anime in _animation_operations:
        fn = _animation_operations[anime]
        return fn(pix)

    if anime == 'Rain':
        return rain(pix, Node(pix))
    if anime in ['Stage Left', 'Stage Right']:
        return stage(pix, anime)
    if anime in ['Spin Left', 'Spin Right']:
        return spin(pix, anime, Node(pix))

    if anime in pathList:
        return setPaths(pix, anime, Node(pix))

### --------------------------------------------------------
def _random():  
    random.seed()
    r = animeList + pathList
    r = r[random.randint(0,len(r)-1)]
    return r

### --------------------------------------------------------
def vibrate(pix):  
    node = Node(pix)
    pos  = node.pix.pos()
    node.pix.setOriginPt()

    random.seed()
    sync = random.randint(130,205)
    ran  = random.randint(3,7)*2

    vibrate = QPropertyAnimation(node, b'pos')
    vibrate.setDuration(sync)

    vibrate.setStartValue(pos)
    vibrate.setKeyValueAt(0.25, pos + QPointF(-ran, ran))  
    vibrate.setKeyValueAt(0.25, pos + QPointF(ran*1.75, ran*1.25))     
    vibrate.setKeyValueAt(0.25, pos + QPointF(-ran*1.75, -ran*1.25))              
    vibrate.setKeyValueAt(0.25, pos + QPointF(-ran, ran))      
    vibrate.setEndValue(pos)

    vibrate.setLoopCount(-1)
    vibrate.setEasingCurve(QEasingCurve.InOutBack)

    return vibrate

### --------------------------------------------------------
def pulse(pix):   
    node = Node(pix)
    node.pix.setOriginPt()
    random.seed()
    sync = random.gauss(450, 50)

    pulse = QPropertyAnimation(node, b'scale')
    pulse.setDuration(sync)

    pulse.setStartValue(node.pix.scale * random.gauss(1.25, .25))
    pulse.setEndValue(node.pix.scale * random.gauss(1.25, .25))

    pulse.setLoopCount(-1)

    seq = QSequentialAnimationGroup()
    seq.addAnimation(pulse)
    seq.addPause(random.randint(10,30) * 30)
  
    return seq
 
### --------------------------------------------------------
def bobble(pix):   
    node = Node(pix)
    pos = node.pix.pos()
    node.pix.setOriginPt()

    sync = random.randint(4,9) * 400
    up   = random.randint(5, 12)
    left = random.randint(5, 9)

    if random.randint(0, 1): up = up * -1
    if random.randint(0, 1): left = left * -1

    bobble = QPropertyAnimation(node, b'pos')
    bobble.setDuration(sync)
  
    bobble.setStartValue(pos)
    bobble.setKeyValueAt(0.25, pos + QPointF(-left, -up*1.75))  
    bobble.setKeyValueAt(0.35, pos + QPointF(-left*1.35, 0))              
    bobble.setKeyValueAt(0.45, pos + QPointF(0, up*1.65))  
    bobble.setKeyValueAt(0.55, pos + QPointF(left*1.35, 0))
    bobble.setKeyValueAt(0.65, pos + QPointF(left, -up*1.75))       
    bobble.setEndValue(pos)

    bobble.setLoopCount(-1)
    bobble.setEasingCurve(QEasingCurve.InOutCubic)

    return bobble

### --------------------------------------------------------
def fin(pix):            ## delete pixitem 
    node = Node(pix)
    node.pix.setOriginPt()
    sync = random.randint(6,10) * 75
    rot = 270 
    if not random.randint(0,1): rot = -270

    rotate = QPropertyAnimation(node, b'rotate')
    rotate.setDuration(sync)
    rotate.setStartValue(node.pix.rotation)
    rotate.setEndValue(rot+node.pix.rotation)

    opacity = QPropertyAnimation(node, b'opacity')
    opacity.setDuration(sync)
    opacity.setStartValue(node.pix.opacity())
    opacity.setEndValue(0)

    scale = QPropertyAnimation(node, b'scale')
    scale.setDuration(sync)
    scale.setStartValue(node.pix.scale)
    scale.setEndValue(node.pix.scale*.25)

    group = QParallelAnimationGroup()

    group.addAnimation(rotate)
    group.addAnimation(opacity)
    group.addAnimation(scale)

    group.setLoopCount(1)

    return group

### --------------------------------------------------------
def reprise(pix):  ## reposition pixitems to starting x,y, etc.
    node = Node(pix)
    node.pix.setOriginPt()
    sync = 1000

    reprise = QPropertyAnimation(node, b'pos') 
    reprise.setDuration(sync)
    reprise.setStartValue(node.pix.pos())
    reprise.setEndValue(QPointF(pix.x, pix.y))

    spin = QPropertyAnimation(node, b'rotate')
    spin.setDuration(sync)
    spin.setStartValue(node.pix.rotation)
    spin.setKeyValueAt(0.50, pix.rotation+random.randint(15, 45))
    spin.setEndValue(pix.rotation)

    scale = QPropertyAnimation(node, b'scale')
    scale.setDuration(sync)
    scale.setStartValue(node.pix.scale)
    scale.setEndValue(pix.scale)

    opacity = QPropertyAnimation(node, b'opacity')
    opacity.setDuration(sync)
    opacity.setStartValue(node.pix.opacity())
    opacity.setEndValue(1)

    group = QParallelAnimationGroup()

    group.addAnimation(reprise)
    group.addAnimation(spin)
    group.addAnimation(scale)  
    group.addAnimation(opacity)     

    return group

### --------------------------------------------------------
def idle(pix):           
    node = Node(pix)
    pos  = node.pix.pos()
    sync = 1000

    idle = QPropertyAnimation(node, b'pos')
    idle.setDuration(sync)
    idle.setStartValue(pos)
    idle.setEndValue(pos)

    idle.setLoopCount(-1)

    return idle
  
### --------------------------------------------------------
def stage(pix, which):           
    node = Node(pix)    
    pos  = node.pix.pos()
    node.pix.setOriginPt()    

    x = int(pos.x())
    viewW = common["viewW"]
    left = x+node.pix.width*3
    right = viewW+node.pix.width*3

    if which.endswith('Left'):
        stage1, stage2 = self._stage_left(node, pos, left, right)
    else:
        stage1, stage2 = self._stage_right(node, pos, left, right)

    stage = QSequentialAnimationGroup()
    stage.addAnimation(stage1)
    stage.addAnimation(stage2)

    stage.setLoopCount(-1)

    return stage

def _stage_left(node, pos, left, right):
    stage1 = QPropertyAnimation(node, b'pos')
    stage1.setDuration(random.randint(14, 23) * 75)
    val = (random.randint(7, 13) * 5) / 100
    stage1.setStartValue(pos)
    stage1.setKeyValueAt(val, pos + QPointF(-left/2, 0))
    stage1.setEndValue(pos + QPointF(-left, 0))

    stage2 = QPropertyAnimation(node, b'pos')
    stage2.setDuration(random.randint(14, 23) * 75)
    val = (random.randint(7, 13) * 5) / 100
    stage2.setStartValue(QPointF(right, 0))
    stage2.setKeyValueAt(val, pos + QPointF(right/2, 0))
    stage2.setEndValue(pos) 
    
    return stage1, stage2

def _stage_right(node, pos, left, right):
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

def spin(pix, anime, node):           
    node.pix.setOriginPt()

    sync = random.randint(14, 23) * 50
    rot  = 360 
    if anime.endswith('Left'): rot = -360

    spin = QPropertyAnimation(node, b'rotate')
    spin.setDuration(sync)
    spin.setStartValue(node.pix.rotation)
    spin.setEndValue(node.pix.rotation+rot)

    spin.setLoopCount(-1)  

    return spin

### --------------------------------------------------------
def rain(pix, node):           
    node.pix.setOriginPt()
    pos  = node.pix.pos()
    sync = random.randint(17, 31) * 50

    y = int(pos.y())
    viewH  = common["viewH"]
    bottom = y+viewH+node.pix.height*2
    top    = y+node.pix.height*2

    rain1 = QPropertyAnimation(node, b'pos')
    rain1.setDuration(sync)
    rain1.setStartValue(pos)
    rain1.setEndValue(pos+QPointF(0, bottom))

    opacity1 = QPropertyAnimation(node, b'opacity')
    opacity1.setDuration(sync)
    opacity1.setStartValue(node.pix.opacity())
    opacity1.setKeyValueAt(.10, .50)
    opacity1.setEndValue(0)

    par1 = QParallelAnimationGroup()
    par1.addAnimation(rain1)
    par1.addAnimation(opacity1)

    rain2 = QPropertyAnimation(node, b'pos')
    rain2.setDuration(sync)
    rain2.setStartValue(pos+QPointF(0, -top))
    rain2.setEndValue(pos)

    opacity2 = QPropertyAnimation(node, b'opacity')
    opacity2.setDuration(sync)
    opacity2.setStartValue(node.pix.opacity())
    opacity2.setEndValue(.85)

    par2 = QParallelAnimationGroup()
    par2.addAnimation(rain2)
    par2.addAnimation(opacity2)

    rain = QSequentialAnimationGroup()
    rain.addAnimation(par1)
    rain.addAnimation(par2)

    rain.setLoopCount(-1)  

    return rain

### --------------------------------------------------------
def setPaths(pix, anime, node):           
    node.pix.setOriginPt()
    pos  = node.pix.pos()
    sync = random.randint(73,173) * 100  ## very arbitrary

    path = QPropertyAnimation(node, b'pos')
    path.setDuration(sync)

    waypts = pathLoader(anime)
    if not waypts: return
    ## offset needed for paths for this setup
    waypts.translate(-165.0,-65.0)

    path.setStartValue(waypts.pointAtPercent(0.0)) 
    for i in range(1, 99):    
        path.setKeyValueAt(i/100.0, waypts.pointAtPercent(i/100.0))
    path.setEndValue(waypts.pointAtPercent(1.0))  
    path.setLoopCount(-1) 

    return path
    
### --------------------------------------------------------
def pathLoader(anime):
    file = paths["paths"] + anime  ## includes '.path'
    try:
        poly = QPainterPath()
        # file = paths["paths"] + anime  
        with open(file, 'r') as fp:
            for line in fp:
                ln = line.rstrip()
                ln = list(map(float, ln.split(',')))
                if not poly.elementCount():
                    poly.moveTo(QPointF(ln[0], ln[1]))
                poly.lineTo(QPointF(ln[0], ln[1]))

        poly.closeSubpath()
        return poly
    except IOError:
        MsgBox("Error loading path file")

### -------------------- dotsAnimation ---------------------
