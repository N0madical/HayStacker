import runpy, os
import tkinter as tk
import write_ESP32, tag_manager, write_ESP32_C3
from serial.tools import list_ports
from tkinter import messagebox
from repeatedTimer import repeatedTimer

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

def deployPopup(parent, tag):
    # Create a Toplevel window for the popup
    popupWindow = tk.Toplevel()
    popupWindow.title("Deploy")
    advanced = False
    collected = []

    def loadPorts():
        nonlocal advanced
        nonlocal collected
        ports = getPortNames(advanced)
        if ports != collected:
            collected = ports
            print(ports)
            listbox.delete(0, tk.END)
            for item in getPortNames(advanced):
                listbox.insert(tk.END, item)

    def loadAdvanced():
        global advanced
        advanced = True

    def startButtonDisplay():
        if listbox.curselection() != ():
            deployButton.pack(pady=5)
        else:
            deployButton.pack_forget()

    def startDeploy():
        if listbox.curselection() != ():
            deployPort = getPortID(listbox.get(listbox.curselection()))
            advKey = tag.advKey
            write_ESP32_C3.write(deployPort, advKey)
            reloader.stop()
            popupWindow.destroy()


    # Title
    title = tk.Label(popupWindow, text = "Choose a USB Port", font=("Courier New ", 15))
    title.pack(padx=40, pady=(10,2))

    subtitle = tk.Label(popupWindow, text=f"To deploy tag: {tag.name}", font=("Courier New ", 10))
    subtitle.pack(padx=40, pady=(2,10))

    reloadButton = tk.Button(popupWindow, text="Reload Ports", command=lambda:loadPorts())
    reloadButton.pack(pady=5)

    advancedButton = tk.Button(popupWindow, text="Load Advanced Ports", command=lambda:loadAdvanced())
    advancedButton.pack(pady=5)

    # Create a Listbox within the popup
    listbox = tk.Listbox(popupWindow)
    listbox.pack(padx=10, pady=10, fill="x")

    # Add items to the Listbox
    loadPorts()
    reloader = repeatedTimer(1, loadPorts).start()

    # Add control buttons
    deployButton = tk.Button(popupWindow, text="Deploy to USB Device", command=startDeploy)

    sidebyside = tk.Frame(popupWindow)

    closeButton = tk.Button(sidebyside, text="Cancel", command=popupWindow.destroy)
    closeButton.pack(side="right", padx=5)

    helpButton = tk.Button(sidebyside, text="Help!", command=helpDialog)
    helpButton.pack(side="left", padx=5)

    sidebyside.pack(pady=5)

    # Bind listbox select
    listbox.bind("<<ListboxSelect>>", lambda e: startButtonDisplay()) # deployButton.pack(pady=5)

    popupWindow.bind("<Return>", lambda x:startDeploy())

    # Optional: Make the popup modal (prevents interaction with main window)
    popupWindow.grab_set()
    popupWindow.transient(parent) # Sets the main window as the parent
    popupWindow.wait_window(popupWindow) # Waits for the popup to be closed
    reloader.stop()

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
