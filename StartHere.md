
### Last Update: 05/30/2024
       
---
**To Begin**  
This file presents an overview of **dots**. I've tried to cover what I feel is important and to give anyone reading this an idea of the how I see it. 

---
       
**Files and Directories**   
There are four directories that you should be aware of - **sprites** and **backgrounds**, **plays** and **paths**. **Sprites** and **backgrounds** are the directories where your stuff needs to go if you want to do something other than play with the **sprites** and **backgrounds** already there. 

What I call a **sprite** needs to be **'transparent.png'** file and should be around **600 pixels square**. For **backgrounds** I'd recommend using a .jpg file and keeping it under or around **500MB** in size.   Format it to **640** pixels on the short side if you plan on scrolling it. 

If you have a current model iPhone, iPad, or Mac you may be able to generate a sprite using **Remove BackGround** as found in Preview Tools or in Photos on IOS devices by using your fingers or mouse to save a selection with the background removed. You also can look into using **SpriteMaker**. There's a write-up and a video for it.

The **plays** directory is made up of **.json** formatted **.play** files used to store **animated scenes** or **collage** data required to restore the last saved scene/canvas. You'll also find the **screenrates.dict** file used by scrolling backgrounds there as well. Lastly the **paths** directory is used by **pathMaker** to store **.path** files - lists of screen point locations for building animated paths sprites can follow.

Along with these four directories there are the **demo, extras, images** and **src** directories.  The **demo** and **images** directories contain some photo assets and demo path files and are primarily used in keeping the **sprites** and **backgrounds** directories free of unnecessary clutter. 

The **extras** directory contains **outline.py** and **dropShadow.py** and the  **spriteMaker** directory. In May 2024, I posted a short video that reintroduces them. There are earlier videos as well.  

I would suggest looking into **Changes** to get an idea of how **dots** works. These videos cover the most recent additions while touching on the basics along the way. Unfortunately YouTube needs to collect its tariff for hosting these videos and you could get misdirected. That's not me trying to sell you something.  

---
    
**Three Important Files**   
There are three files I'd suggest looking into - **dotsControlView.py**, **dotsShared**, and **dotsScreens.py**. **ControlView** handles **drag** and **drop** and most of the key stroke entries - except where it doesn't such as in **Matte**.  **Shared** is made up of lists and dictionaries that are shared throughout dots and **Screens** contains all or most of the code and data used in reformatting and resizing **dots**.


If you're in **Windows** you'll probably need to edit the **paths** dictionary in **dotsShared.py**.


    paths = {        
        'snapShot':     ',/../',  
        'bkgPath':      './../backgrounds/',
        'imagePath':    './../images/',
        'playPath':     './../plays/',
        'spritePath':   './../sprites/',
        'paths':        './../paths/',
        'demo':         './../demo/',
    }



I've recently changed the directory layout for **dots** by moving the **dots\*.py** files to **dots/src**. The following script is working for me using Mac's Automator.  It also required some setting of permissions as I had added an additional login.


    cd '/users/your directory/python/qt5/dots/src'; /usr/local/bin/python3 ./dotsQt.py      
    
---

**Menus and Their Locations**   
The menus for **Animations and Paths**, **Demo Menu**, **HelpMenu** and the **Screen Menu** are in **dotsMenus.py**.   

**From a blank canvas screen** you can trigger the **helpMenu** by entering **H**.  These single-key commands will work if the **screen/canvas** is blank.

    'A':    'Add a Background', 
    'B':    'Add a Background', 
    'D':    'Display the Demo Menu',
    'H':    'Canvas Help Menu',
    'J':    'JSON File Viewer',
    'L':    'Load a play file', 
    'P':    'Switch to PathMaker', 
    'R':    'Display the Demo Menu',
    'S':    'Display the Screen Menu', 

    'C' clears the canvas
     The 'PathMaker' button enables a program with a program to draw a paths used to animate a sprite.
    
---

**Widgets and Keys**  
A **right-mouse-click** on a **sprite, background**, **shadow** and in **pathMaker** from a blank canvas, will pop up a widget that provides access to the most often used functions such as scaling, rotation or scrolling controls.

