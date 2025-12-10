
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

from PyQt6.QtCore       import Qt, QUrl, QPoint
from PyQt6.QtGui        import QGuiApplication
from PyQt6.QtWidgets    import QWidget, QVBoxLayout, QApplication, QSizePolicy
                                    
from PyQt6.QtMultimedia         import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets  import QVideoWidget

# from PyQt6.QtMultimedia           import QMediaContent  ## 5

from videoClipsMaker        import Clips, Ext
from videoClipsWidget       import *
from videoPlayerShared      import *

### --------------------------------------------------------   
class MediaPlayer(QMediaPlayer): 
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
        
        self.videoPlayer = parent
    
        self.mediaPlayer = QMediaPlayer(self) ## 6
        # self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)  ## 5 
            
        self.videoWidget = QVideoWidget()   
        self.mediaPlayer.setVideoOutput(self.videoWidget)
         
        self.videoWidget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
          
        self.mediaPlayer.mediaStatusChanged[QMediaPlayer.MediaStatus].connect(self.mediaStateChanged) 
       
        self.mediaPlayer.positionChanged.connect(self.videoPlayer.shared.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.videoPlayer.shared.durationChanged)
             
        self.audioOut = QAudioOutput()  ## 6
        self.mediaPlayer.setAudioOutput(self.audioOut)  ## 6
  
        self.mediaPlayer.setLoops(-1)
        
### -----------------------------------------------------------------
    def setFileName(self, fileName):  ## set in clipsMaker
        try:
            self.mediaPlayer.setSource((QUrl.fromLocalFile(fileName)))  ## 6
            # self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(fileName))))  ## 5  
        except:
            return False
        self.mediaPlayer.pause()  ## makes it visible 
        return True
        
    def playVideo(self):  
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:  ## 6
        # if self.mediaPlayer.state() == QMediaPlayer.PlayingState:  ## 5
            self.mediaPlayer.pause()  
            self.videoPlayer.playButton.setText('Resume') 
        elif self.videoPlayer.fileName != '':  
            self.mediaPlayer.play()  
            self.videoPlayer.playButton.setText('Pause') 
     
    def mediaStateChanged(self, status): 
        if status == QMediaPlayer.MediaStatus.EndOfMedia:  
            while not (self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.StoppedState):   ## 6
            # while not (self.mediaPlayer.state() == QMediaPlayer.State.StoppedState):  ## 5
                time.sleep(.005) 
            self.stopVideo() 

    def stopVideo(self):  
        if self.videoPlayer.loopSet == False: 
            self.mediaPlayer.stop()
            self.setPosition(0) 
            self.mediaPlayer.pause() 
            self.videoPlayer.playButton.setText('Play')
            time.sleep(.03)
        else:   
            self.playVideo()  ## loop it

    def setPosition(self, position):  ## from videoPlayer by finger pull
        self.mediaPlayer.setPosition(position)
  
### --------------------------------------------------------
class VideoPlayer(QWidget):
### --------------------------------------------------------
    def __init__(self):
        super(VideoPlayer, self).__init__()    
        self.setWindowTitle("Video Player One")
          
        self.setMinimumHeight(MinWid+100);  self.setMinimumWidth(MinWid)
        self.setMaximumHeight(1200);        self.setMaximumWidth(1850)
    
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.resize(int(ViewH*1.5)+WID, ViewH+HGT)  ## default 3:2
             
        self.init()  
         
        self.clips = Clips(self) 
        self.shared = Shared(self)
        
        self.mediaPlayer = MediaPlayer(self)
        self.videoWidget = self.mediaPlayer.videoWidget
        
        self.sliderVisible = True
                
        if len(sys.argv) > 1: 
            self.path = sys.argv[1]
         
        vbox = QVBoxLayout() 
        
        vbox.addWidget(self.videoWidget)
        vbox.addWidget(setButtons(self))
        if self.sliderVisible == True:
            vbox.addWidget(setSlider(self), Qt.AlignmentFlag.AlignCenter) 
       
        self.setLayout(vbox)            
   
        self.shared.openPlayer(self.key)   ## <<----->> open full frame - 3:2]  
         
        x = QGuiApplication.primaryScreen().availableGeometry().center().x()
        self.move(x-int((ViewW+WID)/2), HorzH)  
  
        self.setAcceptDrops(True)  
        self.grabKeyboard() 
            
        self.show()
          
