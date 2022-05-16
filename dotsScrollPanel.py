
import os

from PyQt6.QtCore    import Qt, QTimer, QSize, QPoint, QMimeData, QUrl, QPointF
from PyQt6.QtGui     import QPainter, QImage, QPen, QFont, \
                            QFontMetrics, QBrush, QPolygon, QDrag, QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea, \
                            QFrame, QFileDialog, QLayout

from dotsShared      import paths, Star, common
from functools       import partial
from dotsSideGig     import MsgBox

### ------------------- dotsScrollPanel --------------------
''' dotsScrollPanel: handles scrolling sprite selections.
    Includes ImgLabel and ScrollPanel classes. '''
### --------------------------------------------------------
class ImgLabel(QLabel):
### --------------------------------------------------------
    def __init__(self, imgFile, count, parent):
        super().__init__()
   
        self.scrollPanel = parent
        self.canvas = parent.canvas

        self.imgFile = imgFile
        self.id = count 

        self.setFrameStyle(QFrame.Shape.Panel|QFrame.Shadow.Raised)

### --------------------------------------------------------
    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)

        if self.imgFile == 'Star':
            qp.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))
            qp.setBrush(QBrush(Qt.GlobalColor.red, Qt.BrushStyle.SolidPattern))
            qp.drawPolygon(QPolygon(self.drawStar()))  
            qp.setBrush(Qt.BrushStyle.NoBrush) 
        else:    
            img = QImage(self.imgFile)
                        
            if img.width() > common['MaxW'] or img.height() > common['MaxH']:  ## size it to fit       
                img = img.scaled(common['MaxW'], common['MaxH'],  ## keep it small
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)
      
            newW, newH = img.width(), img.height()
          
            posX = ((common['LabelW'] - newW) /2 )
            posY = ((common['MaxH'] - newH) /2 ) + 9
            qp.drawImage(QPointF(posX, posY), img)

        pen = QPen(Qt.GlobalColor.darkGray)   
        pen.setWidth(2)
        qp.setPen(pen) 
        qp.drawRect(0, 0, common['LabelW'], common['LabelH'])

        pen = QPen(Qt.GlobalColor.white) 
        pen.setWidth(3)
        pen.setJoinStyle(Qt.PenJoinStyle.BevelJoin)
        qp.setPen(pen) 
        qp.drawLine(0, 2, 0, common['LabelH']) # left border
        qp.drawLine(1, 1, common['LabelW'], 1) # top border

        font = QFont()
        pen = QPen(Qt.GlobalColor.black)
        font.setFamily('Arial')
        font.setPointSize(12)

        qp.setPen(pen)  
        qp.setFont(font)
        imgfile = os.path.basename(self.imgFile)

        metrics = QFontMetrics(font)    
        p = metrics.boundingRect(imgfile)
        p = p.width()
        p = (common['LabelW'] - p)/2 

        qp.drawText(int(p), common['Type'], imgfile)
        qp.end()

    def minimumSizeHint(self):
        return QSize(common['LabelW'], common['LabelH'])

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
    
        data.setUrls([QUrl.fromLocalFile(self.imgFile)])
        drag.setMimeData(data)
        drag.setPixmap(QPixmap(paths['imagePath'] + 'dnd2.png'))
        drag.exec()
     
    def drawStar(self):
        poly = QPolygon()
        for s in Star:
            poly.append(QPoint(s[0],s[1])*common['Star'])
        return poly

### --------------------------------------------------------
class ScrollPanel(QWidget):
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
        
        self.canvas = parent  ## used in imgLabel
        self.view   = parent.view  

        self.setFixedSize(common['ScrollW'],common['ScrollH'])
   
        self.layout = QVBoxLayout(self)
        
        self.layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)  # fixed size
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
     
        widget = QWidget()  
        widget.setLayout(self.layout)

        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
      
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
            self.top()   
        ## ------ your choice -------------
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

