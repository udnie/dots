

**Last Update: 05/30/202**

---


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
        self.pix.setPos(pos)

    def _setOpacity(self, opacity):
        self.pix.setOpacity(opacity)
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






