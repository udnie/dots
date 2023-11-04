
import random
import os
import math

from PyQt6.QtCore       import Qt, QTimer, QPointF, QRectF, QPoint
from PyQt6.QtGui        import QPainter, QBrush, QFontMetrics, QColor, QFont, \
                                QGuiApplication, QImage, QPixmap
from PyQt6.QtWidgets    import QMessageBox, QGraphicsSimpleTextItem
         
from dotsShared         import common, paths, pathcolors, PlayKeys

### ---------------------- dotsSideGig ---------------------
''' classes: MsgBox, TagIt plus misc  ...'''
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
class TagIt(QGraphicsSimpleTextItem):
### --------------------------------------------------------   
    def __init__(self, token, tag, color, zval=None):
        super().__init__()
    
        if token == 'paths':
            color = 'lime'
            if 'Locked Random' in tag:
                tag = tag[14:] 
            elif 'Random' in tag:
                tag = tag[7:]
            n = tag.find('path') + 5
            tag = tag[0:n]
            
        elif token in PlayKeys and 'Random' in tag:
            tag = tag[7:]
            self.color = QColor(0,255,127)
            
        elif token == 'pathMaker':
            if ' 0.00%' in tag:
                color = QColor('LIGHTSEAGREEN')
            if len(tag.strip()) > 0: self.color = QColor(color)
            
        elif token == 'points':
            self.color = QColor(color)
            
        else:
            self.color = QColor(255,165,0)
            if 'Locked Random' in tag:
                tag = tag[0:13] 
            elif 'Random' in tag:
                tag = tag[0:6] 
                
        if color:
            self.color = QColor(color)

        if zval != None and token != 'paths':
            if len(tag) > 0:  
                tag = tag + ': ' + str(zval)
            else:
                tag = str(zval)
    
        if token == 'points':
            self.type = 'ptTag'  ## changed from 'pt'
        else:
            self.type = 'tag'

        self.text = tag   

        self.font = QFont()
        self.font.setFamily('Helvetica')
        self.font.setPointSize(12)
        
        if token == 'bkg':
            self.font.setPointSize(14)
        
        metrics = QFontMetrics(self.font)
        p = metrics.boundingRect(self.text)
        p = p.width()
 
        self.rect = QRectF(0, 0, p+13, 19)
        self.waypt = 0
            
    def boundingRect(self):
        return self.rect
    
### --------------------------------------------------------
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
''' functions that mostly return values follow '''
### --------------------------------------------------------
def constrain(lastXY, objSize, panelSize, overlap):
    if lastXY + objSize > panelSize - overlap:
        return panelSize - (objSize + overlap)
    elif lastXY < overlap:
        return overlap
    else:
        return lastXY

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

def point(pt, st=""):  ## you never know when you'll need this
    if isinstance(pt, QPointF):
        pt = pt.toPoint()   
    if st == '':
        return f'{pt.x(), pt.y()}'
    else:
        a = ': '
        return f'{st}{a}{pt.x(), pt.y()}'
    
def rect(pt, st=''):  ## ditto
    if isinstance(pt, QRectF):
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
  
  
        