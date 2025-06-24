import os.path, base64, tkinter as tk
from serial.tools import list_ports
from tkinter import simpledialog

import deploy
from FindMyIntegration.generate_key import writeKey

tags = {}
parent = None

def setParent(parentIn):
    global parent
    parent = parentIn

def NewKey():
    keyName = simpledialog.askstring("New Key", "Please enter a name for the new tag:")
    if keyName is not None and keyName != "":
        writeKey(keyName)
    LoadTags()

def LoadTags():
    global tags
    global parent
    for sel in tags.values():
        sel.destroy()
    tags = {}
    names = os.listdir("keys")
    for name in names:
        keys = open(os.path.join("keys", name), "r")
        advKey = keys.read().splitlines()[1].replace("Advertisement key: ", "").strip()
        tags[name] = Tag(parent, name.replace(".keys", ""), 0, advKey)
        tags[name].pack()
        keys.close()

def renameTag(oldName, newName):
    return


class Tag:
    def __init__(self, parent: tk.Frame, name, status, advKey):
        self.name = name
        self.status = status
        self.advKey = advKey
        self.container = tk.Frame(parent, bg = "white", height=50, padx=1, pady=1, borderwidth=2, relief="ridge")
        self.status = tk.Label(self.container, text = "•", font=("Courier New ", 30), bg="white", fg="red")
        self.title = tk.Label(self.container, text = f"{self.name}", font=("Courier New ", 10), bg="white")
        self.deployButton = tk.Button(self.container, text = "Deploy", font=("Courier New ", 10), bg="white", command=lambda: deploy.deployPopup(parent, self))

    def setStatus(self, status: int):
        self.status = status

    def setName(self, newName: str):
        renameTag(self.name, newName)

    def pack(self):
        self.container.pack(fill = "x", pady=2)
        self.status.pack(side = "left")
        self.title.pack(side = "left")
        self.deployButton.pack(side = "right")
