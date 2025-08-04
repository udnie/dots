
## ------------------- script-qt5.py ----------------------
''' Removes any unnecessary code, comments or tokens leaving
    only PyQt5 code. '''
### -------------------------------------------------------
import os

files = ["dotsHelpMenus.py", \
        "dotsHelpMaker.py", \
        "videoPlayerOne.py", \
        "dotsVideoPlayer.py", \
        "dotsTableMaker.py", \
        "dotsPixItem.py",\
        "dotsSideGig.py"]
for file in files:
    lines = []
    with open(file, 'r') as fp: 
        for line in fp:
            
            if file == "dotsHelpMenus.py":  
                if '45' in line:
                    i = line.index('45') 
                    line = line[0:i] + '59' + line[i+2:]
                    print(line, i)
              
            elif file == "dotsSideGig.py":
                if  '## 5' in line:
                    i = line.index('50') 
                    line = line[0:i] + '250)' + '\n'
                          
            elif file == "dotsHelpMaker.py":  
                if '42' in line:
                    i = line.index('42') 
                    line = line[0:i] + '17' + line[i+2:]
                    print(line, i)
                    
                elif '47' in line:
                    i = line.index('47') 
                    line = line[0:i] + '23' + line[i+2:]
                            
            elif file == "dotsPixItem.py":
                if line.startswith('from dotsShadowMaker'):
                    line = '# ' + line
                
                elif 'dotsShadow_Dummy' in line:
                    i = line.index('f')  ## self.set
                    line = line[i:]   
      
            elif file == "dotsTableMaker.py":
                if 'QtGui' in line and line.find(', QShortcut') > 0:
                    line = line[0:line.find(', QShortcut')] + '\n'
                
                elif 'QtWidgets' in line:
                    line = line.strip() + ', QShortcut' + '\n'
                           
            elif file in ("dotsVideoPlayer.py","videoPlayerOne.py"):
                if line.startswith('import cv2'):
                    line = '# ' + line
                
                elif 'aspect/ratio' in line:  ## there is only one
                    i = line.index('s')  ## self.set
                    line = line[0:i] + '# ' + line[i:]
           
                # if '## 6' in line:     
                #     for i, c in enumerate(line):  
                #         if c != ' ' and c != '\t':
                #             break
                #         line = line[0:i] + '# ' + line[i:]
                
                if '## 6' in line or 'end' in line or '## del' in line or\
                    '##--5' in line:
                    continue
                
                elif '## 5' in line:
                    for i, c in enumerate(line):
                        if c == '#':
                            break
                    if i == 0:
                        line = line[2:]
                    else:
                        line = line[0:i-1] +  ' ' + line[i+2:]
                        
                    i = line.index('## 5')  ## remove it 
                    line = line[0:i] + '\n'
                                         
            if line.startswith('from PyQt'): ## just to make sure
                line = 'from PyQt5' + line[line.index('.'):]
      
            lines.append(line)
                
        if len(lines) > 0:  
            save = file
            os.rename(file, file + '--')  ## the way sed does it 
            with open(file, 'w') as fp: 
                for line in lines:
                    fp.write(line)   
                                                                                                                              
## -------------------- that's all ---------------------

                       
