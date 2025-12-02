
import os
import sys
import time
import math  
import subprocess

### ------------------ videoPlayerOne.py ------------------- 
''' Source for setting formats, buttons, resizing this widget and
    mediaPlayer, and playing video. Running the python script-qt6.py will 
    remove all the qt5 and pyside code and comments, there are scripts 
    for qt5 and pyside as well.
    OpenCV is required, the very latest version - 4.12.0, to create video 
    clips and can also be used to detect and set the videos aspect ratio. 
    Go to getMetaData to enable one of the three code options, 
    the other two can be found tacked onto videoClipsWidget. 
    The keys '[', ']'  can scale up or scale down videoPlayerOne,  
    and a right-mouse click displays the help menu.  
    See videoClipsMaker for changes to defaults and clipsWidget for settings. '''
### -------------------------------------------------------- 

from PyQt6.QtCore       import Qt, QUrl, QPoint, QRect, QSizeF
from PyQt6.QtGui        import QGuiApplication, QCursor
from PyQt6.QtWidgets    import QWidget, QSlider, QHBoxLayout, QVBoxLayout,  \
                                QLabel, QPushButton, QFrame, QApplication, \
                                QSizePolicy
                                    
from PyQt6.QtMultimedia         import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets  import QVideoWidget

# from PyQt6.QtMultimedia           import QMediaContent  ## 5

from videoClipsMaker     import Clips, Ext
from videoClipsWidget    import *

ViewW,  ViewH  =  790,  525   ## starting video size
MaxWid, MaxHgt = 1800, 1065   ## maximum width/height

MinWid = 300  ## minimum widget width
MinHgt = 400  ## minimum widget height
                  
VertW = 525  ## minimum vertical width on open
VertH = 100  ## vertical starting height
HorzH = 200

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
       
        self.mediaPlayer.positionChanged.connect(self.videoPlayer.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.videoPlayer.durationChanged)
             
        self.audioOut = QAudioOutput()  ## 6
        self.mediaPlayer.setAudioOutput(self.audioOut)  ## 6
  
        self.mediaPlayer.setLoops(-1)
        
### -----------------------------------------------------------------
    def setFileName(self, fileName):
        try:
            self.mediaPlayer.setSource((QUrl.fromLocalFile(fileName)))  ## 6
            # self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(fileName))))  ## 5  
        except:
            return False
        self.mediaPlayer.pause() 
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
            time.sleep(.05)
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
        
        self.mediaPlayer = MediaPlayer(self)
        self.videoWidget = self.mediaPlayer.videoWidget
                
        self.init()   
        self.clips = Clips(self) 
        
        self.sliderVisible = True
                
        if len(sys.argv) > 1: 
            self.path = sys.argv[1]
         
        vbox = QVBoxLayout() 
        
        vbox.addWidget(self.videoWidget)
        vbox.addWidget(self.setButtons())
        if self.sliderVisible == True:
            vbox.addWidget(self.setSlider())
         
        self.setLayout(vbox)            
   
        self.openPlayer(self.key)   ## <<----->> open full frame - 3:2]  
         
        x = QGuiApplication.primaryScreen().availableGeometry().center().x()
        self.move(x-int((ViewW+WID)/2), HorzH)  
  
        self.setAcceptDrops(True)  
        self.grabKeyboard() 
            
        self.show()
          
### --------------------------------------------------------        
    def init(self):
        self.key = 'F'   ## <<----->> open full frame - 3:2]
        self.path = ''
        self.lastKey = '' 
        self.fileName = ''
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
            self.mediaPlayer.pause() 
            if self.clips.PlayVideo: self.playVideo()  ## PlayVideo set in clipsMaker
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
            self.clips.toggleSlider()
                          
        elif key == Qt.Key.Key_BracketRight or mod & Qt.KeyboardModifier.ShiftModifier \
            and key in (Qt.Key.Key_Greater, Qt.Key.Key_Plus):
                self.clips.zoom(1.05) 
                             
        elif key == Qt.Key.Key_BracketLeft or mod & Qt.KeyboardModifier.ShiftModifier \
            and key in (Qt.Key.Key_Less, Qt.Key.Key_Underscore):
                self.clips.zoom(.95)  
                
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
            self.openPlayer(key)     
        else: 
            match key:
                case 'L':
                    self.clips.looper()  
                case ']':
                    self.clips.zoom(1.05)  
                case '[':    
                    self.clips.zoom(0.95)      
                case 'Aspect':
                    self.setAspButton()  ## set aspect ratio manually clicking on aspect button
                case 'Settings':
                    self.clips.toggleSettings(self)  ## clipMaker settings
                case 'C':
                    self.closeHelpMenu()  ## improvised clear
                    self.mediaPlayer.stop()        
                case 'Clips':   
                    self.clips.openDirectory()  ## if MakeClipsOn sets path to folder
                case 'Shift-S':
                    self.clips.toggleSlider()
                case 'X' | 'Q':
                    self.bye()   
                case _:
                    return
           
