import json
import numpy as np
import os
import pandas as pd
import pathlib
import re
import subprocess
# import sys

from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from itertools import repeat
from lxml import html
from os.path import basename, getsize, join
from sys import platform

import config as c

from core import db_manager as db_man
# from gresource.alert_dialog import AlertDialogTest


def main():
    run_check(None, "adr_ctr_v1", ["/home/rsm/Documents/empirix_ui_home/raw_html/adr_ctr_v1"], None, 75, True)


def run_check(alert_dialog_parent, declared_strategy, folders_picked, files_picked, max_size, open_excel):
    """Check source dirs/files before parsing raw htmls."""

    if not folders_picked and not files_picked:
        print("nothing selected")
        # AlertDialogTest().present(parent=alert_dialog_parent)
    elif folders_picked:
        # check_dir, check_files = check_src_dir(folders_picked[0])
        check_dir, check_files = check_src_dir(declared_strategy, folders_picked, max_size)
        make_excel(declared_strategy, check_dir, check_files, open_excel)
    else:  # files picked
        print("check zip files")


def make_excel(declared_strategy, check_dir, check_files, open_excel):
    print("Making Excel...")

    df_dirs = pd.DataFrame.from_dict(check_dir, orient="index")
    df_dirs.reset_index(inplace=True)
    df_dirs.rename(columns={"index": "directory"}, inplace=True)

    df_files = pd.DataFrame.from_dict(check_files, orient="index")
    df_files.reset_index(inplace=True)
    df_files.rename(columns={"index": "name"}, inplace=True)

    sanity_checks_dir = db_man.select_var("sanity_checks_dir")

    excel_output_fpath = join(sanity_checks_dir,
                              f"backtest_reports_check_{declared_strategy}.xlsx")

    writer = pd.ExcelWriter(excel_output_fpath, engine="xlsxwriter")

    sh1 = f"{declared_strategy}_dirs"
    sh2 = f"{declared_strategy}_files"
    sh3 = f"{declared_strategy}_distribs"

    df_dirs.to_excel(
        writer,
        sheet_name=sh1,
        index=False,
        freeze_panes=(1, 1)
    )

    df_files.to_excel(
        writer,
        sheet_name=sh2,
        index=False,
        freeze_panes=(1, 1)
    )

    st_col = 0
    for col in ["size_MB", "i_init_equity", "i_fin_equity",
                "p_count", "d_pos_total", "d_closed_pos",
                "ticks_coverage", "orders_errors", "orders_merged"]:

        df_hist = hist_from_series(df_files[col])
        df_hist.to_excel(
            writer,
            sheet_name=sh3,
            index=False,
            startrow=1,
            startcol=st_col
        )
        worksheet = writer.sheets[sh3]
        worksheet.write(0, st_col, col)

        st_col += 4

    # Format sheet 1:
    worksheet = writer.sheets[sh1]
    # Get df dimensions
    max_row, max_col = df_dirs.shape
    # Widen columns
    for idx, col in enumerate(df_dirs):  # iterate over all columns
        series = df_dirs[col]
        max_len = max((
            series.astype(str).map(len).max(),  # len of largest item
            len(str(series.name))  # len of column name/header
        )) + 4  # add a little extra space
        worksheet.set_column(idx, idx, max_len)  # set column width
    # # Set autofilter
    worksheet.autofilter(0, 0, max_row, max_col - 1)

    # Format sheet 2:
    worksheet = writer.sheets[sh2]
    # Get df dimensions
    max_row, max_col = df_files.shape
    # Widen columns
    for idx, col in enumerate(df_files):  # iterate over all columns
        series = df_files[col]
        max_len = max((
            series.astype(str).map(len).max(),  # len of largest item
            len(str(series.name))  # len of column name/header
        )) + 4  # add a little extra space
        worksheet.set_column(idx, idx, max_len)  # set column width
    # # Set autofilter
    worksheet.autofilter(0, 0, max_row, max_col - 1)

    writer.close()

    if open_excel:
        if platform == "linux":
            subprocess.call(["xdg-open", excel_output_fpath], stderr=subprocess.DEVNULL)
        elif platform == "win32":
            os.startfile(excel_output_fpath)


def hist_from_series(df_col, bins=10):
    """
    Build a histogram table based on a pandas df column.
    Show counts or percentages.
    """

    # Initialize np arr
    a = np.array(df_col)

    # Remove nan
    a = a[~(np.isnan(a))]

    # Create counts & bins
    a_count, a_bin = np.histogram(a=a, bins=bins)

    # Get percentages
    a_perc = a_count / a_count.sum()

    # Multiply perc by 100
    a_perc = np.round(a_perc * 100, 2)

    # Insert 0 as first value into values
    a_count = np.insert(a_count, 0, 0)
    a_perc = np.insert(a_perc, 0, 0)

    # Build dataframe
    return pd.DataFrame(data={"bin": a_bin, "count": a_count, "perc": a_perc})


