
import os
import random

from PyQt6.QtCore       import QPointF, QPropertyAnimation, QEasingCurve, \
                                QParallelAnimationGroup
from PyQt6.QtGui        import QPainterPath
from PyQt6.QtWidgets    import QGraphicsPixmapItem

from dotsShared         import paths, common
from dotsSideCar        import PixItem 
from dotsSideGig        import *

### ---------------------- dotsSidePath --------------------
''' dotsPaths is used by storyboard, sideshow, animations, 
    pathmaker and contains Wings, demo, setPath, pathLoader.
    Mostly all of the original demo is here
### --------------------------------------------------------
    Things to know about wings. They're brittle, don't pull on them.
    Use the bat portion to move the bat - the pivot sprite and the wing 
    are in the images folder. Main thing to know, if you need to move 
    or change an animation - do so, save it, clear and reload.
    They're still brittle but it works, even better now. '''
### --------------------------------------------------------
class Wings:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent    
        self.scene  = self.canvas.scene
        
### --------------------------------------------------------
    def bats(self, x, y, tag):  ## was wings 
        self.canvas.pixCount += 1         
        pivot = PixItem(paths['imagePath'] + 'bat-pivot.png', 
            self.canvas.pixCount,
            x, y,  
            self.canvas
        ) 
        pivot.part = 'pivot' 
        pivot.tag  = tag
        pivot.setZValue(pivot.zValue() + 200)
        pivot.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, True) 
        ''' magic numbers warning - results will vary - seems
            to be working for bat wings if loaded using file chooser''' 
                      
        half = pivot.width/2     ## looking better
        height = pivot.height/5  ## good guess, close
        
        try:
            ## another correction -5 for y
            # pivot.setPos(pivot.x - half, pivot.y - height - 5)
            pivot.setScale(.57)
            pivot.setOriginPt() 
        except IOError:
            pass  
          
        self.canvas.pixCount += 1
        rightWing = PixItem(paths['imagePath'] + 'bat-wings.png', 
            self.canvas.pixCount,
            x-20, y-20, 
            self.canvas,
            False,
        )  ## flop it
 
        rightWing.part = 'right'
        rightWing.tag  = 'Flapper'  ## applies this animation when run
        rightWing.setZValue(rightWing.zValue() + 200)  ## reset wing zvals
        rightWing.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, False)
        rightWing.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemStacksBehindParent)
              
        self.canvas.pixCount += 1
        leftWing = PixItem(paths['imagePath'] + 'bat-wings.png', 
            self.canvas.pixCount,
            x + rightWing.width, y, 
            self.canvas,
            True
        )  ## flop it

        leftWing.part = 'left'
        leftWing.tag  = 'Flapper'
        leftWing.setZValue(leftWing.zValue() + 200)
        leftWing.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, False) 
        leftWing.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemStacksBehindParent)
       
        ## center wings around pivot
        rightWing.setPos(half+1, height-2)
        leftWing.setPos(-leftWing.width+(half+5), height)

        ''' if there's a better way to bind these I'd like to know '''
        rightWing.setParentItem(pivot)  
        leftWing.setParentItem(pivot)

        self.scene.addItem(pivot) 
        
### --------------------------------------------------------
def flapper(pix, anime, node):  ## used by demo bat wings        
    baseName = os.path.basename(pix.fileName)

    if pix.part == 'right':
        node.pix.setTransformOriginPoint(QPointF(pix.width*0.25, pix.height*0.65))
        rot = 25.0
    else:
        rot = -25.0
        node.pix.setTransformOriginPoint(QPointF(pix.width*0.75, pix.height*0.65))

    rotate = QPropertyAnimation(node, b'rotate')
    rotate.setDuration(1200)  ## bats

    if 'bat' in baseName:
        rotate.setDuration(300)

    rotate.setStartValue(node.pix.rotation)
    rotate.setKeyValueAt(0.50, rot+pix.rotation)
    rotate.setEndValue(node.pix.rotation)
    rotate.setEasingCurve(QEasingCurve.Type.Linear)

    rotate.setLoopCount(-1) 

    return rotate
    
