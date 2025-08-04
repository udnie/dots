
import sys
import os
import math

from functools          import partial

from PyQt6.QtCore       import Qt, QPoint, QPointF, QTimer
from PyQt6.QtGui        import QImage, QPixmap, QGuiApplication, QFont, QColor
from PyQt6.QtWidgets    import QWidget, QApplication, QGraphicsView, \
                                QGraphicsScene, QGraphicsPixmapItem, QLabel, \
                                QHBoxLayout,  QVBoxLayout, QPushButton, QMessageBox, \
                                QFileDialog, QFrame, QGraphicsTextItem, QTableWidget, \
                                QTableWidgetItem, QAbstractItemView

### --------------------------------------------------------
Path = ''       ## set a default directory
SetY = 175      ## Y position of slideShow   

Hpad = 60       ## padding for buttons added to height
CutOff = 550    ## when to stop showing text 
Ext = (".tif", ".png", ".jpg", ".jpeg", ".webp")

Buttons   = True   ## true adds setButtons to layout
Frameless = False  ## sets windowhint to frameless - see comment on qt5 and frameless
OneColor  = False  ## sets frame same as background

### --------------------------------------------------------
Width, Height     = 1200,  750   ## choose one you like and delete the rest
ViewW, ViewH      = 1150,  700
MaxW, MaxH, MaxV  =  950,  500, 550 

# Width, Height     = 1500, 1000  ## widget size  
# ViewW, ViewH      = 1450,  950  ## scene size
# MaxW, MaxH, MaxV  = 1200,  650, 800 

# Width, Height     = 1450,  900  
# ViewW, ViewH      = 1350,  850
# MaxW, MaxH, MaxV  = 1150,  625, 725 
 
# Width, Height     = 1350,  850  
# ViewW, ViewH      = 1300,  800 
# MaxW, MaxH, MaxV  = 1100,  550, 650  

### --------------------------------------------------------
helpMenuKeys = {  ## help menu - 'H' or button
    'C':                'Clear Screen',  
    'F ':               'File Chooser', 
    'H ':               'Help Menu On/Off',
    'Right Arrow, N':   'Next Slide',
    'Left Arrow, B':    'Previous Slide',
    'O':                'Opening Layout',
    'R, L':             'Rotate 90.0',
    'S, SpaceBar':      'Slide Show',
    'T':                'Text On/Off',   
    'W':                'Where am I?', 
    '>,  +,  ]':          'Scale Up',
    '<,  _,  [':          'Scale Down',
    'X, Q, Escape':     'Quit/Exit',
}

SharedKeys = ('B','C','F','H','N','O','R','L','S','T','W','X','[',']')

### --------------------- slideShow.py ---------------------
''' slideShow.py: reads .png, .jpg, .jpeg, .tif, .tiff, and .webp.
    '>' ,'+', ']' scales up,  '<', '_', scales down'''
### --------------------------------------------------------
class SlideShow(QWidget): 
### --------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__()
    
        self.setWindowTitle("SlideShow")
            
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(0, 0, ViewW, ViewH)
         
        self.view.setScene(self.scene)                 

        self.view.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)     
        self.view.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus);  self.setFocus()
        
        self.ctr = QGuiApplication.primaryScreen().availableGeometry().center()    
        x = int(((self.ctr.x() * 2 ) - Width)/2)
     
        if OneColor:   ##  makes widget one color
            self.setStyleSheet("QWidget {\n" 
                "background-color: rgb(250,250,250);\n"
                "border: 1px solid rgb(250,250,250);\n"
                "color: rgb(250,250,250);\n"      
                "}")
        
        ## in qt5 framelessWindow won't resize with mouse - use zoom keys instead
        if Frameless:  ## set WindowHint to Frameless
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
   
        H = Height
        if Buttons: H = Height + Hpad
        self.setGeometry(x, SetY, Width, H)  
  
        self.init()
        
        self.delay   = 2000  ## slide show timer
        self.setTags = True  ## toggle textItems on/off
  
        vbox = QVBoxLayout()      
        vbox.addWidget(self.view)
        if Buttons: vbox.addWidget(self.setButtons())  ## true adds setButtons to layout
        self.setLayout(vbox)
    
        self.grabKeyboard()
        
        QTimer.singleShot(25, self.fileChooser) if Buttons == False else \
              QTimer.singleShot(25, self.openFiles)

        self.show()
             
### --------------------------------------------------------
    def init(self):  ## on each new directory
        self.files       = []   
        self.txtlst     = []
        self.rotters    = {}
        self.fileName    = ''
        self.path       = Path
        self.current    = 0
        self.rot        = 0
        self.running    = False  ## used by slideshow
        self.save       = QPointF()
        self.pixItem    = None 
        self.textItem   = None
        self.helpMenu   = None
        self.helpFlag   = False
 
