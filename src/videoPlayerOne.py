
import os
import sys
import time
import math  

### ------------------ videoPlayerOne.py ------------------- 
#d ''' You will need to install opencv-python and unComment the cv2 import
#d     and this line # self.setScreenFormat(fileName) inorder to have the 
#d     videoPlayer set the screen format on drag and drop. cv2 is used
#d     in setting the aspect-ratio (width/height) of a video file.
#d     A right-mouse click displays the filename in the window title.
#d
#d     Also, adds a first frame display but not a backdrop and 
#d    '>', ']', '=' expands in both directions horizontally or 
#d    vertically and '<', '[', '-' contracts in both as well. '''    
### -------------------------------------------------------- 
# import cv2 
### --------------------------------------------------------
from PyQt6.QtCore       import Qt, QUrl
from PyQt6.QtGui        import QGuiApplication
from PyQt6.QtWidgets    import QWidget, QSlider, QHBoxLayout, QVBoxLayout, \
                                QFileDialog, QLabel, QPushButton, QFrame, QApplication

from PyQt6.QtMultimedia         import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets  import QVideoWidget

### ------------ comment out for 6, uncomment for 5 -----------------
# from PyQt6.QtMultimedia   import QMediaContent  ## 5
### ---------------------------- end --------------------------------

YoffSet, VYoffset = 450, 550   ## px above screen center
Height,  VHeight  = 500, 815   ## default heights

WID, HGT = 40, 116  ## for opening without discovery

Chars   = ( 'A',  'F',  'H',  'V')  ## as in characters 
Asps    = (1.33, 1.50, 1.77, 0.56)  ## more snakes - Cleopatra's favorite
Widths  =  (550,  615,  720,  435)  ## default widget widths

### --------------------------------------------------------
class VideoPlayer(QWidget):
### --------------------------------------------------------
    def __init__(self, parent=None):
        super(VideoPlayer, self).__init__(parent)
        self.setWindowTitle("VideoPlayer")

### ------------ comment out for 5, uncomment for 6 -----------------
        self.mediaPlayer = QMediaPlayer()  ## 6
        # self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)  ## 5
### ---------------------------- end --------------------------------  

        self.videoWidget = QVideoWidget()
        self.mediaPlayer.setVideoOutput(self.videoWidget)
                   
### ------------ comment out for 5, uncomment for 6 -----------------
        self.audioOut = QAudioOutput()   ## 6      
        self.mediaPlayer.setAudioOutput(self.audioOut)   ## 6   
        self.mediaPlayer.mediaStatusChanged[QMediaPlayer.MediaStatus].connect(self.mediaStateChanged) ## 6    
        self.mediaPlayer.errorChanged.connect(self.handleError)   ## 6
### ------------ uncomment for 5 ... comment out for 6 ----------------- 
        # self.mediaPlayer.mediaStatusChanged[QMediaPlayer.MediaStatus].connect(self.mediaStatusChanged)  ## 5
        # self.mediaPlayer.error.connect(self.handleError)  ## 5  
### ---------------------------- end --------------------------------

        self.mediaPlayer.durationChanged.connect(self.durationChanged) 
        self.mediaPlayer.positionChanged.connect(self.positionChanged)   
      
        self.setAcceptDrops(True)  
      
        self.fileName = ''
        self.path = ''
        
        self.lastKey = ''  ## the last key
        self.lastHeight = 0

        self.started = False
        self.frameW, self.frameH = 0, 0  ## for framing 
        
        if len(sys.argv) > 1:  ## set starting directory
            self.path = sys.argv[1]
                    
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.setPosition)
      
        ## a little help from google AI  
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
        vbox.addLayout(self.setButtons())
        vbox.addWidget(self.slider)
        self.setLayout(vbox)   
      
        self.openPlayer('F') ## current default - 3:2
       
        self.show()
        
