
### *Last Update: 08/23/2026*

## Scripts  

There is only one codebase and it's written in **pyqt6**.  These scripts will make the necessary changes to convert the **pyqt6** code to either **pyqt5** or **pyside6** and provide any cleanup as well.

        script-qt6.py       Removes PyQt5 code and tokens from the two videoplayer files.
        script-ps6.sh       See edits for PySide6
        
        script-qt5.py       Removes PyQt6 code and tokens, etc.., and other code changes
        script-pyqt5.sh     See edit for PyQt5  


The scripts need to be run in the **dots** source code directory if converting **dots** to something other than **pyqt6**. These scripts also run a same named set of scripts in the **dots/extras/src** directory which will do the same conversions and can be run from  **extras/src** without needing to install **dots**.  A **unix/linux bash/zsh** shell is required to run the  **sed** commands in the **script-.sh** files in order to make the changes necessary to run either **pyQt5** or **pyside6**.  See **January 2025** and **November 30 2024**. 

If you only plan to use **pyQt6** running the python **script-qt6.py** file will clean up the no-longer needed tokens used for converting to other versions.


## Help and Stuff
**Dots** is primarily run using single key commands or from a help menu as there's little or no typing required except when entering file names. As of September 2024 I've added help menus that catalog the commands for each screen item, widget and screen plus a bit of extra stuff that would be good to know. The help menus for everything that gets a command in **dots** are accessible by selecting the help button menus in **Canvas, StoryBoard** and **PathMaker** - the three scenes that make up **dots**.  A **right mouse click** on a screen item will launch its widget.

The helpMenus and menuKeys for **videoPlayers** and **slideShow** are located in **videoPlayerHelp** and are separate from **dots**.  

Once you have **dots** up and running - from the blank screen, that is **Canvas**, you can click on the help button to bring up its menu. From there you can click on the **Help Menus** entry or type **'M'** without the menu to bring up the **Help Menus** menu as well.  It's the easiest way to see what commands are available, where they are located and what they do.  From the same blank screen  entering **'D'** from the keyboard will display the **demo menu** or entering **'S'** will bring up the **screen menu** to select other formats and sizes.

**Opencv-python**, **version 4.12** or newer, is required to add **shadows** to **sprites** in **dots** and run many of the apps in the **extras/src** directory.  There's a **Extras.md** file in the **extras** directory which identifies which apps make use of it.
  
  
## Screens 
I use **'screens'** to refer to both the screen format, number of pixels and ratio - and to the three screens that make up **dots**, **Canvas, Storyboard** and **PathMaker**.  **Canvas** and **pathMaker** don't interact with each other but you can access **backgrounds** once **pathMaker** is active including selecting and running a video or to add a background or flat.
      
## Video  
**PyQt5** now supports looping using the loop button - the **videoWidget** I was previously using has been removed. **PyQt5** also won't loop a video if there's an animation running with shadows.  The two stand-alone videoPlayers each share code from videoClipsMaker, videoClipsWidget, videoPlayerShared and videoPlayerHelp.

There are some differences; **videoPlayerOne** uses a **VideoWidget** to display and still retains resizing from the keyboard and manually setting a video format/ aspect ratio; **videoPlayerTwo"** is based on a **GraphicsVideoItem** and additionally was written to auto-detect the video aspect ratio/format when opening a video file whereas "one" can set it manually. Both videoPlayers are able to read a video files metadata, see **videoPlayerShared.getMetaData**. The default is set to use **opencv** as it's required.  If you're on a Mac there's a mac only solution right below it. 

**VideoClipsMaker** started out as a separate app but it soon became apparent I would need access to a videoPlayer to screen its output.  It includes the **opencv** functions, **assembler** and **ctrOnBackground**, used to make video clips based on reading either a directory of photos, the first frame of a directory of video files or every 'Nth' frame of a video.  **VideoClipsWidget** is the widget used by **clipsMaker** to select functions or set variables and **VideoPlayerShared**, as the name suggests, hosts a number go functions in common including the MediaPlayer, **getMetaData**, buttons and the slider setups.

## Four Files  
There are four **dots...py** files I'd suggest taking a look into  - **ControlView**, **ShowBiz**, **Shared** and **Screens** as they're backbone of how many of the actions are triggered and where the defaults are set. **ControlView** handles **drag** and **drop** and processes all the key stroke entries - except when **BkgMatte** has temporarily taken over. 

