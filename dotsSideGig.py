
import random
import os
import math

from PyQt6.QtCore       import Qt, QTimer, QPointF, QRectF, QPoint, QSize
from PyQt6.QtGui        import QPainter, QBrush, QFontMetrics, QColor, QFont, \
                                QGuiApplication, QImage, QPixmap
from PyQt6.QtWidgets    import QMessageBox, QGraphicsSimpleTextItem

from dotsShared         import common, paths, pathcolors, PlayKeys

### ---------------------- dotsSideGig ---------------------
''' dotsSideGigs: MsgBox, TagIt, savePix, saveBkg, saveFlat...'''
### --------------------------------------------------------
class MsgBox(QMessageBox):  ## always use getCtr for setting point
### --------------------------------------------------------
    def __init__(self, text, pause=3, pt=None):
        super().__init__()
                 
        img = QImage(paths['spritePath'] + "doral.png")
        pixmap = QPixmap(img)   
        self.setIconPixmap(pixmap)
        self.setText('\n' + text)
        
        if isinstance(pause, int):
            self.timeOut = pause
        elif isinstance(pause, QPoint):
            pt = pause
            self.timeOut = 3
        elif not isinstance(pt, QPoint):
            MsgBox('Use a QPoint(n,n) to set message position', 6)
            return
        else:
            self.timeOut = 3
                   
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeContent)
        self.timer.start()

        if isinstance(pt, QPoint) and pt.x() > 0 and pt.y() > 0: 
            self.move(pt)
               
        self.exec()
                           
    def enterEvent(self, e):  
        self.close()

    def changeContent(self):
        self.timeOut -= 1
        if self.timeOut <= 0:
            self.close()

    def closeEvent(self, e):
        self.timer.stop()
        e.accept() 

### --------------------------------------------------------
class TagIt(QGraphicsSimpleTextItem):
### --------------------------------------------------------   
    def __init__(self, control, tag, color, zval=None):
        super().__init__()
    
        if control == 'paths':
            color = 'lime'
            if 'Locked Random' in tag:
                tag = tag[14:] 
            elif 'Random' in tag:
                tag = tag[7:]
            n = tag.find('path') + 5
            tag = tag[0:n]
        elif control in PlayKeys and 'Random' in tag:
            tag = tag[7:]
            self.color = QColor(0,255,127)
        elif control == 'pathMaker':
            if ' 0.00%' in tag:
                color = QColor('LIGHTSEAGREEN')
            if len(tag.strip()) > 0: self.color = QColor(color)
        elif control == 'points':
            self.color = QColor(color)
        else:
            self.color = QColor(255,165,0)
            if 'Locked Random' in tag:
                tag = tag[0:13] 
            elif 'Random' in tag:
                tag = tag[0:6] 
        if color:
            self.color = QColor(color)

        if zval != None and control != 'paths':
            if len(tag) > 0:  
                tag = tag + ': ' + str(zval)
            else:
                tag = str(zval)
    
        if control == 'points':
            self.type = 'ptTag'  ## changed from 'pt'
        else:
            self.type = 'tag'

        self.text = tag   

        self.font = QFont()
        self.font.setFamily('Helvetica')
        self.font.setPointSize(12)

        metrics = QFontMetrics(self.font)
        p = metrics.boundingRect(self.text)
        p = p.width()
 
        self.rect = QRectF(0, 0, p+13, 19)
        self.waypt = 0

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget): 
        brush = QBrush()
        brush.setColor(self.color)
        brush.setStyle(Qt.BrushStyle.SolidPattern)

        painter.fillRect(self.boundingRect(), brush)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(Qt.GlobalColor.black)
        painter.setFont(self.font)
        painter.drawText(self.boundingRect(), 
            Qt.AlignmentFlag.AlignCenter, self.text)

### --------------------------------------------------------
def constrain(lastXY, objSize, panelSize, overlap):
    if lastXY + objSize > panelSize - overlap:
        return panelSize - (objSize + overlap)
    elif lastXY < overlap:
        return overlap
    else:
        return lastXY

def getOffSet(pix):
    b = pix.boundingRect()
    return QPointF(b.width()*.5, b.height()*.5)

