
###Last Update: 07/05/2023
---
       
**Starting from zero**  
Here are two directories that you should be aware of - **sprites** and **backgrounds**.  That's where your stuff needs to go if you want to do something other than play with the sprites and backgrounds already there. What I call a **sprite** needs to be **'transparent.png'** file and should be no larger than around 600 pixels square. For **backgrounds** I'd recommend keeping the files under **500MB** in size.

Besides the **sprites** and **backgrounds** directories you've two others, **plays** and **paths**, you'll visit from time to time. A **.play** file holds the sprite and background information used to restore the last saved canvas.  The **.path** file is a collection of screen point locations used in animating a screen object along a path.  There's a video for that.

I suggest looking at a few videos in **Changes.md** starting from the most recent to get an idea of how **dots** works.  These videos will cover the most recent changes while touching on the basics along the way. 

---

If you're in **Windows** you'll probably need to edit the **paths** dictionary in **dotsShared.py**.   

    paths = {        
        'snapShot':     ',/../',  
        'bkgPath':      './../backgrounds/',
        'imagePath':    './../images/',
        'playPath':     './../plays/',
        'spritePath':   './../sprites/',
        'paths':        './../paths/',
        'txy':          './../txy/',
        'demo':         './../demo/',
    }
    
I've recently changed the directory layout for **dots** by moving the **dots\*.py** files to **dots/src**. The following script is working for me using Mac's Automator.  It also required some setting of permissions as I had added an additional login.

    cd '/users/your directory/python/qt5/dots/src'; /usr/local/bin/python3 ./dotsQt.py      

---

**From a blank canvas screen** you can choose to enter one of the following keys: 

 
    'L' to run the file dialog used to load a .play file   
    'S' to display the Screen Menu to change the canvas size and format     
    'R' to display the Demo Menu   
    'A' to add a background  
    'C' clears the canvas
     The 'PathMaker' button to draw a path used to animate a sprite
    

**Sprites** are added by drag and dropping them onto the screen/canvas, **backgrounds** are loaded by either entering **'A'** if the canvas is blank or clicking on the **Add** button.  Clicking on the **Color** button gives you a number options to create a solid color **flat**.     

A **right mouse-click** on a **sprite, background** or **flat** will pop up a widget that provides access to the most often used functions such as scaling or rotation. There's also a widget for a **shadow** if it's enabled and a widget that pops up when entering **pathMaker**.  

Besides widgets you've a number of **keyboard** controls that either match functions of the widget of add additional functions to sprites and backgrounds. Many of these controls will work on a multiple selection of sprites as well. There are two sets of keys, one for the start screen, the **canvas**, the other for **pathMaker**.  They don't interact but you can access **background** once **pathMaker** is active.

---

There are three **\*.py** files besides **dotsShared.py** you should be aware of if you want to change how **dots** behaves. If you wish to try out **shadows**, besides downloading and installing **numpy** and **opencv**, you'll need to make a small edit in **dotsPixItem.py** to comment out an import and uncomment another.

    from dotsShadowMaker    import ShadowMaker  ## add shadows
    ##from dotsShadow_Dummy    import ShadowMaker  ## turns off shadows
    
For **scrolling backgrounds** it gets more interesting.

    abstract = {  ## used by abstract.jpg and snakes.jpg - based on 1280X640 2:1 - under 1MB
        '1080':  (10.0,  17.62, 17.55),  ## first, next, next-right
        '1280':  (10.0,  18.97,  19.0),
        '1215':  (10.0,   17.4,  17.4),  
        '1440':  (10.0,  18.95, 18.95),
        '1296':  (10.0,  17.45, 17.55),  
        '1536':  (10.0,  18.95, 18.95),
        '620':   (10.0,   20.9,   0.0),
    }
    
 
This dictionary is located in **dotsBkgItem.py**, the **background class** file. It's very likely the values I used in the video on scrolling backgrounds won't work for you without some attention. Pick one screen format to work with and get it scrolling without gaps or overlapping. If you look at the numbers, excluding the **'620' vertical**, you'll see there are two groups of values not very far apart. One being the **3:2** and the other **16:9**.  It's a good guess the other screen values you would need will be very close but there's no reason to update them unless you plan to try out all the formats.

The last file you might want to investigate is **dotsBkgWidget.py** for making changes to the **Matte** class.  There are four class variables to consider, two that hold the matte colors, one for the photo and one that modifies the height in order to resize and reformat. You would need to edit the file inorder to change any one of these variables. 

