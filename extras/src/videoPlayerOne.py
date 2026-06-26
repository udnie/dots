
import os
import sys
import time
import math  

### ------------------ videoPlayerOne.py ------------------- 
''' Source for setting formats, buttons, resizing this widget and
    mediaPlayer, and playing video. Running the python script-qt6.py will 
    remove all the qt5 and pyside code and comments, there are scripts 
    for qt5 and pyside as well.
    OpenCV is required, the very latest version - 4.12.0, to create video 
    clips and to detect and set a videos aspect ratios - formats.
    Go to getMetaData in videoPlayerShared to enable one of the three code 
    options. The keys '[', ']'  can scale up or scale down videoPlayerOne,  
    and a right-mouse click displays the help menu.  
    See videoClipsMaker for changes to defaults and clipsWidget for settings. 
    Size detection doesn't work if clips are on.'''
### -------------------------------------------------------- 

from PyQt6.QtCore       import Qt
from PyQt6.QtGui        import QGuiApplication
from PyQt6.QtWidgets    import QWidget, QVBoxLayout, QApplication, QSizePolicy
                                    
from videoClipsMaker    import Clips
from videoClipsWidget   import *
from videoPlayerShared  import *
from videoPlayerHelp    import VideoMenuKeys

### --------------------------------------------------------
class VideoPlayer(QWidget):
### --------------------------------------------------------
    def __init__(self):
        super(VideoPlayer, self).__init__()         
        self.setWindowTitle("VideoPlayerOne and ClipsMaker")
           
        self.setUI()
        self.show()
              
### --------------------------------------------------------        
    def init(self):
        self.key = 'F'   ## <<----->> open full frame - 3:2]
        self.player = 'one'
        self.path = ''
        self.fileName = ''
        self.aspect = 0.0
        self.flag = False
        self.helpFlag = False 
        self.helpMenu = None

        self.saveW = self.width()
        self.saveH = self.height()
                                                               
    def dragEnterEvent(self, e):  
        if e.mimeData().hasUrls():   
            m = e.mimeData()
            fileName = m.urls()[0].toLocalFile() 
            self.setMediaPlayer(fileName)  
            self.shared.playVideo() if self.clips.PlayVideo else \
                self.mediaPlayer.pause()  ## PlayVideo set in clipsMaker
            e.accept()
        else:
            e.ignore()
       
    def dragLeaveEvent(self, e):
        e.accept()

### -------------------------------------------------------- 
    def keyPressEvent(self, e):
        key = e.key()
        mod = e.modifiers()   
                  
        if key == Qt.Key.Key_Space:  ## spacebar to pause/resume
            self.shared.playVideo()   
            
        elif key == Qt.Key.Key_S and mod & Qt.KeyboardModifier.ShiftModifier:
            self.shared.toggleSlider()
                  
        elif key == Qt.Key.Key_F and mod & Qt.KeyboardModifier.ShiftModifier:
            self.clips.openFile() 
                                       
        elif key == Qt.Key.Key_BracketRight or mod & Qt.KeyboardModifier.ShiftModifier \
            and key in (Qt.Key.Key_Greater, Qt.Key.Key_Plus):
                self.zoom(1.05) 
                             
        elif key == Qt.Key.Key_BracketLeft or mod & Qt.KeyboardModifier.ShiftModifier \
            and key in (Qt.Key.Key_Less, Qt.Key.Key_Underscore):
                self.zoom(.95)  
                
        elif key in (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape):
            self.bye()
       
        else:
            try:
                key = chr(e.key())
            except:
                return  
        if key in VideoMenuKeys:
            self.VideoMenuKeys(key)
  
    def VideoMenuKeys(self,key):    
        if key in AspKeys:
            self.shared.openPlayer(key)     
        else:  
            match key:
                case 'Spacebar':
                    self.shared.playVideo()
                case 'L':
                    self.shared.looper()      
                case 'Settings':
                    self.clips.toggleSettings(self)  ## clipMaker settings
                case ']':
                    self.zoom(1.05)  
                case '[':    
                    self.zoom(0.95)      
                case 'Aspect':
                    self.setAspButton()  ## set aspect ratio manually clicking on aspect button
                case 'C':
                    self.shared.closeHelpMenu()  ## improvised clear
                    self.mediaPlayer.stop()        
                case 'Clips':   
                    self.clips.makingClips()  ## if MakeClipsOn sets path to folder
                case 'Shift-F':         
                    self.openFile() 
                case 'Shift-S':
                    self.shared.toggleSlider()
                case 'M':
                    self.shared.videoSliderMenus()  
                case 'W':
                    self.shared.msgbox(self.path) if self.path != '' else\
                        self.shared.msgbox(os.getcwd())  
                case 'X' | 'Q':
                    self.bye()   
                case _:
                    return
           
