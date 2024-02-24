### Changes

---
           
Before all else I'd like to thank those individuals who were kind enough to award me a star.  I'm sorry for being so late in acknowledging you. It means a lot to know that my efforts have found a home somewhere.  Your stars are very nice early birthday present.  Thank you once again.    

---
                          
**February 22 2024**    
I decided to tackle a few things on my todo list and finally got around to fixing the **'missing file'** recovery problem.  I used **QTableView** to display the contents of the **json .play file** and highlight any missing files as well as providing a means to delete them.  In the past when a missing file was encountered you were returned to the canvas and not able to access the **.play file** until you either managed to come up with the missing file or a like named substitute - or, editing the **.play file** with something like **text-edit**, which can work if there's only one file to delete or rename. As a rule, the only way a missing file comes about is you either deleted it, renamed it, or moved it as **dots** expects a particular screen type to be in a designated directory.

I went through a number of revisions of **dotsTableView.py** until I finally arrived at what's here. It helps to have a plan, I have written that before.  **TableView** is in part, is the result of a number of searches on **StackOverFlow** and dives into **Martin Fitzpatrick** online examples, both of which were instrumental in filling in the gaps. The rest of it - mostly trial and error and OJT.

As a reminder, **'J'** is the command that launches the **json .play file viewer** which also works in **StoryBoard** - where the work gets done.  Saving a **.play file** with missing files in **StoryBoard** will delete them as it saves only what's displayed while saving from the **canvas** saves what's in the file including the missing file records. 

**February 23** - Added **'S'** to **save** the **.play file** in **StoryBoard** if there are no animations running. Why I didn't do that two years ago is a good question.  Made sure typing **'J'** to launch the file viewer won't work if an animation is running.   

Here's an interesting something to be aware of. If you turned **shadows on**, did some stuff, saved it and then turned **shadows off**  it could be an issue in the future if you went to reload the file and **shadows** were still **turned off**.  The data that describes the shadow will disappear as the imports, **numpy** and **openCV**, required to build a shadow aren't found. It hasn't been a problem for me as it's always on in development and turned off on GitHub except for testing.

New Video: <https://youtu.be/DoCMdEPZi8E>

---
                          
**January 2024**       
A repeat of January 2023. A few bug fixes and mostly trying to clarify my code by clearing up some naming issues and moving code around. Added some new files and renamed a few to make it easier to locate some classes which may have been hidden.



---
**December 1 2023**  
That was fast.  I had made some small changes to the vertical screen code and posted them to GitHub when I noticed one of the files hadn't made it.  It turns out five files, going back two months or so hadn't made it either.  They were somehow tagged to the **gitignore file**, a few, many times over.  I'm very glad I found it and sorry for any difficulties it may have caused.  Something to remember.  

**December 2** - The next day, a bug fix to scrolling directions.

A reminder: scrolling backgrounds need to be tailored to your os/computer/python/pyqt environment by adjusting the values in the **showtime** and **moretimes** dictionaries in **BkgItem.py**. From what I can distill from the Qt.io docs, there's no frames per second method that would do away with my approach to scrolling backgrounds, at least for now. 

**December 7** - Renamed **SideWorks** to **ShowWorks**. Did some work on **PathChooser** so it  now works better if no path files are found. Applied the changes to the demos as well. Updated MacOS to **Sonoma**. The **CATransaction sync** problem seems to be gone - there's something else in its place.  It may have the same effect - that is, locking the app.

     Python[4447:75880] WARNING: Secure coding is not enabled for restorable state! 
     Enable secure coding by implementing
     NSApplicationDelegate.applicationSupportsSecureRestorableState: and returning YES.
     

**December 30** - Added **Duration** and **Showtime** to the **Background** widget replacing the **Scale** and **Rotate** controls as I can't remember needing to use them.  The new controls make it possible to make adjustments to the values pulled from the dictionaries in **BkgItem.py**  without having to edit the underlying code. Works for me.  Just remember to save the background in a **.play** file using the **Play Save Button** and not the **Background Save Button**.  

Now that it's easy to make adjustments to the next backgrounds duration settings I think it may be possible revisit my initial suggested formats and just stick with scaling the background to 640 pixels on its short side and letting the long side go - staying close or under a 2:1 or 1:2 ratio.  The 350kb.jpg file size is still recommended unless it's a transparent .png. I should also mention that the values in the three dictionaries were derived based on the either a 1280X640 pixel file or a 1080X640 file.  Your results may vary.

New Video: <https://youtu.be/7cdPFkifbC8>

---
**November 2023**       
A bug fix to the demos scrolling backgrounds and a change to the scrolling default from **Mirrored** to **Continuous**.  The default is set in **BkgMaker.py** as is the **trackers** list used to track and update backgrounds. I also removed the **keyboard commands** in backgrounds used for setting the scrolling direction and the key command to trigger the matte as they're now both in the widget.     
  
And since November 3, additional changes to scrolling backgrounds and two new screen formats. I suggest looking at **StartHere.md** which now has an entry detailing how scrolling currently works and where the numbers in the **screentime** and **moretimes** dictionaries come from and why. It may help explain things. It was originally in **BkgItem** and has been moved and updated.

