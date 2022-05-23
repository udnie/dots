
import os
import cv2
import numpy as np

from PyQt6.QtCore       import QPointF, Qt , QRect, QPoint, QSize
from PyQt6.QtGui        import QColor, QImage, QPixmap, QPainter, QPainterPath, QPolygonF, \
                               QPen, QGuiApplication
from PyQt6.QtWidgets    import QGraphicsPixmapItem, QGraphicsEllipseItem, QFileDialog, \
                               QGraphicsRectItem
                
from dotsSideGig        import MsgBox
from dotsShared         import paths
 
Fixed = 720 
V = 8.0     ## the diameter of a pointItem

### ------------------- dotsSpriteWorks --------------------  
class PointItem(QGraphicsEllipseItem):
### --------------------------------------------------------
    def __init__(self, pt, i, idx, parent):
        super().__init__()

        self.spriteMaker = parent
        self.works       = parent.works
    
        ### change this to idx = pts index = ZValue
        self.pt  = pt
        self.idx = i         ## spriteMaker pts index
        self.setZValue(idx)  ## sceneitems index
        
        self.dragCnt = 0
        self.type = 'pt'
    
        self.x = pt.x()-V*.5  ## -V*.5 so it's centered on the path 
        self.y = pt.y()-V*.5
        self.setRect(self.x, self.y, V, V)  
        
        self.setBrush(QColor("white"))        
            
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, True)

 ### --------------------------------------------------------                                   
    def mousePressEvent(self, e): 
        if self.spriteMaker.key == 'del':  
            self.works.deletePointItem(self.idx)
        elif self.spriteMaker.key == 'opt': 
            self.works.insertPointItem(self) 
        if self.spriteMaker.key in ('del','opt'):   
            self.spriteMaker.key = ''      
        e.accept() 
        
    def mouseMoveEvent(self, e):
        self.dragCnt += 1
        if self.dragCnt % 5 == 0: 
            pt = self.mapToScene(e.pos())    
            self.moveIt(pt.x(), pt.y())                                   
        e.accept()
                   
    def mouseReleaseEvent(self, e): 
        if self.dragCnt > 0:
            pt = self.mapToScene(e.pos())    
            self.moveIt(pt.x(), pt.y())      
        e.accept()
              
    def moveIt(self, x, y):
        self.setRect(x-V*.5, y-V*.5, V,V)          
        self.spriteMaker.pts[self.idx] = QPointF(x,y)
        if self.spriteMaker.outline != None or \
            self.works.editingOn == True: 
            self.spriteMaker.updateOutline() 
            self.works.redrawSprite()
                  
### --------------------------------------------------------    
class Works: 
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
        
        self.spriteMaker = parent
        self.init()
    
### --------------------------------------------------------     
    def init(self):     
        self.bkg  = None
        self.imgCopy = None
        self.sprite  = None
        self.rect    = None
              
        self.mode = 0
        self.editingOn = False
        self.cropIt = False
        QGuiApplication.restoreOverrideCursor()
          
### -------------------------------------------------------- 
    def replacePixmap(self):  ## final result of set from sliders
        ## self.imgCopy is the basis of sprites
        self.imgCopy = self.spriteMaker.view.grab(QRect(QPoint(2,5), QSize()))
        pixmap = QGraphicsPixmapItem()     
        pixmap.setPixmap(self.imgCopy)     
        pixmap.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
        pixmap.setZValue(-100)
            
        if self.spriteMaker.pixmap != None:
            self.spriteMaker.scene.removeItem(self.spriteMaker.pixmap)        
        ## replace the original with a sized copy 
        self.spriteMaker.pixmap = pixmap  
        self.spriteMaker.scene.addItem(self.spriteMaker.pixmap)
        
### -------------------------------------------------------- 
    def preview(self):
        if self.spriteMaker.pathClosed == False:
            return
        
        img, w, h = self.makeSprite()
        self.addSprite(img)
              
        p = QPixmap(w, h)  
      
        if self.mode > 2: self.mode = 0
                  
        if self.mode == 0:   
            p.fill(QColor(230,230,230,128))  
        elif self.mode == 1:
            p.fill(QColor(128,128,128,255))
        elif self.mode == 2:
            p.fill(QColor(Qt.GlobalColor.transparent))
 
        if self.bkg != None:
            self.spriteMaker.scene.removeItem(self.bkg)     
                    
        self.bkg = QGraphicsPixmapItem()     
        self.bkg.setPixmap(p)
        self.bkg.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False) 
        self.bkg.setZValue(-50)   
        
        self.spriteMaker.scene.addItem(self.bkg)
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
                        
### -------------------------------------------------------- 
    def addSprite(self, img):                         
        height, width, ch = img.shape
        bytesPerLine = ch * width  
             
        img = QImage(img.data, width, height, bytesPerLine, QImage.Format.Format_ARGB32)
         
        if self.sprite!= None:
            self.spriteMaker.scene.removeItem(self.sprite)
              
        self.sprite = QGraphicsPixmapItem()     
        self.sprite.setPixmap(QPixmap.fromImage(img))    
        self.sprite.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
        self.sprite.setZValue(0)
       
        self.spriteMaker.scene.addItem(self.sprite)  
               
