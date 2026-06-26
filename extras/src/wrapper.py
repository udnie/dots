
import sys
import os

import cv2  ## 4.12.0 or above
import numpy as np
import time

from PyQt6.QtCore       import Qt, QTimer
from PyQt6.QtGui        import QImage, QPixmap, QPalette, QGuiApplication            
from PyQt6.QtWidgets    import QWidget, QApplication, QGraphicsView, QGraphicsScene, \
                                QGraphicsPixmapItem, QHBoxLayout,  QVBoxLayout, \
                                QFileDialog, QMessageBox
                                
from wrapperWrks        import *

Width, Height = ViewW + 140, ViewH + 200   
           
### ----------------------- wrapper ------------------------
''' Blends together the area overlapped by the right hand side 
    image over the left hand side image.  Saves it by adding
    "-wrp" to the file name. File needs to be in ../backgrounds
    for dots to scroll it. I recommend resizing photos to 640 
    pixels in height with a 1280X640 pixels minumum filesize -
    the cropping guide works better that way.  Sliders on right 
    are for future use.  Keys: 'D' deletes blended image. 'H' 
    toggles blended Image. 'SpaceBar' toggles guides.  '''
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
        
        self.gamma = 1.0  ## these three currently not used
        self.rightAlpha = .50
        self.leftAlpha = .50
        
        self.blendWidth = 0 
        self.newSlice = 100
        self.blendVal = 0
     
        self.first = True  ## do not show guides on open if false
        self.showCropped = True  ## not if false
        
        self.save = False 
        self.flipped = False
        self.guidesOn = False  ## handled by works
        self.dragged = False
     
        self.bkg = None
        self.blended = None 
        self.left = None
        self.right = None
        
        self.works.swapBtn.setText("Swap") 

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
        if key == Qt.Key.Key_F: 
            self.openFiles()       
        elif key == Qt.Key.Key_A:
            self.align()     
        elif key == Qt.Key.Key_C:
            self.clear()      
        elif key == Qt.Key.Key_D:
            self.deleteBlended()
        elif key == Qt.Key.Key_H:
            if self.blended != None:
                self.blended.hide() if self.blended.isVisible() else self.blended.show()
        elif key == Qt.Key.Key_Space:
            self.toggleGuides()
        elif key in  (Qt.Key.Key_Q, Qt.Key.Key_X, Qt.Key.Key_Escape):
            self.close()
        