### --------------------------------------------------------                                                                              
    def mousePressEvent(self, e): 
        if e.button() == Qt.MouseButton.RightButton:
            if self.clips.settings == None:
                self.shared.closeHelpMenu() if self.helpFlag else \
                    self.shared.openHelpMenu() 
        else:
            self.shared.closeHelpMenu()
        e.accept() 
   
    def mouseDoubleClickEvent(self, e): 
        if self.fileName != '':  
            self.shared.msgbox(self.fileName + '\n' + 'aspect: ' + str(self.aspect))
        e.accept()
   
    def closeEvent(self, e):
        self.bye()
        e.accept()

### --------------------------------------------------------
    def openFile(self): 
        if fileName := self.clips.returnFileName():      
            self.path = os.path.dirname(fileName)  
            if self.setMediaPlayer(fileName) and self.mediaPlayer != None: 
                if self.clips.PlayVideo:  QTimer.singleShot(100, self.shared.playVideo) 
        else:
            return
        
    def setMediaPlayer(self, fileName): 
        if not self.shared.setFileNameInMediaPlayer(fileName):
            return False   
        self.shared.setAutoAspect(fileName)  ## won't stop it from playing
        self.playButton.setEnabled(True)      
        self.path = fileName[0:fileName.rfind('/')]  
        self.fileName = fileName  
        return True   

    def setDisplaySize(self, key):
        self.flag = True
        hgt = HGT if self.shared.sliderVisible else HGT-PAD  
        if key in AspKeys:
            self.resize(self.ViewW+WID, self.ViewH+hgt)  
        elif self.aspect >= 1.0:  ## use default height for horizontal
            self.resize(int(ViewH*self.aspect)+WID, ViewH+hgt)         
        elif self.aspect < 1.0:
            height = int((VertW-WID)/self.aspect)+hgt ## use default vertical width
            self.resize(VertW, height)  
        self.aspButton.setText("Aspect: " + key)
        if key == 'O':  self.shared.setVideoWH()  ## for assembler 
        time.sleep(.03)
        self.shared.moveAndSet()

    def setAspButton(self):  ## from aspect button   
        if self.aspect == 0:
            v = self.videoWidget.size()  
            self.aspect = math.floor(v.width()/v.height() * 100)/100.0          
            if key := self.shared.returnKey(self.aspect): 
                self.clips.setDefaultSizes(key)  
            else:
                key = 'O'     
            self.setDisplaySize(key)  
        else:
            self.aspect = 0
            self.aspButton.setText("Set Aspect")
       
    def showHideAspectBtn(self):  ## also called from clipsMaker
        self.aspButton.show() if self.width() > VertW \
            else self.aspButton.hide()
                       
    def closeOnOpen(self):  
        self.shared.closeHelpMenu();   
        self.clips.closeSettings()
        time.sleep(.03)  
        self.shared.looperOff() 
        if self.mediaPlayer != None:
            self.shared.stopVideo()
 
