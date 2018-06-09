# -*- coding: utf-8 -*-

"""Generate graphs of player stats."""

import sys
import math
import csv

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import requests

import stat_enum
import ui_utils
import wn8_utils

CONFIG_FILE = '../../res/config.txt'
APP_ID = 'demo'
ACCOUNT_INFO_REQUEST_URL = 'https://api.worldoftanks.eu/wot/account/info/'
BATCH_SIZE = 100
DATA_FOLDER = '../../data'
CATEGORIES_FOLDER = '{data_folder}/categories'.format(data_folder=DATA_FOLDER)
CATEGORY_FILE_FORMAT = '{categories_folder}/%s.csv'.format(categories_folder=CATEGORIES_FOLDER)
UNKNOWN_ID = -1
COLORS = [
    (.93, .11, .14, .75),  # Red
    (.63, .29, .64, .75),  # Purple
    (.99, .80, .06, .75),  # Yellow
    (.00, .00, .00, .40),  # Black
    (.01, .89, .93, .75)   # Cyan
]
COLORS = []  # Comment out to use predefined colors


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
        stats_d = get_stats(stat_type, set_id, None, player_ids, exp_values_d)
        if stats_d:
            stats_array.append(list(stats_d.values()))

            # Compute lower and upper bound of stats
            min_stat, max_stat = min(stats_d.values()), max(stats_d.values())
            lb = preferred_lb if zoom_on_preferred_window and preferred_lb != 0 else int(math.floor(math.floor(min_stat / mark_step) * mark_step))
            ub = preferred_ub if zoom_on_preferred_window and preferred_ub != 0 else int(math.ceil(math.ceil(max_stat / mark_step) * mark_step))
            lb_array.append(lb)
            ub_array.append(ub)

            # Compute number of bins to approach that of preferred window
            bins_factor = None
            if preferred_lb < preferred_ub:
                bins_factor = (ub - lb) / (preferred_ub - preferred_lb)
            else:
                bins_factor = 1
            bins = BINS_IN_PREFERRED_WINDOW * bins_factor

            # Compute number of bins to adjust on marks
            marks = round((ub - lb) / mark_step)
            bins = marks if bins <= marks else round(bins / marks) * marks
            bins_array.append(bins)

    if bins_array:
        bins, lb, ub = max(bins_array), min(lb_array), max(ub_array)
        bin_range = [lb, ub] if lb < ub else None
        weights = [[len(stats_array[0])/len(stats_array[i]) for _ in range(len(stats_array[i]))] for i in range(len(stats_array))]
        colors = COLORS[:len(stats_array)] if len(stats_array) <= len(COLORS) else None
        labels = [', '.join(data_set_names) for data_set_names in data_sets_names]
        x_formatter = ticker.FuncFormatter(lambda x, pos: "{value}{sign}".format(value=int(x), sign=('%' if stat_type['is_percentage'] else '')))
        y_formatter = ticker.FuncFormatter(lambda y, pos: "{value}%".format(value=int((y * 100) / len(stats_array[0]))))

        plt.title("Distribution of players in regard to their {stat}".format(stat=stat_type['long_name']))
        plt.xlabel("{stat} of players".format(stat=stat_type['long_name']))
        plt.ylabel("player ratio")
        plt.gca().xaxis.set_major_formatter(x_formatter)
        plt.gca().yaxis.set_major_formatter(y_formatter)
        plt.hist(x=stats_array, bins=bins, range=bin_range, weights=weights, color=colors, label=labels, alpha=0.75, ec='black')
        plt.legend()
        plt.show()


def plot_scatter(data_sets, stat_types, data_sets_names, zoom_on_preferred_window=False, *args):
    """Plot a set of statistics on an scatter plot."""
    exp_values_d = wn8_utils.get_exp_values_d() if any(stat_type['use_exp_values'] for stat_type in stat_types) else None
    lb_x, ub_x = stat_types[0]['preferred_lb'], stat_types[0]['preferred_ub']
    lb_y, ub_y = stat_types[1]['preferred_lb'], stat_types[1]['preferred_ub']

    for set_id, player_ids in enumerate(data_sets):
        stats_d_array = []
        for axis, stat_type in enumerate(stat_types[:2]):
            axis_exp_values_d = exp_values_d if stat_type['use_exp_values'] else None
            stats_d = get_stats(stat_type, set_id, None, player_ids, axis_exp_values_d)
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

    stat_x_name, stat_y_name = stat_types[0]['long_name'], stat_types[1]['long_name']
    x_formatter = ticker.FuncFormatter(lambda x, pos: "{value}{sign}".format(value=int(x), sign=('%' if stat_types[0]['is_percentage'] else '')))
    y_formatter = ticker.FuncFormatter(lambda x, pos: "{value}{sign}".format(value=int(x), sign=('%' if stat_types[1]['is_percentage'] else '')))
    plt.title("Scatter plot of {stat1} versus {stat0} of players".format(stat0=stat_x_name, stat1=stat_y_name))
    plt.xlabel("{stat0} of players".format(stat0=stat_x_name))
    plt.ylabel("{stat1} of players".format(stat1=stat_y_name))
    plt.gca().xaxis.set_major_formatter(x_formatter)
    plt.gca().yaxis.set_major_formatter(y_formatter)
    if zoom_on_preferred_window:
        if lb_x < ub_x:
            plt.xlim(stat_types[0]['preferred_lb'], stat_types[0]['preferred_ub'])
        if lb_y < ub_y:
            plt.ylim(stat_types[1]['preferred_lb'], stat_types[1]['preferred_ub'])
    plt.legend()
    plt.show()


