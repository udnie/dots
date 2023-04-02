
import os

from PyQt6.QtCore    import Qt, QTimer, QSize, QPoint, QMimeData, QUrl, QPointF, \
                            QEvent
from PyQt6.QtGui     import QPainter, QImage, QPen, QFont, QWheelEvent, \
                            QFontMetrics, QBrush, QPolygon, QDrag, QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea, \
                            QFrame, QFileDialog, QLayout

from dotsShared      import paths, Star, common
from functools       import partial
from dotsSideGig     import MsgBox

panel = {   ## the following is used by ScrollPanel
    'LabelW':   120,  
    'LabelH':   112,  
    'MaxW':     105,
    'MaxH':      85,  
    'Star':     .70,
    'Type':     106,
    'Margin':    15,    
}  ## also, common['modLabel'], scales down the tile's vertical for screen changes

### ------------------- dotsScrollPanel --------------------
''' dotsScrollPanel: handles scrolling sprite selections.
    Includes ImgLabel and ScrollPanel classes. '''
### --------------------------------------------------------
class ImgLabel(QLabel):
### --------------------------------------------------------
    def __init__(self, fileName, count, parent):
        super().__init__()
   
        self.scrollPanel = parent
        self.canvas = parent.canvas

        self.fileName = fileName
        self.id = count 

        self.setFrameStyle(QFrame.Shape.Panel|QFrame.Shadow.Raised)

### --------------------------------------------------------
    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        
        img = ''  ## otherwise it can crash
        if self.fileName == 'Star':
            qp.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))
            qp.setBrush(QBrush(Qt.GlobalColor.red, Qt.BrushStyle.SolidPattern))
            qp.drawPolygon(QPolygon(self.drawStar()))  
            qp.setBrush(Qt.BrushStyle.NoBrush) 
        else:    
            img = QImage(self.fileName)     
            r = common['modLabel']                   
            if img.width() > (panel['MaxW']) or img.height() > (panel['MaxH']):  ## size it to fit       
                img = img.scaled(int(panel['MaxW']), int(panel['MaxH']),  ## keep it small
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)                 
            newW, newH = img.width(), img.height()
            posX = ((panel['LabelW'] - newW) /2 )
            posY = ((panel['MaxH'] - newH) /2 ) + 9
            qp.drawImage(QPointF(posX, posY), img)
        del img
        
        pen = QPen(Qt.GlobalColor.darkGray)   
        pen.setWidth(2)
        qp.setPen(pen) 
        qp.drawRect(0, 0, panel['LabelW'], panel['LabelH'])

        pen = QPen(Qt.GlobalColor.white) 
        pen.setWidth(3)
        pen.setJoinStyle(Qt.PenJoinStyle.BevelJoin)
        qp.setPen(pen) 
        qp.drawLine(0, 2, 0, panel['LabelH']) # left border
        qp.drawLine(1, 1, panel['LabelW'], 1) # top border

        font = QFont()
        pen = QPen(Qt.GlobalColor.black)
        font.setFamily('Arial')
        font.setPointSize(12)

        qp.setPen(pen)  
        qp.setFont(font)
        fileName = os.path.basename(self.fileName)

        metrics = QFontMetrics(font)    
        p = metrics.boundingRect(fileName)
        p = p.width()
        p = (panel['LabelW'] - p)/2 

        qp.drawText(int(p), panel['Type'], fileName)
        qp.end()

    def minimumSizeHint(self):   
        return QSize(panel['LabelW'], self.setNewHeight()) 

    def sizeHint(self):
        return self.minimumSizeHint()
    
    def mousePressEvent(self, event):
        if self.canvas.key == 'del':
            self.scrollPanel.deleteImgLabel(self)

    def mouseMoveEvent(self, event):     
        self.StartDrag()
           
    def StartDrag(self):
        drag = QDrag(self)
        data = QMimeData()
        
        data.setText(None)
        data.setUrls([QUrl.fromLocalFile(self.fileName)])
        drag.setMimeData(data)
        
        drag.setPixmap(QPixmap(paths['imagePath'] + 'dnd2.png'))
        drag.exec()
     
    def drawStar(self):
        poly = QPolygon()
        for s in Star:
            poly.append(QPoint(s[0],s[1])*panel['Star'])
        return poly

    def setNewHeight(self):
        return int(self.scrollPanel.resetLabelH())

### --------------------------------------------------------
class ScrollPanel(QWidget):
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
        
        self.canvas = parent  ## used in imgLabel
        self.view   = self.canvas.view  
        self.dots   = self.canvas.dots

        self.setFixedSize(common['ScrollW'],common['ScrollH'])     
        self.layout = QVBoxLayout(self)    
        self.layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)  # fixed size

        self.widget = QWidget()  
        self.widget.setLayout(self.layout)   
        self.addScrollArea()

        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.layout.setContentsMargins(0,0,0,0)
             
        self.scrollCount = 0
        self.scrollList  = []
        
        self.last = 0        
        self.widget.installEventFilter(self)
        
