
import os
import cv2
import numpy as np

from PyQt6.QtCore       import QPointF, Qt , QRect, QPoint, QSize
from PyQt6.QtGui        import QColor, QImage, QPixmap, QPainter, QPainterPath, QPolygonF, QPen
from PyQt6.QtWidgets    import QGraphicsPixmapItem, QFileDialog, QWidget
                               
from spritePoints       import MsgBox, Fixed

DispWidth, DispHeight = 720, 720
   
paths = {  ## only place it's used 
    "spritePath": "./sprites/",
    "txy":        "./txy/",
}                

### --------------------------------------------------------    
class Works(QWidget):  ## opens, saves, displays sprites and backgrounds
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
        
        self.spriteMaker = parent
        self.scene       = parent.scene
        self.view        = parent.view
                   
        self.init()
         
### --------------------------------------------------------     
    def init(self):     
        self.bkg     = None
        self.pixGrab = None
        self.sprite  = None
        self.imgCopy = None 
                      
        self.mode = 0  
        self.editingOn = False
                                                     
### --------------------------------------------------------         
    def addPixmap(self, file):  ## inital open - scene cleared each new image file                                          
        img = QImage(file)     
        self.spriteMaker.file = file
        
        if img.width() > Fixed or img.height() > Fixed:  ## size it to fit       
            img = img.scaled(Fixed-50, Fixed-50,  
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
      
        self.spriteMaker.pixmap = QGraphicsPixmapItem()     
        self.spriteMaker.pixmap.setPixmap(QPixmap(img))    
        self.spriteMaker.pixmap.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
        
        self.x = (DispWidth-img.width())/2  ## center it
        self.y = (DispHeight-img.height())/2
        
        self.spriteMaker.pixmap.setX(self.x)  
        self.spriteMaker.pixmap.setY(self.y)     
        self.spriteMaker.pixmap.setZValue(-100) 
                
        self.scene.addItem(self.spriteMaker.pixmap)
        
        self.spriteMaker.outlineSet = False
        self.spriteMaker.enableSliders(True)
        
### -------------------------------------------------------- 
    def background(self):  ## preview selection by changing background
        if self.spriteMaker.pathClosed == False:
            return  

        if self.mode > 1: self.mode = 0  ## only for this function  
               
        img, w, h = self.makeSprite()
        self.addSprite(img) 
               
        p = QPixmap(w, h)  
            
        if self.mode == 0:
            p.fill(QColor(128,128,128,255))
        elif self.mode == 1:
            p.fill(QColor('transparent'))
 
        if self.bkg:
            self.scene.removeItem(self.bkg)                         
        self.bkg = QGraphicsPixmapItem()     
        self.bkg.setPixmap(p)
        self.bkg.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False) 
        self.bkg.setZValue(-50)  ## one up from bottom
        
        self.scene.addItem(self.bkg)
        self.mode += 1   
             
    def edit(self):
        if self.spriteMaker.pathClosed == False:
            return       
        if self.editingOn == False:
            self.spriteMaker.removePointItems()
            self.spriteMaker.addPointItems()
            self.spriteMaker.updateOutline()
            self.redrawSprite()
            self.editingOn = True   
        else:
            self.spriteMaker.removePointItems()
            self.spriteMaker.deleteOutline()
            self.editingOn = False           
 
    def getCrop(self):
        x, y, x1, y1 = 2000.0,2000.0,0.0,0.0
        for p in self.spriteMaker.pts:
            if p.x() < x:
                x = p.x()
            if p.x() > x1:
                x1 = p.x()           
            if p.y() < y:
                y = p.y()
            if p.y() > y1:
                y1 = p.y()  
        return x-5, y-5, (x1-x)+10, (y1-y)+10 
                           
