
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
    Go to getVideoWidthHeight to enable one of the three code options, 
    the other two can be found tacked onto videoClipsWidget. 
    The keys '>,  +,  ]' and '<,  _,  [' are used to scale up or scale 
    down videoPlayerOne and a right-mouse click displays the help menu. 
    See videoClipsMaker for changes to defaults and videowidget settings. '''
### -------------------------------------------------------- 

from PyQt6.QtCore       import Qt, QUrl, QTimer
from PyQt6.QtGui        import QGuiApplication
from PyQt6.QtWidgets    import QWidget, QSlider, QHBoxLayout, QVBoxLayout,  \
                                QLabel, QPushButton, QFrame, QApplication, \
                                QSizePolicy
                                    
from PyQt6.QtMultimedia         import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets  import QVideoWidget

VHgt = 150  ## starting 'y' in move for verticals

### ------------ comment out for 6, uncomment for 5 -----------------  ## del
# from PyQt6.QtMultimedia   import QMediaContent  ## 5
### ---------------------------- end --------------------------------

from videoClipsMaker     import Clips
from videoClipsWidget    import *
                    
### --------------------------------------------------------
class VideoPlayer(QWidget):
### --------------------------------------------------------
    def __init__(self):
        super(VideoPlayer, self).__init__()    
        self.setWindowTitle("VideoPlayer")
          
### ------------ comment out for 5, uncomment for 6 ----------------- ## del
        self.mediaPlayer = QMediaPlayer()  ## 6
        # self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)  ## 5
### ---------------------------- end --------------------------------  

        self.videoWidget = QVideoWidget()
        self.mediaPlayer.setVideoOutput(self.videoWidget)
                   
### ------------ comment out for 5, uncomment for 6 ----------------- ## del
        self.audioOut = QAudioOutput()   ## 6      
        self.mediaPlayer.setAudioOutput(self.audioOut)   ## 6   
        self.mediaPlayer.mediaStatusChanged[QMediaPlayer.MediaStatus].connect(self.mediaStateChanged) ## 6    
        ## del
### ------------ uncomment for 5 ... comment out for 6 ----------------- ## del
        # self.mediaPlayer.mediaStatusChanged[QMediaPlayer.MediaStatus].connect(self.mediaStatusChanged)  ## 5
### ---------------------------- end --------------------------------
 
        self.mediaPlayer.durationChanged.connect(self.durationChanged) 
        self.mediaPlayer.positionChanged.connect(self.positionChanged)   
         
        self.timer = QTimer(self)  
        self.timer.timeout.connect(self.resizeFinished)
        self.timer_interval = 5000   
           
        self.init()
        self.clips = Clips(self) 
        
        if len(sys.argv) > 1: 
            self.path = sys.argv[1]
              
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.setPosition)
        
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
   
        vbox = QVBoxLayout() 

        vbox.addWidget(self.videoWidget)
        vbox.addWidget(self.setButtons())
        vbox.addWidget(self.slider)
        self.setLayout(vbox)  
                                             
        self.openPlayer(self.key)   ## <<----->> open full frame - 3:2]  
        
        self.setAcceptDrops(True)  
        self.grabKeyboard() 
    
        self.show()
          
### --------------------------------------------------------        
    def init(self):
        self.key = 'F'
        self.path = ''
        self.lastKey = '' 
        self.fileName = ''
        self.aspect = 0.0
        self.OtherAsp = 0.0
        self.lastVWidth = 0
        self.lastHeight = 0 
        self.loop = False
        self.helpFlag = False 
        self.helpMenu = None
    
    def keyPressEvent(self, e):
        key = e.key()
        mod = e.modifiers()   
         
        if key == Qt.Key.Key_Escape:
            self.bye()    
                 
        if key == Qt.Key.Key_Space:  ## spacebar to pause/resume
            self.playVideo()   
                          
        elif key == Qt.Key.Key_BracketRight or mod & Qt.KeyboardModifier.ShiftModifier \
            and key in (Qt.Key.Key_Greater, Qt.Key.Key_Plus):
                self.clips.zoom(1.05) 
                             
        elif key == Qt.Key.Key_BracketLeft or mod & Qt.KeyboardModifier.ShiftModifier \
            and key in (Qt.Key.Key_Less, Qt.Key.Key_Underscore):
                self.clips.zoom(.95)  
        else:
            try:
                key = chr(e.key())
            except:
                return  
        if key in SharedKeys:
            self.sharedKeys(key)
  
    def sharedKeys(self,key):  
        if key in AspKeys:
            self.openPlayer(key) if key != self.lastKey else \
                self.resizeAndMove(key)    
        else: 
            match key:
                case 'L':
                    self.clips.looper()  ## doesn't run in qt5 - not supported
                case 'W':
                    self.clips.toggleVideoWidget(self)  ## clipMaker settings
                case ']':
                    self.clips.zoom(1.05)  
                case '[':    
                    self.clips.zoom(0.95)      
                case 'B':
                    self.setAspButton()  ## set aspect ratio manually clicking on aspect button
                case 'C':
                    self.closeHelpMenu()  ## improvised clear
                    self.mediaPlayer.stop()        
                case 'D':   
                    self.clips.openDirectory()  ## if MakeClips True sets path to folder
                case 'X' | 'Q':
                    self.bye()   
           
 ### --------------------------------------------------------
    def mousePressEvent(self, e):  ## takes two fingers on a mac and a double-click
        if e.button() == Qt.MouseButton.RightButton:
            if self.clips.videowidget == None:
                self.closeHelpMenu() if self.helpFlag == True \
                    else self.openHelpMenu()
            e.accept()
                                                                               
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
    def openPlayer(self, key):  ## set by 'key' - default on open  - from keyboard or help menu       
        self.closeHelpMenu()
        ctr = QGuiApplication.primaryScreen().availableGeometry().center()
        x, y = ctr.x(), ctr.y()           
        self.clips.setFormat(key)
        if key in AspKeys:
            self.resize(self.ViewW+WID, self.ViewH+ HGT)
            self.lastHeight = self.ViewH
            if key not in ('T','U','V'):
                self.move(x-int(self.ViewW/2), int(y-450))  
            else:
                self.move(x-int(self.ViewW/2), VHgt)           
        self.lastKey = self.key
        self.aspButton.setText("Aspect: " + self.lastKey)
        
    def setAspectRatio(self, fileName=''):  ## if AutoAspect True read video metadata and set aspect ratio 
        if fileName == '': return 
        err, asp, width, height = False, 0, 0, 0
        try:
            width, height = self.getVideoWidthHeight(self.path + '/' + os.path.basename(fileName)) 
        except:   
            err = True              
        if err == False and width > 0 and height > 0: 
            asp = math.floor((width/height) * 100)/100.0  ## passed - set it
            self.selectIt(asp, width, height)
        else:
            self.clips.msgbox("setAspectRatio: error reading metadata in getVideoWidthHeight")
        
    def selectIt(self, asp, width, height):  ## set aspect if match else set 'O' for other
        if key := self.clips.returnKey(asp): 
            self.clips.setFormat(key)
            if self.lastKey == '': 
                self.lastKey = key  
            self.resizeAndMove(key)   
        else:
            self.setOtherAsp(asp, width, height)
   
    def setOtherAsp(self, asp, width, height):  ## set OtherAsp if asp < 1.0 and no match in 'T','U','V'
        self.aspect = asp  
        self.OtherAsp = 0
        if asp < 1.0:  ## verticals - set the self.OtherAsp
            if self.lastVWidth == 0:  
                self.lastVWidth = Chars['V'][1]
            self.OtherAsp = math.floor((height/width) * 100)/100.0 
        self.resizeAndMove('O')
                         
    def setAspButton(self):  ## from aspect button
        v = self.videoWidget.size()  ## uses the current video widget size 
        self.aspect = math.floor(v.width()/v.height() * 100)/100.0   
        self.resizeAndMove('O')  ## becomes shared.lastKey 
  
  ### -------------------------------------------------------- 
    def getVideoWidthHeight(self, path):  ## to detect and set the aspect ratio
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
    def resizeAndMove(self, key): 
        pos = self.pos();  py = pos.y()
        oldWidth = self.width()    
        if key == 'O' and self.OtherAsp > 0 and self.aspect < 1.0:
            dif = self.resizeOtherVerticals()
            py = VHgt
        elif key in ('T','U','V'):
            self.resize(self.ViewW+WID, self.ViewH+ HGT)   
            dif = int((self.width() - oldWidth)/2)
            py = VHgt  ## to keep it constant
        else:
            dif = self.newWidths(key, oldWidth)  ##  resizes here as well        
        self.move(pos.x()-dif, py)     
        self.lastKey = key  
        self.clips.toggleAspectBtn()
        self.aspButton.setText("Aspect: " + self.lastKey)
        
    def newWidths(self, key, oldWidth):  ## uses height * asp
        if key in AspKeys:
            asp = self.aspect  
        elif self.aspect > 0:
            asp = self.aspect
        else:
            self.clips.msgbox('The Aspect Ratio has not been Set')
            return  
        if self.lastKey in ('T','U','V'):     
            height = self.lastHeight  
        else:
            height = self.height()    
        self.lastHeight = height             
        return self.resizeNewWidths(asp, height, oldWidth)
     
    def resizeNewWidths(self, asp, height, oldWidth):  
        newWidth = int(asp * (height - HGT)) + WID 
        self.resize(newWidth, height)                
        return int((newWidth - oldWidth )/2)  ## to center qwidget
                                                              
    def resizeOtherVerticals(self):  ## not 9:16
        width = self.lastVWidth  ## width not changed
        self.ViewW, self.ViewH = width, int(self.OtherAsp * width)
        self.resize(self.ViewW+WID, self.ViewH+ HGT)
        return 0  ## width doesn't change
                             
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
                                     
    def resizeEvent(self, e):
        self.clips.toggleAspectBtn()
        self.timer.start(self.timer_interval)  
        super().resizeEvent(e)
           
    def resizeFinished(self): 
        self.timer.stop() ## and return if nothing has changed
        if self.ViewW == self.width()-WID and self.ViewH == self.height()-HGT or\
            self.fileName == '':
            return
        self.clips.zoom(1.00) 
                                          
### --------------------------------------------------------                                                               
    def setFileName(self, fileName):       
        if self.clips.AutoAspect == True and self.clips.MakeClips == False:
            self.setAspectRatio(fileName)  
           
### ------------ uncomment for 6 ... comment out for 5 -----------------     ## del
        self.mediaPlayer.setSource((QUrl.fromLocalFile(fileName)))  ## 6  ## source doesn't change even if self.fileName gets truncated
        # self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))  ## 5      
### ---------------------------- end ----------------------------------- 

        self.playButton.setEnabled(True)   
        self.fileName = ''
        self.path = fileName[0:fileName.rfind('/')]  ## so it knows where to start looking next time you search
        if fileName != self.fileName and len(fileName) <= 24:  ## if greater than 24 chars or self.fileName "" 
            self.fileName = fileName 
        else:
            self.fileName = self.clips.pathMod(fileName)  ## it's for display]
        self.setWindowTitle(self.fileName) 
        return True

### ------------ uncomment for 6 ... comment out for 5 -----------------         ## del     
    def playVideo(self):  ## 6
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:  ## 6
            self.mediaPlayer.pause()  ## 6
            self.playButton.setText('Resume')  ## 6 
        elif self.fileName != '':   ## 6
            self.mediaPlayer.play()   ## 6
            self.playButton.setText('Pause')  ## 6
        
    def mediaStateChanged(self, state): ## 6
        if state == QMediaPlayer.MediaStatus.EndOfMedia: ## 6
            while not (self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.StoppedState): ## 6
                time.sleep(.05) ## 6
            self.stopVideo()   ## 6    
   ## del
### ------------ uncomment for 5 ... comment out for 6 -----------------  ## del
    # def playVideo(self):   ## 5
    #     if self.mediaPlayer.state() == QMediaPlayer.PlayingState:  ## 5
    #         self.mediaPlayer.pause()   ## 5
    #         self.playButton.setText('Resume')   ## 5
    #     elif self.fileName != '':   ## 5
    #         self.mediaPlayer.play()  ## 5
    #         self.playButton.setText('Pause')  ## 5
    ## del
    # def mediaStatusChanged(self, status):   ## 5
    #     if status == QMediaPlayer.MediaStatus.EndOfMedia:   ## 5
    #         while not (self.mediaPlayer.state() == QMediaPlayer.StoppedState):   ## 5
    #             time.sleep(.05)   ## 5
    #         self.stopVideo()   ## 5
 ### ---------------------------- end -----------------------------------  ## del
    def stopVideo(self):
        if self.loop == False: self.mediaPlayer.stop()
        self.playButton.setText('Play')
        self.setPosition(0)  ## shows first frame plus pause
        self.playVideo() if self.loop == True else self.mediaPlayer.pause() 
  
    def positionChanged(self, position):
        self.slider.setValue(position)

    def durationChanged(self, duration):
        self.slider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)
       
    def bye(self):
        self.clips.closeWidget()
        self.closeHelpMenu()
        self.close()
        
### --------------------------------------------------------          
    def setButtons(self):     
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedHeight(45)
  
        self.openButton  = QPushButton("Files")
        self.playButton  = QPushButton("Play")
        self.aspButton   = QPushButton("Aspect")
        
        self.loopButton  = QPushButton("Loop") 
        if self.loop == True:
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




