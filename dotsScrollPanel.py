import os

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from dotsShared      import common, paths
from functools       import partial
from dotsSideCar     import MsgBox

### ------------------- dotsScrollPanel --------------------
''' dotsScrollPanel: handles scrolling sprite selections.
    Includes ImgLabel and ScrollPanel classes. '''
### --------------------------------------------------------
MaxW, MaxH = 165, 135         # max image size
LabelW, LabelH = 195, 170     # max label size
ScrollW, ScrollH = 215, 682   # scroll panel size

Star = ((100, 20), (112, 63), (158, 63), (122, 91), 
        (136, 133), (100, 106), (63, 132), (77, 90), 
        (41, 63), (86, 63))

### --------------------------------------------------------
class ImgLabel(QLabel):

    def __init__(self, imgFile, count, parent):
        super().__init__()
   
        self.dots = parent
        self.dots.canvas = parent.canvas

        self.imgFile = imgFile
        self.id = count 
       
        self.setFrameShape(QFrame.Panel|QFrame.Raised)
     
### --------------------------------------------------------
    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)

        if self.imgFile == 'Star':
            qp.setPen(QPen(Qt.black, 1, Qt.SolidLine))
            qp.setBrush(QBrush(Qt.red, Qt.SolidPattern))
            qp.drawPolygon(QPolygon(self.drawStar()))  
            qp.setBrush(Qt.NoBrush) 
        else:    
            img = QImage(self.imgFile)
            newW, newH = self.scaleTo(img)
            img = img.scaled(newW, newH,   
                Qt.KeepAspectRatio|
                Qt.SmoothTransformation)
            posX = ((LabelW - newW) /2 )
            posY = ((MaxH - newH) /2 ) + 10
            qp.drawImage(posX, posY, img)

        pen = QPen(Qt.darkGray)   
        pen.setWidth(2)
        qp.setPen(pen) 
        qp.drawRect(0, 0, LabelW, LabelH)

        pen = QPen(Qt.white) 
        pen.setWidth(3)
        pen.setJoinStyle(Qt.BevelJoin)
        qp.setPen(pen) 
        qp.drawLine(0, 2, 0, LabelH) # left border
        qp.drawLine(1, 1, LabelW, 1) # top border

        font = QFont()
        pen = QPen(Qt.black)
        font.setFamily('Arial')
        font.setBold(True)
        font.setPointSize(13)

        qp.setPen(pen)  
        qp.setFont(font)
        imgfile = os.path.basename(self.imgFile)
        metrics = QFontMetrics(font)    

        p = (LabelW - metrics.width(imgfile))/2 
        qp.drawText(p, 160, imgfile)
        qp.end()

    def minimumSizeHint(self):
        return QSize(LabelW, LabelH)

    def sizeHint(self):
        return self.minimumSizeHint()

    def mousePressEvent(self, event):
        if self.dots.canvas.key == 'del':
            self.dots.deleteImgLabel(self)

    def mouseMoveEvent(self, event):
        self.StartDrag()
 
    def StartDrag(self):
        drag = QDrag(self)
        data = QMimeData()
        data.setText(None)
    
        data.setUrls([QUrl.fromLocalFile(self.imgFile)])
        drag.setMimeData(data)
        drag.setPixmap(QPixmap(paths['imagePath'] + 'dnd2.png'))
        drag.exec_()
     
    def drawStar(self):
        poly = QPolygon()
        for s in Star:
            poly.append(QPoint(s[0], s[1]))
        return poly

    def scaleTo(self, img):
        W, H = img.width(), img.height()
        newW, newH = MaxW, MaxH

        if W == H:
            newW, newH = MaxH, MaxH
        elif W > H:
            newW = MaxW
            p = MaxW/ W
            newH = p * H
            if newH > MaxH:
                r = MaxH / newH
                newH, newW = r * newH, newW * r
        elif W < H:
            newH = MaxH
            p = MaxH / H
            newW = p * W
            if newW > MaxW:
                r = MaxW/ newW
                newH, newW = r * newH, newW * r
        return newW, newH   

### --------------------------------------------------------
class ScrollPanel(QWidget):

    def __init__(self, parent):
        super().__init__()
        
        self.dots   = parent
        self.canvas = parent.canvas ## used in imgLabel
        self.scene  = parent.scene 

        self.setFixedSize(ScrollW,ScrollH)
   
        self.layout = QVBoxLayout(self)
        self.layout.setSizeConstraint(3)  # fixed size
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignCenter)
     
        widget = QWidget()  
        widget.setLayout(self.layout)

        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
      
        self.scroll.setWidgetResizable(True)    # always
        self.scroll.verticalScrollBar().setSingleStep(15)

        self.scroll.setWidget(widget)
       
        vBoxLayout = QVBoxLayout(self)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        vBoxLayout.addWidget(self.scroll)
         
        self.setLayout(vBoxLayout) 

        self.scrollCount = 0
        self.scrollList = []

### --------------------------------------------------------
    def add(self, fname):   
        self.scrollCount += 1
        self.scrollList.append(self.scrollCount) 
        self.layout.addWidget(ImgLabel(fname, self.scrollCount, self))
        self.bottom()

    def Star(self):    
        self.add('Star')
        
    def deleteImgLabel(self, this):
        p = self.scrollList.index(this.id)
        del self.scrollList[p]    
        self.layout.itemAt(p).widget().deleteLater()
        p = (p-1) * LabelH
        self.scroll.verticalScrollBar().setSliderPosition(p)

    def top(self):           
        if self.layout.count() > 0:
            firstItem = self.layout.itemAt(0).widget()
            QTimer.singleShot(0, partial(self.scroll.ensureWidgetVisible, 
                firstItem))

    def bottom(self):         ## thanks stackoverflow
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
            "Choose an image file to open", paths['snapShot'], 
            "Images Files(*.bmp *.jpg *.png)")
        if files:
            for imgFile in files:
                self.add(imgFile)
        Q.done(0)
          
    def loadSprites(self):
        sprites = sorted(self.spriteList())
        if sprites:
            for s in sprites:
                self.add(s)
            self.top()   # your choice
        # firstwidget = self.layout.itemAt(0).widget()
        # QTimer.singleShot(0, partial(self.scroll.ensureWidgetVisible, firstwidget))

    def spriteList(self):
        try:
            files = os.listdir(paths['spritePath'])
        except IOError:
            MsgBox("No Sprite Directory Found!", 5)
            return None  
        filenames = []
        for file in files:
            if file.lower().endswith('png'): 
                filenames.append(paths['spritePath'] + file.lower())
        if not filenames:
            MsgBox("No Sprites Found!", 5)
        return filenames

### ------------------- dotsScrollPanel --------------------