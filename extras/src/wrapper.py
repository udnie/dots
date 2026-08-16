
import sys
import time

from PyQt6.QtCore       import Qt, QTimer
from PyQt6.QtGui        import QPixmap, QPalette, QGuiApplication            
from PyQt6.QtWidgets    import QWidget, QApplication, QGraphicsView, QGraphicsScene, \
                                QGraphicsPixmapItem, QHBoxLayout,  QVBoxLayout, \
                                QMessageBox
   
from wrapperWorks       import *                                               
from wrapperFilters     import Filters
from wrapperGuides      import *
from wrapperSliders     import Sliders

Width, Height = ViewW + 150, ViewH + 200 
        
### ----------------------- wrapper ------------------------
''' Blends together the area overlapped by the right hand side 
    image over the left hand side image.  Saves it by adding
    "-wrp" to the file name. File needs to be in ../backgrounds
    for dots to scroll it. I recommend resizing photos to 640 
    pixels in height with a 1280X640 pixels minumum filesize -
    the cropping guide works better that way. Keys: 'D' deletes 
    blended image. 'H' toggles blended Image. 'SpaceBar' toggles 
    guides.  '''
### --------------------------------------------------------                                                                                                                                                                                                                                                                                
class Wrapper(QWidget):  
### --------------------------------------------------------       
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'{"wrapper":<12}')

        self.setUI()   
        self.show()  
        
        self.setAcceptDrops(True) 
        
### --------------------------------------------------------      
    def init(self):
        self.fileName = ''
    
        self.topEndValue = 0
        self.bottomValue = 0
        self.edgesValue = 0
        
        self.blendWidth = 0 
        self.newSlice = 100
        self.blendVal = 0
     
        self.first = False  ## do not show guides on open if false
        self.showCropped = True  ## not if false
        
        self.filtered = ''
        self.flipped = False
        
        self.save = False 
        self.dragged = False
        self.guidesOn = False  ## toggle handled by guides
     
        self.bkg = None
        self.blended = None 
        self.leftSide = None
        self.rightSide = None
          
        self.sliders.setFilterBtns()
  
### --------------------------------------------------------   
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            m = e.mimeData()
            fileName = m.urls()[0].toLocalFile()       
            ext = fileName[fileName.rfind('.'):].lower()      
            if ext in ('.png', '.jpg', '.jpeg', '.bmp'):  
                self.addBkgItem(fileName)   
                e.setAccepted(True)
                self.dragged = True
            else:
                e.ignore()

    def dragLeaveEvent(self, e):
        e.accept()
            
### --------------------------------------------------------                                                             
    def keyPressEvent(self, e):
        key = e.key()
        if key in  (Qt.Key.Key_Q, Qt.Key.Key_X, Qt.Key.Key_Escape):
            self.close()
        match key:
            case Qt.Key.Key_F:  
                self.works.openFiles()       
            case Qt.Key.Key_A:
                self.align()     
            case Qt.Key.Key_C:
                self.clear()      
            case Qt.Key.Key_D:
                self.deleteBlended()
            case Qt.Key.Key_H:
                if self.blended != None:
                    self.blended.hide() if self.blended.isVisible() else self.blended.show()
            case Qt.Key.Key_Space:
                self.guides.toggleGuides()
        
### --------------------------------------------------------       
    def addBkgItem(self, file):
        self.bkg = self.addBkg(file, 'bkg') 
        try: 
            self.scene.addItem(self.bkg)
            self.fileName = file  ## full path name 
        except:
            self.msgbox('Error: openFiles')
            return
              
    def addBkg(self, file, side='', z=0):                                   
        bkg = BkgItem(self, file, side) 
        bkg.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)  
        bkg.setZValue(-100) if z == 0 else bkg.setZValue(z)
        return bkg
     
    def align(self):  
        if len(self.scene.items()) == 0: 
            return
        elif len(self.scene.items()) > 2: 
            try:
                self.scene.removeItem(self.scene.items()[0])
            except:
                return 
        self.alignIt()
            
    def alignIt(self): 
        file = self.fileName  
        self.scene.clear()
        self.init()    
        self.fileName = file  
        self.leftSide = self.addBkg(file, 'left', 100); self.scene.addItem(self.leftSide)   
        self.rightSide = self.addBkg(file, 'right', 101);   self.scene.addItem(self.rightSide)        
        self.sliders.enableSliders(True)
        self.moveIt(0) 
                           
    def moveIt(self, pos):  
        if self.rightSide != None and pos > 0:   
            p = abs(float(pos - self.rightSide.start))
            self.blendWidth = pos  ## only place it's set, same as blendval
            self.rightSide.setPos(p, 0.0)  ## provides a visual reference
        self.wrapIt()
        self.setBlendLabel()
        if self.guidesOn and not self.first:
            self.guides.updateGuides()
            
    def wrapIt(self, saveas=''):   
        if self.fileName != ''and self.blendWidth > 0:
            img = self.works.wrapper(self.fileName)  
            if self.displayBlended(img):  ## only call to it
                self.blended.setPos(float(self.leftSide.start), 0)  ## doesn't move  
                if self.first and self.blendWidth > 20:   ## show guides
                    self.first = False
                    if not self.guides.addGuides():
                        return
                elif self.blended != None and saveas != '':
                    self.works.cropIt(img, saveas)  ## if saving
  
