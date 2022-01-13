
import sys
import os

import pygame as pg
from   pygame.constants import HIDDEN

from PyQt5.QtCore       import Qt, QPointF
from PyQt5.QtGui        import QColor, QImage, QPixmap, QFont, QPolygonF, QPen
from PyQt5.QtWidgets    import QWidget, QApplication, QGraphicsView, QMessageBox, \
                               QGraphicsScene, QGraphicsPixmapItem, QLabel, \
                               QHBoxLayout,  QVBoxLayout, QPushButton, \
                               QFileDialog, QFrame,  QGraphicsPolygonItem
from PyQt5.QtSvg        import QGraphicsSvgItem
## from PyQt6.QtSvgWidgets import QGraphicsSvgItem

DispWidth, DispHeight = 450, 450
Width, Height = 495, 560 
Max = 350

### --------------------------------------------------------
''' outline.py: outline a transparent .png using a pygame function'''
### --------------------------------------------------------
class Display(QWidget): 
    def __init__(self, parent):
        super(Display, self).__init__(parent)
        
        self.cas = parent
             
        self.setStyleSheet("QWidget {\n"
            "background-color: rgb(255,255,255);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "color: rgb(125,125,125);\n"
            "}")
              
        view = QGraphicsView(self)
        self.scene = QGraphicsScene()
        view.setScene(self.scene)
        
        self.scene.setSceneRect(0,0,DispWidth,DispHeight)   
        
        self.pixmap = None 
     
    def addPixmap(self, file):  ## the scene is cleared each new image file                            
        img = QImage(file)     
                
        self.file = file  
        img = img.scaled(Max, Max,  
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
     
        self.pixmap = QGraphicsPixmapItem()     
        self.pixmap.setPixmap(QPixmap(img))    
        
        self.x = (DispWidth-img.width())/2 
        self.y = (DispHeight-img.height())/2
        
        self.pixmap.setX(self.x)  ## center it
        self.pixmap.setY(self.y)
                      
        self.scene.addItem(self.pixmap)
             
    def displayOutline(self, type="pts"): 
        if not self.pixmap:  
            return  
        pts = getOutline(self.file, self.pixmap.boundingRect(), type)
        if type == 'pts':  
            self.poly = QGraphicsPolygonItem(self.drawPoly(pts)) 
            self.poly.setPen(QPen(QColor("lime"), 2, Qt.PenStyle.DotLine))
            self.poly.setZValue(100) 
            self.poly.setPos(self.x, self.y)
            self.scene.addItem(self.poly)
                        
    def drawPoly(self, pts):  
        poly = QPolygonF()   
        for p in pts: 
            poly.append(QPointF(p[0], p[1]))
        return poly    
    
    def addSvg(self, file):
        svg = QGraphicsSvgItem(file)
        b = svg.boundingRect()   
        w, h = b.width(), b.height()
        r = max(w, h )    
        if r > Max:
            r = Max/r
        else:
            r = r/Max
        svg.setScale(r)
        x = (DispWidth-(w*r))/2 
        y = (DispHeight-(h*r))/2
        svg.setPos(x,y)
        self.scene.addItem(svg)
                                                    
### --------------------------------------------------------      
class Caster(QWidget):  
    def __init__(self):
        super(Caster, self).__init__()

        self.font = QFont()
        self.setFont(QFont('Helvetica', 13))
        
        self.setFixedSize(Width,Height)
        self.setWindowTitle("outline a transparent .png")
        
        self.setTabletTracking(False)
             
        self.display = Display(self)
        self.buttons = self.setButtons()
                     
        vbox = QVBoxLayout()    
        vbox.addWidget(self.display, Qt.AlignmentFlag.AlignHCenter)  
        vbox.addSpacing(5)
        vbox.addWidget(self.buttons, Qt.AlignmentFlag.AlignHCenter)
    
        self.setLayout(vbox)
              
        self.show()   
 
 ### --------------------------------------------------------   
    def setButtons(self): 
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedSize(DispWidth, 50)
        
        self.filesBtn = QPushButton("Files")      
        self.filesBtn.clicked.connect(self.openFiles)
        
        self.polyBtn = QPushButton("Points")      
        self.polyBtn.clicked.connect(lambda: self.display.displayOutline("pts"))
        
        self.pathBtn = QPushButton("Path")      
        self.pathBtn.clicked.connect(lambda: self.display.displayOutline("path"))
        
        self.svgBtn = QPushButton("SVG")      
        self.svgBtn.clicked.connect(lambda: self.display.displayOutline("svg"))
    
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
        hbox.addWidget(self.quitBtn)
            
        self.buttonGroup.setLayout(hbox)
        self.buttonGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
        self.buttonGroup.setLineWidth(1)
  
        return self.buttonGroup
                  
    def openFiles(self):
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self,
            "Choose an image file to open", "", "Images Files( *.jpg *.png *.svg)")
        self.display.scene.clear()
        if file:     
            if file.lower().endswith('.png') or file.lower().endswith('.jpg'):
                self.display.addPixmap(file)
            else:
                self.display.addSvg(file)
        Q.accept()
                        
def getOutline(file, b, type):  ## b -> boundingRect
    pg.init()
    
    threshold = 100
    pg.display.set_mode((0,0), HIDDEN)
    
    image = pg.image.load(file).convert_alpha()
    image = pg.transform.smoothscale(image, (b.width(), b.height()))
    
    mask = pg.mask.from_surface(image, threshold)  
    dots = 200  ## the limiting factor 
    
    for i in range(3, 20):     ## save every 3rd, 4th, ... 20th point 
        pts = mask.outline(i)  ## default is 1, all
        if len(pts) < dots:    ## set a limit otherwise you could get 1000's
            dots = i  ## save the winning number     
            break

    pts = []
    for p in mask.outline(dots):  ## once more for real
        pts.append(p)
                 
    if type in ("path", "svg"): 
        savePoints(file, type, b, pts)   
    else: 
        QMessageBox.about(None, "OutLine", os.path.basename(file) + 
                                "{0:4d}".format(len(pts)) + " points")             
    return pts

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cas = Caster()
    sys.exit(app.exec())
    