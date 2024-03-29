import os
import subprocess
import time

from functools import partial
from shutil import which


from about_window import AboutWindow
from edit_window import EditWindow
from help_window import HelpWindow
from info_window import InfoWindow
from run_application_window import RunApplicationWindow
from run_software_window import RunSoftwareWindow
from toolbox_name_window import ToolboxNameWindow

from app import Gtk, GLib, Gdk
from utils import (
    FLATPAK_SPAWN,
    FLATPAK_SPAWN_ARR,
    get_output,
    get_stderr,
    create_toolbox_button,
    create_popover_button,
    execute_delete_toolbox,
    fetch_all_toolboxes,
    fetch_all_toolbox_names,
    launch_app,
    edit_exec_of_toolbox_desktop,
    is_dark_theme,
    is_flatpak,
    copy_desktop_from_toolbox_to_host,
    copy_icons_for_toolbox_desktop,
)

fp_spawn = []
if is_flatpak():
    fp_spawn = ["flatpak", "spawn", "--host"]

terminal = "gnome-terminal"
terminal_exec_arg = "--"
err = get_stderr([*FLATPAK_SPAWN_ARR, "which", "gnome-terminal"])
if err:
    terminal = "konsole"
    terminal_exec_arg = "-e"


class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Toolbox GUI")
        self.init_header_bar()

        self.toolbox_rows = {}
        self.icon_cache = {}

        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # self.box.set_homogeneous(False)

        self.scrolled.add(self.box)

        self.render_all_toolboxes()
        self.add(self.scrolled)

        d_width = 650
        calc_height = 75 * len(self.toolbox_rows)
        if calc_height > 900:
            calc_height = 900
        self.set_default_size(d_width, calc_height)

        self.apply_css()

        self.box.show_all()

    def apply_css(self):
        """
        Applies CSS and sets dark theme
        """
        css = self.get_css()
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css)
        context = Gtk.StyleContext()
        screen = Gdk.Screen.get_default()
        context.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", is_dark_theme())

    def get_css(self):
        """
        CSS for the application
        """
        primary = "white"
        primary2 = "#efefef"

        if is_dark_theme():
            primary = "#020202"
            primary2 = "#333333"

        css = f"""

        .tb_row {{
            background: {primary};
            border: none;
            padding: 20px;
        }}

        .tb_row:nth-child(even) {{
            background: {primary2};
        }}
        """

        return css.encode()

    def init_header_bar(self):
        """
        Sets Header / Title bar at top, containing add button
        """
        header = Gtk.HeaderBar()
        header.set_title("Toolbox GUI")
        header.set_show_close_button(True)

        img = Gtk.Image()
        img.set_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        new_btn = Gtk.Button(image=img)
        new_btn.set_name("new-button")
        new_btn.connect("clicked", lambda s: self.create_new_toolbox())
        new_btn.set_tooltip_text("Create a New Toolbox")
        new_btn.get_style_context().add_class("add_btn")

        menu_items = {
            "Refresh": partial(self.delayed_rerender),
            "Help": partial(self.show_help_window),
            "About": partial(self.show_about_window),
        }

        menu_btn = create_popover_button("open-menu-symbolic", "Open Menu", menu_items)

        header.pack_start(menu_btn)
        header.pack_end(new_btn)

        self.set_titlebar(header)

    def render_all_toolboxes(self):
        """
        Clears window and renders each row for each toolbox
        """
        self.clear_main_box()

        toolboxes = fetch_all_toolboxes()

        for tb in toolboxes:
            self.render_toolbox_row(tb)

        self.box.show_all()

    def clear_main_box(self):
        """
        Removes all children from the main window
        """
        for child in self.box.get_children():
            self.box.remove(child)

    def render_toolbox_row(self, toolbox_info):
        """
        Renders a row for each toolbox, containing the name and buttons
        """
        tb_row = Gtk.Box(spacing=10)
        tb_row.get_style_context().add_class("tb_row")

        tb_frame = Gtk.Frame()
        tb_frame.get_style_context().add_class("tb_frame")

        toolbox, version, status, tb_id = (
            toolbox_info[0],
            toolbox_info[1],
            toolbox_info[2],
            toolbox_info[3],
        )

        lbl = Gtk.Label(label=f"(f{version}) {toolbox} ")
        lbl.set_xalign(0)

        buttons = []

        application_menu_items = {
            "Run a Command in this Toolbox": partial(self.run_from_toolbox, toolbox),
            "Open an Application from this Toolbox": partial(
                self.open_application_in_toolbox, toolbox
            ),
            "Install an RPM in this Toolbox": partial(
                self.install_into_toolbox, toolbox
            ),
            "Update This Toolbox": partial(self.update_toolbox, toolbox),
        }

        if status.startswith("Up"):
            buttons.append(
                create_toolbox_button(
                    "media-playback-stop-symbolic",
                    "Stop this Toolbox",
                    partial(self.stop_toolbox, toolbox),
                )
            )

        buttons.append(
            create_toolbox_button(
                "dialog-information-symbolic",
                "View Information about this Toolbox",
                partial(self.view_toolbox_info, tb_id, toolbox),
            )
        )
        buttons.append(
            create_toolbox_button(
                "preferences-system-symbolic",
                "Edit this Toolbox",
                partial(self.edit_toolbox, toolbox),
            )
        )
        buttons.append(
            create_toolbox_button(
                "utilities-terminal-symbolic",
                "Launch a Terminal in this Toolbox",
                partial(self.start_toolbox, toolbox),
            )
        )
        buttons.append(
            create_popover_button(
                "system-software-install-symbolic",
                "Application Options",
                application_menu_items,
            )
        )
        buttons.append(
            create_toolbox_button(
                "user-trash-symbolic",
                "Delete this Toolbox",
                partial(self.confirm_delete_toolbox, toolbox),
            )
        )

        tb_row.pack_start(lbl, True, True, 0)

        for btn in buttons:
            tb_row.pack_start(btn, False, False, 3)

        tb_row.show_all()
        # tb_frame.add(tb_row)

        self.box.pack_start(tb_row, False, False, 0)

        self.toolbox_rows[toolbox] = tb_row

    def start_toolbox(self, toolbox: str):
        """
        Opens a terminal in a toolbox
        """
        subprocess.Popen(
            [
                *FLATPAK_SPAWN_ARR,
                terminal,
                terminal_exec_arg,
                "toolbox",
                "enter",
                toolbox,
            ]
        )
        GLib.timeout_add_seconds(1, self.delayed_rerender)

    def edit_toolbox(self, toolbox: str):
        """
        Opens popup to rename a toolbox
        """
        d = EditWindow(self, toolbox)
        response = d.run()
        new_name = d.get_entered_name()
        if new_name and new_name != toolbox:
            subprocess.run([*FLATPAK_SPAWN_ARR, "podman", "rename", toolbox, new_name])

        d.destroy()

        self.render_all_toolboxes()

    def install_into_toolbox(self, toolbox: str, *args):
        """
        Passes typed information into ``dnf install`` inside the toolbox
        """
        file_to_install = self.show_file_chooser()
        if file_to_install:
            subprocess.run(
                [
                    *FLATPAK_SPAWN_ARR,
                    terminal,
                    terminal_exec_arg,
                    "toolbox",
                    "run",
                    "-c",
                    toolbox,
                    "sudo",
                    "dnf",
                    "install",
                    "-y",
                    file_to_install,
                ]
            )

    def update_toolbox(self, toolbox, *args):
        """
        Runs ``dnf update`` inside toolbox
        """
        subprocess.Popen(
            [
                *FLATPAK_SPAWN_ARR,
                terminal,
                terminal_exec_arg,
                "toolbox",
                "run",
                "-c",
                toolbox,
                "sudo",
                "dnf",
                "update",
                "-y",
            ]
        )

    def run_from_toolbox(self, toolbox: str, *args):
        """
        Runs command inside a toolbox
        """
        dialog = RunSoftwareWindow(self, toolbox)
        response = dialog.run()
        cmd = None
        if response == Gtk.ResponseType.OK:
            cmd = dialog.get_entered_command()
            dialog.destroy()
        else:
            dialog.destroy()

        if cmd:
            subprocess.Popen(
                [
                    *FLATPAK_SPAWN_ARR,
                    terminal,
                    terminal_exec_arg,
                    "toolbox",
                    "run",
                    "-c",
                    toolbox,
                    *cmd.split(" "),
                ]
            )

    def open_application_in_toolbox(self, toolbox: str, *args):
        """
        Opens a dialog containing the applications inside the toolbox,
        then runs one if selected
        """
        apps = get_output(
            [
                *FLATPAK_SPAWN_ARR,
                "toolbox",
                "run",
                "-c",
                toolbox,
                "ls",
                "/usr/share/applications",
            ]
        )
        apps = apps.replace("\r\n", " ")
        apps = apps.replace("\t", " ")

        apps = [a for a in apps.split(" ") if a.endswith(".desktop")]

        d = RunApplicationWindow(self, toolbox, apps)
        response = d.run()
        if response == Gtk.ResponseType.CANCEL:
            d.destroy()

        chosen_app = d.get_chosen_app()
        d.destroy()

        if chosen_app:
            GLib.timeout_add_seconds(0.5, launch_app, toolbox, chosen_app)

    def create_new_toolbox(self):
        """
        Shows a dialog to fetch a name, then makes a toolbox with that name.
        """
        all_toolboxes = fetch_all_toolbox_names()

        d = ToolboxNameWindow(self, all_toolboxes)
        response = d.run()
        tb_name = None
        if response == Gtk.ResponseType.OK:
            tb_name = d.get_entered_name()

            while tb_name in all_toolboxes:
                d.show_already_exists_message()
                tb_name = None
                response = d.run()

                if response == Gtk.ResponseType.OK:
                    tb_name = d.get_entered_name()

            if tb_name:
                subprocess.run([*FLATPAK_SPAWN_ARR, "toolbox", "create", tb_name, "-y"])

                current_w, current_h = self.get_size()
                min_h = 75 * (len(self.toolbox_rows) + 1)
                if current_h < min_h and current_h < 900:
                    self.resize(current_w, min_h)

            self.render_all_toolboxes()

        d.destroy()

    def confirm_delete_toolbox(self, toolbox: str):
        """
        Shows a dialog to confirm deleting of a toolbox
        Then deletes it if confirmed
        """
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Are you sure you want to delete {toolbox}?",
        )

        dialog.format_secondary_text("This cannot be undone!")

        response = dialog.run()

        if response == Gtk.ResponseType.YES:
            execute_delete_toolbox(toolbox)
            self.render_all_toolboxes()

        dialog.destroy()

    def view_toolbox_info(self, tb_id: str, toolbox: str):
        """
        Shows dialog with information about a toolbox
        """
        cmd = (
            f"{FLATPAK_SPAWN}podman ps -a -f id={tb_id}"
            + " --format={{.ID}}||{{.Image}}||{{.Status}}||{{.CreatedAt}}"
        )
        output = get_output(cmd.split(" "))
        c_id, image, status, created_at = output.split("||")

        info = {
            "container_id": c_id,
            "image": image,
            "status": status,
            "created_at": created_at.split(".")[0],
        }

        d = InfoWindow(self, toolbox, info)
        d.run()
        d.destroy()

    def stop_toolbox(self, toolbox: str):
        """
        Runs podman stop
        """
        subprocess.run([*FLATPAK_SPAWN_ARR, "podman", "stop", toolbox])
        GLib.timeout_add_seconds(1, self.delayed_rerender)

    def copy_desktop_to_host(self, toolbox: str, app: str):
        """
        Kicks off copying of .desktop file to the host
        """
        copy_desktop_from_toolbox_to_host(toolbox, app)
        GLib.timeout_add_seconds(0.5, edit_exec_of_toolbox_desktop, toolbox, app)
        GLib.timeout_add_seconds(0.75, copy_icons_for_toolbox_desktop, toolbox, app)

    def show_file_chooser(self):
        """
        Shows a file chooser dialog to pick an RPM file to install
        """
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file to install",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
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

    def show_help_window(self, *args):
        w = HelpWindow(self)
        w.run()
        w.destroy()

    def show_about_window(self, *args):
        w = AboutWindow(self)
        w.run()
        w.destroy()

    def delayed_rerender(self, *args):
        """
        Used to rerender the rows after a delay
        """

        self.render_all_toolboxes()
