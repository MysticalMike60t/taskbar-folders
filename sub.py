import os
import sys
import customtkinter as ctk
from PIL import Image, ImageTk

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

def open_folder(folder_path, custom_icons):
    root = ctk.CTk()
    root.title("Folder Contents")
    
    print(root.cget("fg_color"))

    icons = load_icons(folder_path, custom_icons)
    if not icons:
        print("No icons found in the folder")
        root.destroy()
        return

    for i, (file_name, icon_info) in enumerate(icons.items()):
        row = i // 4
        col = i % 4
        button = ctk.CTkButton(root, image=icon_info["photo"], command=lambda path=icon_info["file_path"]: os.startfile(path), text="", fg_color=root.cget("fg_color"), hover_color="gray16")  # Corrected "app" to "root"
        button.image = icon_info["photo"]
        button.grid(row=row, column=col, padx=5, pady=5)

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
