import os
import gi
import subprocess

from toolbox_name_window import ToolboxNameWindow
from edit_window import EditWindow

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Toolbox GUI")
        self.set_default_size(800,640)
        self.init_header_bar()

        self.toolbox_rows = {}

        self.box = Gtk.Box(spacing=5, orientation=Gtk.Orientation.VERTICAL)
        self.box.set_homogeneous(False)

        self.render_all_toolboxes()
        self.add(self.box)
        self.box.show_all()

    def init_header_bar(self):
        header = Gtk.HeaderBar()
        header.set_title("Toolbox GUI")
        header.set_show_close_button(True)

        new_btn = Gtk.Button(label=None, image=Gtk.Image(stock=Gtk.STOCK_ADD))
        new_btn.connect("clicked", lambda s: self.create_new_toolbox())
        new_btn.set_tooltip_text("Create New Toolbox")

        header.pack_end(new_btn)

        self.set_titlebar(header)

    def render_all_toolboxes(self):
        self.clear_main_box()

        toolboxes = self.fetch_all_toolboxes()

        for tb in toolboxes:
            self.render_toolbox_row(tb)

        self.box.show_all()

    def clear_main_box(self):
        for child in self.box.get_children():
            self.box.remove(child)

    def render_toolbox_row(self, toolbox_info):
        tb_row = Gtk.Box(spacing=10)
        tb_row.set_border_width(30)
        tb_frame = Gtk.Frame()

        toolbox, version = toolbox_info[0], toolbox_info[1]

        lbl = Gtk.Label(label=f"(f{version}) {toolbox} ")
        buttons = []

        open_btn = Gtk.Button(label=None, image=Gtk.Image(stock=Gtk.STOCK_OPEN))
        open_btn.connect("clicked", lambda b: self.start_toolbox(toolbox))
        open_btn.set_tooltip_text("Launch a Terminal in this Toolbox")
        buttons.append(open_btn)

        edit_btn = Gtk.Button(label=None, image=Gtk.Image(stock=Gtk.STOCK_EDIT))
        edit_btn.connect("clicked", lambda b: self.edit_toolbox(toolbox))
        edit_btn.set_tooltip_text("Edit this Toolbox")
        buttons.append(edit_btn)

        delete_btn = Gtk.Button(label=None, image=Gtk.Image(stock=Gtk.STOCK_DELETE))
        delete_btn.connect("clicked", lambda b: self.confirm_delete_toolbox(toolbox))
        delete_btn.set_tooltip_text("Delete this Toolbox")
        buttons.append(delete_btn)

        tb_row.pack_start(lbl, True, True, 0)

        for btn in buttons:
            tb_row.pack_start(btn, False, False, 10)

        tb_row.show_all()
        tb_frame.add(tb_row)

        self.box.pack_start(tb_frame, False, False, 10)

        self.toolbox_rows[toolbox] = tb_row

    def start_toolbox(self, toolbox: str):
        # Can't get subprocess to do this properly :/
        os.system('gnome-terminal -- toolbox enter junk')

    def edit_toolbox(self, toolbox: str):
        d = EditWindow(self, toolbox)
        response = d.run()
        new_name = d.get_entered_name()
        if new_name and new_name != toolbox:
            os.system(f"podman rename {toolbox} {new_name}")

        d.destroy()

        self.render_all_toolboxes()


    def create_new_toolbox(self):
        d = ToolboxNameWindow(self)
        response = d.run()
        tb_name = d.get_entered_name()

        if tb_name:
            os.system(f"toolbox create {tb_name}")

        d.destroy()

        self.render_all_toolboxes()

    def confirm_delete_toolbox(self, toolbox: str):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Are you sure you want to delete {toolbox}?",
        )

        dialog.format_secondary_text(
            "This cannot be undone!"
        )

        response = dialog.run()

        if response == Gtk.ResponseType.YES:
            self.execute_delete_toolbox(toolbox)
            self.render_all_toolboxes()

        dialog.destroy()

    def execute_delete_toolbox(self, toolbox: str):
        os.system(f"podman stop {toolbox}")
        os.system(f"toolbox rm {toolbox}")

    def fetch_all_toolboxes(self):
        cmd = 'podman ps -a --format={{.Names}}||{{.Image}}'
        toolboxes = self.get_output(cmd.split(" "))

        toolboxes = toolboxes.split("\n")[:-1]

        retval = []

        for tb in toolboxes:
            name, image = tb.split("||")
            image_num = image.split(':')[-1]
            retval.append((name, image_num))

        return retval

    def get_output(self, cmd: str):
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        return proc.stdout.read().decode("utf-8")

win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
