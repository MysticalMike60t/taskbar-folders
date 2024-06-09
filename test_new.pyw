import os
import sys
import tkinter as tk
from tkinter import ttk, Scrollbar, Canvas
from PIL import Image, ImageTk
import json
import ctypes
from ctypes import wintypes

# Define the SHFILEINFO structure
class SHFILEINFO(ctypes.Structure):
    _fields_ = [
        ("hIcon", wintypes.HICON),
        ("iIcon", ctypes.c_int),
        ("dwAttributes", ctypes.c_uint),
        ("szDisplayName", wintypes.WCHAR * 260),
        ("szTypeName", wintypes.WCHAR * 80),
    ]

# Define the BITMAPINFOHEADER structure
class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD)
    ]

# Class to extract icons from .lnk files
class IconExtractor:
    def __init__(self, path):
        self.path = path

    def extract_icon(self):
        shinfo = SHFILEINFO()
        SHGFI_ICON = 0x100
        SHGFI_LARGEICON = 0x0    # Large icon
        res = ctypes.windll.shell32.SHGetFileInfoW(self.path, 0, ctypes.byref(shinfo), ctypes.sizeof(shinfo), SHGFI_ICON | SHGFI_LARGEICON)
        if res:
            return shinfo.hIcon
        return None

    def icon_to_image(self):
        hicon = self.extract_icon()
        if hicon:
            hdc = ctypes.windll.user32.GetDC(0)
            hbm = ctypes.windll.gdi32.CreateCompatibleBitmap(hdc, 32, 32)
            hmemdc = ctypes.windll.gdi32.CreateCompatibleDC(hdc)
            hbm_old = ctypes.windll.gdi32.SelectObject(hmemdc, hbm)
            ctypes.windll.user32.DrawIconEx(hmemdc, 0, 0, hicon, 32, 32, 0, None, 3)
            bmpinfo = BITMAPINFOHEADER()
            bmpinfo.biSize = ctypes.sizeof(bmpinfo)
            bmpinfo.biWidth = 32
            bmpinfo.biHeight = -32  # Negative height for top-down DIB
            bmpinfo.biPlanes = 1
            bmpinfo.biBitCount = 32
            bmpinfo.biCompression = 0  # BI_RGB
            bmpinfo.biSizeImage = 32 * 32 * 4

            buf = ctypes.create_string_buffer(bmpinfo.biSizeImage)
            ctypes.windll.gdi32.GetDIBits(hmemdc, hbm, 0, 32, buf, ctypes.byref(bmpinfo), 0)
            ctypes.windll.gdi32.SelectObject(hmemdc, hbm_old)
            ctypes.windll.gdi32.DeleteDC(hmemdc)
            ctypes.windll.user32.ReleaseDC(0, hdc)

            image = Image.frombuffer('RGBA', (32, 32), buf, 'raw', 'BGRA', 0, 1)
            return image
        return None

# Function to list .lnk files in a directory
def list_lnk_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.lnk')]

# Function to load custom icons from a JSON file
def load_custom_icons():
    custom_icons = {}
    with open('custom_icons.json', 'r') as file:
        custom_icons = json.load(file)
    
    loaded_icons = {}
    for pattern, icon_path in custom_icons.items():
        if os.path.exists(icon_path):
            loaded_icons[pattern] = Image.open(icon_path).resize((64, 64), Image.LANCZOS)  # Resize here
    return loaded_icons

# Main application class
class LnkIconApp:
    def __init__(self, root, directory):
        self.root = root
        self.root.title(directory)
        self.directory = directory
        self.custom_icons = load_custom_icons()

        self.canvas = Canvas(self.root)  # No custom style
        self.frame = ttk.Frame(self.canvas)  # No custom style
        self.scrollbar = Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.load_icons()

    def get_custom_icon(self, filename):
        for pattern, image in self.custom_icons.items():
            if pattern == filename or pattern == '*.lnk':  # Simple matching logic
                return image
        return None

    def open_link(self, lnk_file):
        os.startfile(os.path.join(self.directory, lnk_file))

    def load_icons(self):
        lnk_files = list_lnk_files(self.directory)
        for index, lnk_file in enumerate(lnk_files):
            file_path = os.path.join(self.directory, lnk_file)
            custom_icon = self.get_custom_icon(lnk_file)
            if custom_icon:
                icon_image = custom_icon
            else:
                icon_extractor = IconExtractor(file_path)
                icon_image = icon_extractor.icon_to_image()
                if icon_image:
                    icon_image = icon_image.resize((64, 64), Image.LANCZOS)  # Resize here

            if icon_image:
                tk_image = ImageTk.PhotoImage(icon_image)
                label = tk.Label(self.frame, image=tk_image)  # No custom style
                label.image = tk_image
                label.grid(row=index // 4, column=index % 4, padx=10, pady=10)
                label.bind("<Button-1>", lambda event, lnk_file=lnk_file: self.open_link(lnk_file))

# Main function
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: app.exe <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print("Invalid directory")
        sys.exit(1)
    
    root = tk.Tk()
    app = LnkIconApp(root, directory)
    root.mainloop()
