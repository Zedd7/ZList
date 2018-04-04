# -*- coding: utf-8 -*-

"""Map players' names to their account id in a CSV file."""

import sys
import os
import csv

import requests

APP_ID = 'demo'  # Replace with your own app id to extend the requests limit
REQUEST_URL = 'https://api.worldoftanks.eu/wot/account/list/'
BATCH_SIZE = 100
ZLIST_FOLDER = "../res_mods/mods/shared_resources/xvm/res/clanicons/EU/nick"
OUTPUT_FOLDER = '../data'
OUTPUT_FILE = '%s/ZLIST_ID.csv' % OUTPUT_FOLDER
UNKNOWN_ID = -1


def get_player_list(player_folder):
    """Extract player names from ZList."""
    print("Extracting player names from ZList... ", end='')
    player_list = []
    for file_name in os.listdir(player_folder):
        if not file_name.startswith('.'):  # Is not a category file
            player_list.append(file_name.rstrip('.png'))
    print("Done.")
    return player_list


def register_player_ids(player_list, output_file_path):
    """Map player names to their id in a CSV file."""
    # Retrieve previously registered player ids
    player_id_dict = load_player_id_dict(output_file_path)

    player_count = len(player_list)
    index = 0
    while index < len(player_list):
        batch = []
        while len(batch) < BATCH_SIZE and index < len(player_list):
            player = player_list[index]
            if player not in player_id_dict:
                batch.append(player)
            index += 1
        if batch:
            batch_id_dict = get_player_id_dict(batch)
            for player in batch_id_dict:
                player_id_dict[player] = batch_id_dict[player]
        progress = index / player_count * 100
        sys.stdout.write("\rRequesting player ids : %.2f %%" % progress)
        sys.stdout.flush()
    print()

    print("Registering player ids to CSV file... ", end='')
    with open(output_file_path, 'w', newline='') as output_file:
        csv_writer = csv.writer(output_file, delimiter=',')
        for player in sorted(player_id_dict.keys(), key=str.lower):
            csv_writer.writerow([player, player_id_dict[player]])
    print("Done.")


def load_player_id_dict(output_file_path):
    """Load dictionary of known mappings for player names and their id."""
    print("Loading registered player ids from CSV file... ", end='')
    player_id_dict = {}
    with open(output_file_path, 'r', newline='') as output_file:
        csv_reader = csv.reader(output_file, delimiter=',')
        for player, player_id in csv_reader:
            player_id_dict[player] = player_id
    print("Done.")
    return player_id_dict


def get_player_id_dict(player_list):
    """Retrieve the ids of a list of players."""
    payload = {
        'application_id': APP_ID,
        'search': ','.join(player_list),
        'type': 'exact'
    }
    response = requests.get(REQUEST_URL, params=payload)
    response_content = response.json()
    player_id_dict = {player: UNKNOWN_ID for player in player_list}
    if response_content['status'] == 'ok':
        for player_data in response_content['data']:
            player = get_player_name(player_data['nickname'], player_list)
            player_id = player_data['account_id']
            player_id_dict[player] = player_id
    return player_id_dict


def get_player_name(player_name, player_list):
    """Return the name of the player in the same case as in the list."""
    for player in player_list:
        if player.lower() == player_name.lower():
            return player
    return player_name


if __name__ == "__main__":
    if not os.path.isdir(ZLIST_FOLDER):
        print("ZList folder not found, creating it.")
        os.makedirs(ZLIST_FOLDER)
    if not os.path.isdir(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    if not os.path.exists(OUTPUT_FILE):
        open(OUTPUT_FILE, 'w').close()

    player_list = get_player_list(ZLIST_FOLDER)
    register_player_ids(player_list, OUTPUT_FILE)
