import runpy, os
import tkinter as tk
import write_ESP32, tag_manager, write_ESP32_C3
from serial.tools import list_ports
from tkinter import messagebox, ttk
from repeatedTimer import repeatedTimer
from config import firmwareOptions

def createKey(name):
    open(f"{name}.yaml", "w").close()
    runpy.run_path(os.path.join("FindMyIntegration", "generate_key.py"))
    tag_manager.loadTags()

def getPortNames(advanced):
    usb_ports = []
    for port in list_ports.comports():
        # Check if the port's hardware ID indicates a USB device
        # This is a common way to identify USB serial ports,
        # though the exact string can vary depending on the device.
        if not advanced:
            if "USB" in port.hwid.upper() or "VID:PID" in port.hwid.upper():
                usb_ports.append(port.description)
        else:
            usb_ports.append(port.description)

    return usb_ports

def getPortID(name):
    for port in list_ports.comports():
        if port.description == name:
            return port.device
    return None


# --------------------------------------- Initial USB Select dialog -------------------------------------------

def deployPopup(parent, tag):
    # Create a Toplevel window for the popup
    popupWindow = tk.Toplevel()
    popupWindow.title("Deploy")
    advanced = False
    collected = []

    question = tk.PhotoImage(file=os.path.join("media", "qmark.png"))

    def loadPorts():
        nonlocal advanced
        nonlocal collected
        ports = getPortNames(advanced)
        if ports != collected:
            collected = ports
            print(ports)
            portsList.delete(0, tk.END)
            for item in getPortNames(advanced):
                portsList.insert(tk.END, item)

    def loadAdvanced():
        global advanced
        advanced = True

    def startDeploy():
        # print(portsList.get)
        if portsList.curselection() != ():
            deployPort = getPortID(portsList.selection_get())
            advKey = tag.advKey
            reloader.stop()
            popupWindow.destroy()
            typeDialog(parent, tag, deployPort, advKey)

    # Title
    title = tk.Label(popupWindow, text = f"Deploy {tag.name}", font=("Courier New ", 15))
    title.pack(padx=40, pady=(10,2))

    # Subtitle
    subtitle = tk.Label(popupWindow, text=f"Choose a USB device", font=("Courier New ", 10))
    subtitle.pack(padx=10, pady=(2,10))

    # Side-by-side buttons
    controlFrame = tk.Frame(popupWindow)
    controlFrame.pack(pady=5)

    reloadButton = tk.Button(controlFrame, text="Reload", command=lambda:loadPorts())
    reloadButton.pack(side="left", padx=5)

    advancedButton = tk.Button(controlFrame, text="Show advanced", command=lambda:loadAdvanced())
    advancedButton.pack(side="right", padx=5)

    # Create a Listbox within the popup
    portsList = tk.Listbox(popupWindow, selectmode=tk.SINGLE, width=30)
    portsList.pack(pady=5, padx=10, fill="x")

    # Add items to the Listbox
    loadPorts()
    reloader = repeatedTimer(1, loadPorts).start()

    # Add control buttons
    deployButton = tk.Button(popupWindow, text="Next", command=startDeploy)
    deployButton.pack(pady=10)

    helpButton = tk.Button(popupWindow, command=helpDialog, image=question, borderwidth=0)
    helpButton.pack(pady=5)

    popupWindow.bind("<Return>", lambda x:startDeploy())

    # Optional: Make the popup modal (prevents interaction with main window)
    popupWindow.grab_set()
    popupWindow.transient(parent) # Sets the main window as the parent
    popupWindow.wait_window(popupWindow) # Waits for the popup to be closed
    reloader.stop()


# ---------------------------------------- Type select dialog -------------------------------------------------

def typeDialog(parent, tag, deployPort, advKey):
    print(tag, deployPort, advKey)

    question = tk.PhotoImage(file=os.path.join("media", "qmark.png"))

    def startDeploy():
        if (binList.get() != "") & (devList.get() != ""):
            deployFunc = firmwareOptions[devList.get()][0]
            firmwareLocation = firmwareOptions[devList.get()][1][binList.get()]
            popupWindow.destroy()
            mac = deployFunc.write(firmwareLocation, deployPort, advKey)
            messagebox.showinfo("Success", "Deploying...\nMAC Address: " + mac + "\nPlease power cycle the ESP after completion!")

    def updateBinList(event):
        binList.set("")
        binList['values'] = list(firmwareOptions[devList.get()][1].keys())

    # Create a Toplevel window for the popup
    popupWindow = tk.Toplevel()
    popupWindow.title("Deploy")

    # Title
    title = tk.Label(popupWindow, text = f"Deploy {tag.name}", font=("Courier New ", 15))
    title.pack(padx=40, pady=(10,2))

    # Subtitle
    subtitle = tk.Label(popupWindow, text="Preferences", font=("Courier New ", 10))
    subtitle.pack(padx=10, pady=(2,10))

    devLabel = tk.Label(popupWindow, text="What type is your device?", font=("Courier New ", 8))
    devLabel.pack(padx=10, pady=(2, 0))
    devType = tk.StringVar()
    devList = ttk.Combobox(popupWindow, textvariable=devType, state='readonly')
    devList.pack(padx=10, pady=(0,10), fill="x")

    devList['values'] = list(firmwareOptions.keys())
    devList.bind('<<ComboboxSelected>>', updateBinList)

    binLabel = tk.Label(popupWindow, text="How should this tag operate?", font=("Courier New ", 8))
    binLabel.pack(padx=10, pady=(2, 0))
    binType = tk.StringVar()
    binList = ttk.Combobox(popupWindow, textvariable=binType, state='readonly')
    binList.pack(padx=10, pady=(0,10), fill="x")

    # Add control buttons
    deployButton = tk.Button(popupWindow, text="Deploy", command=startDeploy)
    deployButton.pack(pady=10)

    helpButton = tk.Button(popupWindow, command=helpDialog2, image=question, borderwidth=0)
    helpButton.pack(pady=5)

    popupWindow.bind("<Return>", lambda x:startDeploy())

    # Optional: Make the popup modal (prevents interaction with main window)
    popupWindow.grab_set()
    popupWindow.transient(parent) # Sets the main window as the parent
    popupWindow.wait_window(popupWindow) # Waits for the popup to be closed


def helpDialog():
    messagebox.showinfo("Help",
                        """Help with ESP32 connection:

The process of connecting to an ESP32 board often uses the COM ports. \
This software is simply checking the avaliable COM ports, and Advanced mode \
returns unfiltered results. If your ESP32 isn't there, it's likely \
a connection problem between your PC and the ESP32 usb.

Often, this is simply a driver issue. Look up your board's name and \
\'Serial drivers\' or \'COM drivers\' on Google, and you'll probably find \
instructions. On Espressif boards, for example, look up 'espressif com port driver' 

To tripple-check that this software isn't the problem, open PowerShell and run:

Get-WMIObject Win32_SerialPort

If nothing shows up, it's a COM port connection problem :(
If your board shows up, submit an issue on GitHub and I'll check it out!"""
                        )

def helpDialog2():
    messagebox.showinfo("Help",
                        """Help with ESP32 firmware selection:

"""
                        )