### --------------------------------------------------------
    def keyPressEvent(self, e):  
        key = e.key()
        mod = e.modifiers()  
           
        if key in (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape):
            self.shared('X')
            
        elif key in (Qt.Key.Key_N, Qt.Key.Key_Right):
            self.shared('N')   
            
        elif  key in (Qt.Key.Key_B, Qt.Key.Key_Left):
            self.shared('B')   
            
        elif key == Qt.Key.Key_Space:
            self.shared('Space')
            
        elif key == Qt.Key.Key_BracketRight or mod & Qt.KeyboardModifier.ShiftModifier \
            and key in (Qt.Key.Key_Greater, Qt.Key.Key_Plus):
                self.shared(']')
                
        elif key == Qt.Key.Key_BracketLeft or mod & Qt.KeyboardModifier.ShiftModifier \
            and key in (Qt.Key.Key_Less, Qt.Key.Key_Underscore):
                self.shared('[')                    
        else: 
            try:
                key = chr(key) 
            except: 
                return                     
        if key in SharedKeys:
            self.shared(key)
            
    def shared(self, key): 
        match key:   
            case 'B': 
                self.backOne()
            case 'C':
                self.clearScene()   
            case 'F': 
                self.fileChooser()   
            case 'H':
                self.openHelpMenu()        
            case 'R' | 'L':
                self.rotateThis(90)
            case 'N':
                self.nextSlide()          
            case 'O':
                self.openingLayout()       
            case 'S' | 'Space':
                self.slideShow()    
            case 'T':
                self.toggleText()   
            case 'W':
                if self.path != '': self.msgbox(self.path)        
            case 'X':
                self.clearScene();  
                self.close()  
            case ']':
                self.zoom(1.05)  
            case '[':    
                self.zoom(0.95)
            case _:
                return

### --------------------------------------------------------          
    def mousePressEvent(self, e):
        self.save = e.globalPosition()  
        if e.button() == Qt.MouseButton.RightButton:
            self.openHelpMenu() 
        else:
            self.closeHelpMenu()
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
      
### --------------------------------------------------------       
    def addPixmap(self, file):  ## the scene is cleared each new file  
        if self.pixItem != None:
            self.scene.removeItem(self.pixItem)
            del self.pixItem
            
        if self.helpMenu != None: self.closeHelpMenu()  ## close help menu   
              
        self.fileName = self.path + '/' + file  
        try:
            img = QImage(self.fileName) 
        except:
            self.msgbox('addPixMap: problem with ' + file)
            return
      
        self.scaleW = self.view.width()/ViewW
        self.scaleH = self.view.height()/ViewH   
                
        maxH = MaxH   
        self.txtlst = [file, img.width(), img.height()]  ## save it for textItem
        if rot := self.rotters.get(file): 
            self.rot = rot
                                           
        if self.rot in (90, 270) and abs(img.width() - img.height()) > 5: ## swap width to height for rotation
            img = img.scaled(int(MaxV * self.scaleH), int(MaxH * self.scaleH),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation) 
        else:
            if img.height() > img.width() and abs(img.width() - img.height()) > 5:
                maxH = MaxV  
        
            img = img.scaled(int(MaxW * self.scaleW), int(maxH * self.scaleH),
                Qt.AspectRatioMode.KeepAspectRatio,       
                Qt.TransformationMode.SmoothTransformation)  
          
        self.pixItem = QGraphicsPixmapItem()          
        self.pixItem.setPixmap(QPixmap(img))  
        
        self.pixItem.setZValue(0)
        self.pixItem.setPos(self.pixXY())
        
        self.setOrigin()             
        self.pixItem.setRotation(self.rot) 
        self.pixItem.setScale(1.0)
        
        self.scene.addItem(self.pixItem)
        if self.setTags == True and self.view.height() > CutOff:   
            self.addTextItem()           
        del img
        self.update()   
        
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
     
    def pixXY(self):     
        self.setScene()                                                                                                                                                                       
        x = int((self.view.width() - self.pixItem.boundingRect().width())/2)
        y = int((self.view.height() - self.pixItem.boundingRect().height())/2)   
        return QPointF(x, y)

    def setScene(self):
        self.scene.setSceneRect(0, 0, self.view.width(), self.view.height())
        
    def zoom(self, zoom):
        if self.pixItem != None:           
            if self.width() *zoom > 1920 or self.height() * zoom < 350:
                return    
            self.setScene()     
            p, width = self.pos(), self.width()        
            self.resize(int(self.width() * zoom), int(self.height() * zoom)) 
            dif = int((self.width() - width)/2) 
            self.move(p.x()-dif, p.y())

    def resizeEvent(self, e):  
        if self.pixItem != None:  
            self.pixItem.setScale(self.scaleW)  
            self.addPixmap(self.files[self.current])   
        e.accept()       
                 
    def openingLayout(self):
        if self.pixItem != None:
            self.setScene() 
            x, H = int(((self.ctr.x() * 2 ) - Width)/2), Height
            if Buttons: H = Height + Hpad
            self.setGeometry(x, SetY, Width, H) 
            self.addPixmap(self.files[self.current])  ## refresh  
       
