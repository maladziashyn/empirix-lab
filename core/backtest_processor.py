import hashlib
import json
import os
import pathlib
import re

from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from itertools import repeat
from lxml import html

from os.path import dirname,realpath
from sys import path
project_home_dir = dirname(dirname(realpath(__file__)))
if project_home_dir not in path:
    path.insert(0, project_home_dir)

import config as c

PY_TO_SQLITE_DATATYPES = {str: "TEXT", int: "INTEGER", float: "REAL"}
PY_TO_DB_DATATYPES = {
    str: {"sqlite": "TEXT", "mariadb": "VARCHAR(50)"},
    int: {"sqlite": "INTEGER", "mariadb": "MEDIUMINT"},
    float: {"sqlite": "REAL", "mariadb": "DOUBLE"}
}
instr_meta_keys_mapped = {
    "First tick time": "d_first_tick",
    "First BID": "d_first_bid",
    "First tick bid value": "d_first_bid",
    "First ASK": "d_first_ask",
    "First tick ask value": "d_first_ask",
    "Last tick time": "d_last_tick",
    "Last BID": "d_last_bid",
    "Last tick bid value": "d_last_bid",
    "Last ASK": "d_last_ask",
    "Last tick ask value": "d_last_ask",
    "Positions total": "d_pos_total",
    "Closed positions": "d_closed_pos",
    "Orders total": "d_orders",
    "Amount bought": "d_bought",
    "Bought": "d_bought",
    "Amount sold": "d_sold",
    "Sold": "d_sold",
    "Turnover": "d_turnover",
    "Commission Fees": "d_commission",
    "Commission": "d_commission",
}
date_columns = ["h1_date_from", "h1_date_to", "d_first_tick", "d_last_tick"]

XP_0 = "/html/body/div[3]/"  # beginning of all Xpaths

NA_CLOSE_EVENT = "N/A"

