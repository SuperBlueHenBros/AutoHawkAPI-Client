import tkinter as tk
from tkinter import filedialog

from pathlib import Path
from zipfile import ZipFile



def export_lua_components(path: str=None):
    """Export the Lua components for Bizhawk"""

    if path is None:
        # Open a dialog window for the user
        # to specify where to export the files
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        path = filedialog.askdirectory()

    # Get the path to where the ZIP file is stored
    from_ = str(Path(__file__).parent / 'lua_components.zip')

    # Extract!
    with ZipFile(from_, 'r') as f:
        f.extractall(path)