### --------------------------------------------------------        
    def init(self):
        self.key = 'F'   ## <<----->> open full frame - 3:2]
        self.path = ''
        self.fileName = ''
        self.player = 'one'
        self.aspect = 0.0
        self.lastVWidth = 0
        self.lastHeight = 0 
        self.loopSet = False
        self.helpFlag = False 
        self.helpMenu = None
        self.saveW = self.width()
        self.saveH = self.height()
        self.save = QPoint()
        self.flag = False
                                                                        
    def dragEnterEvent(self, e):  
        if e.mimeData().hasUrls():   
            m = e.mimeData()
            fileName = m.urls()[0].toLocalFile() 
            self.setFileName(fileName)  
            self.playVideo() if self.clips.PlayVideo else \
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
         
        if key == Qt.Key.Key_Escape:
            self.bye()    
                 
        if key == Qt.Key.Key_Space:  ## spacebar to pause/resume
            self.playVideo()   
            
        elif key == Qt.Key.Key_S and mod & Qt.KeyboardModifier.ShiftModifier:
            self.shared.toggleSlider()
                          
        elif key == Qt.Key.Key_BracketRight or mod & Qt.KeyboardModifier.ShiftModifier \
            and key in (Qt.Key.Key_Greater, Qt.Key.Key_Plus):
                self.shared.zoom(1.05) 
                             
        elif key == Qt.Key.Key_BracketLeft or mod & Qt.KeyboardModifier.ShiftModifier \
            and key in (Qt.Key.Key_Less, Qt.Key.Key_Underscore):
                self.shared.zoom(.95)  
                
        elif key in (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape):
            self.bye()
       
        else:
            try:
                key = chr(e.key())
            except:
                return  
        if key in SharedKeys:
            self.sharedKeys(key)
  
    def sharedKeys(self,key):  
        if key in AspKeys:
            self.shared.openPlayer(key)     
        else: 
            match key:
                case 'L':
                    self.shared.looper()  
                case ']':
                    self.shared.zoom(1.05)  
                case '[':    
                    self.shared.zoom(0.95)      
                case 'Aspect':
                    self.setAspButton()  ## set aspect ratio manually clicking on aspect button
                case 'Settings':
                    self.clips.toggleSettings(self)  ## clipMaker settings
                case 'C':
                    self.shared.closeHelpMenu()  ## improvised clear
                    self.mediaPlayer.stop()        
                case 'Clips':   
                    self.shared.openDirectory()  ## if MakeClipsOn sets path to folder
                case 'Shift-S':
                    self.shared.toggleSlider()
                case 'X' | 'Q':
                    self.bye()   
                case _:
                    return
           
### --------------------------------------------------------                                                                              
    def mousePressEvent(self, e):  ## takes two fingers on my mac and a double-click
        self.save = e.globalPosition()  
        if e.button() == Qt.MouseButton.RightButton:
            if self.clips.settings == None:
                self.shared.closeHelpMenu() if self.helpFlag == True \
                    else self.shared.openHelpMenu() 
        e.accept() 
   
    def mouseMoveEvent(self, e):
        self.moveThis(e)
        e.accept()
     
    def mouseReleaseEvent(self, e):
        self.moveThis(e)
        e.accept()       
      
    def moveThis(self, e):
        dif = e.globalPosition() - self.save      
        self.move(self.pos() + QPoint(int(dif.x()), int(dif.y())))
        self.save = e.globalPosition()

    def mouseDoubleClickEvent(self, e): 
        if self.fileName != '':  
            self.shared.msgbox(self.fileName + '\n' + 'aspect: ' + str(self.aspect))
        e.accept()
   
    def closeEvent(self, e):
        self.bye()
        e.accept()

### --------------------------------------------------------
    def setFileName(self, fileName):  
        if self.clips.AutoAspect == True and self.clips.MakeClips == False:
            if not self.shared.setAspectRatio(fileName): ## else skip it and open without
                return 
        if self.mediaPlayer.setFileName(fileName) == False:   ## <- "one"
            self.shared.msgbox('error setting mediaPlayer')
            return
        self.playButton.setEnabled(True)      
        self.path = fileName[0:fileName.rfind('/')]  ## next time you search 
        self.fileName = fileName  
        return True   

    def setDisplaySize(self, key):
        self.flag = True
        hgt = HGT if self.sliderVisible == True else HGT-PAD  
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

    def setAspButton(self):  ## from aspect button   ## <- "one"
        if self.aspect == 0:
            v = self.videoWidget.size()  
            self.aspect = math.floor(v.width()/v.height() * 100)/100.0          
            if key := self.shared.returnKey(self.aspect): 
                self.clips.setDefaultSizes(key)  ## gets default sizes
            else:
                key = 'O'     
            self.setDisplaySize(key)  
        else:
            self.aspect = 0
            self.aspButton.setText("Set Aspect")
                                                                  
### --------------------------------------------------------   
    def resizeEvent(self, e):
        if self.flag == True:
            self.flag = False
            return 
        elif self.aspect > 0:    
  
            hgt = HGT if self.sliderVisible == True else HGT-PAD
            
            width  = int((self.height()-hgt) * self.aspect)+WID
            height = int((self.width()-WID)/ self.aspect)+hgt  
            maxwid = int((MaxHgt-hgt) * self.aspect)+WID 
            which  = getDirection(self)     
            
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
    def setMediaPlayer(self, x=''):  ## set in videoPlayerTwo
        pass
    
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



