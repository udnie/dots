

### ------------------ dotsShadow_Dummy --------------------
''' comment out import ShadowMaker in dotsPixItem and dotsSideShow
    and replace with import Shadow_Dummy to turn off shadows '''                                                                                                                    
### -------------------------------------------------------- 
class ShadowMaker:  
### --------------------------------------------------------    
    def __init__(self, parent):
        super().__init__()

        self.shadow  = None
        self.isActive = False
  
### --------------------------------------------------------
class Shadow: 
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
    
        self.shadow = None
    
### ------------------ dotsShadow_Dummy --------------------
    
    