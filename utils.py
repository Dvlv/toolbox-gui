import os
import subprocess
from functools import partial

from main import Gtk, Gio

def get_output(cmd: str):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    return proc.stdout.read().decode("utf-8")

def create_toolbox_button(icon_name: str, tooltip: str, func):
    icon = Gtk.Image()
    icon.set_from_icon_name(icon_name, Gtk.IconSize.BUTTON)

    btn = Gtk.Button(label=None, image=icon)
    btn.connect("clicked", lambda b: func())
    btn.set_tooltip_text(tooltip)

    return btn

def create_popover_button(icon_name: str, tooltip: str, menu_items: dict):
    popover = Gtk.Popover()
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

    for text, func in menu_items.items():
        b = Gtk.ModelButton(label=text)
        b.connect("clicked", partial(func))

        vbox.pack_start(b, False, True, 10)

    vbox.show_all()
    popover.add(vbox)
    popover.set_position(Gtk.PositionType.BOTTOM)

    icon = Gtk.Image()
    icon.set_from_icon_name(icon_name, Gtk.IconSize.BUTTON)

    btn = Gtk.MenuButton(label=None, image=icon, popover=popover)
    btn.set_tooltip_text(tooltip)

    return btn

def execute_delete_toolbox(toolbox: str):
    subprocess.run(["podman", "stop", toolbox])
    subprocess.run(["toolbox", "rm", toolbox])

def fetch_all_toolboxes():
    cmd = 'podman ps -a --format={{.Names}}||{{.Image}}||{{.Status}}||{{.ID}}'
    toolboxes = get_output(cmd.split(" "))

    toolboxes = toolboxes.split("\n")[:-1]

    retval = []

    for tb in toolboxes:
        name, image, status, tb_id = tb.split("||")
        image_num = image.split(':')[-1]
        retval.append((name, image_num, status, tb_id))

    return retval

def launch_app(toolbox: str, app: str):
    # gtk-launch doesnt work from toolbox run :/
    app_exec_cmd = get_exec_from_desktop(toolbox, app)
    if app_exec_cmd:
        subprocess.run(["toolbox", "run", "-c", toolbox, app_exec_cmd])

def get_exec_from_desktop(toolbox: str, app: str):
    contents = get_output(f"toolbox run -c {toolbox} cat /usr/share/applications/{app}".split(" "))
    exec_cmd = None
    for line in contents.split("\n"):
        if line.startswith("Exec="):
            exec_cmd = line.replace("Exec=", "").strip()
            break

    return exec_cmd


def get_icon_from_desktop(toolbox: str, app: str):
    contents = get_output(f"toolbox run -c {toolbox} cat /usr/share/applications/{app}".split(" "))
    icon = None
    for line in contents.split("\n"):
        if line.startswith("Icon="):
            icon = line.replace("Icon=", "").strip()
            break

    return icon