The **3:2** format now works for scrolling background photo assets that are closer to a **3:2** format by resizing them to **1080X640** rather than the **1280X640** used by the **16:9** format.  Also added, a new widget control, **'Factor'**, that modifies how fast a background moves across the scene and two vertical screen formats. The first is a **2:3** format sized to **600X900 pixels** followed by a **9:16** format sized to **513X912 pixels**, both designed to work on displays of 1080 pixels in height. 

Other than resizing a background to either **1080X640** or **1280X640** the only other requirements are to keep the file sizes under 500K and no duplicate background file names.

Upgrading to Python 3.12 and PyQt6.6 changed the timing in scrolling a bit but it may not mean much in the long run.

New video: <https://youtu.be/aknawo7igVs>

---
**October 2023**        
The 'Save' button in the Backgrounds group will now save only 'flats', full color canvases.
To save a scrolling background you need to save it to a play file - that way you preserve your settings.  I've added another scrolling button, **'Mirroring On/Off/Not Scrollable'**. The default has been Mirroring On from the beginning as I didn't have any pre-made scrolling backgrounds and I liked the mirror effect. I decided now that I can scroll more than one background at a time I should add scrolling without mirroring and see where that goes.

Most of the Halloween demo is not mirrored. I think it should be possible use parallax scrolling backgrounds in dots as long as they've been scaled to **1280X640**, that's all I did for the desert demo section. I've also added some behind the scenes methods to insure I not saving any duplicate backgrounds.  My original method wasn't working as well it should, once a scroller animation starts there will almost always be two backgrounds present, visible or not. 

The Halloween demo also used a random value , 'factor/fact', between .85 - 1.50 by .05 to vary each backgrounds time needed to move one screen width.  It can be found in **BkgWorks.py** in the **'addTracker'** function.  I've commented out the random generator and set the default **factor** to 1.0.  Make sure you have a workable example(s) before commenting it out.

New video: <https://youtu.be/Eu3OqKjtBgw>

Last, here's the url for where I found the scrolling background I used, <https://www.artstation.com>, it was free and a needed visual aid.

---

**September 30 2023**   
Fixed a few embarrassing bugs which caused some keys and key combinations
to fail as well as a sure kill lurking in PathWays code. I've also turned off most of the garbage collection as it seems to be connected to an emergent problem when running on the desktop.

**September 21 2023**  
About two hours after I posted my last effort to GitHub and YouTube I had a moment of clarity and decided I should try using something like the translate transformation rather than the parent/child method I was currently using in order to link the shadow. I replaced it by using an **offset** variable located in **pixItem**. It seems to be the right choice and without any of the previous issues.

You'll need to **unlink** the shadow before making any **additional** changes for scaling or rotation but not for opacity. I've made this easier by **not closing** the widget when you click on **'UnLink'** - big win.  The shadow is no longer linked, the widget hasn't gone away, the shadow outline now appears and the unlink button now reads **'Link'**.  Make your changes, **Relink** the shadow and you should be good to go.  

There's more.  Added two buttons to the **BackGround** widget, one to set the **background scrolling** left to right, the other right to left, plus a button to open the **Matte** widget. That adds three more keys to the mix, **shift-R** to run anything runnable, **shift-P** to pause and resume it, and **shift-S** to stop - but only if the **Matte** is displayed which requires there's a background present.

Lastly, changes to the **scrolling background** making it possible to have two running at the same time in the same or opposite in directions.

There are three problems I've encountered recently. The first was with **QMessageBox** not displaying correctly in PyQt5.  The second, a known Apple/Python bug [:] **+[CATransaction synchronize] called within transaction**, can cause dots to end abruptly, at least on my M1 Mac running Ventura. The third one, a shell error when running dots on the desktop. They all seem to have started with Ventura.

New video: <https://youtu.be/FZTsYaU3Eiw>

---

**August 2023**   
A few more key changes; **'O'** now toggles shadow outlines on and off rather than just off -
**'Shift-O'** now hides shadow outlines. Some bug fixes and a **link** added to shadows that allows the shadow to follow a pixItem when the pixItem is either moved or animated. This works as expected as long as the pixItem hasn't been rotated or scaled.  **Changed - see September and it's video.**
  
    PixSizes = {  ## match up on base filename using 5 characters - sometimes called chars?
        # "apple": (650, 450),  ## see setPixSizes below if you need more to add more chars
        'doral': (215, 215),
    }
    
**No longer necessary**. Scaling up or down can be handled without triggering any issues by editing the **PixSizes** dictionary in **dotsPixWidget.py** and setting the size there rather than using the slider in the pixItem widget as scaling is applied to the pixItem before it hits the canvas.  **No need to watch this video see the next video instead.** Also added a button to the pixItem widget to launch the **Animation Menu** and a slider to the pathMaker widget to change the number of seconds it takes Mr.Ball to complete a circuit around a path. The default is 10 seconds.

New video: <<https://youtu.be/FFn2sq3R3nU>>

Of note: I tried running dots in PyQt5 and ran into a problem with QMessageBox taking up an excessive amount of screen space and no longer being very usable - at least on my Mac.  Too many moving parts to know where to begin.
  
---

**July 2023**   
Renamed dotsShadowWorks.py to dotsShadowWidget.py. Bug fix on Flats.  Updated **Start Here**.

---

**June 2023**       
Just repeating myself. I said in the last video you needed to save a background in a **.play** file in order to run it, **you don't**, programming error. Some small changes to the **demoMenu** and the **sprite scrollPanel**. I was able to add another sprite, clean up some code and remove a few no longer needed screen variables by reducing the size of the **scrollPanel** tiles. 

