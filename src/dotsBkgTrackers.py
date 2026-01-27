
import os
import time

from PyQt6.QtCore       import Qt, QPoint, pyqtSlot
from PyQt6.QtWidgets    import QWidget, QAbstractItemView, QHBoxLayout, \
                                QTableWidget, QPushButton, QVBoxLayout, QTableWidgetItem
                        
from dotsSideGig        import getVuCtr, MsgBox

RowHt = 30
HeaderStr = ["filename", "zvalue",  "direction", "mirrored", "rate", "showtime",\
            "screenrate", "directory"]  
                                                                                       
### ------------------- dotsBkgTrackers --------------------
''' Tracker related code - tracker tableWidget'''
### --------------------------------------------------------
class Trackers(QWidget): 
### -------------------------------------------------------- 
    def __init__(self, parent, dump): 
        super().__init__() 

        self.bkgtrackers = parent
        self.canvas = self.bkgtrackers.canvas
             
        self.setWindowTitle('trackers') 
        
        self.type = 'widget'
        self.setAccessibleName('widget')

        self.tableWidget = QTableWidget()    
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)         
    
        c = len(dump[0])
    
        self.tableWidget.setColumnCount(c)
        self.tableWidget.setRowCount(len(dump))

        self.width, self.height = c*110, (len(dump)+1) * RowHt
        self.tableWidget.setFixedSize(self.width, self.height)
        
        self.tableWidget.setColumnWidth(0, 135)    
 
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
           
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableWidget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)  ## google ai

        self.tableWidget.itemSelectionChanged.connect(self.selectionChanged)   ## google ai

        self.tableWidget.setHorizontalHeaderLabels(HeaderStr) 
        self.tableWidget.horizontalHeader().setStyleSheet('QHeaderView::section{\n'
            'background-color: rgb(115,225,225)}')	 
            
        self.upBtn = QPushButton("Move Up One")
        self.upBtn.clicked.connect(self.up)
        self.upBtn.setMaximumWidth(200)  
              
        self.closeBtn = QPushButton("This Button to Close")
        self.closeBtn.clicked.connect(self.bye)
        self.closeBtn.setMaximumWidth(200)              
              
        self.downBtn = QPushButton("Move Down One")
        self.downBtn.clicked.connect(self.down)
        self.downBtn.setMaximumWidth(200) 
    
        vbox = QVBoxLayout()
        vbox.addWidget(self.tableWidget)
        
        hbox = QHBoxLayout()     
        hbox.addWidget(self.upBtn)
        hbox.addWidget(self.closeBtn)
        hbox.addWidget(self.downBtn) 
        
        vbox.addLayout(hbox) 
        self.setLayout(vbox)
            
        x, y = getVuCtr(self.canvas)
        pos = QPoint(x, int(y - (self.height/2)))
        
        self.move(int(pos.x()-(self.width/2)), int(pos.y())-50)
          
        self.createTable(dump)
 
### ------------------------------------------------------- 
    @pyqtSlot(str) 
    def setPixKeys(self, key):  ## from sideCar2
        if key in ('up', 'down'):
            self.up() if key == 'up' else self.down()

    def createTable(self, dump): 
        for row, val in enumerate(dump):
            for col, v in enumerate(val):
                item = QTableWidgetItem(v)
                if col in (1,4,5):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  
                self.tableWidget.setItem(row, col, item)

    def selectionChanged(self):  ## google ai       
        selectedRows = self.tableWidget.selectionModel().selectedRows()
        self.row = [index.row() for index in selectedRows]
        self.save = self.tableWidget.item(self.row[0], 0).text()
        
### -------------------------------------------------------  
    def up(self):  ## google ai
        selectedRow = self.tableWidget.currentRow()
        if selectedRow > 0: 
            self.swapRows(selectedRow, selectedRow - 1)  
            self.tableWidget.setCurrentCell(selectedRow - 1, self.tableWidget.currentColumn())  
            self.swap_cells(selectedRow - 1, 1, selectedRow, 1)
            
            self.bkgtrackers.swapZvals(self.save, 
                self.tableWidget.item(self.row[0], 1).text(),
                self.tableWidget.item(self.row[0]+1, 0).text(),
                self.tableWidget.item(self.row[0]+1, 1).text())
                                  
    def down(self):  ## google ai
        selectedRow = self.tableWidget.currentRow()    
        if selectedRow < self.tableWidget.rowCount() - 1:
            self.swapRows(selectedRow, selectedRow + 1)  
            self.tableWidget.setCurrentCell(selectedRow + 1, self.tableWidget.currentColumn())  
            self.swap_cells(selectedRow + 1, 1, selectedRow, 1)
               
            self.bkgtrackers.swapZvals(self.save, 
                self.tableWidget.item(self.row[0], 1).text(), 
                self.tableWidget.item(self.row[0]-1, 0).text(),
                self.tableWidget.item(self.row[0]-1, 1).text())           
            
### ------------------------------------------------------- 
    def swapRows(self, source, dest):  ## google ai
        for col in range(self.tableWidget.columnCount()):
            item1 = self.tableWidget.takeItem(source, col)
            item2 = self.tableWidget.takeItem(dest, col)
            self.tableWidget.setItem(source, col, item2)
            self.tableWidget.setItem(dest, col, item1)
                                              
    def swap_cells(self, source, scol, dest, dcol):  ## google ai
        sitem1 = self.tableWidget.takeItem(source, scol)
        ditem2 = self.tableWidget.takeItem(dest, dcol)
        self.tableWidget.setItem(source, scol, ditem2)
        self.tableWidget.setItem(dest, dcol, sitem1)    
                                
    def bye(self):
        if self.tableWidget != None:        
            self.tableWidget.close()
            self.tableWidget = None 
            self.bkgtrackers.closeTracker()
        
