
import os
import random

from PyQt6.QtCore       import QPointF, QPropertyAnimation, QEasingCurve, \
                                QParallelAnimationGroup
from PyQt6.QtGui        import QPainterPath

from dotsShared         import paths, common
from dotsSideGig        import getOffSet, MsgBox, DemoAvailable

### ---------------------- dotsSidePath --------------------
''' dotsSidePath is used by storyboard, showbiz, animations, 
    pathmaker and contains demo, setPath, pathLoader.
    Mostly all of the original demo is here '''
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
    if not DemoAvailable():  ## <--- shouldn't happen
        return
    
    sync = 11000

    waypts = pathLoader(anime)  ## demo-path file name from the demo directory
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
    return pathAnimator(node, sync, waypts)  ## shared

### --------------------------------------------------------
def pathAnimator(node, sync, wpts):         
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



