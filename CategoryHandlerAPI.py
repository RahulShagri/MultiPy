from dearpygui.core import *
from dearpygui.simple import *
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askdirectory
from DatabaseHandlerAPI import *
import threading
import win32gui
import re

categories = {}

class CategoryHandler:
    def __init__(self, title: str):
        self.title = title
        self.parent = "Loaded scripts"
        self.script_count = 0

        with collapsing_header(name=self.title, parent=self.parent):
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

                add_input_text(name=f"script_name??{self.title}", label="    Enter script name", hint="Script name", tip="Leave blank to set it the same as the file name.", width=250)
                add_dummy(name="addScriptDummy02", height=20)

                add_input_text(name=f"script_path??{self.title}", label="", hint="Script path", width=250, readonly=True)
                add_same_line(spacing=5)
                add_button(name=f"Find script##{self.title}", width=150, callback=self.find_script)
                add_dummy(name="addScriptDummy03", height=20)

                add_checkbox(name=f"Script uses virtual environment##{self.title}", callback=self.enable_venv)
                add_dummy(name="addScriptDummy04", height=20)
                add_input_text(name=f"venv_path??{self.title}", label="", hint="Venv folder path", width=250, enabled=False, readonly=True)
                add_same_line(spacing=5)
                add_button(name=f"Find venv folder##{self.title}", width=150, enabled=False, callback=self.find_venv)
                add_dummy(name="addScriptDummy05", height=20)

                add_input_text(name=f"thumbnail_path??{self.title}", label="", hint="Thumbnail file path", width=250, readonly=True)
                add_same_line(spacing=5)
                add_button(name=f"Add thumbnail##{self.title}", width=150, tip="Leave blank to set it to default.", callback=self.find_thumbnail)
                add_dummy(name="addScriptDummy06", height=20)
                add_drawing(name=f"thumbnail??{self.title}", width=410, height=231)
                draw_polyline(drawing=f"thumbnail??{self.title}", points=[[0,0], [410,0], [410,231], [0,231]], color=[255,0,0], thickness=1, closed=True)


                add_dummy(name="addScriptDummy06", height=20)
                add_button(f"Add##AddScript??{self.title}", width=210, callback=self.add_script, callback_data=lambda: self.add_script)
                add_same_line(spacing=5.0)
                add_button(f"Cancel##AddScript??{self.title}", width=210, callback=self.close_popups)

        add_dummy(name=f"{self.title}DummySeparator", height=10, parent=self.parent)

    def close_popups(self, sender, data=""):
        if sender == f"Cancel##AddScript??{self.title}":
            set_value(f"script_name??{self.title}", "")
            set_value(f"script_path??{self.title}", "")
            set_value(f"Script uses virtual environment##{self.title}", False)
            set_value(f"venv_path??{self.title}", "")
            set_value(f"thumbnail_path??{self.title}", "")
            self.enable_venv(f"Script uses virtual environment##{self.title}")
            clear_drawing(f"thumbnail??{self.title}")
            draw_polyline(drawing=f"thumbnail??{self.title}", points=[[0, 0], [410, 0], [410, 231], [0, 231]],
                          color=[255, 0, 0], thickness=1, closed=True)

            if does_item_exist("Please select a script."):
                delete_item("Please select a script.")

            if does_item_exist("Script name already in use. Please use a different name."):
                delete_item("Script name already in use. Please use a different name.")

            if does_item_exist("Script is already in use with the file name.\nPlease enter a name."):
                delete_item("Script is already in use with the file name.\nPlease enter a name.")

            if does_item_exist("Please select a venv path."):
                delete_item("Please select a venv path.")

            close_popup(f"Add new python script##{self.title}")

        if sender == f"No##DeleteCategory{self.title}":
            close_popup(f"Are you sure you want to delete this category?##{self.title}")

        if re.search("Update", sender):
            close_popup(f"Configure script##{self.title}??{data}")

    def delete_category(self):
        delete_item(self.title)
        delete_item(f"{self.title}DummySeparator")
        del categories[self.title]
        delete_table(self.title)

        tables, temp = read_all_tables()

        if not tables:
            configure_item("Instructions", show=True)
            configure_item("view_button", show=False)

    def add_script(self):

        if does_item_exist("Script name already in use. Please use a different name."):
            delete_item("Script name already in use. Please use a different name.")

        if does_item_exist("Script is already in use with the file name.\nPlease enter a name."):
            delete_item("Script is already in use with the file name.\nPlease enter a name.")

        if not get_value(f"script_path??{self.title}"):
            if not does_item_exist("Please select a script."):
                add_text("Please select a script.", color=[255,0,0], parent=f"Add new python script##{self.title}", before="addScriptDummy03")
                return
            else:
                return

        scripts = []
        for script in read_all_scripts(table=self.title):
            scripts.append(script[0])

        if get_value(f"script_name??{self.title}") in scripts:
            if not does_item_exist("Script name already in use. Please use a different name."):
                add_text("Script name already in use. Please use a different name.", color=[255,0,0], parent=f"Add new python script##{self.title}", before="addScriptDummy02")
                return
            else:
                return

        if get_value(f"Script uses virtual environment##{self.title}"):
            if not get_value(f"venv_path??{self.title}"):
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
        _temp_script_name_ = get_value(f"script_name??{self.title}")

        _temp_path_ = ""
        if get_value(f"thumbnail_path??{self.title}"):
            _temp_path_ = get_value(f"thumbnail_path??{self.title}")
        else:
            _temp_path_ = "icons/default_thumbnail.jpg"

        if _temp_script_name_ == "":
            _temp_script_name_ = get_value(f"script_path??{self.title}").split("/")[-1]

            if _temp_script_name_ in scripts:
                if not does_item_exist("Script is already in use with the file name.\nPlease enter a name."):
                    add_text("Script is already in use with the file name.\nPlease enter a name.", color=[255, 0, 0],
                             parent=f"Add new python script##{self.title}", before="addScriptDummy02")
                    return
                else:
                    return


        # Update database
        if get_value(f"Script uses virtual environment##{self.title}"):
            add_script(table=self.title,
                       script_name=_temp_script_name_,
                       script_path=get_value(f"script_path??{self.title}"),
                       thumbnail_path=_temp_path_,
                       venv="True",
                       venv_path=get_value(f"venv_path??{self.title}"))

        else:
            add_script(table=self.title,
                       script_name=_temp_script_name_,
                       script_path=get_value(f"script_path??{self.title}"),
                       thumbnail_path=_temp_path_,
                       venv="False")

        if self.script_count > 0:
            if self.script_count % 3 != 0:
                add_same_line(parent=parent)

            else:
                add_dummy(height=20, parent=parent)

        self.script_count += 1

        with child(name=f"child??{self.title}??{_temp_script_name_}", parent=parent, width=400, height=210):

            if get_value(f"thumbnail_path??{self.title}"):
                add_image_button(f"{self.title}??{_temp_script_name_}", value=get_value(f"thumbnail_path??{self.title}"), width=250,
                                 height=141, frame_padding=5, callback=self.run_script)
                add_same_line(spacing=5)

            else:
                add_image_button(f"{self.title}??{_temp_script_name_}", value="icons/default_thumbnail.jpg", width=250,
                                 height=141, frame_padding=5, callback=self.run_script_dispatcher)
                add_same_line(spacing=5)

            with child(name=f"sub-child??{self.title}??{_temp_script_name_}", width=50, height=150):
                add_image_button(name=f"delete??{self.title}??{_temp_script_name_}", value="icons/delete_script_button_dark.png", width=30, height=30, callback=self.delete_script)
                #add_image_button(name=f"configure??{self.title}??{_temp_script_name_}", value="icons/configure_script_button_dark.png", width=30, height=30)

                # # Popup for configuring script info
                #
                # with popup(popupparent=f"configure??{self.title}??{_temp_script_name_}",
                #            name=f"Configure script##{self.title}??{_temp_script_name_}", mousebutton=mvMouseButton_Left, modal=True):
                #
                #     script_info = get_script_info(table=self.title, script=_temp_script_name_)
                #
                #     set_item_style_var(item=f"Configure script##{self.title}??{_temp_script_name_}", style=mvGuiStyleVar_WindowPadding,
                #                        value=[10, 10])
                #     add_dummy(name="addScriptDummy01", height=10)
                #
                #     # script name
                #     add_input_text(name=f"configure_script_name??{self.title}??{_temp_script_name_}", label="    Enter script name",
                #                    hint="Script name", tip="Leave blank to set it the same as the file name.",
                #                    width=250)
                #
                #     set_value(f"configure_script_name??{self.title}??{_temp_script_name_}", value=script_info[0])
                #
                #     add_dummy(name="addScriptDummy02", height=20)
                #
                #     # script path
                #     add_input_text(name=f"configure_script_path??{self.title}??{_temp_script_name_}", label="", hint="Script path", width=250,
                #                    readonly=True)
                #
                #     set_value(f"configure_script_path??{self.title}??{_temp_script_name_}", value=script_info[1])
                #
                #     add_same_line(spacing=5)
                #     add_button(name=f"Find script##configure??{self.title}??{_temp_script_name_}", width=150, callback=self.find_script, callback_data=_temp_script_name_)
                #     add_dummy(name="addScriptDummy03", height=20)
                #
                #     # venv
                #     add_checkbox(name=f"Script uses virtual environment##configure??{self.title}??{_temp_script_name_}", callback=self.enable_venv, callback_data=_temp_script_name_)
                #     add_dummy(name="addScriptDummy04", height=20)
                #     add_input_text(name=f"configure_venv_path??{self.title}??{_temp_script_name_}", label="", hint="Venv folder path", width=250,
                #                    enabled=False, readonly=True)
                #
                #     if script_info[2] == "":
                #         set_value(f"Script uses virtual environment##configure??{self.title}??{_temp_script_name_}", True)
                #         set_value(f"configure_venv_path??{self.title}??{_temp_script_name_}", script_info[3])
                #     else:
                #         set_value(f"Script uses virtual environment##configure??{self.title}??{_temp_script_name_}", False)
                #
                #     add_same_line(spacing=5)
                #     add_button(name=f"Find venv folder##configure??{self.title}??{_temp_script_name_}", width=150, enabled=False,
                #                callback=self.find_venv, callback_data=_temp_script_name_)
                #     add_dummy(name="addScriptDummy05", height=20)
                #
                #     #thumbnail
                #     add_input_text(name=f"configure_thumbnail_path??{self.title}??{_temp_script_name_}", label="", hint="Thumbnail file path",
                #                    width=250, readonly=True)
                #
                #     if script_info[4] == "icons/default_thumbnail.jpg": set_value(f"configure_thumbnail_path??{self.title}??{_temp_script_name_}", "")
                #     else: set_value(f"configure_thumbnail_path??{self.title}??{_temp_script_name_}", script_info[4])
                #
                #     add_same_line(spacing=5)
                #     add_button(name=f"Add thumbnail##configure??{self.title}??{_temp_script_name_}", width=150,
                #                tip="Leave blank to set it to default.", callback=self.find_thumbnail, callback_data=_temp_script_name_)
                #     add_dummy(name="addScriptDummy06", height=20)
                #     add_drawing(name=f"configure_thumbnail??{self.title}??{_temp_script_name_}", width=410, height=231)
                #     draw_image(f"configure_thumbnail??{self.title}??{_temp_script_name_}", file=script_info[4], pmin=[0,0], pmax=[410, 232])
                #
                #     add_dummy(name="addScriptDummy06", height=20)
                #     add_button(f"Update##UpdateScript??{self.title}??{_temp_script_name_}", width=210, callback=self.update_script, callback_data=lambda: self.update_script(data=_temp_script_name_, old_script_name=_temp_script_name_))
                #     add_same_line(spacing=5.0)
                #     add_button(f"Cancel##UpdateScript??{self.title}??{_temp_script_name_}", width=210, callback=self.close_popups, callback_data=_temp_script_name_)

            add_text(f"{_temp_script_name_}", wrap=265)

        del _temp_path_
        del _temp_script_name_

        # Reset add script popup
        set_value(f"script_name??{self.title}", "")
        set_value(f"script_path??{self.title}", "")
        set_value(f"Script uses virtual environment##{self.title}", False)
        set_value(f"venv_path??{self.title}", "")
        set_value(f"thumbnail_path??{self.title}", "")
        self.enable_venv(f"Script uses virtual environment##{self.title}")
        clear_drawing(f"thumbnail??{self.title}")
        draw_polyline(drawing=f"thumbnail??{self.title}", points=[[0, 0], [410, 0], [410, 231], [0, 231]],
                      color=[255, 0, 0], thickness=1, closed=True)

        close_popup(f"Add new python script##{self.title}")

    def run_script(self, sender):
        category = sender.split("??")[0]
        script = sender[len(category)+2:]

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
            os.system(f'start cmd /k "cd\\ & {file_path[0]} & cd {folder_path} & {file_path[-1]} & exit"')

        else:

            for folder in range(1, len(file_path) - 1):
                folder_path += f"{file_path[folder]}\\"

            # Main run command on cmd
            os.system(f'start cmd /k "cd\\ & {venv_drive} & cd {venv_folder_path} & "activate.bat" & cd\\ & {file_path[0]} & cd {folder_path} & {file_path[-1]} & exit"')

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
            os.system(f'start cmd /k "cd\\ & {file_path[0]} & cd {folder_path} & {file_path[-1]} & exit"')

        else:

            for folder in range(1, len(file_path) - 1):
                folder_path += f"{file_path[folder]}\\"

            # Main run command on cmd
            os.system(
                f'start cmd /k "cd\\ & {venv_drive} & cd {venv_folder_path} & "activate.bat" & cd\\ & {file_path[0]} & cd {folder_path} & {file_path[-1]}"')

    def delete_script(self, sender):
        parent = self.title
        sender = sender[8:]
        category = sender.split("??")[0]
        script = sender[len(category)+2: ]
        delete_script(table=category, script_name=script)
        delete_item(f"child??{sender}")

        scripts = read_all_scripts(table=self.title)
        for script in scripts:
            delete_item(f"child??{self.title}??{script[0]}")

        self.script_count = 0

        if does_item_exist("tempDummy"):
            delete_item("tempDummy")

        add_dummy(name="tempDummy", parent=parent)

        for script in scripts:
            script_name = script[0]
            thumbnail_path = script[1]

            if self.script_count > 0:
                if self.script_count % 3 != 0:
                    add_same_line(parent=parent)

                else:
                    add_dummy(height=20, parent=parent)

            self.script_count += 1

            with child(name=f"child??{self.title}??{script_name}", parent=parent, width=400, height=210):

                add_image_button(f"{self.title}??{script_name}", value=thumbnail_path,
                                 width=250, height=141, frame_padding=5, callback=self.run_script_dispatcher)
                add_same_line(spacing=5)

                with child(name=f"sub-child??{self.title}??{script_name}", width=50, height=150):
                    add_image_button(name=f"delete??{self.title}??{script_name}",
                                     value="icons/delete_script_button_dark.png", width=30, height=30,
                                     callback=self.delete_script)
                    #add_image_button(name=f"configure??{self.title}??{script_name}", value="icons/configure_script_button_dark.png", width=30, height=30)

                add_text(f"{script_name}", wrap=265)

    # def update_script(self, data, old_script_name):
    #     script_name = get_value(f"configure_script_name??{self.title}??{data}")
    #     script_path = get_value(f"configure_script_path??{self.title}??{data}")
    #     venv = get_value(f"Script uses virtual environment##configure??{self.title}??{data}")
    #     venv_path = get_value(f"configure_venv_path??{self.title}??{data}")
    #     thumbnail_path = get_value(f"configure_thumbnail_path??{self.title}??{data}")
    #
    #     update_script(table=self.title, old_script_name=old_script_name, script_name=script_name, script_path=script_path, venv=venv, venv_path=venv_path, thumbnail_path=thumbnail_path)

    def enable_venv(self, sender, data=""):
        if get_value(sender):
            configure_item(f"venv_path??{self.title}", enabled=True)
            configure_item(f"Find venv folder##{self.title}", enabled=True)

            if re.search("configure", sender):
                configure_item(f"configure_venv_path??{self.title}??{data}", enabled=True)
                configure_item(f"Find venv folder##configure??{self.title}??{data}", enabled=True)

        else:
            configure_item(f"venv_path??{self.title}", enabled=False)
            configure_item(f"Find venv folder##{self.title}", enabled=False)

            if re.search("configure", sender):
                configure_item(f"configure_venv_path??{self.title}??{data}", enabled=False)
                configure_item(f"Find venv folder##configure??{self.title}??{data}", enabled=False)

    def find_script(self, sender, data=""):
        Tk().withdraw()

        file_path = askopenfilename(title="MultiPy find script window",
                                    filetypes=[("Python File (*.py)", "*.py")],
                                    defaultextension=[("Python File (*.py)", "*.py")])

        if file_path:
            set_value(f"script_path??{self.title}", file_path)

            if re.search("configure", sender):
                set_value(f"configure_script_path??{self.title}??{data}", file_path)

            if does_item_exist("Please select a script."):
                delete_item("Please select a script.")

    def find_venv(self, sender, data=""):
        Tk().withdraw()

        folder_path = askdirectory(title="MultiPy find venv window")

        if folder_path:
            set_value(f"venv_path??{self.title}", folder_path)

            if re.search("configure", sender):
                set_value(f"configure_venv_path??{self.title}??{data}", folder_path)

            if does_item_exist("Please select a venv path."):
                delete_item("Please select a venv path.")

    def find_thumbnail(self, sender, data=""):
        Tk().withdraw()

        file_path = askopenfilename(title="MultiPy find thumbnail window",
                                    filetypes=[("PNG (*.png)", "*.png"), ("JPG (*.jpg)", "*.jpg")],
                                    defaultextension=[("PNG (*.png)", "*.png"), ("JPG (*.jpg)", "*.jpg")])

        if file_path:
            set_value(f"thumbnail_path??{self.title}", file_path)
            clear_drawing(f"thumbnail??{self.title}")
            draw_image(drawing=f"thumbnail??{self.title}", file=get_value(f"thumbnail_path??{self.title}"), pmin=[0,0], pmax=[410,231])

            if re.search("configure", sender):
                set_value(f"configure_thumbnail_path??{self.title}??{data}", file_path)
                clear_drawing(f"configure_thumbnail??{self.title}??{data}")
                draw_image(drawing=f"configure_thumbnail??{self.title}??{data}", file=get_value(f"thumbnail_path??{self.title}"),
                           pmin=[0, 0], pmax=[410, 231])