The **demo .paths** and **Snake photo assets** are now in a separate **demo** directory so as not to clutter things up.  All the **demo .play** files have been replaced by **dotsAbstractBats.py** which also houses a rewrite of **Wings**. That helped to fix the primary issue of being able to pull the wings off as well as another issue - the wings going invisible if the bat did.

Last is the addition of what might be thought of as a digital **Matte** to better show off your efforts. It currently features light grey as the default border color, black and also a photo/image for the matte.  The border sizes run from 5-12-25 pixels and up by 25 pixel increments.  It's also possible to change the a mattes overall ratio to better accommodate wider screen formats.      

I guess I'll be adding some more keys to **Keys.pdf** to cover it. All you need to do to add a matte is hold down the **'opt/alt'** key or it's replacement and click on the background. A 25 pixel border pops up so you can start an animation without interfering with the matte.  Use **'opt/alt' or 'X'** to leave. The **Matte widget** grabs the keyboard and can act as if you had a piece of glass floating over the screen, my humble opinion.  Other keys, **'<'**  and **'>'** to change the border size, **'C'** will change the matte color from light grey to black and back. '**P'** will display a photo image in the matte border and **'R'** will reformat the matte to a wider format.  Feel free to experiment.   

**New video at:** <https://youtu.be/XHc5NGJ86NE>

---


**May 31 2023**      
Trying again.  I came to realize why I had to change directory settings and such.  VSCode needed to start in the src directory and it kept putting me in the old directory. Finally I saw the light and reset the workspace to put me into the correct source directory. Sorry for the confusion - I'm not sure how I set it up in the first place but that was over two years ago. DotsShared,py and DotsQt.py are back to the way they were and so are the automator scripts with the /src addition.


        cd '/users/ml/python/qt5/dots/src'; /usr/local/bin/python3 ./dotsQt.py
        

**May 29 2023**     
~~I needed to edit the paths in dotsShared,py and dotsQt.py once I relocated the *.py files to the /src directory in order to locate the other directories. A problem soon developed and I think it's been resolved.  The following script is how Mac's Automator launches Dots on my Mac. It's probably a good guide as it works for the development script as well.~~

~~cd '/users/ml/python/qt5/dots'~~      
 ~~/usr/local/bin/python3 ./src/dotsQt.py~~  
        
A retraction: I said in the last video you needed to save a background in a .play file in order to run it, you don't. I was wrong - I had shut off that feature by accident it's now restored.
        
**May 28 2023**     
Moved dots*.py to src. I think my GitHub landing page was getting overcrowded and I have a few more files to eventually add.
 
**May 27 2023**     
Renamed dotsDrawsPaths.py to dotsPathEdits.py.  What was I thinking.  

**May 26 2023**        
Moved the Screen Formats Menu to dotsScreens.py and the Demos Menu to dotsSnakes.py. I've also added the appropriate messages to fill-in what I left out earlier.

**May 23 2023**      
Upgraded both PyQt5 and PyQt5 to their latest versions as of the first week of May 2023.  I've also updated to the latest version of Ventura.  Seems there's a bug between Python 3.11 and Ventura.  Here's a sample, it doesn't show on the desktop. I followed some suggested fixes and it seems to cut down on the occurrences but it hasn't gone away.  It also didn't go away with Ventura 13.4.

    **Python[976:11264] +[CATransaction synchronize] called within transaction** 
       
I've also made a few key changes that I should have made in the first place. The **Screens Menu** is now just plain old **'S'** on a blank screen and **'R'** that used to run the **batwing** demo now displays the new **Demos Menu**. In March I added **'Option/Alt R'** to run the **Snakes** demo which is now a selection on the **Demos Menu** so its services are no longer required. Not all demos work across both screens. I'll be removing the ones that don't the next time around. 

There's more, **Scrolling Backgrounds**.  You'll need to get into the code to tune it for your hardware as it's based on magic numbers which will vary from computer to computer.

```
abstract = {  ## used by abstract.jpg and snakes.jpg - based on 1280X640 2:1 - under 1MB
    '1080':  (10.0,  17.4,  17.55),  ## first, next, next-right
    '1280':  (10.0,  18.85, 19.0),
    '1215':  (10.0,  17.4,  17.4),  
    '1440':  (10.0,  18.9,  18.95),
    '1296':  (10.0,  17.45, 17.55),  
    '1536':  (10.0,  18.95, 18.95),
    '620':   (10.0,  20.9,   0.0),
    }    
```     
This dictionary is located in **dotsBkgItem.py**, the background screen item.  There are two other dictionaries, one for wider formats, only one entry so far, and one that acts to trigger a new background.  

Scaling the background to a **2:1 ratio, 18:9**, will cover the widest screen format and also leave an out-of-view overage. I call that overage the **runway** as it gets shorter as the background moves.  The shorter the runway the fewer pixels remain before the **runway** goes to zero and the background is no longer covering the full screen as it moves. The moving background is continuously updating its position based on setting the flag below to True - it happens on its own just before the background animation starts. The updated position is used in recalculating the number of remaining out-of-view pixels. The value of **runway** is also used to position backgrounds whose default screen positions are other than (0,0).
  
```
 self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, False)      
```

