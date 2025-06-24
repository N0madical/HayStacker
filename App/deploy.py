import runpy
import tkinter as tk
import write_ESP32, tag_manager
from serial.tools import list_ports

def createKey(name):
    open(f"{name}.yaml", "w").close()
    runpy.run_path("FindMyIntegration\\generate_key.py")
    tag_manager.LoadTags()

def getPortNames(advanced):
    usb_ports = []
    for port in list_ports.comports():
        # Check if the port's hardware ID indicates a USB device
        # This is a common way to identify USB serial ports,
        # though the exact string can vary depending on the device.
        print(port.description)
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

    def loadPorts(advanced):
        listbox.delete(0, tk.END)
        for item in getPortNames(advanced):
            listbox.insert(tk.END, item)

    def startButtonDisplay():
        if listbox.curselection() != ():
            deployButton.pack(pady=5)
        else:
            deployButton.pack_forget()

    def startDeploy():
        if listbox.curselection() != ():
            deployPort = getPortID(listbox.get(listbox.curselection()))
            advKey = tag.advKey
            write_ESP32.write(deployPort, advKey)
            popupWindow.destroy()


    # Title
    title = tk.Label(popupWindow, text = "Choose a USB Port", font=("Courier New ", 15))
    title.pack(padx=40, pady=10)

    reloadButton = tk.Button(popupWindow, text="Reload Ports", command=lambda:loadPorts(False))
    reloadButton.pack(pady=5)

    advancedButton = tk.Button(popupWindow, text="Load Advanced Ports", command=lambda: loadPorts(True))
    advancedButton.pack(pady=5)

    # Create a Listbox within the popup
    listbox = tk.Listbox(popupWindow)
    listbox.pack(padx=10, pady=10, fill="x")

    # Add items to the Listbox
    loadPorts(False)

    # Add control buttons
    deployButton = tk.Button(popupWindow, text="Deploy to USB Device", command=startDeploy)

    closeButton = tk.Button(popupWindow, text="Cancel", command=popupWindow.destroy)
    closeButton.pack(pady=5)

    # Bind listbox select
    listbox.bind("<<ListboxSelect>>", lambda e: startButtonDisplay()) # deployButton.pack(pady=5)

    # Optional: Make the popup modal (prevents interaction with main window)
    popupWindow.grab_set()
    popupWindow.transient(parent) # Sets the main window as the parent
    popupWindow.wait_window(popupWindow) # Waits for the popup to be closed