# RegEx patterns
re_strategy = re.compile(r"^\w+\b")
re_vjf_endings = re.compile(r"_(mux|mxu|cux|cxu)")
re_aux = re.compile(r"_aux_ins_([MC](XU|UX))")
re_version = re.compile(r"version.?")
re_date = re.compile(r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b")
re_instrument = re.compile(r"\b\w{3}/\w{3}")

re_e_cmsn = re.compile(r"\d+\.\d+")
re_e_comma_vals = re.compile(r"(rder|tion) \[.*\]")  # ordeR or positioN

re_e_overnt = re.compile(r"-?\d+(,\d+)?")
re_e_tail = re.compile(r"].*")

# Xpath
x_h1 = XP_0 + "h1"  # "/html/body/div[3]/h1"
x_info = XP_0 + "table[1]"  # Account Currency, etc.
x_params = XP_0 + "table[2]"
x_h2_ins = XP_0 + "h2[2]"  # "/html/body/div[3]/h2[2]"
x_instrument = XP_0 + "table[3]"
x_cl_pos = XP_0 + "table[5]"
x_events = XP_0 + "table[6]"

# User inputs
db_home = "C:\\RM_local\\misc\\emp_home\\"
# src_home = "C:\\RM_local\\misc\\empirix_home\\html_raw\\"
src_home = "/home/rsm/Documents/backtest_raw_reports"
src_dir = src_home


# WAIT (ERRORS): "Allig_stoch_v1"

# my_dirs = ["Greed", "hashi_v1", "hashi_v2", "hey_perry"]
# my_dirs = ["Pizza"]
# my_dirs = ["pin_regression"]
my_dirs = ["Dennis_Richards"]

# new: []

src_dirs = [os.path.join(src_home, d) for d in my_dirs]

src_type = 0  # 0 - old, 1 - new
user_name = "rsm"




def get_src_files(src_path):
    """
    Return list of tuples like
    (
        "AUD/JPY",
        "/home/path/to/audjpy/jforex_optimizer111.html",
        "jforex_optimizer111.html",
    )
    where:
    - "audjpy" is mapped to "AUD/JPY" - for precise search for tables in html
    - full path - to parse file
    - basename - to store in db

    :param src_path: str, dir path
    :return: list of 3-item tuples
    """

    with open(c.SPECS_TBL_DB, "r") as f:
        tickers = json.load(f)["mapping_tickers"]  # mapped tickers

    result = list()
    for root, dirs, files in os.walk(src_path):
        if files:
            for f in files:
                if pathlib.Path(f).suffix == ".html":
                    fpath = os.path.join(root, f)

                    # Ignore large files > 60 MB and 0-byte files
                    fsize = os.path.getsize(fpath)
                    if fsize == 0 or fsize > 62914560:
                        logger.info(f"Skip file {fpath}, size {
                                    (fsize/(1024**2)):.2f} MB.")
                        continue

                    result.append(
                        (
                            tickers[os.path.basename(root).lower()],
                            fpath,
                            os.path.basename(f),
                        )
                    )

    return result


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
            # return raw_val as is
            pass
        return value_out
    else:
        # This is for empty table cells
        return None

# def extract_headers(html_elem=None, axis_row=True, to_sort=False, to_map=False):
#     """
#     Extract headers from an HTML table: from column or row.
#
#     :param html_elem: lxml.html.HtmlElement
#     :param axis_row: bool, True for row, False for column
#     :param to_sort: bool, sort the resulting list
#     :param to_map: bool, whether to convert to values in MAP_TRADES_COLUMNS
#     :return: list
#     """
#
#     if axis_row:
#         result = list()
#         for row in html_elem:
#             result.append(row.xpath("./th")[0].text)
#     else:
#         row_gen = html_elem.iterfind("tr")  # build generator
#         result = list(h.text for h in next(row_gen))
#
#     if to_sort:
#         result.sort()
#     if to_map:
#         result = \
#             [MAP_TRADES_COLUMNS[h] if h in MAP_TRADES_COLUMNS.keys() else h for
#             h in result]
#         # for h in result:
#         #     if h in MAP_TRADES_COLUMNS.keys():
#
#     return result


def parse_h1(h1):
    """

    :return: 3-tuple
    - strategy name
    - list of instruments
    - list of dates: [0] from and [1] to
    E.g.: ('sd_20', ['EUR/GBP', 'GBP/USD'], ['2010-01-04 00:00:00', '2015-01-04 23:59:00'])
    """

    return (
        re.sub(re_vjf_endings, "", re.search(re_strategy, h1).group()),
        re.findall(re_instrument, h1),
        re.findall(re_date, h1)
    )


def parse_two_columns(html_elem):  # , fname):
    """
    Iterate over <tr> to extract table data <td>.
    Method .iter(tag="tr") is used on html_elem because 2 types of html
    documents were found:
    1) one that has <body> tag:
    <table class="simple" width="400px"><tbody><tr><th>Account Currency</th><td>USD</td></tr>
    2) and the other without it:
    <table class="simple" width="400px"><tr><th>Account Currency</th><td>USD</td></tr>
    Same is implemented in parse_two_columns_aux.

    :param html_elem: lxml.html
    :return: list of clean values
    """
    # try:
    return [
        clean_value(row.xpath("./td")[0].text.strip())
        for row in html_elem.iter(tag="tr")
    ]
    # except IndexError as e:
    #     print(f"Err {e} in file: {fname}")


def parse_two_columns_aux(html_elem):
    """
    Return 2-item tuple of:
    1) regular dictionary of parameters and their values - for hash
    2) list of clean values only - to insert into DB
    This function ignores AUX instruments in parameters using regex.

    :param html_elem: HtmlElement
    :return: tuple of (parameters keys-values, list of clean values only)
    """

    keys_values = dict()
    values_only = list()
    for row in html_elem.iter(tag="tr"):
        key = row.xpath("./th")[0].text
        if not re.search(re_aux, key) and not re.search(re_version, key):
            # Exclude _mux etc, and "version..."
            val = clean_value(row.xpath("./td")[0].text.strip())
            keys_values[key] = val
            values_only.append(val)
    return keys_values, values_only


def str_to_hash(str_val):
    dhash = hashlib.md5()
    dhash.update(str_val.encode())
    return dhash.hexdigest()


def full_parse_batch(src_batch):
    records = list()
    for i in full_parse_html(src_batch):
        records.append(i)
    return records


# def two_columns_dct(html_elem):
#     """
#     Convert 2-column table `th-td` into dict.
#
#     :param html_elem: lxml.html.HtmlElement
#     :return: dict
#     """
#
#     out = dict()
#     for row in html_elem:
#         out[row.xpath("./th")[0].text] = clean_value(
#             row.xpath("./td")[0].text.strip())
#     return out


# def two_columns_dct_aux(html_elem):
#     """
#     Convert 2-column table `th-td` into dict excluding aux currency parameter.
#
#     :param html_elem: lxml.html.HtmlElement
#     :return: dict
#     """
#
#     result = dict()
#     for row in html_elem:
#         key = row.xpath("./th")[0].text
#         if not re.search(re_aux, key):
#             result[key] = clean_value(row.xpath("./td")[0].text.strip())
#     return result


def map_param_datatypes(html_elem):
    """
    Map strategy's parameter's values from Python datatypes
    to their datatypes as they will work in databases: SQLite, MariaDB.
    E.g.: int becomes INTEGER, str becomes TEXT, etc.

    Datatypes:
    - SQLite: https://www.sqlite.org/datatype3.html
    - MariaDB: https://mariadb.com/kb/en/data-types/

    :param html_elem: lxml.html.HtmlElement
    :return: dict, with value as dict {"type": ..., "insert": True}, where
        insert is always True as additional fields are inserted by default
    """

    # params = two_columns_dct_aux(html_elem)
    params = parse_two_columns_aux(html_elem)[0]
    result = dict()
    for key, value in params.items():
        # result[key] = {"type": PY_TO_SQLITE_DATATYPES[type(value)],
        #                "insert": True}
        result[key] = {"type": PY_TO_DB_DATATYPES[type(value)],
                       "insert": True}
    return result


def parse_orders_table(html_elem):
    """
    Extract table rows.
    Return a list of lists - rows data.
    Output has to be picklable! for ProcessPoolExecutor.

    :param html_elem: lxml.html.HtmlElement
    :return: list (of lists)
    """

    # 1. create generator
    # row_gen = html_elem.iterfind("tr")
    row_gen = html_elem.iter(tag="tr")
    # 2. skip headers
    next(row_gen)

    # 3. extract rows, append to list
    result = list()
    try:
        while row_gen:
            # try:
            result.append(
                list(clean_value(cell.text) for cell in next(row_gen))
            )
            # except AttributeError as e:
            #     print(f"func 'parse_orders_table'. Cust err {e} in file {fname}")
            #     return
    except StopIteration:
        pass

    return result


def parse_event_log(html_elem, fpath):
    """
    Extract table rows.
    Return a list of lists - rows data for 4 event types:
    - "Order filled",
    - "Commissions" (Commission Fees),
    - "Overnights",
    - "Order closed" (Position closed)

    Ignored events: Order submitted, Order canceled, Order changed.

    :param html_elem: lxml.html.HtmlElement
    :param fpath: str, file path to raw report
    :return: list of lists
    """

    # 1. create generator
    # row_gen = html_elem.iterfind("tr")
    row_gen = html_elem.iter(tag="tr")
    # 2. skip headers
    next(row_gen)
    # 3. extract rows, append to list
    result = list()
    try:
        while row_gen:
            e_time, e_type, e_text = list(next(row_gen))

            # Scan and add to result only these 4 events:
            if e_type.text in ("Order filled",
                               "Commissions", "Commission Fees",
                               "Overnights",
                               "Order closed", "Position closed"):
                # Initialize vars for extracted values
                (e_label, e_instr, e_is_long, e_vol, e_price_fill,
                 e_cmsn, e_overnt, e_descr) = [None] * 8

                try:
                    if e_type.text in ("Commissions", "Commission Fees"):
                        e_cmsn = float(re.search(re_e_cmsn, e_text.text)
                                       .group())
                        # Exit
                        result.append(
                            [e_time.text, e_type.text, e_label, e_instr, e_is_long,
                             e_vol, e_price_fill, e_cmsn, e_overnt, e_descr]
                        )

                    else:
                        # Split event text in [] on comma, ignore last element
                        e_label, e_instr, e_is_long, e_vol = (
                            re.search(re_e_comma_vals, e_text.text)
                            .group()[6:-1].split(", ")
                        )
                        e_is_long = 1 if e_is_long == "BUY" else 0

                        if e_type.text in ("Order filled",
                                           "Order closed", "Position closed"):
                            # Get volume and fill price
                            e_vol, e_price_fill = e_vol.split(" at ")
                            e_vol, e_price_fill = float(
                                e_vol), float(e_price_fill)
                            # Get event description from event tail, before comma
                            e_descr = (re.search(re_e_tail, e_text.text)
                                       .group()[2:].split(", ")[0])
                            # if e_type.text in ("Order closed", "Position closed"):
                            #     e_descr = e_descr[10:-6]
                            # Exit
                            result.append(
                                [e_time.text, e_type.text, e_label, e_instr,
                                 e_is_long, e_vol, e_price_fill, e_cmsn, e_overnt,
                                 e_descr]
                            )

                        elif e_type.text == "Overnights":
                            e_vol = float(e_vol)
                            e_overnt = float(re.search(re_e_overnt, e_text.text)
                                             .group().replace(",", "."))
                            # Skip zero overnights
                            if e_overnt != 0:
                                # Exit
                                result.append(
                                    [e_time.text, e_type.text, e_label, e_instr,
                                     e_is_long, e_vol, e_price_fill, e_cmsn,
                                     e_overnt, e_descr]
                                )
                except AttributeError as e:
                    print(f"CUSTOM Error {e}, found in file: {fpath}. "
                          f"At time: {e_time.text}, "
                          f"event type: {e_type.text}")
                    return e, fpath, e_time, e_type, e_text
    except StopIteration:
        pass

    return result


def fees_swaps_close_event(event_log):
    """
    Extract fees, swap points, and close event for each position
    from the event log.
    Returned dict is structured like so:
    orders_master = {"label_ABC": {"fees": 40,
                                   "swap_points": 7.4444,
                                   "close_event": "take profit"},
                     "label_XYZ": {"fees": 50,
                                   "swap_points": 3.2222,
                                   "close_event": "stop loss"}, ...}
    The purpose of this function is to retrieve data that is going to be
    added to closed_orders.

    :param event_log: list (of lists) where each nested list is a parsed row
        from event_log
    :return orders_master: dict of dicts
    """

    orders_master = dict()

    # Init temp daily dicts before the loop
    orders_daily = dict()
    cmsn_daily = {"n_legs": 0, "sum_volume": 0, "sum_fees": 0}  # one day only

    for e in event_log:

        if e[1] in ("Commissions", "Commission Fees"):
            # Commissions end the banking day
            # Capture total commission
            cmsn_daily["sum_fees"] = e[7]

            # Transfer commission data to orders_daily
            for order in orders_daily.values():
                order["fees"] = (cmsn_daily["sum_fees"]
                                 * (order["volume"] / cmsn_daily["sum_volume"])
                                 if cmsn_daily["sum_volume"] > 0 else 0)

            # ADD ORDERS_DAILY TO ORDERS_MASTER
            # Add only fees & swap points, ignore volume
            if orders_daily:
                for key, value in orders_daily.items():
                    if key in orders_master.keys():
                        orders_master[key]["fees"] += value["fees"]
                        orders_master[key]["swap_points"] += value[
                            "swap_points"]
                    else:
                        orders_master[key] = {
                            "fees": value["fees"],
                            "swap_points": value["swap_points"]
                        }
                    if "close_event" in value.keys():
                        orders_master[key]["close_event"] = value[
                            "close_event"]

            # print(f"\torders_daily before reset: {orders_daily}")
            # reset temp daily dicts
            cmsn_daily = {"n_legs": 0, "sum_volume": 0, "sum_fees": 0}
            orders_daily = dict()

        elif e[1] == "Overnights":

            if e[2] not in orders_daily.keys():
                orders_daily[e[2]] = {"volume": 0, "swap_points": e[8]}
            else:
                orders_daily[e[2]]["swap_points"] += e[8]

        else:  # Order filled, Order closed, Position closed
            # Collect legs data
            # POSITION LABEL IS THE UNIQUE IDENTIFIER - dict key
            # We assume that position labels aren't duplicated
            cmsn_daily["n_legs"] += 1
            cmsn_daily["sum_volume"] += e[5]

            if e[2] not in orders_daily.keys():
                orders_daily[e[2]] = {"volume": e[5], "swap_points": 0.0}
            else:
                orders_daily[e[2]]["volume"] += e[5]
            if e[1] in ("Order closed", "Position closed"):
                orders_daily[e[2]]["close_event"] = e[-1]

    # Before "return", iterate over each row to find orders without
    # close event.
    for key, value in orders_master.items():
        if "close_event" not in value.keys():
            orders_master[key]["close_event"] = NA_CLOSE_EVENT

    return orders_master


def extend_with_evlog(closed_orders, event_log, start_eq):  # , fname):
    """
    Add 3+1 more values from "Event log" to each "Closed orders" row:
    fees, swap_points, close_event, + return (calculate)
    Use func fees_swaps_close_event on event_log to extract the 3 values.

    :param closed_orders: list (of lists), parsed "Closed orders:" table with
        label being the 0th element
    :param event_log: list (of lists), parsed "Event log:" table
    :param start_eq: float, start equity, normally 10000.0
    :return result: list (of lists), same as input but extended
    """

    # try:
    # Extract fees, swaps, close event
    fsce = fees_swaps_close_event(event_log)

    # Equity curve
    prev = start_eq

    # Add them to each row
    for r in closed_orders:

        if r[0] not in fsce.keys():
            # This is a workaround for a report that is by default invalid.
            # There are cases where event log abruptly breaks in long reports
            # and some events are missing.
            # This does not always mean there was no event, this is because
            # "Commissions" event never happened (is missing): only on this
            # event `orders_daily` dict in `fees_swaps_close_event`
            # get filled.
            fsce[r[0]] = {"fees": 0.0,
                          "swap_points": 0.0,
                          "close_event": NA_CLOSE_EVENT}

        # PnL with fees
        pnl = r[5] - fsce[r[0]]["fees"]
        # Extend "Closed orders:" row with 4 new values
        r.extend([
            # fsce[r[0]]["fees"],
            # fsce[r[0]]["swap_points"],
            fsce[r[0]]["close_event"],
            pnl / prev
        ])
        # Update previous equity
        prev += pnl
    return closed_orders
    # except TypeError as e:
    #     print(f"Got custom error {e} in file {fname}")
    #     return None


def full_parse_html(files_in):
    """
    Return hash, strategy, date_from, etc

    :param files_in: list of tuples (ticker, file path, file name)
    """

    for f in files_in:

        # # Ignore large files > 75 MB
        # fsize = os.path.getsize(f[1])
        # if fsize > 78643200:
        #     logger.info(f"Skip file {f[1]}, size {fsize:.2f} MB.")
        #     continue

        root = html.parse(f[1])

        # Description
        h1 = parse_h1(root.xpath("/html/body/div[3]/h1")[0].text)

        # Info
        info_vals = parse_two_columns(
            root.xpath("/html/body/div[3]/table[1]")[0]
        )

        # Parameters
        param_dict, param_vals = parse_two_columns_aux(
            root.xpath("/html/body/div[3]/table[2]")[0]
        )
        param_str = json.dumps(param_dict, sort_keys=True)
        hash_val = str_to_hash(param_str)

        # Find set of tables for main ticker: h2 with ticker
        try:
            _ = root.xpath(f".//h2[text()='Instrument {f[0]}']")[0]
            tbls = list(_.itersiblings(tag="table"))
        except IndexError as e:
            print(f"Custom Err: HTML in wrong folder. Err {e}, "
                  f"instrument expected {f[0]}, fpath {f[1]}\n")
            continue

        # Instrument
        instr_vals = parse_two_columns(tbls[0])

        # Event log
        event_log = parse_event_log(tbls[-1], f[1])

        # Closed orders
        # closed_orders = parse_orders_table(tbls[2])
        closed_orders = extend_with_evlog(
            closed_orders=parse_orders_table(tbls[2]),
            event_log=event_log,
            start_eq=info_vals[1]  # ,
            # fname=f[1]
        )

        yield (
            # `updates`
            (
                hash_val,  # hash from parameters
                # f[0],  # fdir
                f[2],  # fname

                # h1 values

                # h1[0],  # strategy

                # re.sub(re_vjf_endings, "", re.search(re_strategy, h1).group()),

                # ", ".join(h1[1]),  # instruments

                # ", ".join(re.findall(re_instrument, h1)),

                h1[2][0],  # date from
                h1[2][1],  # date to
                # *re.findall(re_date, h1),


                # info table values
                # *info_vals,  # from "acc_currency" to "fees_total"
                # instrument table values
                # *instr_vals  # from "first_tick_time" to "fees_instrument"
            ),

            # `parameters`
            (
                hash_val,
                # h1[2][0],  # date from
                # h1[2][1],  # date to
                param_str,
                *param_vals,
            ),

            # `closed_orders`
            (
                closed_orders
            ),

            # # `event_log`
            # (
            #     event_log
            # ),

        )


def pre_check_files_all(base_dir, ins_mapped, root, files):
    """
    Check all source htmls before parsing them and moving results into
    the database.

    :param base_dir: str, actually it's the strategy name
    :param ins_mapped: str, file dir mapped as default instrument, comes in
        as basename of the file's home dir
    :param root: str, full path to instrument folder, like "audusd"
    :param files: list of files in folder
    :return: dict
    """

    files_stats = dict()
    full_fpaths = [os.path.join(root, f) for f in files]

    with ProcessPoolExecutor() as executor:
        results = executor.map(
            pre_check_file_one,
            repeat(base_dir, len(files)),
            repeat(ins_mapped, len(files)),
            full_fpaths
        )
        for res in results:
            files_stats = {**files_stats, **res}

    return files_stats


def pre_check_file_one(strategy_name, ins_mapped, full_fpath):
    """
    Parse one html, extract basic data: path, extension, size (MB),
    h1_strategy, h1_instruments, h1_dates.

    :param strategy_name: str, as main root
    :param ins_mapped: str, file dir mapped as default instrument
    :param full_fpath: str, full file path
    :return: dict
    """

    result = dict()
    fext = pathlib.Path(full_fpath).suffix
    fsize = round(os.path.getsize(full_fpath) / (1024 ** 2), 2)
    file_home = os.path.basename(os.path.dirname(full_fpath))

    f = os.path.basename(full_fpath)
    result[f] = {
        "path": full_fpath, "ext": fext, "size_MB": fsize,
        "h1_strategy": "", "h1_instruments": "", "h1_date_from": None,
        "h1_date_to": None, "i_acc_currency": "", "i_init_equity": 0.0,
        "i_fin_equity": 0.0
    }
    if fext == ".html":
        lxml_root = html.parse(full_fpath)

        # Parse h1 header
        h1 = lxml_root.xpath(x_h1)[0].text
        strategy, instruments, dates = parse_h1(h1)
        result[f]["h1_strategy"] = ("OK" if strategy == strategy_name
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
            instr_meta_keys_mapped[row.xpath("./th")[0].text.strip()]:
                clean_value(row.xpath("./td")[0].text.strip())
            for row in tbls[0].iter(tag="tr")
        }
        result[f] = {**result[f], **instr_meta}

        for dc in date_columns:
            dt_string = result[f][dc]
            result[f][dc] = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")

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

    return result
