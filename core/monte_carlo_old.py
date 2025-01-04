import concurrent.futures
import itertools
import pandas as pd
import plotly.express as px
import random
# import time
import webbrowser
from datetime import datetime
from os.path import join
from decimal import Decimal


def foo(x, y):
    """

    :param x:
    :param y:
    :return:
    """
    return x + y


class MonteCarlo:
    """
    Monte Carlo simulations: single and F-search.
    Randomization types: random number, random choice, shuffle.
    """

    def __init__(self, stg, sim_type, rand_type):
        """
        :param stg: dict of all parameters from gui
        :param sim_type: str - 'single', 'search'
        :param rand_type: 'Random Number' (0), 'Random Choice' (1),
        'Shuffle' (1)
        """
        self.stg = stg
        self.sim_type = sim_type
        self.rand_type = rand_type
        self.years = self.stg['montecarlo']['random_number']['years']
        self.data = None
        if self.rand_type in ['Random Choice', 'Shuffle']:
            df = pd.read_excel(
                io=self.stg['montecarlo']['choice_or_shuffle']['mixer_fpath'],
                sheet_name=self.stg['montecarlo']['choice_or_shuffle']['sheet_name'],
                usecols='K',
                skiprows=3,
                header=None).squeeze("columns")
            self.src_list = df.tolist()

    def run_simulation(self):
        """Single or F-search simulations."""

        if self.sim_type == 'single':
            if self.rand_type == 'Random Number':
                # Separate USER_SETTINGS dict
                user_settings = {'rand_type': self.rand_type,
                                 **self.stg['montecarlo']['basic'],
                                 **self.stg['montecarlo']['random_number']}
                del user_settings['years']
            else:  # 'Random Choice', 'Shuffle'
                user_settings = {
                    'rand_type': self.rand_type,
                    'fraction': self.stg['montecarlo']['random_number']['fraction'],
                    **self.stg['montecarlo']['basic']
                }

            self.__get_risk_of_ruin(
                **user_settings,
                show_curves=self.stg['montecarlo']['report']['show_curves'],
                with_data=True
            )

            self.__update_dataframes()
            self.__update_figures(
                simulations=self.stg['montecarlo']['basic']['simulations'],
                show_curves=self.stg['montecarlo']['report']['show_curves'],
                bins=self.stg['montecarlo']['report']['bins']
            )
            self.__generate_html(
                reports_dir=self.stg['montecarlo']['report']['reports_dir'],
                user_settings=user_settings
            )

        elif self.sim_type == 'search':
            user_settings = {
                'rand_type': self.rand_type,
                **self.stg['montecarlo']['basic'],
                'trades': self.stg['montecarlo']['random_number']['trades'],
                'win_rate': self.stg['montecarlo']['random_number']['win_rate'],
                'wl_ratio': self.stg['montecarlo']['random_number']['wl_ratio'],
                'f_min': self.stg['montecarlo']['search']['f_min'],
                'f_max': self.stg['montecarlo']['search']['f_max'],
                'f_step': self.stg['montecarlo']['search']['f_step'],
                **self.stg['montecarlo']['report'],
            }

            self.__search_optimal_f(**user_settings)
            self.__update_dataframes()
            self.__update_figures(
                simulations=self.stg['montecarlo']['basic']['simulations'],
                show_curves=self.stg['montecarlo']['report']['show_curves'],
                bins=self.stg['montecarlo']['report']['bins']
            )
            self.__generate_html(
                reports_dir=self.stg['montecarlo']['report']['reports_dir'],
                user_settings=user_settings
            )

    def __search_optimal_f(self, rand_type, ruin, simulations, trades,
                           win_rate, wl_ratio, f_min, f_max, f_step,
                           reports_dir, show_curves, bins):
        """Use the provided randomization type and find optimal F."""

        f_delta = f_step * 20
        f_rnd = str(Decimal(str(f_step)))[::-1].index(".")
        f_mid = self.__calc_f_mid(f_min, f_max, f_rnd)
        ror_data = {
            'f_min': [f_min],
            'f_mid': [f_mid],
            'f_max': [f_max],
            'f_delta': [f_max - f_min],
            'r_min': [self.__get_risk_of_ruin(rand_type, ruin, simulations,
                                              trades, win_rate, wl_ratio,
                                              f_min)],
            'r_mid': [self.__get_risk_of_ruin(rand_type, ruin, simulations,
                                              trades, win_rate, wl_ratio,
                                              f_mid)],
            'r_max': [self.__get_risk_of_ruin(rand_type, ruin, simulations,
                                              trades, win_rate, wl_ratio,
                                              f_max)],
        }
        # Initialize search points with data from ror_data
        search_points = {
            'fraction': [f_min, f_max, f_mid],
            'ror': [ror_data['r_min'][-1],
                    ror_data['r_max'][-1],
                    ror_data['r_mid'][-1]],
        }

        # Search: narrow down until delta is reached
        while ror_data['f_delta'][-1] > f_delta:
            f_max = ror_data['f_max'][-1]
            f_min = ror_data['f_min'][-1]
            f_mid = ror_data['f_mid'][-1]

            r_max = ror_data['r_max'][-1]
            r_min = ror_data['r_min'][-1]
            r_mid = ror_data['r_mid'][-1]

            if r_max > 0 and r_mid > 0:
                # Decrease maximum, go left from mid
                f_max_new = f_mid
                r_max_new = r_mid
                f_min_new = f_min
                r_min_new = r_min
                f_delta_new = f_mid - f_min
                f_mid_new = self.__calc_f_mid(f_min, f_mid, f_rnd)
            elif r_min == 0 and r_mid == 0:
                # Increase, go right from mid
                f_min_new = f_mid
                r_min_new = r_mid
                f_max_new = f_max
                r_max_new = r_max
                f_delta_new = f_max - f_mid
                f_mid_new = self.__calc_f_mid(f_mid, f_max, f_rnd)

            # append new stuff
            ror_data['f_min'].append(f_min_new)
            ror_data['r_min'].append(r_min_new)
            ror_data['f_max'].append(f_max_new)
            ror_data['r_max'].append(r_max_new)
            ror_data['f_delta'].append(f_delta_new)

            # calculate new ror
            r_mid_new = self.__get_risk_of_ruin(rand_type, ruin, simulations,
                                                trades, win_rate, wl_ratio,
                                                f_mid_new)

            # append new vals to ror_data...
            ror_data['f_mid'].append(f_mid_new)
            ror_data['r_mid'].append(r_mid_new)
            # ...and search_points
            search_points['fraction'].append(f_mid_new)
            search_points['ror'].append(r_mid_new)

        if ror_data['r_mid'][-1] > 0:
            start_f = ror_data['f_mid'][-1]
        elif ror_data['r_max'][-1] > 0:
            start_f = ror_data['f_max'][-1]
        else:
            return None

        # Once delta is reached, start stepping down from it
        if start_f:
            fraction = start_f
            self.__get_risk_of_ruin(rand_type, ruin, simulations, trades,
                                    win_rate, wl_ratio, fraction,
                                    show_curves=show_curves, with_data=True)
            ror = self.data['ror']
            # In case the fraction is already zero, we add it to dict
            # to display as the result
            self.data['fraction'] = fraction
            # print(f'before last while loop: {self.data["fraction"]}')

            while ror > 0:
                fraction = round(fraction - f_step, f_rnd)
                self.__get_risk_of_ruin(rand_type, ruin, simulations, trades,
                                        win_rate, wl_ratio, fraction,
                                        show_curves=show_curves,
                                        with_data=True)
                ror = self.data['ror']
                self.data['fraction'] = fraction

                # print(f'from last while loop: {self.data["fraction"]}')

                search_points['fraction'].append(fraction)
                search_points['ror'].append(ror)

            self.data['search_points'] = search_points.copy()
            # print(f'OPTIMAL F = {fraction}; RoR = {ror}')
        else:
            return None

    @staticmethod
    def __user_settings_to_string(**kwargs):
        """Convert user settings to string, for html."""

        result = ""
        for key, value in kwargs.items():
            result += f'{key}: {value}</br>'
        return result

    def __get_risk_of_ruin(self, rand_type, ruin, simulations=0, trades=0,
                           win_rate=0, wl_ratio=0, fraction=0, show_curves=0,
                           with_data=False):
        """
        Obtain risk of ruin based on a list of trade returns, randomization
        type, etc."""

        # time_start = time.perf_counter()
        ruined = list()  # items are booleans
        self.data = {
            'eq_curves': dict(),
            'mdds': list(),
            'fin_results': list(),
            'fraction': None,
            'ror': None,
        }
        # Run simulations
        if rand_type == 'Random Number':
            with concurrent.futures.ProcessPoolExecutor() as executor:
                results = executor.map(
                    self.one_simulation,
                    itertools.repeat(rand_type, simulations),
                    itertools.repeat(trades, simulations),
                    itertools.repeat(win_rate, simulations),
                    itertools.repeat(wl_ratio, simulations),
                    itertools.repeat(fraction, simulations)
                )
        elif rand_type in ['Random Choice', 'Shuffle']:
            with concurrent.futures.ProcessPoolExecutor() as executor:
                results = executor.map(
                    self.one_simulation,
                    itertools.repeat(rand_type, simulations),
                    # dummy for unused named arg: trades
                    itertools.repeat([0], simulations),
                    # dummy for unused named arg: win_rate
                    itertools.repeat([0], simulations),
                    # dummy for unused named arg: wl_ratio
                    itertools.repeat([0], simulations),
                    itertools.repeat(fraction, simulations)
                )

        res_id = 0
        for result in results:
            mdd = self.__kpi_mdd(result)
            ruined.append(mdd >= ruin)
            if with_data:
                if len(self.data['eq_curves']) < show_curves:
                    self.data['eq_curves'][f'eq_curve_{res_id:02d}'] = result
                self.data['mdds'].append(mdd)

                annualized_return = result[-1] ** (1 / self.years) - 1

                self.data['fin_results'].append(annualized_return)
            res_id += 1

        ror = sum(ruined) / simulations

        # print(f'risk-of-ruin, elapsed:'
        #       f' {round(time.perf_counter() - time_start, 4)} sec.')

        if with_data:
            self.data['ror'] = ror
        if not with_data:
            return ror

    @staticmethod
    def __kpi_mdd(eq_curve, add_first_val=False, first_val=1):
        """Return one KPI: MDD - maximum drawdown."""

        if add_first_val:
            eq_curve.insert(0, first_val)
        hwm = [eq_curve[0]]
        draw_down = [0]
        for trade_id in range(1, len(eq_curve)):
            hwm.append(max(hwm[trade_id - 1], eq_curve[trade_id]))
            draw_down.append(
                (hwm[trade_id] - eq_curve[trade_id]) / hwm[trade_id])
        return max(draw_down)

    def one_simulation(self, rand_type, trades=0, win_rate=0.0,
                       wl_ratio=0.0, fraction=0.0):
        """Obtain equity curve from one simulation."""

        eq_curve = [1]
        if rand_type == 'Random Number':
            for trade in range(1, trades + 1):
                if random.random() < win_rate:  # WINNER!
                    append_value = (eq_curve[trade - 1]
                                    * (1 + fraction * wl_ratio))
                else:  # LOSER!
                    append_value = eq_curve[trade - 1] * (1 - fraction)
                eq_curve.append(append_value)
        elif rand_type == 'Random Choice':
            fraction *= 100
            for trade in range(len(self.src_list)):
                rand_return = random.choice(self.src_list) * fraction
                eq_curve.append(eq_curve[trade] * (1 + rand_return))
        elif rand_type == 'Shuffle':
            fraction *= 100
            random.shuffle(self.src_list)
            for trade in range(len(self.src_list)):
                shuf_return = self.src_list[trade] * fraction
                eq_curve.append(eq_curve[trade] * (1 + shuf_return))
        return eq_curve

    def __update_dataframes(self):
        if self.sim_type == 'search':
            self.df_search_points = pd.DataFrame(self.data['search_points'])
        self.df_curves = pd.DataFrame(self.data['eq_curves'])
        self.df_mdds = pd.DataFrame(self.data['mdds'])
        self.df_finres = pd.DataFrame(self.data['fin_results'])

    def __update_figures(self, simulations, show_curves, bins):
        if self.sim_type == 'search':
            self.fig_search_points = px.scatter(
                self.df_search_points,
                x='fraction', y='ror',
                title='Fraction vs Risk of Ruin'
            )
        self.fig_curves = px.line(
            self.df_curves,
            title=f'Equity curves, {show_curves} of {simulations}'
        )
        self.fig_mdds = px.histogram(
            self.df_mdds,
            nbins=bins,
            title='MDD distribution'
        )
        self.fig_finres = px.histogram(
            self.df_finres,
            nbins=bins,
            title='FinResult distribution'
        )
        # self.fig_finres.show()

    def __generate_html(self, reports_dir, user_settings):
        """Generate html report."""

        n = datetime.now()
        html_fname = f"mc_{self.sim_type}_" \
                     f"{self.rand_type.lower().replace(' ', '_')}_" \
                     f"{n.year:04d}{n.month:02d}{n.day:02d}" \
                     f"{n.hour:02d}{n.minute:02d}{n.second:02d}.html"
        html_fpath = join(reports_dir, html_fname)

        if self.sim_type == 'single':
            html_content = f"""
                <h1>Report: Monte Carlo simulation</h1>
                <p>
                Type: {self.sim_type}</br>
                Randomization: {self.rand_type}
                </p>

                <h2>Settings</h2>
                <p>{self.__user_settings_to_string(**user_settings)}</p>
                <h2>Results</h2>

                <p>
                RISK OF RUIN = <b>{round(self.data['ror'] * 100, 2)}%</b></br>
                Mean MDD = {round(self.df_mdds.mean()[0] * 100, 2)}%</br>
                Mean FinResult = {round(self.df_finres.mean()[0] * 100, 2)}%
                </p>
                """
        elif self.sim_type == 'search':
            html_content = f"""
                <h1>Report: Monte Carlo simulation</h1>
                <p>
                Type: {self.sim_type}</br>
                Randomization: {self.rand_type}
                </p>

                <h2>Settings</h2>
                <p>{self.__user_settings_to_string(**user_settings)}</p>
                <h2>Results</h2>

                <p>
                <b>OPTIMAL F = {self.data['fraction']}</b>
                (or {round(self.data['fraction']*100, 6)}%)</br>
                Risk of ruin = kinda zero</br>
                Mean MDD = {round(self.df_mdds.mean()[0] * 100, 2)}%</br>
                Mean FinResult = {round(self.df_finres.mean()[0] * 100, 2)}%
                </p>
                """

        with open(html_fpath, 'w', encoding='utf-8') as f:
            f.write(html_content)
            f.write(self.fig_curves.to_html(full_html=False))
            f.write(self.fig_mdds.to_html(full_html=False))
            f.write(self.fig_finres.to_html(full_html=False))
            if self.sim_type == 'search':
                f.write(self.fig_search_points.to_html(full_html=False))

        webbrowser.open_new_tab(html_fpath)

    @staticmethod
    def __calc_f_mid(f_min, f_max, f_rnd):
        """Calculate fraction in the middle, between max and min provided."""

        return round(f_min + (f_max - f_min) * 0.5, f_rnd)
