import os

from PyQt5.QtCore    import Qt, QTimer, QSize, QPoint, QMimeData, QUrl
from PyQt5.QtGui     import QPainter, QImage, QColor, QPen, QFont, \
                            QFontMetrics, QBrush, QPolygon, QDrag, QPixmap 
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea, \
                            QFrame, QFileDialog

from dotsShared      import paths, Star, common
from functools       import partial
from dotsSideGig     import MsgBox

### ------------------- dotsScrollPanel --------------------
''' dotsScrollPanel: handles scrolling sprite selections.
    Includes ImgLabel and ScrollPanel classes. '''
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
            posX = ((common['LabelW'] - newW) /2 )
            posY = ((common['MaxH'] - newH) /2 ) + 9
            qp.drawImage(posX, posY, img)

        pen = QPen(Qt.darkGray)   
        pen.setWidth(2)
        qp.setPen(pen) 
        qp.drawRect(0, 0, common['LabelW'], common['LabelH'])

        pen = QPen(Qt.white) 
        pen.setWidth(3)
        pen.setJoinStyle(Qt.BevelJoin)
        qp.setPen(pen) 
        qp.drawLine(0, 2, 0, common['LabelH']) # left border
        qp.drawLine(1, 1, common['LabelW'], 1) # top border

        font = QFont()
        pen = QPen(Qt.black)
        font.setFamily('Arial')
        font.setPointSize(12)

        qp.setPen(pen)  
        qp.setFont(font)
        imgfile = os.path.basename(self.imgFile)
        metrics = QFontMetrics(font)    

        p = (common['LabelW'] - metrics.width(imgfile))/2 
        qp.drawText(p, common['Type'], imgfile)
        qp.end()

    def minimumSizeHint(self):
        return QSize(common['LabelW'], common['LabelH'])

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
            poly.append(QPoint(s[0]-3, s[1])*common['Star'])
        return poly

    def scaleTo(self, img):
        W, H = img.width(), img.height()
        newW, newH = common['MaxW'], common['MaxH']

        if W == H:
            newW, newH = common['MaxH'], common['MaxH']
        elif W > H:
            newW = common['MaxW']
            p = common['MaxW']/ W
            newH = p * H
            if newH > common['MaxH']:
                r = common['MaxH'] / newH
                newH, newW = r * newH, newW * r
        elif W < H:
            newH = common['MaxH']
            p = common['MaxH'] / H
            newW = p * W
            if newW > common['MaxW']:
                r = common['MaxW']/ newW
                newH, newW = r * newH, newW * r
        return newW, newH   

### --------------------------------------------------------
class ScrollPanel(QWidget):

    def __init__(self, parent):
        super().__init__()
        
        self.dots   = parent
        self.canvas = parent.canvas ## used in imgLabel
        self.scene  = parent.scene 

        self.setFixedSize(common['ScrollW'],common['ScrollH'])
   
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
        vBoxLayout.setContentsMargins(0, common['Margin'], 0, 0)  ## change for dotsDocks
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
        p = (p-1) * common['LabelH']
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