It also handles all/most of the multi-key function requests - the rest pass on to **Storyboard** which in turn passes them on either to **ShowBiz**, which handles most of the single key requests from **Canvas** and **Storyboard** through the **PlayFile** list, or on to functions that send keys to the current screen items to perform actions not already triggered. 

**Shared** is made up of lists and dictionaries that are shared throughout **dots** and **Screens** is responsible for most of the code and data used in reformatting and resizing **dots**. It now hosts four sub-classed entities in support of **pyside6**.

I recently made some code changes to **ControlView**, **ShowBiz**, **Storyboard** and others, not only to accommodate new additions but to clarify working processes as well. My code can change, especially if I think there's room for improvement.
       

## Files and Directories 
There are four directories to be aware of, **sprites**, **backgrounds**, **plays** and **paths**. **Sprites** and **backgrounds** are the directories where your stuff needs to go if you want to add your own material to **dots**. You can add any **videos** you plan to use to the **backgrounds** directory as they're treated as just another background.  

What I call a **sprite** needs to be **'transparent.png'** file and should be around **600 pixels square**. For **backgrounds** I'd recommend using a .jpg file and keeping it under or around **500MB** in size and formatting it to **640** pixels on the short side if you plan on scrolling it. I'd considered these to be the minimum required sizes.  You'll need to do some experimenting to find out what works best for your setup, especially if scrolling backgrounds.

If you have a current model iPhone, iPad, or Mac you may be able to generate a sprite using **Remove BackGround** as found in Preview Tools or in Photos on IOS devices by using your fingers or mouse to save a selection with the background removed. You also can look into using **SpriteMaker** in the **extras** dictionary. There's a write-up and a video for it. SpriteMaker requires **opencv-python** to generate a useable image.  Opencv is also used to create shadows and as an option in videoPlayerOne in helping to set the screen format used to display the video. 

The **plays** directory is made up of **.json** formatted **.play** files used to store **animated scenes** or **collage** data required to restore the last saved scene/canvas. Lastly the **paths** directory is used by **pathMaker** to store **.path** files - lists of screen point locations for building animated paths sprites can follow.

Along with these four directories there are the **demo, extras, images** and **src** directories.  The **demo** and **images** directories contain some photo assets and demo path files and are primarily used in keeping the **sprites** and **backgrounds** directories free of unnecessary clutter. 

The **extras** directory has been expanded and now hosts all the non dots source files. If it doesn't begin with **dots** it's there - **wrapper.py** as an example.

I would suggest looking into **Changes.md** to get an idea of how the various parts of **dots** work together. There are videos which cover the most recent additions while touching on the basics along the way. Unfortunately YouTube needs to collect its tariff for hosting these videos and you could get misdirected. That's not me trying to sell you something. 

---

If you're in **Windows** you won't need to edit the **paths** dictionary in **Shared**. That was my experience recently when installing and running **dots** on a **windows 11** laptop. It just worked other than having to set the path to include **site-packages** so python could find PyQt and anything else I've added.



    paths = {        
        'snapShot':     ',/../',  
        'bkgPath':      './../backgrounds/',
        'imagePath':    './../images/',
        'playPath':     './../plays/',
        'spritePath':   './../sprites/',
        'paths':        './../paths/',
        'demo':         './../demo/',
    }


## Menus and Their Locations  
There are five help *.py files and each one has a list of help files that details the location of each help menu.  Selecting **help Menus** from a help button menu will let you examine them all. Many of the help menus will let you click on line item to perform the function attached to the key you'd actually use. Not all do and I've tried to distinguish those.
   
## Widgets and Keys
A **right-mouse-click** on a **sprite, background**, **shadow** and in **pathMaker** from a blank canvas, will pop up a widget that provides access to the most often used functions such as scaling, rotation, scrolling controls or others, including a help menu, depending on what you've selected.

     There are a number of keyboard controls that either match the functions provided by 
     the widgets or add additional functions, especially if more than one sprite has been 
     selected. The right hand panel - the KeysPanel - is a scrolling list of the keys, 
     key combinations and their actions. The key assignments will change as you switch 
     between StoryBoard/Canvas and PathMaker or by entering 'K'. 

*The KeysPanel data has been replaced by the help buttons and menus and will eventually disappear.*

## Sprites, Backgrounds and Flats  
**Sprites** are added by drag and dropping them onto the **screen/canvas**.  **Backgrounds** are loaded by either entering **'A'** from the **canvas** or **'B'** if there are sprites but no background or clicking on the **Add** button.  Clicking on the **Color** button gives you a number options to create a solid color **flat** which is treated as a **background** except for scrolling. The **save** button that's next to the **Color** button saves the **flat** to a **.bkg** file whilst the **save** button in the **play** group will save **sprites**, **backgrounds** and **video** to a **play** file.


