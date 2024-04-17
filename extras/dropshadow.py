
import sys

from PyQt6.QtCore    import Qt, QTimer, QPointF
from PyQt6.QtGui     import QColor, QImage, QPixmap, QGuiApplication
from PyQt6.QtWidgets import QSlider, QWidget, QApplication, QGraphicsView, \
                            QGraphicsScene, QGraphicsPixmapItem, QLabel, \
                            QSlider, QHBoxLayout,  QVBoxLayout, QGridLayout, QPushButton, \
                            QGraphicsDropShadowEffect, QFileDialog, QFrame

ExitKeys = (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape)
DispWidth, DispHeight = 425, 425
Width, Height = 870, 475 
Blur, Xoff, Yoff, Scale, Rotate, Rgb, Alpha = 11, 8, 8, 100, 0, 125, 125
Color = QColor(Rgb, Rgb, Rgb, Alpha) 

### --------------------- dropshadow.py --------------------
''' dropshadow.py: a dropshadow visualizer, works with .png or .jpg files '''
### --------------------------------------------------------
class DropShadow(QWidget): 
### --------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__()
   
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)

        ctr = QGuiApplication.primaryScreen().availableGeometry().center()
        x = int(((ctr.x() * 2 ) - Width)/2)
        self.setGeometry(x,75,Width,Height)

        self.setFixedSize(Width,Height)
        self.setWindowTitle("a pyqt dropshadow visualizer")

        self.scene.setSceneRect(0,0,DispWidth,DispHeight-2)   
        
        self.pixmap = None 
        self.shadow = None 
        self._rgb, self._alpha = 0, 0
        
        self.sliders = self.setSliders() 
        self.grid    = self.setGrid()
        self.buttons = self.setButtons()
        
        hbox = QHBoxLayout()  
        hbox.addWidget(self.view)
 
        vbox = QVBoxLayout()      
        vbox.addSpacing(0)
        vbox.addWidget(self.sliders, Qt.AlignmentFlag.AlignTop)
        vbox.addWidget(self.grid, Qt.AlignmentFlag.AlignTop)
        vbox.addSpacing(10)
        vbox.addWidget(self.buttons, Qt.AlignmentFlag.AlignBottom)
    
        hbox.addLayout(vbox)    
        self.setLayout(hbox)
        
        self.setStyleSheet("QGraphicsView {\n"  ## seems to work better positioned here
            "background-color: rgb(250,250,250);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "color: rgb(125,125,125);\n"
            "}")
 
        self.enableSliders()  ## false to start
        self.view.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)
          
        self.show()     

