

import os
import time
import math  
import subprocess

from PyQt6.QtCore       import Qt, QTimer, QPoint, QRect, QSizeF, QUrl
from PyQt6.QtGui        import QGuiApplication, QCursor
from PyQt6.QtWidgets    import QSlider, QHBoxLayout, QLabel, QFrame, \
                                QPushButton, QSizePolicy, QMessageBox

from PyQt6.QtMultimedia         import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets  import QVideoWidget, QGraphicsVideoItem

# from PyQt6.QtMultimedia           import QMediaContent  ## 5

from videoClipsWidget   import *
from videoClipsMaker    import Ext  
from videoPlayerHelp    import VideoHelp, SlideShowHelp, VideoHelpWidget

WID, HGT, PAD = 40, 140, 100 ## pixels added to videowidget size when resizing videoPlayerOne's width and height

### -------------------------------------------------------- 
''' The function getMetaData and code shared by both videoPlayers 
    and some singletons relocated here to help reduce file sizes 
    and make files less packed and easier to read. I've added a 
    visual aid to point out files or code specific to videoPlayer 
    one or two... ## <- "one", ## <- "two". Easy to search for. '''
### --------------------------------------------------------   
class MediaPlayer(QMediaPlayer): 
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
        
        self.parent = parent
        self.shared = parent.shared
    
        self.mediaPlayer = QMediaPlayer(self) ## 6
        # self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)  ## 5 
            
        if self.parent.player == "one":
            self.videoWidget = QVideoWidget()   
            self.mediaPlayer.setVideoOutput(self.videoWidget) 
            self.videoWidget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
            
        elif self.parent.player == "two":
            self.videoItem = QGraphicsVideoItem()   
            self.mediaPlayer.setVideoOutput(self.videoItem)  
            self.videoItem.setZValue(100)
            self.videoItem.setSize(QSizeF(float(ViewH*1.5), float(ViewH)))  
            self.videoItem.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
            
        self.mediaPlayer.mediaStatusChanged[QMediaPlayer.MediaStatus].connect(self.mediaStateChanged) 
       
        if self.shared.sliderVisible:  ## you'll need to load a file to kickstart the slider if it won't move
            self.mediaPlayer.positionChanged.connect(self.parent.shared.positionChanged)
            self.mediaPlayer.durationChanged.connect(self.parent.shared.durationChanged)
             
        self.audioOut = QAudioOutput()  ## 6
        self.mediaPlayer.setAudioOutput(self.audioOut)  ## 6
  
        if self.parent.player == "one":  ## 6
            self.mediaPlayer.setLoops(-1)  ## 6
        
### -----------------------------------------------------------------
    def setFileName(self, fileName): 
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
            self.parent.playButton.setText('Resume') 
        elif self.parent.fileName != '':  
            self.mediaPlayer.play()  
            self.parent.playButton.setText('Pause') 
     
    def mediaStateChanged(self, status): 
        if status == QMediaPlayer.MediaStatus.EndOfMedia:  
            while not (self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.StoppedState):   ## 6
            # while not (self.mediaPlayer.state() == QMediaPlayer.State.StoppedState):  ## 5
                time.sleep(.005) 
            self.stopVideo() 

    def stopVideo(self):  
        if not self.shared.loopSet: 
            self.mediaPlayer.stop()
            self.setPosition(0) 
            self.mediaPlayer.pause() 
            self.parent.playButton.setText('Play')
            time.sleep(.03)
        else:   
            self.playVideo()  ## loop it

    def setPosition(self, position):  ## from videoPlayer by finger pull
        self.mediaPlayer.setPosition(position)

### --------------------------------------------------------     
class Shared:  
### -------------------------------------------------------- 
    def __init__(self, parent): 
        super().__init__()  
        
        self.parent = parent
        self.player = 'shared'
        
        self.helpMenus = False
        self.videoPlaying = False
        self.loopSet = False
        
        self.frameVisible = True
        self.sliderVisible = True 
      