### --------------------------------------------------------                                                                              
    def mousePressEvent(self, e):  ## takes two fingers on my mac and a double-click
        self.save = e.globalPosition()  
        if e.button() == Qt.MouseButton.RightButton:
            if self.clips.settings == None:
                self.closeHelpMenu() if self.helpFlag == True \
                    else self.openHelpMenu() 
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
            self.clips.msgbox(self.fileName + '\n' + 'aspect: ' + str(self.aspect))
        e.accept()
   
    def closeEvent(self, e):
        self.bye()
        e.accept()

### --------------------------------------------------------
    def openPlayer(self, key):  ## set by 'key' - default on open  - from keyboard or help menu       
        self.closeHelpMenu()    
        if key in AspKeys:
            self.clips.setFormat(key)
            self.setDisplaySize(key)
        else:
            self.clips.msgbox('Unknown key entered')
            return
        
    def setAutoAspectRatio(self, fileName):  ## if AutoAspect True read video metadata to set aspect ratio 
        if fileName == '':
            return 
        ext = fileName[fileName.rfind('.'):].lower()
        if ext in Ext:  ## photo not video
            return
        
        width, height = 0, 0
        try:
            width, height = self.getMetaData(fileName) 
        except:   
            None                   
        if width > 0 and height > 0: 
            self.aspect = math.floor((width/height) * 100)/100.0    
            if key := self.clips.returnKey(self.aspect): 
                self.clips.setFormat(key)  ## gets default sizes
            else:
                key = 'O'     
            self.setDisplaySize(key)  
        else:
            self.clips.msgbox("setAspectRatio: error reading getMetaData")
            return
   
    def setDisplaySize(self, key):
        self.lastKey = key
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
        time.sleep(.05)
        self.moveAndSet()
        
    def moveAndSet(self):
        x = QGuiApplication.primaryScreen().availableGeometry().center().x()
        y = VertH if self.aspect < 1.0 else HorzH
        self.move(x - int(self.width()/2), y)            
        self.saveW, self.saveH = self.width(), self.height()   
          
### --------------------------------------------------------
    def setAspButton(self):  ## from aspect button
        if self.aspect == 0:
            v = self.videoWidget.size()  ## uses the current video widget size 
            self.aspect = math.floor(v.width()/v.height() * 100)/100.0          
            if key := self.clips.returnKey(self.aspect): 
                self.clips.setFormat(key)  ## gets default sizes
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
            which  = self.getDirection()     
            
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
    
    def getDirection(self):
        corner, which = 5, ''
        pos = self.mapFromGlobal(QCursor.pos())
        
        bottomLeft  = self.rect().bottomLeft()
        bottomRight = self.rect().bottomRight()
        
        if QRect(QPoint(bottomLeft.x()-(1*corner), bottomLeft.y()-(3*corner)),
            QPoint(bottomLeft.x()+(3*corner), bottomLeft.y()+(1*corner))).contains(pos):
            which = 'botleft'
            
        elif QRect(QPoint(bottomRight.x()-(3*corner), bottomRight.y()-(3*corner)),
            QPoint(bottomRight.x()+(1*corner), bottomRight.y()+(1*corner))).contains(pos):
            which = 'botright'
            
        elif QRect(QPoint( bottomLeft.x()-(2*corner), bottomLeft.y()-(3*corner)),
            QPoint(bottomRight.x()+(2*corner), bottomRight.y()+(1*corner))).contains(pos):
            which = 'bottom'
            
        return which
                                           
### --------------------------------------------------------
    def openHelpMenu(self):
        if self.helpFlag == True:
            self.closeHelpMenu()
        else:
            self.helpMenu = Help(self)
            self.helpFlag = True
            
    def closeHelpMenu(self):
        if self.helpMenu != None: 
            self.helpMenu.tableClose()
            self.helpMenu.close()
            self.helpFlag = False
            time.sleep(.05)
                                                        
