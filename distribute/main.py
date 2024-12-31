import PyInstaller.__main__
import shutil

from jinja2 import Template
from math import ceil
from os import makedirs, mkdir, remove, system, walk
from os.path import dirname, expanduser, getsize, isdir, join, realpath
from sys import platform


# Version is a full date, not zero-padded, 'yy.mm[.dd]', e.g.: '23.12.31'.
VERSION = '24.12.1'
APP_NAME = 'Empirix Lab'
PKG_NAME = 'empirix-lab'
SETUP_FILE_LIN = PKG_NAME + "-setup_all"
SETUP_FILE_WIN = PKG_NAME + "-setup"

DIST_HOME = dirname(realpath(__file__))
if platform == "linux":
    SPEC_FPATH = join(DIST_HOME, "main.spec")
elif platform == "win32":
    SPEC_FPATH = join(DIST_HOME, "main.spec").replace("\\", "\\\\")
PROJ_HOME = dirname(DIST_HOME)
CTRL_DESC = f"{APP_NAME}\n Tools for algorithmic trading by Empirix."
DTOP_CMNT = "Tools for algorithmic trading by Empirix"
DTOP_LOGO = f"{PKG_NAME}.xpm"
TPL_FPATH = join(DIST_HOME, "tpl.jinja")


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

    # BUNDLE APP WITH PYINSTALLER
    print("Bundling with PyInstaller...")

    if platform == "linux":
        main_script_fpath = join(PROJ_HOME, "src", "main.py")
    elif platform == "win32":
        main_script_fpath = join(PROJ_HOME, "src", "main.py").replace("\\", "\\\\")

    spec_values = {
        "main_script_fpath": main_script_fpath,
        "package_name": PKG_NAME,
        "hooksconfig": {"gi": {"module-versions": {"Gtk": "4.0", "Adw": "1"}}},
    }

    datas = {
        join(PROJ_HOME, "data", "logo", DTOP_LOGO): "./logo",
        join(PROJ_HOME, "src", "gresource", f"{PKG_NAME}.gresource"): "./gresource",
    }

    # Typelibs for DEB
    if platform == "linux":
        typelibs = ["Gdk-4.0", "Gsk-4.0", "Gtk-4.0", "Graphene-1.0"]
        for typelib in typelibs:
            datas.update(add_typelib_deb(typelib))

    spec_values["datas"] = list(datas.items())

    pyinstaller_bundle(spec_values, dist_dir, work_dir, bundle_home)

    # PLATFORM SPECIFIC BELOW

    # Place for all debian source stuff: dir empirix-ui-setup_all
    deb_src_home = join(bundle_home, SETUP_FILE_LIN)

    if platform == "linux":
        # PREPARE DEBIAN SOURCE FILES
        # Re-create home dir for DEB src stuff
        try:
            shutil.rmtree(deb_src_home)
        except FileNotFoundError as e:
            print("Unable to remove dir, doesn't exist.", e, sep='--->\n')
        mkdir(deb_src_home)

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

        # BUILD .DEB PACKAGE
        print("Building deb package...")
        system(f"dpkg-deb --build {deb_src_home}")

        # Remove 'dist', 'work', .spec
        print("Cleaning up...")
        shutil.rmtree(dist_dir)
        shutil.rmtree(work_dir)
        # remove(join(bundle_home, f"{PKG_NAME}.spec"))


def pyinstaller_bundle(spec_values, dist_dir=None, work_dir=None,
                       bundle_home=None):
    """
    Bundle app with PyInstaller.
    Read more: https://pyinstaller.org/en/stable/usage.html
    https://pyinstaller.org/en/stable/runtime-information.html
    """

    # Generate .spec file
    with open(TPL_FPATH, "r") as f:
        template = Template(f.read())

    spec_content = template.render(**spec_values)

    # Save the generated .spec file
    with open(SPEC_FPATH, "w") as f_out:
        f_out.write(spec_content)

    system("pyinstaller " \
        "--noconfirm " \
        "--log-level=WARN " \
        f"--distpath={dist_dir} " \
        f"--workpath={work_dir} " \
        f"{SPEC_FPATH}"
    )


def add_typelib_deb(typelib):
    """
    Because typelibs are not added automatically by PyInstaller, this is a fix to:
    ImportError: Typelib file for namespace 'Gtk', version '4.0' not found.
    windows girepository path = "C:\\gtk\\lib\\girepository-1.0"
    """
    deb_girepository = "/usr/lib/x86_64-linux-gnu/girepository-1.0"
    win_girepository = "C:\\gtk\\lib\\girepository-1.0"
    return {join(deb_girepository, typelib + ".typelib"): "./gi_typelibs"}
    # return {f"/usr/lib/x86_64-linux-gnu/girepository-1.0/{typelib}.typelib": "./gi_typelibs"}


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
            f"Icon=/usr/local/bin/{PKG_NAME}/_internal/logo/{DTOP_LOGO}\n"
            "Terminal=false\n"
            "Type=Application\n"
            "Categories=Finance;Math;Office;\n"
            "Keywords=forex;trading;algorithms;"
        )


if __name__ == '__main__':
    main()