### --------------------------------------------------------
    def openPlayer(self, key):  ## from keyboard or helpMenu - default on open     
        self.closeHelpMenu()    
        if key == 'S' and self.videoPlaying:
            self.stopVideo()  ## next 'S' is the square format 
            return   
        if self.parent.player == "two": 
            self.parent.closeMediaPlayer()  
        try:  
            self.parent.clips.setDefaultSizes(key)  ## sets self.aspect
            self.setScreenFormat()  ## just resize it
        except:
            self.msgbox('Unknown key entered')
            return

    def setAspectRatio(self, fileName):
        ext = fileName[fileName.rfind('.'):].lower()   
        if ext in Ext or fileName == '':  ## photo - not a video
            self.msgbox('error setting fileName')
            return False
        key, width, height = '', 0, 0
        try: 
            width, height = getMetaData(fileName)  ## it's here
        except:   
            None    
        if width > 0 and height > 0: 
            self.parent.aspect = math.floor((width/height) * 100)/100.0    
            if key := self.returnKey(self.parent.aspect): 
                self.parent.clips.setDefaultSizes(key) 
            else:
                key = 'O'   
            self.parent.setDisplaySize(key) 
            return True
        else:
            self.msgbox("setAspectRatio: error reading getMetaData")
            return False  
    
    def setFileNameInMediaPlayer(self, fileName):
        if not self.parent.mediaPlayer.setFileName(fileName): 
            self.msgbox('error setting mediaPlayer')
            return False  
        return True 
        
    def setAutoAspect(self, fileName):
        if self.parent.clips.AutoAspect and not self.parent.clips.MakeClips:
            if not self.setAspectRatio(fileName): ## skip it and open without
                return
        return  ## hasn't been updated
    
    def moveAndSet(self):
        x = QGuiApplication.primaryScreen().availableGeometry().center().x()
        y = VertH if self.parent.aspect < 1.0 else HorzH
        self.parent.move(x - int(self.parent.width()/2), y)            
        self.parent.saveW, self.parent.saveH = self.parent.width(), self.parent.height()         
        if self.parent.player == 'two' and self.parent.videoItem != None:  ## <- "two"
            self.parent.videoWidth = int(self.parent.videoItem.size().width())
  
    ## if 'O', ctr on background requires more than just the video size
    def setVideoWH(self):  ## from setDisplaySize
        hgt = HGT if self.sliderVisible else HGT-PAD   
        self.parent.VideoH = int((self.parent.height()-hgt) * 1.20)
        self.parent.VideoW = int(self.parent.VideoH * self.parent.aspect)
  
    def setScreenFormat(self):  ## just resize it - single key format
        self.parent.flag = True
        hgt = HGT if self.sliderVisible else HGT-PAD  
        self.parent.resize(self.parent.ViewW+WID, self.parent.ViewH+hgt) 
        self.moveAndSet()  
                     
  ### --------------------------------------------------------          
    def looper(self): 
        if not self.loopSet:
            self.loopSet = True
            self.parent.loopButton.setText('LoopOn')
            self.parent.stopButton.setEnabled(False)
            time.sleep(.03)   
        elif self.loopSet:
            self.looperOff()
            if self.parent.mediaPlayer != None:
                self.parent.shared.stopVideo()
            time.sleep(.03)
 
    def looperOff(self):
        self.loopSet = False
        self.parent.loopButton.setText('Loop')
        self.parent.stopButton.setEnabled(True)
                   
### --------------------------------------------------------
    def openHelpMenu(self):
        if self.parent.helpFlag:
            self.closeHelpMenu()
        else:
            self.parent.helpMenu = VideoHelp(self.parent)
            self.parent.helpFlag = True
            time.sleep(.03)
 
    def closeHelpMenu(self):
        if self.parent.helpMenu != None: 
            self.parent.helpMenu.tableClose()
            self.parent.helpMenu.close()
            self.parent.helpFlag = False
            time.sleep(.03)
            if self.helpMenus:
                self.closeVideoSlideMenus()
         
    def videoSliderMenus(self):  ## from videoplayerhelp
        self.helpMenus = True
        self.vwidget   = VideoHelpWidget(self.parent)
        self.settings  = Settings(self.parent, 'aaa', 10)
        self.videohelp = VideoHelp(self.parent, -415, 'aaa')
        self.slidehelp = SlideShowHelp(self.parent, 428, 'aaa')
    
    def closeVideoSlideMenus(self):
        if self.helpMenus:    
            self.settings.close()
            time.sleep(.03)
            self.videohelp.table.close()
            self.slidehelp.table.close()
            self.vwidget.close() 
            self.helpMenus = False
   
### --------------------------------------------------------     
    def playVideo(self):  ## setButtons and setSlider don't know about mediaPlayer
        if self.parent.mediaPlayer != None:
            self.parent.mediaPlayer.playVideo()
            self.videoPlaying = True
      
    def stopVideo(self):  
        if self.parent.mediaPlayer != None:
            if self.loopSet:
                self.looperOff()
            self.parent.mediaPlayer.stopVideo()
            time.sleep(.03)
            self.videoPlaying = False
            
    def setPosition(self, position):  ## called by slider if finger pull
        if self.parent.mediaPlayer != None:
            self.parent.mediaPlayer.setPosition(position)
    
    def positionChanged(self, position):  
        if self.sliderVisible:  
            self.parent.slider.setValue(position)     
            
    def durationChanged(self, duration):
        if self.sliderVisible: 
            self.parent.slider.setRange(0, duration)  
  