### -------------------------------------------------------- 
    def addSprite(self, img):  ## from which it's saved                     
        height, width, ch = img.shape
        bytesPerLine = ch * width  
             
        img = QImage(img.data, width, height, bytesPerLine, QImage.Format.Format_ARGB32)
         
        if self.sprite:
            self.scene.removeItem(self.sprite)
              
        self.sprite = QGraphicsPixmapItem()     
        self.sprite.setPixmap(QPixmap.fromImage(img))    
        self.sprite.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
        self.sprite.setZValue(0)  ## top of stack -- see loupe
       
        self.scene.addItem(self.sprite)  
                            
    def makeSprite(self, crop=False):  ## final product     
        img = self.imgCopy   
                    
        output = QImage(Fixed, Fixed, QImage.Format.Format_ARGB32)  ## definitely ARGB
        output.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(output) 
        poly = QPolygonF()
        
        for s in self.spriteMaker.pts:
            poly.append(QPointF(s))
    
        path = QPainterPath()     
        path.addPolygon(poly)
   
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
         
        ## add a light-grey semi-transparent border to help with anti-aliasing
        painter.setPen(QPen(QColor(100,100,100,50), 5, Qt.PenStyle.SolidLine))     
        painter.drawPolygon(poly)  
            
        painter.setClipPath(path)  
        painter.drawImage(QPointF(),img)     
        painter.end()
                
        if crop == True:  ## only if saving it 
            x, y, x1, y1 = self.getCrop()
            output = output.copy(int(x), int(y), int(x1), int(y1))  
                
        output = output.convertToFormat(QImage.Format.Format_ARGB32)
                    
        width = output.width()
        height = output.height()
                                                         
        bits = output.bits()  
        bits.setsize(output.sizeInBytes())  ## comment out for pyside - 6.4 still
        
        img = np.array(bits).reshape(height, width, 4)                      
        kernel = np.array([  ## sharpen matrix below
            [0, -1, 0],
            [-1, 5,-1],
            [0, -1, 0]])
        ## try shapening overall - then blur edges
        img = cv2.filter2D(src=img, ddepth=-1, kernel=kernel)
        img = cv2.GaussianBlur(img,(3,3),cv2.BORDER_DEFAULT)
                    
        return img, width, height
                                      
    def redrawSprite(self):
        img, _, _ = self.makeSprite()
        self.addSprite(img)
     
### -------------------------------------------------------- 
    def replacePixmap(self):  ## set from sliders
        ## self.pixGrab is the basis of sprites - view.grab returns a pixmap
        if self.pixGrab:
            self.pixGrab = None
        self.pixGrab = self.spriteMaker.view.grab(QRect(QPoint(2,5), QSize()))
        pixmap = QGraphicsPixmapItem()     
        pixmap.setPixmap(self.pixGrab)     
        pixmap.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
        pixmap.setZValue(-100)  ## bottom layer
        
        if self.spriteMaker.pixmap:
            self.scene.removeItem(self.spriteMaker.pixmap)        
        ## replace the original with a same size copy 
        self.spriteMaker.pixmap = pixmap  
        self.scene.addItem(self.spriteMaker.pixmap)
        
        self.imgCopy = self.pixGrab.toImage()  ## view.grab returns a pixmap
                                 
    def openCopy(self, file):  ## only if '-copy' in file name
        try:           
            img = QImage(file) 
            self.spriteMaker.file = file
                 
            img = img.scaled(Fixed, Fixed, 
                Qt.AspectRatioMode.IgnoreAspectRatio, 
                Qt.TransformationMode.SmoothTransformation) 
    
            self.spriteMaker.pixmap = QGraphicsPixmapItem()     
            self.spriteMaker.pixmap.setPixmap(QPixmap(img))    
            self.spriteMaker.pixmap.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
    
            self.spriteMaker.pixmap.setZValue(-100)  ## bottom layer       
            self.scene.addItem(self.spriteMaker.pixmap)
            
            self.imgCopy = img  
            
            self.openTxy(file)                                             
        except IOError:
            MsgBox("openCopy: Error opening " + file, 5)
            return
   
