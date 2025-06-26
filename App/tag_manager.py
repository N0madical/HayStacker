# Packages
import math
import time
from tkinter import simpledialog, messagebox
import tkinter as tk
import threading, subprocess, os.path, platform, sqlite3
from PIL import ImageTk, Image
from datetime import datetime, timezone, date

# Project  files
import deploy
from FindMyIntegration.request_reports import request_reports
from FindMyIntegration.generate_key import writeKey, getKeysDir

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
        try:
            writeKey(keyName)
        except FileExistsError:
            messagebox.showerror("Error", f"The key name '{keyName}' already exists")
    loadTags()

def delKey(name):
    result = messagebox.askyesno("Delete tag", f"Are you sure you want to delete: {name.replace(".keys", "")}")
    if result:
        os.remove(os.path.join(getKeysDir(), name))
        loadTags()

# Loads tags from the local keys directory
# On windows, keys are stored in %appdata%\local
def loadTags():
    global tags
    global parent
    for sel in tags.values():
        sel.container.destroy()
    tags = {}
    fpath = getKeysDir()
    if not os.path.exists(fpath): os.makedirs(fpath)
    names = os.listdir(fpath)
    try:
        for name in names:
            if ".keys" in name:
                keys = open(os.path.join(fpath, name), "r")
                readfile = keys.read().splitlines()
                for line in readfile:
                    if "Advertisement key: " in line:
                        advKey = line.replace("Advertisement key: ", "").strip()
                        tags[name] = Tag(parent, name.replace(".keys", ""), 0, 0, advKey)
                tags[name].pack()
                keys.close()
    except AttributeError:
        raise AttributeError("Failed to capture parent")


def renameTag(oldName):
    keyName = simpledialog.askstring("New tag", f"Please enter a new name for: {oldName}")
    if keyName is not None and keyName != "":
        try:
            os.rename(os.path.join(getKeysDir(), (oldName+".keys")), os.path.join(getKeysDir(), (keyName+".keys")))

            conn = sqlite3.connect('reports.db')
            sq3 = conn.cursor()
            sq3.execute("UPDATE reports SET id_short = ? WHERE id_short = ?", (keyName, oldName))
            conn.commit()
            sq3.close()
            conn.close()
        except FileExistsError:
            messagebox.showerror("Error", f"The key name '{keyName}' already exists")

    loadTags()


anisette = None

def getLocations(user='', pswd='', useSMS=False):
    """Queries the Apple server to get Tag locations. Writes locations to local database"""

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
    """Grabs Tag location data from local database and displays on the map"""

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

    avgLong = 0
    avgLat = 0
    minLong = 0
    minLat = 0
    maxLong = 0
    maxLat = 0
    total = len(locations.values())
    try:
        for item in locations.values():
            mapUI.set_marker(item[3], item[4], text=item[0], icon=ImageTk.PhotoImage(Image.open(os.path.join("media", "pin.png"))), icon_anchor='s')
            if time.time() - item[1] < 600:
                tags[f"{item[0]}.keys"].setStatus(2)
            else:
                tags[f"{item[0]}.keys"].setStatus(1)
            tags[f"{item[0]}.keys"].setTimeStamp(item[1])
            avgLong += item[3]
            avgLat += item[4]
            minLong = item[3] if minLong == 0 else min(minLong, item[3])
            minLat = item[4] if minLat == 0 else min(minLat, item[4])
            maxLong = item[3] if maxLong == 0 else max(maxLong, item[3])
            maxLat = item[4] if maxLat == 0 else max(maxLat, item[4])
            print(item[3], item[4])
    except AttributeError:
        raise AttributeError("Failed to connect to Map to add pin")

    mapUI.set_position(avgLong / total, avgLat / total)
    # print((minLat - 1, minLong - 1), (maxLat + 1, maxLong + 1))
    print(minLat, maxLat, minLong, maxLong)
    boundsLevel = getBoundsZoomLevel(maxLat + 0.0005, maxLong + 0.0005, minLat - 0.0005, minLong - 0.0005)
    if boundsLevel >= 9:
        mapUI.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
    mapUI.set_zoom(boundsLevel)
    
