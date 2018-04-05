# -*- coding: utf-8 -*-

"""Map players' names to their account id in a CSV file."""

import sys
import os
import csv

import requests

CONFIG_FILE = '../res/config.txt'
APP_ID = 'demo'
ACCOUNT_INFO_REQUEST_URL = 'https://api.worldoftanks.eu/wot/account/list/'
BATCH_SIZE = 100
ZLIST_FOLDER = '../res_mods/mods/shared_resources/xvm/res/clanicons/EU/nick'
OUTPUT_FOLDER = '../data'
OUTPUT_FILE = '{folder}/ZLIST_ID.csv'.format(folder=OUTPUT_FOLDER)
UNKNOWN_ID = -1


def get_player_names(player_folder):
    """Extract player names from ZList."""
    print("Extracting player names from ZList... ", end='')
    player_names = []
    for file_name in os.listdir(player_folder):
        if not file_name.startswith('.'):  # Is not a category file
            player_names.append(file_name.rstrip('.png'))
    print("Done.")
    return player_names


def get_player_ids(player_names, output_file_path):
    """Get account id of players."""
    # Retrieve previously registered player ids
    player_ids = load_player_ids(output_file_path)
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
            for player_name in batch_ids:
                player_ids[player_name] = batch_ids[player_name]
        progress = index / player_count * 100
        sys.stdout.write("\rRequesting player ids: %.2f %%" % progress)
        sys.stdout.flush()
    print()
    return player_ids


def load_player_ids(output_file_path):
    """Load dictionary of known mappings for player names and their id."""
    print("Loading registered player ids from CSV file... ", end='')
    player_ids = {}
    with open(output_file_path, 'r', newline='') as output_file:
        csv_reader = csv.reader(output_file, delimiter=',')
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


def register_player_ids(player_ids, output_file_path):
    """Register player ids in CSV file."""
    print("Registering player ids to CSV file... ", end='')
    with open(output_file_path, 'w', newline='') as output_file:
        csv_writer = csv.writer(output_file, delimiter=',')
        for player in sorted(player_ids.keys(), key=str.lower):
            csv_writer.writerow([player, player_ids[player]])
    print("Done.")


if __name__ == "__main__":
    default_app_id = True
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as config:
            app_id_line = config.readline().rstrip()
            print(APP_ID)
            if (len(app_id_line.split('=')) == 2 and
                    app_id_line.split('=')[0] == 'WG_API_APPLICATION_ID' and
                    app_id_line.split('=')[1] != APP_ID):
                API_ID = app_id_line.split('=')[1]
                default_app_id = False
    if default_app_id:
        print("No custom application id could be found in",
              "{config}.".format(config=os.path.abspath(CONFIG_FILE)), '\n'
              "The default id will be used but the number of requests to",
              "WG API will be limited and the results may be truncated.")
    else:
        print("New application id loaded from config: {id}".format(id=API_ID))

    if not os.path.isdir(ZLIST_FOLDER):
        print("ZList folder not found, creating it.")
        os.makedirs(ZLIST_FOLDER)

    if not os.path.isdir(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    if not os.path.exists(OUTPUT_FILE):
        open(OUTPUT_FILE, 'w').close()

    player_names = get_player_names(ZLIST_FOLDER)
    player_ids = get_player_ids(player_names, OUTPUT_FILE)
    register_player_ids(player_ids, OUTPUT_FILE)
