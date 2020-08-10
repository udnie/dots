import os

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from functools import partial

import dotsQt 

### ------------------- dotsScrollPanel --------------------

maxH, maxW = 135, 165         # max image size
labelH, labelW = 170, 195     # max label size
scrollW, scrollH = 215, 682   # panel size

star = [(100, 20), (112, 63), (158, 63), (122, 91), 
        (136, 133), (100, 106), (63, 132), (77, 90), 
        (41, 63), (86, 63)]

### --------------------------------------------------------
class ImgLabel(QLabel):

    def __init__(self, imgFile, count, parent):
        super().__init__()
   
        self.shared = dotsQt.Shared()

        self.imgFile = imgFile
        self.parent = parent

        self.id = count 
       
        self.setFrameShape(QFrame.Panel|QFrame.Raised)
        # self.setLineWidth(2)
        # self.setMidLineWidth(2)
     
### --------------------------------------------------------
    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)

        if self.imgFile == 'star':
            qp.setPen(QPen(Qt.black, 1, Qt.SolidLine))
            qp.setBrush(QBrush(Qt.red, Qt.SolidPattern))
            qp.drawPolygon(QPolygon(self.drawStar()))  
            qp.setBrush(Qt.NoBrush) 
        else:    
            img = QImage(self.imgFile)
            newW, newH = self.scaleTo(img, maxW, maxH)
            img = img.scaled(newW, newH,   
                Qt.KeepAspectRatio|
                Qt.SmoothTransformation)
            posX = ((labelW - newW) /2 )
            posY = ((maxH - newH) /2 ) + 10
            qp.drawImage(posX, posY, img)

        pen = QPen(Qt.darkGray)   
        pen.setWidth(2)
        qp.setPen(pen) 
        qp.drawRect(0, 0, labelW, labelH)

        pen = QPen(Qt.white) 
        pen.setWidth(3)
        pen.setJoinStyle(Qt.BevelJoin)
        qp.setPen(pen) 
        qp.drawLine(0, 2, 0, labelH) # left border
        qp.drawLine(1, 1, labelW, 1) # top border

        font = QFont()
        pen = QPen(Qt.black)
        font.setFamily('Modern')
        font.setBold(True)
        font.setPointSize(13)

        qp.setPen(pen)  
        qp.setFont(font)
        imgFile = os.path.basename(self.imgFile)
        metrics = QFontMetrics(font)

        p = (labelW - metrics.width(imgFile))/2 
        qp.drawText(p, 160, imgFile)
        qp.end()

    def minimumSizeHint(self):
        return QSize(labelW, labelH)

    def sizeHint(self):
        return self.minimumSizeHint()

    def mousePressEvent(self, event):
        if self.parent.canvas.key == 'del':
            self.parent.deleteImgLabel(self)

    def mouseMoveEvent(self, event):
        self.startDrag()
 
    def startDrag(self):
        drag = QDrag(self)
        data = QMimeData()
        data.setText(None)
    
        data.setUrls([QUrl.fromLocalFile(self.imgFile)])
        drag.setMimeData(data)
        drag.setPixmap(QPixmap(self.shared.imagePath + 'dnd2.png'))
        drag.exec_()
     
    def drawStar(self):
        poly = QPolygon()
        for s in star:
            poly.append(QPoint(s[0], s[1]))
        return poly

    def scaleTo(self, img, maxW, maxH):
        W, H = img.width(), img.height()
        newW, newH = maxW, maxH

        if W == H:
            newW, newH = maxH, maxH
        elif W > H:
            newW = maxW
            p = maxW / W
            newH = p * H
            if newH > maxH:
                r = maxH / newH
                newH, newW = r * newH, newW * r
        elif W < H:
            newH = maxH
            p = maxH / H
            newW = p * W
            if newW > maxW:
                r = maxW / newW
                newH, newW = r * newH, newW * r
        return newW, newH   

### --------------------------------------------------------
class ScrollPanel(QWidget):

    def __init__(self, parent):
        super().__init__()
        
        self.parent = parent
        self.canvas = parent.canvas

        self.shared = dotsQt.Shared()
        self.setFixedSize(scrollW,scrollH)
   
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

    def leaveEvent(self, e):
        self.parent.view.setFocus()

### --------------------------------------------------------
    def add(self, fname):   
        self.scrollCount += 1
        self.scrollList.append(self.scrollCount) 
        img = ImgLabel(fname, self.scrollCount, self)
        self.layout.addWidget(img)
        self.bottom()

    def star(self):    
        self.add('star')
        
    def deleteImgLabel(self, this):
        p = self.scrollList.index(this.id)
        del self.scrollList[p]    
        self.layout.itemAt(p).widget().deleteLater()
        p = (p-1) * labelH
        self.scroll.verticalScrollBar().setSliderPosition(p)

    def top(self):           
        if self.layout.count() > 0:
            firstItem = self.layout.itemAt(0).widget()
            QTimer.singleShot(0, partial(self.scroll.ensureWidgetVisible, firstItem))

    def bottom(self):         ## thanks stackoverflow
        if self.layout.count() > 0:
            lastItem = self.layout.itemAt(self.layout.count()-1).widget()
            QTimer.singleShot(0, partial(self.scroll.ensureWidgetVisible, lastItem))

    def clear(self):
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()
        self.scrollCount = 0
        self.scrollList = []
 
    def scrollFiles(self):
        Q = QFileDialog()
        files, _ = Q.getOpenFileNames(self,
            "Choose an image file to open", self.shared.snapShot, 
            "Images Files(*.bmp *.jpg *.png)")
        if len(files) != 0:
            for imgFile in files:
                self.add(imgFile)
        Q.done(0)
          
    def loadSprites(self):
        sprites = self.spriteList()
        if sprites:
            for s in sprites:
                self.add(s)
            self.top()   # your choice
        # firstwidget = self.layout.itemAt(0).widget()
        # QTimer.singleShot(0, partial(self.scroll.ensureWidgetVisible, firstwidget))

    def spriteList(self):
        try:
            files = os.listdir(self.shared.spritePath)
        except IOError:
            self.canvas.MsgBox("No Sprite Directory Found!", 5)
            return None  
        filenames = []
        for file in files:
            if file.lower().endswith('png'): 
                filenames.append(self.shared.spritePath + file)
        if not filenames:
            self.canvas.MsgBox("No Sprites Found!", 5)
        return filenames

### ------------------- dotsScrollPanel --------------------