There's a complimentary variable to **runway** which I've named **showtime**. It's the number in pixels used to **trigger** a new background and animation when matched by the remaining number of hidden pixels. It's was easier for me to count pixels then compute a trigger in milliseconds.


 **Showtime** can vary based on the direction the background is moving and also what the animation is consuming in resources. For example, **showtime** for **snakes** is **10**,  **scrolling** a background to the **left**  is **4** and **scrolling** a background to the  **right** is **15** on my MAC. **Showtime** controls how all the backgrounds other than the first background line up. Too large a setting will cause them to gap while too small a setting will cause them to overlap. The setting that works the best has one background following the other seamlessly. The **showtime** values don't appear to change as the screen formats change. 

I strongly recommend getting **showtime** settled first as well as keeping the background size **under 1MB** and saving it as a **.jpg**. It's also a good idea to choose a background that's not overwhelmed with detail as too much detail can cause the background to scroll slowly.  One other thing, these's no need to recreate all of the format settings to get this working, just pick one screen format and see about getting the abstract.jpg to scroll smoothly.  
    
The first column values are all 10.0. **Ten** times the screen width or height translates to how many **milliseconds** the first background's **duration** is set - the time it takes to scroll the background past the edge of the screen. I did that to eliminate one other variable to fuss with, one I could return to once I had everything running. The second column sets the **duration** for all the backgrounds other than the first. The same considerations for **showtime** apply here as well.  Too big a value and the backgrounds will run slow and will gap between the first background and the next.  Too small a value and the next background will overlap the first as they're both moving across the screen in the same direction. The third column is for scrolling left to right, the same stuff applies. Eliminating gaps and overlaps should result in a possible 'Rorschach' like image as I flop alternate backgrounds.

There's no handy scrolling widget but it's easy to set the direction by first holding down either the left or right arrow key and clicking on a background.  if the background image's ratio is **2:1** or  greater you'll get a message confirming the direction you've chosen, otherwise it won't work.  The next step is to save it with the **play** save button and not the **background** save button. Animations can only be run from a **play** file which is why I chose to write the scrolling routine as I did so it would play nice with the other animations in being able to **run**, **pause, resume**, and **stop** using the app play buttons.

**New video at:** <https://youtu.be/E-1Mzau2KBw>
        
**Further Notes:**     
The cloud from my video isn't included - I'm sorry to disappoint you.  But here is some data about it that might be useful.  It's based on a 5MB .tiff, some 5000 pixels in width. I scaled it down
to 1500X500 pixels, res'd it down to just over 250KB and saved it as a .jpg.
 
        
---

**March**   
This months **bonus**; **page up** and **page down** keys on the scrolling sprite panel by entering **Option/Alt**  plus the **Up/Down Arrow** keys. Also, **one tile Up** and **one tile down** with the Apple Command key/Windows Control key plus the **Up/Down Arrow** keys. Also, with enough sprites, if a partial tile is showing it will scroll down till it's fully visible.

I've updated two of the **3:2** screens so their height now matches the height of two of the **16:9** screens, eliminating the 1350 and 1432,  which makes maintaining the **3:2** much easier. Sorry for the confusion again, but this is what happens when you don't have a clear plan. I've also revised some of the changes from **February** to reflect the current screens sizes - many of the earlier changes still hold.
  
| key   | format |
|:---- |:-----------:|
| 1080 | 1080X720 - 3:2|
| 1280 | 1280X720 - 16:9 |
| 1215 | 1215X810 - 3:2 |
| 1440 | 1440X810 - 16:9 |
| 1296 | 1296X864 - 3:2 |
| 1536 | 1536X864 - 16:9 |
| 620  | 620X1102 - 9:16|

Also, there's a new demo of sorts which I call **'Snakes'** - though they're more of a cross between a woolly-bear and something like an aquatic snake.  It's accessed by entering an **Option/Alt R**. The **pause, resume,** and **stop** play keys work and you can re-run it by entering **'R'** once it's stopped.  There's no **play** file to save as it's all code except for the three cactus images.
I also fixed the sometime problem of saving path files to the wrong directory. Dots still runs in 5.17, look for the necessary edits below. 
A new video: <https://youtu.be/hFfXc0H2oZM>.

---

**February 23 2023**      
Added a **1440-16:9** format plus some cosmetic code fixes.  See the revised **02/10/2023** entry for more about screen formats. See **Even More** for updates to **paths** and **widgets** after the following **'New Screen Formats'** entry.  There are also two videos.


**February 10 2023**  
Added some **New Screen Formats** and sizes made accessible by entering **Shift-S** to bring up the **Screen Formats menu**. What happens next depends on your computers display. Worse case the selected size is wider than the number of pixels your computer can display and outside of the software limits to detect it. The result would have the app overflow the edges of your screen making **dots** possibly unusable. I make a point of this in the video by explaining how the position of the dock can effect whether the program interprets the screen size correctly. The dock knocks off around 50 pixels from the useable display width or height based on where it's positioned - that's on my Mac. Results will vary depending on your hardware, see the video for a further examples.         

This table represents the **screens** dictionary in **dotsScreens.py** used to build the **Screen Formats menu** and everything else that affects the screen sizes and layouts.  The numbers in the **key** column are the widths associated with the format.

If there's a particular format you rather have as the default other than 1080, you can easily write a simple shell script to manage that by adding a key value as in the example below. Mistakes or nothing added default to the 1080 format. Additionally
each screen format has it's own demo play and path file identified by **'demo-'**
followed by the the format key, ie., demo-1440.play, demo-1440.path. Entering **R** or clicking on the **Run** button will run it.

     % python3 ./dotsQt.py 1440       
     