### --------------------------------------------------------       
    def openFiles(self):
        self.clear()  
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self, "Dialog Never Shows",  
            "Choose an image file to open", "Images Files(*.jpg *.png)")
        if file:  
            self.addBkgItem(file)
            
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
        self.left = self.addBkg(file, 'left', 100); self.scene.addItem(self.left)   
        self.right = self.addBkg(file, 'right', 101);   self.scene.addItem(self.right)        
        self.works.enableSliders(True)
        self.moveIt(0) 
                           
    def moveIt(self, pos):  
        if self.right != None and pos > 0:   
            p = abs(float(pos - self.right.start))
            self.blendWidth = pos  ## only place it's set, same as blendval
            self.right.setPos(p, 0.0)  ## provides a visual reference
        self.wrapIt()
        self.setBlendLabel()
        if self.guidesOn and not self.first:
            self.works.updateGuides()
            
    def wrapIt(self, saveas=''):   
        if self.fileName != ''and self.blendWidth > 0:
            img = self.wrapper(self.fileName)  
            if self.displayBlended(img):  ## only call
                self.blended.setPos(float(self.left.start), 0) ## doesn't move  
                if self.first and self.blendWidth > 20: 
                    self.first = False
                    if not self.works.addGuides():
                        return
                elif self.blended != None and saveas != '':
                    self.cropIt(img, saveas)  ## if saving and for debug
                                   
    def setNewSlice(self, slice):  ## call by cropGuide
        ns = int(ViewW//2-abs(int(slice)))
        self.newSlice = ns  ## only place it's set
        self.setBlendLabel()
             
### --------------------------------------------------------
    def wrapper(self, img_left_path):  ## gemini pro 3.0, additions by claude
        img1 = cv2.imread(img_left_path)  ## Load images (OpenCV loads as BGR)  
        img2 = cv2.imread(img_left_path)  

        if img1 is None or img2 is None:
            self.msgbox("wrapper: Could not load images")
            return
  
        blendWidth = self.blendWidth
             
        # 1. Match heights (standardize to img1's height)
        h, w1, _ = img1.shape
        h2, w2, _ = img2.shape
        
        if h != h2:
            img2 = cv2.resize(img2, (int(w2 * h / h2), h))
            w2 = img2.shape[1]

        # 2. Create the canvas - new_width is (Image1 + Image2) minus the shared ctr  
        new_width = w1 + w2 - blendWidth
        final_img = np.zeros((h, new_width, 3), dtype=np.uint8)

        # 3. Place the left image (excluding the ctr zone)
        final_img[:, :w1 - blendWidth] = img1[:, :w1 - blendWidth]

        # 4. Place the right image (excluding the ctr zone)
        final_img[:, w1:] = img2[:, blendWidth:]

        # # 5. The blend strips
        strip1 = img1[:, w1 - blendWidth:].astype(np.float32)
        strip2 = img2[:, :blendWidth].astype(np.float32)
               
        if self.flipped:
            t = np.linspace(0, 1, blendWidth)
            alpha = ((1 - np.cos(t * np.pi)) / 2).reshape(1, blendWidth, 1)
            ''' hsv blend '''
            s1 = cv2.cvtColor(strip1.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
            s2 = cv2.cvtColor(strip2.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    
            blended_hsv = (s1 * (1 - alpha) + s2 * alpha)
            blended = cv2.cvtColor(blended_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
            ''' end hsv blend '''
        else:
            # Create a linear gradient (1.0 to 0.0 for Image 1, 0.0 to 1.0 for Image 2)
            # Reshaped to (1, p, 1) for broadcasting across height and channels
            alpha = np.linspace(0, 1, blendWidth).reshape(1, blendWidth, 1)
            blended = (strip1 * (1 - alpha) + strip2 * alpha).astype(np.uint8)
  
        # Insert the blended strip into the middle of the canvas
        final_img[:, w1 - blendWidth:w1] = blended
        
        del blended, strip1, strip2, img1, img2
        
        time.sleep(.02)
           
        return final_img     
 
### -------------------------------------------------------- 
    def cropIt(self, img, saveas):
        h, w, _ = img.shape
        ctr  = w // 2
        half = self.blendWidth // 2  # half blendwidth
   
        ''' begin claude '''
        ns = max(self.newSlice, half)  # newSlice must be at least half to keep news >= 0
        news = ns - half   ### where the crop takes place
       
        slice_x = ctr - (news-10)  ## approx.radius of crop handle - my magic number
        
        # crop1: starts at slice, half the blended image less half blendwidth
        crop1_start = slice_x        
        crop1_end   = slice_x + (ctr - half)
        crop1 = img[0:h, crop1_start:crop1_end].copy()

        # crop2: backs up from slice by 100 + half blendwidth
        crop2_start = slice_x - (100)
        crop2_end   = slice_x
        crop2 = img[0:h, crop2_start:crop2_end].copy()

        # crop3: half 2 pixels of crop2, resized to 5px wide, spliced back 2px from end
        # (extend crop2 by 3px to make the stretch less noticeable)
        ''' begin crop3 experiment - comment out block to disable '''
        
        # Takes the last 2 columns of pixels from crop2 — a thin sliver from its right edge.
        # This is the source material for the stretch 
        crop3 = crop2[:, -2:].copy()
        
        # Stretches that 2px sliver to 5px wide. INTER_LINEAR interpolates 
        # smoothly between the two columns rather 
        # than just duplicating pixels. So now crop3 is 5px wide.
        crop3 = cv2.resize(crop3, (5, h), interpolation=cv2.INTER_LINEAR)
         
        # Creates a blank canvas 3px wider than crop2. It's +3 and not +5 
        # because the next two lines will overlap the last 
        # 2px of crop2 with the first 2px of crop3 — so the net gain is 3px
        crop2_extended = np.zeros((h, crop2.shape[1] + 3, crop2.shape[2]), dtype=crop2.dtype)
    
        # Copies crop2 into the canvas but stops 2px short of the end — 
        # leaving room for crop3 to overlap.   
        crop2_extended[:, :crop2.shape[1] - 2] = crop2[:, :-2]
        
        # Places the 5px crop3 starting at that 2px-from-the-end position, so it overlaps 
        # the last 2px of crop2 and extends 3px beyond.
        crop2_extended[:, crop2.shape[1] - 2:] = crop3
        crop2 = crop2_extended
        ''' end crop3 experiment '''

        # place crop2 onto crop1 flush at its right edge
        crop1[:, -crop2.shape[1]:] = crop2
        ''' end claude '''

        if self.save:
            self.saveWrap(saveas, crop1)

        if self.showCropped:
            cv2.imshow("Cropped Image", crop1)  ## for debug 
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        del crop1, crop2, crop3, crop2_extended
        
        time.sleep(.02)
                               
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
        self.blended.setPixmap(QPixmap.fromImage(self.finalizeImg(img)))
        self.blended.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True) 
        self.blended.setZValue(200) 
        try:
            self.scene.addItem(self.blended) 
        except: 
            self.msgbox('Error: displayBlended add')
            return False
        return True
     
    def finalizeImg(self, img):  ## it hasn't been saved to disk as yet
        h, w, _ = img.shape
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (int(w * (ViewH/h)), ViewH), interpolation=cv2.INTER_AREA)
        h, w, ch = img.shape
        return QImage(img.data, w, h, ch * w, QImage.Format.Format_RGB888)
        
    def saveWrap(self, saveas, blank):  ## from cropIt
        file = saveas if saveas != '' else self.fileName        
        str = self.strwrp(file)    
        cv2.imwrite(str, blank) 
        self.msgbox(f'file: {os.path.basename(str)} saved')
        self.save = False    
    
    def swap(self): 
        # self.flipped = not self.flipped  ## I like it!
        if self.left != None:
            if not self.flipped:
                self.flipped = True
                self.works.swapBtn.setText("Swapped")
            else:
                self.flipped = False    
                self.works.swapBtn.setText("Swap")      
            self.deleteBlended()
            self.works.deleteGuides()
            self.wrapIt()
   
### --------------------------------------------------------
    def saveDialog(self):
        if self.fileName != '':
            file_dialog = QFileDialog()       
            str = self.strwrp(self.fileName)
            file, _ = file_dialog.getSaveFileName(self, "Save Image", str)
            if file:
                self.save = True
                self.wrapIt(file)
                        
    def strwrp(self, fileName):
        if 'wrp' not in fileName:     
            file = self.fileName    
            str = file[0:file.rfind('.')]      
            str = f'{str}-{'wrp'}.jpg'
            return str
        else:
            return fileName
                           
    def toggleGuides(self):
        self.works.addGuides() if not self.guidesOn else self.works.deleteGuides()
        
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
            
    def setBlendLabel(self):
        if self.right != None:
            try:
                rgt = int(self.right.pos().x())
            except:
                rgt = 0
            self.works.blendlabel.setText(
                f'{self.newSlice:5d}' \
                f'{self.blendWidth//2:5d}' \
                f'{self.blendWidth:5d}' \
                f'{rgt:5d}' \
                f'{ViewW//2:5d}')
                
### --------------------------------------------------------
    def setRightAlpha(self, val):  ## not used
        self.rightAlpha = (val/100)
        self.works.rightAlphaValue.setText(f'{self.rightAlpha:.2f}')
        self.works.rightAlphalabel.setText(f'{self.rightAlpha:.2f}')
        # if self.blendWidth > 0:  
        #     self.wrapIt()
        
    def setLeftAlpha(self, val):  ## not used
        self.leftAlpha = (val/100)  
        self.works.leftAlphaValue.setText(f'{self.leftAlpha:.2f}')
        self.works.leftAlphalabel.setText(f'{self.leftAlpha:.2f}')
        # if self.blendWidth > 0:  
        #     self.wrapIt()
    
    def resetBlendSlider(self):
        self.setBlendVal(0)
        self.works.blendSlider.setValue(0) 
        self.works.blendlabel.setText('')
     
    def msgbox(self, str):
        msg = QMessageBox()
        msg.setText(str)
        timer = QTimer(msg)
        timer.setSingleShot(True)
        timer.setInterval(7000)
        timer.timeout.connect(msg.close)
        timer.start()
        msg.exec() 
        
    def clear(self):
        self.works.deleteGuides()
        self.scene.clear()      
        self.init()
        self.resetBlendSlider()
       
    def bye(self): 
        self.works.deleteGuides()
        self.scene.clear() 
        self.close()

### --------------------------------------------------------          
    def setUI(self):  
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(0, 0, ViewW, ViewH)
      
        self.view.setScene(self.scene)
        self.setFixedSize(Width, Height-1) ## the border throws height off 1px
                      
        self.works = Works(self) 
        
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
     
        self.setStyleSheet("QGraphicsView {\n"
            "background-color: rgb(250,250,250);\n"
            "border: 1px solid rgb(125,125,125);\n" 
            "}")
        
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("silver"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        self.blender = self.works.setBlendSlider()
        self.sliders = self.works.setSliders() 
        self.buttons = self.works.setButtons()
        
        vbox = QVBoxLayout()
  
        hbox = QHBoxLayout()            
        hbox.addWidget(self.view) 
        hbox.addWidget(self.sliders)          
        vbox.addLayout(hbox) 

        vbox.addWidget(self.buttons, Qt.AlignmentFlag.AlignHCenter)
        bbox = QHBoxLayout()  
        bbox.addWidget(self.blender, Qt.AlignmentFlag.AlignHCenter)
        vbox.addLayout(bbox)         
    
        self.setLayout(vbox)
        
        x = QGuiApplication.primaryScreen().availableGeometry().center().x()  
        self.move(int(((x * 2 ) - Width)/2), 125) 
                
        self.init() 
        self.works.enableSliders()  ## off default        
        
        self.grabKeyboard() 
 
### -------------------------------------------------------- 
if __name__ == '__main__':
    app = QApplication(sys.argv) 
    boo = Wrapper()
    sys.exit(app.exec())

### --------------------- that's all -----------------------