There are also a number of **keyboard** controls that either match the functions provided by the widgets or add additional functions, especially if more than one **sprite** has been selected.  The right hand panel is a scrolling list of the keys, key combinations and their actions. The key assignments will change as you switch between **StoryBoard/Canvas** and **PathMaker** or by entering **'K'** from the keyboard . **Canvas** and **pathMaker** don't interact with each other but you can access **backgrounds** once **pathMaker** is active.

---

**Sprites, Backgrounds and Flats**  
**Sprites** are added by drag and dropping them onto the **screen/canvas**.  **Backgrounds** are loaded by either entering **'A', 'B'**  or clicking on the **Add** button.  Clicking on the **Color** button gives you a number options to create a solid color **flat** which is treated as a **background** except for scrolling. The **save** button that's next to the **Color** button saves the **flat** to a **.bkg** file whilst the **save** button in the **play** group will save **sprites** and **backgrounds** to a **play** file.

---

**Shadows**   
If you would like to try out **shadows**, besides downloading and installing **numpy** and **opencv**, you'll need to make a small edit in **dotsPixItem.py** to comment out an import and uncomment another.

    from dotsShadowMaker    import ShadowMaker  ## add shadows
    ##from dotsShadow_Dummy    import ShadowMaker  ## turns off shadows
    
An easy test is to run a left or right scrolling demo once you've downloaded, installed and edited the comments. If you see 5 shadows it's working. 

**Shadows** are created through the **sprite widget** and **right-clicking** on a shadow will trigger its widget which should take care most of the functions specific to shadows. **Double-clicking** on a shadow toggles the perspective controls (**points and outlines**) on and off.

---
    
**Scrolling Backgrounds**  
I've moved the really gnarly stuff concerning scrolling backgrounds to the **screenrates.dict** in the **play** directory. Its contents are the two dictionaries, **screentimes** and **moretimes** which I've commented out in **BkgItem.py** and left as a reference. The **screentimes dictionary** handles the **16:9** formats while the **moretimes dictionary** takes care of the **3:2** formats.  You can mix formats if you use the **3:2** format to display them as each **background** is tracked separately. 

**Screentimes** and **moretimes** still provide the defaults for the **scrolling backgrounds screen rates** even though they're no longer tied to the code in **BkgItem.py**. By adding the **ScreenRate** slider to the **background widget** you're now able to adjust the rate and if the new rate is a better fit you can save it as the new default to **screenrates.dict** using the **update button**. The current **screen rate** value as well as the **factor** and **showtime** values are carried over if the **background** is saved to a **.play** file.

Running a demo with a scrolling background will immediately inform you as to whether my best guess on **screenrates** was correct or not.  Probably not, which is why the demo background, **bluestone.jpg**, is in the **backgrounds** directory. As it's the same background used in the demos - once you've got the background to scroll smoothly the demo will do the same. Some of the bat demo backgrounds are also now read from the backgrounds directory as I've deleted the three same named files from the demo directory.

**Scrolling Backgrounds** are constantly being deleted and created and the data necessary to maintain the scrolling rate is lost between the two which is why I added the **newTracker** dictionary in **dotsBkgMaker.py**. Tracker data doesn't change unless there's a change in direction or to a control and it's saved between sessions when saving to a **.play** file.

    tmp = {
        "fileName":   os.path.basename(bkg.fileName),
        "direction":  bkg.direction,
        "mirroring":  bkg.mirroring,
        "factor":     bkg.factor,
        "rate":       bkg.rate,
        "showtime":   bkg.showtime,
        "useThis":    bkg.useThis,
        "path":       bkg.path,
        "scrollable": bkg.scrollable,
    }

---

**Rates and Background Widget Controls**  
The **rate** is a list of three values each of which I also refer to as a rate.  The first value, **10.0**, is the **first screen rate**, the other two values are the rates for **next-left** and **next-right**.  The **first** background doesn't have to travel as far to exit while the second background, **next** has to wait its turn till it's **showtime** and then match the speed the **first** is traveling without gapping or overrunning it. Once **first** has exited the screen the backgrounds that follow are now all **next** and shouldn't require further adjustments.

Moving the **background widgets screenrate slider** to a higher value slows the backgrounds speed and a smaller value will speed it up. Once the **next screenrate** has been established and the background is scrolling smoothly you can use the **factor** dial - it's a multiplier - to speed up or slow down the backgrounds travel without changing the sliders rate or needing to edit **screenrates.dict**.  The **factor** value is saved to the **.play** file as well.

