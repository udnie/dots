
import math
import time
# import cv2   ## required <<<----- 4.12.0 or above

import os.path
import numpy as np

### --------------------- videoClips.py --------------------
''' Source for assembler, ctrOnBackground and zoom as well as both 
    file dialogs and a number of small functions including setFormat. 
    Import cv2 needs to be uncommented once opencv is installed and 
    MakeClips set to true inorder to run assembler. The videoClipsWidget 
    defaults are set here.  '''
### --------------------------------------------------------
    
from functools          import partial

from PyQt6.QtCore       import QTimer
from PyQt6.QtWidgets    import QMessageBox, QFileDialog
                                
from videoClipsWidget   import *

Ext = (".tif", ".png", ".jpg", ".jpeg", ".webp")
Mxt = (".mov", ".mp4")

### --------------------------------------------------------
class Clips:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
        
        self.parent = parent
        self.videowidget = None

        ### widget defaults - the limits are set in the widget sliders

        self.Fps = 5    ## frames per second - less than 5 and the video won't play
        self.Max = 25   ## max number of photos to read/write  
        self.Wpr = 1    ## writes per read
        self.Rnf = 0    ## read every 'n frame
                       
        self.AutoAspect  = False     ## True reads the video metadata to set the aspect ratio and resize the widget
                                     ## requires that getVideoWidthHeight is working                                     
        self.MakeClips   = False     ## True requires having opencv installed and import cv2 uncommented
        self.FirstFrame  = False     ## True - read only the first frame of a video       
        self.SkipFrames  = False     ## True - read the Nth frame of a video 
        self.FilterOn    = False     ## True - image aspect matches self.aspect (parent)
        self.PlayVideo   = False     ## True plays video upon loading
        self.AddFileName = False     ## True add to frame
        
### --------------------------------------------------------       
    def toggleVideoWidget(self, parent):
        if self.videowidget == None:
            self.videowidget = VideoWidget(parent)
        elif self.videowidget != None:
            self.closeWidget()
      
    def closeWidget(self):
        if self.videowidget != None:
            self.videowidget.close()
        self.videowidget = None               

    def setWidgetButtons(self, str):
        match str:
            case 'asp':
                if self.AutoAspect == False:
                    self.AutoAspect = True
                    self.videowidget.aspBtn.setText('AutoAspectOn')
                else: 
                    self.AutoAspect = False
                    self.videowidget.aspBtn.setText('AutoAspect')
           
            case 'clips':
                if self.MakeClips == False:
                    self.MakeClips = True
                    self.videowidget.clpsBtn.setText('MakeClipsOn')
                else: 
                    self.MakeClips = False
                    self.videowidget.clpsBtn.setText('MakeClips')
           
            case 'first':
                if self.FirstFrame == False:
                    self.FirstFrame = True
                    self.videowidget.firstBtn.setText('FirstFrameOn')  
                    if self.SkipFrames == True:
                        self.SkipFrames = False
                        self.videowidget.skipBtn.setText("NthFrame")     
                else: 
                    self.FirstFrame = False
                    self.videowidget.firstBtn.setText('FirstFrame')
                         
            case 'skip':
                if self.SkipFrames == False:
                    self.SkipFrames = True
                    self.videowidget.skipBtn.setText("NthFrameOn")
                    if self.FirstFrame == True:
                        self.FirstFrame = False
                        self.videowidget.firstBtn.setText('FirstFrame')
                else: 
                    self.SkipFrames = False
                    self.videowidget.skipBtn.setText("NthFrame")                    
                         
            case 'filter':
                if self.FilterOn == False:
                    self.FilterOn = True
                    self.videowidget.filterBtn.setText('FilterOn')
                else: 
                    self.FilterOn = False
                    self.videowidget.filterBtn.setText('Filter')       
            
            case 'play':
                if self.PlayVideo == False:
                    self.PlayVideo = True
                    self.videowidget.playBtn.setText('PlayVideoOn')
                else: 
                    self.PlayVideo = False
                    self.videowidget.playBtn.setText('PlayVideo')  
                    
            case 'name':
                if self.AddFileName == False:
                    self.AddFileName = True
                    self.videowidget.nameBtn.setText('FileNameOn')
                else: 
                    self.AddFileName = False
                    self.videowidget.nameBtn.setText('FileName') 
                    
