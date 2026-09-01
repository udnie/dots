

import os
import time 
import subprocess

from PyQt6.QtCore       import Qt, QSizeF, QUrl
from PyQt6.QtWidgets    import QSlider, QHBoxLayout, QLabel, QFrame, \
                                QPushButton, QSizePolicy

from PyQt6.QtMultimedia         import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets  import QVideoWidget, QGraphicsVideoItem

# from PyQt6.QtMultimedia           import QMediaContent  ## 5

### -------------------------------------------------------- 
''' Relocated MediaPlayer, getMetaData, setSlider and setButtons -  
    shared by both videoPlayers. '''
### --------------------------------------------------------   
class MediaPlayer(QMediaPlayer): 
### --------------------------------------------------------
    def __init__(self, parent, ViewW, ViewH):
        super().__init__()
        
        self.parent = parent
        self.shared = parent.shared
        
        self.mediaPlayer = QMediaPlayer(self) ## 6
        # self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)  ## 5 
            
        if self.parent.player == "one":
            self.setVideoWidget()
     
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

### -----------------------------------------------------------------
    def setFileName(self, fileName): 
        try:
            self.mediaPlayer.setSource((QUrl.fromLocalFile(fileName)))  ## 6
            # self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(fileName))))  ## 5  
        except:
            return False
        self.mediaPlayer.pause()  ## makes it visible 
        return True
        
    def setVideoWidget(self):   
        self.videoWidget = QVideoWidget()   
        self.mediaPlayer.setVideoOutput(self.videoWidget) 
        self.videoWidget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        
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

    openButton = QPushButton("Files")
    self.playButton = QPushButton("Play")  
    if self.player == "one":            
        self.aspButton = QPushButton("Aspect")
    self.loopButton = QPushButton("Loop")
    
    self.stopButton = QPushButton("Stop")
    if self.player == "two":  
        self.clearButton = QPushButton("Clear")
    byeButton  = QPushButton("Quit")
    openButton.clicked.connect(self.openFile) if self.player == "one" \
        else openButton.clicked.connect(self.openFile)         ## <- "two"
    
    self.playButton.clicked.connect(self.shared.playVideo)
    if self.player == "one":
        self.aspButton.clicked.connect(self.setAspButton)
    self.loopButton.clicked.connect(self.shared.looper)
    self.stopButton.clicked.connect(self.shared.stopVideo)
    if self.player == "two":
        self.clearButton.clicked.connect(self.shared.clearScreen)
    byeButton.clicked.connect(self.bye)

    hbox = QHBoxLayout(self)        
    hbox.addWidget(openButton)  
    hbox.addWidget(self.playButton)    
    if self.player == "one":       
        hbox.addWidget(self.aspButton)
    hbox.addWidget(self.loopButton)    
    hbox.addWidget(self.stopButton)  
    if self.player == "two":       
        hbox.addWidget(self.clearButton)
    hbox.addWidget(byeButton)
    
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
    try:  
        import cv2  ## <<---------------------  
        try:
            cap = cv2.VideoCapture(path) 
        except:
            return 0,0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        return width, height
    except:
        return 0, 0
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
 

  