### --------------------------------------------------------
    def keyPressEvent(self, e):
        mod = e.modifiers()  
        
        if e.key() == Qt.Key.Key_Space:  ## spacebar to pause/resume
            self.playVideo()
            
        elif e.key() in (Qt.Key.Key_BracketRight, Qt.Key.Key_BracketLeft):
            self.zoom(1.10) if e.key() == Qt.Key.Key_BracketRight else self.zoom(.90)
        
        elif mod & Qt.KeyboardModifier.ShiftModifier and e.key() in (Qt.Key.Key_Greater, Qt.Key.Key_Less):
            self.zoom(1.10) if e.key() == Qt.Key.Key_Greater else self.zoom(.90)
                
        elif mod & Qt.KeyboardModifier.ShiftModifier and  e.key() in (Qt.Key.Key_Plus, Qt.Key.Key_Underscore):
            self.zoom(1.10) if e.key() == Qt.Key.Key_Plus else self.zoom(.90)
      
        else:
            try:
                key = chr(e.key())
            except:
                return
            if key in Chars:
                self.resizeAndMove(key)
            elif key == 'S':  ## toggle start and stop
                if self.started == False:   
                    self.playVideo()
                else:
                    self.stopVideo(); self.started = False
            elif key in ('Q', 'X'):
                self.bye()
            e.accept()
        
    def mousePressEvent(self, e):    
        if e.button() == Qt.MouseButton.RightButton:
            if self.fileName != '':
                self.setWindowTitle(self.fileName)
            e.accept()
         
    def mouseReleaseEvent(self, e):
        self.setWindowTitle("VideoPlayer")
        e.accept()
  
### --------------------------------------------------------   
    def dragEnterEvent(self, e):  
        if e.mimeData().hasUrls():   
            m = e.mimeData()
            fileName = m.urls()[0].toLocalFile() 
            self.setFileName(fileName)
            self.playVideo()     
            e.accept()
        else:
            e.ignore()
       
    def dragLeaveEvent(self, e):
        e.accept()
                 
### --------------------------------------------------------                
    def openPlayer(self, key):  ## for default opening setting
        ctr = QGuiApplication.primaryScreen().availableGeometry().center()
        x, y = ctr.x(), ctr.y() 
        width = Widths[Chars.index(key)]
        if key in ('A', 'H', 'F'):   
            self.resize(width, Height) 
            self.move(x-int(width/2), int(y-YoffSet))  
            self.lastHeight = Height
        elif key == 'V':      
            self.resize(Widths[3], VHeight) 
            self.move(x-int(width/2), int(y-VYoffset))
        self.lastKey = key
     
    def resizeAndMove(self, key):          
        oldWidth = self.width()
        pos = self.pos()
        if key == 'V':
            self.resize(Widths[3], VHeight)  ## doesn't change
            dif = int((Widths[3] - oldWidth)/2) 
        else:
            dif = self.resizeNewWidth(key, oldWidth)  
        self.move(pos.x()-dif, pos.y())  
        self.lastKey = key  
         
    def resizeNewWidth(self, key, oldWidth):  
        asp = Asps[Chars.index(key)]
        if self.lastKey == 'V':     
            height = self.lastHeight  
        else:
            height = self.height()
            self.lastHeight = height
        if  self.frameH > 0:  ## based on videoWidget
            newWidth = int(asp * (height - self.frameH) + self.frameW) 
        else:              ## videoWidget not discoverable
            newWidth = int(asp * (height - HGT) + WID)   ## or use a screen pixel ruler
        self.resize(newWidth, height)   
        return int((newWidth - oldWidth )/2)  ## center qwidget
  
    def zoom(self, zoom):
        if self.mediaPlayer != None:  
            height = int(self.height()* zoom)  ## new height
            p, width = self.pos(), self.width()  
 
            asp = Asps[Chars.index(self.lastKey)]   
            frW, frH = self.framing() 
      
            nvH = (height - frH)  ## new video height
            nvW = int(nvH *asp)   ## new video width   
            nwidth = nvW + frW    ## new widget width 
            
            self.resize(nwidth, height)   
            dif = int((self.width() - width)/2) 
            self.move(p.x()-dif, p.y())   
        
    def setScreenFormat(self, video_path):  ## optional - requires opencv-python
        cap = cv2.VideoCapture(video_path)  ## plus edits - reads video file    
        if not cap.isOpened():
            return None  
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        asp = math.floor(width/height * 100)/100.0  
        try: 
            self.resizeAndMove(Chars[Asps.index(asp)])
        except:
            return None
   
    def framing(self):  ## the differences between widget size and videoWidget
        s, v = self.size(), self.videoWidget.size()   
        return s.width() - v.width(), s.height() - v.height()
             
### --------------------------------------------------------                         
    def openFile(self):
        if self.path == '':  self.path = os.getcwd()    
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Media", self.path, \
                       "Video Files (*.mov *.mp4 *.mp3 *.m4a *.wav)")
        if fileName != '':
            self.setFileName(fileName)
            self.mediaPlayer.setPosition(0)  ## shows first frame plus pause
            self.mediaPlayer.pause()  
              
    def setFileName(self, fileName):        