### --------------------------------------------------------
    def toggleAspectBtn(self):
        if self.parent.width()- WID <= Chars['V'][1]:
            self.parent.aspButton.hide()
        else:
            self.parent.aspButton.show()

    def looper(self):  ## doesn't run in qt5
        if self.parent.loop == False:
            self.parent.loop = True
            self.parent.loopButton.setText('LoopOn')
            self.parent.stopButton.setEnabled(False)
        else:
            self.parent.loop = False
            self.parent.loopButton.setText('Loop')
            self.parent.stopButton.setEnabled(True)
            self.parent.stopVideo()
            
    def msgbox(self, str):
        msg = QMessageBox()
        msg.setText(str)
        timer = QTimer(msg)
        timer.setSingleShot(True)
        timer.setInterval(5000)
        timer.timeout.connect(msg.close)
        timer.start()
        msg.exec() 
        
    def pathMod(self, fileName):
        fileName = fileName[-24:]
        if fileName.find('/') > 0:
            fileName = '..' + fileName[fileName.find('/'):]
        return fileName
    
    def returnKey(self, asp):  
        for k, v in Chars.items():
            if asp in v: return k
        return None
    
### --------------------------------------------------------  
    def openFile(self, open=False):  ## opens one file - open = True comes openDirectory else the button 
        self.parent.closeHelpMenu();   self.parent.mediaPlayer.stop() ## blacks out previous video
        if self.parent.path == '':  
            path = os.getcwd()   
        else:
            path = self.parent.path
        fileName, _ = QFileDialog.getOpenFileName(self.parent, "Select Media", path, \
                        "Video Files (*.mov *.mp4 *.mp3 *.m4a *.wav)")
        if fileName != '': 
            if self.SkipFrames == True and open == True:  ## read only one file every Nth frame
                path = os.path.dirname(fileName)  
                fileName = os.path.basename(fileName)
                title = self.setTitle(path)
                self.parent.setFileName(title) 
                QTimer.singleShot(20, partial(self.assembler, path, title, fileName))
            else:       ## play a video
                self.parent.path = os.path.dirname(fileName)    
                self.parent.setFileName(fileName)
                self.parent.mediaPlayer.setPosition(0)  ## shows first frame
                self.parent.mediaPlayer.pause()    
                if self.PlayVideo:  QTimer.singleShot(100, self.parent.playVideo)   ## up to you
                     
    def openDirectory(self):  ## used by clips, point to directory to read from   
        self.parent.closeHelpMenu();   self.parent.mediaPlayer.stop()    
        if self. MakeClips == False: 
            self.msgbox('Make sure Opencv is installed and MakeClipsOn is set')
            return      
        if self.SkipFrames == True:
            self.openFile(True)
        else:
            path = QFileDialog.getExistingDirectory(self.parent, '')
            if path == None or path == '':
                return  
            title = self.setTitle(path)    
            self.parent.setFileName(title)
            QTimer.singleShot(20, partial(self.assembler, os.getcwd(), title))
    
    def setTitle(self, path):
        os.chdir(path)
        title = os.path.basename(path) + '.mov'  ## uses .mp4 codec - works on my mac
        try:
            os.remove(title)
        except:
            None      
        return title
       
    def setFormat(self, key):  
        try:
            self.parent.key = key
            self.parent.aspect = Chars[key][0]
            self.parent.ViewW  = Chars[key][1]
            self.parent.ViewH  = Chars[key][2]
            self.parent.VideoW = Chars[key][3] 
            self.parent.VideoH = Chars[key][4] 
            if key in ('S','T','U','V'):
                self.toggleAspectBtn()
        except:
            return False
                  
