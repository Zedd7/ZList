# -*- coding: utf-8 -*-

"""Provide UI functions for the console."""

import os


def load_app_id(config_file, default_app_id):
    """Load a custom WG application ID from config."""
    app_id = None
    if os.path.exists(config_file):
        with open(config_file, 'r') as config:
            app_id_line = config.readline().rstrip()
            if (len(app_id_line.split('=')) == 2 and
                    app_id_line.split('=')[0] == 'WG_API_APPLICATION_ID' and
                    app_id_line.split('=')[1] != default_app_id):
                app_id = app_id_line.split('=')[1]
    if app_id:
        print("New application id loaded from config: {id}".format(id=app_id))
    else:
        print("No custom application id could be found in",
              "{config}.".format(config=os.path.abspath(config_file)), '\n'
              "The default id will be used but the number of requests to",
              "WG API will be limited and the results may be truncated.")
    return app_id


def prepare_folders(*folders, clean=False):
    """Create the folders if not already done."""
    for folder in folders:
        if not os.path.isdir(folder):
            os.makedirs(folder)
        if clean:
            for file in os.listdir(folder):
                os.remove(os.path.join(folder, file))


def prepare_files(folder, *files):
    """Create the folder and the file if not already done."""
    prepare_folders(folder)
    for file in files:
        if not os.path.exists(file):
            open(file, "w").close()


def select_simple_option(options, menu_prompt, type, recommended):
    """Prompt a menu for the selection of a simple option."""
    selection = -1
    print(menu_prompt)
    for i, option in enumerate(options):
        print("  {number} : {name}".format(number=(i + 1), name=option[0]))
    while selection not in range(1, len(options) + 1):
        try:
            selection = int(input("Number of the selection (recommended: %d) : " % recommended))
            if selection not in range(1, len(options) + 1):
                raise ValueError
        except:
            print("The value must be the number of a {type}.".format(type=type))
    value = options[selection - 1][1]
    return value


def select_search_mode(*search_modes):
    """Prompt a menu for the selection of the search mode."""
    return select_simple_option(
        search_modes,
        "Choose the search mode for account id testing among the followings:",
        "search mode",
        2
    )


def select_offset_option(*offset_options):
    """Prompt a menu for the selection of the offset option."""
    return select_simple_option(
        offset_options,
        "Choose between deterministic or random search:",
        "search method",
        2
    )


def select_repair_option(*repair_options):
    """Prompt a menu for the selection of the repair option."""
    return select_simple_option(
        repair_options,
        "Should repaired image files be registered ?",
        "repair option",
        1
    )


def select_category_option(*category_options):
    """Prompt a menu for the selection of the category option."""
    return select_simple_option(
        category_options,
        "Should categorization take composite categories into account ?",
        "repair option",
        1
    )


def select_graph_type(*graph_types):
    """Prompt a menu for the selection of the graph type."""
    return select_simple_option(
        graph_types,
        "On which type of graph would you like to plot player statistics ?",
        "graph type",
        1
    )


def select_zoom_option(*zoom_options):
    """Prompt a menu for the selection of the zoom option."""
    return select_simple_option(
        zoom_options,
        "Choose between zooming on recommended window or not:",
        "zoom option",
        1
    )


def select_stat_type(stat_types):
    """Prompt a menu for the selection of the stat type."""
    return select_simple_option(
        stat_types,
        "What statistic should be plotted on the graph ?",
        "statistic type",
        1
    )


def select_data_sets_number(min_data_sets=1, max_data_sets=1):
    """Prompt a menu for the selection of the number of data sets."""
    if min_data_sets == max_data_sets:
        return min_data_sets
    data_sets_number = -1
    print("Specify the number of data sets to use (between {min} and {max}).".format(min=min_data_sets, max=max_data_sets))
    while data_sets_number not in range(min_data_sets, max_data_sets + 1):
        try:
            data_sets_number = int(input("Number of data sets : "))
            if data_sets_number not in range(min_data_sets, max_data_sets + 1):
                raise ValueError
        except:
            print("The number must be between {min} and {max}.".format(min=min_data_sets, max=max_data_sets))
    return data_sets_number


def select_data_files(data_set_id, data_folder, *extra_files):
    """Prompt a menu for the selection of data files."""
    categories = [(file_name.rstrip('.csv'), os.path.join(data_folder, file_name)) for file_name in os.listdir(data_folder)]
    extras_options = [(os.path.basename(file_path).rstrip('_ID.csv'), file_path) for file_path in extra_files]
    data_options = categories + extras_options
    data_option_selection, data_files = -1, []
    print("Select one or several data files to include to the data set # %d." % (data_set_id + 1))
    print("  {number} : {name}".format(number=0, name="Finish selection"))
    for i, data_option in enumerate(data_options):
        print("  {number} : {name}".format(number=(i + 1), name=data_option[0]))
    while data_option_selection != 0:
        try:
            data_option_selection = int(input("Number of the selection : "))
            if data_option_selection not in range(0, len(data_options) + 1):
                raise ValueError
            if data_option_selection == 0:
                data_file_names = ', '.join([data_option[0] for data_option in data_files])
                print("Selected data file(s) :", data_file_names if data_file_names else "none")
            elif data_options[data_option_selection - 1] not in data_files:
                data_files.append(data_options[data_option_selection - 1])
        except:
            print("The value must be the number of a data file, or 0 to finish.")
    return data_files
