
### Last Update: 07/07/2023
       
---
       
**Starting from zero**  
Here are two directories that you should be aware of - **sprites** and **backgrounds**.  That's where your stuff needs to go if you want to do something other than play with the **sprites** and **backgrounds** already there. What I call a **sprite** needs to be **'transparent.png'** file and should be no larger than around **600 pixels square**. For **backgrounds** I'd recommend keeping the files under **500MB** in size.

If you have a current model iPhone, iPad, or Mac you can generate a sprite using **Remove BackGround** in Preview, selecting it in Photos or you can look into **SpriteMaker**. There's a write-up and a video for it.

Besides the **sprites** and **backgrounds** directories you've two others, **plays** and **paths**, you'll visit from time to time. A **.play** file holds the **sprites** and **backgrounds** information used to restore the last saved canvas.  The **.path** file is a collection of screen point locations used in animating a screen object to move along a path.  

A **.play** file can also be used to display a **photo collage** without any animation attached.

Besides these four directories there are the **demo, images, shadows, spriteMaker, src**, and **txy** directories.  The **demo** and **images** directories hold photo assets and the demo **path** files used by **dots** to keep the **sprites** and **backgrounds** directories free of clutter.

The **shadows, spriteMaker**, and **txy** directories are extras and I would look at **Changes** for a description of what they do. I'd also suggest looking at the videos in **Changes** starting with the latest entry and working backwards to get an idea of how **dots** works. These videos cover the most recent additions while touching on the basics along the way. 

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
    
There are two other files I'd suggest looking at are **dotsControlView.py** and **dotsScreens.py**. **ControlView** handles **drag** and **drop** and all the key stroke entries - except where it doesn't as in **Matte**.  **Screens** is the file that contains all or most of the code and data used in reformatting and sizing **dots** as well as the **Screen Menu** class.

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
    

**Sprites** are added by drag and dropping them onto the screen/canvas, **backgrounds** are loaded by either entering **'A'** if the canvas is blank or clicking on the **Add** button.  Clicking on the **Color** button gives you a number options to create a solid color **flat** which is treated as a **background** except for scrolling. 

A **right-mouse-click** on a **sprite, background** or **flat** will pop up a widget that provides access to the most often used functions such as scaling or rotation. There' a widget for a **shadow** if shadows are enabled and a widget that pops up when entering **pathMaker** - both of these also work with a **right-mouse-click**. 

Besides widgets you've a number of **keyboard** controls that either match the functions provided by the **sprite** and **background widgets** or add additional functions, especially if one or more **sprites** has been selected.

 The right hand panel displays a set of allowable keys and their function, one set for the start screen, the **canvas**, the other for **pathMaker**.  **Canvas** and **pathMaker** don't interact with each other but you can access **backgrounds** once **pathMaker** is active.

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
    
 
This dictionary is located in **dotsBkgItem.py**, the **background class** file. It's very likely the values I used in the video on **scrolling backgrounds** won't work for you without some attention. Pick one screen format to work with and get it scrolling without gaps or overlapping. If you look at the numbers, excluding the **'620' vertical**, you'll see there are two groups of values not very far apart. One being the **3:2** and the other **16:9**.  It's a good guess the other screen values you would need will be very close but there's no reason to update them unless you plan to try out all the formats.

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

  
**\** number of screen items + 100 decreasing by 1 per item

---

### A Brief History of Animation

**It's not advisable to attempt changes or make selections when running an animation as interesting and unwanted problems can occur.**   

**PixItems** and **BkgItems** are the only ones currently that are animated. **Wings** is also included as it's a collection of **PixItems**. **BkgItems** have their methods for scrolling a background and will **play, pause, resume and stop** along with any **sprites**.

Animations come in two basic flavors, either ones that are programmatic, you wrote some code, or ones that are path driven. **Paths** are created in **Path Maker** and are a means of moving a character around the screen. The ability to draw is not required. 

A third possibility would be a combination of the two such as **demo** in **dotsSidePaths**. An animation can be added to a screen object, a **PixItem**, once it's been selected by right-mouse clicking on it and choosing an animation or path from the **Animations and Paths** pop-up menu. The selection is applied to the **tag** property of the **PixItem** which later is used to run the animation it references.

The file **dotsSideShow.py** **loads** and **displays** the contents of a **.play** file and also is the source for launching the **Demo Menu** while **dotsShowTime.py** can both **run** and **save** an animation to a file. Originally these two were one file.
 
In **dotsSidePath.py** you'll find the **demo animation** path code, the function **setPaths** that creates paths from **.path** files plus the functions to **load** the path file and set the **node origin**. The code for the actual demos is divided between **dotsAbstractBats.py** and **dotsSnakes.py** which also contains the **Demo Menu** class.
 
The majority of the animation code is in the **dotsAnimation.py** file.  You can probabably skip what follows and save it for a later date as there's nothing here you'll need to deal with until you're ready to animate something. 


---


The first thing of interest in reading thru this file are the four variables, **AmnimeList, OneOffs, Stage, Spins**. The first two are lists which later are combined into one. These items reference the animations that are selectable and runnable from a pop-up context-menu. 

	AnimeList = ['Vibrate', 'Pulse','Bobble','Idle']
	OneOffs   = ['Rain','Spin Left','Spin Right','Stage Left','Stage Right']
	Stages    = ('Stage Left', 'Stage Right')
	Spins     = ('Spin Left', 'Spin Right')
	
You can add your animation to one of these lists so it appears in the pop-up menu.  Some of these animations take more than input variable.

The **Node** class provides the code used to control a **PixItem** property you might want to animate; **position, scale, rotation, or opacity**. They can also be combined to run in parallel or run sequentially as illustrated in some of the animations in this file.  No code changes needed here.  *Edited for brevity.*

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


Next is the **Animation** class.  First up, a short dictionary of animations 
already referenced at the start followed by the **setAnimation** and **_random** 
functions. You may need to edit this class or **setAnimation** if you add a new animation that matches this type.

	class Animation:
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



You'll see these three lines in many of the animations that follow.  I mentioned the **Node** class earlier and here I'm creating a reference, **pos**, to the pix screen items current position, I'm also setting the **node's** point of origin based on the **PixItem**.  An animation function may **require** more that one **argument** which will need to be accounted for prior to using it.

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

---

A note about **Wings** - it's been rewritten and is now a class rather than a function. It's made up of three 
**PixItems** each defined by their **part** tag. The bat portion **part** is named **pivot** and the wings **left** and **right**. The animation is applied to the **pivot** while the wings have their own **flapper** animations.  

Two other animations worth mentioning, **fin** and **reprise**, two of my little amusements. When you delete a **PixItem**, except for frames, I run **fin** which the scales the **PixItem** down in size, while rotating it and lowering its opacity before deleting it. When stopping an animation I run **reprise** to reposition screen objects back to their starting positions.  Carry overs from my original java program. 


Have fun

