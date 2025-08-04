
import os
import sys
import time
import math  
import subprocess

### ------------------ videoPlayerOne.py ------------------- 
#d ''' Run the python script-qt6.py to remove all the qt5 and 
#d     pyside code and CommentS - there are scripts for both.
#d     See getVideoWidthHeight to set the aspect ratio using one
#d     of the three options for auto format sizing and display.
#d     I moved return 0,0 from video. Set AspectRatioOo and 
#d     PlayVideo globals as needed. VideoPlayerOne uses a first 
#d     frame display not a backdrop. 
#d     The keys '>', ']', '=' expands the frame in both 
#d     directions horizontally or vertically and the keys
#d     '<', '[', '-' contracts in both as well.  '''
### -------------------------------------------------------- 
from PyQt6.QtCore       import Qt, QUrl, QTimer
from PyQt6.QtGui        import QGuiApplication
from PyQt6.QtWidgets    import QWidget, QSlider, QHBoxLayout, QVBoxLayout, QMessageBox, \
                                    QFileDialog, QLabel, QPushButton, QFrame, QApplication

from PyQt6.QtMultimedia         import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets  import QVideoWidget
### ------------ comment out for 6, uncomment for 5 -----------------
# from PyQt6.QtMultimedia   import QMediaContent  ## 5
### ---------------------------- end --------------------------------

### -------------------------------------------------------- 
PlayVideo = True  ## when loaded - no start button
AspectRatioOn = True  ## requires a method that returns width and height

AspKeys = ['A','F','H','V']
WID, HGT, OTH = 40, 116, 60  ## for opening without discovery
Height, VHeight, VWidth = 560, 815, 435    ## widget default heights and width

Chars = {'A': [1.33, 620],   ## default widths 
         'F': [1.50, 700], 
         'H': [1.77, 810],
         'V': [0.56, 435],
} 

Asps  = {1.33: ['A', 620],
         1.50: ['F', 700],
         1.77: ['H', 810],
         0.56: ['V', 435],
}

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
        ## 6
### ------------ uncomment for 5 ... comment out for 6 ----------------- 
        # self.mediaPlayer.mediaStatusChanged[QMediaPlayer.MediaStatus].connect(self.mediaStatusChanged)  ## 5
        # self.mediaPlayer.error.connect(self.handleError)  ## 5  
### ---------------------------- end --------------------------------
 
        self.mediaPlayer.durationChanged.connect(self.durationChanged) 
        self.mediaPlayer.positionChanged.connect(self.positionChanged)   
        
        self.timer = QTimer(self)  ## google A.I. 
        self.timer.timeout.connect(self.resizeFinished)
        self.timer_interval = 5000  
        
        self.setAcceptDrops(True)  
        self.path= ''
        
        if len(sys.argv) > 1: 
            self.path = sys.argv[1]
              
        self.lastKey = '' 
        self.fileName = ''
        
        self.aspect = 0.0    ## set if not in AspKeys, mainly for horizontals
        self.OtherAsp = 0.0  ## the reciprocal of aspect ratio used by non 9:16 verticals
        
        self.lastVWidth = 0
        self.lastHeight = 0
        
        self.started = False   
        self.frameW, self.frameH = 0, 0  ## for framing 
                        
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
      
        self.openPlayer('F') ## open full frame - 3:2
       
        self.show()
        
