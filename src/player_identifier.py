# -*- coding: utf-8 -*-

"""Map players' names to their account id in a CSV file."""

import os
import sys
import csv

import requests

import ui_utils

CONFIG_FILE = '../res/config.txt'
APP_ID = 'demo'
ACCOUNT_INFO_REQUEST_URL = 'https://api.worldoftanks.eu/wot/account/list/'
BATCH_SIZE = 100
ZLIST_FOLDER = '../res_mods/mods/shared_resources/xvm/res/clanicons/EU/nick'
DATA_FOLDER = '../data'
CSV_FILE = '{folder}/ZLIST.csv'.format(folder=DATA_FOLDER)
UNKNOWN_ID = -1


def get_player_names():
    """Extract player names from ZList."""
    print("Extracting player names from ZList... ", end='', flush=True)
    player_names = []
    for file_name in os.listdir(ZLIST_FOLDER):
        if not file_name.startswith('.'):  # Is not a category file
            player_names.append(file_name.rstrip('.png'))
    print("Done.")
    return player_names


def get_player_ids(player_names):
    """Get account id of players."""
    # Retrieve previously registered player ids
    player_ids = load_player_ids()
    index, player_count = 0, len(player_names)
    while index < len(player_names):
        batch = []
        while len(batch) < BATCH_SIZE and index < len(player_names):
            player_name = player_names[index]
            if player_name not in player_ids:
                batch.append(player_name)
            index += 1
        if batch:
            batch_ids = fetch_player_ids(batch)
            for player_name, player_id in batch_ids.items():
                player_ids[player_name] = player_id
        progress = index / player_count * 100
        sys.stdout.write("\rRequesting player ids: %.2f %%" % progress)
        sys.stdout.flush()
    print()
    return player_ids


def load_player_ids():
    """Load dictionary of known mappings for player names and their id."""
    print("Loading registered player ids from CSV file... ", end='', flush=True)
    player_ids = {}
    with open(CSV_FILE, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for player_name, player_id in csv_reader:
            player_ids[player_name] = player_id
    print("Done.")
    return player_ids


def fetch_player_ids(player_names):
    """Retrieve the ids of a batch of players."""
    payload = {
        'application_id': APP_ID,
        'search': ','.join(player_names),
        'type': 'exact'
    }
    response = requests.get(ACCOUNT_INFO_REQUEST_URL, params=payload)
    response_content = response.json()

    player_ids = {player: UNKNOWN_ID for player in player_names}
    if response_content['status'] == 'ok':
        for player_data in response_content['data']:
            player = get_player_name(player_data['nickname'], player_names)
            player_id = player_data['account_id']
            player_ids[player] = player_id
    return player_ids


def get_player_name(player_name, player_names):
    """Return the name of the player in the same case as in the list."""
    for player in player_names:
        if player.lower() == player_name.lower():
            return player
    return player_name


def register_player_ids(player_ids):
    """Register player ids in CSV file."""
    print("Registering player ids to CSV file... ", end='', flush=True)
    with open(CSV_FILE, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        for player in sorted(player_ids.keys(), key=str.lower):
            csv_writer.writerow([player, player_ids[player]])
    print("Done.")


if __name__ == '__main__':
    input("The module player_identifier connects to the WG API to retrieve "
          "the account ids of listed players.\n"
          "They are then registered to file and ready to be used by following scripts.\n\n"
          "Press ENTER to continue (or CTRL + C + ENTER to abort).\n")

    APP_ID = ui_utils.load_app_id(CONFIG_FILE, APP_ID)
    ui_utils.prepare_folders(ZLIST_FOLDER)
    ui_utils.prepare_files(DATA_FOLDER, CSV_FILE)

    player_names = get_player_names()
    player_ids = get_player_ids(player_names)
    register_player_ids(player_ids)
