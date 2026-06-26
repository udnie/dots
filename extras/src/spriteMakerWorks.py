
import os
import cv2
import numpy as np
import time

from PyQt6.QtCore       import QPointF, Qt , QRect, QPoint, QSize
from PyQt6.QtGui        import QColor, QImage, QPixmap, QPainter, QPainterPath, QPolygonF
from PyQt6.QtWidgets    import QGraphicsPixmapItem, QFileDialog, QWidget
                               
from spriteMakerPoints  import Fixed, msgbox
from spriteMakerHelp    import SpriteHelp

ViewW, ViewH = 720, 720

### --------------------------------------------------------
''' find 'bits.setsize' and comment it out for pyside. 
    functions to open, save and display sprites and backgrounds
    functions that save sprites and related files are in the 
     SaveTxy Class in Points. '''
### --------------------------------------------------------   
class Works(QWidget):  
### --------------------------------------------------------
    def __init__(self, spriteMaker):
        super().__init__()
        
        self.spriteMaker = spriteMaker
        self.scene       = spriteMaker.scene
        self.view        = spriteMaker.view
                   
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
    def addPixitem(self, file):  ## inital open - scene cleared each new image file                                          
        img = QImage(file)     
        self.spriteMaker.file = file
        
        if img.width() > Fixed or img.height() > Fixed:  ## size it to fit       
            img = img.scaled(Fixed-50, Fixed-50,  
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
      
        self.spriteMaker.pixItem = QGraphicsPixmapItem()     
        self.spriteMaker.pixItem.setPixmap(QPixmap(img))    
        self.spriteMaker.pixItem.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
        
        self.x = (ViewW-img.width())/2  ## center it
        self.y = (ViewH-img.height())/2
        
        self.spriteMaker.pixItem.setX(self.x)  
        self.spriteMaker.pixItem.setY(self.y)     
        self.spriteMaker.pixItem.setZValue(-100) 
                
        self.scene.addItem(self.spriteMaker.pixItem)
        
        self.spriteMaker.outlineSet = False
        self.spriteMaker.enableSliders(True)
        
### -------------------------------------------------------- 
    def background(self):  ## preview selection by changing background
        if not self.spriteMaker.pathClosed:
            return  

        if self.mode > 1: self.mode = 0  ## only for this function  
               
        img, w, h = self.makeSprite()
        self.addSprite(img) 
               
        p = QPixmap(w, h)      
        p.fill(QColor(128,128,128,255)) if self.mode == 0 else \
            p.fill(QColor('transparent'))
 
        if self.bkg != None:
            self.scene.removeItem(self.bkg)                         
        self.bkg = QGraphicsPixmapItem()     
        self.bkg.setPixmap(p)
        self.bkg.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False) 
        self.bkg.setZValue(-50)  ## one up from bottom
        
        self.scene.addItem(self.bkg)
        self.mode += 1   
             
    def edit(self):
        if not self.spriteMaker.pathClosed:
            return       
        if not self.editingOn:
            self.spriteMaker.removePointItems()
            self.spriteMaker.addPointItems()
            self.spriteMaker.updateOutline()
            self.redrawSprite()
            self.editingOn = True   
        else:
            self.spriteMaker.removePointItems()
            self.spriteMaker.deleteOutline()
            self.editingOn = False           
    
    def openHelpMenu(self):
        if self.spriteMaker.helpFlag:
            self.closeHelpMenu()
            self.spriteMaker.helpMenu == None
        else:
            self.spriteMaker.helpMenu = SpriteHelp(self.spriteMaker)
            self.spriteMaker.helpFlag = True
  
    def closeHelpMenu(self):
        if self.spriteMaker.helpMenu != None: 
            self.spriteMaker.helpMenu.tableClose()
            self.spriteMaker.helpMenu.close()
            self.spriteMaker.helpFlag = False
                               