### --------------------------------------------------------
    def keyPressEvent(self, e):
        key = e.key()
        mod = e.modifiers()   
            
        if key == Qt.Key.Key_Space:  ## spacebar to pause/resume
            self.playVideo()     
                  
        elif key == Qt.Key.Key_BracketRight or mod & Qt.KeyboardModifier.ShiftModifier \
            and key in (Qt.Key.Key_Greater, Qt.Key.Key_Plus):
                self.zoom(1.10)     
                  
        elif key == Qt.Key.Key_BracketLeft or mod & Qt.KeyboardModifier.ShiftModifier \
            and key in (Qt.Key.Key_Less, Qt.Key.Key_Underscore):
                self.zoom(.90)  
        else:
            try:
                key = chr(e.key())
            except:
                return
            if key in AspKeys:
                self.resizeAndMove(key)   
            elif key == 'S':  ## toggle start and stop
                if self.started == False:   
                    self.playVideo()
                else:
                    self.stopVideo(); self.started = False         
            elif key in ('Q','X'):
                self.bye()
            e.accept()
   
 ### --------------------------------------------------------      
    def mousePressEvent(self, e):    
        if e.button() == Qt.MouseButton.RightButton:
            if self.fileName != '':
                self.setWindowTitle(self.fileName)
            e.accept()
         
    def mouseReleaseEvent(self, e):   
        self.setWindowTitle("VideoPlayer")
        e.accept()
   
    def dragEnterEvent(self, e):  
        if e.mimeData().hasUrls():   
            m = e.mimeData()
            fileName = m.urls()[0].toLocalFile() 
            self.setFileName(fileName)
            self.mediaPlayer.pause() 
            if PlayVideo: self.playVideo()
            e.accept()
        else:
            e.ignore()
       
    def dragLeaveEvent(self, e):
        e.accept()
                 
### --------------------------------------------------------
    def openPlayer(self, key):  ## default setting only
        ctr = QGuiApplication.primaryScreen().availableGeometry().center()
        x, y = ctr.x(), ctr.y()       
        width = Chars[key][1]  
        if AspectRatioOn and key in AspKeys != self.lastKey: 
            self.setAspectRatio()
        if key in ('A', 'H', 'F'):   
            self.resize(width, Height) 
            self.move(x-int(width/2), int(y-450))  ## tailor to taste
            self.lastHeight = Height
        elif key == 'V':      
            width = Chars[key][1]
            self.resize(width, VHeight) 
            self.move(x-int(width/2), 150)
        self.lastKey = key
   
    def openFile(self):
        if self.path == '':  
            self.path = os.getcwd()    
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Media", self.path, \
                        "Video Files (*.mov *.mp4 *.mp3 *.m4a *.wav)")
        if fileName != '':
            self.setFileName(fileName)
            self.mediaPlayer.setPosition(0)  ## shows first frame plus pause
            self.mediaPlayer.pause()     
            if PlayVideo: QTimer.singleShot(100, self.playVideo)  
  
    def setAspectRatio(self):
        if self.fileName == '': return    
        path = self.path + '/' + os.path.basename(self.fileName)   
        width, height = self.getVideoWidthHeight(path) 
        try:
            asp = math.floor((width/height) * 100)/100.0  
        except:
            asp = 0
        if width == 0 or asp == 0:
            if AspectRatioOn:
                str = ("AspectRatioOn -see getVideoWidthHeight to set format detection")   
            else:
                str = ("Exception with width/height from getVideoWidthHeight")   
            self.msgbox(str)
            return  
        self.aspect = 0
        try:              
            self.resizeAndMove(Asps[asp][0]) 
        except:
            self.theOtherAsp(asp, width, height)
                             
    def theOtherAsp(self, asp, width, height):  
        self.aspect = asp  
        self.OtherAsp = 0
        if asp < 1.0:  ## non 9:16 verticals
            if self.lastVWidth == 0:  
                self.lastVWidth = VWidth
            self.OtherAsp = math.floor((height/width) * 100)/100.0 
        self.resizeAndMove('O')
        # self.aspButton.setText(str(asp))
            
    def setOther(self):  ## from aspect button
        v = self.videoWidget.size()  ## uses the current video widget size 
        self.aspect = math.floor(v.width()/v.height() * 100)/100.0   
        self.resizeAndMove('O')  ## becomes lastKey
 
    def msgbox(self, str):
        msg = QMessageBox()
        msg.setText(str)
        msg.exec()  
      
    def framing(self):  ## the differences between widget size and videoWidget
        s, v = self.size(), self.videoWidget.size()   
        return s.width() - v.width(), s.height() - v.height()  
                    
