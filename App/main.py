# -----
# HayStacker project by Aiden C
# Licensed under Creative Commons BY (Attribution)
# Created June 22nd, 2025
#
# Intended for users to make custom item trackers
# using the AirTag network on any platform
#
# Credits:
# FindMy - Biemster - https://github.com/biemster/FindMy - Apple server querying
# anisette-v3-server - Dadoum - https://github.com/Dadoum/anisette-v3-server - Apple server querying
# OpenHaystack - seemoo-lab - https://github.com/seemoo-lab/openhaystack -
#   ESP32 Firmware & AirTag network research 7 GUI design
#
# HayStacker, and it's creator, are not responsible for action taken by apple following
# use of this software. Measures have been taken to ensure this project is safe for users.
# I do not recommend using this commercially
# -----

# Packages
import os, tkintermapview, subprocess
from tkinter import *

# Project Files
import tag_manager, scroll_window, account_manager

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

deployButton = Button(headFrame, image=plus_image, bg=UIBG, borderwidth=0, command=tag_manager.newKey)
deployButton.pack(side = "right", padx=10)

# deployButton = Button(headFrame, text = "Login to Apple", font=("Courier New ", 10), bg="white", command=lambda:account_manager.passwordDialog())
# deployButton.pack(side = "right", padx=5)

welcome = Label(UIFrame, text = "Your tags", font=("Lexend", 15), bg=UIBG)
welcome.pack(side = "top", pady=10)

scrollable = scroll_window.ScrollableFrame(UIFrame)
scrollable.pack(fill="both", expand=True, padx=10, pady=(0,20))
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
        account_manager.loginDialog()
        loadButton.configure(text="", image=reload_img, background=parBG, borderwidth=0)

loadButton = Button(ControlFrame, font=("Courier New ", 10), bg="white", borderwidth=1, command=checkLogged)
loadButton.pack(side = "right", padx=5, pady=8)
if os.path.exists("auth.json"):
    loadButton.configure(image=reload_img, background=parBG, borderwidth=0)
else:
    loadButton.configure(text="Login to Apple")

mapLabel = Label(ControlFrame, text = "Your accessories", font=("Lexend", 12))
mapLabel.pack(side="left", padx=10)

# The main map
map_widget = tkintermapview.TkinterMapView(MapFrame, corner_radius=0)
map_widget.set_position(38.4502257, -100.3839858)
map_widget.set_zoom(4)
map_widget.pack(side="top", fill="both", expand=True)


# Change map to google maps when zoomed in
def onZoom(event):
    if map_widget.zoom >= 9 and "openstreetmap" in map_widget.tile_server:
        map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
    elif map_widget.zoom < 9 and "google" in map_widget.tile_server:
        map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")

root.bind("<MouseWheel>", onZoom)

tag_manager.setMapUI(map_widget)

if os.path.exists("auth.json"):
    tag_manager.getLocations()

######

tag_manager.loadTags()

# Loop and run the window
mainloop()