### --------------------------------------------------------            
    def zoom(self, zoom):
        if self.parent.mediaPlayer != None:  
            if int(self.parent.height() * zoom) > 1280 or int(self.parent.height()* zoom) < 300:
                return  
                
            asp = 0    
            if self.parent.aspect == 0 and (self.parent.key != '' and self.parent.key != 'O'):
                self.parent.aspect = Chars[self.parent.key][0]  
                      
            elif self.parent.key == 'O' and self.parent.aspect > 0:  ## horizontals
                asp = self.parent.aspect
                nwidth = self.parent.lastVWidth
                
            if self.parent.aspect != 0:
                asp = self.parent.aspect
                
            elif asp == 0:
                self.msgbox('The Aspect Ratio Has Not Been Set')
                return 
                                 
            frW, frH = WID, HGT                      
            height = int(self.parent.height()* zoom)  ## new height  
            
            nvH = (height - frH)  ## new video height
            nvW = int(nvH * asp)  ## new video width   
            nwidth = nvW + frW    ## new widget width   
            
            p, width = self.parent.pos(), self.parent.width()  
            self.parent.resize(nwidth, height)   
            dif = int((self.parent.width() - width)/2) 
            self.parent.move(p.x()-dif, p.y()) 
                 
            self.parent.ViewW, self.parent.ViewH = self.parent.width()-WID, self.parent.height()-HGT 
            
            self.toggleAspectBtn()
                       
### --------------------------------------------------------
    def assembler(self, path, outputVideo, fileName=''):
        self.parent.setWindowTitle(outputVideo)
        
        reads = 0;  frameCount = 0;  dim = (self.parent.VideoW, self.parent.VideoH)
        try:  
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 and .mov
            out = cv2.VideoWriter(outputVideo, fourcc, self.Fps, dim)
        except:
            self.msgbox('assembler: OpenCV not Found')
            return
     
        # print(cv2.__version__)
     
        if self.SkipFrames == False:
            if self.FirstFrame == True:  
                images = [img for img in os.listdir(path) if img.lower().endswith(Mxt)]  ## reads videos
            else:
                images = [img for img in os.listdir(path) if img.lower().endswith(Ext)]  ## reads photos
            images.sort()  
                    
        elif self.SkipFrames == True:
            images = [fileName]  ## read only one file
            image_name = images
 
        for image_name in images:
            image_path = os.path.join(path, image_name)     
            
            if outputVideo in image_path:  ## don't read the output file
                continue
            
            cap = cv2.VideoCapture(image_path)
            if not cap.isOpened():
                self.msgbox("assembler: Could not open video.")
                return

            if self.FirstFrame == True:  ## reads the first frame of a video 
                ret, img = cap.read()
                if not ret:
                    self.msgbox("assembler: Could not read the first frame.")
                    return
                if self.FilterOn and self.aspMatch(img) == False:
                    continue     
                reads = self.writeOut(img, image_name, out, reads)
                if reads >= self.Max:
                    break

            elif self.SkipFrames == True:  ## reads the Nth frame of a video
                while True:
                    ret, img = cap.read()
                    if not ret:  # end of video
                        break   
                    if self.FilterOn and self.aspMatch(img) == False:
                        continue
                    if frameCount % self.Rnf == 0:  ## default one, every frame - set in widget
                        reads = self.writeOut(img, image_name, out, reads)
                        if reads >= self.Max:
                            break     
                    frameCount += 1
                    
            else:  
                img = cv2.imread(image_path)  ## reads a directory of photos
                if img is None:
                    self.msgbox(f"assembler Could not read file {image_name}")
                    continue  
                if self.FilterOn and self.aspMatch(img) == False:
                    continue
                reads = self.writeOut(img, image_name, out, reads)
                if reads >= self.Max:       
                    break
              
        if reads > 0:
            if self.FirstFrame == True or self.SkipFrames == True: cap.release()
            out.release()
            self.msgbox(f"Video: {outputVideo} frames: {reads}")
            fileName = os.getcwd() + '/' + outputVideo  
            self.parent.setFileName(fileName)  
            self.parent.mediaPlayer.setPosition(0)
            self.parent.mediaPlayer.pause()
            if self.PlayVideo:  QTimer.singleShot(100, self.parent.playVideo)
        else:
            os.remove(outputVideo)
            self.msgbox('assembler: Nothing saved')
            return
        
    def aspMatch(self, img):
        h, w = img.shape[:2]  ## numpy - returns rows and columns
        asp  = math.floor(w/h *100)/100.0 
        if asp != self.parent.aspect:
            del img
            return False
        return True
 
    def writeOut(self, img, image_name, out, k):     
        # img = cv2.rotate(img, cv2.ROTATE_180)    ## just in case they're upsidedown - and ROTATE_90_CLOCKWISE) etc. 
        img = self.ctrOnBackground(img, image_name)     
        if self.AddFileName == True:
            self.addFileName(img, image_name)
        if isinstance(img, np.ndarray):
            n = 0 
            while n < self.Wpr:  ## writes per read
                time.sleep(.05)
                out.write(img)  
                n += 1        
            del img
            k += 1
        return k
                    
    def addFileName(self, img, name):  ## right out of google - thanks
        org   = (20, self.parent.VideoH-30)
        font  = cv2.FONT_HERSHEY_SIMPLEX
        scale = 1
        color = (0,255,255)
        thickness = 2
        type  = cv2.LINE_AA 
        cv2.putText(img, name, org, font, scale, color, thickness, type)
        
