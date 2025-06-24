import os.path, base64, tkinter as tk
import subprocess

from serial.tools import list_ports
from tkinter import simpledialog
from FindMyIntegration.request_reports import request_reports
import threading

import deploy
from FindMyIntegration.generate_key import writeKey

tags = {}
parent = None

def setParent(parentIn):
    global parent
    parent = parentIn

def NewKey():
    keyName = simpledialog.askstring("New tag", "Please enter a name for the new tag:")
    if keyName is not None and keyName != "":
        writeKey(keyName)
    LoadTags()

def LoadTags():
    global tags
    global parent
    for sel in tags.values():
        sel.container.destroy()
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

def getLocations(user='', pswd='', useSMS=False):
    print("committing bruh")
    os.remove("reports.db")
    subprocess.run("sqlite3 reports.db \"CREATE TABLE reports (id_short TEXT, timestamp INTEGER, datePublished TEXT, lat INTEGER, lon INTEGER, link TEXT, statusCode INTEGER, conf INTEGER)\"")
    threading.Thread(target=lambda:subprocess.run("wsl ./anisette-v3-server/anisette-v3-server"), daemon=True).start()
    threading.Thread(target=request_reports, daemon=True).start()


class Tag:
    def __init__(self, parent: tk.Frame, name, status, advKey):
        self.name = name
        self.status = status
        self.advKey = advKey
        self.container = tk.Frame(parent, bg = "white", height=50, padx=2, pady=2, borderwidth=2, relief="ridge")
        self.status = tk.Label(self.container, text = "•", font=("Courier New ", 30), bg="white", fg="red")
        self.title = tk.Label(self.container, text = f"{self.name}", font=("Courier New ", 10), bg="white")
        self.deployButton = tk.Button(self.container, text = "Deploy", font=("Courier New ", 10), bg="white", command=lambda: deploy.deployPopup(parent, self))

    def setStatus(self, status: int):
        self.status = status

    def setName(self, newName: str):
        renameTag(self.name, newName)

    def pack(self):
        self.container.pack(fill = "x", pady=4, padx=20)
        self.status.pack(side = "left")
        self.title.pack(side = "left")
        self.deployButton.pack(side = "right", padx = 5)
