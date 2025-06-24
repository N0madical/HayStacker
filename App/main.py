# Importing everything from tkinter module
import os
from shutil import which
from tkinter import *
import tag_manager, scroll_window, account_manager
from tag_manager import newKey
import tkintermapview, subprocess

# main tkinter window
root = Tk()
root.title("HayStacker")
root.geometry("1000x500")
icon_image = PhotoImage(file=os.path.join("media", "HayStacker64.png"))
root.iconphoto(True, icon_image)
logo_image = PhotoImage(file=os.path.join("media", "HayStackerLogo.png"))
plus_image = PhotoImage(file=os.path.join("media", "plus.png"))
reload_img = PhotoImage(file=os.path.join("media", "reload.png"))

UIBG = "#E9DFE1"
parBG = root.cget("bg")

# Central pained window
pw = PanedWindow(orient ='horizontal', sashrelief = "flat", bg="slate gray", sashwidth=2)
pw.pack(fill = "both", expand = True)


### User Interface Pane ###

UIFrame = Frame(pw, bg = UIBG)
pw.add(UIFrame)

headFrame = Frame(UIFrame, bg = UIBG, pady=15, padx=5)
headFrame.pack(side= "top", fill = "x")

logo = Label(headFrame, image=logo_image, compound="left", borderwidth=0)
logo.pack(side="left", padx=(10,5))

title = Label(headFrame, text = "HayStacker", font=("Lexend", 13), bg=UIBG)
title.pack(side = "left")

deployButton = Button(headFrame, image=plus_image, bg=UIBG, borderwidth=0, command=newKey)
deployButton.pack(side = "right", padx=10)

# deployButton = Button(headFrame, text = "Login to Apple", font=("Courier New ", 10), bg="white", command=lambda:account_manager.passwordDialog(root))
# deployButton.pack(side = "right", padx=5)

welcome = Label(UIFrame, text = "Your tags", font=("Lexend", 15), bg=UIBG)
welcome.pack(side = "top", pady=10)

scrollable = scroll_window.ScrollableFrame(UIFrame)
scrollable.pack(fill="both", expand=True, padx=10)
scrollable.canvas.configure(background=UIBG)
scrollable.content_frame.configure(background=UIBG)

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

def checkLogged():
    if os.path.exists("auth.json"):
        tag_manager.getLocations()
    else:
        account_manager.loginDialog(root)
        loadButton.configure(text="", image=reload_img, background=parBG, borderwidth=0)

loadButton = Button(ControlFrame, font=("Courier New ", 10), bg="white", borderwidth=1, command=checkLogged)
loadButton.pack(side = "right", padx=5, pady=8)
if os.path.exists("auth.json"):
    loadButton.configure(image=reload_img, background=parBG, borderwidth=0)
else:
    loadButton.configure(text="Login to Apple")

mapLabel = Label(ControlFrame, text = "Your accessories", font=("Lexend", 12))
mapLabel.pack(side="left", padx=10)

map_widget = tkintermapview.TkinterMapView(MapFrame, corner_radius=0)
map_widget.set_position(38.4502257, -100.3839858)
map_widget.set_zoom(4)
map_widget.pack(side="top", fill="both", expand=True)

tag_manager.setMapUI(map_widget)

######

tag_manager.loadTags()

# Loop and run the window
mainloop()

subprocess.run("wsl killall anisette-v3-server")