### --------------------------------------------------------
    def eventFilter(self, obj, e): 
        if e.type() == QEvent.Type.Wheel: 
            if e.phase() == Qt.ScrollPhase.ScrollEnd:        
                QTimer.singleShot(100, self.reposition) 
        return QWidget.eventFilter(self, obj, e)      
                                            
    def reposition(self):  ## topmost partial tile down so all are evenly distributed 
        step = self.scroll.verticalScrollBar().singleStep()
        v = self.scroll.verticalScrollBar().value()
        p = int(v/step)
        if v % step != 0:  ## only if needed
            self.scroll.verticalScrollBar().setValue(p * step)  
   
    def addScrollArea(self):
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    
        self.scroll.setStyleSheet('background: rgb(235, 235, 235)')
        self.scroll.setStyleSheet('border: 1px solid rgb(160,160,160)')
        self.scroll.verticalScrollBar().setStyleSheet('QScrollBar:vertical {\n' 
            'background: rgb(245,245,245) }');  ## shows handle better
        
        self.scroll.setWidgetResizable(True)    # always
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.scroll.verticalScrollBar().setSingleStep(int(panel['LabelH'] * common['modLabel']))  
        self.scroll.setWidget(self.widget)
           
        self.scroll.verticalScrollBar().sliderReleased.connect(self.reposition)
    
        vBoxLayout = QVBoxLayout(self)
        vBoxLayout.setContentsMargins(0, common['margin1'],0,0)  ## change for dotsDocks??
        vBoxLayout.addWidget(self.scroll, Qt.AlignmentFlag.AlignVCenter)
         
        self.setLayout(vBoxLayout)
                                                
    def pageDown(self, key):
        scrollBar = self.scroll.verticalScrollBar()
        if key == 'down': 
            steps = common['steps']
        elif key == 'up':
            steps = common['steps'] * -1
        elif key == '1':
            steps = 1
        else:
            steps = -1      
        scrollBar.setValue(scrollBar.value() + scrollBar.singleStep() * steps)
        
 ### --------------------------------------------------------               
    def add(self, fname):   
        self.scrollCount += 1
        self.scrollList.append(self.scrollCount)   
        label = ImgLabel(fname, self.scrollCount, self)
        label.setFixedHeight(int(self.resetLabelH()))      
        self.layout.addWidget(label)
        self.bottom()
        
    def Star(self):    
        self.add('Star')
        
    def resetLabelH(self):  ## reset label height
        pan, mod = panel['LabelH'], common['modLabel']
        return pan * mod
        
    def deleteImgLabel(self, this):
        p = self.scrollList.index(this.id)
        del self.scrollList[p]    
        self.layout.itemAt(p).widget().deleteLater()
        # p *= self.resetLabelH()
        self.scroll.verticalScrollBar().setSliderPosition(int(p))

    def top(self):           
        if self.layout.count() > 0:
            firstItem = self.layout.itemAt(0).widget()
            QTimer.singleShot(0, partial(self.scroll.ensureWidgetVisible, 
                firstItem))

    def bottom(self):  ## thanks stackoverflow
        if self.layout.count() > 0:
            lastItem = self.layout.itemAt(self.layout.count()-1).widget()
            QTimer.singleShot(0, partial(self.scroll.ensureWidgetVisible, 
                lastItem))
   
    def clear(self):
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()
        self.scrollCount = 0
        self.scrollList = []
 
    def scrollFiles(self):
        Q = QFileDialog()
        files, _ = Q.getOpenFileNames(self,
            'Choose an image file to open', paths['snapShot'], 
            'Images Files(*.bmp *.jpg *.png)')
        if files:
            for fileName in files:
                self.add(fileName)
        Q.accept()
          
    def loadSprites(self):
        sprites = sorted(self.spriteList())
        if sprites:
            for s in sprites:
                self.add(s)
            self.top()   
        self.dots.statusBar.showMessage('Number of Sprites:  {}'.format(self.scrollCount),15000) 
        ## ------ your choice -------------
        # firstwidget = self.layout.itemAt(0).widget()
        # QTimer.singleShot(0, partial(self.scroll.ensureWidgetVisible, firstwidget))

    def spriteList(self):
        try:
            files = os.listdir(paths['spritePath'])
        except IOError:
            MsgBox('No Sprite Directory Found!', 5)
            return None  
        filenames = []
        for file in files:
            if file.lower().endswith('png'): 
                filenames.append(paths['spritePath'] + file.lower())       
        if not filenames:
            MsgBox('No Sprites Found!', 5)
            return
        return filenames

### ------------------- dotsScrollPanel --------------------

