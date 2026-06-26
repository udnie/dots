
## ------------------- script-qt5.py ----------------------
''' Removes any unnecessary code, comments or tokens leaving
    only PyQt5 code. '''
### -------------------------------------------------------
import os

for file in ["outline.py", "vhx.py", "videoPlayerShared.py"]:
    lines = []
    with open(file, 'r') as fp: 
        for line in fp:

            if file == "outline.py":
                if "QtSvgWidgets" in line:
                    line = '# ' + line

                elif "##from PyQt5.QtSvg" in line:
                    line = line[2:]
                    
            elif file == "vhx.py":
                
                if "e.globalPos().toPoint()" in line:
                    i = line.index('.toP')  
                    line = line[0:i] + line[i+10:]
                    
            elif file == "videoPlayerShared.py":

                if 'aspect/ratio' in line:  ## there is only one
                    i = line.index('s')  ## self.set
                    line = line[0:i] + '# ' + line[i:]
            
                if '## 6' in line or 'end' in line or '## del' in line or \
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

                       
