# -*- coding: utf-8 -*-

"""Generate graphs of player stats."""

import sys
import math
import csv

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import requests

import ui_utils
import wn8_utils

CONFIG_FILE = '../res/config.txt'
APP_ID = 'demo'
ACCOUNT_INFO_REQUEST_URL = 'https://api.worldoftanks.eu/wot/account/info/'
BATCH_SIZE = 100
DATA_FOLDER = '../data'
CATEGORIES_FOLDER = '{data_folder}/categories'.format(data_folder=DATA_FOLDER)
ZLIST_FILE = '{data_folder}/ZLIST_ID.csv'.format(data_folder=DATA_FOLDER)
SERVER_LIST_FILE = '{data_folder}/SERVER_ID.csv'.format(data_folder=DATA_FOLDER)
CATEGORY_FILE_FORMAT = '{categories_folder}/%s.csv'.format(categories_folder=CATEGORIES_FOLDER)
UNKNOWN_ID = -1
COLORS = [(.93, .11, .14, .75), (.63, .29, .64, .75), (.99, .80, .06, .75), (.00, .00, .00, .40), (.01, .89, .93, .75)]


def load_player_ids_sets(data_sets_file_paths):
    """Load lists of registered player ids in given data files."""
    print("Loading registered player ids from CSV files... ", end='', flush=True)
    player_ids_sets = []
    for data_set_file_paths in data_sets_file_paths:
        player_ids_set = []
        for data_file_path in data_set_file_paths:
            with open(data_file_path, 'r', newline='') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for _, player_id in csv_reader:
                    if player_id not in player_ids_set and player_id != str(UNKNOWN_ID):
                        player_ids_set.append(player_id)
        player_ids_sets.append(player_ids_set)
    print("Done. Loaded a total of %d valid account ids." % sum(len(_) for _ in player_ids_sets))
    return player_ids_sets


def plot_histogram(data_sets, stat_types, data_sets_names, zoom_on_preferred_window=False, *args):
    """Plot a set of statistics on an histogram."""
    BINS_IN_PREFERRED_WINDOW = 20
    stat_type = stat_types[0]
    preferred_lb, preferred_ub, mark_step = [stat_type[key] for key in ('preferred_lb', 'preferred_ub', 'mark_step')]
    exp_values_d = wn8_utils.get_exp_values_d() if stat_type['use_exp_values'] else None

    stats_array, bins_array, lb_array, ub_array = [], [], [], []
    for set_id, player_ids in enumerate(data_sets):
        stats_d = get_stats(set_id, player_ids, stat_type['stats_fetcher'], stat_type['short_name'], exp_values_d)
        if stats_d:
            stats_array.append(list(stats_d.values()))

            # Compute lower and upper bound of stats
            min_stat, max_stat = min(stats_d.values()), max(stats_d.values())
            lb = preferred_lb if zoom_on_preferred_window else int(math.floor(min_stat / mark_step) * mark_step)
            ub = preferred_ub if zoom_on_preferred_window else int(math.ceil(max_stat / mark_step) * mark_step)
            lb_array.append(lb)
            ub_array.append(ub)

            # Compute number of bins to approach that of preferred window
            bins_factor = (ub - lb) / (preferred_ub - preferred_lb)
            bins = BINS_IN_PREFERRED_WINDOW * bins_factor

            # Compute number of bins to adjust on marks
            marks = round((ub - lb) / mark_step)
            bins = marks if bins <= marks else round(bins / marks) * marks
            bins_array.append(bins)

    if bins_array:
        bins, lb, ub = max(bins_array), min(lb_array), max(ub_array)
        weights = [[len(stats_array[0])/len(stats_array[i]) for _ in range(len(stats_array[i]))] for i in range(len(stats_array))]
        colors = COLORS[:len(stats_array)] if len(stats_array) <= len(COLORS) else None
        labels = [', '.join(data_set_names) for data_set_names in data_sets_names]
        x_formatter = ticker.FuncFormatter(lambda x, pos: "{value}{sign}".format(value=int(x), sign=('%' if stat_type['is_precentage'] else '')))
        y_formatter = ticker.FuncFormatter(lambda y, pos: "{value}%".format(value=int((y * 100) / len(stats_array[0]))))

        plt.title("Distribution of players in regard to their {stat}".format(stat=stat_type['long_name']))
        plt.xlabel("{stat} of players".format(stat=stat_type['long_name']))
        plt.ylabel("Player Ratio")
        plt.gca().xaxis.set_major_formatter(x_formatter)
        plt.gca().yaxis.set_major_formatter(y_formatter)
        plt.hist(x=stats_array, bins=bins, range=[lb, ub], weights=weights, color=colors, label=labels, alpha=0.75, ec='black')
        plt.legend()
        plt.show()


