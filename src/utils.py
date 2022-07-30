import time
import os
import subprocess
from functools import partial

from app import Gtk, Gio, GdkPixbuf


def get_output(cmd: list):
    """
    Runs command and returns stdout
    """
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    return proc.stdout.read().decode("utf-8")


def get_stderr(cmd: list):
    """
    Runs command and returns stderr
    """
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)

    return proc.stderr.read().decode("utf-8")


def create_toolbox_button(icon_name: str, tooltip: str, func):
    """
    Makes a button containing an icon which is bound to
    the provided func
    """
    icon = Gtk.Image()
    set_icon_at_small_size(icon_name, icon)

    btn = Gtk.Button(label=None, image=icon)
    btn.connect("clicked", lambda b: func())
    btn.set_tooltip_text(tooltip)
    btn.get_style_context().add_class("tb_btn")

    return btn


def set_icon_at_small_size(icon: str, img: Gtk.Image):
    """
    Uses pixbuf to set an icon at 16x16
    """
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
    """
    Makes a popover button containing an icon and the provided menu items
    """
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
    """
    Stops and removes toolbox
    """
    subprocess.run([*FLATPAK_SPAWN_ARR, "podman", "stop", toolbox])
    subprocess.run([*FLATPAK_SPAWN_ARR, "toolbox", "rm", toolbox])


def fetch_all_toolboxes():
    """
    Returns info about all toolboxes
    """
    cmd = f"{FLATPAK_SPAWN}podman ps -a --format=" + "{{.Names}}||{{.Image}}||{{.Status}}||{{.ID}}"

    toolboxes = get_output(cmd.split(" "))

    toolboxes = toolboxes.split("\n")[:-1]

    retval = []

    for tb in toolboxes:
        name, image, status, tb_id = tb.split("||")
        image_num = image.split(":")[-1]
        retval.append((name, image_num, status, tb_id))

    return retval


def fetch_all_toolbox_names():
    """
    Returns names of all toolboxes
    """
    cmd = f"{FLATPAK_SPAWN}podman ps -a --format=" + "{{.Names}}"
    toolboxes = get_output(cmd.split(" "))

    toolboxes = toolboxes.split("\n")[:-1]

    retval = []

    for tb in toolboxes:
        retval.append(tb)

    return retval


def launch_app(toolbox: str, app: str):
    """
    Opens provided app in the toolbox
    """
    # gtk-launch doesnt work from toolbox run :/
    app_exec_cmd = get_exec_from_desktop(toolbox, app)
    if app_exec_cmd:
        cmd = app_exec_cmd.split(" ")
        subprocess.Popen([*FLATPAK_SPAWN_ARR, "toolbox", "run", "-c", toolbox, *cmd])


def get_exec_from_desktop(toolbox: str, app: str):
    """
    Returns the Exec= line from a .desktop file
    """
    contents = get_output(
        f"{FLATPAK_SPAWN}toolbox run -c {toolbox} cat /usr/share/applications/{app}".split(" ")
    )
    exec_cmd = None
    for line in contents.split("\n"):
        if line.startswith("Exec="):
            exec_cmd = line.replace("Exec=", "").strip()
            break

    return exec_cmd


def get_icon_from_desktop(toolbox: str, app: str):
    """
    Returns the Icon= line from a .desktop file
    """
    contents = get_output(
        f"{FLATPAK_SPAWN}toolbox run -c {toolbox} cat /usr/share/applications/{app}".split(" ")
    )
    icon = None
    for line in contents.split("\n"):
        if line.startswith("Icon="):
            icon = line.replace("Icon=", "").strip()
            break

    return icon


def copy_desktop_from_toolbox_to_host(toolbox: str, app: str):
    """
    Copies .desktop file from toolbox into host
    """
    home = os.path.expanduser("~")
    local_folder = f"{home}/.local/share/applications"
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    subprocess.run(
        [
            *FLATPAK_SPAWN_ARR,
            "toolbox",
            "run",
            "-c",
            toolbox,
            "cp",
            f"/usr/share/applications/{app}",
            f"{home}/.local/share/applications/{app}",
        ]
    )


def edit_exec_of_toolbox_desktop(toolbox: str, app: str):
    """
    Replaces Exec= line from a .desktop file to include the toolbox run
    """
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


def copy_icons_for_toolbox_desktop(toolbox: str, app: str):
    """
    Searches for icons matching the app name inside the toolbox and
    copies them to ~/.icons on the host
    """
    home = os.path.expanduser("~")
    app_path = f"{home}/.local/share/applications/{app}"
    if not os.path.exists(app_path):
        time.sleep(1)

        if not os.path.exists(app_path):
            # bail
            return

    content = []
    icon_name = ""
    with open(app_path, "r") as f:
        content = f.readlines()
        for line in content:
            if line.startswith("Icon="):
                icon_name = line[5:]

    if not icon_name:
        return

    if icon_name.endswith(".png") or icon_name.endswith(".svg"):
        # is a file rather than a name
        # try copying it over?
        return

    icon_name = icon_name.strip()

    if not os.path.exists(f"{home}/.icons"):
        os.makedirs(f"{home}/.icons")

    script_dir = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "echo_into_file.sh"
    )

    cmd = [*FLATPAK_SPAWN_ARR, "toolbox", "run", "-c", toolbox, script_dir, icon_name]
    subprocess.run(cmd)

    if not os.path.exists(f"{home}/.icons/tb_gui_icon_files.txt"):
        # bail
        return

    with open(f"{home}/.icons/tb_gui_icon_files.txt", "r") as f:
        for line in f:
            print(line)
            line = line.strip()
            dest_path = line.replace("/usr/share/icons", f"{home}/.icons")

            if not os.path.exists(os.path.dirname(dest_path)):
                os.makedirs(os.path.dirname(dest_path))

            subprocess.run(
                [
                    *FLATPAK_SPAWN_ARR,
                    "toolbox",
                    "run",
                    "-c",
                    toolbox,
                    "cp",
                    line,
                    dest_path,
                ]
            )

    os.remove(f"{home}/.icons/tb_gui_icon_files.txt")


def is_dark_theme():
    """
    Tries to find if the user has set themselves to dark mode
    """
    try:
        out = subprocess.run(
            [*FLATPAK_SPAWN_ARR, "gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            capture_output=True,
        )
        stdout = out.stdout.decode()
    except:
        return False

    try:
        theme = stdout.lower().strip()[1:-1]
        if "-dark" in theme.lower():
            return True
        else:
            return False
    except IndexError:
        return False

def is_flatpak():
    f = os.getenv("FLATPAK_ID")
    if f:
        return True
    return False

FLATPAK_SPAWN = "flatpak-spawn --host " if is_flatpak() else ""
FLATPAK_SPAWN_ARR = ["flatpak-spawn", "--host"] if is_flatpak() else []