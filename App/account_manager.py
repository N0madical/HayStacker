# ------
# HayStacker Apple account login dialog
# Developed by Aiden C
# This script does not store or share your password
# I've made the most effort to make this script simple for your reading pleasure
# ------

import re # Regex matching, for moderating text box input
import queue # Giving the user time to input responses to the script
import os # For accessing the auth.json file
import tkinter as tk # python tkinter GUI library
from FindMyIntegration.request_reports import setRetryFunc # So we can define what happens if login fails
from FindMyIntegration.pypush_gsa_icloud import set_callback # Allows us to define a GUI for entering a 2FA code
from tag_manager import getLocations # The function that retrieves and displays tag locations

# Main password dialog function
def loginDialog():
    parent = tk._default_root

    popupWindow = tk.Toplevel()
    popupWindow.title("Login")

    popupWindow.transient(parent)  # Sets the main window as the parent

    def login():
        if email.get() != "" and pswd.get() != "":
            getLocations(email.get(), pswd.get(), bool(useSms.get()))
            popupWindow.destroy()
        else:
            badColor = "wheat1"
            if email.get() == "":
                email.configure(bg=badColor)
            if pswd.get() == "":
                pswd.configure(bg=badColor)

    header = tk.Label(popupWindow, text="Login to Apple ID", font=("Arial", 15))
    header.pack(side = "top")

    description = tk.Label(popupWindow, text="Necessary to access apple servers & retrieve AirTag network data")
    description.pack(side="top", padx=5)

    emailHeader = tk.Label(popupWindow, text="Email", font=("Arial", 8))
    email = tk.Entry(popupWindow, width=30)
    emailHeader.pack(side="top", pady=(10, 0))
    email.pack(side="top", pady=(0, 5))

    showPwd = tk.IntVar()
    paswHeader = tk.Label(popupWindow, text="Password", font=("Arial", 8))
    pswd = tk.Entry(popupWindow, show='*', width=30)
    paswHeader.pack(side="top", pady=(5, 0))
    pswd.pack(side="top", pady=(0, 0))

    showFrame = tk.Frame(popupWindow)
    showck = tk.Checkbutton(showFrame, variable = showPwd, command=lambda: pswd.configure(show='' if showPwd.get() else '*'))
    showck.pack(side="top", pady=(5, 0))
    showLabel = tk.Label(showFrame, text="Show password", font=("Arial", 8))
    showck.pack(side="left")
    showLabel.pack(side="right")
    showFrame.pack(side="top", pady=(0, 5))

    useSms = tk.IntVar()
    ckboxFrame = tk.Frame(popupWindow)
    txtAuth = tk.Checkbutton(ckboxFrame, variable = useSms, command=lambda: print(useSms.get()))
    txtAuthLabel = tk.Label(ckboxFrame, text="Use SMS auth instead of Apple popup (unreliable)", font=("Arial", 8))
    txtAuth.pack(side="left")
    txtAuthLabel.pack(side="right")
    ckboxFrame.pack(side="top", pady=5)

    tryLogin = tk.Button(popupWindow, text="Login", command=login)
    tryLogin.pack(side="top", pady=(5,10))


def authDialog():
    result = queue.Queue()

    def show():
        popupWindow = tk.Toplevel()
        popupWindow.title("Auth code")

        header = tk.Label(popupWindow, text="Apple auth code", font=("Arial", 15))
        header.pack(side="top")

        def validate(event):
            value = code.get()
            value = re.sub("[^0-9]", "", value)
            code.delete(0, tk.END)
            code.insert(0, value[0:5])

        def submit():
            value = code.get()
            if len(value) == 6 and value.isdigit():
                result.put(value)
                popupWindow.destroy()  # Close window

        codeHeader = tk.Label(popupWindow, text="6 numbers...", font=("Arial", 8))
        code = tk.Entry(popupWindow, width=6, font=("Arial", 15))
        code.bind('<Key>', validate)
        codeHeader.pack(side="top", pady=(10, 0))
        code.pack(side="top", pady=(0, 5))

        tryLogin = tk.Button(popupWindow, text="Submit", command=submit)
        tryLogin.pack(side="top", pady=(5, 10))

    tk._default_root.after(0, show)  # Wait until window is destroyed
    return result.get()


def retryLogin():
    # os.remove("auth.json")
    loginDialog()


set_callback(authDialog)
setRetryFunc(retryLogin)
