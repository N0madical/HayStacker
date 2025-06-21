# Importing everything from tkinter module
from shutil import which
from tkinter import *

# main tkinter window
root = Tk()
root.title("HayStacker")
root.geometry("1000x500")

UIBG = "#E9DFE1"
parBG = root.cget("bg")

# Central pained window
pw = PanedWindow(orient ='horizontal')
pw.pack(fill = "both", expand = True)
pw.configure(sashrelief = "flat", width=0) # Show the sash


### User Interface Pane ###

UIFrame = Frame(pw, bg = UIBG)
pw.add(UIFrame)

title = Label(UIFrame, text = "HayStacker", font=("Lexend", 30), bg=UIBG, padx=30)
title.pack(side = "top")

welcome = Label(UIFrame, text = "No Locations Found...", font=("Courier New ", 10), bg=UIBG)
welcome.pack(side = "top")

deploy = Button(UIFrame, text = "Create New Tag", font=("Courier New ", 10), bg="white")
deploy.pack(side = "top", pady=30)

######
### Location Map Pane ###

MapFrame = Frame(pw, bg = "tan")
pw.add(MapFrame)

ControlFrame = Frame(MapFrame, bg = parBG, height=100)
ControlFrame.pack(fill = "x")

map = Label(ControlFrame, text = "Map Goes Here", font=("Courier New ", 10), bg="white")
map.pack()

######

# Loop and run the window
mainloop()