---

This is in **ReadMe** but it fits better here:

I use the **QGraphicsitem** zValue() as a means to order the dots graphic types which share 
the scene items list. There are two functions, toFront() and lastZval() that help to make sure 
the different types I've created are good neighbors.

#### types and zValue range		
| scene.item  | type  | zValue |
|:------------- |:---------------:| -------------:|
| PointItem | pt | 200 from topmost item+ |
| MapItem | map | 50 over top pixItem |
| TagItem | tag|45 over top pixItem|
| Paths| path| 35 over top pixItem
| PixItem | pix  | **\*see below**
| Shadow  |shadow| 50|
| Points  |point | 40|
| Outline |  none   | 30| 
| LineItem  | grid   | -50 as a group |
| BkgItem   | big | -99 decreasing by -1 |  

  
**\***number of screen items + 100 decreasing by 1 per item

---

####A Brief History of Animation

**It's not advisable to attempt changes or make selections when running an animation as interesting and unwanted problems can occur.**   

**PixItems** and **BkgItems** are the only ones currently that are animated, that includes **Wings**.

Animations come in two basic flavors, either ones that are programmatic or 
ones that are path driven, and a third possibility would be a combination of the two.  An animation can be added to a screen object, pixItem, once it's been selected by right-mouse clicking on it and then clicking on an animation or path from the pop-up menu that appears. The selection, either a **.play** or **.path** file is applied to the **tag** property of the pixItem which later is used to run the animation it references.
 
The majority of the animation code is in the **dotsAnimation.py** file.  The first thing of interest in reading thru this file are the four variables, **AmnimeList, OneOffs, Stage, Spins**. The first two are lists which I'll later combine into one. These items reference the animations that are selectable and runnable from a pop-up context-menu. 

	AnimeList = ['Vibrate', 'Pulse','Bobble','Idle']
	OneOffs   = ['Rain','Spin Left','Spin Right','Stage Left','Stage Right']
	Stages    = ('Stage Left', 'Stage Right')
	Spins     = ('Spin Left', 'Spin Right')
	
Here's where you add your animation so it appears in the pop-up menu.

Next of interest is the **Node** class.  This class   provides the code used to control one of the four properties you might want to animate, **position, scale, rotation, or opacity**. They can also be combined, run in parallel or run sequentially.  No code changes needed here.  *Edited for brevity.*

	class Node(QObject):
	### --------------------------------------------------------
        def __init__(self, pix):
            super().__init__()
            self.pix = pix
    
    
        def _setPos(self, pos):
            try:
                self.pix.setPos(pos)
            except RuntimeError:
                return None
    
        def _setOpacity(self, opacity):
            try:
                self.pix.setOpacity(opacity)
            except RuntimeError:
                return None
        ...
    
        pos = pyqtProperty(QPointF, fset=_setPos)
        opacity = pyqtProperty(float, fset=_setOpacity)


Next is the **Animation** class.  First up, a short dictionary of animations already referenced at the start followed by the **setAnimation** and **_random** functions. You may need to edit this class or **setAnimation** if you add a new animation, to do so follow the examples and read the published docs.  

	class Animation:
	### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
        self.canvas = parent 
    
        self.singleFunctions = {  ## values are objects 
            'Vibrate': vibrate,  
            'Pulse': pulse,
            'Bobble': bobble,
            'Idle': idle,
        }

The **setAnimation** function is the main driver for selecting which 
animation to run. *Edited for brevity*.

    def setAnimation(self, anime, pix):
        ## pathList comes from self.canvas.pathList
        ## this function returns an animation to a pixitem
        
        if anime == 'Random':
            anime = self._random()   ## add the animation type to the tag
            pix.tag = pix.tag + ',' + anime 

        if anime in self.singleFunctions:  ## thanks again to Martin
            fn = self.singleFunctions[anime]  ## objects passed as functions
            return fn(pix)

        ## one-offs
        if anime == 'Rain':
            return rain(pix, Node(pix))
        elif anime in Stages:
            return stage(pix, anime)
        elif anime == 'Flapper':
		...

###Animation code follows...

You'll see these three lines in many of the animations that follow.  I mentioned the **Node** class earlier, here I'm creating a reference, **pos**, to the pix screen items current position, I'm also setting the **node's** point of origin based on the pixItem.  *Note* **->** An animation function may require more that one argument which will need to be accounted for prior to using it.

	def vibrate(pix):  
	    node = Node(pix)
	    pos  = node.pix.pos()
	    node.pix.setOriginPt()

