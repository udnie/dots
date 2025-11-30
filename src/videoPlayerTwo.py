
import os
import sys
import time
import math  
import subprocess

from PyQt6.QtCore       import Qt, QUrl, QTimer, QPoint, QSizeF, QRect, QSize
from PyQt6.QtGui        import QGuiApplication, QPixmap, QCursor
from PyQt6.QtWidgets    import QWidget, QSlider, QHBoxLayout, QVBoxLayout,  \
                                QLabel, QPushButton, QFrame, QApplication, \
                                QSizePolicy,  QGraphicsView, QGraphicsScene, \
                                QFileDialog, QGraphicsPixmapItem, QMessageBox
                                                                        
from PyQt6.QtMultimedia         import QMediaPlayer,  QAudioOutput
from PyQt6.QtMultimediaWidgets  import QGraphicsVideoItem

# from PyQt6.QtMultimedia          import QMediaContent   ## 5

ViewW,  ViewH  =  790,  525  ## starting video size
MaxWid, MaxHgt = 1800, 1065

MinWid = 300  ## minimum widget width
MinHgt = 400  ## minimum widget height

VertW  = 525  ## vertical starting width
VertH  = 100  ## vertical starting height
HorzH  = 200  ## horizontal starting height

## Frames width and height and slider height 
WID, HGT, PAD = 40, 140, 30

### -------------------------------------------------------- 
''' Uses videoPlayer from dotsVideoPlayer with a few small changes 
    as it doesn't have a slider. Shift-S hides/shows slider. '''
### --------------------------------------------------------   
class MediaPlayer(QMediaPlayer): 
### --------------------------------------------------------
    def __init__(self, parent, fileName):
        super().__init__()
        
        self.videoPlayer = parent
        self.backdrop = None
     
        self.mediaPlayer = QMediaPlayer(self) ## 6
        # self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)  ## 5 
        try:
            self.mediaPlayer.setSource((QUrl.fromLocalFile(fileName)))  ## 6
            # self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(fileName))))  ## 5  
        except:
            self.videoPlayer.msgbox('error setting mediaPlayer')
            return None
        
        self.videoItem = QGraphicsVideoItem()   
        self.mediaPlayer.setVideoOutput(self.videoItem)
        
        self.videoItem.setZValue(100)
        self.videoItem.setSize(QSizeF(float(ViewH*1.5), float(ViewH)))  
        self.videoItem.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
          
        self.mediaPlayer.mediaStatusChanged[QMediaPlayer.MediaStatus].connect(self.mediaStateChanged) 
  
        self.mediaPlayer.positionChanged.connect(self.videoPlayer.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.videoPlayer.durationChanged)
          
        self.audioOut = QAudioOutput()  ## 6
        self.mediaPlayer.setAudioOutput(self.audioOut)  ## 6   
   
### -----------------------------------------------------------------
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
                time.sleep(.01) 
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
 
    def setBackDrop(self):  
        if self.backdrop != None:
            self.videoPlayer.scene.removeItem(self.backdrop)
            self.backdrop = None
            time.sleep(.05) 
        self.setPosition(0)
        self.mediaPlayer.pause()
        QTimer.singleShot(300,self.copyFrame) ## at least this much for qt5
   
    def copyFrame(self): 
        hgt = HGT if self.videoPlayer.sliderVisible == True else HGT-PAD
        pix = self.videoPlayer.view.grab(QRect(QPoint(0,0),QSize(self.videoPlayer.width()-WID, self.videoPlayer.height()-hgt)))
        self.backdrop = QGraphicsPixmapItem(QPixmap(pix.toImage())) 
        self.backdrop.setZValue(0)  ## set to 300 to test - to make sure it's there
        # self.backdrop.setOpacity(.50)  ## also for test
        self.videoPlayer.scene.addItem(self.backdrop)
        
