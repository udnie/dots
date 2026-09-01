
import math
import time
import cv2  ## 4.12.0 or above

import os.path
import numpy as np  

### ----------------- videoClipsMaker.py -------------------
''' Source for assembler, ctrOnBackground, a single-file dialog.
    and a number of functions including setDefaultSizes and those 
    used by Settings. 
    Opencv is required to run assembler and by getMetaData in 
    videoPlayerShared to set the video aspect-ratio on opening if
    self.AutoAspect is True.  The videoClipsWidget defaults(Settings) 
    are set here. '''
### --------------------------------------------------------
    
from functools          import partial

from PyQt6.QtCore       import QTimer
from PyQt6.QtWidgets    import QFileDialog
                                
from videoClipsWidget   import *

Ext = (".tif", ".png", ".jpg", ".jpeg", ".webp")
Mxt = (".mov", ".mp4")

### --------------------------------------------------------
class Clips:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
        
        self.parent = parent
        self.settings = None
   
### ----- widget defaults(Settings) - the limits are set in the widget sliders ----- ###

        self.Fps = 5    ## frames per second - less than 5 and the video won't play
        self.Max = 25   ## max number of photos to read/write  
        self.Wpr = 4    ## writes per read
        self.Rnf = 1    ## read every 'n frame - just to make sure 
                       
        self.AutoAspect  = True      ## True reads the video metadata to set the aspect ratio and resize the widget
                                     ## requires that getVideoWidthHeight is working                                     
        self.MakeClips   = False     ## set on from widget only when making a clip - interferes with autoAspect
        self.FirstFrame  = False     ## True - read only the first frame of a video       
        self.SkipFrames  = False     ## True - read the Nth frame of a video 
        self.FilterOn    = False     ## True - image aspect matches self.aspect (parent)
        self.PlayVideo   = False     ## True plays video upon loading
        self.AddFileName = False     ## True add to frame
        
        # print(cv2.__version__)  ## just to make sure - needs to be 4.12 or better
   
### --------------------------------------------------------       
    def toggleSettings(self, parent):
        if self.settings == None:  ## widget for clips settings  
            self.settings = Settings(parent)
        elif self.settings != None:
            self.closeSettings()
      
    def closeSettings(self):
        if self.settings != None:
            self.settings.close()
        self.settings = None 
        time.sleep(.03)         
                
    def setWidgetButtons(self, str):
        match str:
            case 'asp':
                if not self.AutoAspect:
                    self.AutoAspect = True
                    self.settings.aspBtn.setText('AutoAspectOn')
                else: 
                    self.AutoAspect = False
                    self.settings.aspBtn.setText('AutoAspect')
           
            case 'clips':
                if not self.MakeClips:
                    self.MakeClips = True
                    self.settings.clpsBtn.setText('MakeClipsOn')
                else: 
                    self.MakeClips = False
                    self.settings.clpsBtn.setText('MakeClipsOff')
           
            case 'first':
                if not self.FirstFrame:
                    self.FirstFrame = True
                    self.settings.firstBtn.setText('FirstFrameOn')  
                    if self.SkipFrames:
                        self.SkipFrames = False
                        self.settings.skipBtn.setText("NthFrame")     
                else: 
                    self.FirstFrame = False
                    self.settings.firstBtn.setText('FirstFrame')
                         
            case 'skip':
                if not self.SkipFrames:
                    self.SkipFrames = True
                    self.settings.skipBtn.setText("NthFrameOn")
                    if self.FirstFrame:
                        self.FirstFrame = False
                        self.settings.firstBtn.setText('FirstFrame')
                else: 
                    self.SkipFrames = False
                    self.settings.skipBtn.setText("NthFrame")                    
                         
            case 'filter':
                if not self.FilterOn:
                    self.FilterOn = True
                    self.settings.filterBtn.setText('FilterOn')
                else: 
                    self.FilterOn = False
                    self.settings.filterBtn.setText('Filter')       
            
            case 'play':
                if not self.PlayVideo:
                    self.PlayVideo = True
                    self.settings.playBtn.setText('PlayVideoOn')
                else: 
                    self.PlayVideo = False
                    self.settings.playBtn.setText('PlayVideo')  
                    
            case 'name':
                if not self.AddFileName:
                    self.AddFileName = True
                    self.settings.nameBtn.setText('FileNameOn')
                else: 
                    self.AddFileName = False
                    self.settings.nameBtn.setText('FileName') 
            case _:
                    return
                    