### --------------------------------------------------------  
def demo(pix, anime, node):  ## sets the demo path         
    sync = 11000

    waypts = pathLoader(anime)
    if not waypts: return
    ## offset for origin pt - setOrigin wasn't working
    pt = getOffSet(node.pix)

    path = QPropertyAnimation(node, b'pos')
    path.setDuration(int(sync))
    path.setStartValue(waypts.pointAtPercent(0.0)-pt)
    for i in range(1, 99):    
        path.setKeyValueAt(i/100.0, waypts.pointAtPercent(i/100.0)-pt)
    path.setEndValue(waypts.pointAtPercent(1.0)-pt)  
    path.setLoopCount(-1) 

    rotate = QPropertyAnimation(node, b'rotate')
    rotate.setDuration(int(sync/3))
    rotate.setEasingCurve(QEasingCurve.Type.InBounce)
    rotate.setStartValue(node.pix.rotation)    
    rotate.setKeyValueAt(0.25, pix.rotation-45)
    rotate.setKeyValueAt(0.50, pix.rotation)
    rotate.setKeyValueAt(0.75, pix.rotation+45)
    rotate.setEndValue(node.pix.rotation)
    rotate.setEasingCurve(QEasingCurve.Type.OutBounce)
    rotate.setLoopCount(-1)

    opacity = QPropertyAnimation(node, b'opacity')
    opacity.setDuration(int(sync))
    opacity.setStartValue(node.pix.opacity())
    opacity.setKeyValueAt(.20, 1.0) 
    opacity.setKeyValueAt(.53, 1.0)
    opacity.setKeyValueAt(.56, 0.0)
    opacity.setKeyValueAt(.73, 0.0)
    opacity.setKeyValueAt(.75, .70)
    opacity.setKeyValueAt(.85, .95)
    opacity.setEndValue(node.pix.opacity())
    opacity.setLoopCount(-1)

    scale = QPropertyAnimation(node, b'scale')
    scale.setDuration(int(sync))
    scale.setStartValue(node.pix.scale*1.05)
    scale.setKeyValueAt(.45, pix.scale*.80)
    scale.setKeyValueAt(.53, pix.scale*.25)
    scale.setKeyValueAt(.56, pix.scale*0.0)
    scale.setKeyValueAt(.75, pix.scale*.25)
    scale.setKeyValueAt(.80, pix.scale*.50)
    scale.setKeyValueAt(.85, pix.scale*.65)
    scale.setKeyValueAt(.90, pix.scale*.80)
    scale.setKeyValueAt(.95, pix.scale*.90)
    scale.setEndValue(node.pix.scale*1.05)
    scale.setLoopCount(-1)

    group = QParallelAnimationGroup()
    group.addAnimation(path)
    group.addAnimation(rotate)
    group.addAnimation(scale)
    group.addAnimation(opacity)

    group.setLoopCount(-1)

    return group

### --------------------------------------------------------
def setPaths(tag, node):  ## called by setAnimation, one at a time        
    waypts = pathLoader(tag)  
    if not waypts: 
        return 
    sync = random.randint(118,179) * 100  ## very arbitrary   
    k = random.randint(55,105) % 5  ## just to make things interesting
    if k == 0: 
        waypts = waypts.toReversed()
    return pathWorks(node, sync, waypts)  ## shared

### --------------------------------------------------------
def pathWorks(node, sync, wpts):         
    path = QPropertyAnimation(node, b'pos')  
    pt = getOffSet(node.pix)  
    path.setDuration(sync)  
    
    path.setStartValue(wpts.pointAtPercent(0.0)-pt)
    for i in range(1, 99):    
        path.setKeyValueAt(i/100.0, wpts.pointAtPercent(i/100.0)-pt)
    path.setEndValue(wpts.pointAtPercent(1.0)-pt)

    path.setLoopCount(-1)
    return path 
      
### --------------------------------------------------------
def pathLoader(path):  ## also by MapItem
    file = paths['paths'] + path 
    try:
        scaleX, scaleY = 1.0, 1.0 
        path = QPainterPath()
        if 'demo-' not in file:         ## apply scaleX, scaleY from screens
            scaleX = common['scaleX']  ## this does not actually scale but it's enough
            scaleY = common['scaleY'] 
        with open(file, 'r') as fp:
            for line in fp:
                ln = line.rstrip()  
                ln = list(map(float, ln.split(',')))
                ln[0] = ln[0] * scaleX
                ln[1] = ln[1] * scaleY
                if not path.elementCount():
                    path.moveTo(QPointF(ln[0], ln[1]))
                path.lineTo(QPointF(ln[0], ln[1])) 
        path.closeSubpath()
        return path
    except IOError:
        MsgBox('pathLoader: Error loading path file, ' + os.path.basename(file), 5)
        return None

### ---------------------- dotsSidePath --------------------