def check_src_dir(declared_strategy, folders_picked, max_size):
    """
    Sanity check source directory.

    :param declared_strategy: str, strategy name
    :param src_dir: str, folder to check for errors
    :return: TODO
    """

    with open(c.SPECS_TBL_DB, "r") as f:
        tickers = json.load(f)["mapping_tickers"]

    dirs_all = dict()  # non-empty dirs
    files_all = dict()
    size_total = 0
    n_files_total = 0
    subdirs_total = 0

    for folder in folders_picked:
        for root, dirs, files in os.walk(folder):
            root_basename = basename(root)
            as_instrument = tickers[root_basename] if root_basename in tickers.keys() else None

            # Delete long path, leave root as "/"
            short_root = root.replace(folder, "")
            short_root = os.sep if not short_root else short_root

            dirs_all[short_root] = {
                "basename": root_basename,  # only dir name, not full path
                "as_instrument": as_instrument,  # e.g. audusd as AUD/USD
                "subdirs": len(dirs),  # subdirs count inside dir
                "n_files": len(files),  # files count inside dir
                "files_MB": 0.0  # sum of files sizes inside dir
            }

            subdirs_total += len(dirs)
            n_files_total += len(files)

            if files:
                print(f"Looking into dir {root}")
                add_to_files_all = pre_check_files_all(
                    declared_strategy, as_instrument, root, files, max_size)
                # files_all = {**files_all, **add_to_files_all}
                files_all.update(add_to_files_all)

                for f in files:
                    full_fpath = join(root, f)
                    fsize = round(getsize(full_fpath) / (1024**2), 2)
                    size_total += fsize
                    dirs_all[short_root]["files_MB"] += fsize

                dirs_all[short_root]["files_MB"] = round(
                    dirs_all[short_root]["files_MB"], 2)

            dirs_all[os.sep]["files_MB"] = round(size_total, 2)
            dirs_all[os.sep]["n_files"] = n_files_total
            dirs_all[os.sep]["subdirs"] = subdirs_total

    # print("Complete")
    return dirs_all, files_all


def pre_check_files_all(declared_strategy, ins_mapped, root, files, max_size):
    """
    Check all source htmls before parsing them and moving results into
    the database.

    :param declared_strategy: str, actually it's the strategy name
    :param ins_mapped: str, file dir mapped as default instrument, comes in
        as basename of the file's home dir
    :param root: str, full path to instrument folder, like "audusd"
    :param files: list of files in folder
    :return: dict
    """

    files_stats = dict()
    full_fpaths = [join(root, f) for f in files]

    with ProcessPoolExecutor() as executor:
        results = executor.map(
            pre_check_file_one,
            repeat(declared_strategy, len(files)),
            repeat(ins_mapped, len(files)),
            full_fpaths,
            repeat(max_size, len(files))
        )
        for res in results:
            files_stats = {**files_stats, **res}

    return files_stats