### --------------------------------------------------------
    def closeThese(self):  
        self.closeSettings() 
        self.parent.closeMediaPlayer() if self.parent.player == 'two' else \
            self.parent.closeOnOpen()
              
    def makingClips(self):  ## by reading one or all files - "both"
        if not self.MakeClips: 
            self.parent.shared.msgbox('Make sure Opencv is installed and MakeClipsOn is set')
            return        
        self.closeThese()
        self.skipFrames() if self.SkipFrames else self.readAll()
            
    def skipFrames(self):  ## read a file reading every N'th frame - "both"
        if fileName := self.returnFileName():   
            path = os.path.dirname(fileName)  
            fileName = os.path.basename(fileName)       
            output = self.setOutput(path)
            if self.parent.player == "one": 
                self.parent.shared.setFileNameInMediaPlayer(fileName)
            QTimer.singleShot(20, partial(self.assembler, path, output, fileName)) 
                      
    def readAll(self):  ## needed an update - was only writing to .mov
        path = QFileDialog.getExistingDirectory(self.parent, '') 
        if path == None or path == '':
            return 
        output = self.setOutput(path)
        QTimer.singleShot(20, partial(self.assembler, path, output))

    def setOutput(self, path):
        os.chdir(path)
        output = os.path.basename(os.getcwd())
        return output.strip() + '.mov'
    
    def returnFileName(self):  
        self.closeThese()  ## select a single file - open for "one" or make clips for "both"  
        path = os.getcwd() if self.parent.path == '' \
            else self.parent.path    
        try:
            fileName, _ = QFileDialog.getOpenFileName(self.parent, "Select Media",\
                path, "Video Files (*.mov *.mp4 *.mp3 *.m4a *.wav)")
        except:
            self.parent.shared.msgbox('error opening file')
            return None
        return fileName 
                                        
    def setDefaultSizes(self, key):  
        try:
            self.parent.key = key
            self.parent.aspect = Keys[key][0]  ## aspect
            self.parent.ViewW  = Keys[key][1]  ## min width
            self.parent.ViewH  = Keys[key][2]  ## min height
            self.parent.VideoW = Keys[key][3]  ## max width
            self.parent.VideoH = Keys[key][4]  ## max height
        except:
            self.parent.shared.msgbox('error in setDefaultSizes')
            return
        if key in ('S','T','U','V') and self.parent.player == 'one':
            self.parent.showHideAspectBtn()   ## <- "one"
                                                                  
### --------------------------------------------------------
    def assembler(self, path, outputVideo, fileName=''):
        self.parent.setWindowTitle(outputVideo)
         
        tmp = os.path.basename(os.path.dirname(path).strip() + '.mov')
        if os.path.exists(tmp) and tmp == outputVideo:
            os.remove(tmp)
        
        reads = 0;  frameCount = 0;  dim = (self.parent.VideoW, self.parent.VideoH)
 
        try:  
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 and .mov
            out = cv2.VideoWriter(outputVideo, fourcc, self.Fps, dim)
        except:
            self.parent.shared.msgbox('assembler: error setting output' +  '\n' + 
                                      'check if opencv installed')
            return
                          
        if self.SkipFrames:
            images = [fileName]  ## read only one file
            image_name = images     
        else:      
            if self.FirstFrame:  ## make a list of all the files that match the extension
                images = [img for img in os.listdir(path) if img.lower().endswith(Mxt)]  ## reads videos
            else:
                images = [img for img in os.listdir(path) if img.lower().endswith(Ext)]  ## reads photos
            images.sort()  

        for image_name in images:   
            if outputVideo == image_name:  ## don't read the output file ".mov"
                continue
         
            image_path = os.path.join(path, image_name)   
            cap = cv2.VideoCapture(image_path)
            
            if not cap.isOpened():
                self.parent.shared.msgbox("assembler: Could not open video.")
                return

            if self.FirstFrame:  ## reads the first frame of a video    
                ret, img = cap.read()
                if not ret:
                    self.parent.shared.msgbox("assembler: Could not read the first frame.")
                    return
                
                if self.FilterOn and not self.aspMatch(img):
                    continue     
                
                reads = self.writeOut(img, image_name, out, reads)
                if reads >= self.Max:  ## number of files to read
                    break

            elif self.SkipFrames:  ## reads the Nth frame of a video
                while True:
                    ret, img = cap.read()
                    if not ret:  # end of video
                        break   
                    if self.FilterOn and not self.aspMatch(img):
                        continue
                    if frameCount % self.Rnf == 0:  ## default one, every frame - set in widget
                        reads = self.writeOut(img, image_name, out, reads)
                        if reads >= self.Max:
                            break     
                    frameCount += 1
                    
            else:       
                img = cv2.imread(image_path)  ## read a directory of photos
                if img is None:
                    self.parent.shared.msgbox(f"assembler Could not read file {image_name}")
                    continue  
                if self.FilterOn and not self.aspMatch(img):
                    continue
                reads = self.writeOut(img, image_name, out, reads)
                if reads >= self.Max:       
                    break
              
        if reads > 0:
            if self.FirstFrame or self.SkipFrames: cap.release()
            out.release()   
            self.parent.shared.msgbox(f"Video: {outputVideo} frames: {reads}")
            fileName = os.getcwd() + '/' + outputVideo    
            
            self.parent.setMediaPlayer(fileName) if self.parent.player == 'one' else \
                self.parent.setMediaPlayer(fileName, 'addToScene')  ## setMediaPlayer is unique by parent
            
            if self.parent.mediaPlayer:
                self.parent.mediaPlayer.setPosition(0)
                self.parent.mediaPlayer.pause()
            if self.PlayVideo: QTimer.singleShot(100, self.parent.shared.playVideo)
        else:
            os.remove(outputVideo)
            self.parent.shared.msgbox('assembler: Nothing saved')
            return
    
    def aspMatch(self, img):  ## if filterOn selected
        h, w = img.shape[:2]  ## numpy - returns rows and columns
        asp  = math.floor(w/h *100)/100.0 
        if asp != self.parent.aspect:
            del img
            return False
        return True
 
    def writeOut(self, img, image_name, out, k):     
        # img = cv2.rotate(img, cv2.ROTATE_180)  ## just in case they're upsidedown 
        img = self.ctrOnBackground(img, image_name)  ## or ROTATE_90_CLOCKWISE) etc...
        if self.AddFileName:
            self.addFileName(img, image_name.strip())
        if isinstance(img, np.ndarray):
            n = 0 
            while n < self.Wpr:  ## writes per read
                time.sleep(.03)
                out.write(img)  
                n += 1        
            del img
            k += 1
        return k
                    
    def addFileName(self, img, name):  ## right out of google - thanks
        if name == '.mov':
            return
        org   = (20, self.parent.VideoH-25)
        font  = cv2.FONT_HERSHEY_SIMPLEX
        scale = 1
        color = (0,255,255)
        thickness = 2
        type  = cv2.LINE_AA 
        cv2.putText(img, name, org, font, scale, color, thickness, type)
        