### --------------------------------------------------------         
class VideoPlayer(QWidget): 
### -------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Video Player Two")
                
        self.setMinimumHeight(MinHgt);   self.setMinimumWidth(MinWid)
        self.setMaximumHeight(MaxHgt);   self.setMaximumWidth(MaxWid)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.resize(int(ViewH*1.5)+WID, ViewH+HGT)  ## default 3:2
                 
        self.setStyleSheet("QGraphicsView {\n"  ## seems to work better positioned here
            "background-color: black;\n"
            "border: 1px solid rgb(125,125,125);\n"
            "color: rgb(125,125,125);\n"
            "}")

        self.scene = QGraphicsScene(self)   
        self.view = QGraphicsView(self.scene)

        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
         
        self.init()
        
        self.sliderVisible = True  ## initial
    
        vbox = QVBoxLayout() 
          
        vbox.addWidget(self.view, Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(self.setButtons(), Qt.AlignmentFlag.AlignCenter)
        if self.sliderVisible == True:
            vbox.addWidget(self.setSlider(), Qt.AlignmentFlag.AlignCenter) 
            
        self.setLayout(vbox)         
     
        x = QGuiApplication.primaryScreen().availableGeometry().center().x()
        self.move(x-int((ViewW+WID)/2), int(HorzH)) 
        
        self.setAcceptDrops(True)  
        self.grabKeyboard() 
                                                     
        self.show()
        
### --------------------------------------------------------
    def init(self):
        self.fileName = ''
        self.path = ''
        self.aspect = 0.0
        self.videoWidth = 0.0 
        self.saveW = self.width()
        self.saveH = self.height()
        self.loopSet = False 
        self.save = QPoint()
        self.videoItem = None
        self.mediaPlayer = None
        self.flag = False

    def dragEnterEvent(self, e):  
        if e.mimeData().hasUrls():   
            m = e.mimeData()
            fileName = m.urls()[0].toLocalFile() 
            self.setMediaPlayer(fileName)
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
            self.playVideo() 
            
        elif key == Qt.Key.Key_S and mod & Qt.KeyboardModifier.ShiftModifier:
            self.toggleSlider()
            
        elif key in (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape):
            self.bye()
        
    def mousePressEvent(self, e):  
        self.save = e.globalPosition()
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
        e.accept()
        
    def mouseDoubleClickEvent(self, e): 
        if self.fileName != '':  
            self.msgbox(self.fileName + '\n' + 'aspect: ' + str(self.aspect))
        e.accept()

    def closeEvent(self, e):
        self.bye()
        e.accept()
        
### --------------------------------------------------------
    def openFile(self):
        self.loopSet = False 
        self.closeMediaPlayer()
        self.init()
  
        if len(sys.argv) > 1:
            self.path = sys.argv[1]
        elif self.path == '':   ## can be set on open
            self.path = os.getcwd()  
                   
        try:    
            fileName, _ = QFileDialog.getOpenFileName(self, "Select Media", \
                self.path, "Video Files (*.mov *.mp4)")   
        except:
            self.msgbox('error opening file')
            return    
        if fileName != '':
            time.sleep(.05)
            self.setMediaPlayer(fileName)
        else:
            self.msgbox('nothing selected')
            return
        
    def setMediaPlayer(self, fileName):
        self.mediaPlayer = MediaPlayer(self, fileName)
        if self.mediaPlayer == None:
            return
        self.videoItem = self.mediaPlayer.videoItem       
        if self.setAspectRatio(fileName):
            self.fileName = fileName  
            self.scene.addItem(self.videoItem)
            self.mediaPlayer.setBackDrop()
        else:
            return
    
    def setAspectRatio(self, fileName):
        asp, width, height = 0, 0, 0
        try:
            width, height = self.getMetaData(fileName)
        except:   
            None        
        if width > 0 and height > 0: 
            asp = math.floor((width/height) * 100)/100.0
            self.setVideoSize(asp)
            return True
        else:
            self.msgbox("setAspectRatio: error reading getMetaData")
            return False
     
    def setVideoSize(self, asp):
        self.Flag = True
        hgt = HGT if self.sliderVisible == True else HGT-PAD
        if asp > 1.0:  
            self.videoItem.setSize(QSizeF(ViewH*asp, ViewH))
            self.resize(int(ViewH*asp)+WID, ViewH+hgt)        
        else:
            height = int((VertW-WID)/asp)+hgt ## use default vertical width - pardon the fudge factor
            self.videoItem.setSize(QSizeF(VertW-WID, (height-hgt)-5))
            self.resize(VertW, height-5)  
        time.sleep(.05)
        self.moveAndSet(asp)
        
    def moveAndSet(self, asp):
        x = QGuiApplication.primaryScreen().availableGeometry().center().x()
        y = VertH if asp < 1.0 else HorzH
        self.move(x - int(self.width()/2), y)            
        self.aspect = asp  ## this way it's 0 and doesn't trigger a resize event
        self.videoWidth = self.videoItem.size().width()   
        self.saveW, self.saveH = self.width(), self.height() 
   
    def toggleSlider(self):
        self.flag = True
        if self.sliderVisible and self.height() > MinHgt+PAD:  ## otherwise it gaps under 30px
            self.sliderVisible = False  
            self.slider.hide()
            self.resize(self.width(), self.height()-PAD)
            time.sleep(.05)      
        elif self.sliderVisible == False:
            self.slider.show()
            self.sliderVisible = True
            self.resize(self.width(), self.height()+PAD)
            time.sleep(.05)
              
### --------------------------------------------------------   
    def resizeEvent(self, e):
        if self.flag == True:
            self.flag = False
            return 
        elif self.aspect > 0: 
    
            hgt = HGT if self.sliderVisible == True else HGT-PAD
            
            width  = int((self.height()-hgt) * self.aspect)+WID
            height = int((self.width()-WID) / self.aspect)+hgt  
            maxwid = int((MaxHgt-hgt) * self.aspect)+WID  
            which  = self.getDirection()
            
            self.mediaPlayer.backdrop.setScale((self.width()-WID)/self.videoWidth) 

            if width != self.saveW:         
                if width > maxwid:
                    self.videoItem.setSize(QSizeF(float(maxwid-WID), float(height-hgt)))
                    self.resize(maxwid, height)
         
                elif width < MinWid: 
                    if self.aspect != 1.0:  
                        self.videoItem.setSize(QSizeF(float(MinWid-WID), float(height-hgt)))
                        self.resize(MinWid, height) 
                    else:   ## square
                        self.videoItem.setSize(QSizeF(float(MinWid-WID), float(MinHgt-hgt)))                      
                        self.resize(MinWid, MinHgt) 
         
                elif which in ('botleft', 'botright'):   
                    self.videoItem.setSize(QSizeF(float(self.width()-WID), float(height-hgt)))          
                    self.resize(self.width(), height)  
                          
                else:
                    self.videoItem.setSize(QSizeF(float(width-WID), float(self.height()-hgt)))
                    self.resize(width, self.height())
                             
            elif height != self.saveH: 
                if height > MaxHgt:
                    self.resize(maxwid, MaxHgt) 
                   
                elif height < MinHgt:
                    self.resize(width, MinHgt-hgt)
                    
                else:
                    self.videoItem.setSize(QSizeF(float(self.width()-WID), float(height-hgt)))
                    self.resize(self.width(), height) 
             
            dif = int((self.width() - self.saveW)/2)
            self.move(self.pos().x()-dif, self.pos().y()) 
              
            time.sleep(.007)  
            self.saveW, self.saveH = self.width(), self.height()        
        e.accept() 
                                   
    def getDirection(self):  ## left out top, topleft and topright - feel free to add them
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
    
### ------------------------------------------------------             
    def closeMediaPlayer(self):
        if self.mediaPlayer != None:
            self.mediaPlayer.stopVideo() 
            time.sleep(.05)  
            self.looperOff()
            self.scene.removeItem(self.mediaPlayer.backdrop)
            self.scene.removeItem(self.videoItem) 
            self.mediaPlayer = None 
            time.sleep(.05)
                 
    def looper(self): 
        if self.loopSet == False:
            self.loopSet = True
            self.loopButton.setText('LoopOn')
            self.stopButton.setEnabled(False)  
            time.sleep(.05)        
        elif self.loopSet == True:
            self.looperOff()
            if self.mediaPlayer != None:
                self.mediaPlayer.stopVideo()
            time.sleep(.05)
            
    def looperOff(self):
        self.loopSet = False
        self.loopButton.setText('Loop')
        self.stopButton.setEnabled(True)
            
    def msgbox(self, str):
        msg = QMessageBox()
        msg.setText(str)
        msg.exec() 
  
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
        self.scene.clear()  
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
           
        self.openButton = QPushButton("Files")
        self.playButton = QPushButton("Play")  
        self.loopButton = QPushButton("Loop")
        self.stopButton = QPushButton("Stop")
        self.byeButton  = QPushButton("Quit")
        
        self.openButton.clicked.connect(self.openFile)
        self.playButton.clicked.connect(self.playVideo)
        self.loopButton.clicked.connect(self.looper)
        self.stopButton.clicked.connect(self.stopVideo)
        self.byeButton.clicked.connect(self.bye)
    
        hbox = QHBoxLayout(self)
              
        hbox.addWidget(self.openButton)  
        hbox.addWidget(self.playButton)      
        hbox.addWidget(self.loopButton)    
        hbox.addWidget(self.stopButton)  
        hbox.addWidget(self.byeButton)
       
        self.buttonGroup.setLayout(hbox)
        self.buttonGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
        self.buttonGroup.setLineWidth(1)
        
        hbox = QHBoxLayout(self)
        hbox.addWidget(self.buttonGroup)
 
        self.bGroup = QLabel()
        self.buttonGroup.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.bGroup.setFixedHeight(60)
        self.bGroup.setLayout(hbox)
      
        return self.bGroup

### -------------------------------------------------------- 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    videoPlayer = VideoPlayer()
    sys.exit(app.exec())
    
    
### ---------------------- that's all ---------------------- 

            
         
            