## Shadows
Are now on by default and requires that you've installed **opencv-python 4.12** or above. Running the left or right scrolling backgrounds demo will illustrate both **shadows** and **scrolling backgrounds**.


**Shadows** are created through the **sprite widget** and **right-clicking** on a shadow will trigger its widget which should take care most of the functions specific to shadows. **Double-clicking** on a shadow toggles the perspective controls (**points and outlines**) on and off.


## Scrolling Backgrounds
As of **August 2026** there's been a significant change and all previous bets are off. There's essentially one major variable you may need to change and that is **ShowTime** located in **BkgWorks** - it's currently set to 4. There you'll find two other variables, **RWY** and **VT5**, for making adjustments to vertical scrolling backgrounds once **ShowTime** has been set.   

Running a demo with a scrolling background will immediately inform you as to whether you'll need to make any adjustments. If there's a gap between backgrounds **ShowTime** needs to be set higher and if there's an overlap then lower.  Backgrounds are constantly being deleted and the data necessary to maintain the scrolling data is lost which is why I added **Trackers**.  There's a listview widget for trackers that lets you change the order on how multiple backgrounds are positioned front to back. Trackers don't track flats.


## Rates for Scrolling Backgrounds and Widget Controls 
You can pretty ignore the screen rate slider in the background widget as it's all based on code now rather than stored data and replaces any previous settings. The speed factor is a multiplier that can be applied to speed up or slow how fast the backgrounds scroll, its value is saved to the play file.

Scrolling backgrounds require different **rates** based on distance to travel and image size and are used to set the duration of the animation that drives the scrolling background. As the **first** background is already present it doesn't need to scroll as far to completely clear the screen view and it's rate is smaller compared to the **next** background which must travel further, starts off screen and travels its entire length.
   
The **ShowTime'** constant represents the number of pixels remaining before the current background is fully visible on screen.  When reached it triggers the **'next'** background process which creates a new background and sets it scrolling to seamlessly follow the background ahead of it.


## Background Matte Widget
Selected from the **background widget** the **BkgMatte** widget draws a mat/matte around the background. Its help menu pops up when first selected and can also be triggered by entering **H** from the keyboard which toggles it on or off.  The menu should be pretty much self-explanatory and there are videos that illustrate the commands as well.

