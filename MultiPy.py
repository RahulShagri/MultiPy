from dearpygui.core import *
from dearpygui.simple import *
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
import threading

def run_script(file_path: str):
    file_path = file_path.split("/")
    folder_path = ''

    for folder in range(1, len(file_path)-1):
        folder_path += f"{file_path[folder]}\\"

    #Main run command on cmd
    os.system(f'start cmd /k "cd\\ & {file_path[0]} & cd {folder_path} & {file_path[-1]}"')

def run_script_dispatcher(file_path: str):
    run_script_thread = threading.Thread(name="runScriptThread", target=run_script, args=(file_path,), daemon=True)
    run_script_thread.start()

def remove_script(file: str, file_path:str):
    parent = "Loaded scripts"

    delete_item(f"{file}")
    delete_item(f"Run##{file_path}")
    delete_item(f"Remove##{file}")

def add_script():

    Tk().withdraw()
    file_path = askopenfilename(filetypes=[("Python file (*.py)", "*.py")],
                                defaultextension=[("Python file (*.py)", "*.py")])

    if file_path:
        file = file_path.split("/")[-1]

        add_text(f"{file}", parent="Loaded scripts")
        add_same_line(parent="Loaded scripts")
        add_button(f"Run##{file_path}", parent="Loaded scripts", callback=lambda data: run_script_dispatcher(file_path=file_path))
        add_same_line(parent="Loaded scripts")
        add_button(f"Remove##{file}", parent="Loaded scripts", callback=lambda data: remove_script(file=file, file_path=file_path))

with window("Main Window"):
    # Main Window styling
    set_theme(theme="grey")
    set_main_window_title("MultiPy")
    set_main_window_pos(x=0, y=0)
    set_main_window_size(width=1370, height=740)
    add_additional_font("fonts/glacial_font.otf", 20)

with window("Add Delete Scripts"):
    add_button(name="Load python script", callback=add_script)
    
with window("Loaded scripts"):
    pass

start_dearpygui(primary_window="Main Window")