def close_popups(sender):

    if sender == "Cancel##AddCategory":

        set_value("category_name", value='')

        if does_item_exist("Category name already in use. Please enter a new name."):
            delete_item("Category name already in use. Please enter a new name.")
            add_dummy(name="addCategoryDummy02", height=20, before="Add##AddCategory")

        if does_item_exist("Category name cannot include \\ / : ? \" < >  |"):
            delete_item("Category name cannot include \\ / : ? \" < >  |")
            add_dummy(name="addCategoryDummy02", height=20, before="Add##AddCategory")

        close_popup("Add new category")

def add_category():

    global categories

    category_name = get_value("category_name")

    if category_name:
        invalid_characters = ["\\", "/", ":", "?", "\"", "<", ">", "|"]

        for character in category_name:
            if character in invalid_characters:
                if not does_item_exist("Category name cannot include \\ / : ? \" < >  |"):
                    add_text("Category name cannot include \\ / : ? \" < >  |", color=[255,0,0], parent="Add new category", before="addCategoryDummy02")
                    delete_item("addCategoryDummy02")
                return

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

        if does_item_exist("Category name cannot include \\ / : ? \" < >  |"):
            delete_item("Category name cannot include \\ / : ? \" < >  |")
            add_dummy(name="addCategoryDummy02", height=20, before="Add##AddCategory")

        close_popup("Add new category")

        configure_item("Instructions", show=False)

        # Creating new category tree nodes
        categories[category_name] = CategoryHandler(title=category_name)

        create_table(name=category_name) # Create new table in DB

        # Show tool buttons
        configure_item("view_button", show=True)

