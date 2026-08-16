
import os
import time

import cv2  ## 4.12.0 or above
import numpy as np

from PyQt6.QtGui        import QImage            
from PyQt6.QtWidgets    import QFileDialog

ViewW, ViewH = 1080, 720
Magic = 25  ## best guess as an offset for the crop guide

### ------------------------ Works -------------------------                                                                                                                                                                                                                                                                           
class Works: 
### --------------------------------------------------------    
    def __init__(self, parent):
        super().__init__()
             
        self.parent = parent   

### -------------------------------------------------------- 
    def openFiles(self):
        self.parent.clear()  
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self.parent, "Dialog Never Shows",  
            "Choose an image file to open", "Images Files(*.jpg *.png)")
        if file:  
            self.parent.addBkgItem(file)
            
    def saveDialog(self):
        if self.parent.fileName != '':
            self.parent.guides.addGuides()  ## a reminder
            file_dialog = QFileDialog()       
            str = self.strwrp(self.parent.fileName)
            file, _ = file_dialog.getSaveFileName(self.parent, "Save Image", str)
            if file:
                self.parent.save = True
                self.parent.wrapIt(file)
                
    def saveWrap(self, saveas, blank):  ## from cropIt
        file = saveas if saveas != '' else self.parent.fileName        
        str = self.strwrp(file) 
        try:   
            cv2.imwrite(str, blank) 
        except:            
            self.parent.msgbox(f'Error saving file: {os.path.basename(str)}')
        self.parent.save = False   
        
    def strwrp(self, fileName):
        if 'wrp' not in fileName:     
            file = self.parent.fileName    
            str = file[0:file.rfind('.')]      
            str = f'{str}-{'wrp'}.jpg'
            return str
        else:
            return fileName
        
### --------------------------------------------------------                            
    def swap(self, which):
        if self.parent.leftSide == None:
            return
        filter = self.parent.filtered

        if which == 8:
            if filter == '':
                filter = '8'
            elif filter == '8':
                filter = ''
    
        elif which == 9:
            if filter == '':      
                filter = '9'
            elif filter == '9':
                filter = ''
                
        self.parent.filtered = filter           
        if filter == '': 
            self.parent.sliders.setFilterBtns()   
          
        self.parent.deleteBlended()
        self.parent.guides.deleteGuides()
        self.parent.wrapIt()
        
    def finalizeImg(self, img):  ## it hasn't been saved to disk as yet
        h, w, _ = img.shape
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (int(w * (ViewH/h)), ViewH), interpolation=cv2.INTER_AREA)
        h, w, ch = img.shape
        return QImage(img.data, w, h, ch * w, QImage.Format.Format_RGB888)
        
    def setNewSlice(self, slice):  ## call by cropGuide
        ns = int(ViewW//2-abs(int(slice)))
        self.parent.newSlice = ns  ## only place it's set
        self.parent.setBlendLabel()
                                                
### --------------------------------------------------------
    def wrapper(self, img_left_path):  ## gemini pro 3.0
        img1 = cv2.imread(img_left_path)  ## Load images (OpenCV loads as BGR)  
        img2 = cv2.imread(img_left_path)  
 
        if img1 is None or img2 is None:
            self.parent.works.box("wrapper: Could not load images")
            return
      
        blendWidth = self.parent.blendWidth
             
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
 
        # Linear Gradient Mode (Needs float32 arrays) - original 
        strip1 = img1[:, w1 - blendWidth:].astype(np.float32)
        strip2 = img2[:, :blendWidth].astype(np.float32)
        
        # Create a linear gradient (1.0 to 0.0 for Image 1, 0.0 to 1.0 for Image 2)
        alpha = np.linspace(0, 1, blendWidth).reshape(1, blendWidth, 1)
        blended = (strip1 * (1 - alpha) + strip2 * alpha).astype(np.uint8)

        if self.parent.filtered == '8':
            blended = self.parent.filters.Filter8(strip1, strip2)
            
        elif self.parent.filtered == '9':
            blended = self.parent.filters.Filter9(strip1, strip2)
                                              
        mid_val = int(self.parent.edgesValue)   
    
        if mid_val > 5:   
            blended = self.parent.filters.EdgesSlider(mid_val, blended, strip1, strip2)

        # blended is based on rows and columns - select all rows[:,
        # select all the columns starting at w1 minus the blendWidth
        # paste blended starting there
        final_img[:, w1 - blendWidth:w1] = blended 
         
        del blended, strip1, strip2, img1, img2

        time.sleep(.010)
        return final_img

### --------------------------------------------------------
    def cropIt(self, img, saveas):  
        h, w, _ = img.shape
        ctr  = w // 2
        half = self.parent.blendWidth // 2 
        
        crop3, crop2_extended = None, None
    
        ''' begin claude '''
        ns = max(self.parent.newSlice, half)  # newSlice must be at least half to keep news >= 0
        news = ns - half   ### where the crop takes place
        slice_x = ctr - (news-Magic)  ## approx.offset of crop handle - a magic number
        
        # crop1: starts at slice, half the blended image less half blendwidth
        crop1_start = slice_x        
        crop1_end   = slice_x + (ctr - half)
        crop1 = img[0:h, crop1_start:crop1_end].copy()

        # crop2: backs up from slice by 100 + half blendwidth
        crop2_start = slice_x - (100)
        crop2_end   = slice_x
        crop2 = img[0:h, crop2_start:crop2_end].copy()
          
        ''' begin crop3 experiment - comment out to disable '''
        # crop3 = crop2[:, -2:].copy()
        # crop3 = cv2.resize(crop3, (5, h), interpolation=cv2.INTER_LINEAR)
        # crop2_extended = np.zeros((h, crop2.shape[1] + 3, crop2.shape[2]), dtype=crop2.dtype)
        # crop2_extended[:, :crop2.shape[1] - 2] = crop2[:, :-2]
        # crop2_extended[:, crop2.shape[1] - 2:] = crop3
        # crop2 = crop2_extended
        ''' end crop3 experiment '''
        
        # place crop2 onto crop1 flush at its right edge
        crop1[:, -crop2.shape[1]:] = crop2
        ''' end claude '''

        if self.parent.save:
            self.saveWrap(saveas, crop1)

        if self.parent.showCropped:
            cv2.imshow("Cropped Image", crop1)  ## for debug 
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        del crop1, crop2
        if crop3 != None: del crop3, crop2_extended
        
        time.sleep(.015)
        
### --------------------- that's all -----------------------