### --------------------------------------------------------
    def openFiles(self):  ## open non "-copy" files     
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self.spriteMaker, "Dialog Never Shows",  
            "Choose an image file to open", "Images Files(*.jpg *.png)")
        if file:
            self.spriteMaker.clear()
            if '-copy' not in file.lower():
                self.addPixmap(file)
            else:
                self.openCopy(file)  ## from txy directory
       
    def openTxy(self, file): 
        try:
            file = file[:-9] + ".txy" 
            tmp = []        
            with open(file, 'r') as fp: 
                for line in fp:
                    ln = line.rstrip()  
                    ln = list(map(float, ln.split(',')))   
                    tmp.append(QPointF(ln[0],ln[1]))
            fp.close()
            
            self.spriteMaker.pts = tmp 
            ## skip to pathClosed
            self.spriteMaker.pathClosed = True               
            self.spriteMaker.outlineSet = False 
            self.spriteMaker.outline = None 
            
            self.spriteMaker.resetSliders() 
            self.spriteMaker.sliders.setEnabled(False)
            
            self.editingOn = True 
            self.mode = 0
        
            self.spriteMaker.updateOutline()        
            self.spriteMaker.redrawPoints() 

            self.redrawSprite()
                    
            del tmp             
        except IOError:
            MsgBox("openTxy: Error reading pts " + file, 5)
            
### --------------------------------------------------------    
    def saveSprite(self):  ## from save button
        if len(self.spriteMaker.pts) > 0: 
            img,  w, h = self.makeSprite(True)  ## crop it
            h, w, ch = img.shape
            bytesPerLine = ch * w  
                 
            file = os.path.basename(self.spriteMaker.file)
            if "-copy.png" in file.lower():  ## loaded from txy
                file = file[:-9] + ".png"   
  
            Q = QFileDialog()
            self.openPathFile =  paths['spritePath'] + file
            f = Q.getSaveFileName(self.spriteMaker,
                self.openPathFile,
                self.openPathFile)
            Q.accept()
            
            if not f[0]: 
                return
            elif not f[0].lower().endswith('.png'):
                MsgBox("saveSprite: Wrong file extention - use '.png", 5)  
                return                        
            try:                  
                img = QImage(img.data, w, h, bytesPerLine, QImage.Format.Format_ARGB32)
                img.save(paths["spritePath"] + file,
                        format='png',
                        quality=100)
            except IOError:
                MsgBox("saving Sprite: Error saving file", 5) 
                      
            self.saveTxy(file)  ## saves txy and original copy
      
    def saveTxy(self, file): 
        try:    
            file = file[:-4] + ".txy"
            Q = QFileDialog()
            self.openPathFile =  paths['txy'] + file
            f = Q.getSaveFileName(self.spriteMaker,
                self.openPathFile,
                self.openPathFile)
            Q.accept()    
              
            if not f[0]: 
                return        
            elif not f[0].lower().endswith('.txy'):
                MsgBox("saveTxy: Wrong file extention - use '.txy", 5)  
                return    
            
            MsgBox("saving sprite copy and points", 5) 
            self.saveTxyFile()
          
            if "-copy.png" in self.spriteMaker.file.lower():  ## no need to save it again
                return
            else:
                file = file[:-4] + "-copy.png"                   
            self.pixGrab.save(paths["txy"]+ file, "PNG") 
        except IOError:
            MsgBox("saveCopy: Error saving file" + "-copy", 5)   
               
    def saveTxyFile(self):    
        try:
            file = os.path.basename(self.spriteMaker.file)               
            if "-copy.png" in file.lower():
                file = file[:-9] 
            else:
                file = file[:-4]       
            file = file + ".txy"               
            with open(paths["txy"] + file, 'w') as fp:
                for i in range(0, len(self.spriteMaker.pts)):
                    p = self.spriteMaker.pts[i]
                    x = str("{0:.2f}".format(p.x()))
                    y = str("{0:.2f}".format(p.y()))
                    fp.write(x + ", " + y + "\n")
                fp.close()            
        except IOError:
            MsgBox("saveTxy: Error saving file", 5)
        return
                                                                       
### ------------------- dotsSpriteWorks --------------------


 