def xy(max):
    return random.randrange(-40, max+40)

def getCtr(x,y):  ## return center x,y with offsets
    ctr = QGuiApplication.primaryScreen().availableGeometry().center()
    return QPoint(ctr.x()+x, ctr.y()+y)

def getPathList(bool=False):  ## used by DoodleMaker & context menu
    try:                        
        files = os.listdir(paths['paths'])
    except IOError:
        MsgBox('getPathList: No Path Directory Found!', 5)
        return None  
    filenames = []
    for file in files:
        if file.lower().endswith('path'):
            if bool:    
                file = os.path.basename(file)  ## short list
                filenames.append(file)
            else:
                filenames.append(paths['paths'] + file)
    if not filenames:
        MsgBox('getPathList: No Paths Found!', 5)
        return
    filenames.sort()  ## can't return it sorted otherwise 
    return filenames

def getPts(file, scalor=1.0, inc=0):  ## also used by pathChooser
    try:
        tmp = []
        with open(file, 'r') as fp: 
            for line in fp:
                ln = line.rstrip()  
                if len(ln) == 0: continue  ## skip empty lines
                ln = list(map(float, ln.split(',')))   
                tmp.append(QPointF(ln[0]*scalor+inc, ln[1]*scalor+inc))
        return tmp
    except IOError:
        MsgBox('getPts: Error reading pts file', 5)

def getColorStr():  
    random.seed()
    p = pathcolors
    return p[random.randint(0,len(p)-1)]

def distance(x1, x2, y1, y2):
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt((dx * dx ) + (dy * dy)) 

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
### from sideshow
### --------------------------------------------------------
def savePix(pix): 
    p = pix.pos() 
    tmp = {
        'fname':    os.path.basename(pix.fileName),
        'type':    'pix',
        'x':        float('{0:.2f}'.format(p.x())),
        'y':        float('{0:.2f}'.format(p.y())),
        'z':        pix.zValue(),
        'mirror':   pix.flopped,
        'rotation': pix.rotation,
        'scale':    float('{0:.2f}'.format(pix.scale)),
        'tag':      pix.tag,
        'alpha2':   float('{0:.2f}'.format(pix.alpha2)), 
        'locked':   pix.locked,
        'part':     pix.part,
    }  
    
    if pix.shadow != None:   
        shadow = {
            'alpha':    float('{0:.2f}'.format(pix.shadowMaker.alpha)),
            'scalor':   float('{0:.2f}'.format(pix.shadowMaker.scalor)),
            'rotate':   pix.shadowMaker.rotate,
            'width':    pix.shadowMaker.imgSize[0],
            'height':   pix.shadowMaker.imgSize[1],
            'pathX':    [float('{0:.2f}'.format(pix.shadowMaker.path[k].x()))
                            for k in range(len(pix.shadowMaker.path))],
            'pathY':    [float('{0:.2f}'.format(pix.shadowMaker.path[k].y()))
                            for k in range(len(pix.shadowMaker.path))],
            'flopped':   pix.shadowMaker.flopped,
        }
        tmp.update(shadow)
          
    return tmp 

def saveBkg(pix):
    p = pix.boundingRect() 
    tmp = {
        'fname':    os.path.basename(pix.fileName),
        'type':    'bkg',
        'x':        float('{0:.2f}'.format(pix.x)),
        'y':        float('{0:.2f}'.format(pix.y)),
        'z':        pix.zValue(),
        'mirror':   pix.flopped,
        'locked':   pix.locked,
        'rotation': pix.rotation,
        'scale':    float('{0:.2f}'.format(pix.scale)),
        'opacity':  float('{0:.2f}'.format(pix.opacity)),
        'width':    int(p.width()),
        'height':   int(p.height()),
        'tag':      pix.tag,
        'scrollable':   pix.scrollable,
        'direction':    pix.direction,
    }
    return tmp

def saveFlat(pix):
    tmp = {
        'fname': 'flat',
        'type':  'bkg',
        'z':      pix.zValue(),
        'tag':    pix.color.name(),
        'color':  pix.color.name(),
    }
    return tmp

### --------------------- dotsSideGig ----------------------
  
  
        