### --------------------------------------------------------                  
    def rotateThis(self, r=0):
        if self.pixItem != None:  
            r = r + self.rot
            if r > 270: r = 0
            self.rot = r
            self.rotters[self.txtlst[0]] = self.rot 
            self.addPixmap(self.files[self.current])  ## refresh  
                                 
    def nextSlide(self):
        if length := len(self.files):
            if self.current >= 0 and self.current < length:
                self.current += 1
                if self.current == length:  ## wrap it
                    self.current = 0   
            self.rot = 0
            self.addPixmap(self.files[self.current])
            
    def backOne(self):
        if length := len(self.files):
            if self.current >= 0 and self.current <= length:
                self.current -= 1
                if self.current < 0:
                    self.current = length -1
            self.rot = 0
            self.addPixmap(self.files[self.current])
   
### --------------------------------------------------------
    def addTextItem(self):   
        if self.textItem != None:
            self.scene.removeItem(self.textItem)
            del self.textItem       
        self.textItem = self.tagIt()   
        if self.textItem == None: 
            return         
        self.textItem.setZValue(100) 
        self.textItem.setPos(self.textXY()) 
        self.scene.addItem(self.textItem)
        
    def textXY(self):   
        self.setScene()  
        w, W = self.textItem.boundingRect().width(),  int(self.width())  
        h, H = self.textItem.boundingRect().height(), int(self.height()) 
        x, y = int((W - w)/2), int(H-h)
        if Buttons: 
            y = y - 105
        else:
            y = y - 50
        return QPointF(x-15, y)
    
    def updTextItem(self):
        if self.setTags == True and self.textItem != None:
            if int(self.view.height()) > CutOff: 
                self.textItem.setPos(self.textXY()) 
    
    def tagIt(self):   
        try:
            file, width, height = self.txtlst[0], self.txtlst[1], self.txtlst[2]   
            asp = math.floor(width/height *100)/100.0  
        except:
            self.msgbox('tagIt: problem with ' + file)
            return None
        if self.rot in (90, 270):  ## recalc for rotation
            asp = math.floor(height/width *100)/100.0    
            s = (f"{file}   {(height)}X{int(width)}   asp {asp}")           
        else:
            s = (f"{file}   {int(width)}X{int(height)}   asp {asp}")   
        textItem = QGraphicsTextItem(s.strip())
        font = QFont("Arial", 14)
        textItem .setFont(font)
        return textItem
    
    def toggleText(self):   
        if self.pixItem != None:    
            if self.setTags == False:
                self.setTags = True
                self.addTextItem()
            elif self.textItem != None:
                self.scene.removeItem(self.textItem)
                self.textItem = None
                self.setTags = False
                    
### --------------------------------------------------------         
    def clearScene(self):
        self.closeHelpMenu()
        self.scene.clear()  
        self.init() 
            
    def msgbox(self, str):
        msg = QMessageBox()
        msg.setText(str)
        timer = QTimer(msg)
        timer.setSingleShot(True)
        timer.setInterval(5000)
        timer.timeout.connect(msg.close)
        timer.start()
        msg.exec() 
                                            
    def setOrigin(self):   
        b = self.pixItem.boundingRect()
        op = QPointF(b.width()/2, b.height()/2)
        self.pixItem.setTransformOriginPoint(op)
        self.pixItem.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
                                                                                                                 
    def slideShow(self):     
        self.showtime() if self.running == False else self.timerStop()
      
    def showtime(self):
        self.running = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.nextSlide)
        self.timer.start(self.delay)
  
    def timerStop(self):
        self.timer.stop()
        self.running = False
        
### --------------------------------------------------------
    def fileChooser(self):
        if path := self.selectDirectory():
            self.path = path
            self.openFiles(path)
                          
    def openFiles(self, path=''):
        self.clearScene()  ## calls self.init() 
        if path != '':  
            os.chdir(path);  self.path = os.getcwd() 
        if list := self.getPathList():      
            files = self.getFileNames(list)
            if files != None:
                self.files = sorted(files)
                self.addPixmap(self.files[0]) 
                if len(self.files) == 1:
                    self.msgbox('openFiles: Only One Matching File')
        
    def selectDirectory(self):
        path = QFileDialog.getExistingDirectory(self, '')
        if path == None or path == '':
            path = os.getcwd()
        os.chdir(path)
        return os.getcwd()
                            
    def getPathList(self):
        if len(sys.argv) > 1:  ## set starting directory
            self.path = sys.argv[1]
        elif self.path == '':
            self.path = os.getcwd()  
        else:
            files = os.listdir(self.path)  ## path set with default directory
            return files
       
    def getFileNames(self, files):       
        filenames = []
        for file in files: 
            path = os.path.join(self.path, file)
            if os.path.isdir(path):  ## ignore directories
                continue  
            file = file.lower(); 
            if file[file.rfind('.'):] in Ext:                  
                filenames.append(file)
        if len(filenames) == 0:
            self.msgbox('getFileNames: No Files Found')
            return None
        return filenames
                                         
