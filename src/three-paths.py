
import sys
import os

from PyQt6.QtCore       import Qt, QPointF, pyqtProperty, QPropertyAnimation, QObject 
from PyQt6.QtGui        import QGuiApplication, QPainterPath, QPixmap
from PyQt6.QtWidgets    import QWidget, QApplication, QGraphicsView, QMessageBox, \
                                QGraphicsScene, QLabel, QFrame, QGraphicsPixmapItem, \
                                QHBoxLayout, QVBoxLayout, QPushButton
                                 
from dotsShared         import paths  ## for use.path and sprite

ViewW, ViewH, Width = 650, 500, 695

### ------------------- three-paths.py --------------------- 
''' This app relies on imports from dots sprite and path directories
    and needs be run in the dots source directory in order to work. 
    There's an edit to ptqtproperty for pyside - need to drop pyqt. '''
### -------------------------------------------------------- 
class Node(QObject):
### --------------------------------------------------------
    def __init__(self, pix):
        super().__init__()
        
        self.pix = pix

    def _setPos(self, pos):
        try:
            self.pix.setPos(pos)
        except RuntimeError:
            return None
        
    pos =  pyqtProperty(QPointF, fset=_setPos)  ## needs an edit for pyside
        
### --------------------------------------------------------  
class Test(QWidget):  
### --------------------------------------------------------
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("animation test")
        
        self.scene = QGraphicsScene(0, 0, ViewW, ViewH)
        self.view = QGraphicsView(self.scene)
   
        ctr = QGuiApplication.primaryScreen().availableGeometry().center()
        x = int(((ctr.x() * 2 ) - Width)/2)
        self.move(x, 250) 
        
        self.animation = None
        self.file   = None 
        self.pix    = None
        self.three  = False 
        self.first  = QPointF() 
       
        self.setStyleSheet("QGraphicsView {\n"
            "border: 1px solid rgb(125,125,125);\n"
            "color: rgb(125,125,125);\n"
            "}") 
                       
        hbox = QHBoxLayout()            
        hbox.addWidget(self.view) 
                 
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.setButtons(), Qt.AlignmentFlag.AlignHCenter)
               
        self.setLayout(vbox)
        
        self.pix = QGraphicsPixmapItem()    
        self.pix.setPixmap(QPixmap(paths['spritePath'] + "apple.png"))

        self.pix.setScale(.20)
        self.pix.setPos(0,0)
        
        self.first = QPointF()
         
        self.scene.addItem(self.pix)
        self.node = Node(self.pix)

        self.show()
     
### --------------------------------------------------------
    def setUp(self):
        if self.animation != None:
            self.animation.stop()   
        self.animation = QPropertyAnimation(self.node, b"pos") 
        self.animation.setDuration(2000) # Duration in milliseconds
        self.animation.setStartValue(QPointF(0, 0))
                    
    def pathOne(self):
        self.setUp()
        self.three = False; self.pathBtnThree.setText('Path Three')
        self.animation.setEndValue(QPointF(ViewW-110, ViewH-110))    
        self.animation.start()
        
    def pathTwo(self):
        self.setUp()  
        self.three = False; self.pathBtnThree.setText('Path Three')
        path = QPainterPath()
        path.moveTo(0, 00)
        path.cubicTo(0, 0, 250, 875, 550, 0) 

        vals = [p/100 for p in range(0, 101)]
        for i in vals:
            self.animation.setKeyValueAt(i, path.pointAtPercent(i))           
        self.animation.setEndValue(QPointF(550, 0)) 
        self.animation.start()
  
    def pathThree(self):
        if self.three == True:
            self.three = False
            self.animation.stop()  
            self.pix.setPos(0, 0)
            self.pathBtnThree.setText('Path Three')
        else:
            self.wuf()
       
    def wuf(self): 
        self.setUp()    
        self.three = True  
        self.first = QPointF()
        path = self.pathLoader('three.path') 
        
        if path == None:
            self.pix.setPos(0,0)
            return
        
        self.x = int(self.first.x()); self.y = int(self.first.y())          
        path.moveTo(self.x, self.y)   
    
        self.animation.setDuration(4000) # Duration in milliseconds
        vals = [p/100 for p in range(0, 101)]
        
        for i in vals:
            self.animation.setKeyValueAt(i, path.pointAtPercent(i))           
        self.animation.setEndValue(QPointF(self.x, self.y)) 
        
        self.pathBtnThree.setText('Stop')
        self.animation.setLoopCount(-1)
     
        del path
        self.animation.start()
                
    def pathLoader(self, path): 
        file = paths['paths'] + path  ## paths directory
        path = QPainterPath()  
        try:
            with open(file, 'r') as fp:
                for line in fp:
                    ln = line.rstrip()  
                    ln = list(map(float, ln.split(',')))
                    ln[0] = ln[0] - 275  
                    ln[1] = ln[1] - 175 
                    if not path.elementCount():
                        path.moveTo(QPointF(ln[0], ln[1]))
                        self.first = QPointF(ln[0], ln[1])
                    path.lineTo(QPointF(ln[0], ln[1])) 
        except IOError:
            msg = QMessageBox(self)
            msg.setText(f'pathLoader: Error loading pathFile, {os.path.basename(file)}') 
            msg.exec()     
            return None             
        path.closeSubpath()
        return path

    def clearScene(self):
        self.file = None  
        self.scene.clear()

    def setOriginPt(self):                 
        b = self.pix.boundingRect()
        op = QPointF(b.width()/2, b.height()/2)
        self.pix.setTransformOriginPoint(op)
        self.pix.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
                                          
### --------------------------------------------------------   
    def setButtons(self): 
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedSize(ViewW+5, 50)
        
        self.pathBtnOne = QPushButton("Path One")      
        self.pathBtnOne.clicked.connect(self.pathOne)
        
        self.pathBtnTwo = QPushButton("Path Two")      
        self.pathBtnTwo.clicked.connect(self.pathTwo)

        self.pathBtnThree = QPushButton("Path Three")
        self.pathBtnThree.clicked.connect(self.pathThree)
    
        self.threeBtn = QPushButton("Quit")
        self.threeBtn.clicked.connect(self.close)
        
        hbox = QHBoxLayout(self)
        
        hbox.addWidget(self.pathBtnOne)
        hbox.addSpacing(5)
        
        hbox.addWidget(self.pathBtnTwo)
        hbox.addSpacing(5)     
          
        hbox.addWidget(self.pathBtnThree)
        hbox.addSpacing(5)     
          
        hbox.addWidget(self.threeBtn)
            
        self.buttonGroup.setLayout(hbox)
        self.buttonGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
        self.buttonGroup.setLineWidth(1)
  
        return self.buttonGroup          

### --------------------------------------------------------  
if __name__ == '__main__':
    app = QApplication(sys.argv)
    out = Test()
    sys.exit(app.exec())

### ----------------------- test.py ------------------------   



    