### --------------------------------------------------------             
    def makeSprite(self, crop=False):        
        img = QImage(self.imgCopy)
        
        output = QImage(Fixed, Fixed, QImage.Format.Format_ARGB32)
        output.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(output) 
        poly = QPolygonF()
        
        for s in self.spriteMaker.pts:
            poly.append(QPointF(s))
    
        path = QPainterPath()     
        path.addPolygon(poly)
        painter.setClipPath(path)   
        painter.drawPolygon(poly)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.drawImage(QPointF(),img)      
        painter.end()
                
        if crop == True:  ## only if saving it 
            x, y, x1, y1 = self.getCrop()
            output = output.copy(int(x), int(y), int(x1), int(y1))  
                
        output = output.convertToFormat(QImage.Format.Format_ARGB32)
                
        width = output.width()
        height = output.height()
       
        bits = output.bits()  ## change for pyside
        bits.setsize(output.sizeInBytes())
        
        img = np.array(bits).reshape(height, width, 4) 
                           
        kernel = np.array([  ## sharpen matrix below
            [0, -1, 0],
            [-1, 5,-1],
            [0, -1, 0]])
        
        img = cv2.filter2D(src=img, ddepth=-1, kernel=kernel)
        img = cv2.GaussianBlur(img,(3,3),cv2.BORDER_DEFAULT)
        
        if crop == False and self.spriteMaker.pathClosed:
             self.showCrop() if self.cropIt == True else self.delCrop()
      
        return img, width, height
                          
    def redrawSprite(self):
        img, _, _ = self.makeSprite()
        self.addSprite(img)

### --------------------------------------------------------
    def openFiles(self):  ## open non "-copy" files     
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self.spriteMaker, "Dialog Never Shows",  
            "Choose an image file to open", "Images Files(*.jpg *.png)")
        if file:
            self.spriteMaker.scene.clear()    
            self.init()
            if '-copy' not in file.lower():
                self.spriteMaker.addPixmap(file)
            else:
                self.openCopy(file)  ## from txy directory
                    
    def openCopy(self, file):  ## open only '-copy' in file
        try:           
            img = QImage(file) 
            img = img.scaled(Fixed, Fixed, 
                Qt.AspectRatioMode.IgnoreAspectRatio, 
                Qt.TransformationMode.SmoothTransformation) 
    
            self.spriteMaker.pixmap = QGraphicsPixmapItem()     
            self.spriteMaker.pixmap.setPixmap(QPixmap(img))    
            self.spriteMaker.pixmap.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
    
            self.spriteMaker.pixmap.setZValue(-100)          
            self.spriteMaker.scene.addItem(self.spriteMaker.pixmap)
            
            self.imgCopy = img  ## set sprite copy 
            self.spriteMaker.file = file
            self.openTxy(file)  
                             
        except IOError:
            MsgBox("openCopy: Error opening " + file, 5)
            return
        
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
            img,  w, h = self.makeSprite(True)
            h, w, ch = img.shape
            bytesPerLine = ch * w  
                 
            file = os.path.basename(self.spriteMaker.file)
            if "-copy.png" in file.lower():
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
            ## try and continue
            self.saveCopy()
            MsgBox("saving sprite copy and points", 4)
            self.saveTxy()
           
    def saveCopy(self):     
        try:
            file = os.path.basename(self.spriteMaker.file)       
            if "-copy.png" in file.lower():
                return    
            elif not "-copy.png" in file.lower():
                file = file[:-4] + "-copy.png"
            self.imgCopy.save(paths["txy"]+ file, "PNG") 
        except IOError:
            MsgBox("saveCopy: Error saving file", 5)   
                
    def saveTxy(self):        
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
    
### -------------------------------------------------------- 
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
        return x-10, y-10, (x1-x)+20, (y1-y)+20           
        
    def toggleCrop(self):
        if self.cropIt == False:
            self.cropIt = True
        else:
            self.cropIt = False
                           
    def showCrop(self):
        if self.rect != None:
            self.spriteMaker.scene.removeItem(self.rect)
        x, y, x1, y1 = self.getCrop()
        self.rect = QGraphicsRectItem(x, y, x1, y1)
        self.rect.setPen(QPen(QColor('lime'), 2, Qt.PenStyle.SolidLine)) 
        self.rect.setZValue(150) 
        self.spriteMaker.scene.addItem(self.rect)
       
    def delCrop(self):
        if self.rect != None:
            self.spriteMaker.scene.removeItem(self.rect)
        self.rect = None
        self.cropIt = False
  
  ### --------------------------------------------------------
    def deletePointItem(self, idx):  
        self.spriteMaker.pts.pop(idx) 
        self.spriteMaker.redrawPoints()
        self.spriteMaker.updateOutline() 
        
    def insertPointItem(self, pointItem):  ## halfway between points
        idx, pt = pointItem.idx + 1, pointItem.pt  ## idx, the next point
        if idx == len(self.spriteMaker.pts): 
            idx = 0    
        pt1 = self.spriteMaker.pts[idx]  ## calculate new x,y
        pt1 = QPointF(pt1.x() - pt.x(), pt1.y() - pt.y())
        pt1 = pt + pt1*.5      
        self.spriteMaker.pts.insert(idx, pt1)
        self.spriteMaker.redrawPoints()     
        self.spriteMaker.updateOutline() 
                          
### ------------------- dotsSpriteWorks -------------------- 
 
 
