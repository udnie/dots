
from PyQt6.QtCore       import Qt, QPointF, QPoint, QRectF
from PyQt6.QtGui        import QColor, QPen, QPainter, QPolygonF
from PyQt6.QtWidgets    import QSlider, QWidget, QGroupBox,   QDial, QGraphicsPolygonItem, \
                               QLabel, QSlider, QHBoxLayout,  QVBoxLayout, QPushButton
    
from dotsShared         import common    
from dotsSideGig        import point
    
V = common['V']  ## the diameter of a pointItem, same as in ShadowWidget       
                                            
### ------------------- dotsShadowWidget -------------------
''' class: ShadowWidget, Works '''
### --------------------------------------------------------
class Works:  ## small functions that were in ShadowMaker
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.maker = parent
        self.scene = self.maker.scene
        
### --------------------------------------------------------
    def resetSliders(self): 
        self.maker.widget.opacitySlider.setValue(int(self.maker.alpha*100))
        self.maker.widget.opacityValue.setText('{0:.2f}'.format((self.maker.alpha)))
        self.maker.widget.scaleSlider.setValue(int(self.maker.scalor*100))
        self.maker.widget.scaleValue.setText('{0:.2f}'.format(int(self.maker.scalor*100)))
        self.maker.widget.rotaryDial.setValue(int(self.maker.rotate))
        self.maker.widget.rotateValue.setText('{:3d}'.format(int(self.maker.rotate)))
         
    def closeWidget(self):
        if self.maker.widget != None:
            self.maker.widget.close()          
            if self.maker.shadow != None and self.maker.linked:
                self.maker.pixitem.key = 'return'  ## trying to fake-out the tag showing      
        self.maker.widget = None  
                                                     
    def cleanUpShadow(self):  
        self.closeWidget()
        self.deletePoints()  
        self.deleteOutline()
        self.removeShadow()
   
    def deleteShadow(self): 
        if self.maker.shadow != None:
            self.cleanUpShadow()
        self.maker.shadow = None
 
    def removeShadow(self):
        if self.maker.shadow != None:
            self.scene.removeItem(self.maker.shadow)
        self.maker.shadow = None 
 
    def hideAll(self):
        if self.maker.isHidden == False:
            self.maker.isHidden = True
            if self.maker.outline != None and \
                self.maker.outline.isVisible() == True:
                self.hideOutline()
        elif self.maker.isHidden == True: 
            self.maker.isHidden = False   
            self.showOutline() 
    
    def addPointsToScene(self):
        for p in self.maker.points:   
            if self.maker.isHidden:
                p.hide()                              
            self.scene.addItem(p)
                             
    def deletePoints(self):  ## the path stays
        for p in self.maker.points:  
            self.scene.removeItem(p) 
            del p
        self.maker.points = [] 
 
    def updateOutline(self): 
        self.deleteOutline()
        self.maker.outline = QGraphicsPolygonItem(self.makeOutline()) 
        self.maker.outline.setPen(QPen(QColor('lime'), 2, Qt.PenStyle.DotLine))
        self.maker.outline.setZValue(common['outline'])       
        if self.maker.linked: ## used throughout shadow and updateShadow
            self.hideOutline()      
        self.addOutline()
                                                                         
    def addOutline(self):
        self.scene.addItem(self.maker.outline)

    def deleteOutline(self): 
        if self.maker.outline != None:
            self.scene.removeItem(self.maker.outline)
        self.maker.outline = None
                      
    def makeOutline(self):  
        outline = QPolygonF()   
        for p in self.maker.path:  
            outline.append(QPointF(p))
        return outline 
                              
    def hidePoints(self, hide=True): 
        for p in self.maker.points:       
            p.hide() if hide == True else p.show()  
                              
    def hideOutline(self):
        if self.maker.outline != None:
            self.maker.outline.hide()
            self.hidePoints()  ## default True       
            
    def showOutline(self):
        if self.maker.outline != None:
            self.maker.outline.setVisible(True)
            self.maker.updatePath(self.maker.shadow.save) 
            self.updateOutline()
            self.maker.outline.show()
            self.hidePoints(False)      
   
    def toggleOutline(self):
        if self.maker.outline != None:
            if self.maker.outline.isVisible() == True:
                self.hideOutline()  
            elif self.maker.outline.isVisible() == False:
                self.showOutline()            
                                                                   
    def rotateShadow(self, val): 
        inc = (val - self.maker.rotate)
        self.maker.rotateScale(0, -inc)
        self.maker.rotate = val
      
    def scaleShadow(self, val): 
        per = (val - self.maker.scalor) / self.maker.scalor    
        self.maker.rotateScale(per, 0)
        self.maker.scalor = val
                                                                                                             
    def pixWidthHeight(self):
        b = self.maker.pixitem.boundingRect()
        return self.maker.pixitem.fileName, b.width(), b.height() 
                                                                                                                                                        
### --------------------------------------------------------        
class ShadowWidget(QWidget): 
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()
                                        
        self.maker = parent                          
        self.works = self.maker.works
        
        self.type = 'widget'
        self.save = QPointF(0.0,0.0)
                
        self.setAccessibleName('widget')
        self.WidgetW, self.WidgetH = 330.0, 225.0
                
        hbox = QHBoxLayout()
        hbox.addWidget(self.sliderGroup())
        hbox.addSpacing(5) 
        hbox.addWidget(self.buttonGroup())
        self.setLayout(hbox)
        
        self.setFixedHeight(int(self.WidgetH))
        self.setStyleSheet('background-color: rgba(0,0,0,0)')
        self.setContentsMargins(0,15,0,-15)
             
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)
                                
        self.show()
                
