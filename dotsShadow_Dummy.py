

### ------------------ dotsShadow_Dummy --------------------
''' comment out import ShadowMaker in dotsPixItem and dotsSideShow
    and replace with import Shadow_Dummy to turn off shadows '''                                                                                                                    
### -------------------------------------------------------- 
class ShadowMaker:  
### --------------------------------------------------------    
    def __init__(self, parent):
        super().__init__()
    
        self.path = []   
        
        self.ishidden = False
        self.alpha  =  0
        self.scalor =  0
        self.rotate =  0
        self.imgSize = 0  
        self.shadow  = None
        
        self.widget  = None
        
        self.addRestore = 'pass'
           
    def restoreShadow(self):
        pass
    
    def addShadow(self, width, height, viewW, viewH):
        return None
    
    def deleteShadow(self):
        pass
    
    def hideAll(self):
        pass
    
    def toggleOutline(self):
        pass
    
    def clearOutlines(self):
        pass
    
    def deleteOutline(self):
        pass
    
    def deletePoints(self):
        pass
    
    def cleanUpShadow(self):
        pass
    
    def init(self):
        pass
       
### --------------------------------------------------------
class Shadow(): 
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
    
        self.shadow  = None
    
### ------------------ dotsShadow_Dummy --------------------
    
    