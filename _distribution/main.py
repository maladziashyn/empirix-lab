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


IS_CONSOLE = True


def main():
    print(f"Packaging \"{c.APP_NAME}\"...")

    # Start with checking/making home dir for packaging process
    bundles_home = join(expanduser("~"), "Documents", "Bundles")

    if not isdir(bundles_home):
        makedirs(bundles_home)

    # Remove existing version package
    target_dir = join(bundles_home, f"{c.PACKAGE_NAME}_{c.VERSION}",
                      c.PACKAGE_NAME)
    if isdir(target_dir):
        print("Removing existing bundle...")
        shutil.rmtree(target_dir)

    # Home for Pyinstaller's files: name is 'dist' like default
    dist_dir = join(bundles_home, "dist")
    work_dir = join(bundles_home, "work")

    main_script_fpath = join(c.PROJECT_HOME_DIR, "main.py")
    if platform == "win32":
        main_script_fpath = main_script_fpath.replace("\\", "\\\\")

    spec_values = {
        "main_script_fpath": main_script_fpath,
        "executive_name": c.PACKAGE_NAME,
        "package_name": f"{c.PACKAGE_NAME}_{c.VERSION}",
        "hooksconfig": {"gi": {"module-versions": {"Gtk": "4.0", "Adw": "1"}}},
        "is_console": IS_CONSOLE,
    }
    datas = {
        join(c.PROJECT_HOME_DIR, "gresource",
             f"{c.PACKAGE_NAME}.gresource"): "./gresource",
    }
    # Add XPM logo for Linux
    if platform == "linux":
        datas.update(
            {
                join(c.PROJECT_HOME_DIR, "_distribution", "logo",
                     c.DESKTOP_ITEM_LOGO): "./logo",
            }
        )
    spec_values["datas"] = list(datas.items())
    pyinstaller_bundle(spec_values, dist_dir, work_dir)




    # # Bundled package directory, like for real: dist/empirix-ui
    # bundled_pkg_dir = join(dist_dir, PKG_NAME)
    #
    # compile_gresource_for_bundle()
    #
    # # Change IS_DEV to False
    # init_gresource_py = join(
    #     dirname(dirname(realpath(__file__))),
    #     "src",
    #     "gresource",
    #     "init_gresource.py"
    # )
    # with open(init_gresource_py, "r") as f:
    #     init_gresource_content = f.read()
    #
    #
    #
    # # BUNDLE APP WITH PYINSTALLER
    # print("Bundling with PyInstaller...")
    #
    #
    #
    #
    # # Typelibs for DEB
    # if platform == "linux":
    #     typelibs = ["Gdk-4.0", "Gsk-4.0", "Gtk-4.0", "Graphene-1.0"]
    #     for typelib in typelibs:
    #         datas.update(add_typelib_deb(typelib))
    #
    #
    #
    # # PLATFORM SPECIFIC BELOW
    #
    # # Place for all debian source stuff: dir empirix-ui-setup_all
    # deb_src_home = join(bundles_home, SETUP_FILE_LIN)
    #
    # if platform == "linux":
    #     # PREPARE DEBIAN SOURCE FILES
    #     # Re-create home dir for DEB src stuff
    #     try:
    #         shutil.rmtree(deb_src_home)
    #     except FileNotFoundError as e:
    #         print("Unable to remove dir, doesn't exist.", e, sep='--->\n')
    #     mkdir(deb_src_home)
    #
    #     # Create 'control' file
    #     # Read more: https://www.debian.org/doc/debian-policy/ch-controlfields.html
    #     print("Creating control file...")
    #     deb_ctrl_path = join(deb_src_home, "DEBIAN")
    #     mkdir(deb_ctrl_path)
    #
    #     create_control_file(deb_ctrl_path, bundled_pkg_dir)
    #
    #     # Re-create usr/local/bin tree; distro in deb tree
    #     dist_in_deb_tree = join(deb_src_home, "usr", "local", "bin")
    #     makedirs(dist_in_deb_tree)
    #
    #     # Re-create usr/share/applications tree - for .desktop item
    #     apps_dir = join(deb_src_home, "usr", "share", "applications")
    #     makedirs(apps_dir)
    #
    #     # Create .desktop item
    #     print("Creating desktop item...")
    #     create_desktop_item(apps_dir)
    #
    #     # Move 'dist' contents to 'empirix-trader-setup_all/usr/local/bin/...'
    #     print("Moving dist contents to dist in deb tree...")
    #     shutil.move(bundled_pkg_dir, dist_in_deb_tree)
    #
    #     # BUILD .DEB PACKAGE
    #     print("Building deb package...")
    #     system(f"dpkg-deb --build {deb_src_home}")
    #
    #     # Remove 'dist', 'work', .spec
    #     print("Cleaning up...")
    #     shutil.rmtree(dist_dir)
    #     shutil.rmtree(work_dir)
    #     # remove(join(bundle_home, f"{PKG_NAME}.spec"))
    print("Packaging complete.")


