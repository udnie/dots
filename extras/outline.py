
import sys
import os

import pygame as pg
from   pygame.constants import HIDDEN

from PyQt6.QtCore       import Qt, QPointF
from PyQt6.QtGui        import QColor, QImage, QPixmap, QPolygonF, QPen, \
                               QGuiApplication
from PyQt6.QtWidgets    import QWidget, QApplication, QGraphicsView, QMessageBox, \
                               QGraphicsScene, QGraphicsPixmapItem, QLabel, \
                               QHBoxLayout,  QVBoxLayout, QPushButton, \
                               QFileDialog, QFrame,  QGraphicsPolygonItem
from PyQt6.QtSvgWidgets import QGraphicsSvgItem

DispWidth, DispHeight = 650, 650
Width, Height = 695, 760
MaxPts = 350  ## limiting factor
ImgWH  = 600  ## width/height

### ---------------------- outline.py ----------------------
''' outline.py: outline a transparent .png using a pygame function'''
### --------------------------------------------------------      
class Outline(QWidget):  
### --------------------------------------------------------
    def __init__(self):
        super(Outline, self).__init__()
        
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
                 
        ctr = QGuiApplication.primaryScreen().availableGeometry().center()
        x = int(((ctr.x() * 2 ) - Width)/2)
        self.setGeometry(x,135,Width,Height)
        
        self.setFixedSize(Width,Height)     
        self.setWindowTitle("outline a transparent .png")
    
        self.scene.setSceneRect(0,0,DispWidth-2,DispHeight-2) 
        
        self.file = None  
        self.pixmap = None  
        self.x, self.y = 0, 0
        
        self.buttons = self.setButtons()
                        
        hbox = QHBoxLayout()            
        hbox.addWidget(self.view) 
                 
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.buttons, Qt.AlignmentFlag.AlignHCenter)
               
        self.setLayout(vbox)
        
        self.setStyleSheet("QGraphicsView {\n"
            "background-color: rgb(250,250,250);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "color: rgb(125,125,125);\n"
            "}")   
        
        self.view.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False) 
        
        self.show()   
       
### --------------------------------------------------------                
    def openFiles(self):
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self,
            "Choose an image file to open", "", "Images Files( *.jpg *.png *.path *.svg)")
        self.clearScene()
        if file:     
            self.file = file
            if file.lower().endswith('.png') or file.lower().endswith('.jpg'):
                self.addPixmap()
            elif file.lower().endswith('.svg'):
                self.addSvg()
            elif file.lower().endswith('.path'):
                self.addOutLine(self.loadPoints())      
        else:
            self.file = None
        Q.accept()
  