### --------------------------------------------------------                   
    def resizeAndMove(self, key): 
        oldWidth = self.width()
        pos = self.pos()
        if key == 'O' and self.OtherAsp > 0:
            dif = self.resizeOtherVerticals()
        elif key == 'V':  
            width = Chars[key][1] 
            self.resize(width, VHeight)  ## doesn't change
            dif = int((width - oldWidth)/2) 
        else:
            dif = self.newWidths(key, oldWidth)  
        self.move(pos.x()-dif, pos.y())  
        self.lastKey = key  
         
    def newWidths(self, key, oldWidth):  ## uses height * asp
        if key in AspKeys:  ## works with type 'O' horizontal
            asp = Chars[key][0]   
        else:
            asp = self.aspect    
        if self.lastKey == 'V':     
            height = self.lastHeight  
        else:
            height = self.height()
            self.lastHeight = height 
        return self.resizeNewWidths(asp, height, oldWidth)
    
    def resizeNewWidths(self, asp, height, oldWidth):
        if  self.frameH > 0:  ## based on videoWidget
            newWidth = int(asp * (height - self.frameH) + self.frameW) 
        else:              ## videoWidget not discoverable
            newWidth = int(asp * (height - HGT) + WID)   ## or use a screen pixel ruler
        self.resize(newWidth, height)   
        return int((newWidth - oldWidth )/2)  ## center qwidget
    
    def resizeOtherVerticals(self):  ## not 9:16
        asp = self.OtherAsp
        width = self.lastVWidth 
        self.lastVWidth = width
        self.resize(width, int(asp * width)+OTH) 
        return 0
       
    def zoom(self, zoom):
        if self.mediaPlayer != None:  
            if int(self.height()* zoom) > 1280 or int(self.height()* zoom) < 300:
                return    
                               
            if  self.lastKey == 'O' and self.aspect > 0:  ## horizontals
                asp = self.aspect
                nwidth = self.lastVWidth
            else:
                asp = Chars[self.lastKey][0] 
                            
            height = int(self.height()* zoom)  ## new height     
             
            frW, frH = self.framing() 
            nvH = (height - frH)  ## new video height
            nvW = int(nvH *asp)   ## new video width   
            nwidth = nvW + frW    ## new widget width   
              
            p, width = self.pos(), self.width()  
            self.resize(nwidth, height)  
            dif = int((self.width() - width)/2) 
            self.move(p.x()-dif, p.y()) 
        
    def resizeEvent(self, e):
        self.timer.start(self.timer_interval)  
        e.accept()
           
    def resizeFinished(self):
        self.timer.stop()
        self.zoom(1.00)  ## seems like the only thing that works
           
### --------------------------------------------------------
    def getVideoWidthHeight(self, path):
        
        return 0,0  ## ComMent this out inorder to work
        
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
                
        ''' requires opencv-python - may not always report width/height correctly 
            for non 9:16 verticals - initial method - not mac specific '''
        # try:  
        #     import cv2   
        #     cap = cv2.VideoCapture(path)     
        #     if not cap.isOpened():
        #         return None  
        #     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        #     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        #     cap.release()
        #     return width, height
        # except:
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

### --------------------------------------------------------                                                     
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
            self.fileName = pathMod(fileName)  ## it's for display]
        self.setWindowTitle(self.fileName) 
        if AspectRatioOn: 
            self.setAspectRatio()  ## just to make sure and avoid crashing

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
    ## comment out for 6
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
    ## comment out for 6
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
        self.aspButton  = QPushButton("Aspect")
        self.stopButton = QPushButton("Stop")
        self.byeButton  = QPushButton("Quit")  
        
        self.openButton.clicked.connect(self.openFile)
        self.playButton.clicked.connect(self.playVideo)
        self.aspButton.clicked.connect(self.setOther)
        self.stopButton.clicked.connect(self.stopVideo)
        self.byeButton.clicked.connect(self.bye)

        hbox = QHBoxLayout()
        
        hbox.addWidget(self.openButton)  
        hbox.addWidget(self.playButton)
        hbox.addWidget(self.aspButton)
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





