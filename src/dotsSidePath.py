
import os
import random

from PyQt6.QtCore       import QPointF, QPropertyAnimation, QEasingCurve, \
                                QParallelAnimationGroup
from PyQt6.QtGui        import QPainterPath

from dotsShared         import paths, common
from dotsSideGig        import MsgBox, DemoAvailable
from dotsAnimation      import Node

### ---------------------- dotsSidePath --------------------
''' dotsSidePath is used by storyboard, showbiz, animations, 
    pathmaker and contains flapper, demo, setPath, pathLoader.
    Mostly all of the original demo is here '''
### --------------------------------------------------------
def flapper(pix):  ## used by demo bat wings  
    baseName = os.path.basename(pix.fileName)
    
    pix.setOriginPt()  
    pix.node = Node(pix)
    
    if pix.part == 'right':
        pix.setTransformOriginPoint(QPointF(pix.width*0.25, pix.height*0.65))
        rot = 25.0
    else:
        rot = -25.0
        pix.setTransformOriginPoint(QPointF(pix.width*0.75, pix.height*0.65))

    rotate = QPropertyAnimation(pix.node, b'rotate')
    rotate.setDuration(1200)  ## bats

    if 'bat' in baseName:
        rotate.setDuration(300)

    rotate.setStartValue(pix.rotation)
    rotate.setKeyValueAt(0.50, rot+pix.rotation)
    rotate.setEndValue(pix.rotation)
    rotate.setEasingCurve(QEasingCurve.Type.Linear)

    rotate.setLoopCount(-1) 
    
    group = QParallelAnimationGroup()
    group.addAnimation(rotate)

    return group

### --------------------------------------------------------  
def demo(pix, path):  ## sets the demo path  
    if not DemoAvailable():  ## <--- shouldn't happen
        return
    
    waypts = pathLoader(path)  ## demo-path file name from the demo directory
    if not waypts: 
        return
    
    pix.node = Node(pix)   
    pt = getOffSet(pix)   ## offset for origin pt - setOrigin wasn't working
    sync = 11000
 
    path = QPropertyAnimation(pix.node, b'pos')
    path.setDuration(int(sync))
    
    path.setStartValue(waypts.pointAtPercent(0.0)-pt)
    for i in range(1, 99):    
        path.setKeyValueAt(i/100.0, waypts.pointAtPercent(i/100.0)-pt)
    path.setEndValue(waypts.pointAtPercent(1.0)-pt)  
    path.setLoopCount(-1) 

    rotate = QPropertyAnimation(pix.node, b'rotate')
    rotate.setDuration(int(sync/3))
    rotate.setEasingCurve(QEasingCurve.Type.InBounce)
    rotate.setStartValue(pix.rotation)    
    rotate.setKeyValueAt(0.25, pix.rotation-45)
    rotate.setKeyValueAt(0.50, pix.rotation)
    rotate.setKeyValueAt(0.75, pix.rotation+45)
    rotate.setEndValue(pix.rotation)
    rotate.setEasingCurve(QEasingCurve.Type.OutBounce)
    rotate.setLoopCount(-1)

    opacity = QPropertyAnimation(pix.node, b'opacity')
    opacity.setDuration(int(sync))
    opacity.setStartValue(pix.opacity())
    opacity.setKeyValueAt(.20, 1.0) 
    opacity.setKeyValueAt(.53, 1.0)
    opacity.setKeyValueAt(.56, 0.0)
    opacity.setKeyValueAt(.73, 0.0)
    opacity.setKeyValueAt(.75, .70)
    opacity.setKeyValueAt(.85, .95)
    opacity.setEndValue(pix.opacity())
    opacity.setLoopCount(-1)

    scale = QPropertyAnimation(pix.node, b'scale')
    scale.setDuration(int(sync))
    scale.setStartValue(pix.scale*1.05)
    scale.setKeyValueAt(.45, pix.scale*.80)
    scale.setKeyValueAt(.53, pix.scale*.25)
    scale.setKeyValueAt(.56, pix.scale*0.0)
    scale.setKeyValueAt(.75, pix.scale*.25)
    scale.setKeyValueAt(.80, pix.scale*.50)
    scale.setKeyValueAt(.85, pix.scale*.65)
    scale.setKeyValueAt(.90, pix.scale*.80)
    scale.setKeyValueAt(.95, pix.scale*.90)
    scale.setEndValue(pix.scale*1.05)
    scale.setLoopCount(-1)

    group = QParallelAnimationGroup()
    group.addAnimation(path)
    group.addAnimation(rotate)
    group.addAnimation(scale)
    group.addAnimation(opacity)

    group.setLoopCount(-1)

    return group

### --------------------------------------------------------
def getOffSet(pix):
    b = pix.boundingRect()
    return QPointF(b.width()*.5, b.height()*.5)

### --------------------------------------------------------
def setPaths(tag, pix):  ## called by setAnimation, one at a time        
    waypts = pathLoader(tag)  
    if not waypts: 
        return 
    sync = random.randint(118,179) * 100  ## very arbitrary   
    k = random.randint(55,105) % 5  ## just to make things interesting
    if k == 0: 
        waypts = waypts.toReversed()
    return pathAnimator(pix, sync, waypts)  ## shared

### --------------------------------------------------------
def pathAnimator(pix, sync, wpts):  ## called by demo
    pt = getOffSet(pix) 
    pix.node = Node(pix)
          
    path = QPropertyAnimation(pix.node, b'pos')   
    path.setDuration(sync)  
    
    path.setStartValue(wpts.pointAtPercent(0.0)-pt)
    for i in range(1, 99):    
        path.setKeyValueAt(i/100.0, wpts.pointAtPercent(i/100.0)-pt)
    path.setEndValue(wpts.pointAtPercent(1.0)-pt)

    path.setLoopCount(-1)
    
    group = QParallelAnimationGroup()
    group.addAnimation(path)
    
    return group
      
### --------------------------------------------------------
def pathLoader(path):  ## used by MapItem, Snakes. Abstract, Bats
    file = paths['paths'] + path  ## paths directory
    isDemo = False    
    if 'demo' in path:
        file = paths['demo'] + path 
        isDemo = True
    try:
        scaleX, scaleY = 1.0, 1.0 
        path = QPainterPath()
        if not isDemo:  ## apply scaleX, scaleY from screens except for bats demo
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
        MsgBox(f'pathLoader: Error loading pathFile, {os.path.basename(file)}', 5)
        return None

### ---------------------- dotsSidePath --------------------



