import subprocess
import time

from functools import partial
from shutil import which


from edit_window import EditWindow
from info_window import InfoWindow
from run_software_window import RunSoftwareWindow
from toolbox_name_window import ToolboxNameWindow

from main import Gtk
from utils import get_output, create_toolbox_button, execute_delete_toolbox, fetch_all_toolboxes

terminal = "gnome-terminal"
terminal_exec_arg = "--"
if which(terminal) is None:
    terminal = "konsole"
    terminal_exec_arg = "-e"

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
        new_btn.set_name("new-button")
        new_btn.connect("clicked", lambda s: self.create_new_toolbox())
        new_btn.set_tooltip_text("Create a New Toolbox")

        header.pack_end(new_btn)

        self.set_titlebar(header)
    
    def render_all_toolboxes(self):
        self.clear_main_box()

        toolboxes = fetch_all_toolboxes()

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

        toolbox, version, status, tb_id = toolbox_info[0], toolbox_info[1], toolbox_info[2], toolbox_info[3]

        lbl = Gtk.Label(label=f"(f{version}) {toolbox} ")
        buttons = []

        if status.startswith("Up"):
            buttons.append(create_toolbox_button("media-stop", "Stop this Toolbox", partial(self.stop_toolbox, toolbox)))

        buttons.append(create_toolbox_button("dialog-information", "View Information about this Toolbox", partial(self.view_toolbox_info, tb_id, toolbox)))
        buttons.append(create_toolbox_button("preferences-system", "Edit this Toolbox", partial(self.edit_toolbox, toolbox)))
        buttons.append(create_toolbox_button("utilities-terminal", "Launch a Terminal in this Toolbox", partial(self.start_toolbox, toolbox)))
        buttons.append(create_toolbox_button("system-run", "Execute a Command in this Toolbox", partial(self.run_from_toolbox, toolbox)))
        buttons.append(create_toolbox_button("document-open", "Run an Application in this Toolbox", partial(self.open_application_in_toolbox, toolbox)))
        buttons.append(create_toolbox_button("system-software-install", "Install an RPM in this Toolbox", partial(self.install_into_toolbox, toolbox)))
        buttons.append(create_toolbox_button("edit-delete", "Delete this Toolbox", partial(self.confirm_delete_toolbox, toolbox)))

        tb_row.pack_start(lbl, True, True, 0)

        for btn in buttons:
            tb_row.pack_start(btn, False, False, 3)

        tb_row.show_all()
        tb_frame.add(tb_row)

        self.box.pack_start(tb_frame, False, False, 10)

        self.toolbox_rows[toolbox] = tb_row

    def start_toolbox(self, toolbox: str):
        subprocess.run([terminal, terminal_exec_arg, "toolbox", "enter", toolbox])
        GLib.timeout_add_seconds(1, self.delayed_rerender)

    def edit_toolbox(self, toolbox: str):
        d = EditWindow(self, toolbox)
        response = d.run()
        new_name = d.get_entered_name()
        if new_name and new_name != toolbox:
            subprocess.run(["podman", "rename", toolbox, new_name])

        d.destroy()

        self.render_all_toolboxes()

    def install_into_toolbox(self, toolbox: str):
        file_to_install = self.show_file_chooser()
        if file_to_install:
            subprocess.run([terminal, terminal_exec_arg, "toolbox", "run", "-c", toolbox, "sudo", "dnf", "install", "-y", file_to_install])


    def show_file_chooser(self):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file to install", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            rpm_name = dialog.get_filename()
            dialog.destroy()

            return rpm_name
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

        return None

    def run_from_toolbox(self, toolbox: str):
        dialog = RunSoftwareWindow(self, toolbox)
        response = dialog.run()
        cmd = None
        if response == Gtk.ResponseType.OK:
            cmd = dialog.get_entered_command()
            dialog.destroy()
        else:
            dialog.destroy()

        if cmd:
            subprocess.run([terminal, terminal_exec_arg, "toolbox", "run", "-c", toolbox, *cmd.split(" ")])

    def open_application_in_toolbox(self, toolbox: str):
        apps = get_output(["toolbox", "run", "-c", toolbox, "ls", "/usr/share/applications"])
        apps = apps.replace("\r\n", " ")
        apps = apps.replace("\t", " ")

        apps = [a for a in apps.split(" ") if a.endswith(".desktop")]

    def create_new_toolbox(self):
        d = ToolboxNameWindow(self)
        response = d.run()
        tb_name = None
        if response == Gtk.ResponseType.OK:
            tb_name = d.get_entered_name()

        if tb_name:
            subprocess.run(["toolbox", "create", tb_name])

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
            execute_delete_toolbox(toolbox)
            self.render_all_toolboxes()

        dialog.destroy()

    def view_toolbox_info(self, tb_id: str, toolbox: str):
        cmd = f"podman ps -a -f id={tb_id}" + ' --format={{.ID}}||{{.Image}}||{{.Status}}||{{.CreatedAt}}'
        output = get_output(cmd.split(" "))
        c_id, image, status, created_at  = output.split("||")

        info = {"container_id": c_id, "image": image, "status":status, "created_at": created_at.split('.')[0]}

        d = InfoWindow(self, toolbox, info)
        d.run()
        d.destroy()

    def stop_toolbox(self, toolbox:str):
        subprocess.run(["podman", "stop", toolbox])
        GLib.timeout_add_seconds(1, self.delayed_rerender)

    def delayed_rerender(self, *args):
        time.sleep(2)
        self.render_all_toolboxes()