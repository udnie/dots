
import sys
import os

import cv2

# import pygame as pg
# from   pygame.constants import HIDDEN

from PyQt6.QtCore       import Qt, QPointF, QTimer
from PyQt6.QtGui        import QColor, QImage, QPixmap, QPolygonF, QPen, \
                               QGuiApplication
from PyQt6.QtWidgets    import QWidget, QApplication, QGraphicsView, QMessageBox, \
                               QGraphicsScene, QGraphicsPixmapItem, QLabel, \
                               QHBoxLayout,  QVBoxLayout, QPushButton, \
                               QFileDialog, QFrame,  QGraphicsPolygonItem
                               
from PyQt6.QtSvgWidgets import QGraphicsSvgItem  ## py-qt6
##from PyQt5.QtSvg      import QGraphicsSvgItem  ## py-qt5

ViewW, ViewH = 650, 650
Width, Height = 695, 760
MaxPts = 200  ## limiting factor
ImgWH  = 600  ## width/height

### ---------------------- outline.py ----------------------
''' Outline a transparent .png using a pygame function or opencv.
    You will need to have installed opencv, required, or pygame 
    to use this. Pygame wouldn't install in python 3.14 at the time
    of writing. GraphicsSvgItem changes SVG module name in py-qt5 and is 
    taken care of when you run the appropriate script. Double-click to 
    toggle between opencv or pygame if both are installed. '''       