### --------------------------------------------------------    
    def setButtons(self): 
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedHeight(50)
  
        self.buttonGroup.setStyleSheet("QPushButton {\n"               
            "max-width:   200px;\n"
            "max-height:   40px;\n"  ## 30 must be the default
            "font-size:    13px;\n"
            "}")   
        
        self.filesBtn = QPushButton("Files")  
        self.helpBtn = QPushButton("Help")
        self.clearBtn = QPushButton("Clear")
        self.quitBtn = QPushButton("Quit")        
          
        self.filesBtn.clicked.connect(self.fileChooser)
        self.helpBtn.clicked.connect(lambda: self.shared('H'))
        self.clearBtn.clicked.connect(self.clearScene)
        self.quitBtn.clicked.connect(lambda: self.shared('X'))
        
        hbox = QHBoxLayout(self)
        hbox.addSpacing(50)       
        hbox.addWidget(self.filesBtn)
        hbox.addSpacing(50)        
        hbox.addWidget(self.helpBtn)
        hbox.addSpacing(50)       
        hbox.addWidget(self.clearBtn)
        hbox.addSpacing(50)
        hbox.addWidget(self.quitBtn)
            
        self.buttonGroup.setLayout(hbox)
        self.buttonGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
        self.buttonGroup.setLineWidth(1)
  
        return self.buttonGroup
### --------------------------------------------------------     
class Help(QWidget): 
### -------------------------------------------------------- 
    def __init__(self, parent): 
        super().__init__()  
        
        self.parent = parent
         
        self.table = QTableWidget()
        self.table.setRowCount(len(helpMenuKeys)+1)
        self.table.setColumnCount(2)
     
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
      
        self.table.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) 
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        self.table.setHorizontalHeaderLabels(["Key", "Function"])
        stylesheet = "::section{Background-color: lightgray; font-size:14px;}"
        self.table.horizontalHeader().setStyleSheet(stylesheet)
        
        self.table.setStyleSheet('QTableWidget{\n'   
            'background-color: rgb(250,250,250);\n'                 
            'font-size: 13pt;\n' 
            'font-family: Arial;\n' 
            'border: 3px solid dodgerblue;\n'
            'gridline-color: silver;}') 
                                                                                                             
        self.table.setColumnWidth(0, 130) 
        self.table.setColumnWidth(1, 130)

        width, height = 267, 451  
        self.table.setFixedSize(width, height)  
        
        self.table.verticalHeader().setVisible(False) 
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        self.table.itemClicked.connect(self.clicked)   
         
        row = 0
        for k,  val in helpMenuKeys.items():
            item = QTableWidgetItem(k)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item)
            item = QTableWidgetItem(val)
            self.table.setItem(row, 1, item)      
            row += 1
                  
        item = QTableWidgetItem("Enter 'H' or Click Here to Close")
        item.setBackground(QColor('lightgray'))
        item.setFont(QFont("Arial", 14))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.table.setSpan(row, 0, 1, 2)  
        self.table.setItem(row, 0, item)   
        
        p, pwidth, pheight = self.parent.pos(), self.parent.width(), self.parent.height()
        
        x = int(p.x() + (pwidth/2)) - int(width/2)   
        y = int(p.y() + (pheight/2)) - int(height/2)   
        
        self.table.move(x,y)  
        self.table.show()
        
    def clicked(self):
        help = self.table.item(self.table.currentRow(), 0).text().strip()
        match help: 
            case 'S, SpaceBar':  
                help = 'S'
            case 'R, L':        
                help = 'R'
            case 'Right Arrow, N':
                help = 'N'
            case 'Left Arrow, B': 
                help = 'B'               
            case '>,  +,  ]':
                help = ']'
            case '<,  _,  [':  
                help = '['
            case 'X, Q, Escape':
                help = 'X'     
        if help in SharedKeys:
            try:
                QTimer.singleShot(25, partial(self.parent.shared, help))
            except:
                None
        self.tableClose()
            
    def tableClose(self):
        self.parent.helpFlag = False 
        self.table.close()
 
### -------------------------------------------------------- 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    slides = SlideShow()
    sys.exit(app.exec())

### ---------------------- that's all ----------------------
    

 

     