**February 10 2023 - continued**  
Removed the **VHX** pixel ruler **Shift-V** start key as I was having some difficulty in getting it to run from my desktop **dotsQt app**. The simple solution was to add the **VHX** desktop app to the dock/taskbar.
Also, just after I recorded the accompanying video I decided to try and shave off some pixels from the scrollPanel by cutting back on the width of the image tile and in the sliderPanel, reducing the font size.  The result is the two panels in the video are slightly wider and the tiles in scrollPanel less square from what you would see when running dots. Lastly, I'm running Python and friends in **Rosetta** and have no complaints, especially when it comes to launching dots, and particularly when it's importing numpy and open-cv.  New video at: <https://youtu.be/-mpV2f8Qj6w>


**February 10 2023 - Even More**  
Since I posted the changes for **'new screen formats'** I've a made few more adjustments. The first being, addressing what would happen if the **'demo-' path** file was missing?  The result, the bats will be the only moving screen items, dots wouldn't crash. The second change has to do  with ensuring the bats or any other screen item following a path can cover the canvas width and height as the 1080 format is currently the source of all of the **'non-demo paths'.** For that I added two more variables , **'scaleX', 'scaleY'** to scale up or down paths based on the 1080 screen format, its' **scale..** settings defaulting to **1.0, 1.0**, essentially, do nothing, unlike the other screen formats. Paths beginning  with **'demo-'** aren't effected. The third and last change, keeping the **pixItem** and **shadow widgets** closer to their source even if the screen format shifts together with changes to the **background** and **pathMaker widgets** so they appear in a fixed starting location regardless of the format or screen size. See the **'widget' and 'bkgrnd'** variables/keys and the following video. <https://youtu.be/2iqnlGBLCso>

---
                          
**January 2023**       
A few bug fixes and mostly trying to clarify my code by clearing some naming issues.


---   
**December 2022**      
Added a few more widgets, one to **backGrounds** to replace the sliders originally located on the right hand panel - the space now extends the **keys menu/list**.  I've also added a widget to **pathMaker** to give easy access to the major path functions, files, edit, delete, new path, and waypoints. Also in pathMaker the **W** key that toggled **wayPoints** on and off has been replaced by the **shift-W** combination as to not interfere with the **W** key now used to clear widgets. Video: <https://youtu.be/9i8w6DsY1Ys>

Repeating myself a bit, to run **Shadows** requires an easy edit to **dotsPixItem.py** by commenting on and off two lines near the top of the file. **Open-cv** and **numpy** are required to run both **Shadows** and **SpriteMaker**. 

```
# from dotsShadowMaker    import ShadowMaker  ## add shadows
from dotsShadow_Dummy    import ShadowMaker  ## turns off shadows

```

**Other Stuff:** **VHX** now expands and contracts evenly end to end. Though I didn't demo it, you can now delete paths directly from **PathChooser** by holding down the delete key and clicking on the path. Also, see **SpriteMaker.md** for the latest news, especially if you own a later model **iPhone**.         

**Lastly**, there's sort of an easter egg, real easy to spot, in **dotsQt.py**.

---

**November 2022**      
Renamed **dotsDropCanvas** to **dotsStoryBoard**, **dotsBkgItem** to **dotsBkgMaker**. The **StoryBoard** change affects the file name while continuing to maintain the reference thru **.canvas**.  **BkgMaker** goes a little deeper with both file and reference changes - though not many. 

---

**October 2022**        
**Dots** updated to **PyQt 6.4**, **PyQt5.17** and **Python 3.11**. 
**Dots** doesn't run in **PyQt5** but **VHX** and **SpriteMaker** can with minor edits.

Some additions and updates to **Shadows**. There's a new button added to the  shadow widget for flopping the shadow, also known as a horizontal flip. Along with that the screen-item's scaling and rotational properties are now applied to the shadow when created.  Some new keys and one update.  The **shift-W** key that cleared widgets is now **W**, no-shift. Added keys are the **O** key to clear shadow outlines and the **shift-H** key which clears widgets, hides select boxes, outlines, and pixitems - leaving only the shadows. It's also a toggle and entering it again restores all except the widgets. **open-cv** and **numpy** are required to run **Shadows** and **SpriteMaker**. Latest video:<https://youtu.be/CLOVUHtD-Ts>

---

**September 2022**  
Minor edits to widgets and sliders, mostly for scaling. 

A **reminder** for edits going from 6.3 to 5.16. In **dotsControlView.py** change e.position() to e.pos(). For the rest change e.globalPos() to e.globalPos(), plus of course, PyQt5 to PyQt5. Going the other way, in dotsDropCanvas.py leave globalPos alone - doesn't like it otherwise.  

---

**July 2022**     
See **SpriteMaker.md** for current changes as I'm breaking **SpriteMaker** out of **dots**.  It's still part of the package as it shares two folders which can be relocated. It's also possible to run **SpriteMaker** in **PyQt5.3.1** and **PyQt5** with some minor edits. Latest video:
<https://youtu.be/bGYBj_bjEJU>


**Good News!!!** No more **qt-warnings** - all that was required was having the right attribute set, fortunately someone at Qt came up with the fix.  Also, it seems to only effect Mac laptop users who don't use a mouse like me.  Video at: <https://youtu.be/NjMg-95ecgw>

