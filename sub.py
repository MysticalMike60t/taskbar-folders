import os
import sys
import platform
import ctypes
import customtkinter as ctk
from PIL import Image, ImageTk
import textwrap

def load_icons(folder_path, custom_icons):
    icons = {}
    
    try:
        files = os.listdir(folder_path)
    except FileNotFoundError:
        print("Folder not found")
        return {}

    for file in files:
        if os.path.isfile(os.path.join(folder_path, file)):
            _, ext = os.path.splitext(file)
            icon_file = custom_icons["filenames"].get(file.lower(), custom_icons["extensions"].get(ext.lower(), "default_icon.png"))
            icon_path = os.path.join("icons", icon_file)
            if os.path.isfile(icon_path):
                try:
                    image = Image.open(icon_path)
                    image = image.resize((100, 100))
                    photo = ImageTk.PhotoImage(image)
                    icons[file] = {"photo": photo, "file_path": os.path.join(folder_path, file)}
                except Exception as e:
                    print(f"Failed to load icon for {file}: {e}")
            else:
                print(f"No custom icon found for {file}, using default icon")
    return icons

def get_taskbar_height():
    if platform.system() == "Windows":
        try:
            # Use ctypes to get the taskbar height
            taskbar_height = ctypes.windll.user32.GetSystemMetrics(30)  # SM_CYFULLSCREEN
            return taskbar_height
        except Exception as e:
            print(f"Failed to get taskbar height: {e}")
    return 0

def open_file(file_path):
    os.startfile(file_path)

def open_folder(folder_path, custom_icons):
    root = ctk.CTk()
    root.title("Folder Contents")
    
    # Get the screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Get the taskbar height
    taskbar_height = get_taskbar_height()
    
    # Set the window size
    window_width = 400
    window_height = 300
    
    # Calculate the position to place the window in the center of the screen horizontally and vertically
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2 - taskbar_height // 2
    
    # Set the window geometry
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    print(root.cget("fg_color"))

    icons = load_icons(folder_path, custom_icons)
    if not icons:
        print("No icons found in the folder")
        root.destroy()
        return

    # Create a frame to contain the icons
    frame = ctk.CTkFrame(root)
    frame.pack(fill=ctk.BOTH, expand=True)

    canvas = ctk.CTkCanvas(frame)
    canvas.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
    scrollbar = ctk.CTkScrollbar(frame, command=canvas.yview)
    scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    inner_frame = ctk.CTkFrame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor=ctk.NW)

    # Calculate the number of icons per row based on available width and icon size
    icon_size = 100  # Assuming each icon is square
    available_width = window_width - scrollbar.winfo_width()  # Adjust for scrollbar width
    icons_per_row = max(1, available_width // (icon_size + 10))  # 10 pixels for padding
    
    for i, (file_name, icon_info) in enumerate(icons.items()):
        # Wrap the text based on a specified width
        wrapped_text = textwrap.fill(file_name, width=20)
        
        # Create a CTkLabel for each icon
        label = ctk.CTkLabel(inner_frame, image=icon_info["photo"], text=wrapped_text, compound="top", fg_color=root.cget("fg_color"))
        label.image = icon_info["photo"]
        label.grid(row=i // icons_per_row, column=i % icons_per_row, padx=5, pady=5)
        label.bind("<Button-1>", lambda event, path=icon_info["file_path"]: open_file(path))

    inner_frame.update_idletasks()  # Update the frame to calculate its size
    canvas.config(scrollregion=canvas.bbox("all"))

    # Enable scrolling with the mouse wheel
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    root.mainloop()

def main():
    if len(sys.argv) != 2:
        print("Usage: python folder_opener_gui.py <folder_path>")
        return

    folder_path = sys.argv[1]
    print("Folder path:", folder_path)

    custom_icons = {
        "extensions": {
            ".png": "png.png",
            ".jpg": "jpg.png",
            ".jpeg": "jpeg.png",
            ".gif": "gif.png",
            ".lnk": "lnk.png",
        },
        "filenames": {
            "xbox.lnk": "xbox.png",
            "ea.lnk": "ea.png",
            "minecraft launcher.lnk": "mojang.png",
            "battle.net.lnk": "battle.net.png",
            "epic games launcher.lnk": "epic-games.png",
            "steam.lnk": "steam.png",
            "oculus.lnk": "oculus.png",
            "pcsx2 1.6.0.lnk": "pcsx2.png",
            "playnite.lnk": "playnite.png",
            "battlestate games launcher.lnk": "bsg.png",
            "ubisoft connect.lnk": "ubisoft.png",
        }
    }

    open_folder(folder_path, custom_icons)

if __name__ == "__main__":
    main()