### --------------------------------------------------------       
    def addPixmap(self, img):  ## the scene is cleared each new image file                       
        img = QImage(img)             
        img = img.scaled(250, 250,  ## keep it small
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
     
        self.pixmap = QGraphicsPixmapItem()     
        self.pixmap.setPixmap(QPixmap(img))    
        
        self.pixmap.setX((DispWidth-img.width())/2)  ## center it
        self.pixmap.setY((DispHeight-img.height())/2)
        
        QTimer.singleShot(100, self.addShadow)  ## just to be sure          
        self.scene.addItem(self.pixmap)
             
    def addShadow(self):
        self.shadow = QGraphicsDropShadowEffect(blurRadius=Blur, xOffset=Xoff, yOffset=Yoff)
        self.shadow.setColor(Color)
        self.pixmap.setGraphicsEffect(self.shadow)
        self.defaultSliderVals()  ## sets the default slider values - seven in all
             
    def clearScene(self):
        self.shadow = None  
        self.pixmap = None   
        self.scene.clear()  
        self.resetSliderVals()  ## sets slider values to 1
              
### -------------------------------------------------------- 
    def blur(self, val):
        if self.shadow != None: self.shadow.setBlurRadius(val)
        self.blurValue.setText(f'{val:>4}')   

    def xoffSet(self, val):
        if self.shadow != None: self.shadow.setXOffset(val)
        self.xoffValue.setText(f'{val:>4}')   
        
    def yoffSet(self, val):
        if self.shadow != None: self.shadow.setYOffset(val)
        self.yoffValue.setText(f'{val:>4}')   
   
    def rgb(self, val):
        self._rgb = val
        if self.shadow != None: self.shadow.setColor(QColor(val,val,val,self._alpha) ) 
        self.rgbValue.setText("{:3d}".format(val))  
          
    def alpha(self, val):
        self._alpha = val
        if self.shadow != None: self.shadow.setColor(QColor(self._rgb,self._rgb,self._rgb,val) ) 
        self.alphaValue.setText(f'{val:>4}')
                    
    def scale(self, val):
        val = val/100.0    
        self.setOriginPt() 
        if self.pixmap != None: self.pixmap.setScale(val)   
        self.scaleValue.setText(f'{val:>4.2f}%')
            
    def rotate(self, val):
        self.setOriginPt() 
        if self.pixmap != None: self.pixmap.setRotation(val)   
        self.rotateValue.setText(f'{val:>4}')       
                 
    def setOriginPt(self):  
        if self.pixmap != None:   
            b = self.pixmap.boundingRect()
            op = QPointF(b.width()/2, b.height()/2)
            self.pixmap.setTransformOriginPoint(op)
            self.pixmap.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        
### -------------------------------------------------------- 
    def enableSliders(self, bool=False): 
        self.sliderGroup.setEnabled(bool)
    
    def defaultSliderVals(self):
        self.blurSlider.setValue(Blur) 
        self.xoffSlider.setValue(Xoff)
        self.yoffSlider.setValue(Yoff)
        self.rgbSlider.setValue(Rgb)
        self.alphaSlider.setValue(Alpha)        
        self.scaleSlider.setValue(Scale)
        self.rotateSlider.setValue(Rotate)                   

    def resetSliderVals(self):
        self.blurSlider.setValue(1) 
        self.xoffSlider.setValue(1)
        self.yoffSlider.setValue(1)
        self.rgbSlider.setValue(1)
        self.alphaSlider.setValue(1)        
        self.scaleSlider.setValue(100)
        self.rotateSlider.setValue(1)

    def setSliders(self):     
        self.sliderGroup = QLabel()
        self.sliderGroup.setFixedSize(385,365)
        
        self.setStyleSheet('QLabel{font-size: 13pt;}')
      
        self.blurLabel = QLabel('Blur')
        self.blurValue = QLabel("1", alignment=Qt.AlignmentFlag.AlignRight)
        self.blurSlider = QSlider(Qt.Orientation.Horizontal,                            
            minimum=1, maximum=100,             
            singleStep=1, value=1, valueChanged=self.blur)
     
        self.xoffLabel = QLabel("XOffSet")
        self.xoffValue = QLabel("1", alignment=Qt.AlignmentFlag.AlignRight)
        self.xoffSlider = QSlider(Qt.Orientation.Horizontal, 
            minimum=-200, maximum=200,
            singleStep=1, value=1, valueChanged=self.xoffSet)
        
        self.yoffLabel = QLabel("YOffSet")
        self.yoffValue = QLabel("1", alignment=Qt.AlignmentFlag.AlignRight)
        self.yoffSlider = QSlider(Qt.Orientation.Horizontal, 
            minimum=-200, maximum=200,
            singleStep=1, value=1, valueChanged=self.yoffSet)
        
        self.rgbLabel = QLabel("Rgb")
        self.rgbValue = QLabel("1", alignment=Qt.AlignmentFlag.AlignRight)
        self.rgbSlider = QSlider(Qt.Orientation.Horizontal, 
            minimum=0, maximum=255,
            singleStep=1, value=1, valueChanged=self.rgb)        
        
        self.alphaLabel = QLabel("Alpha")
        self.alphaValue = QLabel("1", alignment=Qt.AlignmentFlag.AlignRight)
        self.alphaSlider = QSlider(Qt.Orientation.Horizontal, 
            minimum=0, maximum=255,
            singleStep=1, value=1, valueChanged=self.alpha)        
        
        self.scaleLabel = QLabel("Scale")
        self.scaleValue = QLabel("1.00%", alignment=Qt.AlignmentFlag.AlignHCenter)
        self.scaleSlider = QSlider(Qt.Orientation.Horizontal, 
            minimum=50, maximum=150,
            singleStep=1, value=1, valueChanged=self.scale)
        
        self.rotateLabel = QLabel("Rotate")
        self.rotateValue = QLabel("1", alignment=Qt.AlignmentFlag.AlignRight)
        self.rotateSlider = QSlider(Qt.Orientation.Horizontal, 
            minimum=-360, maximum=360,
            singleStep=1, value=1, valueChanged=self.rotate)

### --------------------------------------------------------       
    def setGrid(self):      
        widget = QWidget()
        grid = QGridLayout(widget) 
 
        grid.addWidget(self.blurLabel, 0, 0)
        grid.addWidget(self.blurValue, 0, 1)    
        grid.addWidget(self.blurSlider, 1, 0)
        
        grid.addWidget(self.xoffLabel, 2, 0)
        grid.addWidget(self.xoffValue, 2, 1)        
        grid.addWidget(self.xoffSlider, 3, 0)

        grid.addWidget(self.yoffLabel, 4, 0)
        grid.addWidget(self.yoffValue, 4, 1)    
        grid.addWidget(self.yoffSlider, 5, 0)
    
        grid.addWidget(self.rgbLabel, 6, 0)
        grid.addWidget(self.rgbValue, 6, 1) 
        grid.addWidget(self.rgbSlider, 7, 0) 
    
        grid.addWidget(self.alphaLabel, 8, 0)
        grid.addWidget(self.alphaValue, 8, 1) 
        grid.addWidget(self.alphaSlider, 9, 0)
    
        grid.addWidget(self.scaleLabel, 10, 0)
        grid.addWidget(self.scaleValue, 10, 1) 
        grid.addWidget(self.scaleSlider, 11, 0)
        
        grid.addWidget(self.rotateLabel, 12, 0)
        grid.addWidget(self.rotateValue, 12, 1)
        grid.addWidget(self.rotateSlider, 13, 0)
                                  
        grid.setContentsMargins(-10, -5, 10, -15)
             
        vbox = QVBoxLayout(self)                       
        vbox.addWidget(widget) 
        
        self.sliderGroup.setLayout(vbox)
        self.sliderGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
        self.sliderGroup.setLineWidth(1)

        return self.sliderGroup
 
### --------------------------------------------------------    
    def setButtons(self): 
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedSize(385,50)
        
        self.filesBtn = QPushButton("Files")      
        self.filesBtn.clicked.connect(self.openFiles)
        
        self.clearBtn = QPushButton("Clear")
        self.clearBtn.clicked.connect(self.clearScene)
        
        self.quitBtn = QPushButton("Quit")
        self.quitBtn.clicked.connect(self.close)
        
        hbox = QHBoxLayout(self)
        hbox.addWidget(self.filesBtn)
        hbox.addSpacing(50)        
        hbox.addWidget(self.clearBtn)
        hbox.addSpacing(50)
        hbox.addWidget(self.quitBtn)
            
        self.buttonGroup.setLayout(hbox)
        self.buttonGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
        self.buttonGroup.setLineWidth(1)
  
        return self.buttonGroup
    
### --------------------------------------------------------               
    def openFiles(self):
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self,
            "Choose an image file to open", "", "Images Files( *.jpg *.png)")
        if file and file.lower().endswith('.png') or file.lower().endswith('.jpg'):
            self.scene.clear()
            self.enableSliders(True)  ## sets defaults
            self.addPixmap(file)
              
    def keyPressEvent(self, e):
        if e.key() in ExitKeys:
            self.close()

### -------------------------------------------------------- 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    drop = DropShadow()
    sys.exit(app.exec())
    
### --------------------- dropshadow.py --------------------
    
 
 
    