def show_edit_mode_switcher(sender):
    tables, all_scripts = read_all_tables()

    if sender == "view_button":

        delete_item("view_button")

        add_image_button(name="edit_button", value="icons/edit_button_dark.png", width=36, height=36,
                         tip="Switch to edit mode", parent="Tools", before="tools_line", callback=show_edit_mode_switcher)

        configure_item("add_category", show=False)
        configure_item("File", show=False)

        table_count = 0

        for table in tables:

            configure_item(f"add_script##{table[0]}", show=False)
            configure_item(f"run_all##{table[0]}", show=False)
            configure_item(f"delete_category##{table[0]}", show=False)

            for scripts in all_scripts[table_count]:
                for script in scripts:
                    configure_item(f"delete??{table[0]}??{script}", show=False)
                    configure_item(f"configure??{table[0]}??{script}", show=False)

            table_count += 1

    if sender == "edit_button":

        delete_item("edit_button")

        add_image_button(name="view_button", value="icons/view_button_dark.png", width=36, height=36,
                         tip="Switch to view-only mode", parent="Tools", before="tools_line", callback=show_edit_mode_switcher)

        configure_item("add_category", show=True)
        configure_item("File", show=True)

        table_count = 0

        for table in tables:

            configure_item(f"add_script##{table[0]}", show=True)
            configure_item(f"run_all##{table[0]}", show=True)
            configure_item(f"delete_category##{table[0]}", show=True)

            for scripts in all_scripts[table_count]:
                for script in scripts:
                    configure_item(f"delete??{table[0]}??{script}", show=True)
                    configure_item(f"configure??{table[0]}??{script}", show=True)

            table_count += 1