### --------------------------------------------------------
    def setUI(self):
        self.setMinimumHeight(MinWid+100)
        self.setMinimumWidth(MinWid)
        
        self.setMaximumHeight(1200)
        self.setMaximumWidth(1850)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.resize(int(ViewH*1.5)+WID, ViewH+HGT)  ## default 3:2
             
        self.init()  
         
        self.clips = Clips(self) 
        self.shared = Shared(self)
           
        self.mediaPlayer = MediaPlayer(self)
        self.videoWidget = self.mediaPlayer.videoWidget
     
        if len(sys.argv) > 1: 
            self.path = sys.argv[1]
         
        vbox = QVBoxLayout() 
     
        vbox.addWidget(self.videoWidget, Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(setButtons(self), Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(setSlider(self), Qt.AlignmentFlag.AlignHCenter)
   
        self.setLayout(vbox)            
   
        self.shared.openPlayer(self.key)  ## open full frame - 3:2
         
        x = QGuiApplication.primaryScreen().availableGeometry().center().x()
        self.move(x-int((ViewW+WID)/2), HorzH)  
  
        self.setAcceptDrops(True)  
        self.grabKeyboard() 
   
### -------------------------------------------------------- 
    def zoom(self, zoom):  ## maintain current aspect ratio
        if self.mediaPlayer != None:  
            if int(self.height() * zoom) > 1280 or int(self.height()* zoom) < 300:
                return  
                
            asp = 0    
            if self.aspect == 0 and (self.key != '' and self.key != 'O'):
                self.aspect = Keys[self.key][0]  
                      
            elif self.key == 'O' and self.aspect > 0:  ## horizontals
                asp = self.aspect
                nwidth = self.VideoW
                
            if self.aspect != 0:
                asp = self.aspect
                
            elif asp == 0:
                self.shared.msgbox('The Aspect Ratio Has Not Been Set')
                return 
                                                       
            height = int(self.height()* zoom)  ## new height   
            nvH = (height - HGT)  ## new video height
            
            nvW = int(nvH * asp)  ## new video width   
            nwidth = nvW + WID    ## new widget width   
            
            p, width = self.pos(), self.width()  
            self.resize(nwidth, height)  
             
            dif = int((self.width() - width)/2) 
            self.move(p.x()-dif, p.y())  
                   
            self.ViewW, self.ViewH = self.width()-WID, self.height()-HGT 
            self.showHideAspectBtn() 
                                                                                                                               
### --------------------------------------------------------   
    def resizeEvent(self, e):  ## maintains current aspect ratio
        if self.flag:
            self.flag = False
            return 
        elif self.aspect > 0:    
            
            hgt = HGT if self.shared.sliderVisible else HGT-PAD
            
            width  = int((self.height()-hgt) * self.aspect)+WID
            height = int((self.width()-WID)/ self.aspect)+hgt  
            maxwid = int((MaxHgt-hgt) * self.aspect)+WID 
            which  = self.shared.getDirection()     
            
            if width != self.saveW:
                if width > maxwid:
                    self.videoWidget.resize(maxwid-WID, height-hgt)
                    self.resize(maxwid, height)
              
                elif width < MinWid:         
                    if self.aspect != 1.0 and which != 'bottom': 
                        self.videoWidget.resize(MinWid-WID, height-hgt)
                        self.resize(MinWid, height)  
                    else:
                        self.videoWidget.resize(MinWid-WID, MinHgt-hgt) 
                        self.resize(MinWid, MinHgt)  ## square  
              
                elif which in ('botleft', 'botright'):   
                    self.videoWidget.resize(self.width()-WID, height-hgt)
                    self.resize(self.width(), height)       
                      
                else:
                    self.videoWidget.resize(width-WID, self.height()-hgt)
                    self.resize(width, self.height())   
                              
            elif height != self.saveH: 
                if height > MaxHgt:
                    self.resize(maxwid, MaxHgt)
                                           
                elif height < MinHgt:       
                    self.resize(width, MinHgt-hgt)  
                    
                elif height > MinHgt:  
                    self.videoWidget.resize(self.width()-WID, height-hgt)
                    self.resize(self.width(), height) 
      
            dif = int((self.width() - self.saveW)/2)
            self.move(self.pos().x()-dif, self.pos().y()) 
             
            time.sleep(.007)  
            self.saveW, self.saveH = self.width(), self.height()        
        e.accept() 

### --------------------------------------------------------
    def bye(self):
        self.shared.closeHelpMenu()
        self.clips.closeSettings()
        self.close()
   
### --------------------------------------------------------  
if __name__ == '__main__':
    app = QApplication(sys.argv)
    play = VideoPlayer()
    sys.exit(app.exec())
    
### ---------------------- that's all ----------------------