def getBoundsZoomLevel(max_lat, max_lon, min_lat, min_lon, map_width_px=1024, map_height_px=768):
    # Clamp latitudes to Mercator projection limits
    def clamp(value, min_value, max_value):
        return max(min_value, min(value, max_value))

    min_lat = clamp(min_lat, -85.0511, 85.0511)
    max_lat = clamp(max_lat, -85.0511, 85.0511)

    # Convert lat/lon to pixel space at zoom level 0
    def lon_to_x(lon):
        return (lon + 180.0) / 360.0

    def lat_to_y(lat):
        sin_lat = math.sin(math.radians(lat))
        return (1.0 - math.log((1 + sin_lat) / (1 - sin_lat)) / (2 * math.pi)) / 2.0

    x1, y1 = lon_to_x(min_lon), lat_to_y(min_lat)
    x2, y2 = lon_to_x(max_lon), lat_to_y(max_lat)

    # Calculate bounding box size in tiles
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    # Find maximum zoom where box fits within view
    for zoom in range(22, -1, -1):
        scale = 256 * (2 ** zoom)
        if dx * scale <= map_width_px and dy * scale <= map_height_px:
            return zoom

    return 0  # Fallback if no zoom fits


class Tag:
    def __init__(self, parent: tk.Frame, name, status, timeStamp, advKey):
        self.name = name
        self.status = status
        self.advKey = advKey
        self.timeStamp = timeStamp
        self.container = tk.Frame(parent, bg="white", height=50, padx=2, pady=2, borderwidth=2, relief="ridge")
        self.statusDot = tk.Label(self.container, text="•", font=("Courier New ", 30), bg="white", fg="red")
        self.nameBox = tk.Frame(self.container, bg="white")
        self.title = tk.Label(self.nameBox, text=f"{self.name}", font=("Courier New ", 12), bg="white")
        self.subtitle = tk.Label(self.nameBox, text=f"Last seen: Never", font=("Courier New ", 8), bg="white")
        self.deployButton = tk.Button(self.container, text="Deploy", font=("Courier New ", 10), bg="white", command=lambda: deploy.deployPopup(parent, self))
        self.menu = tk.Menu(self.container, tearoff=False)
        self.menu.add_command(label="Rename tag", command=lambda: renameTag(self.name))
        self.menu.add_command(label="Delete tag", command=lambda: delKey(self.name + ".keys"))
        self.menu.add_command(label="Copy advertisement key",
                              command=lambda: self.container.clipboard_append(self.advKey))
        self.menu.add_command(label="Copy keyfile path",
                              command=lambda: self.container.clipboard_append(getKeysDir() / (self.name+".keys")))

    def updateStatusDot(self):
        if self.status == 2:
            self.statusDot.configure(fg="green")
        elif self.status == 1:
            self.statusDot.configure(fg="dark orange")
        else:
            self.statusDot.configure(fg="red")


    def setStatus(self, status: int):
        self.status = status
        self.updateStatusDot()

    def setName(self, newName: str):
        renameTag(self.name, newName)

    def setTimeStamp(self, timeStamp: int):
        try:
            dt = datetime.fromtimestamp(timeStamp)
            if platform.system() == "Windows":
                hourFormat = "%#I"
            else:
                hourFormat = "%-I"
            if (time.time()- timeStamp) > 432000:
                self.timeStamp = dt.strftime(f"%b %d, %Y at {hourFormat}:%M %p")
            elif dt.date() == date.today():
                self.timeStamp = dt.strftime(f"Today at {hourFormat}:%M %p")
            else:
                self.timeStamp = dt.strftime(f"%A at {hourFormat}:%M %p")
        except Exception as e:
            print("Error formatting timeStamp: ", e)
            messagebox.showerror("Error", f"Error formatting timeStamp: {e}")
        self.subtitle.configure(text=f"Last seen: {self.timeStamp}")

    def pack(self):
        self.container.pack(fill="x", pady=4, padx=20)
        self.statusDot.pack(side="left", padx=5)
        self.nameBox.pack(side="left")
        self.title.pack(side="top", anchor="nw")
        self.subtitle.pack(side="top", anchor="sw")
        self.deployButton.pack(side="right", padx=5)

        def do_popup(event):
            try:
                self.menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()

        self.container.bind("<Button-3>", do_popup)
