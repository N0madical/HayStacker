# Packages
from tkinter import simpledialog, messagebox
import tkinter as tk
import threading, subprocess, os.path, platform, sqlite3

# Project  files
import deploy
from FindMyIntegration.request_reports import request_reports
from FindMyIntegration.generate_key import writeKey

tags = {}
parent = None
locations = {}
mapUI = None


def setParent(parentIn):
    global parent
    parent = parentIn

def setMapUI(mapIn):
    global mapUI
    mapUI = mapIn


def newKey():
    keyName = simpledialog.askstring("New tag", "Please enter a name for the new tag:")
    if keyName is not None and keyName != "":
        writeKey(keyName)
    loadTags()


def delKey(name):
    result = messagebox.askyesno("Delete tag", f"Are you sure you want to delete: {name.replace(".keys", "")}")
    if result:
        os.remove(os.path.join("keys", name))
        loadTags()


def loadTags():
    global tags
    global parent
    for sel in tags.values():
        sel.container.destroy()
    tags = {}
    names = os.listdir("keys")
    try:
        for name in names:
            keys = open(os.path.join("keys", name), "r")
            advKey = keys.read().splitlines()[1].replace("Advertisement key: ", "").strip()
            tags[name] = Tag(parent, name.replace(".keys", ""), 0, advKey)
            tags[name].pack()
            keys.close()
    except AttributeError:
        print("Failed to capture parent")


def renameTag(oldName, newName):
    return


anisette = None


def getLocations(user='', pswd='', useSMS=False):
    global anisette
    if anisette is None:
        def start_anisette():
            global anisette
            print("started anisette")
            if platform.system() == "Windows":
                anisette = subprocess.Popen("./anisette-v3-server/anisette-v3-server.exe")
            else:
                anisette = subprocess.Popen("./anisette-v3-server/anisette-v3-server")
            anisette.wait()
            anisette = None
            displayLocations()

        print("committing bruh")

        conn = sqlite3.connect('reports.db')
        sq3 = conn.cursor()
        sq3.execute("CREATE TABLE IF NOT EXISTS reports ("
                    "id_short TEXT, "
                    "timestamp INTEGER, "
                    "datePublished TEXT, "
                    "lat INTEGER, "
                    "lon INTEGER, "
                    "link TEXT, "
                    "statusCode INTEGER, "
                    "conf INTEGER, "
                    "UNIQUE(id_short, timestamp))")
        sq3.close()
        conn.commit()
        conn.close()

        threading.Thread(target=start_anisette, daemon=True).start()

        t = threading.Timer(0.5, lambda: threading.Thread(target=request_reports, args=(anisette, user, pswd, useSMS), daemon=True).start())
        t.start()
    else:
        print("Bruh wait lol")


def displayLocations():
    global locations

    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()

    # Execute a SELECT query to retrieve data
    cursor.execute('SELECT * FROM reports')

    # Fetch all the results
    data = cursor.fetchall()

    # Close the connection
    conn.close()

    locations = {}
    for row in data:
        name = row[0]
        if name not in locations or row[1] > locations[name][1]:
            locations[name] = row

    try:
        for item in locations.values():
            mapUI.set_marker(item[3], item[4], text=item[0])
            tags[f"{item[0]}.keys"].status.configure(fg="green")
    except AttributeError:
        print("Failed to connect to Map to add pin")


class Tag:
    def __init__(self, parent: tk.Frame, name, status, advKey):
        self.name = name
        self.status = status
        self.advKey = advKey
        self.container = tk.Frame(parent, bg="white", height=50, padx=2, pady=2, borderwidth=2, relief="ridge")
        self.status = tk.Label(self.container, text="•", font=("Courier New ", 30), bg="white", fg="red")
        self.title = tk.Label(self.container, text=f"{self.name}", font=("Courier New ", 10), bg="white")
        self.deployButton = tk.Button(self.container, text="Deploy", font=("Courier New ", 10), bg="white", command=lambda: deploy.deployPopup(parent, self))
        self.menu = tk.Menu(self.container, tearoff=False)
        self.menu.add_command(label="Delete tag", command=lambda: delKey(self.name + ".keys"))
        self.menu.add_command(label="Copy advertisement key",
                              command=lambda: self.container.clipboard_append(self.advKey))

    def setStatus(self, status: int):
        self.status = status

    def setName(self, newName: str):
        renameTag(self.name, newName)

    def pack(self):
        self.container.pack(fill="x", pady=4, padx=20)
        self.status.pack(side="left")
        self.title.pack(side="left")
        self.deployButton.pack(side="right", padx=5)

        def do_popup(event):
            try:
                self.menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()

        self.container.bind("<Button-3>", do_popup)
