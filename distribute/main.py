import PyInstaller.__main__
import shutil

from math import ceil
from os import makedirs, mkdir, remove, system, walk
from os.path import dirname, expanduser, getsize, isdir, join, realpath


# Version is a full date, not zero-padded, 'yy.mm[.dd]', e.g.: '23.12.31'.
VERSION = '24.12.1'
APP_NAME = 'Empirix Lab'
PKG_NAME = 'empirix-lab'
SETUP_FILE_LIN = PKG_NAME + "-setup_all"
SETUP_FILE_WIN = PKG_NAME + "-setup"

PROJ_HOME = dirname(dirname(realpath(__file__)))
CTRL_DESC = "Empirix UI\n Tools for algorithmic trading by Empirix."
DTOP_CMNT = "Tools for algorithmic trading by Empirix"
DTOP_LOGO = "logo_empirix.xpm"


def main():
    # Start with checking/making home dir for empirix packaging process
    bundle_home = join(expanduser("~"), "Documents", "Bundles",
                       f"{PKG_NAME}_{VERSION}")
    if not isdir(bundle_home):
        makedirs(bundle_home)

    # Home for Pyinstaller's files: name is 'dist' like default
    dist_dir = join(bundle_home, "dist")

    # Pyinstaller's work dir
    work_dir = join(bundle_home, "work")

    # Bundled package directory, like for real: dist/empirix-ui
    bundled_pkg_dir = join(dist_dir, PKG_NAME)

    # Place for all debian source stuff: dir empirix-ui-setup_all
    deb_src_home = join(bundle_home, SETUP_FILE_LIN)

    # BUNDLE APP WITH PYINSTALLER
    print("Bundling with PyInstaller...")
    pyinstaller_bundle(dist_dir, work_dir, bundle_home)

    # PREPARE DEBIAN SOURCE FILES
    # Re-create home dir for DEB src stuff
    try:
        shutil.rmtree(deb_src_home)
    except FileNotFoundError as e:
        print("Unable to remove dir, doesn't exist.", e, sep='--->\n')
    mkdir(deb_src_home)

    return

    # Create 'control' file
    # Read more: https://www.debian.org/doc/debian-policy/ch-controlfields.html
    print("Creating control file...")
    deb_ctrl_path = join(deb_src_home, "DEBIAN")
    mkdir(deb_ctrl_path)

    create_control_file(deb_ctrl_path, bundled_pkg_dir)

    # Re-create usr/local/bin tree; distro in deb tree
    dist_in_deb_tree = join(deb_src_home, "usr", "local", "bin")
    makedirs(dist_in_deb_tree)

    # Re-create usr/share/applications tree - for .desktop item
    apps_dir = join(deb_src_home, "usr", "share", "applications")
    makedirs(apps_dir)

    # Create .desktop item
    print("Creating desktop item...")
    create_desktop_item(apps_dir)

    # Move 'dist' contents to 'empirix-trader-setup_all/usr/local/bin/...'
    print("Moving dist contents to dist in deb tree...")
    shutil.move(bundled_pkg_dir, dist_in_deb_tree)

    # Remove 'dist', 'work', .spec
    print("Cleaning up...")
    shutil.rmtree(dist_dir)
    shutil.rmtree(work_dir)
    remove(join(bundle_home, f"{PKG_NAME}.spec"))

    # BUILD .DEB PACKAGE
    print("Building deb package...")
    system(f"dpkg-deb --build {deb_src_home}")