These values were established based on a fixed size which isn't as important as it once was as you now have more flexibility in setting a rate that best fits your background.  Scaling the short side to 640 pixels still helps.
   
    screentimes = {  ## based on a 1280X640 .jpg under .5MB for 16:9 background
        ##   first, next-rt<lft, next-lft>right --- there are always two backgrounds once started
        '1080':  [10.0,  17.50,  17.45],     ## 1440px actual size when scaled 1280X640 for 16:9
        '1280':  [10.0,  18.75,  18.85],  
        '1215':  [10.0,  17.35,  17.4],     ## 1620px actual size when scaled 1280X640 for 16:9
        '1440':  [10.0,  18.7,   18.85],
        '1296':  [10.0,  17.50,  17.45],     ## 1728px actual size when scaled 1280X640 for 16:9
        '1536':  [10.0,  18.65,  18.60],  
        '1102':  [10.0,  20.9,    0.0],
         '900':  [10.0,  23.2,    0.0],
         '912':  [10.0,  20.9,    0.0],
    }
       
I use 10.0 for the **'first'** value as the background is already visible and needs to travel less of a distance to **clear the screen**. The **'first'** value 10.0 translates to 10 times the screen width and is used to set the duration, time in milliseconds, required to move the backgrounds scaled width from one side of the screen to completely off the other.  A 1080 pixel screen format for the **'first'** background translates to 10.0 X 1080 = 10,800 milliseconds to clear the screen.  A **'next'** background has to cover more distance and therefore its rate would be higher and results in a longer duration, more travel time, while also matching the **first** rate of travel.   
      
The **background widgets 'showtime'** slider value represents the number of pixels remaining before the background appears in the scene.  When reached it triggers the **'next'** background process. This will vary depending on which direction the background is traveling and if it's a snake. It's set once you choose a direction. Hopefully you'll never need to edit showtime, but if you do it's in **dotsScrollWrks.py**.

---

**Background Matte Widget**  
Selected from the **background widget** the **matte widget** draws a mat/matte around the background. Its help menu pops up when first selected and can also be triggered by entering **H** from the keyboard which toggles it on or off.  The menu should be pretty much self-explanatory and there are videos that illustrate the commands as well.

 
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
        'R':    'Resize Matte by Height',
        'W':    'White',
        'X':    'Close Matte',   
        'Shift-R - Run Animation'   ## the matte may cover the play buttons
        'Space   - Pause/Resume'
        'Shift-S - Stop Animation'
    }

---

**Types**  
The four main types are **'frame', 'pix', 'bkg'** and **'flat'**.  These help to organize the screen items from front to back as I use the **QGraphicsitem zValue()** in combination with the types to order the scene items list. There are two functions, **toFront()** and **lastZval()** that help to make sure the different types I've created are good neighbors.  The types also determine how the data is to be processed.

#### types and zValue range		
| scene.item  | type  | zValue |
|:------------- |:---------------:| -------------:|
| PointItem | pt | 200 from topmost item+ |
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

This was in **ReadMe** but it fits better here:

---

### A Brief History of Animation

---

**It's not advisable to attempt changes or make selections when running an animation as interesting and unwanted problems can occur.**   

**PixItems**, **BkgItems** and **BkgItems** have methods to **play, pause, resume and stop**. **Shadows** are not animated rather they can link to a **sprite** and share the ride.  **Wings** are also included as they're based on a collection of **PixItems**.  **Scrolling Backgrounds** have their own methods to set an animation but follow the  same **play** commands.

A note about **Wings** - it's been rewritten and is now a class rather than a function. It's made up of three **PixItems** each defined by their **part** tag. The bat portion **part** is named **pivot** and the wings **left** and **right**. The animation is applied to the **pivot** while the wings have their own **flapper** animations.  

Animations come in two basic flavors, either ones that are programmatic, you wrote some code, or ones that are path driven. **Paths** are created in **PathMaker** and are a means of moving a character around the screen. The ability to draw is not required. 

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

Two other animations worth mentioning, **fin** and **reprise**, two of my little amusements. When you delete a **PixItem**, except for frames, I run **fin** which the scales the **PixItem** down in size, while rotating it and lowering its opacity before deleting it. When stopping an animation I run **reprise** to reposition screen objects back to their starting positions.  Carry overs from my original java program. 


Have fun

