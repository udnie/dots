
import os
import time

from PyQt6.QtCore       import Qt, QUrl, QSizeF, QTimer, QRect, QPoint, QSize  
from PyQt6.QtGui        import QImage, QPixmap                        
from PyQt6.QtWidgets    import QMessageBox
                                
from PyQt6.QtMultimedia         import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets  import QGraphicsVideoItem

# from PyQt5.QtMultimedia           import QMediaContent  ## 5 

from dotsSideGig        import MsgBox
from dotsShared         import common, Ball, paths

### --------------------------------------------------------
class QVD(QGraphicsVideoItem):  ## added type to track it better
### --------------------------------------------------------
     def __init__(self):
          super().__init__()          
         
          self.type = 'video'
          self.fileName = 'Breathless'

### ------------------ dotsVideoPlayer ---------------------        
class VideoPlayer(QMediaPlayer): 
### --------------------------------------------------------
    def __init__(self, parent, fileName='', src='', loops=False):
        super().__init__()

        self.canvas = parent 
        self.scene  = self.canvas.scene
   
        self.fileName = ''
        self.type    = 'video'
        self.tag     = src
        self.loops   = loops
        self.widget  = None 
        self.backdrop = None
        self.loopSet = False
        
        if self.loops:
            self.loopSet = True
            self.canvas.btnLoop.setText('LoopOn')
         
        if fileName != '': self.fileName = os.path.basename(fileName)

        self.mediaPlayer = QMediaPlayer(self)   ## 6
        # self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)  ## 5
      
        self.videoItem = QVD()  ## to add 'type' 
        self.videoItem.setZValue(self.canvas.mapper.toFront(100))  ## sets zValue
        
        self.videoItem.setSize(QSizeF(common['ViewW'], common['ViewH']))    
        self.mediaPlayer.setVideoOutput(self.videoItem) 
           
        self.mediaPlayer.mediaStatusChanged[QMediaPlayer.MediaStatus].connect(self.mediaStateChanged) 
        
        self.mediaPlayer.setSource((QUrl.fromLocalFile(fileName)))  ## 6
        # self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(fileName))))  ## 5
      
        self.audioOut = QAudioOutput()  ## 6
        self.mediaPlayer.setAudioOutput(self.audioOut)  ## 6
        ## del
### -----------------------------------------------------------------
    def playVideo(self):  
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:  ## 6
        # if self.mediaPlayer.state() == QMediaPlayer.PlayingState:  ## 5
            self.mediaPlayer.pause()  
        else: 
            if self.backdrop == None: 
                self.videoItem.setZValue(self.canvas.mapper.toFront(100)) 
                self.setBackDrop() 
                time.sleep(.20) 
            self.mediaPlayer.play()  
 
    def mediaStateChanged(self, status): 
        if status == QMediaPlayer.MediaStatus.EndOfMedia:  
            while not (self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.StoppedState):  ## 6
            # while not (self.mediaPlayer.state() == QMediaPlayer.State.StoppedState):  ## 5
                time.sleep(.01) 
            self.stopVideo() 
             
    def stopVideo(self):
        if self.loopSet == False: 
            self.mediaPlayer.stop()
            self.mediaPlayer.setPosition(0) 
            self.mediaPlayer.pause() 
            self.canvas.btnRun.setText('Run') 
            if self.canvas.animation == False and  \
                self.canvas.openPlayFile not in ('snakes', 'bats', 'hats'):            
                self.canvas.showWorks.enablePlay()  
        elif self.loopSet:
            self.playVideo() 
   
    def setBackDrop(self):   
        self.mediaPlayer.setPosition(0)
        self.mediaPlayer.pause()
        QTimer.singleShot(300, self.copyFrame) 

    def copyFrame(self):      
        pix = self.canvas.view.grab(QRect(QPoint(0,0),QSize(common['ViewW'], common['ViewH'])))
        self.backdrop = Ball(pix.toImage(), self.canvas)  ## subclass - borrowed
        self.backdrop.setZValue(-100)  ## copy is a graphics pixmapItem 
        self.scene.addItem(self.backdrop)    
        self.videoItem.setZValue(-99)  ## reset behind sprites - zval was 100 over topmost sceneitem 
        if self.tag == 'dnd': self.mediaPlayer.play()  
   
    def ask2deleteVideo(self):
        img = QImage(paths['spritePath'] + "doral.png")  ## icon .png
        img = img.scaled(60, 60,  ## keep it small
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)  
        pixmap = QPixmap(img)  
   
        msgbox = QMessageBox()
        msgbox.setIconPixmap(pixmap)
        msgbox.setText("Delete this Video?")
        msgbox.setStandardButtons(msgbox.StandardButton.Yes |msgbox.StandardButton.No)
        answer = msgbox.exec()

        if answer == msgbox.StandardButton.No:
            return 
        self.deleteVideo()
  
    def deleteVideo(self):
        name = os.path.basename(self.canvas.openPlayFile) 
        if name != '':
            fsize = len(self.canvas.showbiz.showRunner.openPlay(self.canvas.openPlayFile))   
        if fsize == 1:  ## only one so delete it
            try:
                os.remove(self.canvas.openPlayFile)     
            except IOError:
                MsgBox('Error deleting file ' + name, 5)
            MsgBox('The file ' + name + ' has been deleted', 7)       
        elif fsize > 1:
            MsgBox('Save the play file to finalize removing the video', 7)
        self.canvas.sideCar.videoOff() 
   
### --------------------------------------------------------          
    def saveVideo(self):      
        tmp = {
            'fileName':      os.path.basename(self.canvas.videoPlayer.fileName),
            'type':         'video',     
            'x':            float(f'{0:.2f}'),
            'y':            float(f'{0:.2f}'),
            'z':            -99,
            'tag':          'Vertigo',
            'locked':       False,
            'loops':        self.loopSet,    
        }
        return tmp
       
### ------------------ dotsVideoPlayer --------------------- 