### --------------------------------------------------------
    def msgbox(self, str):
        msg = QMessageBox()
        msg.setText(str)
        timer = QTimer(msg)
        timer.setSingleShot(True)
        timer.setInterval(7000)
        timer.timeout.connect(msg.close)
        timer.start()
        msg.exec() 
        
    def returnKey(self, asp): 
        for k, v in Keys.items():
            if asp == v[0]: 
                return k
            elif asp - .01 == v[0] or asp + .01 == v[0]:
                return k
        return None
   
    def toggleSlider(self):  ## now all
        self.parent.flag = True
        self.toggleFrameless()
        if self.sliderVisible and self.parent.height() > MinHgt+PAD: 
            self.sliderVisible = False  
            self.parent.slider.hide()
            self.parent.buttons.hide()
            self.parent.resize(self.parent.width(), self.parent.height()-PAD)
            time.sleep(.03)      
        elif not self.sliderVisible:
            self.parent.slider.show()
            self.parent.buttons.show()
            self.sliderVisible = True
            self.parent.resize(self.parent.width(), self.parent.height()+PAD)
            time.sleep(.03) 

    def toggleFrameless(self):  ## from toggleSlider
        p = self.parent.pos()
        if not self.frameVisible:  ## make it visible 
            self.parent.setWindowFlags(self.parent.windowFlags() & ~Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
            self.frameVisible = True
            self.parent.move(p.x(), p.y()-28) 
        else:
            self.parent.setWindowFlags(self.parent.windowFlags() | Qt.WindowType.FramelessWindowHint)
            self.frameVisible = False
            self.parent.move(p.x(), p.y()+28)  ## keep the frame stationary
        self.closeHelpMenu()
        self.parent.show()
        
### -------------------------------------------------------           
    def getDirection(self):  ## left out top, topleft and topright - feel free to add them
        corner, which = 6, ''      
        pos = self.parent.mapFromGlobal(QCursor.pos())
        
        bottomLeft  = self.parent.rect().bottomLeft()
        bottomRight = self.parent.rect().bottomRight()
            
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
def setSlider(self):
    self.slider = QSlider(Qt.Orientation.Horizontal)
    self.slider.sliderMoved.connect(self.shared.setPosition)
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

    self.openButton = QPushButton("Files")
    self.playButton = QPushButton("Play")  
    if self.player == "one":            
        self.aspButton   = QPushButton("Aspect")
    self.loopButton = QPushButton("Loop")
    self.stopButton = QPushButton("Stop")
    self.byeButton  = QPushButton("Quit")
    
    self.openButton.clicked.connect(self.openFile) if self.player == "one"\
        else self.openButton.clicked.connect(self.openFile)         ## <- "two"
    
    self.playButton.clicked.connect(self.shared.playVideo)
    if self.player == "one":
        self.aspButton.clicked.connect(self.setAspButton)
    self.loopButton.clicked.connect(self.shared.looper)
    self.stopButton.clicked.connect(self.shared.stopVideo)
    self.byeButton.clicked.connect(self.bye)

    hbox = QHBoxLayout(self)
            
    hbox.addWidget(self.openButton)  
    hbox.addWidget(self.playButton)    
    if self.player == "one":       
        hbox.addWidget(self.aspButton)
    hbox.addWidget(self.loopButton)    
    hbox.addWidget(self.stopButton)  
    hbox.addWidget(self.byeButton)
    
    self.buttonGroup.setLayout(hbox)
    self.buttonGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
    self.buttonGroup.setLineWidth(1)
    
    hbox = QHBoxLayout(self)
    hbox.addWidget(self.buttonGroup)

    self.buttons = QLabel()
    self.buttonGroup.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    self.buttons.setFixedHeight(60)
    self.buttons.setLayout(hbox)
    
    return self.buttons
    
### --------------------------------------------------------
### detect video width and height to set aspect ratio 
### --------------------------------------------------------      
def getMetaData(path):    
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
    ''' uses ffprobe -- may not always report width/height correctly for non 9:16 verticals
        and blows up if run from mac desktop -- works well in vscode '''
    # try: 
    #     result = subprocess.run(
    #         ['ffprobe', '-v', 'error', '-select_streams',  'v:0', '-show_entries', 'stream=width,height','-of', 'csv=s=,:p=0', path],
    #         capture_output=True,
    #         text=True,
    #         check=True
    #     )
    #     res = result.stdout.strip()
    #     i = res.index(',')
    #     width, height = res[0:i], res[i+1:]
    #     return int(width), int(height) 
    # except Exception:
    #     return 0, 0
           
        
### ---------------------- that's all ---------------------- 
 


