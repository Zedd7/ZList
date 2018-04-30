# -*- coding: utf-8 -*-

"""Categorize players according to the color of their assigned PNG file."""

import os
import sys
import csv

import image_utils
import ui_utils

ZLIST_FOLDER = '../../res/zlist'
DATA_FOLDER = '../../data'
CATEGORIES_FOLDER = '{data_folder}/categories'.format(data_folder=DATA_FOLDER)
ZLIST_FILE = '{data_folder}/ZLIST.csv'.format(data_folder=DATA_FOLDER)
CATEGORY_FILE_FORMAT = '{categories_folder}/%s.csv'.format(categories_folder=CATEGORIES_FOLDER)
MAIN_CATEGORIES = ['ASSHOLE', 'CAMPER', 'GOLD', 'REROLL', 'TEAMKILL']


def load_player_ids():
    """Load a dictionary of known mappings for player names and their id."""
    print("Loading registered player ids from CSV file... ", end='', flush=True)
    player_ids = {}
    with open(ZLIST_FILE, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for player_name, player_id in csv_reader:
            player_ids[player_name] = player_id
    print("Done.")
    return player_ids


def get_player_image_d(should_repair_images=False):
    """Load the PNG file assigned to each player."""
    player_image_d, repaired_image_file_name_d = {}, {}
    file_names = os.listdir(ZLIST_FOLDER)
    for index, file_name in enumerate(file_names):
        if file_name[0] != '.':
            player_name = file_name.rstrip('.png')
            image, repaired = image_utils.get_player_image(ZLIST_FOLDER, file_name)
            player_image_d[player_name] = image
            if repaired:
                repaired_image_file_name_d[file_name] = image
        progress = (index + 1) / len(file_names) * 100
        sys.stdout.write("\rLoading and repairing image files: %.2f %%" % progress)
        sys.stdout.flush()
    print()

    index, repair_count = 0, len(repaired_image_file_name_d)
    if should_repair_images and repair_count > 0:
        for file_name, image in repaired_image_file_name_d.items():
            image.save(os.path.join(ZLIST_FOLDER, file_name))
            progress = (index + 1) / repair_count * 100
            sys.stdout.write("\rRegistering repaired image files: %.2f %%" % progress)
            sys.stdout.flush()
            index += 1
        print()
    return player_image_d


def get_player_categories_d(player_image_d, category_palette):
    """Identify the categories of players."""
    player_categories_d = {}
    index, player_count = 0, len(player_image_d)
    for player_name, player_image in player_image_d.items():
        categories = image_utils.get_player_categories(player_image, category_palette)
        player_categories_d[player_name] = categories
        progress = (index + 1) / player_count * 100
        sys.stdout.write("\rIdentifying player categories: %.2f %%" % progress)
        sys.stdout.flush()
        index += 1
    print()
    return player_categories_d


def register_player_categories(player_categories_d, player_ids, use_complex_categories=False):
    """Register identified player categories to CSV file."""
    print("Registering player categories to CSV file... ", end='', flush=True)
    categories_d = {}
    if not use_complex_categories:  # Register players in main category CSV files only
        for player_name, player_categories in player_categories_d.items():
            for player_category in player_categories:
                if player_category not in categories_d:
                    categories_d[player_category] = []
                categories_d[player_category].append(player_name)
    else:  # Register players in exact complex category CSV files
        for player_name, player_categories in player_categories_d.items():
            complex_player_category = '_'.join(sorted(player_categories))
            if complex_player_category not in categories_d:
                categories_d[complex_player_category] = []
            categories_d[complex_player_category].append(player_name)

    for category, player_names in categories_d.items():
        category_file_path = CATEGORY_FILE_FORMAT % category
        with open(category_file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            for player_name in sorted(player_names, key=str.lower):
                if player_name in player_ids:
                    csv_writer.writerow([player_name, player_ids[player_name]])
    print("Done.")


if __name__ == '__main__':
    input("The module player_categorizer relies on the colours of the PNG file "
          "associated with the name of a player to determine the category of "
          "the latter.\n"
          "It handles altered image files (some pixels may see their color "
          "change when the file is copied or moved) and custom categories if "
          "you wish to extend this list by yourself.\n"
          "Avalaible categories are associated with a PNG file whose name "
          "follows the format '.CATEGORY.png'.\n"
          "You will be asked to choose between replacing altered image files "
          "with their repaired version (speed up next executions of this script) "
          "or leave them unchanged (skip this step).\n"
          "You will also be asked to choose between sorting players according to "
          "their main category (if a player has more than one category, he will "
          "be listed in more than one file) or sorting them according to their "
          "composite category (combinaison of the main categories of the player).\n\n"
          "Press ENTER to continue (or CTRL + C + ENTER to abort).\n")

    ui_utils.prepare_files(DATA_FOLDER, ZLIST_FILE)
    ui_utils.prepare_folders(CATEGORIES_FOLDER, clean=True)

    should_repair_images = ui_utils.select_repair_option(
        ('save repaired images', True),
        ('do nothing', False)
    )
    use_complex_categories = ui_utils.select_category_option(
        ('use main categories only', False),
        ('use composite categories', True)
    )

    player_ids = load_player_ids()
    category_palette = image_utils.get_category_palette(ZLIST_FOLDER, MAIN_CATEGORIES)
    player_image_d = get_player_image_d(should_repair_images)
    player_categories_d = get_player_categories_d(player_image_d, category_palette)
    register_player_categories(player_categories_d, player_ids, use_complex_categories)