### --------------------------------------------------------      
class Outline(QWidget):  
### --------------------------------------------------------
    def __init__(self):
        super(Outline, self).__init__()
        
        self.setWindowTitle("outline a transparent .png")
        
        self.setUI()
        self.show()   
       
    def mouseDoubleClickEvent(self, e): 
        self.switch = 'pygame' if self.switch == 'opencv' else 'opencv' 
        self.switchBtn.setText(self.switch)  
        e.accept()
        
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
        if self.file == None:
            return                          
        img = QImage(self.file)                 
                
        if img.width() > ImgWH or img.height() > ImgWH:  ## size it to fit
            img = img.scaled(ImgWH, ImgWH,  
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
     
        self.img = QGraphicsPixmapItem()     
        self.img.setPixmap(QPixmap(img))    
        
        self.x = (ViewW-img.width())/2 
        self.y = (ViewH-img.height())/2
    
        self.img.setX(self.x)  ## center it
        self.img.setY(self.y)
                  
        self.scene.addItem(self.img)
                
    def clearScene(self):
        self.file = None  
        self.img = None 
        self.x, self.y = 0, 0
        self.scene.clear()

### --------------------------------------------------------                       
    def addOutLine(self, pts): 
        self.removeOutline()    
        self.poly = QGraphicsPolygonItem(self.drawPoly(pts)) 
        self.poly.setPen(QPen(QColor("lime"), 2, Qt.PenStyle.DotLine))
        self.poly.setZValue(100) 
        self.setXY(self.poly.boundingRect())
        self.poly.setPos(self.x, self.y)
        self.scene.addItem(self.poly)
        
    def removeOutline(self):
        if self.poly != None: 
            try: 
                self.scene.removeItem(self.poly)
            except:
                None
        self.poly = None
         
    def displayOutline(self, type="pts"):  ## save if type in ('path', 'svg') pts = points
        if self.img == None or self.file == None:
            return    
        if pts := makeOutline(self.file, self.img.boundingRect(), type, MaxPts, self.switch):
            self.addOutLine(pts)
         
    def switchPointSource(self):
        if self.img != None:
            self.addPixmap()
            self.displayOutline() 
        else:
            self.scene.clear()

    def addSvg(self):
        svg = QGraphicsSvgItem(self.file)
        self.setXY(svg.boundingRect())
        svg.setPos(self.x, self.y)
        self.scene.addItem(svg)
        
    def setXY(self, b):
        if self.x == 0 and self.y == 0:  ## straight from a file, ('path', 'svg') - not an image 
            self.x = (ViewW-b.width())/2 
            self.y = (ViewH-b.height())/2

    def drawPoly(self, pts): 
        poly = QPolygonF()   
        for p in pts: 
            poly.append(QPointF(float(p[0]), float(p[1])))  
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
    def setUI(self):
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
                       
        self.setFixedSize(Width,Height)     
        self.scene.setSceneRect(0,0,ViewW-2,ViewH-2) 
        
        self.file  = None  
        self.img  = None  
        self.poly = None
        
        self.switch = 'opencv'  ## change default here
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
        ctrx = QGuiApplication.primaryScreen().availableGeometry().center().x()
        
        x = int(((ctrx * 2 ) - Width)/2)
        self.move(x, 175)

### --------------------------------------------------------   
    def setButtons(self): 
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedSize(ViewW+5, 50)
        
        filesBtn = QPushButton("Files")      
        filesBtn.clicked.connect(self.openFiles)
        
        polyBtn = QPushButton("Points")      
        polyBtn.clicked.connect(lambda: self.displayOutline("pts"))
        
        pathBtn = QPushButton("SavePath")      
        pathBtn.clicked.connect(lambda: self.displayOutline("path"))
        
        svgBtn = QPushButton("SaveSVG")      
        svgBtn.clicked.connect(lambda: self.displayOutline("svg"))
        
        self.switchBtn = QPushButton(self.switch)      
        self.switchBtn.clicked.connect(self.switchPointSource)
    
        clearBtn = QPushButton("Clear")
        clearBtn.clicked.connect(self.clearScene)
    
        quitBtn = QPushButton("Quit")
        quitBtn.clicked.connect(self.close)
        
        hbox = QHBoxLayout(self)
        hbox.addWidget(filesBtn)
        hbox.addSpacing(5)
        hbox.addWidget(polyBtn)
        hbox.addSpacing(5)
        hbox.addWidget(pathBtn)
        hbox.addSpacing(5)
        hbox.addWidget(svgBtn)
        hbox.addSpacing(5)       
        hbox.addWidget(self.switchBtn)
        hbox.addSpacing(5)     
        hbox.addWidget(clearBtn)
        hbox.addSpacing(5)    
        hbox.addWidget(quitBtn)
            
        self.buttonGroup.setLayout(hbox)
        self.buttonGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
        self.buttonGroup.setLineWidth(1)
  
        return self.buttonGroup   
 
### --------------------------------------------------------  
def msgbox(str, intv=3000):
    msg = QMessageBox()
    msg.setText(str)
    timer = QTimer(msg)
    timer.setSingleShot(True)
    timer.setInterval(intv)
    timer.timeout.connect(msg.close)
    timer.start()
    msg.exec()
        
## b: boundingRect used by svg - types: 'path', 'svg' and 'pts' for points                 
def makeOutline(file, b, type, max, switch): 
    if switch == 'opencv':
        pts = getCVPoints(file, b) ## this uses opencv
        
    elif switch == 'pygame':
        pts = getPgPoints(file, b) ## this uses pygame and doesn't run in python 3.14 

    if pts == None:
        msgbox('Error makeOutline: Reading Image File')
        return None

    tmp, use = [], 1
    if len(pts) > max:
        for i in range(2, 25): 
            use = int((len(pts))/i)
            if use < max:
                use = i
                break

    for i in range(len(pts)):  ## just the ones to use
        if i % use == 0:
            tmp.append(pts[i])
        
    if type == 'pts':  ## just get the points
        msgbox(f'OutLine: {os.path.basename(file)}  points: {len(pts)}  used: {len(tmp)} ')
        return tmp    
    else:
        if pts := savePoints(file, type, b, tmp):
            msgbox( f'OutLine: {os.path.basename(file)} saved')  
        else:
            msgbox( f'OutLine: {os.path.basename(file)} not saved')    

### -------------------------------------------------------- 
def getPgPoints(file, b):  ## pygame version -   
    try:
        pg.init() 
    except:
        msgbox("error in getPgPoints", 3)
        return
    
    threshold = 100
    pg.display.set_mode((0,0), HIDDEN)
    
    image = pg.image.load(file).convert_alpha()
    image = pg.transform.smoothscale(image, (b.width(), b.height()))
               
    mask = pg.mask.from_surface(image, threshold)    
    pts = mask.outline()
           
    pg.quit() 
    
    return pts

### --------------------------------------------------------    
def getCVPoints(file, b):  ## opencv version - cobbled together from google queries  
    img = cv2.imread(file, cv2.IMREAD_UNCHANGED)
    w, h = int(b.width()), int(b.height())  
    
    img = cv2.resize(img, (w,h), interpolation=cv2.INTER_AREA)    
    alpha_channel = img[:, :, 3]
    
    _, thresh = cv2.threshold(alpha_channel, 1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
     
    for cnt in contours:
        pts = [tuple(point[0]) for point in cnt]

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
        try:         
            with open(f[0], 'w') as fp:
                for p in pts:
                    x = f"{p[0]:.2f}" 
                    y = f"{p[1]:.2f}" 
                    fp.write(x + ", " + y + "\n")
                fp.close()  
        except:
            return
        return True
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
        try: 
            f = open(f[0], "w")
            f.write(out_str + end_str)
            f.close()     
        except:
            return  
        return True

### --------------------------------------------------------  
if __name__ == '__main__':
    app = QApplication(sys.argv)
    out = Outline()
    sys.exit(app.exec())
    
### ---------------------- outline.py ----------------------



    