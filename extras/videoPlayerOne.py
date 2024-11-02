
import os
import sys
import time
import math  
   
# import cv2      ## required to choose screen format

from PyQt6.QtCore       import Qt, QUrl
from PyQt6.QtGui        import QGuiApplication
from PyQt6.QtWidgets    import QWidget, QSlider, QHBoxLayout, QVBoxLayout, \
                                QFileDialog, QLabel, QPushButton, QFrame, QApplication

from PyQt6.QtMultimedia         import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets  import QVideoWidget

# from PyQt6.QtMultimedia   import QMediaContent  ## common out for 6, uncomment for 5 <<<--------

### --------------------------------------------------------
''' There's a commented out self.resizeEvent which would probably be useful 
    if you plan to make any size changes.  You will need to install opencv-python 
    and uncomment out the two imports and this line # self.setScreenFormat(fileName) 
    inorder to have the videoPlayer set the screen format on drag and drop. '''
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
        self.audioOut = QAudioOutput()        
        self.mediaPlayer.setAudioOutput(self.audioOut)     
        self.mediaPlayer.mediaStatusChanged[QMediaPlayer.MediaStatus].connect(self.mediaStateChanged)    
        self.mediaPlayer.errorChanged.connect(self.handleError)  
            
### ------------ uncomment for 5 ... comment out for 6 ----------------- 
        # self.mediaPlayer.mediaStatusChanged[QMediaPlayer.MediaStatus].connect(self.mediaStatusChanged)
        # self.mediaPlayer.error.connect(self.handleError)     
### ---------------------------- end --------------------------------

        self.mediaPlayer.durationChanged.connect(self.durationChanged) 
        self.mediaPlayer.positionChanged.connect(self.positionChanged)   
      
        self.setAcceptDrops(True)  
      
        self.fileName = ''
        self.path = '' 
        
        if len(sys.argv) > 1:  ## set starting directory
            self.path = sys.argv[1]
                    
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.setPosition)
      
        ## 'Customize the appearance' - to quote the browser
        ##  with a little help from google AI  
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
        vbox.addSpacing(10)
        vbox.addLayout(self.setButtons())
        vbox.addSpacing(10)
        vbox.addWidget(self.slider)
        self.setLayout(vbox)   
        
        self.moveResize('F') ## default - roughly 3:2
        self.show()

### --------------------------------------------------------
    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Space:  ## spacebar to pause/resume
            self.playVideo()
        elif chr(e.key()) in ('A', 'F', 'H', 'S', 'V'):
            self.moveResize(chr(e.key()))
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
            self.doit(fileName)
            self.playVideo()     
            e.accept()
        else:
            e.ignore()
       
    def dragLeaveEvent(self, e):
        e.accept()
                 
### --------------------------------------------------------                         
    def openFile(self):
        if self.path == '':  self.path = os.getcwd()    
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Media", self.path, \
                       "Video Files (*.mov *.mp4 *.mp3 *.m4a *.wav)")
        if fileName != '':
            self.doit(fileName)
            
    def doit(self, fileName):        
### ------------ uncomment for 6 ... comment out for 5 -----------------     
        self.mediaPlayer.setSource((QUrl.fromLocalFile(fileName)))     ## source doesn't change even if self.fileName gets truncated
        # self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))  ## uncomment for 5      
### ---------------------------- end ----------------------------------- 
        self.playButton.setEnabled(True)   
        self.path = fileName[0:fileName.rfind('/')]  ## so it knows where to start looking next time you search
        if fileName != self.fileName and len(fileName) <= 24:  ## if greater than 24 chars or self.fileName "" 
            self.fileName = fileName 
        else:
            self.fileName = pathMod(fileName)  ## it's for display

        # self.setScreenFormat(fileName)    ## uses cv2 to set screen format on start of video

### ------------ uncomment for 6 ... comment out for 5 -----------------              
    def playVideo(self):
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.mediaPlayer.pause()
            self.pauseButton.setText('Resume')  
        else:
            self.mediaPlayer.play()
            self.pauseButton.setText('Pause') 
                   
    def mediaStateChanged(self, state):
        if state == QMediaPlayer.MediaStatus.EndOfMedia:
            while not (self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.StoppedState):
                time.sleep(.05)
            self.stopVideo()
            
### ------------ uncomment for 5 ... comment out for 6 -----------------
    # def playVideo(self):
    #     if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
    #         self.mediaPlayer.pause()
    #         self.pauseButton.setText('Resume')  
    #     else:
    #         self.mediaPlayer.play()   
    #         self.pauseButton.setText('Pause')  
           
    # def mediaStatusChanged(self, status):
    #     if status == QMediaPlayer.MediaStatus.EndOfMedia:
    #         while not (self.mediaPlayer.state() == QMediaPlayer.StoppedState):
    #             time.sleep(.01)
    #         self.stopVideo()
    
 ### ---------------------------- end -----------------------------------    
    def stopVideo(self):
        self.mediaPlayer.stop()
        self.setPosition(0)
  
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
    def moveResize(self, key):
        ctr = QGuiApplication.primaryScreen().availableGeometry().center()
        x, y = ctr.x(), ctr.y() 
        if key == 'A':      ## academy - 4:3
            self.move(x-320, y-350)
            self.resize(645, 600)
        elif key == 'F':    ## full-frame - 3:2
            self.move(x-360, y-350)
            self.resize(720, 600)
        elif key == 'H':        ## 16:9 aka 1080
            self.move(x-425,y-350)
            self.resize(850, 600)
        elif key == 'V':        ## 9:16
            self.move(x-225, y-450)
            self.resize(450, 875) 
        elif key == 'S':
            self.stopVideo()

    def setScreenFormat(self, video_path):  ## optional - requires opencv-python
        cap = cv2.VideoCapture(video_path)  ## plus edits
        if not cap.isOpened():
            return None

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()

        asp = math.floor(width/height * 100)/100.0
        if asp == 1.77:
            self.moveResize('H')
        elif asp == 1.50:
            self.moveResize('F')
        elif asp == 1.33:
            self.moveResize('A')
        elif asp == 0.56:
            self.moveResize('V')
        else:
            self.moveResize('F')  ## default

    # def resizeEvent(self, event):   ## get the aspect ratio for both widgets
    #     s, v = self.size(), self.videoWidget.size()    
    #     print(f"( {v.width()}, {v.height()}, {math.floor(v.width()/v.height() * 100)/100.0}, {s.width()}, {s.height()})")

### --------------------------------------------------------          
    def setButtons(self):     
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedHeight(50)
        
        self.openButton  = QPushButton("Files")
        self.playButton  = QPushButton("Start")
        self.pauseButton = QPushButton("Pause")
        self.stopButton  = QPushButton("Stop")
        self.byeButton   = QPushButton("Quit")  
        
        self.openButton.clicked.connect(self.openFile)
        self.playButton.clicked.connect(self.playVideo)
        self.pauseButton.clicked.connect(self.playVideo)
        self.stopButton.clicked.connect(self.stopVideo)
        self.byeButton.clicked.connect(self.bye)

        hbox = QHBoxLayout()
        
        hbox.addSpacing(15)
        hbox.addWidget(self.openButton)  
        hbox.addSpacing(10)
        hbox.addWidget(self.playButton)
        hbox.addSpacing(5)
        hbox.addWidget(self.pauseButton) 
        hbox.addSpacing(5) 
        hbox.addWidget(self.stopButton)
        hbox.addSpacing(10)
        hbox.addWidget(self.byeButton)
        hbox.addSpacing(15)
 
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
    