def plot_scatter(data_sets, stat_types, data_sets_names, zoom_on_preferred_window=False, *args):
    """Plot a set of statistics on an scatter plot."""
    exp_values_d = wn8_utils.get_exp_values_d() if any(stat_type['use_exp_values'] for stat_type in stat_types) else None

    for set_id, player_ids in enumerate(data_sets):
        stats_d_array = []
        for axis, stat_type in enumerate(stat_types[:2]):
            axis_exp_values_d = exp_values_d if stat_type['use_exp_values'] else None
            stats_d = get_stats(set_id, player_ids, stat_type['stats_fetcher'], stat_type['short_name'], axis_exp_values_d)
            stats_d_array.append(stats_d)

        stats_d_x, stats_d_y = stats_d_array
        stats_x, stats_y = [], []
        for player_id in player_ids:
            if all(player_id in stats_d for stats_d in (stats_d_x, stats_d_y)):
                stats_x.append(stats_d_x[player_id])
                stats_y.append(stats_d_y[player_id])

        label = ', '.join(data_sets_names[set_id])
        color = COLORS[set_id] if set_id < len(COLORS) else None
        plt.scatter(x=stats_x, y=stats_y, label=label, c=color, marker='.', alpha=0.50)

    x_formatter = ticker.FuncFormatter(lambda x, pos: "{value}{sign}".format(value=int(x), sign=('%' if stat_types[0]['is_precentage'] else '')))
    y_formatter = ticker.FuncFormatter(lambda x, pos: "{value}{sign}".format(value=int(x), sign=('%' if stat_types[1]['is_precentage'] else '')))
    plt.title("Scatter plot of {stat0} versus {stat1} of players".format(stat0=stat_types[0]['long_name'], stat1=stat_types[1]['long_name']))
    plt.xlabel("{stat0} of players".format(stat0=stat_types[0]['long_name']))
    plt.ylabel("{stat1} of players".format(stat1=stat_types[1]['long_name']))
    plt.gca().xaxis.set_major_formatter(x_formatter)
    plt.gca().yaxis.set_major_formatter(y_formatter)
    if zoom_on_preferred_window:
        plt.xlim(stat_types[0]['preferred_lb'], stat_types[0]['preferred_ub'])
        plt.ylim(stat_types[1]['preferred_lb'], stat_types[1]['preferred_ub'])
    plt.legend()
    plt.show()