This has been changed as well but marginally.  **BkgMatte** grabs the keyboard so it's best to plan ahead if you going to run an animation with a matte around it.

 
    helpKeys = {
        '>':    'Expand Matte Size',
        '<':    'Reduce Matte Size',
        'B':    'Black Matte Color',  
        'C':    'Change Matte Color', 
        'E':    'E/Enter to Close Menu',
        'G':    'Grey Matte Color',
        'H':    'Matte Help Menu',
        'P':    'Photo Background', 
        'Q':    'Close Matte', 
        'V':    'Vary Matte by Height',
        'W':    'White',
        'X':    'Close Matte',   
        'R':    'Run Animation'   ## the matte may cover the play buttons
        'Space': Pause/Resume'
        'S':    `Stop Animation'
    }

## Types
The types are **'frame', 'pix', 'bkg', 'flat', 'shadow', and 'video'** .  These are used to organize the screen items from front to back as I use the **QGraphicsitem zValue()** in combination with the types to order the scene items list. There are two functions, **toFront()** and **lastZval()** that help to make sure the different types I've created are good neighbors.  The types also determine how each row of data from the .play file is to be processed.  

The class attribute **type** is replaced in **PySide6** with **desc** as **pyside** appears to treat it as a function and tosses an error.

#### types and zValue range		
| scene.item  | type  | zValue |
|:------------- |:---------------:| -------------:|
| PointItem | pt | 100 from topmost item+ |
| MapItem | map | 50 over top pixItem |
| TagItem | tag|45 over top pixItem|
| Paths| path| 35 over top pixItem
| Frame | frame  | usually 1 zvalue above the top pix
| PixItem | pix  | **\*see below**
| Shadow  |shadow| 1 value below the sprite
| Points  |point | 40|
| Outline |  none   | 30| 
| LineItem  | grid   | -50 as a group |
| BkgItem   | bkg | -99 decreasing by -1 | 
| Flat    | flat | -99 or less than background 

  
**\** number of screen items + 100 decreasing by 1 per item


## A Brief History of Animation

**It's not advisable to attempt changes or make selections when running an animation as interesting and unwanted problems can occur.**   

You can create your own animation using **dotsAnimation.py** as a guide and add it to a sprite to run in **StoryBoard**.

**PixItems**, **BkgItems** and **BkgItems** have methods to **play, pause, resume and stop**. **Shadows** are not animated rather they can link to a **sprite** and share the ride.  **Wings** are also included as they're based on a collection of **PixItems**.  **Scrolling Backgrounds** have their own methods to set an animation but follow the  same **play** commands as do **videos**.

A note about **Wings** - it's been rewritten and is now a class rather than a function. It's made up of three **PixItems** each defined by their **part** tag. The bat portion **part** is named **pivot** and the wings **left** and **right**. The animation is applied to the **pivot** while the wings have their own **flapper** animations.  

Animations come in two basic flavors, either ones that are programmatic, you wrote some code, or ones that are path driven. **Paths** are created in **PathMaker** and are a means of moving a character around the screen. The ability to draw is not required. 

A third possibility would be a combination of the two such as **demo** in **dotsSidePaths**. An animation can be added to a screen object, a **PixItem**, once it's been selected by right-mouse clicking on it and choosing an animation or path from the **Animations and Paths** pop-up menu. The selection is applied to the **tag** property of the **PixItem** which later is used to run the animation it references.

The file **dotsSidePath.py** **loads** and the contents of a **.play**  and **path** files and also is the source for launching the **Demo Menu** items that feature bats. **DotsShowTime.py** can both **run** and **save** an animation to a file.
 
In **dotsSidePath.py** you'll find the **demo animation** path code, the function **setPaths** that creates paths from **.path** files plus the functions to **load** the path file and set the **node origin**. The code for the actual demos is divided between **dotsAbstractBats.py** and **dotsSnakes.py** which also contains the **Demo Menu** class.
 
The majority of the animation code is in the **dotsAnimation.py** file.  You can probabably skip what follows and save it for a later date as there's nothing here you'll need to deal with until you're ready to animate something. 


---


The first thing of interest in reading thru this file are the four variables, **AmnimeList, OneOffs, Stage, Spins**. The first two are lists which later are combined into one. These items reference the animations that are selectable and runnable from a pop-up context-menu. 

	AnimeList = ['Vibrate', 'Pulse','Bobble','Idle']
	OneOffs   = ['Rain','Spin Left','Spin Right','Stage Left','Stage Right']
	Stages    = ('Stage Left', 'Stage Right')
	Spins     = ('Spin Left', 'Spin Right')
	
You can add your animation to one of these lists so it appears in the pop-up menu.  Some of these animations take more than input variable.

The **Node** class provides the code used to control a **PixItem** property you might want to animate; **position, scale, rotation, or opacity**. They can also be combined to run in parallel or run sequentially as illustrated in some of the animations in this file.  This has been updated for **python 6.11**.  *Edited for brevity.*


     ### --------------------------------------------------------
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
    
        def _getPos(self):
            try:
                return self.pix.pos()
            except RuntimeError:
                return QPointF()
                
        def _setRotation(self, rotate):
            try:
                self.pix.setRotation(rotate)
            except RuntimeError:
                return None   
     
        def _getRotation(self):
            try:
                return self.pix.rotation()
            except TypeError:
                return 0.0 
    
        pos = pyqtProperty(QPointF,  fget=_getPos,  fset=_setPos) 
        rotate  = pyqtProperty(float, fget=_getRotation,  fset=_setRotation) 

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


        elif anime == 'Flapper':  ## bat wings
            return sidePath.flapper(pix)
         
        elif 'demo' in anime:  ## from BatsAndHats
            return sidePath.demo(pix, anime)
        
        elif anime in self.canvas.pathList:
            return sidePath.setPaths(anime, pix)
		...



You'll see these three lines in many of the animations that follow.  I mentioned the **Node** class earlier and here I'm creating a reference, **pos**, to the pix screen items current position, I'm also setting the **node's** point of origin based on the **PixItem**.  An animation function may **require** more that one **argument** which will need to be accounted for prior to using it.


    	def vibrate(pix): 
            pos = pix.pos()
            pix.setOriginPt()  
            pix.node = Node(pix)

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


Two other animations worth mentioning, **fin** and **reprise**, two of my little amusements. When you delete a **PixItem**, except for frames, I run **fin** which the scales the **PixItem** down in size, while rotating it and lowering its opacity before deleting it. When stopping an animation I run **reprise** to reposition screen objects back to their starting positions.  Carry overs from my original java program. 

---
### *Have fun*

