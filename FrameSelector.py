import fnmatch
import os
import shutil
import _thread
import time
from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
from utils.ImageUtils import ImageUtils
        
class FrameSelector(object):
    
    # Init the app GUI
    def __init__(self):
        self.index = 0
        self.images = []
        self.imagesFilename = []
        self.saveLocation = None
        self.coords = {}
        self.coordShow = None
        self.isSlideToRun = False

        # Create a windows and remove the resize option
        self.root = Tk()
        self.root.wm_title("Frame Selector")
        self.root.minsize(width=640, height=480)
        self.root.resizable(width=False, height=False)
        self.configureGUI()       
    
    def configureGUI(self):
        self.l = Label(self.root, bg="black")
        self.l.bind('<Button-1>', self.click)
        self.l.pack(fill=BOTH, expand=1)

        # Create the options buttons and add to GUI
        f = Frame(self.root)
        Button(f, text="Open folder", command=self.openFolderClick).pack(side=LEFT, padx=5, pady=5)
        Button(f, text="Save location", command=self.saveClick).pack(side=LEFT, padx=5, pady=5)
        Button(f, text="Prev", command=self.prevClick).pack(side=LEFT, padx=5, pady=5)
        Button(f, text="Next", command=self.nextClick).pack(side=LEFT, padx=5, pady=5)
        self.slideText = StringVar()
        Button(f, textvariable=self.slideText, command=self.slide).pack(side=LEFT, padx=5, pady=5)
        self.slideText.set("Slide start")
        f.place(x=0, y=0)

        # Create a label option
        f2 = Frame(self.root)
        Label(f2, text="Image label").pack(side=LEFT, padx=5, pady=5)
        self.imageLabel = Entry(f2)
        self.imageLabel.pack(side=LEFT, padx=5, pady=5)
        Button(f2, text="Select", command=self.selectClick).pack(side=LEFT, padx=5, pady=5)
        f2.place(x=0, y=35)

        f3 = Frame(self.root)
        self.log = StringVar()
        Label(f3, textvariable=self.log).pack(side=LEFT, padx=5, pady=5)
        self.jumpTo = Entry(f3)
        self.jumpTo.pack(side=LEFT, padx=5, pady=5)
        Button(f3, text="Jump to", command=self.jump).pack(side=LEFT, padx=5, pady=5)
        f3.place(x=0, y=445, height=35)

        f4 = Frame(self.root)
        self.coordsLog = StringVar()
        self.coordsLog.set("Coords: (640,480)")
        Label(f4, textvariable=self.coordsLog).pack(side=LEFT, padx=5, pady=5)
        f4.place(x=540, y=0, width=100)

        # Start application
        self.root.mainloop()

    def jump(self):
        if self.jumpTo.get() != "" and self.jumpTo.get().isnumeric():
            self.index = int(self.jumpTo.get()) - 1
            self.nextClick()

    def slide(self):
        self.isSlideToRun = not self.isSlideToRun
        _thread.start_new_thread(self.slideRun, ())
        
        if self.isSlideToRun == False:
            self.slideText.set("Slide start")
        else:
            self.slideText.set("Slide stop")
    
    def slideRun(self):
        while self.isSlideToRun:
            self.nextClick()
            time.sleep(0.1)

    def click(self, event):
        self.coords["x"] = event.x
        self.coords["y"] = event.y
        self.coordsLog.set("Coords: ("+str(event.x)+","+str(event.y)+")")
        if not self.coordShow:
            self.coordShow = Label(self.root, text=" ", bg="red")
            self.coordShow.place_configure(x=event.x-5, y=event.y-5, width=10, height=10)
        else:
            self.coordShow.place_forget()
            self.coordShow.place_configure(x=event.x-5, y=event.y-5, width=10, height=10)

    # Action to open button click
    def openFolderClick(self):        
        # Select a folder
        folderName = filedialog.askdirectory()

        # Verify if a folder is selected
        if folderName:
            self.log.set("Search start")
            self.images = []
            self.imagesFilename = []
            self.index = 0

            _thread.start_new_thread(self.searchImages, (folderName,))

    def searchImages(self, folderName):
        # Verify in every subfolder id a .bin file exist inside of a Color folder
        for root, dirnames, filenames in os.walk(folderName):
            for filename in fnmatch.filter(filenames, '*.bin'):
                if "Color" in root:
                    # Add the find image to a list
                    self.imagesFilename.append(filename)
                    self.images.append(os.path.join(root, filename))
        
        # Show first image in GUI
        self.nextClick()
        self.log.set("Search ended")

    # Action to save button click
    def saveClick(self):
        # Select a folder
        folderName = filedialog.askdirectory()

        # Verify if a folder is selected
        if folderName:
            self.saveLocation = folderName
            self.log.set("Save location: " + folderName)
    
    # Action to select button click
    def selectClick(self):
        if self.images and len(self.images) != 0 and self.saveLocation:
            if self.imageLabel.get() != "":
                if len(self.coords) == 2 and self.coords["x"] and self.coords["y"]:
                    if not os.path.exists(self.saveLocation+"\\"+self.imagesFilename[self.index]):
                        # Save the file name label and coords
                        with open(self.saveLocation+"\info.txt","a+") as f:
                            f.write(self.imagesFilename[self.index]+"@"+self.imageLabel.get()+"@"+str(self.coords["x"])+","+str(self.coords["y"])+"\n")
                        shutil.copy2(self.images[self.index], self.saveLocation)

                        self.log.set(self.imagesFilename[self.index] + " copied")
                    else:
                        self.log.set(self.imagesFilename[self.index] + " alread exist")
                else:
                    self.log.set("You need to specify a coord")
            else:
                self.log.set("You need to specify a label")
            
        else:
            self.log.set("You need to open a folder and set a save location")

    # Action to next button click
    def nextClick(self):
        # Verify if the list have image and is not the last image
        if len(self.images) != 0 and len(self.images) > self.index:
            #Create a PIL image from the bin
            imageb = ImageUtils.readAsByte(self.images[self.index])
            img = ImageUtils.decodeBytesToImage(imageb, 640, 480)
            self.index = self.index + 1

            # Add the PIL image to GUI
            self.photo = ImageTk.PhotoImage(image=img)
            self.l.configure(image=self.photo)

            self.log.set("Image " + str(self.index) + "/" + str(len(self.images)))
        else:
            self.log.set("No more images")
            self.isSlideToRun = False

    def prevClick(self):
        # Verify if the list have image and is not the last image
        
        if len(self.images) != 0 and self.index > 0:
            self.index = self.index - 1
            #Create a PIL image from the bin
            imageb = ImageUtils.readAsByte(self.images[self.index])
            img = ImageUtils.decodeBytesToImage(imageb, 640, 480)

            # Add the PIL image to GUI
            self.photo = ImageTk.PhotoImage(image=img)
            self.l.configure(image=self.photo)

            self.log.set("Image " + str(self.index) + "/" + str(len(self.images)))
        else:
            self.log.set("No more images")
            self.isSlideToRun = False