### -------------------------------------------------------- 
    def addSprite(self, img):  ## from which it's saved                     
        height, width, ch = img.shape
        bytesPerLine = ch * width        
        img = QImage(img.data, width, height, bytesPerLine, QImage.Format.Format_ARGB32)  
        if self.sprite != None:
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
         
        # ## add a light-grey semi-transspriteMaker border to help with anti-aliasing
        # painter.setPen(QPen(QColor(100,100,100,50), 5, Qt.PenStyle.SolidLine))     
        # painter.drawPolygon(poly)  
            
        painter.setClipPath(path)  
        painter.drawImage(QPointF(),img)     
        painter.end()
                
        if crop:  ## only if saving it 
            x, y, x1, y1 = self.getCrop()
            output = output.copy(int(x), int(y), int(x1), int(y1))  
                
        output = output.convertToFormat(QImage.Format.Format_ARGB32)
                    
        width = output.width()
        height = output.height()
                                                         
        bits = output.bits()  
        ''' comment out bits.setsize.. for pyside '''
        bits.setsize(output.sizeInBytes()) 
        
        img = np.array(bits).reshape(height, width, 4)                      
        kernel = np.array([  ## sharpen matrix below
            [0, -1, 0],
            [-1, 5,-1],
            [0, -1, 0]])
        ## try shapening overall - then blur edges
        img = cv2.filter2D(src=img, ddepth=-1, kernel=kernel)
        img = cv2.GaussianBlur(img,(3,3),cv2.BORDER_DEFAULT)
                    
        return img, width, height
     
    def getCrop(self):
        x, y, x1, y1 = ViewW, ViewH, 0.0, 0.0
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
                                     
    def redrawSprite(self):
        img, _, _ = self.makeSprite()
        self.addSprite(img)
     
### -------------------------------------------------------- 
    def replacePixitem(self):  ## clicking on set from vertical sliders
        ## self.pixGrab is the basis of sprites - view.grab returns a pixItem
        self.pixGrab = self.spriteMaker.view.grab(QRect(QPoint(2,5), QSize()))
        pixItem = QGraphicsPixmapItem()     
        pixItem.setPixmap(self.pixGrab)     
        pixItem.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
        pixItem.setZValue(-100)  ## bottom layer  
        if self.spriteMaker.pixItem != None:
            self.scene.removeItem(self.spriteMaker.pixItem)        
        ## replace the original with a same size copy 
        self.spriteMaker.pixItem = pixItem  
        self.scene.addItem(self.spriteMaker.pixItem)
        self.imgCopy = self.pixGrab.toImage()  ## view.grab returns a pixItem
                  
### --------------------------------------------------------
    def openFiles(self):  ## open non "-copy" files     
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self.spriteMaker, "Dialog Never Shows",  
            "Choose an image file to open", "Images Files(*.jpg *.png)")
        if file:
            self.spriteMaker.clear()
            if '-copy' not in file.lower():
                self.spriteMaker.loupe.addFrame()  ## always if not 'copy'
                self.addPixitem(file)
            else:
                if not self.openCopy(file):  ## from txy directory     
                    msgbox( f'openTxy: Error reading pts in {os.path.basename(file)}', 5)
            return
     
    def openCopy(self, file):  ## only if '-copy' in file name          
        img = QImage(file) 
        self.spriteMaker.file = file
                
        img = img.scaled(Fixed, Fixed, 
            Qt.AspectRatioMode.IgnoreAspectRatio, 
            Qt.TransformationMode.SmoothTransformation) 

        self.spriteMaker.pixItem = QGraphicsPixmapItem()     
        self.spriteMaker.pixItem.setPixmap(QPixmap(img))    
        self.spriteMaker.pixItem.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)

        self.spriteMaker.pixItem.setZValue(-100)  ## bottom layer       
        self.scene.addItem(self.spriteMaker.pixItem)
        
        self.imgCopy = img  
            
        if not self.openTxy(file):   
            msgbox(f'openCopy: Error opening {os.path.basename(file)}', 5)
            return False                                   
        return True
     
    def openTxy(self, file): 
        file = file[:-9] + ".txy" 
        tmp = []      
        try:  
            with open(file, 'r') as fp: 
                for line in fp:
                    ln = line.rstrip()  
                    ln = list(map(float, ln.split(',')))   
                    tmp.append(QPointF(ln[0],ln[1]))
            fp.close()
        except:
            return False
        
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
        return True
                                                                            
### ------------------- dotsSpriteWorks --------------------


 