def pyinstaller_bundle(spec_values, dist_dir, work_dir):
    """
    Bundle app with PyInstaller.
    Read more: https://pyinstaller.org/en/stable/usage.html
    https://pyinstaller.org/en/stable/runtime-information.html
    """

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


# def add_typelib_deb(typelib):
#     """
#     Because typelibs are not added automatically by PyInstaller, this is a fix to:
#     ImportError: Typelib file for namespace 'Gtk', version '4.0' not found.
#     windows girepository path = "C:\\gtk\\lib\\girepository-1.0"
#     """
#
#     deb_girepository = "/usr/lib/x86_64-linux-gnu/girepository-1.0"
#     return {join(deb_girepository, typelib + ".typelib"): "./gi_typelibs"}
#     # return {f"/usr/lib/x86_64-linux-gnu/girepository-1.0/{typelib}.typelib": "./gi_typelibs"}
#
#
# def create_control_file(deb_ctrl_path, bundled_pkg_dir):
#     with open(join(deb_ctrl_path, 'control'), 'w') as f_obj:
#         f_obj.write(
#             f"Package: {PKG_NAME}\n"
#             f"Version: {VERSION}\n"
#             "Section: misc\n"
#             "Priority: optional\n"
#             "Architecture: all\n"
#             f"Installed-Size: {get_size(bundled_pkg_dir)}\n"
#             "Maintainer: Raman Maładziašyn <maladziashyn@gmail.com>\n"
#             f"Description: {CTRL_DESC}\n"
#             "Homepage: https://empirix.ru/\n"
#         )
#
#
# def get_size(dir_path):
#     """
#     Return size of all directory contents in kilobytes.
#     Symlinks not followed.
#     """
#
#     total_size = 0
#     for root, dirs, files in walk(dir_path):
#         for f in files:
#             fp = join(root, f)
#             total_size += getsize(fp)
#     return ceil(total_size / 1024)
#
#
# def create_desktop_item(apps_dir):
#     # Create .desktop item
#     # Read more: https://specifications.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html#example
#
#     with open(join(apps_dir, f"{PKG_NAME}.desktop"), "w") as f_obj:
#         f_obj.write(
#             "[Desktop Entry]\n"
#             "Encoding=UTF-8\n"
#             "Version=1.0\n"
#             f"Name={APP_NAME}\n"
#             f"Comment={DTOP_CMNT}\n"
#             f"Exec=/usr/local/bin/{PKG_NAME}/{PKG_NAME}\n"
#             f"TryExec=/usr/local/bin/{PKG_NAME}/{PKG_NAME}\n"
#             f"Icon=/usr/local/bin/{PKG_NAME}/_internal/logo/{DTOP_LOGO}\n"
#             "Terminal=false\n"
#             "Type=Application\n"
#             "Categories=Finance;Math;Office;\n"
#             "Keywords=forex;trading;algorithms;"
#         )


if __name__ == '__main__':
    main()