---

**June 2022**  
Some cosmetic changes to the right-click widgets. Also, I finally was able to file a bug report with Qt about the pointer.dispatch warnings. It's in their work queue.  Maybe by the next release it will have been taken care of. Remember, you can always use a mouse if the warnings bother you. They're not visible running dots from your desktop.


------

**May 2022**  
A few small dumb bug fixes, I'm sorry for any problems they may have caused. I've added a sprite-maker, **SpriteMaker.py**, currently standalone as it requires **cv2** and **numpy**. I decided to leave it outside of dots for the present, however it does rely on dotsQt for some data, functions, and directories(folders), so it's not totally standalone. A good deal of its code is based on pathMaker, including being able to add or delete points so it may prove familiar.
See the demo: <https://youtu.be/sySmphW7bYA>

As of April dots was updated to **PyQt5.3** and **Python 3.10.4**. If you're on a Mac laptop running either Big Sur or Monterey and you _*_**don't**_*_ use a mouse there's good change you'll see this warning
many times.


    qt.pointer.dispatch: delivering touch release to same window QWindow(0x0) not QWidgetWindow(0x7f888e691040, name="CasterClassWindow")
    qt.pointer.dispatch: skipping QEventPoint(id=1 ts=0 pos=0,0 scn=789.445,580.564 gbl=789.445,580.564 Released ellipse=(1x1 ∡ 0) vel=0,0 press=-789.445,-580.564 last=-789.445,-580.564 Δ 789.445,580.564) : no target window

The easiest way to make it go away is to use a mouse. Pretty sure this is a qt bug as another Mac user has it as well.  You might want to let Qt know if you experience it. I'm going to that as soon as I finish posting the latest to GitHub. The warning also appears running PyQt5.

---

**April 2022**  
DotsQt has been updated to **PyQt5.3** and **Python 3.10.4**.

I also made some additions that aren't in the video, mainly to do with editing in pathMaker and centering backgrounds.  The big new stuff follows.
  
I've added shadow emulation to the mix but have it turned off as some folks may not share my interests in shadows and having it on adds 10-12 seconds to dots' startup time which may not be a great first-time user experience.  The two examples below give you the file names and snapshots of what code needs to tweaked inorder to have shadows working.  Comment one line off, uncomment the other line on. Save the files and restart dots. Next load shadowdemo.play and you should have 8 screen items and 8 shadows appearing as in the video. The time can vary but on my 6 year old Mac it's taking around 4 seconds for the shadows to appear once the screen items are up.  I'm using asyncio to restore shadows which has help to make the process 2 to 3 times faster then my first attempts. **cv2 and numpy are required** in order to add shadows.

#### dotsPixItem.py

```
# from dotsShadowMaker    import ShadowMaker  ## add shadows
from dotsShadow_Dummy    import ShadowMaker  ## turns off shadows

```
##### dotsSideShow.py

```
# from dotsShadowWorks    import Shadow  ## adds shadows
from dotsShadow_Dummy    import Shadow  ## turns off shadows

```
To create a shadow right-mouse click on a screen item and click on the top button labeled 'Shadow' which appears on the pixItem widget. This will work if there are no screen items selected.  See the keys.pdf for more on right-mouse click usage. If you right-mouse click on the shadow it's widget will appear.  I've colored the widgets yellow for pixItems and blue for the shadows to more easily tell them apart. There's only shadow per pixItem and deleting a pixItem deletes it's shadow.  You can't add shadows to frames or bats and you can't add animations to shadows. **Shift-W** will clear all widgets rather than closing them one at a time.  

I added a few lines to dotsSideShow.py that can output the keys and values of a play file as it's loaded and format it for csv.  There's a shadowdemo.csv in the play folder of the output to view in your default spreadsheet app, makes it more readable. Also added a mouse-over tag to alert you if a pixItem is locked. Beats wondering why you can't move it. Lastly, the bat-wing has been replaced with the actual screen bat. Yet another video: <https://youtu.be/rbFCvU9_IUs>

---

**March 2022**  
I'm pretty sure **castShadow4.py**, is the last of the shadow apps. It requires both **numpy** and **cv2.** I didn't bother to demo **castShadow3.py** as it was more of an interim process. These two files and the other **'shadow'** files starting with **shadow.py** have been moved to their own folder, **dots/shadows**.  Thanks to Stack Over Flow for rounded corners and borders.  Latest video: <https://youtu.be/yqCDZHhBBww>

---

**February 28 2022**  
Replaced **PIL** with **cv2**.  Still runs slow from a dead start but one less library to load.  Changes to insure only .pngs get loaded with the **Files** button.

**February 22 2022**   
 **cast_shadow2.py**, another cast shadow emulator. This one uses points rather than pixels to create a shadow - as a result I updated **outline.py** to display a larger image, I also set the point limit up to 350. It didn't help the shadow look any better, too edgy, but a good learning experience, more to share. It works best with apple.png - cv2 and numpy required.
Video at: <https://youtu.be/eAsH9412Bww>

**February 14 2022**  
One more stand-alone app, **cast_shadow.py**, a cast shadow emulator.
Requires, PIL, cv2, and numpy - consequently it takes a while to start when first run but it's worth it. My opinion. Another new video: <https://youtu.be/1VWjhypf0xk>

---

