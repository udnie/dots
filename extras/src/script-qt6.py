
## ------------------- script-qt6.py ----------------------
''' Removes any unnecessary code, comments or tokens leaving
    only PySide6 code. '''
### -------------------------------------------------------
import os

qstring = "PyQt6"

for file in ["videoPlayerShared.py", "spriteMakerWorks.py"]:
    lines = []
    with open(file, 'r') as fp: 
        for line in fp:
            
            if file == "videoPlayerShared.py":
                
                if 'aspect/ratio' in line:  ## there is only one
                    i = line.index('s')  ## self.set
                    line = line[0:i] + '# ' + line[i:]
            
                if '## 6' in line:
                    i = line.index('## 6')  ## self.set
                    line = line[0:i] + '\n'   
            
                if '## 5' in line or 'end' in line or '## del' in line:  ## skip
                    continue
        
                if '##--5' in line:
                    i = line.index('##--5') 
                    line = line[0:i] + '\n' 
                       
            elif file == "spriteMakerWorks.py" and qstring == "PySide6":
                
                if 'sizeInBytes' in line: 
                    i = line.index('bits') 
                    line = line[0:i] + '# ' + line[i:]
                                       
            lines.append(line)
                
    if len(lines) > 0:  
        save = file
        os.rename(file, file + '--')  ## the way sed does it 
        with open(file, 'w') as fp: 
            for line in lines:
                fp.write(line)   
                                                                                                                              
## -------------------- that's all ---------------------

                       