### --------------------------------------------------------        
    def addPixmap(self):  ## the scene is cleared each new image file                            
        img = QImage(self.file)                 
                
        if img.width() > ImgWH or img.height() > ImgWH:  ## size it to fit
            img = img.scaled(ImgWH, ImgWH,  
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
     
        self.pixmap = QGraphicsPixmapItem()     
        self.pixmap.setPixmap(QPixmap(img))    
        
        self.x = (DispWidth-img.width())/2 
        self.y = (DispHeight-img.height())/2
    
        self.pixmap.setX(self.x)  ## center it
        self.pixmap.setY(self.y)
                  
        self.scene.addItem(self.pixmap)
                
    def clearScene(self):
        self.file = None  
        self.pixmap = None 
        self.x, self.y = 0, 0
        self.scene.clear()

### --------------------------------------------------------                       
    def addOutLine(self, pts):       
        self.poly = QGraphicsPolygonItem(self.drawPoly(pts)) 
        self.poly.setPen(QPen(QColor("lime"), 2, Qt.PenStyle.DotLine))
        self.poly.setZValue(100) 
        self.setXY(self.poly.boundingRect())
        self.poly.setPos(self.x, self.y)
        self.scene.addItem(self.poly)
        
    def displayOutline(self, type="pts"):  ## type in ('path', 'svg')
        if not self.pixmap:  
            return  
        if pts := getOutline(self.file, self.pixmap.boundingRect(), type, MaxPts):
            self.addOutLine(pts)

    def addSvg(self):
        svg = QGraphicsSvgItem(self.file)
        self.setXY(svg.boundingRect())
        svg.setPos(self.x, self.y)
        self.scene.addItem(svg)
        
    def setXY(self, b):
        if self.x == 0 and self.y == 0:  ## straight from a file, ('path', 'svg') - not an image 
            self.x = (DispWidth-b.width())/2 
            self.y = (DispHeight-b.height())/2

    def drawPoly(self, pts): 
        poly = QPolygonF()   
        for p in pts: 
            poly.append(QPointF(p[0], p[1]))
        return poly    

    def loadPoints(self):  ## from path file       
        tmp = []
        with open(self.file, 'r') as fp: 
            for line in fp:
                ln = line.rstrip()  
                if len(ln) == 0: 
                    continue  ## skip empty lines
                ln = list(map(float, ln.split(',')))        
                tmp.append((ln[0], ln[1]))               
        return tmp

### --------------------------------------------------------   
    def setButtons(self): 
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedSize(DispWidth+5, 50)
        
        self.filesBtn = QPushButton("Files")      
        self.filesBtn.clicked.connect(self.openFiles)
        
        self.polyBtn = QPushButton("Points")      
        self.polyBtn.clicked.connect(lambda: self.displayOutline("pts"))
        
        self.pathBtn = QPushButton("Path")      
        self.pathBtn.clicked.connect(lambda: self.displayOutline("path"))
        
        self.svgBtn = QPushButton("SVG")      
        self.svgBtn.clicked.connect(lambda: self.displayOutline("svg"))
    
        self.clearBtn = QPushButton("Clear")
        self.clearBtn.clicked.connect(self.clearScene)
    
        self.quitBtn = QPushButton("Quit")
        self.quitBtn.clicked.connect(self.close)
        
        hbox = QHBoxLayout(self)
        hbox.addWidget(self.filesBtn)
        hbox.addSpacing(5)
        hbox.addWidget(self.polyBtn)
        hbox.addSpacing(5)
        hbox.addWidget(self.pathBtn)
        hbox.addSpacing(5)
        hbox.addWidget(self.svgBtn)
        hbox.addSpacing(5)       
        hbox.addWidget(self.clearBtn)
        hbox.addSpacing(5)    
        hbox.addWidget(self.quitBtn)
            
        self.buttonGroup.setLayout(hbox)
        self.buttonGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
        self.buttonGroup.setLineWidth(1)
  
        return self.buttonGroup          

### -------------------------------------------------------- 
## uses a few pygame functions to return a list of points that maps the image outline                     
def getOutline(file, b, type, points):  ## b = boundingRect
    pg.init() 
    
    threshold = 100
    pg.display.set_mode((0,0), HIDDEN)
    
    image = pg.image.load(file).convert_alpha()
    image = pg.transform.smoothscale(image, (b.width(), b.height()))
    
    w, h = str(int(b.width())), str(int(b.height()))            
    mask = pg.mask.from_surface(image, threshold)  
        
    for i in range(3, 20):     ## save every other 3rd, 4th, ... 20th point - keep reducing the number
        pts = mask.outline(i)  ## default is 1, keep going till less than MaxPts(points)
        if len(pts) < points:  ## set a limit otherwise you could get 1000's
            points = i  ## save the winning number     
            break
        
    pts = []
    for p in mask.outline(points):  ## once more for real
        pts.append(p)
                 
    pg.quit()
                 
    if type in ("path", "svg"): 
        savePoints(file, type, b, pts)   
    else: 
        QMessageBox.about(None, "OutLine", os.path.basename(file) + 
            " - " + "{0:4d}".format(len(pts)) + " points" + "\n" +
            "width: " +  w + "  height: " + h)
    return pts
    
### --------------------------------------------------------  
def savePoints(file, type, b, pts):
    if type == "path": 
        file = file[:-4] + ".path"   
    elif type == "svg":  
        file = file[:-4] + ".svg" 
    Q = QFileDialog()
    f = Q.getSaveFileName(None, "", file)
    Q.accept()    
    if len(f[0]) == 0: 
        return
    if type == "path":             
        with open(f[0], 'w') as fp:
            for p in pts:
                x = "{0:.2f}".format(p[0])  
                y = "{0:.2f}".format(p[1])
                fp.write(x + ", " + y + "\n")
            fp.close()  
    else:
        cnt, last = 0, len(pts)-1
        ## not all programs accept this but most do
        out_str = "<svg xmlns='http://www.w3.org/2000/svg'" \
            " viewBox='0 0 " + str(b.width()) + " " + str(b.height()) + "\'>\n <path d=\"M"
        end_str = "\" stroke='#000' stroke-width='1' fill='none'/>\n </svg>"
        for p in pts:
            if cnt == last:
                out_str = out_str + " L"
                out_str += " " + str(p[0]) + " " + str(p[1])
                out_str += " Z"
            else:
                out_str += " " + str(p[0]) + " " + str(p[1])
            cnt += 1
        f = open(f[0], "w")
        f.write(out_str + end_str)
        f.close()     
    QMessageBox.about(None, "OutLine", os.path.basename(file) + " saved")  
    return pts 

### --------------------------------------------------------  
if __name__ == '__main__':
    app = QApplication(sys.argv)
    out = Outline()
    sys.exit(app.exec())
    
### ---------------------- outline.py ----------------------



    