**January 2022**        
Yet another stand-alone app, **outline.py**. Combines Pygame **(required)** and PyQt as a way to outline a transparent .png and save the result as a SVG file.  This is a rewrite of the my pygame original of 3-4 years ago. It also features a SVG viewer. New video: <https://youtu.be/leTFR89YxA4>
  
--- 
   
**December 2021**    
Added another stand-alone app, **shadow.py**, a PyQt dropshadow visualizer. It's either run from the command line or thru an editor. It's written to work with transparent .png and .jpg files while also as a template for future such apps. Another new video. <https://youtu.be/V-kkzuURsjg>

I've added two new functions/keys to editing a path in pathMaker.
**L** in **edit** changes the cursor to a crosshair to let you know that things have changed. Holding down the mouse button while moving the mouse draws a closed shape to either select or unselect selected pointItems. Once selected you can use the arrow keys to move the selected points or using the other new key, **shift-D**, to delete them.  Lastly, you can easily move between **editing points** and **waypoints** and and not lose any points you previously selected in **edit** by toggling between **E** and **W** or **W** to **E**.  New video: <https://youtu.be/AMTV3umYyuc>

Additionally, some key reassignments in dropCanvas. I replaced **{/}** for rotating a sprite 45 degrees with **[/]** to match the same command in pathMaker. I also reassigned the keys that increment or decrement a sprite's **ZValue** back to front position. A **comma** sets a sprite back one **ZValue** and **period** up one value.  The four keys that are used to change a sprites **ZValue** are much closer together now. Big Win.

---

**November 2021**  
Added a right-mouse click to dropCanvas to trigger the **play** load dialog and to pathMaker to trigger **path chooser**.  Added a path edit function to pathMaker. Entering **E** after choosing a path allows you move, delete, or add a point and also re-distribute or half the number of points that make up the path. Some of these functions are also in wayPoints but not the ability to move individual points. Entering **W** from **edit** will put you into wayPoints and conversely **E** in **wayPoints** drops you into edit.  More work on bat-wings. They're now easier to select and move by clicking anywhere on the bats body but not the wings. Added **Shift U** to unlock all screen items in dropCanvas.

---

**October 2021**   
I've done some more work on wings and have some observations concerning the tendency for them to drift when stopped. The only differences I can see is using or not using the file chooser somehow affects the reprise animation for the wings screen objects.  

---

**September 2021**      
**Bonus...**  I've added a screen pixel ruler, **vhx.py** to the mix.  It runs both in Dots and on my Mac as a desktop widget - **vhx.app**, created using the MacOS Automator, the same utility that lets me run Dots as a desktop app. **Note:** Also on my Mac, **vhx.py** only runs in Dots when in VSCode, otherwise you can run it from the command line. This finally replaces my JavaFx version. See **keys.pdf** for updates. New video:  <https://youtu.be/98m-fNB16-w> 

**Runs on Linux.**
I wanted to see what it would take to set up a VM, a virtual machine, and run dots in Ubuntu 20.4 Linux. So I used VirtualBox, as recommended by Martin Fitzpatrick, as the VM of choice. After downloading and installing Ubuntu I gradually came to realize that no matter how many more times I downloaded and installed PyQt it was going to land in the python3.8 directory.  So I ran Dots in python3.8 with no problems other than not having dots displayed full size and having to use the control key in place of the Mac command key. I probably spent half my time with this project in the VM trying to find the menu bar which had disappeared - not an uncommon problem. I was finally able to resize the linux window to pretty much my Mac view and by setting the scaled setting to 200% dots opened up to the same size as I run it in MacOS though it could use a few small 10-15 pixels tweaks to reposition the inner side panels.  **Done.**

See **keys.pdf** for the current key assignments and hopefully some clarity. I added a **45 degree** toggle to pathMaker and changed the **half path** function to evenly distribute the new points. It looks better that way, uses less data though it may alter the path slightly. In dropCanvas, selecting screen objects will now be outlined by an actually visible lime green boundingRect. Lastly, I posted a remake of the last video I created in DotsJavaFx, **Tableau 2018**, recreated now in DotsQt as **Tableau 2021**, which was sort of the idea and why I spent the last two years writing in PyQt. I've included the code for wings 
in DotsSideCar. Two videos follow, **Tableau 2021** <https://youtu.be/h70MO0V7CNw> and **DotsQt Wings** <https://youtu.be/HtOaDZfeCzg>

---

**August 2021**  
The annoyance is no more. It's taken a while and the fix was easier to apply once I had isolated pathMaker from the rest of dots. The solution bothers me some - otherwise an interesting programming challenge.  Moving on, more key changes and additions.  I've moved the **-/= scale Y** keys to **;** and **'** to line up with **scale X :/"**.  The old **-/= scale Y** keys are now rotate **-/+15** degrees.  Also, the highest positioned pixItem by zValue is now tagged in yellow if you show tags by pressing **T**. The latest video. <https://youtu.be/cBvLJh02LgQ>

---
   
**July 2021**	      
Changed, holding down the **space-bar** and a **left-mouse click** will show the pixItem tag.  **T** still displays all the tags and a **shift-T** will display the tags of everything that's been **selected**.  I've also added three methods to lock and unlock pixItem screen positions. The first, **shift-L** works to toggle **selected pixItems** locked or unlocked. The second method, **shift-R**, locks **all pixItems**. The last method, **apostrophe** and a **mouse-click** toggles individual pixItems. You will need to save the changes for them to take effect. There's a new file, as of August, **dotsPathEdits**, that isolates the code that draws the path and displays pointItems. The annoyance still persists. Still working on it.