def pre_check_file_one(declared_strategy, ins_mapped, full_fpath, max_size):
    """
    Parse one html, extract basic data: path, extension, size (MB),
    h1_strategy, h1_instruments, h1_dates.

    :param declared_strategy: str, as main root
    :param ins_mapped: str, file dir mapped as default instrument
    :param full_fpath: str, full file path
    :param max_size: str, maximum allowed file size in megabytes
    :return: dict
    """

    result = dict()
    fext = pathlib.Path(full_fpath).suffix
    fsize = round(getsize(full_fpath) / (1024 ** 2), 2)  # in Megabytes

    try:
        f = basename(full_fpath)
        result[f] = {
            "path": full_fpath, "ext": fext, "size_MB": fsize,
            "h1_strategy": "", "h1_instruments": "", "h1_date_from": None,
            "h1_date_to": None, "i_acc_currency": "", "i_init_equity": 0.0,
            "i_fin_equity": 0.0
        }

        if fsize > max_size:
            # skip files greater than e.g. 75 MB
            return result

        if fext == ".html":
            lxml_root = html.parse(full_fpath)

            # Parse h1 header
            h1 = lxml_root.xpath(c.xp_h1)[0].text
            strategy, instruments, dates = parse_h1(h1)
            result[f]["h1_strategy"] = ("OK" if strategy == declared_strategy
                                        else strategy)
            result[f]["h1_instruments"] = ("OK" if ins_mapped in instruments
                                           else instruments)
            result[f]["h1_date_from"] = dates[0]
            result[f]["h1_date_to"] = dates[1]

            # Parse "Info" table
            html_elem = lxml_root.xpath("/html/body/div[3]/table[1]")[0]
            acc_currency, init_equity, fin_equity, tmp3, tmp4 = [
                clean_value(row.xpath("./td")[0].text.strip())
                for row in html_elem.iter(tag="tr")
            ]
            result[f]["i_acc_currency"] = acc_currency
            result[f]["i_init_equity"] = init_equity
            result[f]["i_fin_equity"] = fin_equity

            # Parse "Parameters" table
            html_elem = lxml_root.xpath("/html/body/div[3]/table[2]")[0]

            params = [row.xpath("./th")[0].text
                      for row in html_elem.iter(tag="tr")]
            result[f]["p_count"] = len(params)
            result[f]["p_listed"] = ";".join(params)

            # Parse "Instrument abc/def" table
            # Find set of tables for main ticker: h2 with ticker
            # try:
            _ = lxml_root.xpath(f".//h2[text()='Instrument {ins_mapped}']")[0]

            tbls = list(_.itersiblings(tag="table"))
            # except IndexError as e:
            #     # print(f"Custom Err: HTML in wrong folder. Err {e}, "
            #     #       f"instrument expected {f[0]}, fpath {f[1]}\n")
            #     tbls = None

            # Instrument
            # if tbls:
            instr_meta = {
                c.instr_meta_keys_mapped[row.xpath("./th")[0].text.strip()]:
                    clean_value(row.xpath("./td")[0].text.strip())
                for row in tbls[0].iter(tag="tr")
            }
            result[f] = {**result[f], **instr_meta}

            for dc in c.date_columns:
                dt_string = result[f][dc]
                result[f][dc] = datetime.strptime(
                    dt_string, "%Y-%m-%d %H:%M:%S")

            result[f]["days_delta_h1_date_from"] = (result[f]["d_first_tick"]
                                                    - result[f]["h1_date_from"])
            result[f]["days_delta_h1_date_to"] = (result[f]["h1_date_to"]
                                                  - result[f]["d_last_tick"])
            result[f]["ticks_coverage"] = (
                (result[f]["d_last_tick"] - result[f]["d_first_tick"])
                / (result[f]["h1_date_to"] - result[f]["h1_date_from"])
            )
            # Closed orders tbls[2]
            row_gen = tbls[2].iter(tag="tr")
            # 2. skip headers
            next(row_gen)
            errors, merged = 0, 0
            try:
                while row_gen:
                    # try:
                    for cell in next(row_gen):
                        if cell.text == "ERROR":
                            errors += 1
                        elif cell.text == "MERGED":
                            merged += 1
            except StopIteration:
                pass
            result[f]["orders_errors"] = errors
            result[f]["orders_merged"] = merged

        # Event log tbls[-1]
    except Exception as e:
        print(f"ERROR >> {full_fpath}. Info: {e}")

        # sys.exit(1)

        return result

    return result


def parse_h1(h1):
    """

    :return: 3-tuple
    - strategy name
    - list of instruments
    - list of dates: [0] from and [1] to
    E.g.: ('sd_20', ['EUR/GBP', 'GBP/USD'], ['2010-01-04 00:00:00', '2015-01-04 23:59:00'])
    """

    return (
        re.sub(c.re_vjf_endings, "", re.search(c.re_strategy, h1).group()),
        re.findall(c.re_instrument, h1),
        re.findall(c.re_date, h1)
    )


def clean_value(raw_val):
    """
    Extract clean value of relevant type from a string.
    In case of numeric values, return float, as returning int caused errors
    in mariadb when values in the same column were both float AND int.

    Read more:
    - About apostrophe "U+2019, RIGHT SINGLE QUOTATION MARK":
     https://stackoverflow.com/questions/45539010/apostrophes-are-printing-out-as-%C3%A2-x80-x99
     This appears in some MTBankFX reports.

    :param raw_val: str, can be converted to int, float, date
    :return: float, date, or string
    """

    if raw_val:
        # 1. replace HEX apostrophe, and comma with dot
        value_out = (raw_val.replace("\x92", "")
                     .replace(",", ".")
                     .replace("?", "")
                     .replace(chr(226), "")
                     .replace("\x80\x99", ""))

        # 2. obtain numerical/date value
        try:
            if value_out.count(".") == 1:
                value_out = float(value_out)
            elif value_out.upper() in ['TRUE', 'FALSE']:
                value_out = 1 if value_out.upper() == 'TRUE' else 0
            elif value_out.upper() in ['BUY', 'SELL']:
                value_out = 1 if value_out.upper() == 'BUY' else 0
            elif value_out in ("ERROR", "MERGED", ""):
                value_out = None
            elif raw_val.count(",") > 1:
                # To account for such "34,290,902,87" values
                value_out = value_out.replace(".", "", value_out.count(".")-1)
                value_out = float(value_out)
            else:
                value_out = float(value_out)
        except (ValueError, TypeError):
            if "+ MERGED" in value_out.upper():
                return clean_value(value_out.upper().replace(" + MERGED", ""))
            else:
                # return raw_val as is
                pass
        return value_out
    else:
        # This is for empty table cells
        return None


if __name__ == "__main__":
    main()
