import shutil

from jinja2 import Template
from math import ceil
from os import makedirs, mkdir, system, walk
from os.path import dirname, expanduser, getsize, isdir, join, realpath
from sys import platform, path

project_home_dir = dirname(dirname(realpath(__file__)))
if project_home_dir not in path:
    path.insert(0, project_home_dir)

import config as c


IS_CONSOLE = False


def main():
    print(f"Packaging \"{c.APP_NAME}\"...")

    # Check gresource recompile flag
    with open(join(c.PROJECT_HOME_DIR, "config.py"), "r") as f:
        config_content = f.read()
    if "GRESOURCE_RECOMPILE = True" in config_content:
        print("[BLOCKER] config.py: set GRESOURCE_RECOMPILE to False.")
        return

    # Start with checking/making home dir for packaging process
    bundles_home = join(expanduser("~"), "Documents", "Bundles")
    versioned_dirname = f"{c.PACKAGE_NAME}_{c.VERSION}"  # empirix-lab_v25.1

    if not isdir(bundles_home):
        makedirs(bundles_home)

    # Remove existing version package
    target_dirpath = join(bundles_home, versioned_dirname)
    if isdir(target_dirpath):
        print("Removing existing bundle...")
        shutil.rmtree(target_dirpath)

    # Home for Pyinstaller's files: name is 'dist' like default
    dist_dir = join(bundles_home, "dist")
    work_dir = join(bundles_home, "work")

    main_script_fpath = join(c.PROJECT_HOME_DIR, "main.py")
    if platform == "win32":
        main_script_fpath = main_script_fpath.replace("\\", "\\\\")

    spec_values = {
        "main_script_fpath": main_script_fpath,
        "executive_name": c.PACKAGE_NAME,
        "package_name": c.PACKAGE_NAME,
        "hooksconfig": {"gi": {"module-versions": {"Gtk": "4.0", "Adw": "1"}}},
        "is_console": IS_CONSOLE,
    }
    datas = {
        join(c.PROJECT_HOME_DIR, "gresource",
             f"{c.PACKAGE_NAME}.gresource"): "./gresource",
    }
    if platform == "linux":
        # Add XPM logo for Linux desktop-item
        datas.update(
            {
                join(c.PROJECT_HOME_DIR, "_distribution", "logo",
                     c.DESKTOP_ITEM_LOGO): "./logo",
            }
        )
        # Typelibs for DEB
        typelibs = ["Gdk-4.0", "Gsk-4.0", "Gtk-4.0", "Graphene-1.0"]
        for typelib in typelibs:
            datas.update(add_typelib(typelib))

    spec_values["datas"] = list(datas.items())

    # BUNDLE
    pyinstaller_bundle(spec_values, dist_dir, work_dir)
    
    if platform == "win32":
        # Recreate target dirpath
        if not isdir(target_dirpath):
            makedirs(target_dirpath)
        # Move dist data to bundles_home
        shutil.move(join(dist_dir, c.PACKAGE_NAME), target_dirpath)
        # shutil.move(dist_dir, target_dirpath)
        print("Zipping...")
        shutil.make_archive(target_dirpath, "zip", target_dirpath)
        # Move zip into versioned dir
        shutil.move(target_dirpath + ".zip", target_dirpath)
    elif platform == "linux":
        # Place for all debian source stuff: dir empirix-ui-setup_all
        deb_src_home = join(target_dirpath, c.SETUP_FILE_LINUX)

        # Re-create home dir for DEB src stuff
        try:
            shutil.rmtree(deb_src_home)
        except FileNotFoundError as e:
            print(f"Unable to remove directory, doesn't exist.", e, sep='--->\n')
        makedirs(deb_src_home)

        # PREPARE DEBIAN SOURCE FILES
        # Bundled package directory, like for real: dist/empirix-ui
        bundled_pkg_dir = join(dist_dir, c.PACKAGE_NAME)


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

    # Remove 'dist', 'work'
    print("Cleaning up...")
    shutil.rmtree(dist_dir)
    shutil.rmtree(work_dir)

    print("Packaging complete.")


def pyinstaller_bundle(spec_values, dist_dir, work_dir):
    """
    Bundle app with PyInstaller.
    Read more: https://pyinstaller.org/en/stable/usage.html
    https://pyinstaller.org/en/stable/runtime-information.html
    """
    
    print("Running PyInstaller...")
    
    # Generate .spec file
    with open(join(project_home_dir, "_distribution", "tpl.jinja"), "r") as f:
        template = Template(f.read())

    spec_content = template.render(**spec_values)

    # Save the generated .spec file
    spec_file = join(project_home_dir, "_distribution", "main.spec")
    with open(spec_file, "w") as f_out:
        f_out.write(spec_content)

    system("pyinstaller " \
        "--noconfirm " \
        "--log-level=WARN " \
        f"--distpath={dist_dir} " \
        f"--workpath={work_dir} " \
        f"{spec_file}"
    )


def add_typelib(typelib):
    """
    Because typelibs are not added automatically by PyInstaller, this is a fix to:
    ImportError: Typelib file for namespace 'Gtk', version '4.0' not found.
    windows girepository path = "C:\\gtk\\lib\\girepository-1.0"
    """

    girepository = "/usr/lib/x86_64-linux-gnu/girepository-1.0"
    return {join(girepository, typelib + ".typelib"): "./gi_typelibs"}



def create_control_file(deb_ctrl_path, bundled_pkg_dir):
    with open(join(deb_ctrl_path, 'control'), 'w') as f_obj:
        f_obj.write(
            f"Package: {c.PACKAGE_NAME}\n"
            f"Version: {c.VERSION}\n"
            "Section: misc\n"
            "Priority: optional\n"
            "Architecture: all\n"
            f"Installed-Size: {get_size(bundled_pkg_dir)}\n"
            f"Maintainer: {c.MAINTAINER}\n"
            f"Description: {c.CONTROL_FILE_DESC}\n"
            f"Homepage: {c.WEB_HOMEPAGE}\n"
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

    with open(join(apps_dir, f"{c.PACKAGE_NAME}.desktop"), "w") as f_obj:
        f_obj.write(
            "[Desktop Entry]\n"
            "Encoding=UTF-8\n"
            "Version=1.0\n"
            f"Name={c.APP_NAME}\n"
            f"Comment={c.DESKTOP_ITEM_COMMENT}\n"
            f"Exec=/usr/local/bin/{c.PACKAGE_NAME}/{c.PACKAGE_NAME}\n"
            f"TryExec=/usr/local/bin/{c.PACKAGE_NAME}/{c.PACKAGE_NAME}\n"
            f"Icon=/usr/local/bin/{c.PACKAGE_NAME}/_internal/logo/{c.DESKTOP_ITEM_LOGO}\n"
            f"Terminal={"true" if IS_CONSOLE else "false"}\n"
            "Type=Application\n"
            "Categories=Finance;Math;Office;\n"
            "Keywords=forex;trading;algorithms;empirix;"
        )


if __name__ == '__main__':
    main()