def save_tool():
    Tk().withdraw()

    file_path = asksaveasfilename(title="MultiPy Save window",
                                  initialfile="MultiPy Dashboard",
                                  filetypes=[("MultiPy File (*.mpy)", "*.mpy")],
                                  defaultextension=[("MultiPy File (*.mpy)", "*.mpy")])
    hwnd = win32gui.FindWindow(None, "MultiPy")
    win32gui.SetForegroundWindow(hwnd)

    if file_path:
        save_all(file_path=file_path)

def open_tool():
    Tk().withdraw()

    file_path = askopenfilename(title="MultiPy Open window",
                                filetypes=[("MultiPy File (*.mpy)", "*.mpy")],
                                defaultextension=[("MultiPy File (*.mpy)", "*.mpy")])
    hwnd = win32gui.FindWindow(None, "MultiPy")
    win32gui.SetForegroundWindow(hwnd)

    if file_path:
        global categories
        os.remove("_temp_.db")
        categories = {}

        original = file_path
        target = os.path.abspath("_temp_.db")
        shutil.copyfile(original, target)

        delete_item("Loaded scripts", children_only=True)
        configure_item("view_button", show=True)

        with child("Instructions", height=200, show=False, parent="Loaded scripts"):
            add_dummy(name="loadedScriptsDummy01", height=15)
            add_text("INSTRUCTIONS:")
            add_dummy(name="loadedScriptsDummy01", height=20)
            add_text(">    Click on \"Add new category\" button to get started.")
            add_text(">    Enter a name and click \"Add\".")
            add_text(">    Click on \"Add new python script\", and enter all the details as required.")
            add_text(">    Click on the thumbnails to run individual scripts or click on \"Run all\" to run all the scripts in that category.")
            add_dummy(name="dummy03", height=20)
            # add_text("You can find more information in the help menu.")

        tables, all_scripts = read_all()

        if not tables:
            configure_item("Instructions", show=True)
            configure_item("view_button", show=False)

        table_count = 0
        script_count = 0

        for table in tables:
            categories[table[0]] = CategoryHandler(title=table[0])

            parent = table[0]

            for script_info in all_scripts[table_count]:

                if script_count > 0:
                    if script_count % 3 != 0:
                        add_same_line(parent=parent)
                    else:
                        add_dummy(height=20, parent=parent)

                script_count += 1

                with child(name=f"child??{table[0]}??{script_info[0]}", parent=parent, width=400, height=210):
                    add_image_button(f"{table[0]}??{script_info[0]}", value=script_info[4],
                                     width=250, height=141, frame_padding=5, callback=categories[table[0]].run_script_dispatcher)
                    add_same_line(spacing=5)

                    with child(name=f"sub-child??{table[0]}??{script_info[0]}", width=50, height=150):
                        add_image_button(name=f"delete??{table[0]}??{script_info[0]}",
                                         value="icons/delete_script_button_dark.png", width=30, height=30,
                                         callback=categories[table[0]].delete_script)
                        # add_image_button(name=f"configure??{table[0]}??{script_info[0]}",
                        #                  value="icons/configure_script_button_dark.png", width=30, height=30)

                    add_text(f"{script_info[0]}", wrap=265)

            table_count += 1
            script_count = 0