### --------------------------------------------------------                                   
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)   
        rect = QRectF(2, 2, self.WidgetW-4, self.WidgetH-4)                   
        painter.setPen(QPen(QColor(0,80,255), 5, Qt.PenStyle.SolidLine,            
            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(QColor(0,150,245,255))
        painter.drawRoundedRect(rect, 15, 15)
              
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
        
    def mouseDoubleClickEvent(self, e):
        self.works.closeWidget()
        e.accept()
        
### -------------------------------------------------------- 
    def sliderGroup(self):
        groupBox = QGroupBox('Rotate     Scale   Opacity   ')
        
        groupBox.setFixedWidth(170)
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
   
        self.rotateValue = QLabel('0', alignment=Qt.AlignmentFlag.AlignCenter)
        self.rotaryDial = QDial()
        self.rotaryDial.setMinimum(0)
        self.rotaryDial.setMaximum(360)
        self.rotaryDial.setValue(0)
        self.rotaryDial.setFixedWidth(60)
        self.rotaryDial.setWrapping(False)
        self.rotaryDial.setNotchesVisible(True)
        self.rotaryDial.setNotchTarget(15.0)
        self.rotaryDial.valueChanged.connect(self.Rotate)
    
        self.scaleValue = QLabel('1.00')
        self.scaleSlider = QSlider(Qt.Orientation.Vertical)   
        self.scaleSlider.setMinimum(25)
        self.scaleSlider.setMaximum(250)
        self.scaleSlider.setSingleStep(10)
        self.scaleSlider.setValue(100)
        self.scaleSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scaleSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.scaleSlider.setTickInterval(50)  
        self.scaleSlider.valueChanged.connect(self.Scale)   
        
        self.opacityValue = QLabel('.50')
        self.opacitySlider = QSlider(Qt.Orientation.Vertical)   
        self.opacitySlider.setMinimum(0)
        self.opacitySlider.setMaximum(100)
        self.opacitySlider.setSingleStep(1)
        self.opacitySlider.setValue(50) 
        self.opacitySlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.opacitySlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.opacitySlider.setTickInterval(16)  
        self.opacitySlider.valueChanged.connect(self.Opacity)
                  
        sbox = QHBoxLayout()  ## sliders  
        sbox.addSpacing(-10)    
        sbox.addWidget(self.rotaryDial)  
        sbox.addSpacing(10)       
        sbox.addWidget(self.scaleSlider) 
        sbox.addSpacing(10)                
        sbox.addWidget(self.opacitySlider) 
        
        vabox = QHBoxLayout()  ## values
        vabox.addSpacing(0) 
        vabox.addWidget(self.rotateValue)        
        vabox.addSpacing(0) 
        vabox.addWidget(self.scaleValue)     
        vabox.addSpacing(0) 
        vabox.addWidget(self.opacityValue)  
        vabox.setAlignment(Qt.AlignmentFlag.AlignBottom)
         
        vbox = QVBoxLayout()  
        vbox.addLayout(sbox)
        vbox.addLayout(vabox)
        
        groupBox.setLayout(vbox)
        return groupBox
    
### --------------------------------------------------------   
    def buttonGroup(self):
        groupBox = QGroupBox(' Shadow')
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        
        groupBox.setFixedWidth(103)
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
                     
        hideBtn = QPushButton('Hide')
        flipBtn  = QPushButton('Flip')
        flopBtn  = QPushButton('Flop')
        self.linkBtn = QPushButton('Link')
        newBtn  = QPushButton('New')
        delBtn  = QPushButton('Delete')
        quitBtn = QPushButton('Close')
    
        hideBtn.clicked.connect(self.works.hideOutline)  ## that's it, no toggle
        flipBtn.clicked.connect(self.maker.flip)
        flopBtn.clicked.connect(self.maker.flop)
        self.linkBtn.clicked.connect(self.maker.toggleLink)
        newBtn.clicked.connect(self.maker.newShadow)
        delBtn.clicked.connect(self.works.deleteShadow)
        quitBtn.clicked.connect(self.works.closeWidget)
    
        hbox = QVBoxLayout(self)
        hbox.addWidget(hideBtn)
        hbox.addWidget(flipBtn)
        hbox.addWidget(flopBtn)
        hbox.addWidget(self.linkBtn)
        hbox.addWidget(newBtn)
        hbox.addWidget(delBtn)
        hbox.addWidget(quitBtn)
                
        groupBox.setLayout(hbox)
        return groupBox
    
 ### --------------------------------------------------------
    def Rotate(self, val): 
        if self.maker.linked == False:
            self.works.rotateShadow(val)
            self.rotateValue.setText('{:3d}'.format(val))
             
    def Scale(self, val):  
        if self.maker.linked == False:
            op = (val/100)
            self.works.scaleShadow(op) 
            self.scaleValue.setText('{0:.2f}'.format(op))
                    
    def Opacity(self, val):
        if self.maker.linked == False:
            op = (val/100)
            self.maker.shadow.setOpacity(op)
            self.maker.alpha = op
            self.opacityValue.setText('{0:.2f}'.format(op)) 
                                                                                                                                                                                                               
### ------------------- dotsShadowWidget -------------------