def plot_pie(data_sets, stat_types, data_set_names, *args):
    """Plot a set of statistics on an histogram."""
    EXPLODE_FACTOR = 0.1
    stat_type = stat_types[0]
    stats_count_array = []
    for set_id, player_ids in enumerate(data_sets):
        stats_d = get_stats(set_id, player_ids, stat_type['stats_fetcher'], stat_type['short_name'])
        stats_count = sum(stats_d.values())
        stats_count_array.append(stats_count)

    if sum(stats_count_array) > 0:
        colors = COLORS[:len(stats_count_array)] if len(stats_count_array) <= len(COLORS) else None
        labels = [', '.join(data_set_names) for data_set_names in data_sets_names]
        explode = [(1 - stats_count / sum(stats_count_array)) * EXPLODE_FACTOR for stats_count in stats_count_array]
        plt.title("Pie chart of the {stat} of players".format(stat=stat_type['long_name']))
        plt.pie(x=stats_count_array, colors=colors, labels=labels, explode=explode, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.tight_layout()
        plt.show()


def get_stats(set_id, player_ids, stats_fetcher, stat_name, exp_values_d=None):
    """Split the list of player ids in batches and get their stats."""
    stats_d = {}
    index, batches = 0, []
    while index < len(player_ids):
        batches.append(player_ids[index:min(index + BATCH_SIZE, len(player_ids))])
        index += len(batches[-1])
    for batch_id, batch in enumerate(batches):
        batch_d = stats_fetcher(batch, exp_values_d) if exp_values_d else stats_fetcher(batch)
        for player_id, stat in batch_d.items():
            stats_d[player_id] = stat
        progress = (batch_id + 1) / len(batches) * 100
        sys.stdout.write("\rCalculating %s for set #%d : %.2f %%" % (stat_name, set_id + 1, progress))
        sys.stdout.flush()
    print()
    return stats_d


def get_win_ratio_d(player_ids):
    """Compute the win ratio of a batch of players."""
    payload = {
        'application_id': APP_ID,
        'account_id': ','.join(player_ids),
        'fields': ','.join(['statistics.all.battles', 'statistics.all.wins'])
    }
    response = requests.get(ACCOUNT_INFO_REQUEST_URL, params=payload)
    response_content = response.json()

    win_ratio_d = {}
    if response_content['status'] == 'ok':
        for player_id in player_ids:
            player_data = response_content['data'][player_id]
            if player_data:
                player_stats = player_data['statistics']['all']
                battles = player_stats['battles']
                wins = player_stats['wins']
                win_ratio = (wins / battles) * 100 if battles > 0 else 0
                if win_ratio > 0:
                    win_ratio_d[player_id] = win_ratio
    return win_ratio_d


def get_wn8_d(player_ids, exp_values_d):
    """Compute the WN8 of a batch of players."""
    wn8_d = wn8_utils.calculate_wn8(player_ids, exp_values_d, APP_ID)
    return wn8_d


def get_count_d(player_ids):
    """Compute the count of a batch of players."""
    count_d = {player_id: 1 for player_id in player_ids}
    return count_d


GRAPH_TYPES = {
    'hist': {
        'plotter': plot_histogram,
        'name': "histogram",
        'axis': ['x'],
        'allowed_stats': ['wr', 'wn8'],
        'min_data_sets_number': 1,
        'max_data_sets_number': 5,
        'is_zoomable': True,
    },
    'scatter': {
        'plotter': plot_scatter,
        'name': "scatter plot",
        'axis': ['x', 'y'],
        'allowed_stats': ['wr', 'wn8'],
        'min_data_sets_number': 1,
        'max_data_sets_number': 5,
        'is_zoomable': True
    },
    'pie': {
        'plotter': plot_pie,
        'name': "pie chart",
        'axis': ['circle'],
        'allowed_stats': ['count'],
        'min_data_sets_number': 1,
        'max_data_sets_number': 10,
        'is_zoomable': False
    }
}
STAT_TYPES = {
    'wr': {
        'stats_fetcher': get_win_ratio_d,
        'short_name': "WR",
        'long_name': "win ratio",
        'use_exp_values': False,
        'is_precentage': True,
        'preferred_lb': 40,
        'preferred_ub': 75,
        'mark_step': 5
    },
    'wn8': {
        'stats_fetcher': get_wn8_d,
        'short_name': "WN8",
        'long_name': "WN8",
        'use_exp_values': True,
        'is_precentage': False,
        'preferred_lb': 0,
        'preferred_ub': 3500,
        'mark_step': 500
    },
    'count': {
        'stats_fetcher': get_count_d,
        'short_name': "count",
        'long_name': "count",
    }
}

if __name__ == "__main__":
    input("The module player_profiler helps you plotting statistics of players "
          "whose account id has been registered by the previous modules.\n"
          "You will be asked to choose the type of the graph you want to plot "
          "the statistics on and, depending on your choice, the number of data "
          "sets to superpose on the same graph.\n"
          "Each data set is composed of at least one data file (which you will "
          "also be able to select to your liking) and a data file is a list of "
          "account ids produced by the previous modules.\n\n"
          "Press ENTER to continue (or CTRL + C + ENTER to abort).\n")

    APP_ID = ui_utils.load_app_id(CONFIG_FILE, APP_ID)
    ui_utils.prepare_folders(DATA_FOLDER, CATEGORIES_FOLDER)
    ui_utils.prepare_files(DATA_FOLDER, SERVER_LIST_FILE, ZLIST_FILE)

    graph_properties = ui_utils.select_graph_type(
        [(properties['name'], properties) for properties in GRAPH_TYPES.values()]
    )
    stat_types = []
    if len(graph_properties['axis']) == 1:
        stat_types.append(ui_utils.select_stat_type(
            [(properties['long_name'], properties) for id, properties in STAT_TYPES.items() if id in graph_properties['allowed_stats']]
        ) if len(graph_properties['allowed_stats']) > 1 else STAT_TYPES[graph_properties['allowed_stats'][0]])
    else:
        for axis in graph_properties['axis']:
            stat_types.append(ui_utils.select_stat_type(
                [(properties['long_name'], properties) for id, properties in STAT_TYPES.items() if id in graph_properties['allowed_stats']], axis
            ) if len(graph_properties['allowed_stats']) > 1 else STAT_TYPES[graph_properties['allowed_stats'][0]])
    data_sets_number = ui_utils.select_data_sets_number(
        graph_properties['min_data_sets_number'], graph_properties['max_data_sets_number']
    )
    data_sets_names, data_sets_files = [], []
    for data_set_id in range(data_sets_number):
        data_set_names, data_set_files = [], []
        data_options = ui_utils.select_data_files(data_set_id, CATEGORIES_FOLDER, SERVER_LIST_FILE, ZLIST_FILE)
        for name, file in data_options:
            data_set_names.append(name)
            data_set_files.append(file)
        data_sets_names.append(data_set_names)
        data_sets_files.append(data_set_files)
    zoom_on_preferred_window = ui_utils.select_zoom_option(
        ('zoom', True),
        ('do nothing', False)
    ) if graph_properties['is_zoomable'] else False

    data_sets = load_player_ids_sets(data_sets_files)
    graph_properties['plotter'](data_sets, stat_types, data_sets_names, zoom_on_preferred_window)
