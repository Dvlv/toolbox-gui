import time
import os
import subprocess
from functools import partial

from app import Gtk, Gio, GdkPixbuf

def get_output(cmd: str):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    return proc.stdout.read().decode("utf-8")

def create_toolbox_button(icon_name: str, tooltip: str, func):
    icon = Gtk.Image()
    set_icon_at_small_size(icon_name, icon)

    btn = Gtk.Button(label=None, image=icon)
    btn.connect("clicked", lambda b: func())
    btn.set_tooltip_text(tooltip)
    btn.get_style_context().add_class("tb_btn")

    return btn

def set_icon_at_small_size(icon: str, img: Gtk.Image):
    thm = Gtk.IconTheme.get_default()
    info = thm.lookup_icon(icon, 16, 0)
    set_from_pb = False
    if info:
        fn = info.get_filename()
        if fn:
            pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(fn, 16, 16, True)
            img.set_from_pixbuf(pb)
            set_from_pb = True

    if not set_from_pb:
        img.set_from_icon_name(icon, Gtk.IconSize.BUTTON)

    return img

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
    set_icon_at_small_size(icon_name, icon)

    btn = Gtk.MenuButton(label=None, image=icon, popover=popover)
    btn.set_tooltip_text(tooltip)

    btn.get_style_context().add_class("tb_btn")

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
        cmd = app_exec_cmd.split(" ")
        subprocess.run(["toolbox", "run", "-c", toolbox, *cmd])

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

def edit_exec_of_toolbox_desktop(toolbox: str, app: str):
    home = os.path.expanduser("~")
    app_path = f"{home}/.local/share/applications/{app}"
    if not os.path.exists(app_path):
        time.sleep(1)

        if not os.path.exists(app_path):
            # bail
            return

    content = []
    with open(app_path, "r") as f:
        content = f.readlines()
        for idx, line in enumerate(content):
            if line.startswith("Exec="):
                print("found exec")
                content[idx] = line.replace("Exec=", f"Exec=toolbox run -c {toolbox} ")

    with open(app_path, "w") as f:
        f.writelines(content)


def is_dark_theme():
    try:
        out = subprocess.run(
            ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
            capture_output=True)
        stdout = out.stdout.decode()
    except:
        return False

    try:
        theme = stdout.lower().strip()[1:-1]
        if '-dark' in theme.lower():
            return True
        else:
            return False
    except IndexError:
        return False