### --------------------------------------------------------
class BkgTrackers: 
### -------------------------------------------------------- 
    def __init__(self, parent): 
        super().__init__() 
                                 
        self.bkgMaker = parent 
        self.canvas   = self.bkgMaker.canvas 
  
        self.tracker  = None
                
  ### --------------------------------------------------------   
    def addTracker(self, bkg):  ## always - either loading a play file or adding from backgrounds
        fileName = bkg.fileName
        
        if len(self.bkgMaker.newTracker) == 0:  ## add the first one as its unique
            self.bkgMaker.newTracker[fileName] = self.addNewTracker(bkg)  
            return True
        else:   
            if self.bkgMaker.newTracker.get(fileName) == None:  ## no duplicate filenames
                self.bkgMaker.newTracker[fileName] = self.addNewTracker(bkg)
                return True
            else:   
                return False
    
    def trackThis(self):
        if self.tracker == None:  
            self.tracker = Trackers(self, self.dumpTrackers())
            self.tracker.show()   
           
    def swapZvals(self, saved, savedZ, other, otherZ):
        for itm in self.canvas.scene.items():
            if itm.type == 'bkg':
                if itm.fileName == saved.lower():   
                    itm.setZValue(float(savedZ))  
                    time.sleep(.05) 
                    
                elif itm.fileName == other.lower():
                    itm.setZValue(float(otherZ)) 
                    time.sleep(.05)  
  
    def closeTracker(self):
        self.tracker.close()
        self.tracker = None 
                                       
    def delTracker(self, bkg):  
        if self.bkgMaker.newTracker.get(bkg.fileName):
            del self.bkgMaker.newTracker[bkg.fileName]
                       
    def dumpTrackers(self):  ## used by bkgItem - 'B' in BkgHelp menu
        dump = []  
        for bkg in self.canvas.scene.items(): ## need a bkg referernce for bkglabels
            if bkg.type == 'bkg':
                fileName = os.path.basename(bkg.fileName) 
                try:            
                    if trk := self.canvas.bkgMaker.newTracker[fileName]: 
                        zval = bkg.zValue()
                        fileName, direction, mirroring, locked = self.addBkgLabels(bkg)
                        rate, showtime, path = str(trk['rate']), str(trk['showtime']), trk['path']
                        s = f"{fileName} {zval} {direction} {mirroring} {rate} {showtime} {path[5:-1]}"
                        dump.append(s.split())
                except:
                    None            
        if len(dump) > 0:
            return dump
        else:
            MsgBox('Error in dumpTrackers')
            return None
        
    def addBkgLabels(self, bkg): 
        fileName = bkg.fileName       
        if bkg.locked:
            locked = 'Locked' 
        else:
            locked = 'UnLocked' 
            
        if bkg.direction == 'left':
            direction = 'Left'
        elif bkg.direction == 'right': 
            direction = 'Right'     
        elif self.canvas.dots.Vertical:  ## don't forget dots.
            direction = 'Vertical'
            
        else:
            if self.bkgMaker.newTracker[fileName]:   
                direction = self.bkgMaker.newTracker[fileName]['direction']     
            if direction == '':
                direction = 'NoDirection'
                
        if bkg.mirroring == False:
            mirror = 'Continuous'
        elif bkg.mirroring:
            mirror = 'Mirrored'
        elif bkg.direction == '' and bkg.scrollable == False:
            mirror = 'Not Scrollable'    
        return fileName.capitalize(), direction, mirror, locked
              
### -------------------------------------------------------- 
    def restoreFromTrackers(self, bkg):  ## returns what gets lost on each new bkg
        if tmp := self.bkgMaker.newTracker.get(bkg.fileName):
            bkg.direction  = tmp['direction']           
            bkg.mirroring  = tmp['mirroring']
            bkg.factor     = tmp['factor']
            bkg.showtime   = tmp['showtime']
            bkg.rate       = tmp['rate']
            bkg.path       = tmp['path']
            bkg.scrollable = tmp['scrollable']
                                                                                             
    def resetTracker(self, bkg):  ## reset both tracker and bkgItem
        if tmp := self.bkgMaker.newTracker.get(bkg.fileName):  
            tmp['fileName']    = bkg.fileName 
            tmp['direction']  = ''
            tmp['mirroring']  = False
            tmp['factor']     = 1.0
            tmp['showtime']   = 0
            tmp['rate']       = 0
            tmp['scrollable'] = False
            tmp['path']       = bkg.path
             
        bkg.direction  = ''             
        bkg.mirroring  = False
        bkg.factor     = 1.0
        bkg.showtime   = 0   
        bkg.rate       = 0
        bkg.scrollable = False    
        bkg.path       = ''
  
        self.bkgMaker.addWidget(bkg)
        
### -------------------------------------------------------- 
    def addNewTracker(self, bkg):  ## used here
        tmp = {
            "fileName":    os.path.basename(bkg.fileName),
            "direction":  bkg.direction,
            "mirroring":  bkg.mirroring,
            "factor":     bkg.factor,
            "rate":       bkg.rate,
            "showtime":   bkg.showtime,
            "path":       bkg.path,
            "scrollable": bkg.scrollable,
        }
        return tmp
                                                                                                                                                                                                                                        
### ------------------- dotsBkgTrackers --------------------
             