def plot_pie(data_sets, stat_types, data_sets_names, *args):
    """Group players by statistic value on a pie chart."""
    EXPLODE_FACTOR = 0.1
    stat_type = stat_types[0]

    stat_count_d = {}
    for set_id, player_ids in enumerate(data_sets):
        set_name = ', '.join(data_sets_names[set_id])
        stats_d = get_stats(stat_type, set_id, set_name, player_ids)
        for player_id, stat in stats_d.items():
            if stat not in stat_count_d:
                stat_count_d[stat] = 0
            stat_count_d[stat] += 1

    if stat_count_d:
        # Merge smaller groups
        for stat in list(stat_count_d.keys()):
            count = stat_count_d[stat]
            if count / sum(stat_count_d.values()) < 0.05:
                if 'other' not in stat_count_d:
                    stat_count_d['other'] = 0
                stat_count_d['other'] += count
                del stat_count_d[stat]

        groups = stat_count_d.keys()
        if stat_type['sort_by_count']:
            groups = sorted(groups, key=lambda group: stat_count_d[group])
        else:
            groups = sorted(groups)
        counts = [stat_count_d[group] for group in groups]
        colors = COLORS[:len(groups)] if len(groups) <= len(COLORS) else None
        labels = [group.upper() for group in groups]
        explodes = [(1 - count / sum(counts)) * EXPLODE_FACTOR for group, count in zip(groups, counts)]
        plt.title("Pie chart of the {stat} of players".format(stat=stat_type['long_name']))
        plt.pie(x=counts, colors=colors, labels=labels, explode=explodes, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.tight_layout()
        plt.show()


def get_stats(stat_type, set_id, set_name, player_ids, exp_values_d=None):
    """Split the list of player ids in batches and get their stats."""
    stats_fetcher, stat_name = stat_type['stats_fetcher'], stat_type['short_name']
    stats_d = {}
    index, batches = 0, []
    while index < len(player_ids):
        batches.append(player_ids[index:min(index + BATCH_SIZE, len(player_ids))])
        index += len(batches[-1])
    for batch_id, batch in enumerate(batches):
        batch_d = {}
        if stat_type['use_exp_values']:
            batch_d = stats_fetcher(batch, exp_values_d, APP_ID)
        elif stat_type['group_by_value']:
            batch_d = stats_fetcher(batch, stat_type, APP_ID, set_name)
        else:
            batch_d = stats_fetcher(batch, stat_type, APP_ID)
        for player_id, stat in batch_d.items():
            stats_d[player_id] = stat
        progress = (batch_id + 1) / len(batches) * 100
        sys.stdout.write("\rCalculating %s for set #%d : %.2f %%" % (stat_name, set_id + 1, progress))
        sys.stdout.flush()
    print()
    return stats_d


def get_wn8_d(player_ids, exp_values_d, app_id):
    """Compute the WN8 of a batch of players."""
    wn8_d = wn8_utils.calculate_wn8(player_ids, exp_values_d, app_id)
    return wn8_d


def get_total_stat_d(player_ids, stat_type, app_id):
    """Compute the total stat of a batch of players."""
    return get_stat_d(player_ids, stat_type, stat_type['field'], app_id)


def get_average_stat_d(player_ids, stat_type, app_id):
    """Compute the average stat of a batch of players."""
    fields = ','.join([stat_type['field'], stat_type['dependency_field']])
    return get_stat_d(player_ids, stat_type, fields, app_id, compute_ratio=True, per_shot=False)


def get_per_shot_stat_d(player_ids, stat_type, app_id):
    """Compute the average stat per shot of a batch of players."""
    fields = ','.join([stat_type['field'], stat_type['dependency_field']])
    return get_stat_d(player_ids, stat_type, fields, app_id, compute_ratio=False, per_shot=True)


def get_count_d(player_ids, stat_type, app_id, set_name):
    """Compute the count of a batch of players for a given set."""
    count_d = {player_id: set_name for player_id in player_ids}
    return count_d


def get_language_d(player_ids, stat_type, app_id, set_name):
    """Compute the count of a batch of players for a given set."""
    return get_stat_d(player_ids, stat_type, stat_type['field'], app_id)


def get_stat_d(player_ids, stat_type, fields, app_id, compute_ratio=False, per_shot=False):
    """Compute the stat of a batch of players."""
    payload = {
        'application_id': app_id,
        'account_id': ','.join(player_ids),
        'fields': fields
    }
    response = requests.get(ACCOUNT_INFO_REQUEST_URL, params=payload)
    response_content = response.json()

    stat_d = {}
    if response_content['status'] == 'ok':
        for player_id in player_ids:
            player_data = response_content['data'][player_id]
            if player_data:
                stat = get_nested_stat(stat_type['field'], player_data)
                if compute_ratio:
                    battles = get_nested_stat(stat_type['dependency_field'], player_data)
                    average_stat = stat / battles if battles > 0 else 0
                    if stat_type['is_percentage']:
                        average_stat *= 100
                    if average_stat > 0:
                        stat_d[player_id] = average_stat
                elif per_shot:
                    shots = get_nested_stat(stat_type['dependency_field'], player_data)
                    per_shot_stat = stat / shots if shots > 0 else 0
                    if stat_type['is_percentage']:
                        per_shot_stat *= 100
                    if per_shot_stat > 0:
                        stat_d[player_id] = per_shot_stat
                else:
                    stat_d[player_id] = stat
    return stat_d


def get_nested_stat(nested_field, player_data):
    """Get the stat for the given nested field."""
    stat = player_data
    for field_part in nested_field.split('.'):
        stat = stat[field_part]
    return stat


GRAPH_TYPES = {
    'hist': {
        'plotter': plot_histogram,
        'name': "histogram",
        'axis': ['x'],
        'allowed_stats': ['battles', 'wn8', 'global_rating', 'wr', 'avg_xp',
                          'avg_damage', 'avg_assist', 'avg_blocked', 'avg_kill',
                          'avg_spot', 'hit_ratio', 'avg_capture', 'avg_defense',
                          'splash_ratio'],
        'min_data_sets_number': 1,
        'max_data_sets_number': 5,
        'is_zoomable': True,
    },
    'scatter': {
        'plotter': plot_scatter,
        'name': "scatter plot",
        'axis': ['x', 'y'],
        'allowed_stats': ['battles', 'wn8', 'global_rating', 'wr', 'avg_xp',
                          'avg_damage', 'avg_assist', 'avg_blocked', 'avg_kill',
                          'avg_spot', 'hit_ratio', 'avg_capture', 'avg_defense',
                          'splash_ratio'],
        'min_data_sets_number': 1,
        'max_data_sets_number': 5,
        'is_zoomable': True
    },
    'pie': {
        'plotter': plot_pie,
        'name': "pie chart",
        'axis': ['circle'],
        'allowed_stats': ['count', 'language'],
        'min_data_sets_number': 1,
        'max_data_sets_number': 10,
        'is_zoomable': False
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

    graph_properties = ui_utils.select_graph_type(
        [(properties['name'], properties) for properties in GRAPH_TYPES.values()]
    )
    stat_types = []
    for axis in graph_properties['axis']:
        stat_types.append(ui_utils.select_stat_type(
            [(properties['long_name'], properties) for id, properties in stat_enum.STATS.items() if id in graph_properties['allowed_stats']], axis
        ) if len(graph_properties['allowed_stats']) > 1 else stat_enum.STATS[graph_properties['allowed_stats'][0]])
    data_sets_number = ui_utils.select_data_sets_number(
        graph_properties['min_data_sets_number'], graph_properties['max_data_sets_number']
    )
    data_sets_names, data_sets_files = [], []
    for data_set_id in range(data_sets_number):
        data_set_names, data_set_files = [], []
        data_options = ui_utils.select_data_files(data_set_id, CATEGORIES_FOLDER, DATA_FOLDER)
        for name, file in data_options:
            data_set_names.append(name)
            data_set_files.append(file)
        data_sets_names.append(data_set_names)
        data_sets_files.append(data_set_files)
    zoom_on_preferred_window = ui_utils.select_zoom_option(
        ('zoom', True),
        ('do nothing', False)
    ) if graph_properties['is_zoomable'] and any(stat_type['preferred_lb'] < stat_type['preferred_ub'] for stat_type in stat_types) else False

    data_sets = load_player_ids_sets(data_sets_files)
    graph_properties['plotter'](data_sets, stat_types, data_sets_names, zoom_on_preferred_window)