### ------------ uncomment for 6 ... comment out for 5 -----------------     
        self.mediaPlayer.setSource((QUrl.fromLocalFile(fileName)))  ## 6  ## source doesn't change even if self.fileName gets truncated
        # self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))  ## 5      
### ---------------------------- end ----------------------------------- 
        self.playButton.setEnabled(True)   
        self.fileName = ''
        self.path = fileName[0:fileName.rfind('/')]  ## so it knows where to start looking next time you search
        if fileName != self.fileName and len(fileName) <= 24:  ## if greater than 24 chars or self.fileName "" 
            self.fileName = fileName 
        else:
            self.fileName = pathMod(fileName)  ## it's for display

### -------------------------- if using cv2 ----------------------------
        # self.setScreenFormat(fileName)  ## uses cv2 to get aspect/ratio screen format on start of video
### -------------------------- if using cv2 ----------------------------
    ## 6
### ------------ uncomment for 6 ... comment out for 5 -----------------              
    def playVideo(self):  ## 6
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:  ## 6
            self.mediaPlayer.pause()  ## 6
            self.playButton.setText('Resume')  ## 6 
        else:   ## 6
            if self.fileName != '':   ## 6
                self.mediaPlayer.play()   ## 6
                self.playButton.setText('Pause')  ## 6
                self.started = True ## 6
                self.frameW, self.frameH = self.framing()   ## 6   ## uses the videoWidget to get the widget framing sizes  
           
    def mediaStateChanged(self, state): ## 6
        if state == QMediaPlayer.MediaStatus.EndOfMedia: ## 6
            while not (self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.StoppedState): ## 6
                time.sleep(.05) ## 6
            self.stopVideo()   ## 6    
    ## 6          
### ------------ uncomment for 5 ... comment out for 6 -----------------
    # def playVideo(self):   ## 5
    #     if self.mediaPlayer.state() == QMediaPlayer.PlayingState:  ## 5
    #         self.mediaPlayer.pause()   ## 5
    #         self.playButton.setText('Resume')   ## 5
    #     else:   ## 5
    #          if self.fileName != '':   ## 5
    #             self.mediaPlayer.play()  ## 5
    #             self.playButton.setText('Pause')  ## 5
    #             self.started = True   ## 5
    #             self.frameW, self.frameH = self.framing()  ## uses the videoWidget to get the widget framing sizes   ## 5
         
    # def mediaStatusChanged(self, status):   ## 5
    #     if status == QMediaPlayer.MediaStatus.EndOfMedia:   ## 5
    #         while not (self.mediaPlayer.state() == QMediaPlayer.StoppedState):   ## 5
    #             time.sleep(.05)   ## 5
    #         self.stopVideo()   ## 5
    
 ### ---------------------------- end ----------------------------------- 
    def stopVideo(self):
        self.mediaPlayer.stop()
        time.sleep(.10)
        self.playButton.setText('Start')
        self.started = False 
        self.setPosition(0)  ## shows first frame plus pause
        self.mediaPlayer.pause() 
  
    def positionChanged(self, position):
        self.slider.setValue(position)

    def durationChanged(self, duration):
        self.slider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.setWindowTitle("Error: " + self.mediaPlayer.errorString())
               
    def bye(self):
        self.close()
        
### --------------------------------------------------------          
    def setButtons(self):     
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedHeight(40)
  
        self.openButton = QPushButton("Files")
        self.playButton = QPushButton("Start")
        self.stopButton = QPushButton("Stop")
        self.byeButton  = QPushButton("Quit")  
        
        self.openButton.clicked.connect(self.openFile)
        self.playButton.clicked.connect(self.playVideo)
        self.stopButton.clicked.connect(self.stopVideo)
        self.byeButton.clicked.connect(self.bye)

        hbox = QHBoxLayout()
        
        hbox.addWidget(self.openButton)  
        hbox.addWidget(self.playButton)
        hbox.addWidget(self.stopButton)
        hbox.addWidget(self.byeButton)

        self.buttonGroup.setLayout(hbox)
        self.buttonGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
        self.buttonGroup.setLineWidth(1)
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.buttonGroup)

        return hbox
    
def pathMod(fileName):
    fileName = fileName[-24:]
    if fileName.find('/') > 0:
        fileName = '..' + fileName[fileName.find('/'):]
    return fileName

### --------------------------------------------------------  
if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    sys.exit(app.exec())
    
### ---------------------- that's all ----------------------





