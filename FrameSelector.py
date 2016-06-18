import fnmatch
import os
from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
from utils.ImageUtils import ImageUtils
        
class FrameSelector(object):
    
    # Init the app GUI
    def __init__(self):
        self.index = 0;
        # Create a windows and remove the resize option
        self.root = Tk()
        self.root.minsize(width=640, height=480)
        self.root.resizable(width=False, height=False)
        self.configureGUI()       
    
    def configureGUI(self):
        self.l = Label(self.root)
        self.l.pack(fill=BOTH, expand=1)

        # Create the options buttons and add to GUI
        f = Frame(self.root)
        Button(f, text="Open folder", command=self.openFolderClick).pack(side=LEFT, padx=5, pady=5)
        Button(f, text="Save location", command=self.saveClick).pack(side=LEFT, padx=5, pady=5)
        Button(f, text="Select", command=self.selectClick).pack(side=LEFT, padx=5, pady=5)
        Button(f, text="Next", command=self.nextClick).pack(side=RIGHT, padx=5, pady=5)
        f.place(x=0, y=0)

        # Start application
        self.root.mainloop()

    # Action to open button click
    def openFolderClick(self):
        # Select a folder
        folderName = filedialog.askdirectory()

        # Verify if a folder is selected
        if folderName:
            print("Search start")
            self.images = []
            self.index = 0

            # Verify in every subfolder id a .bin file exist inside of a Color folder
            for root, dirnames, filenames in os.walk(folderName):
                for filename in fnmatch.filter(filenames, '*.bin'):
                    if "Color" in root:
                        # Add the find image to a list
                        self.images.append(os.path.join(root, filename))
            
            # Show first image in GUI
            self.nextClick()
            print("Search ended")

    # Action to save button click
    def saveClick(self):
        print("SAVE")
    
    # Action to select button click
    def selectClick(self):
        print("SELECT")

    # Action to next button click
    def nextClick(self):
        # Verify if the list have image and is not the last image
        if len(self.images) != 0 and len(self.images) >= self.index:
            #Create a PIL image from the bin
            imageb = ImageUtils.readAsByte(self.images[self.index])
            img = ImageUtils.decodeBytesToImage(imageb, 640, 480)
            self.index = self.index + 1

            # Add the PIL image to GUI
            self.photo = ImageTk.PhotoImage(image=img)
            self.l.configure(image=self.photo)