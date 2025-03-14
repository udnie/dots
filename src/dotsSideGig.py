
import random
import os
import math

from PyQt6.QtCore       import Qt, QTimer, QPointF, QRectF, QPoint
from PyQt6.QtGui        import QGuiApplication, QImage, QPixmap, QPen, QColor
from PyQt6.QtWidgets    import QMessageBox, QGraphicsLineItem, QGraphicsSimpleTextItem
     
from dotsShared         import common, paths, pathcolors

### ---------------------- dotsSideGig ---------------------
''' class: MsgBox, Grid, and misc  ...'''                       
### --------------------------------------------------------
class MsgBox:  ## always use getCtr for setting point
### --------------------------------------------------------
    def __init__(self, text, pause=3, pt=None):
        super().__init__()
                 
        self.msg = QMessageBox()     
                     
        img = QImage(paths['spritePath'] + "doral.png")         
        img = img.scaled(60, 60,  ## keep it small
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation) 
        
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

        pt = getCtr(-200,-50)  ## 5

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
class Grid:  ## moved from sideCar
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
        self.scene  = self.canvas.scene
        
        self.gridZ   = common['gridZ']    
        self.gridSet = False  
        
### -------------------------------------------------------                                        
    def toggleGrid(self):
        self.removeGrid() if self.gridSet == True else self.addGrid()
     
    def addGrid(self):   
        self.gridSet = True 
        gs = common['gridSize']
        pen = QPen(QColor(0,0,255))       
        for y in range(1, int(common['ViewH']/gs)):
            self.addLines(QGraphicsLineItem(0.0, gs*y,
                float(common['ViewW']), gs*y), pen)
        for x in range(1, int(common['ViewW']/gs)):
            self.addLines(QGraphicsLineItem(gs*x, 0.0,
                gs*x, float(common['ViewH'])), pen)
        
    def addLines(self, line, pen):
        line.type = 'grid'
        line.setPen(pen)
        line.setOpacity(.30)
        line.setZValue(common['gridZ'])
        line.setFlag(QGraphicsLineItem.GraphicsItemFlag.ItemIsMovable, False)
        self.scene.addItem(line)

    def removeGrid(self):
        self.gridSet = False 
        try:
            for pix in self.scene.items():
                if pix.type == 'grid': self.scene.removeItem(pix)
        except:
            return
        
    def gridCount(self):  
        return sum(pix.type == 'grid' 
            for pix in self.canvas.scene.items())
                       
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
    
def getVuCtr(self):  ## used by menus and widgets - maps view center to global
    x,y = int(common['ViewW']/2), int(common['ViewH']/2) 
    p = self.canvas.mapToGlobal(QPoint(x,y))
    return int(p.x()), int(p.y())

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

### --------------------------------------------------------
    ## single tag - press the '\' backslash key then click 
    ## for screen items pix, bkg, flat, shadows and frames    
### --------------------------------------------------------  
def tagBkg(bkg, pos):  
    x, y, z = pos.x(), pos.y(), bkg.zValue()   
    text = QGraphicsSimpleTextItem() 
              
    src = 'bkg'  
    color = 'orange'
    
    topZVal = bkg.canvas.mapper.toFront()
       
    if bkg.type == 'shadow': 
        color = 'lightgreen'   
        if bkg.maker.linked == True:
            tag = 'Linked' 
        else: 
            tag = 'Unlinked' 
    else:    
        if bkg.locked == True:
            text = 'Locked' 
        else:
            text = 'Unlocked'
        fileName = os.path.basename(bkg.fileName)  ## other than shadows
        tag = fileName + " " + text     
    
    if bkg.type == 'bkg':
        if bkg.direction == ' left':
            tag = tag + ' Left'
        elif bkg.direction == 'right': 
            tag = tag + ' Right'
        tag = tag + ' ' + bkg.useThis  
        color = 'AQUA'
           
    elif bkg.type in ('pix', 'frame') and z == topZVal:
        color = 'yellow' 
        src = 'pix'  
            
    if 'frame' in bkg.fileName: 
        x, y = common['ViewW']*.47, common['ViewH']-35
   
    bkg.canvas.mapper.tagsAndPaths.TagItTwo('bkg', tag,  QColor(color), x, y, z, src)
    
### --------------------- dotsSideGig ----------------------
  
  
        