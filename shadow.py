
import sys

from PyQt5.QtCore    import Qt, QTimer, QPointF
from PyQt5.QtGui     import QColor, QImage, QPixmap, QFont
from PyQt5.QtWidgets import QSlider, QWidget, QApplication, QGraphicsView, \
                            QGraphicsScene, QGraphicsPixmapItem, QLabel, \
                            QSlider, QHBoxLayout,  QVBoxLayout, QGridLayout, QPushButton, \
                            QGraphicsDropShadowEffect, QFileDialog, QFrame

ExitKeys = (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape)
DispWidth, DispHeight = 425, 425
Width, Height = 870, 475 
Blur, Xoff, Yoff, Scale, Rotate, Rgb, Alpha = 11, 8, 8, 100, 0, 125, 125
Color = QColor(Rgb, Rgb, Rgb, Alpha) 

### --------------------------------------------------------
''' shadow.py: a dropshadow visualizer, works with .png or .jpg files '''
### --------------------------------------------------------
class Display(QWidget): 
    def __init__(self, parent):
        super(Display, self).__init__(parent)
        
        self.setStyleSheet("QWidget {\n"
            "background-color: rgb(250,250,250);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "color: rgb(125,125,125);\n"
            "}")
      
        self.cas = parent
         
        view = QGraphicsView(self)
        self.scene = QGraphicsScene()
        view.setScene(self.scene)

        self.scene.setSceneRect(0,0,DispWidth,DispHeight)   
        
        self.pixmap = None 
        self.shadow = None 
        self._rgb, self._alpha = 0, 0
  
  ### --------------------------------------------------------       
    def addPixmap(self, img):  ## the scene is cleared each new image file                     
        ## name = os.path.basename(img)  ##  use it for testing 
        
        img = QImage(img)             
        img = img.scaled(250, 250,  ## keep it small
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
     
        self.pixmap = QGraphicsPixmapItem()     
        self.pixmap.setPixmap(QPixmap(img))    
        
        self.pixmap.setX((DispWidth-img.width())/2)  ## center it
        self.pixmap.setY((DispHeight-img.height())/2)
        
        QTimer.singleShot(200, self.addShadow)  ## just to be sure
              
        self.scene.addItem(self.pixmap)
             
    def addShadow(self):
        self.shadow = QGraphicsDropShadowEffect(blurRadius=Blur, xOffset=Xoff, yOffset=Yoff)
        self.shadow.setColor(Color)
        self.pixmap.setGraphicsEffect(self.shadow)
        self.resetSliders()
        
    def blur(self, val):
        self.shadow.setBlurRadius(val)
        self.cas.blurValue.setText("{:3d}".format(val))

    def xoffSet(self, val):
        self.shadow.setXOffset(val)
        self.cas.xoffValue.setText("{:3d}".format(val))
        
    def yoffSet(self, val):
        self.shadow.setYOffset(val)
        self.cas.yoffValue.setText("{:3d}".format(val))
   
    def rgb(self, val):
        self._rgb = val
        self.shadow.setColor(QColor(val,val,val,self._alpha) ) 
        self.cas.rgbValue.setText("{:3d}".format(val))  
          
    def alpha(self, val):
        self._alpha = val
        self.shadow.setColor(QColor(self._rgb,self._rgb,self._rgb,val) ) 
        self.cas.alphaValue.setText("{:3d}".format(val)) 
                    
    def scale(self, val):
        val = val/100.0    
        self.setOriginPt() 
        self.pixmap.setScale(val)   
        self.cas.scaleValue.setText("{0:.2f}%".format(val))
            
    def rotate(self, val):
        self.setOriginPt() 
        self.pixmap.setRotation(val)   
        self.cas.rotateValue.setText("{:3d}".format(val))        
            
    def resetSliders(self):
        self.cas.blurSlider.setValue(Blur)  ## default
        self.cas.xoffSlider.setValue(Xoff)
        self.cas.yoffSlider.setValue(Yoff)
        self.cas.rgbSlider.setValue(Rgb)
        self.cas.alphaSlider.setValue(Alpha)        
        self.cas.scaleSlider.setValue(Scale)
        self.cas.rotateSlider.setValue(Rotate)
        
    def setOriginPt(self):    
        b = self.pixmap.boundingRect()
        op = QPointF(b.width()/2, b.height()/2)
        self.pixmap.setTransformOriginPoint(op)
        self.pixmap.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        
### --------------------------------------------------------      
class Caster(QWidget):  
    def __init__(self):
        super(Caster, self).__init__()

        self.font = QFont()
        self.setFont(QFont('Helvetica', 13))
        
        self.setFixedSize(Width,Height)
        self.setWindowTitle("a dropshadow visualizer")
     
        self.display = Display(self)
        self.sliders = self.setSliders() 
        self.buttons = self.setButtons()
       
        hbox = QHBoxLayout() 
        hbox.addWidget(self.display, Qt.AlignmentFlag.AlignBottom)
               
        vbox = QVBoxLayout()      
        vbox.addSpacing(-8)
        vbox.addWidget(self.sliders, Qt.AlignmentFlag.AlignTop)
        vbox.addSpacing(5)
        vbox.addWidget(self.buttons, Qt.AlignmentFlag.AlignBottom)
    
        hbox.addLayout(vbox)    
        self.setLayout(hbox)
        
        self.enableSliders()  ## false to start
        
        self.show()   
 
 ### --------------------------------------------------------                                         
    def enableSliders(self, bool=False): 
        self.sliderGroup.setEnabled(bool)
                       
    def setSliders(self):     
        self.sliderGroup = QLabel()
        self.sliderGroup.setFixedSize(385,355)
             
        blurLabel = QLabel('Blur')
        blurLabel.setFont(self.font)
        self.blurValue = QLabel("1")
        self.blurSlider = QSlider(Qt.Orientation.Horizontal,                            
            minimum=1, maximum=100, singleStep=1, value=1)
        self.blurSlider.valueChanged.connect(self.display.blur)
        
        xoffLabel = QLabel("XOffSet")
        xoffLabel.setFont(self.font)
        self.xoffValue = QLabel("1")
        self.xoffSlider = QSlider(Qt.Orientation.Horizontal, 
            minimum=-200, maximum=200, singleStep=1, value=1)
        self.xoffSlider.valueChanged.connect(self.display.xoffSet)
        
        yoffLabel = QLabel("YOffSet")
        yoffLabel.setFont(self.font)
        self.yoffValue = QLabel("1")
        self.yoffSlider = QSlider(Qt.Orientation.Horizontal, 
            minimum=-200, maximum=200, singleStep=1, value=1)
        self.yoffSlider.valueChanged.connect(self.display.yoffSet)
        
        rgbLabel = QLabel("Rgb")
        rgbLabel.setFont(self.font)
        self.rgbValue = QLabel("1")
        self.rgbSlider = QSlider(Qt.Orientation.Horizontal, 
            minimum=0, maximum=255, singleStep=1, value=1)
        self.rgbSlider.valueChanged.connect(self.display.rgb)   
              
        alphaLabel = QLabel("Alpha")
        alphaLabel.setFont(self.font)
        self.alphaValue = QLabel("1")
        self.alphaSlider = QSlider(Qt.Orientation.Horizontal, 
            minimum=0, maximum=255, singleStep=1, value=1)
        self.alphaSlider.valueChanged.connect(self.display.alpha)  
             
        scaleLabel = QLabel("Scale")
        scaleLabel.setFont(self.font)
        self.scaleValue = QLabel("1.00%")
        self.scaleSlider = QSlider(Qt.Orientation.Horizontal, 
            minimum=50, maximum=150, singleStep=1, value=1)
        self.scaleSlider.valueChanged.connect(self.display.scale)  
        
        rotateLabel = QLabel("Rotate")
        rotateLabel.setFont(self.font)
        self.rotateValue = QLabel("1")
        self.rotateSlider = QSlider(Qt.Orientation.Horizontal, 
            minimum=-360, maximum=360, singleStep=1, value=1)
        self.rotateSlider.valueChanged.connect(self.display.rotate)  
                 
        widget = QWidget()
        grid = QGridLayout(widget) 
        grid.addWidget(blurLabel, 0, 0)
        grid.addWidget(self.blurValue, 0, 1)    
        grid.addWidget(self.blurSlider, 1, 0)
        
        grid.addWidget(xoffLabel, 2, 0)
        grid.addWidget(self.xoffValue, 2, 1)        
        grid.addWidget(self.xoffSlider, 3, 0)

        grid.addWidget(yoffLabel, 4, 0)
        grid.addWidget(self.yoffValue, 4, 1)    
        grid.addWidget(self.yoffSlider, 5, 0)
    
        grid.addWidget(rgbLabel, 6, 0)
        grid.addWidget(self.rgbValue, 6, 1) 
        grid.addWidget(self.rgbSlider, 7, 0) 
    
        grid.addWidget(alphaLabel, 8, 0)
        grid.addWidget(self.alphaValue, 8, 1) 
        grid.addWidget(self.alphaSlider, 9, 0)
    
        grid.addWidget(scaleLabel, 10, 0)
        grid.addWidget(self.scaleValue, 10, 1) 
        grid.addWidget(self.scaleSlider, 11, 0)
        
        grid.addWidget(rotateLabel, 12, 0)
        grid.addWidget(self.rotateValue, 12, 1)
        grid.addWidget(self.rotateSlider, 13, 0)
                                  
        grid.setContentsMargins(20, -5, 0, -15)
             
        vbox = QVBoxLayout(self)                       
        vbox.addWidget(widget) 
        
        self.sliderGroup.setLayout(vbox)
        self.sliderGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
        self.sliderGroup.setLineWidth(1)

        return self.sliderGroup
    
    def setButtons(self): 
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedSize(385,50)
        
        self.filesBtn = QPushButton("Files")      
        self.filesBtn.clicked.connect(self.openFiles)
        
        self.quitBtn = QPushButton("Quit")
        self.quitBtn.clicked.connect(self.close)
        
        hbox = QHBoxLayout(self)
        hbox.addWidget(self.filesBtn)
        hbox.addSpacing(150)
        hbox.addWidget(self.quitBtn)
            
        self.buttonGroup.setLayout(hbox)
        self.buttonGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
        self.buttonGroup.setLineWidth(1)
  
        return self.buttonGroup
                  
    def openFiles(self):
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self,
            "Choose an image file to open", "", "Images Files( *.jpg *.png)")
        if file and file.lower().endswith('.png') or file.lower().endswith('.jpg'):
            self.display.scene.clear()
            self.enableSliders(True)  
            self.display.addPixmap(file)
              
    def keyPressEvent(self, e):
        if e.key() in ExitKeys:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cas = Caster()
    sys.exit(app.exec())
    


