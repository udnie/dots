
import random
import os
import math

from PyQt6.QtCore       import QTimer, QPointF, QRectF, QPoint
from PyQt6.QtGui        import QGuiApplication, QImage, QPixmap
from PyQt6.QtWidgets    import QMessageBox
         
from dotsShared         import common, paths, pathcolors

### ---------------------- dotsSideGig ---------------------
''' class: MsgBox plus misc  ...'''
### --------------------------------------------------------
class MsgBox:  ## always use getCtr for setting point
### --------------------------------------------------------
    def __init__(self, text, pause=3, pt=None):
        super().__init__()
                 
        self.msg = QMessageBox()
                        
        img = QImage(paths['spritePath'] + "doral.png")
        pixmap = QPixmap(img)   
        self.msg.setIconPixmap(pixmap)
        self.msg.setText('\n' + text)
        
        if isinstance(pause, int):
            self.timeOut = pause
        elif isinstance(pause, QPoint):
            pt = pause
            self.timeOut = 3
        elif not isinstance(pt, QPoint):
            self.msg('Use a QPoint(n,n) to set message position', 6)
            return
        else:
            self.timeOut = 3
                   
        self.timer = QTimer(self.msg)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeContent)
        self.timer.start()

        if isinstance(pt, QPoint) and pt.x() > 0 and pt.y() > 0: 
            self.msg.move(pt)
               
        self.msg.exec()
                           
    def enterEvent(self, e):  
        self.msg.close()

    def changeContent(self):
        self.timeOut -= 1
        if self.timeOut <= 0:
            self.msg.close()

    def closeEvent(self, e):
        self.timer.stop()
        e.accept() 

### --------------------------------------------------------
''' functions that mostly return values follow '''
### --------------------------------------------------------
def constrain(lastXY, objSize, panelSize, overlap):
    if lastXY + objSize > panelSize - overlap:
        return panelSize - (objSize + overlap)
    elif lastXY < overlap:
        return overlap
    else:
        return lastXY

def getPathList(bool=False):  ## used by DoodleMaker & context menu
    try:                        
        files = os.listdir(paths['paths'])
    except IOError:
        # MsgBox('getPathList: No Path Directory Found!', 5)
        return None    
    if not files:
        # MsgBox('getPathList: No Paths Found!', 5)
        return None  
    filenames = []
    for file in files:
        if file.lower().endswith('path'):
            if bool:    
                file = os.path.basename(file)  ## short list
                filenames.append(file)
            else:
                filenames.append(paths['paths'] + file)
    filenames.sort()  ## can't return it sorted otherwise 
    return filenames

def getPts(file, scalor=1.0, inc=0):  ## also used by pathChooser
    tmp = []
    try:  
        with open(file, 'r') as fp: 
            for line in fp:
                ln = line.rstrip()  
                if len(ln) == 0: continue  ## skip empty lines
                ln = list(map(float, ln.split(',')))   
                tmp.append(QPointF(ln[0]*scalor+inc, ln[1]*scalor+inc))
        return tmp
    except IOError:
        MsgBox('getPts: Error reading pts file', 5)
        
def DemoAvailable():
    if os.path.exists(paths['demo']):  ## note
        return True
    else:
        return False

def getOffSet(pix):
    b = pix.boundingRect()
    return QPointF(b.width()*.5, b.height()*.5)

def xy(max):
    return random.randrange(-40, max+40)

def getCtr(x,y):  ## return center x,y with offsets
    ctr = QGuiApplication.primaryScreen().availableGeometry().center()
    return QPoint(ctr.x()+x, ctr.y()+y)

def getColorStr():  
    random.seed()
    p = pathcolors
    return p[random.randint(0,len(p)-1)]

def distance(x1, x2, y1, y2):
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt((dx * dx ) + (dy * dy)) 

def point(pt, st=""):  ## you never know when you'll need this
    if isinstance(pt, QPointF):  ## formats point(f) as fstr
        pt = pt.toPoint()   
    if st == '':
        return f'{pt.x(), pt.y()}'
    else:
        a = ': '
        return f'{st}{a}{pt.x(), pt.y()}'
    
def rect(pt, st=''):  ## ditto
    if isinstance(pt, QRectF):  ## formats rect(f) as fstr
        pt = pt.toRect()  
    if st == '':
        return f'{pt.x(), pt.y(), pt.width(), pt.height()}'
    else:
        a = ': '
        return f'{st}{a}{pt.x(), pt.y(), pt.width(), pt.height()}'

def getCrop(path):  ## from path - bounding size and position
    x, y, x1, y1 = common['ViewW'], common['ViewH'], 0.0, 0.0
    for p in path:
        if p.x() < x:
            x = p.x()
        if p.x() > x1:
            x1 = p.x()           
        if p.y() < y:
            y = p.y()
        if p.y() > y1:
            y1 = p.y()  
    return int(x), int(y), int((x1-x)), int((y1-y))

### --------------------- dotsSideGig ----------------------
  
  
        