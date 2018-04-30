# -*- coding: utf-8 -*-

"""Add players listed by the Gold Logger mod to the ZList."""

import os
import csv

import image_utils
import ui_utils

GAME_FOLDER = 'C:/Games/World of Tanks'
GOLD_USER_FILE = '{folder}/GOLD_USER.csv'.format(folder=GAME_FOLDER)
ZLIST_FOLDER = '{folder}/res_mods/mods/shared_resources/xvm/res/clanicons/EU/nick'.format(folder=GAME_FOLDER)
MAIN_CATEGORIES = ['ASSHOLE', 'CAMPER', 'GOLD', 'REROLL', 'TEAMKILL']
MANDATORY_CATEGORY = 'GOLD'


def load_logged_players():
    """Load a dictionary of the name and id of logged players."""
    print("Loading logged players from CSV file... ", end='', flush=True)
    player_ids = {}
    with open(GOLD_USER_FILE, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for player_name, player_id in csv_reader:
            player_ids[player_name] = player_id
    print("Done.")
    return player_ids


def get_player_files(logged_players, category_palette):
    """Get the base file corresponding to the new category code of players."""
    print("Loading existing players' image files... ", end='', flush=True)
    player_files, category_code_files = {}, {}
    player_file_names = os.listdir(ZLIST_FOLDER)
    for player_name in logged_players:
        player_file_name = '{player}.png'.format(player=player_name)
        fixed_player_file_name = get_player_file_name(player_file_name, player_file_names)
        if player_file_name != fixed_player_file_name:
            player_file_name = fixed_player_file_name
            player_name = fixed_player_file_name.rstrip('.png')

        category_code = get_category_code(player_file_name, player_file_names, category_palette)
        category_code_file_name = '.{code}.png'.format(code=category_code)
        category_code_file_path = os.path.join(ZLIST_FOLDER, category_code_file_name)
        player_files[player_name] = (player_file_name, category_code_file_name)
        if category_code_file_name not in category_code_files and os.path.isfile(category_code_file_path):
            category_code_file, _ = image_utils.get_player_image(ZLIST_FOLDER, category_code_file_name)
            category_code_files[category_code_file_name] = category_code_file
    print("Done.")
    return player_files, category_code_files


def get_player_file_name(player_file_name, player_file_names):
    """Return the name of the file of the player in the same case as in the list."""
    for file_name in player_file_names:
        if file_name.lower() == player_file_name.lower():
            return file_name
    return player_file_name


def get_category_code(player_file_name, player_file_names, category_palette):
    """Get the concatened string of player's categories."""
    categories = []
    if player_file_name in player_file_names:
        image, _ = image_utils.get_player_image(ZLIST_FOLDER, player_file_name)
        categories += image_utils.get_player_categories(image, category_palette)
    if MANDATORY_CATEGORY not in categories:
        categories.append(MANDATORY_CATEGORY)
    category_code = ''.join(sorted(categories))
    return category_code


def register_player_files(player_files, category_code_files):
    """Register player files in the ZList."""
    print("Registering player files in the ZList... ", end='', flush=True)
    unprocessed_player_names, missing_category_code_files = [], []
    for player_name in player_files:
        player_file_name, category_code_file_name = player_files[player_name]
        if category_code_file_name in category_code_files:
            player_file_path = os.path.join(ZLIST_FOLDER, player_file_name)
            category_code_file = category_code_files[category_code_file_name]
            category_code_file.save(player_file_path)
        else:
            unprocessed_player_names.append(player_name)
            if category_code_file_name not in missing_category_code_files:
                missing_category_code_files.append(category_code_file_name)
    if not unprocessed_player_names:
        print("Done. Logged {passing} players.".format(passing=(len(player_files))))
    else:
        print("Done. Logged {passing} players, ommited {omitted} due to following missing category files :".format(
            passing=(len(player_files) - len(unprocessed_player_names)), omitted=len(unprocessed_player_names)
        ))
        for category_code_file_name in sorted(missing_category_code_files):
            print("  {file_name}".format(file_name=category_code_file_name))
    return unprocessed_player_names


def clear_log_file(logged_players, unprocessed_player_names):
    """Clear the log file and eventually leaves unprocessed players."""
    print("Clearing added players from log file... ", end='', flush=True)
    unprocessed_players = {player_name: logged_players[player_name] for player_name in unprocessed_player_names}
    with open(GOLD_USER_FILE, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        for player_name in sorted(unprocessed_players.keys()):
            csv_writer.writerow([player_name, unprocessed_players[player_name]])
    print("Done.")


if __name__ == '__main__':
    input("The module player_logger adds players listed by the Gold Logger mod "
          "to the ZList used by the game client (not the one included in this) "
          "release.\n"
          "You will be asked to choose between removing from log file player "
          "names that have been successfully added to the ZList or not.\n"
          "If you wish to target the ZList made available with this release, "
          "you must edit the paths at the beginning of this script.\n\n"
          "Press ENTER to continue (or CTRL + C + ENTER to abort).\n")

    ui_utils.prepare_files(GAME_FOLDER, GOLD_USER_FILE)
    ui_utils.prepare_folders(ZLIST_FOLDER)

    should_remove_added_players = ui_utils.select_repair_option(
        ('remove added players', True),
        ('do nothing', False)
    )

    logged_players = load_logged_players()
    category_palette = image_utils.get_category_palette(ZLIST_FOLDER, MAIN_CATEGORIES)
    player_files, category_code_files = get_player_files(logged_players, category_palette)
    unprocessed_player_names = register_player_files(player_files, category_code_files)
    if should_remove_added_players:
        clear_log_file(logged_players, unprocessed_player_names)
