from dearpygui.core import *
from dearpygui.simple import *
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
import os
import threading
from CategoryHandlerAPI import  *
from DatabaseHandlerAPI import *

with window("Main Window"):
    # Main Window styling
    set_theme(theme="Grey")
    set_main_window_title("MultiPy")
    set_main_window_pos(x=0, y=0)
    set_main_window_size(width=1370, height=740)
    add_additional_font("fonts/glacial_font.otf", 21)

    set_style_window_border_size(0.0)
    set_style_child_border_size(0.0)
    set_style_window_title_align(0.5, 0.5)
    set_style_window_rounding(5.0)
    set_style_frame_rounding(5.0)

    set_theme_item(mvGuiCol_TextDisabled, 143, 143, 143, 255)
    set_theme_item(mvGuiCol_Separator, 127, 127, 127, 255)

    with menu_bar("Main menu bar"):
        with menu("File"):
            add_menu_item("Save dashboard", callback=save_tool)
            add_menu_item("Open dashboard", callback=open_tool)

with window(name="Add scripts button", no_title_bar=True, no_resize=True, no_close=True, no_collapse=True, no_move=True,
            x_pos=1070, y_pos=630, autosize=True):

    add_image_button(name="add_category", value="icons/add_category_button_dark.png", width=250, height=36)

    with popup(popupparent="add_category", name="Add new category", mousebutton=mvMouseButton_Left, modal=True):
        set_item_style_var(item="Add new category", style=mvGuiStyleVar_WindowPadding, value=[10, 10])
        add_dummy(name="addCategoryDummy01", height=10)
        add_input_text(name="category_name", label="    Enter category name", hint="Category name", width=250, on_enter=True, callback=add_category, callback_data=lambda: add_category)
        add_dummy(name="addCategoryDummy02", height=20)
        add_button("Add##AddCategory", width=220, callback=add_category, callback_data=lambda: add_category)
        add_same_line(spacing=5.0)
        add_button("Cancel##AddCategory", width=220, callback=close_popups)

with window(name="Tools", no_title_bar=True, no_resize=True, no_close=True, no_collapse=True, no_move=True,
            x_pos=80, y_pos=630, autosize=True):

    add_image_button(name="view_button", value="icons/view_button_dark.png", width=36, height=36, tip="Switch to view-only mode", show=False, callback=show_edit_mode_switcher)
    add_same_line(spacing=10, name="tools_line")

with window(name="Loaded scripts", no_title_bar=True, no_resize=True, no_close=True, no_collapse=True, no_move=True,
            x_pos=80, y_pos=40, width=1260, height=590):

    with child("Instructions", height=200):
        add_dummy(name="loadedScriptsDummy01", height=15)
        add_text("INSTRUCTIONS:")
        add_dummy(name="loadedScriptsDummy01", height=20)
        add_text(">    Click on \"Add new category\" button to get started.")
        add_text(">    Enter a name and click \"Add\".")
        add_text(">    Click on \"Add new python script\", and enter all the details as required.")
        add_text(">    Click on the thumbnails to run individual scripts or click on \"Run all\" to run all the scripts in that category.")
        add_dummy(name="dummy03", height=20)
        #add_text("You can find more information in the help menu.")

def main():
    create_database()
    # Start app
    start_dearpygui(primary_window="Main Window")

if __name__ == '__main__':
    main()