---

**June 2021**  
Decided to change things around again and reassigned some keys from February changes. In dropCanvas **'R'**, for run, replaces **'P'** for play. Typing **'R'** on a blank screen will run the demo or any play file you've set in dotsShared under 'runThis'. **'P'** will toggle paths replacing **'O'** - from February again. In pathMaker **'P'**, under wayPoint to show pointItems, has been replaced with **'V'** to view pointItems. Changed status-bar color. No video. The annoyance still persists.  Still working on it.

---

**April 2021**  
Changed the single zValue keys to **'['** and **']'** as the **option-click** key was conflicting with the **option-double click**.  Added a display for a single **ztag** when right-mouse clicking over a pixItem. Changed the **single-click** to **enter/return** to eliminate any accidental or unnecessary movement back to front. Reduced the screen width of dots and added one more sprite selection to the scrollPanel. Blocked any mouse actions to a pixItem while running an animation - this will prevent any screen items from getting lost. The **'C-key** can quit pathMaker if the screen is empty and no longer requires a click on the pathMaker button to do so. See dotsDropCanvas.py starting at line 96 for a fuller explanation of what I call an annoyance.
Video at: <https://youtu.be/AI1E8hszBbk>

---

**March 2021**  
Added the **Color** button to launch a color picker *widget. A color can be saved to the backgrounds directory as a named file that ends in **'.bkg'**, this allows it to be recalled and added to a play file as a regular background object. The expected color token is a hex string - **#FFFFFF**, there is no saved image file. Also added the pixItems zValue to tags and keys to send a pixItem back one zValue using **option-click** or forward one zValue using **command-click**. Frames are now a special case sprite rather than a background item.  DropCanvas now 1080X720 pixels.  See Video: <https://youtu.be/yUzqY7p9X3I>

---

**February 2021**       
Added the **'O'** key to the main window to toggle the paths prior to running animations as the **'P'** is now the **play** hot-key. Both keys can toggle the paths display once the animations are running. Also updated the parent window from a QGroupBox widget to QMainWindow adding QDockWidgets, a CentralWidget and a statusBar.  Currently running in Python 3.9.2 and PyQt 5.15.3 on a Mac, OSX  10.14.6.  QFileDialog in native mode no longer lets the user delete files. 

---

**December 2020**       
Added the **'L','P','S'** keys to dropCanvas to Load, Play, and Stop animations, same as the buttons - also reinstated **'C'** to clear the screen in dropCanvas. Clicking on the clear button will close pathMaker and as well as clicking on the pathMaker button if it's green. The **'C'** key is also used in pathMaker to center a path.

The **'P'** key still toggles paths but only after play begins. It's either that or start play and immediately show the paths. In wayPoints, under pathMaker, I've added another **'P'**  key that toggles the points used to draw the path. If you mouse over a point a yellow tag with the points x,y value, percent, and index will appear - mouse away to clear it. 	

The method used to calculate percents has changed. The old method was based on a fixed percentage which returned a point value position along the path but not necessarily an actual point, especially if the total number of points wasn't evenly divisible by 10. There's a fix for that if you desire an actual 10% correspondence. Mouse over a point to display the tag, hold down the delete key and click to **delete** the point or option click on it to **add** a new point midway from the point you're on to the next point down the path. Either approach will update the path and the percents.

---

**November 2020**  
Added **'P'** key to toggle paths if found in a play file or if assigned when running and the **'K'** key to toggle the help keyList from dropCanvas to pathMaker.  Added a new **button** for pathMaker functions.  Reassigned some dropKeys to match up with similar functions in pathMaker and pixItems. Added **'R'** key to run the animation path demo. It's looks a little odd when it starts but the end result matches the original. It required a few work arounds to get the effect I was after.   
  
Use the **'!'** key in **pathMaker** to reduce the path points size. I found that around 200 points should be sufficient in most cases. Also, you can use the snapshot button to record the waypoint tags and paths, plus any background. See video: <https://youtu.be/kalDltrQkWs>

---

**September 2020**   
Added the play, pause/resume and stop buttons to run animations. Added **paths** to animations.  Added a right-click **context menu** for adding animations to screen selections.  

Added **tags** to show a screen items current animation. After selecting an animation you can type 'T' to toggle the tags on and off. Tags will be orange initially if there are no animations running.  Once running and if set to Random, tags will appear green and display the animation that was randomly assigned. The **context menu** only works if something is selected, even to clear **tags**. A video showing some basic animations and how to add them to a screen object - pixitem. <https://youtu.be/SHDmcySukGg>

---

**August 2020**  
Added two new buttons. The save button maps the canvas items, pixItems and background to a Json file written to the ./plays directory as a .play file.  The load button reconstructs the saved canvas layout from the named .play file. Changed delete from the shift key to the actual delete key. Seems it shows up as a backspace key on some installs which is why I may not have used it earlier. Video to illustrate the save and load functions. <https://youtu.be/RPwEjgAcITk> 

---
 
**June 2020**  
Initial posting followed by minor bug fixes and fussy changes. The original video that illustrates some of the features of this app. <https://youtu.be/rd4LtR88UjE> 
≠≠≠