def pyinstaller_bundle(dist_dir=None, work_dir=None, bundle_home=None):
    """
    Bundle app with PyInstaller.
    Read more: https://pyinstaller.org/en/stable/usage.html
    https://pyinstaller.org/en/stable/runtime-information.html
    """

    PyInstaller.__main__.run(
        [
            "--onedir",
            "--noconfirm",
            "--log-level=WARN",
            f"--distpath={dist_dir}",
            f"--workpath={work_dir}",
            f"--specpath={bundle_home}",

            # Below adds data to "_internal" folder as root
            # f"--add-data={join(PROJ_HOME, "data", "img")}:img",
            # f"--hidden-import=src.my_vars.py",
            # "--debug=all",
            # "--paths=/home/rsm/Documents/MyProjects/empirix-lab/src",
            f"--add-data={join(PROJ_HOME, "src", "gresource",
                               f"{PKG_NAME}.gresource")}:./gresource",
            f"--add-data={add_typelib("Gdk-4.0")}",
            f"--add-data={add_typelib("Gsk-4.0")}",
            f"--add-data={add_typelib("Gtk-4.0")}",
            f"--add-data={add_typelib("Graphene-1.0")}",

            f"--name={PKG_NAME}",
            join(PROJ_HOME, "src", "main.py")  # what script to bundle
        ]
    )

    # PyInstaller.__main__.run(
    #     [
    #         "--onedir",
    #         "--noconfirm",
    #         "--log-level=WARN",
    #         f"--distpath={dist_dir}",
    #         f"--workpath={work_dir}",
    #         f"--specpath={bundle_home}",
    #
    #         # Below adds data to "_internal" folder as root
    #         # f"--add-data={join(PROJ_HOME, "data", "img")}:img",
    #         # f"--hidden-import=src.my_vars.py",
    #         # "--debug=all",
    #         # "--paths=/home/rsm/Documents/MyProjects/empirix-lab/src",
    #         # f"--add-data={join(PROJ_HOME, "src", "widget",
    #         #                    f"{PKG_NAME}.gresource")}:.",
    #         f"--add-data={add_typelib("Gdk-4.0")}",
    #         f"--add-data={add_typelib("Gsk-4.0")}",
    #         f"--add-data={add_typelib("Gtk-4.0")}",
    #         f"--add-data={add_typelib("Graphene-1.0")}",
    #
    #         f"--name={PKG_NAME}",
    #         join(PROJ_HOME, "src", "main2.py")  # what script to bundle
    #     ]
    # )


def add_typelib(typelib):
    """
    This is a fix to this error:
    ImportError: Typelib file for namespace 'Gtk', version '4.0' not found.
    Because typelibs are not added automatically by PyInstaller.
    """

    return f"/usr/lib/x86_64-linux-gnu/girepository-1.0/{typelib}.typelib:gi_typelibs"


def create_control_file(deb_ctrl_path, bundled_pkg_dir):
    with open(join(deb_ctrl_path, 'control'), 'w') as f_obj:
        f_obj.write(
            f"Package: {PKG_NAME}\n"
            f"Version: {VERSION}\n"
            "Section: misc\n"
            "Priority: optional\n"
            "Architecture: all\n"
            f"Installed-Size: {get_size(bundled_pkg_dir)}\n"
            "Maintainer: Raman Maładziašyn <maladziashyn@gmail.com>\n"
            f"Description: {CTRL_DESC}\n"
            "Homepage: https://empirix.ru/\n"
        )


def get_size(dir_path):
    """
    Return size of all directory contents in kilobytes.
    Symlinks not followed.
    """

    total_size = 0
    for root, dirs, files in walk(dir_path):
        for f in files:
            fp = join(root, f)
            total_size += getsize(fp)
    return ceil(total_size / 1024)


def create_desktop_item(apps_dir):
    # Create .desktop item
    # Read more: https://specifications.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html#example

    with open(join(apps_dir, f"{PKG_NAME}.desktop"), "w") as f_obj:
        f_obj.write(
            "[Desktop Entry]\n"
            "Encoding=UTF-8\n"
            "Version=1.0\n"
            f"Name={APP_NAME}\n"
            f"Comment={DTOP_CMNT}\n"
            f"Exec=/usr/local/bin/{PKG_NAME}/{PKG_NAME}\n"
            f"TryExec=/usr/local/bin/{PKG_NAME}/{PKG_NAME}\n"
            f"Icon=/usr/local/bin/{PKG_NAME}/_internal/img/{DTOP_LOGO}\n"
            "Terminal=false\n"
            "Type=Application\n"
            "Categories=Finance;Math;Office;\n"
            "Keywords=forex;trading;algorithms;"
        )


if __name__ == '__main__':
    main()