### --------------------------------------------------------
    def ctrOnBackground(self, img, imgName):  
        img_h, img_w = img.shape[:2]
        vid_w, vid_h = self.parent.VideoW, self.parent.VideoH
        
        if vid_h < img_h:  ## resize vertical - numpy likes it reversed  
            r = vid_h / img_h
            img_h = int(img_h * r)
            img_w = int(img_w * r)
            img  = cv2.resize(img, (img_w, img_h), interpolation= cv2.INTER_LINEAR)    
            img_h, img_w = img.shape[:2] 
        else:
            r = img_h / vid_h
            img_h = int(img_h * r)
            img_w = int(img_w * r)
            img  = cv2.resize(img, (img_w, img_h), interpolation= cv2.INTER_LINEAR)    
            img_h, img_w = img.shape[:2]
        
        if img_w > vid_w:  ## do this till it fits   
            while (vid_w - img_w) != 0:
                r = vid_w / img_w
                img_w = int(img_w * r)
                img_h = int(img_h * r)
                img  = cv2.resize(img, (img_w, img_h), interpolation= cv2.INTER_LINEAR)    
                img_h, img_w = img.shape[:2]
                
        elif img_w < vid_w:
            if img_h < vid_h:  ## do this first - set to height
                r = vid_h/img_h
                if (r * img_w) <= vid_w:
                    img_h = int(img_h * r)
                    img_w = int(img_w * r)
                else:
                    s = vid_w/(img_w *r)  ##  width needs to be reduced
                    img_w = int((img_w * r) * s)
                    img_h = int((img_h * r) * s)
                
                img  = cv2.resize(img, (img_w, img_h), interpolation= cv2.INTER_LINEAR)  
                img_h, img_w = img.shape[:2]
                                                                                                                                                
        background_color = (0, 0, 0)  ## Black (B, G, R)  ## numpy
        bkgImage = np.full((vid_h, vid_w, 3), background_color, dtype=np.uint8)

        start_x = (vid_w - img_w) // 2  ## Calculate the centering position  
        start_y = (vid_h - img_h) // 2

        end_x = start_x + img_w
        end_y = start_y + img_h
    
        bkgImage[start_y:end_y, start_x:end_x] = img
   
        # # Ensure foreground fits within background <<------------------- shouldn't need to check
        # # if start_x < 0 or start_y < 0 or end_x > vid_w or end_y > vid_h: 
        # #     print(f'a: {imgName}\tstart x {start_x}  bkgW {vid_w}  
        # #           forW {img_w}  offs {(vid_w - img_w) // 2}' )
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




