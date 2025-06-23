# Importing everything from tkinter module
from shutil import which
from tkinter import *
import deploy
import tag_manager, scroll_window
from FindMyIntegration import generate_key
from FindMyIntegration.generate_key import writeKey
from deploy import createKey
from tag_manager import NewKey, LoadTags

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

title = Label(UIFrame, text = "HayStacker", font=("Lexend", 30), bg=UIBG, padx=30, pady=10)
title.pack(side = "top")

welcome = Label(UIFrame, text = "No Locations Found...", font=("Courier New ", 10), bg=UIBG)
welcome.pack(side = "top")

deployButton = Button(UIFrame, text = "Create New Tag", font=("Courier New ", 10), bg="white", command=NewKey)
deployButton.pack(side = "top", pady=30)

scrollable = scroll_window.ScrollableFrame(UIFrame, padding=5)
scrollable.pack(fill="both", expand=True)

tag_manager.setParent(scrollable.content_frame)

# exTag = Frame(tagsFrame, bg = "white", height=50, padx=1, pady=1, borderwidth=2, relief="ridge")
# exTag.pack(fill = "x")
#
# exTagStatus = Label(exTag, text = "•", font=("Courier New ", 30), bg="white", fg="red")
# exTagStatus.pack(side = "left")
#
# exTagName = Label(exTag, text = "My Tag", font=("Courier New ", 10), bg="white")
# exTagName.pack(side = "left")
#
# exTagDeploy = Button(exTag, text = "Deploy", font=("Courier New ", 10), bg="white", command=deploy.getPortID("Silicon Labs CP210x USB to UART Bridge (COM4)"))
# exTagDeploy.pack(side = "right")

######
### Location Map Pane ###

MapFrame = Frame(pw, bg = "tan")
pw.add(MapFrame)

ControlFrame = Frame(MapFrame, bg = parBG, height=100)
ControlFrame.pack(fill = "x")

map = Label(ControlFrame, text = "Map Goes Here", font=("Courier New ", 10), bg="white")
map.pack()

######

tag_manager.LoadTags()

# Loop and run the window
mainloop()