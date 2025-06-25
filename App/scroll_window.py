# Made using ChatGPT, slight modifications, and elbow grease, but sooooo helpful
# For HayStacker by Aiden C

# Packages
import tkinter as tk
from tkinter import ttk

# -------- helper to make wheel work everywhere ----------------------
def bind_mousewheel(widget):
    widget.bind_all("<MouseWheel>",
                    lambda e: widget.yview_scroll(-int(e.delta/120), "units"))
    widget.bind_all("<Button-4>",
                    lambda e: widget.yview_scroll(-1, "units"))      # Linux
    widget.bind_all("<Button-5>",
                    lambda e: widget.yview_scroll(+1, "units"))      # Linux


# ------- Scrollable Frame Widget ------------------------------------
class ScrollableFrame(ttk.Frame):
    """A frame that behaves like a ListBox of Frames — vertically scrollable."""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # ---- 1. create canvas + scrollbar ------------------------------
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        vscroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vscroll.set)

        # ---- 2. this frame lives *inside* the canvas --------------------
        self.content_frame = tk.Frame(self.canvas)

        # ---- 3. put the internal frame in a canvas window --------------
        self.canvas_window = self.canvas.create_window((0, 0), anchor="nw",
                                  window=self.content_frame)

        # ---- 4. geometry management ------------------------------------
        self.canvas.grid(row=0, column=0, sticky="nsew")
        # vscroll.grid(row=0, column=1, sticky="ns")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # ---- 5. whenever size changes, update the scroll region ---------
        self.content_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width)
        )

        # optional: enable mouse-wheel scrolling on Windows/Mac/X11
        bind_mousewheel(self.canvas)

        def update_scroll_region(event):
            self.canvas.update_idletasks()
            content_height = self.content_frame.winfo_height()
            canvas_height = self.canvas.winfo_height()

            # Always update scrollregion to fit content
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

            # If content is smaller than canvas, scroll to top and disable scroll
            if content_height <= canvas_height:
                self.canvas.yview_moveto(0.0)

        self.content_frame.bind("<Configure>", update_scroll_region)