### --------------------------------------------------------  
    def displayBlended(self, img): 
        if self.blended != None:
            try:
                self.scene.removeItem(self.blended)     
            except: 
                self.msgbox('Error: displayBlended remove')
                return False
            
        self.blended = None    
        self.blended = BasicBkg(self, 'blended')     
        self.blended.setPixmap(QPixmap.fromImage(self.works.finalizeImg(img)))
        self.blended.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True) 
        self.blended.setZValue(200) 
        try:
            self.scene.addItem(self.blended) 
        except: 
            self.msgbox('Error: displayBlended add')
            return False
        return True
                                 
### --------------------------------------------------------
    def deleteBlended(self):
        if self.blended != None:
            try:
                self.scene.removeItem(self.blended)
            except:
                None
            self.blended = None
        else:
            self.moveIt(self.blendWidth)
           
    def setBlendVal(self, val):
        self.blendVal = val     
        self.moveIt(self.blendVal)             
        time.sleep(.005)
    
    def setBlendLabel(self):
        if self.rightSide != None:
            try:
                rgt = int(self.rightSide.pos().x())
            except:
                rgt = 0
            self.sliders.blendlabel.setText(
                f'B: {self.bottomValue/100:>3.2f}  ' \
                f'E: {self.edgesValue/100:>3.2f}   ' \
                f'T: {self.topEndValue/100:>3.2f}  ' \
                f'{self.newSlice:>4d}' \
                f'{self.blendWidth//2:>4d} ' \
                f'{self.blendWidth:>4d} '\
                f'{rgt:>4d} ' \
                f'{ViewW//2:>5d}')
                
### --------------------------------------------------------
    def setTopEndValue(self, val):  
        self.topEndValue = val
        self.sliders.topEndLabel.setText(f'{self.topEndValue/100:.2f}')
        self.setBlendLabel()
        if self.blendWidth > 0:  
            self.wrapIt()    
      
    def setBottomValue(self, val): 
        self.bottomValue = val 
        self.sliders.bottomLabel.setText(f'{self.bottomValue/100:.2f}')
        self.setBlendLabel()
        if self.blendWidth > 0:  
            self.wrapIt()   

    def setEdgeValue(self, val): 
        self.edgesValue = val 
        self.sliders.edgesLabel.setText(f'{self.edgesValue/100:.2f}')
        self.setBlendLabel()
        if self.blendWidth > 0:  
            self.wrapIt()
  
### --------------------------------------------------------             
    def clear(self):
        self.guides.deleteGuides()
        self.scene.clear()      
        self.init()
        self.sliders.resetSliders()
        self.sliders.resetblendImgSlider()
       
    def bye(self): 
        self.guides.deleteGuides()
        self.scene.clear() 
        self.close()
               
    def msgbox(self, str):
        msg = QMessageBox()
        msg.setText(str)
        timer = QTimer(msg)
        timer.setSingleShot(True)
        timer.setInterval(6000)
        timer.timeout.connect(msg.close)
        timer.start()
        msg.exec()

# ### --------------------------------------------------------          
    def setUI(self):  
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(0, 0, ViewW, ViewH)
      
        self.view.setScene(self.scene)
        self.setFixedSize(Width, Height-1) ## the border throws height off 1px
                          
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
     
        self.setStyleSheet("QGraphicsView {\n"
            "background-color: rgb(250,250,250);\n"
            "border: 1px solid rgb(125,125,125);\n" 
            "}")
       
        self.works   = Works(self)    
        self.sliders = Sliders(self)
        self.filters  = Filters(self) 
        self.guides  = Guides(self)
        
        self.buttons = self.sliders.setButtons()
        
        self.init()
           
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("silver"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
       
        vbox = QVBoxLayout()
  
        hbox = QHBoxLayout()            
        hbox.addWidget(self.view) 
        hbox.addWidget(self.sliders.setSliders())          
        vbox.addLayout(hbox) 

        vbox.addWidget(self.buttons, Qt.AlignmentFlag.AlignHCenter)
        bbox = QHBoxLayout()  
        bbox.addWidget(self.sliders.setblendImgSlider())
        bbox.addSpacing(100)
        vbox.addLayout(bbox)         
    
        self.setLayout(vbox)
        
        self.sliders.enableSliders()  ## off default
        self.sliders.resetSliders()
        
        x = QGuiApplication.primaryScreen().availableGeometry().center().x()  
        self.move(int(((x * 2 ) - Width)/2), 125) ## 125
       
        self.grabKeyboard() 
 
### -------------------------------------------------------- 
if __name__ == '__main__':
    app = QApplication(sys.argv) 
    boo = Wrapper()
    sys.exit(app.exec())

### --------------------- that's all -----------------------




