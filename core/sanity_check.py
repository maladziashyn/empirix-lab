# import json
import os

# from os.path import basename

# import config as c

from gresource.alert_dialog import AlertDialogTest


def main(alert_dialog_parent, declared_strategy, folders_picked, files_picked):
    # print("sanity check")
    # print(f"folders: {folders_picked}")
    # print(f"files: {files_picked}")
    if not folders_picked and not files_picked:
        AlertDialogTest().present(parent=alert_dialog_parent)

    if folders_picked:
        # check_dir, check_files = check_src_dir(folders_picked[0])
        check_src_dir(folders_picked[0])


def check_src_dir(src_dir):
    """
    Sanity check source directory.

    :param src_dir: str, folder to check for errors
    :return: TODO
    """

    print("start checking dirs")

    # Remove trailing slash
    if src_dir[-1] == os.sep:
        src_dir = src_dir[:-1]

    # with open(c.SPECS_TBL_DB, "r") as f:
    #     tickers = json.load(f)["mapping_tickers"]

    # home_dir = basename(src_dir)



#     dirs_all = dict()  # non-empty dirs
#     files_all = dict()
#     size_total = 0
#     n_files_total = 0
#     subdirs_total = 0
#
#     for root, dirs, files in os.walk(src_dir):
#         basenm = basename(root)
#         as_instrument = tickers[basenm] if basenm in tickers.keys() else None
#
#         # Delete long path, leave root as "/"
#         short_root = root.replace(src_dir, "")
#         short_root = os.sep if not short_root else short_root
#
#         dirs_all[short_root] = {
#             "basename": basenm,
#             "as_instrument": as_instrument,
#             "subdirs": len(dirs),
#             "n_files": len(files),
#             "files_MB": 0.0
#         }
#
#         subdirs_total += len(dirs)
#         n_files_total += len(files)
#
#         if files:
#             print(f"Looking into dir {root}")
#             add_to_files_all = pre_check_files_all(
#                 home_dir, as_instrument, root, files)
#             files_all = {**files_all, **add_to_files_all}
#
#             for f in files:
#                 full_fpath = join(root, f)
#                 fsize = round(getsize(full_fpath) / (1024**2), 2)
#                 size_total += fsize
#                 dirs_all[short_root]["files_MB"] += fsize
#
#             dirs_all[short_root]["files_MB"] = round(
#                 dirs_all[short_root]["files_MB"], 2)
#
#         dirs_all[os.sep]["files_MB"] = round(size_total, 2)
#         dirs_all[os.sep]["n_files"] = n_files_total
#         dirs_all[os.sep]["subdirs"] = subdirs_total
#
#     return dirs_all, files_all
