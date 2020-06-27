## DotsQt

**DotsQt** is a work in progress and as it stands today, a program for creating photo-collages using transparent pngs.

The original dots was/is a program written in JavaFx that added animation to the photo-collage portion of the dots app I called storyboard as well as providing a means to create sprites. DotsQt is a pyqt implementation of storyboard and its attendant classes. There is no animation in this release.

**Note:** There is no dots in DotsQt either. Dots was the original front end and is no longer required as the pixitem screen objects are now based on transparent pngs.


## Why

I've a few reasons for posting this. 

* I've some questions that I'd like answered and having the code and supporting materials should help.

* I never got the chance to publish the original as Oracle killed off JavaFx. I've read it's not yet dead but I rather code in python.

* I wanted to share the fun. 

## Questions

* I've slots and signals working in a few of the modules but was unable to make it work between the dotsDropCanvas.py and dotsPixItem.py files. There are stubs for PyPubSub that did work as a reference. The setPixKeys slot in PixItem is unchanged and all I've done is to replace the PyPubSub code in DropCanvas with the sendPixKeys function, my work around.


	How would I go about wiring up dropcanvas to talk to setPixKeys in pixitem using a signal from dropcanvas?  Would using pyqt slots and signals be any more efficient then my work around?   

* I'd like to add two gestures, one to scale a pixitem and the other to rotate it.  The code to scale and rotate is already working in pixitem using keyboard commands, adding gestures would be a bonus. I found one working example based on a widget but I couldn't get the code to work in pixitem.

	How would I go about adding gestures to the PixItem class and could I do it without a major code overhaul?  Another possibility is to add an event filter to DropCanvas and apply the gestures to selected items. Adding gestures to the pixitem is how it currently operates in Java.

* I'm looking for samples or documentation on animation, svg, paths. Are there any sources to recommend besides the latest pyside docs?


## Stuff to know

One of the few coding decisions I made was to try and keep my files, modules, under 300 lines.  

Sprites in dots average up to 500-600 pixels per side and aren't necessarily square.

The upper right hand panel of dotsQt is a read only list of the keys, key combinations and their actions. Consider that help. 

Currently I'm using the graphics item zValue() as a means to order the four types which share the scene items list.

#### types and zValue range

| scene.item  | type  | zValue |
|:------------- |:---------------:| -------------:|
| MapItem | map | 10.0 over top pixitem |
| PixItem | pix  |  0.0 increasing by 0.011 |  
| LineItem  | grid   | -33.0 as a group |
| BkgItem   | bkg | -99.0 decreasing by -1.0 |

***The .011 value for PixItems is arbitrary and could change.

The star in scrollPanel isn't currently designed to be dragged to the canvas, without it though, none of this would exist.

## Requirements
* PyQt5
* functools
* PyPubSub - only for testing 
* Any program that can create transparent pngs

## Lastly

Here's a link to a short video that illustrates the features of this app. <https://youtu.be/rd4LtR88UjE>

My background combines degrees in fine arts, photography and ceramics, work as a graphics artist and layout artist, teaching, mail order rubber stamps, and a 21 year career as a business application programmer. All procedural code and other than Fortran, languages you probably never heard of. 

This is my first pyqt app and it wouldn't have been possible without Stack OverFlow and Google Search. I can say pretty much the same about the Java version as well.

Hope you enjoy it.








  







 