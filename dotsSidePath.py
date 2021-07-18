import sys
import random
import time

from PyQt5.QtCore       import QPointF, QPropertyAnimation, QEasingCurve, \
                               QParallelAnimationGroup, QSequentialAnimationGroup     
from PyQt5.QtGui        import QPainterPath

from dotsShared         import paths
from dotsSideGig        import MsgBox

### ---------------------- dotsSidePath --------------------
''' dotsPaths is used by animations and pathmaker and contains 
    demo, setPath, getOffSet and pathLoader '''
### --------------------------------------------------------
def demo(pix, anime, node):           
    pos  = node.pix.pos()
    sync = 10000
        
    ## needs a pause before it starts followed by a delayed
    ## start, also see play(), to match the animation in java 

    idle = QPropertyAnimation(node, b'pos')
    idle.setDuration(13)
    idle.setStartValue(pos)
    idle.setEndValue(pos)

    waypts = pathLoader(anime)
    if not waypts: return
    ## offset for origin pt - setOrigin wasn't working
    pt = getOffSet(node.pix)

    path = QPropertyAnimation(node, b'pos')
    path.setDuration(sync)
    path.setStartValue(waypts.pointAtPercent(0.0)-pt)
    for i in range(1, 99):    
        path.setKeyValueAt(i/100.0, waypts.pointAtPercent(i/100.0)-pt)
    path.setEndValue(waypts.pointAtPercent(1.0)-pt)  
    path.setLoopCount(-1) 

    rotate = QPropertyAnimation(node, b'rotate')
    rotate.setDuration(sync/3)
    rotate.setEasingCurve(QEasingCurve.InBounce)
    rotate.setStartValue(node.pix.rotation)    
    rotate.setKeyValueAt(0.25, pix.rotation-45)
    rotate.setKeyValueAt(0.50, pix.rotation)
    rotate.setKeyValueAt(0.75, pix.rotation+45)
    rotate.setEndValue(node.pix.rotation)
    rotate.setEasingCurve(QEasingCurve.OutBounce)
    rotate.setLoopCount(-1)

    opacity = QPropertyAnimation(node, b'opacity')
    opacity.setDuration(sync)
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
    scale.setDuration(sync)
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

    seq = QSequentialAnimationGroup()
    seq.addAnimation(idle)
    seq.addAnimation(group)

    seq.setLoopCount(-1)

    return seq

### --------------------------------------------------------
def setPaths(pix, anime, node):           
    pos  = node.pix.pos()
    sync = random.randint(73,173) * 100  ## very arbitrary

    path = QPropertyAnimation(node, b'pos')
    path.setDuration(sync)

    waypts = pathLoader(anime)
    if not waypts: return
    ## offset for origin pt - setOrigin wasn't working
    pt = getOffSet(node.pix)

    path.setStartValue(waypts.pointAtPercent(0.0)-pt)
    for i in range(1, 99):    
        path.setKeyValueAt(i/100.0, waypts.pointAtPercent(i/100.0)-pt)
    path.setEndValue(waypts.pointAtPercent(1.0)-pt)

    path.setLoopCount(-1) 
    
    return path

### --------------------------------------------------------
def getOffSet(pix):
    b = pix.boundingRect()
    w = (b.width()*.5)
    h = (b.height()*.5)
    return QPointF(w,h)

def pathLoader(anime):
    file = paths["paths"] + anime  ## includes '.path'
    try:
        path = QPainterPath()
        with open(file, 'r') as fp:
            for line in fp:
                ln = line.rstrip()  
                ln = list(map(float, ln.split(',')))
                if not path.elementCount():
                    path.moveTo(QPointF(ln[0], ln[1]))
                path.lineTo(QPointF(ln[0], ln[1])) 
        path.closeSubpath()
        return path
    except IOError:
        MsgBox("pathLoader: Error loading path file")

### ---------------------- dotsSidePath --------------------