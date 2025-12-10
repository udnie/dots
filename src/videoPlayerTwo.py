
import os
import sys
import time
import math  

### ------------------ videoPlayerTwo.py ------------------- 
''' Updated to reflect videoPlayerOne without resize keys and aspect
    button. Uses a GraphicsVideoItem which I refresh along with 
    the mediaPlayercfor each new file - unlike videoPlayerOne.'''
### -------------------------------------------------------- 

from PyQt6.QtCore       import Qt, QUrl, QTimer, QPoint, QSizeF, QRect, QSize
from PyQt6.QtGui        import QGuiApplication, QPixmap
from PyQt6.QtWidgets    import QWidget, QVBoxLayout, QApplication, \
                                QSizePolicy,  QGraphicsView, QGraphicsScene, \
                                QFileDialog, QGraphicsPixmapItem
                                                                        
from PyQt6.QtMultimedia         import QMediaPlayer,  QAudioOutput
from PyQt6.QtMultimediaWidgets  import QGraphicsVideoItem

# from PyQt6.QtMultimedia          import QMediaContent   ## 5

from videoClipsMaker     import Clips
from videoClipsWidget    import *
from videoPlayerShared   import *

### --------------------------------------------------------   
class MediaPlayer(QMediaPlayer): 
### --------------------------------------------------------
    def __init__(self, parent, fileName):
        super().__init__()
        
        self.parent = parent
        self.backdrop = None
     
        self.mediaPlayer = QMediaPlayer(self) ## 6
        # self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)  ## 5 
        try:
            self.mediaPlayer.setSource((QUrl.fromLocalFile(fileName)))  ## 6
            # self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(fileName))))  ## 5  
        except:
            self.parent.shared.msgbox('error setting mediaPlayer')
            return None
        
        self.videoItem = QGraphicsVideoItem()   
        self.mediaPlayer.setVideoOutput(self.videoItem)
        
        self.videoItem.setZValue(100)
        self.videoItem.setSize(QSizeF(float(ViewH*1.5), float(ViewH)))  
        self.videoItem.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
          
        self.mediaPlayer.mediaStatusChanged[QMediaPlayer.MediaStatus].connect(self.mediaStateChanged) 
  
        if self.parent.sliderVisible:  ## you'll need to load a file to kickstart the slider if it won't move
            self.mediaPlayer.positionChanged.connect(self.parent.shared.positionChanged)
            self.mediaPlayer.durationChanged.connect(self.parent.shared.durationChanged)
          
        self.audioOut = QAudioOutput()  ## 6
        self.mediaPlayer.setAudioOutput(self.audioOut)  ## 6   
   