Further down you'll see a variation of this repeated for each of the four properties used in other animations. An example of creating an animation that controls the position of the screen item.

   		vibrate = QPropertyAnimation(node, b'pos')

And just below that how the **pos** variable is used.

	    vibrate.setStartValue(pos)
	    vibrate.setKeyValueAt(0.25, pos + QPointF(-ran, ran))
	    vibrate.setKeyValueAt(0.25, pos + QPointF(ran*1.75, ran*1.25))
	    vibrate.setKeyValueAt(0.25, pos + QPointF(-ran*1.75, -ran*1.25))           
	    vibrate.setKeyValueAt(0.25, pos + QPointF(-ran, ran))
	    vibrate.setEndValue(pos)
	
	    vibrate.setLoopCount(-1)  ## let it run forever...

There is one other file that extends what I'm calling code driven animation and that is  **dotsSidePath.py**. Here you'll find the **demo animation** path code, the function **setPaths** that creates paths from **.path** files plus the functions to load the path file and set the node origin.

That's a brief rundown on code driven animations in dots and their locations.

**dotsSideShow.py** is the file which **loads, displays, runs,** and **saves** your animations in the form of **.play** files. Here you'll find some of my not so pythonic code if you search for **demo** or **wings**.  

This is all the code in **sideShow** for running the **demo** other then a few variables initialized earlier and it being part of a larger enclosing for-loop. It's based on having 22 aliens on the screen whose tags are set to **demo.path**. I'm scaling them down as I process them while also setting a delayed start to get the effect I want. This *Code fragment* is found in sideShow's **run** function. This is the only bit of code you might want to tweak in sideShow.
	
		## set scale factor if demoPath and alien
		if pix.tag.endswith('demo.path') and r >= 0:  
		    if 'alien' in pix.fileName:  ## just to make sure you don't scale everything
		        pix.scale = scale * (67-(r*3))/100.0  ## 3 * 22 screen items
		        r += 1
		        ## delay each demo pixitems start 
		        QTimer.singleShot(100 + (r * 50), pix.anime.start)
		        
		        
 

In the function **addPixToScene** I end with a line of code that passes a reference of the pixItem to **dotsSideCar.py** where you'll find the function **transFormPixItem**. This function after applying any tranforms either adds the pixItem to the screen or passes it on to the **wings** function if **'wings'** appears in it's filename. The **wings** function also in sideCar.  

        ## may require rotation or scaling - adds to scene items
        ## and where wings are created using the 'right' wing pix
        self.sideCar.transFormPixItem(pix, pix.rotation, pix.scale)

The **wings** function is the only other bit of code that you may want to explore, particularly if you want to use something other the supplied bat wings and body.  *Code fragment* 

    def wings(self, pix):
        rightWing = pix
        pathTag = pix.tag
  
        rightWing.part = 'right'
        rightWing.tag  = 'Flapper'  ## applies this animation when run
		...
		...
		
Back to **dotsSideCar.py** for a look at the function **savePivots** which as the comment states, saves a pivots path, it's tag setting and xy position in the pixItem rightWing reference for later retrieval.  See the **wings** function for how that works. Kinda of cheesy but simple as I only save the one wing to rebuild the bat or winged object.

    def savePivots(self):
        ## save a pivots path and xy in rightWing for later
        for pix in self.scene.items(Qt.SortOrder.AscendingOrder):
            if pix.type == "pix":      
                if pix.part == 'pivot':  ## pivot comes up first
                    t = pix.tag
                    p = pix.sceneBoundingRect()
                if pix.part == 'right':  ## update the next 'right'
                    pix.tag = t
                    pix.x = p.x() + p.width()/2
                    pix.y = p.y()

There are two other animations worth mentioning, **fin** and **reprise**, two of my little amusements. When you delete a pixItem, except for frames, I run **fin** which the scales the pixItem down in size, while rotating it and lowering its opacity before deleting it. When stopping an animation I run **reprise** to reposition screen objects back to their starting positions.  Carry overs from my original java program. 

Lastly, **Path** animations are accessed from the **Path Maker** button and are a non-programming means of moving a character around the screen. The ability to draw is not required. The paths that appear in context-menu are drawn from the files in the paths folder. Play.  






