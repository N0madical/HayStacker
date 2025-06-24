# ------
# HayStacker Apple account login dialog
# Developed by Aiden C
# This script does not store or share your password
# I've made the most effort to make this script transparent for your reading pleasure if you wish
# ------

import tkinter as tk #python tkinter GUI library

# Main password dialog function
def passwordDialog(parent):
    popupWindow = tk.Toplevel()
    popupWindow.title("Login")

    popupWindow.transient(parent)  # Sets the main window as the parent

    def login():
        if email.get() != "" and pswd.get() != "":
            attemptLogin(email.get(), pswd.get(), useSms.get())
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


def authDialog(parent):
    popupWindow = tk.Toplevel()
    popupWindow.title("Auth code")

    popupWindow.transient(parent)  # Sets the main window as the parent


def attemptLogin(username, pswd, useSMS):
    return