### --------------------------------------------------------                                                               
    def setFileName(self, fileName):       
        if self.clips.AutoAspect == True and self.clips.MakeClips == False:
            self.setAutoAspectRatio(fileName)  ## else skip it and open without
          
        if self.mediaPlayer.setFileName(fileName) == False:
            self.msgbox('error setting mediaPlayer')
            return
        
        self.playButton.setEnabled(True)      
        self.path = fileName[0:fileName.rfind('/')]  ## next time you search 
         
        self.fileName = fileName  
        return True
    
    def playVideo(self):
        if self.mediaPlayer != None:
            self.mediaPlayer.playVideo()
            
    def stopVideo(self):
        if self.mediaPlayer != None:
            self.mediaPlayer.stopVideo()
            time.sleep(.05)
             
    def setPosition(self, position):  ## called by slider if finger pull
        if self.mediaPlayer != None:
            self.mediaPlayer.setPosition(position)
            
    def positionChanged(self, position):  
        if self.sliderVisible == True:  
            self.slider.setValue(position)  
            
    def durationChanged(self, duration):
        if self.sliderVisible == True: 
            self.slider.setRange(0, duration)      
 
    def bye(self):
        self.closeHelpMenu()
        self.clips.closeSettings()
        self.close()
   
### -------------------------------------------------------- 
    def getMetaData(self, path):  ## to detect and set the aspect ratio  
        ''' requires opencv-python - may not always report width/height correctly 
            for non 9:16 verticals - initial method - not mac specific '''
        # try:  
        #     import cv2  ## <<---------------------  
        #     try:
        #         cap = cv2.VideoCapture(path) 
        #     except:
        #         return 0,0
        #     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        #     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        #     cap.release()
        #     return width, height
        # except:
        #     return 0, 0

        ''' uses mdls - mac only - reports non 9:16 vertical width and height correctly -- 
        drag and drop doesn't work in pyqt5 on desktop '''   
        # try:  
        #     result = subprocess.run(
        #         ['mdls', '-name', 'kMDItemPixelWidth', '-name', 'kMDItemPixelHeight', path],
        #         capture_output=True,
        #         text=True,
        #         check=True
        #         )
        #     output = result.stdout
        #     width, height = None, None
        #     for line in output.splitlines():
        #         if 'kMDItemPixelWidth' in line:
        #             width = int(line.split('=')[-1].strip())
        #         elif 'kMDItemPixelHeight' in line:
        #             height = int(line.split('=')[-1].strip())
        #         del line
        #     return width, height
        # except Exception:
        #     return 0, 0 
                                
### -------------------------------------------------------- 
    def setSlider(self):
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.setPosition)
        self.slider.setFixedHeight(30)
        
        self.slider.setStyleSheet("""                                        
            QSlider::groove:horizontal {
                background-color: #ccc;
                height: 3px;
            }     
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e4e4e4, stop:1 #4f4f4f);
                border: 1px solid rgb(105,105,105);
                width: 11px;
                margin: -7px 0;
                border-radius: 3px;
            }
        """)

        return self.slider
    
### --------------------------------------------------------   
    def setButtons(self):     
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedHeight(45)
  
        self.openButton  = QPushButton("Files")
        self.playButton  = QPushButton("Play")
        self.aspButton   = QPushButton("Aspect")
        
        self.loopButton  = QPushButton("Loop") 
        if self.loopSet == True:
            self.loopButton  = QPushButton("LoopOn") 
        
        self.stopButton  = QPushButton("Stop")
        self.byeButton   = QPushButton("Quit")  
        
        self.openButton.clicked.connect(self.clips.openFile)
        self.playButton.clicked.connect(self.playVideo)
        self.aspButton.clicked.connect(self.setAspButton)
        self.loopButton.clicked.connect(self.clips.looper)
        self.stopButton.clicked.connect(self.stopVideo)
        self.byeButton.clicked.connect(self.bye)

        hbox = QHBoxLayout()
        
        hbox.addWidget(self.openButton)  
        hbox.addWidget(self.playButton)
        hbox.addWidget(self.aspButton)
        hbox.addWidget(self.loopButton)
        hbox.addWidget(self.stopButton)
        hbox.addWidget(self.byeButton)
 
        self.buttonGroup.setLayout(hbox)
        self.buttonGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
        self.buttonGroup.setLineWidth(1)
    
        hbox = QHBoxLayout()
        hbox.addWidget(self.buttonGroup)
        
        self.bGroup = QLabel()
        self.buttonGroup.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.bGroup.setFixedHeight(60)
        self.bGroup.setLayout(hbox)
      
        return self.bGroup
                                 
### --------------------------------------------------------  
if __name__ == '__main__':
    app = QApplication(sys.argv)
    play = VideoPlayer()
    sys.exit(app.exec())
    
### ---------------------- that's all ----------------------



