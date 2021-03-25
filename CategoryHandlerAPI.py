from dearpygui.core import *
from dearpygui.simple import *
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
from DatabaseHandlerAPI import *
import threading

categories = {}

class CategoryHandler:
    def __init__(self, title: str):
        self.title = title
        self.parent = "Loaded scripts"
        self.script_count = 0

        with tree_node(name=self.title, parent=self.parent, default_open=True):
            add_dummy(name=f"{self.title}Dummy01", height=10)
            add_image_button(name=f"add_script##{self.title}", value="icons/add_script_button_dark.png", width=150, height=26)
            add_same_line(spacing=10)
            add_image_button(name=f"run_all##{self.title}", value="icons/run_all_button_dark.png", width=84, height=26, callback=self.run_all_scripts)
            add_same_line(spacing=10)
            add_image_button(name=f"delete_category##{self.title}", value="icons/delete_category_button_dark.png", width=157, height=26)
            add_dummy(name=f"{self.title}Dummy02", height=10)
            add_separator(name=f"{self.title}Separator01")
            add_dummy(name=f"{self.title}Dummy03", height=20)

            with popup(popupparent=f"delete_category##{self.title}", name=f"Are you sure you want to delete this category?##{self.title}", mousebutton=mvMouseButton_Left, modal=True):
                set_item_style_var(item=f"Are you sure you want to delete this category?##{self.title}", style=mvGuiStyleVar_WindowPadding, value=[10, 10])
                add_button(f"Yes##DeleteCategory{self.title}", width=220, callback=self.delete_category)
                add_same_line(spacing=10.0)
                add_button(f"No##DeleteCategory{self.title}", width=220, callback=self.close_popups)

            with popup(popupparent=f"add_script##{self.title}", name=f"Add new python script##{self.title}", mousebutton=mvMouseButton_Left, modal=True):
                set_item_style_var(item=f"Add new python script##{self.title}", style=mvGuiStyleVar_WindowPadding, value=[10, 10])
                add_dummy(name="addScriptDummy01", height=10)

                add_input_text(name=f"script_name_{self.title}", label="    Enter script name", hint="Script name", tip="Leave blank to set it the same as the file name.", width=250)
                add_dummy(name="addScriptDummy02", height=20)

                add_input_text(name=f"script_path_{self.title}", label="", hint="Script path", width=250, readonly=True)
                add_same_line(spacing=5)
                add_button(name=f"Find script##{self.title}", width=150, callback=self.find_script)
                add_dummy(name="addScriptDummy03", height=20)

                add_checkbox(name=f"Script uses virtual environment##{self.title}", callback=self.enable_venv)
                add_dummy(name="addScriptDummy04", height=20)
                add_input_text(name=f"venv_path_{self.title}", label="", hint="Venv folder path", width=250, enabled=False, readonly=True)
                add_same_line(spacing=5)
                add_button(name=f"Find venv folder##{self.title}", width=150, enabled=False, callback=self.find_venv)
                add_dummy(name="addScriptDummy05", height=20)

                add_input_text(name=f"thumbnail_path_{self.title}", label="", hint="Thumbnail file path", width=250, readonly=True)
                add_same_line(spacing=5)
                add_button(name=f"Add thumbnail##{self.title}", width=150, tip="Leave blank to set it to default.", callback=self.find_thumbnail)
                add_dummy(name="addScriptDummy06", height=20)
                add_drawing(name=f"thumbnail_{self.title}", width=410, height=231)
                draw_polyline(drawing=f"thumbnail_{self.title}", points=[[0,0], [410,0], [410,231], [0,231]], color=[255,0,0], thickness=1, closed=True)


                add_dummy(name="addScriptDummy06", height=20)
                add_button(f"Add##AddScript_{self.title}", width=210, callback=self.add_script, callback_data=lambda: self.add_script)
                add_same_line(spacing=5.0)
                add_button(f"Cancel##AddScript_{self.title}", width=210, callback=self.close_popups)

        add_dummy(name=f"{self.title}DummySeparator", height=10, parent=self.parent)

    def close_popups(self, sender):
        if sender == f"Cancel##AddScript_{self.title}":
            set_value(f"script_name_{self.title}", "")
            set_value(f"script_path_{self.title}", "")
            set_value(f"Script uses virtual environment##{self.title}", False)
            set_value(f"venv_path_{self.title}", "")
            set_value(f"thumbnail_path_{self.title}", "")
            self.enable_venv()
            clear_drawing(f"thumbnail_{self.title}")
            draw_polyline(drawing=f"thumbnail_{self.title}", points=[[0, 0], [410, 0], [410, 231], [0, 231]],
                          color=[255, 0, 0], thickness=1, closed=True)

            if does_item_exist("Please select a script."):
                delete_item("Please select a script.")

            if does_item_exist("Script name already in use. Please use a different name."):
                delete_item("Script name already in use. Please use a different name.")

            if does_item_exist("Please select a venv path."):
                delete_item("Please select a venv path.")

            close_popup(f"Add new python script##{self.title}")

        if sender == f"No##DeleteCategory{self.title}":
            close_popup(f"Are you sure you want to delete this category?##{self.title}")

    def delete_category(self):
        delete_item(self.title)
        del categories[self.title]
        delete_table(self.title)

    def add_script(self):

        if does_item_exist("Script name already in use. Please use a different name."):
            delete_item("Script name already in use. Please use a different name.")

        if not get_value(f"script_path_{self.title}"):
            if not does_item_exist("Please select a script."):
                add_text("Please select a script.", color=[255,0,0], parent=f"Add new python script##{self.title}", before="addScriptDummy03")
                return
            else:
                return

        scripts = []
        for script in read_all_script_names(table=self.title):
            scripts.append(script[0])

        if get_value(f"script_name_{self.title}") in scripts:
            if not does_item_exist("Script name already in use. Please use a different name."):
                add_text("Script name already in use. Please use a different name.", color=[255,0,0], parent=f"Add new python script##{self.title}", before="addScriptDummy02")
                return
            else:
                return

        if get_value(f"Script uses virtual environment##{self.title}"):
            if not get_value(f"venv_path_{self.title}"):
                if not does_item_exist("Please select a venv path."):
                    add_text("Please select a venv path.", color=[255,0,0], parent=f"Add new python script##{self.title}", before="addScriptDummy05")
                    return
                else:
                    return

        if does_item_exist("Please select a script."):
            delete_item("Please select a script.")

        if does_item_exist("Script name already in use. Please use a different name."):
            delete_item("Script name already in use. Please use a different name.")

        if does_item_exist("Please select a venv path."):
            delete_item("Please select a venv path.")

        parent = self.title
        _temp_script_name_ = get_value(f"script_name_{self.title}")

        _temp_path_ = ""
        if get_value(f"thumbnail_path_{self.title}"):
            _temp_path_ = get_value(f"thumbnail_path_{self.title}")
        else:
            _temp_path_ = "icons/default_thumbnail.jpg"

        if _temp_script_name_ == "":
            _temp_script_name_ = get_value(f"script_path_{self.title}").split("/")[-1]

        # Update database
        if get_value(f"Script uses virtual environment##{self.title}"):
            add_script(table=self.title,
                       script_name=_temp_script_name_,
                       script_path=get_value(f"script_path_{self.title}"),
                       thumbnail_path=_temp_path_,
                       venv="True",
                       venv_path=get_value(f"venv_path_{self.title}"))

        else:
            add_script(table=self.title,
                       script_name=_temp_script_name_,
                       script_path=get_value(f"script_path_{self.title}"),
                       thumbnail_path=_temp_path_,
                       venv="False")

        if self.script_count > 0:
            if self.script_count % 3 != 0:
                add_same_line(spacing=70, parent=parent)

            else:
                add_dummy(height=10)

        self.script_count += 1

        with child(name=f"child_{self.title}_{_temp_script_name_}", parent=parent, width=350, height=200):

            if get_value(f"thumbnail_path_{self.title}"):
                add_image_button(f"{self.title}_{_temp_script_name_}", value=get_value(f"thumbnail_path_{self.title}"), width=250,
                                 height=141, frame_padding=5, callback=self.run_script)
                add_same_line(spacing=5)

            else:
                add_image_button(f"{self.title}_{_temp_script_name_}", value="icons/default_thumbnail.jpg", width=250,
                                 height=141, frame_padding=5, callback=self.run_script_dispatcher)
                add_same_line(spacing=5)

            with child(name=f"sub-child_{self.title}_{_temp_script_name_}", width=50, height=150):
                add_image_button(name=f"delete_{self.title}_{_temp_script_name_}", value="icons/delete_script_button_dark.png", width=30, height=30, callback=self.delete_script)
                #add_image_button(name=f"configure_{self.title}_{_temp_script_name_}", value="icons/configure_script_button_dark.png", width=30, height=30)

            add_text(f"{_temp_script_name_}", wrap=265)

        del _temp_path_
        del _temp_script_name_

        # Reset add script popup
        set_value(f"script_name_{self.title}", "")
        set_value(f"script_path_{self.title}", "")
        set_value(f"Script uses virtual environment##{self.title}", False)
        set_value(f"venv_path_{self.title}", "")
        set_value(f"thumbnail_path_{self.title}", "")
        self.enable_venv()
        clear_drawing(f"thumbnail_{self.title}")
        draw_polyline(drawing=f"thumbnail_{self.title}", points=[[0, 0], [410, 0], [410, 231], [0, 231]],
                      color=[255, 0, 0], thickness=1, closed=True)

        close_popup(f"Add new python script##{self.title}")

    def run_script(self, sender):
        category = sender.split("_")[0]
        script = sender[len(category)+1:]

        script_info = read_to_run_script(table=category, script_name=script)
        file_path = script_info[0].split("/")
        folder_path = ''
        venv_folder_path = script_info[2] + "/Scripts"
        venv_drive = venv_folder_path.split("/")[0]
        venv_folder_path = venv_folder_path[3:]

        if script_info[1] == "False":

            for folder in range(1, len(file_path) - 1):
                folder_path += f"{file_path[folder]}\\"

            # Main run command on cmd
            os.system(f'start cmd /k "cd\\ & {file_path[0]} & cd {folder_path} & {file_path[-1]}"')

        else:

            for folder in range(1, len(file_path) - 1):
                folder_path += f"{file_path[folder]}\\"

            # Main run command on cmd
            os.system(f'start cmd /k "cd\\ & {venv_drive} & cd {venv_folder_path} & "activate.bat" & cd\\ & {file_path[0]} & cd {folder_path} & {file_path[-1]}"')

    def run_script_dispatcher(self, sender):
        run_script_thread = threading.Thread(name="runScriptThread", target=self.run_script, args=(sender,),
                                             daemon=True)
        run_script_thread.start()

    def run_all_scripts(self, sender):
        all_script_info = read_to_run_all_scripts(sender[9:])

        for script_info in all_script_info:
            self.run_all_scripts_dispatcher(script_info)

    def run_all_scripts_dispatcher(self, script_info):
        run_script_thread = threading.Thread(name="runScriptThread", target=self.run_each_script, args=(script_info,),
                                             daemon=True)
        run_script_thread.start()

    def run_each_script(self, script_info):
        file_path = script_info[0].split("/")
        folder_path = ''
        venv_folder_path = script_info[2] + "/Scripts"
        venv_drive = venv_folder_path.split("/")[0]
        venv_folder_path = venv_folder_path[3:]

        if script_info[1] == "False":

            for folder in range(1, len(file_path) - 1):
                folder_path += f"{file_path[folder]}\\"

            # Main run command on cmd
            os.system(f'start cmd /k "cd\\ & {file_path[0]} & cd {folder_path} & {file_path[-1]}"')

        else:

            for folder in range(1, len(file_path) - 1):
                folder_path += f"{file_path[folder]}\\"

            # Main run command on cmd
            os.system(
                f'start cmd /k "cd\\ & {venv_drive} & cd {venv_folder_path} & "activate.bat" & cd\\ & {file_path[0]} & cd {folder_path} & {file_path[-1]}"')

    def delete_script(self, sender):
        sender = sender[7:]
        category = sender.split("_")[0]
        script = sender[len(category)+1: ]
        delete_script(table=category, script_name=script)
        delete_item(f"child_{sender}")

        self.script_count -= 1

    def enable_venv(self):
        if get_value(f"Script uses virtual environment##{self.title}"):
            configure_item(f"venv_path_{self.title}", enabled=True)
            configure_item(f"Find venv folder##{self.title}", enabled=True)

        else:
            configure_item(f"venv_path_{self.title}", enabled=False)
            configure_item(f"Find venv folder##{self.title}", enabled=False)

    def find_script(self):
        Tk().withdraw()

        file_path = askopenfilename(title="MultiPy find script window",
                                    filetypes=[("Python File (*.py)", "*.py")],
                                    defaultextension=[("Python File (*.py)", "*.py")])

        if file_path:
            set_value(f"script_path_{self.title}", file_path)

            if does_item_exist("Please select a script."):
                delete_item("Please select a script.")

    def find_venv(self):
        Tk().withdraw()

        folder_path = askdirectory(title="MultiPy find venv window")

        if folder_path:
            set_value(f"venv_path_{self.title}", folder_path)

            if does_item_exist("Please select a venv path."):
                delete_item("Please select a venv path.")

    def find_thumbnail(self):
        Tk().withdraw()

        file_path = askopenfilename(title="MultiPy find thumbnail window",
                                    filetypes=[("PNG (*.png)", "*.png"), ("JPG (*.jpg)", "*.jpg")],
                                    defaultextension=[("PNG (*.png)", "*.png"), ("JPG (*.jpg)", "*.jpg")])

        if file_path:
            set_value(f"thumbnail_path_{self.title}", file_path)
            clear_drawing(f"thumbnail_{self.title}")
            draw_image(drawing=f"thumbnail_{self.title}", file=get_value(f"thumbnail_path_{self.title}"), pmin=[0,0], pmax=[410,231])


def close_popups(sender):

    if sender == "Cancel##AddCategory":

        set_value("category_name", value='')

        if does_item_exist("Category name already in use. Please enter a new name."):
            delete_item("Category name already in use. Please enter a new name.")
            add_dummy(name="addCategoryDummy02", height=20, before="Add##AddCategory")

        close_popup("Add new category")

def add_category():

    global categories

    category_name = get_value("category_name")

    if category_name:
        if category_name in categories.keys():
            if not does_item_exist("Category name already in use. Please enter a new name."):
                add_text("Category name already in use. Please enter a new name.", color=[255,0,0], parent="Add new category", before="addCategoryDummy02")
                delete_item("addCategoryDummy02")
            return

        # Resetting add category popup window
        set_value("category_name", value='')

        if does_item_exist("Category name already in use. Please enter a new name."):
            delete_item("Category name already in use. Please enter a new name.")
            add_dummy(name="addCategoryDummy02", height=20, before="Add##AddCategory")

        close_popup("Add new category")

        if does_item_exist("Instructions"):
            delete_item("Instructions")

        # Creating new category tree nodes
        categories[category_name] = CategoryHandler(title=category_name)

        create_table(name=category_name) # Create new table in DB