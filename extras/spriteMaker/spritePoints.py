
import os
import math
import random
 
from PyQt6.QtCore       import QPointF, QTimer, QRectF
from PyQt6.QtGui        import QColor, QImage                       
from PyQt6.QtWidgets    import QGraphicsEllipseItem, QMessageBox, QFileDialog
                        
pathcolors = (
    "DODGERBLUE", "AQUAMARINE", "CORAL", "CYAN", "DEEPSKYBLUE",   
    "LAWNGREEN", "GREEN", "HOTPINK", "WHITESMOKE", "LIGHTCORAL", 
    "LIGHTGREEN", "LIGHTSALMON", "LIGHTSKYBLUE", "LIGHTSEAGREEN", 
    "MAGENTA", "TOMATO", "ORANGERED", "RED", "YELLOW", "WHITE", )     

Fixed = 720 

paths = {   
    "spritePath": "./",
    "txy":        "./",
}   

### ---------------------- spritePoints --------------------
''' classes: PointItem, SaveTxy, MsgBox '''
### -------------------------------------------------------- 
class PointItem(QGraphicsEllipseItem):
### --------------------------------------------------------
    def __init__(self, pt, i, zval, parent):
        super().__init__()

        self.spriteMaker = parent
        self.works       = parent.works
        self.loupe       = parent.loupe
       
        self.pt  = pt
        self.idx = i          
        self.setZValue(zval) ## 150+ for outline
        
        self.dragCnt = 0
        self.type = 'pt'
    
        self.moving = False
    
        self.V = 5.0
        self.setBrush(QColor("white"))
        self.saveColor = None
            
        self.x = pt.x()-self.V*.5  ## -V*.5 so it's centered on the path 
        self.y = pt.y()-self.V*.5
            
        self.setRect(self.x, self.y, self.V, self.V)  
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setAcceptHoverEvents(True)

 ### -------------------------------------------------------- 
    def hoverEnterEvent(self, e):
        self.saveColor = self.brush().color()  ## changed for pyside
        self.setBrush(QColor("coral"))
        if self.idx != self.loupe.idx:
            self.loupe.loupeIt(self.idx) 
        p = self.rect()      
        if p.width() < self.V*1.5:
            self.setRect(QRectF(p.x(), p.y(), self.V*1.5, self.V*1.5))
        e.accept()
        
    def hoverLeaveEvent(self, e): 
        self.setBrush(QColor(self.saveColor)) 
        p = self.rect()
        self.setRect(QRectF(p.x(), p.y(), self.V, self.V))
        e.accept()
    
    def mousePressEvent(self, e): 
        if self.spriteMaker.key in ('del','opt'):   
            if self.spriteMaker.key == 'del':
                self.loupe.deletePointItem(self.idx)
            elif self.zValue() < 900 and self.spriteMaker.key == 'opt': 
                self.loupe.insertPointItem(self) 
        e.accept() 
        
    def mouseMoveEvent(self, e):
        self.dragCnt += 1
        if self.dragCnt % 5 == 0 and self.zValue() < 900: 
            x, y = self.returnXY(self.mapToScene(e.pos()))
            self.moveIt(x, y) 
            self.moving = True                                    
        e.accept()
                   
    def mouseReleaseEvent(self, e): 
        if self.dragCnt > 0:
            x, y = self.returnXY(self.mapToScene(e.pos()))
            self.moveIt(x, y) 
        if self.moving and self.zValue() < 900:
            self.moving = False
            self.loupe.loupeIt(self.idx)  
        e.accept()
                                
    def moveIt(self, x, y):        
        self.setRect(x-self.V*.5, y-self.V*.5, self.V, self.V) 
        if self.zValue() < 900:  ## update outline  
            self.spriteMaker.pts[self.idx] = QPointF(x,y)
            if self.spriteMaker.outline or \
                self.works.editingOn == True: 
                self.spriteMaker.updateOutline() 
                self.works.redrawSprite()   
                          
    def returnXY(self, p):  
        x = int(constrain(p.x(), self.V, Fixed, 15))
        y = int(constrain(p.y(), self.V, Fixed, 15))
        return x, y       
                    
### -------------------------------------------------------- 
class SaveTxy():  ## functions: saveSprite, saveTxy, saveTxyFile
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()

        self.spriteMaker = parent
        self.works = self.spriteMaker.works
        
### --------------------------------------------------------
    def saveSprite(self):  ## from save button
        if len(self.spriteMaker.pts) > 0: 
            img,  w, h = self.works.makeSprite(True)  ## crop it
            h, w, ch = img.shape
            bytesPerLine = ch * w  
                 
            file = os.path.basename(self.spriteMaker.file)
            if "-copy.png" in file.lower():  ## loaded from txy
                file = file[:-9] + ".png"   
            else:
                file = file[:file.index('.')] + '.png'
       
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
            self.works.pixGrab.save(paths["txy"]+ file, "PNG") 
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

### --------------------------------------------------------
class MsgBox(QMessageBox):  
### --------------------------------------------------------
    def __init__(self, text, pause=2):
        super().__init__()

        self.timeOut = pause
        self.setText("\n" + text)
        self.setStandardButtons(QMessageBox.StandardButton.NoButton)
       
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeContent)
        self.timer.start()

        self.exec()

    def enterEvent(self, e):  
        self.close()

    def changeContent(self):
        self.timeOut -= 1
        if self.timeOut <= 0:
            self.close()

    def closeEvent(self, e):
        self.timer.stop()
        e.accept() 

### -------------------------------------------------------- 
def constrain(lastXY, objSize, panelSize, overlap):
    if lastXY + objSize > panelSize - overlap:
        return panelSize - (objSize + overlap)
    elif lastXY < overlap:
        return overlap
    else:
        return lastXY
    
def getColorStr():  
    random.seed()
    p = pathcolors
    return p[random.randint(0,len(p)-1)]

def distance(x1, x2, y1, y2):
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt((dx * dx ) + (dy * dy))

### ---------------------- spritePoints --------------------