### -----------------------------------------------------------------
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
                time.sleep(.01) 
            self.stopVideo() 

    def stopVideo(self):   
        if self.parent.loopSet == False: 
            self.mediaPlayer.stop()
            self.setPosition(0) 
            self.mediaPlayer.pause() 
            self.parent.playButton.setText('Play')
            time.sleep(.03)
        else:   
            self.playVideo()  ## loop it

    def setPosition(self, position):  ## from videoPlayer by finger pull
        self.mediaPlayer.setPosition(position)
 
    def setBackDrop(self):  
        if self.backdrop != None:
            self.parent.scene.removeItem(self.backdrop)
            self.backdrop = None
            time.sleep(.03) 
        self.setPosition(0)
        self.mediaPlayer.pause()
        QTimer.singleShot(300,self.copyFrame) ## at least this much for qt5
   
    def copyFrame(self): 
        hgt = HGT if self.parent.sliderVisible == True else HGT-PAD
        pix = self.parent.view.grab(QRect(QPoint(0,0),QSize(self.parent.width()-WID, self.parent.height()-hgt)))
        self.backdrop = QGraphicsPixmapItem(QPixmap(pix.toImage())) 
        self.backdrop.setZValue(0)  ## set to 300 to test - to make sure it's there
        # self.backdrop.setOpacity(.50)  ## also for test
        self.parent.scene.addItem(self.backdrop)
        
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
        self.clips = Clips(self)
        self.shared = Shared(self)
   
        self.sliderVisible = True 
        
        if len(sys.argv) > 1: 
            self.path = sys.argv[1]
    
        vbox = QVBoxLayout() 
          
        vbox.addWidget(self.view, Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(setButtons(self), Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(setSlider(self), Qt.AlignmentFlag.AlignCenter) 
            
        self.setLayout(vbox)         
        
        self.shared.openPlayer(self.key)   ## <<----->> open full frame - 3:2]  
          
        x = QGuiApplication.primaryScreen().availableGeometry().center().x()
        self.move(x-int((ViewW+WID)/2), int(HorzH)) 
        
        self.setAcceptDrops(True)  
        self.grabKeyboard() 
                                                     
        self.show()
        
        # QTimer.singleShot(50, self.shared.toggleSlider)  ## hides slider on open
        
### --------------------------------------------------------
    def init(self):
        self.fileName = ''
        self.key = 'F'  ## only place it's used - change default open format
        self.path = ''
        self.player = 'two'
        self.aspect = 0.0
        self.videoWidth = 0.0 
        self.loopSet = False 
        self.helpFlag = False 
        self.helpMenu = None
        self.videoItem = None
        self.mediaPlayer = None
        self.saveW = self.width()
        self.saveH = self.height()
        self.save = QPoint()   
        self.flag = False
  
    def dragEnterEvent(self, e):  
        if e.mimeData().hasUrls():   
            m = e.mimeData()
            fileName = m.urls()[0].toLocalFile() 
            self.setMediaPlayer(fileName)
            self.shared.playVideo() if self.clips.PlayVideo else \
                self.mediaPlayer.pause()  
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
                    self.clips.looper(self)  
                case 'Settings':
                    self.clips.toggleSettings(self)  ## clipMaker settings
                case 'C':
                    self.shared.closeHelpMenu()  ## improvised clear
                    if self.mediaPlayer:
                        self.mediaPlayer.stop()        
                case 'Clips':     
                    self.shared.openDirectory()  ## if MakeClipsOn sets path to folder
                case 'Shift-S':
                    self.shared.toggleSlider()
                case 'X' | 'Q':
                    self.bye()   
                case _:
                    return
    
### -------------------------------------------------------                     
    def mousePressEvent(self, e):  
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
        e.accept()
        
    def mouseDoubleClickEvent(self, e): 
        if self.fileName != '':  
            self.shared.msgbox(self.fileName + '\n' + 'aspect: ' + str(self.aspect))
        e.accept()

    def closeEvent(self, e):
        self.bye()
        e.accept()
        
### --------------------------------------------------------
    def openFile(self):  ## from button - "two"
        self.shared.closeMediaPlayer()
        self.init()
        if self.path == '':   ## can be set on open
            self.path = os.getcwd()               
        try:    
            fileName, _ = QFileDialog.getOpenFileName(self, "Select Media", \
                self.path, "Video Files (*.mov *.mp4 *.mp3 *.m4a *.wav)")
        except:
            self.shared.msgbox('error opening file')
            return      
        if fileName != '':
            time.sleep(.03)
            self.setMediaPlayer(fileName)
        else:
            return
        
    def setMediaPlayer(self, fileName, where=''):  ## each new file opened - "two"
        self.mediaPlayer = MediaPlayer(self, fileName)
        if self.mediaPlayer == None:
            self.shared.msgbox('error opening mediaplayer')
            return
        self.videoItem = self.mediaPlayer.videoItem   
        if where == '':
            if self.shared.setAspectRatio(fileName):
                self.shared.addToScene(fileName)  
        elif where == 'assembler':  ## bypasses setAspectRatio if from assembler
            hgt = HGT if self.sliderVisible == True else HGT-PAD   
            self.videoItem.setSize(QSizeF(float(self.width()-WID), float(self.height()-hgt)))
            self.shared.addToScene(fileName)  
                                      
    def setDisplaySize(self, key):  ## - "two"
        self.flag, height = True, 0
        hgt = HGT if self.sliderVisible == True else HGT-PAD 
        if key in AspKeys:
            self.videoItem.setSize(QSizeF(self.ViewH*self.aspect, self.ViewH))
            self.resize(self.ViewW+WID, self.ViewH+hgt) 
        elif self.aspect >= 1.0:  ## use default height for horizontal 
            self.videoItem.setSize(QSizeF(ViewH*self.aspect, ViewH))
            self.resize(int(ViewH*self.aspect)+WID, ViewH+hgt)        
        elif self.aspect < 1.0:
            height = int((VertW-WID)/self.aspect)+hgt ## use default vertical width
            self.videoItem.setSize(QSizeF(VertW-WID, (height-hgt)-5))  ##  pardon the fudge factor
            self.resize(VertW, height-5)  
        if key == 'O':  self.shared.setVideoWH()  ## for assembler - from setDisplaySize
        time.sleep(.03)
        self.shared.moveAndSet()
   
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
            which  = getDirection(self)
            
            if self.mediaPlayer != None:
                self.mediaPlayer.backdrop.setScale((self.width()-WID)/self.videoWidth) if self.mediaPlayer.backdrop \
                else self.shared.msgbox('backdrop not found')
                
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

### ------------------------------------------------------                         
    def setFileName(self, x=''): ## for videoplayerOne
        pass 
                                
    def bye(self):  
        self.shared.closeHelpMenu()   
        self.scene.clear()  ## - "two"
        self.close()    

### -------------------------------------------------------- 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    play = VideoPlayer()
    sys.exit(app.exec())
    
### ---------------------- that's all ---------------------- 

            
         
            