### --------------------------------------------------------
    def ctrOnBackground(self, img, imgName): 
        fg_h, fg_w = img.shape[:2]
        bg_w, bg_h = self.parent.VideoW, self.parent.VideoH
  
        if bg_h < fg_h:  ## resize vertical - numpy likes it reversed  
            r = bg_h / fg_h
            fg_h = int(fg_h * r)
            fg_w = int(fg_w * r)
            img  = cv2.resize(img, (fg_w, fg_h), interpolation= cv2.INTER_LINEAR)    
            fg_h, fg_w = img.shape[:2]  
        
        if fg_w > bg_w:  ## do this till it fits
            while (bg_w - fg_w) != 0:
                r = bg_w / fg_w
                fg_w = int(fg_w * r)
                fg_h = int(fg_h * r)
                img  = cv2.resize(img, (fg_w, fg_h), interpolation= cv2.INTER_LINEAR)    
                fg_h, fg_w = img.shape[:2]
                                                                                                                                                    
        background_color = (0, 0, 0)  ## Black (B, G, R)  ## numpy
        bkgImage = np.full((bg_h, bg_w, 3), background_color, dtype=np.uint8)

        start_x = (bg_w - fg_w) // 2  ## Calculate the centering position  
        start_y = (bg_h - fg_h) // 2

        end_x = start_x + fg_w
        end_y = start_y + fg_h
        
        bkgImage[start_y:end_y, start_x:end_x] = img
        
        # # Ensure foreground fits within background <<------------------- shouldn't need to check
        # # if start_x < 0 or start_y < 0 or end_x > bg_w or end_y > bg_h: 
        # #     print(f'a: {imgName}\tstart x {start_x}  bkgW {bg_w}  
        # #           forW {fg_w}  offs {(bg_w - fg_w) // 2}' )
        # #     return None
        # try:
        #     if img.shape[2] == 4:  ## <<<---------------  uncomment for alpha channel
        #         alpha_channel = img[:, :, 3] / 255.0
        #         for c in range(0, 3):
        #             bkgImage[start_y:end_y, start_x:end_x, c] = (
        #                 bkgImage[start_y:end_y, start_x:end_x, c] * (1 - alpha_channel) +
        #                 img[:, :, c] * alpha_channel
        #             )
        #     else:   ## No alpha channel      
        #         bkgImage[start_y:end_y, start_x:end_x] = img
        # except:
        #     return None  
                          
        return bkgImage
                
### ---------------------- that's all ---------------------- 
 

    