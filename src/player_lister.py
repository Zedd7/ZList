# -*- coding: utf-8 -*-

"""List a fraction of all existing account ids and save them to file."""

import sys
import os
import random
import csv

import requests

CONFIG_FILE = '../res/config.txt'
APP_ID = 'demo'
ACCOUNT_INFO_REQUEST_URL = "https://api.worldoftanks.eu/wot/account/info/"
BATCH_SIZE = 100
OUTPUT_FOLDER = "../data"
CSV_FILE = '{folder}/SERVER_ID.csv'.format(folder=OUTPUT_FOLDER)
ID_LOWER_BOUND = 500000000
ID_UPPER_BOUND = 560000000


def list_accounts(step, csv_file_path, random_offset=True):
    """List a fraction of all existing accounts ids in provided range."""
    account_ids, loaded_account_id_amount = load_account_ids()
    offset = random.randint(0, step) if random_offset else 0
    account_id = ID_LOWER_BOUND + offset
    while account_id <= ID_UPPER_BOUND:
        batch = []
        while len(batch) < BATCH_SIZE and account_id <= ID_UPPER_BOUND:
            # Do not test if already registered to update nickname
            batch.append(str(account_id))
            if account_id < ID_UPPER_BOUND:
                account_id = min(account_id + step, ID_UPPER_BOUND)
            else:
                account_id += 1
        payload = {
            'application_id': APP_ID,
            'account_id': ','.join(batch),
            'fields': 'nickname,account_id'
        }
        response = requests.get(ACCOUNT_INFO_REQUEST_URL, params=payload)
        response_content = response.json()

        if response_content['status'] == 'ok':
            for player_id in response_content['data']:
                account_data = response_content['data'][player_id]
                if account_data:
                    player_name = account_data['nickname']
                    account_ids[player_id] = player_name

        progress = (account_id - ID_LOWER_BOUND) / (ID_UPPER_BOUND - ID_LOWER_BOUND + 1) * 100
        sys.stdout.write("\rTesting account ids : %.2f %%" % progress)
        sys.stdout.flush()
    print(". Found %d existing accounts." % (len(account_ids) - loaded_account_id_amount))
    return account_ids


def load_account_ids():
    """Load dictionary of known existing accounts."""
    print("Loading existing accounts from CSV file... ", end='', flush=True)
    account_ids = {}
    with open(CSV_FILE, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for player_name, account_id in csv_reader:
            account_ids[account_id] = player_name
    print("Done.", end=' ')
    loaded_account_id_amount = len(account_ids)
    print("Found %d registered accounts." % loaded_account_id_amount)
    return account_ids, loaded_account_id_amount


def register_accounts(account_ids):
    """Register existing accounts in CSV file."""
    print("Registering account ids to CSV file... ", end='', flush=True)
    with open(CSV_FILE, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        for account_id in sorted(account_ids, key=lambda x: int(x)):
            csv_writer.writerow([account_ids[account_id], account_id])
    print("Done.")


if __name__ == '__main__':
    # Load custom application id from config
    default_app_id = True
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as config:
            app_id_line = config.readline().rstrip()
            if (len(app_id_line.split('=')) == 2 and
                    app_id_line.split('=')[0] == 'WG_API_APPLICATION_ID' and
                    app_id_line.split('=')[1] != APP_ID):
                APP_ID = app_id_line.split('=')[1]
                default_app_id = False
    if default_app_id:
        print("No custom application id could be found in",
              "{config}.".format(config=os.path.abspath(CONFIG_FILE)), '\n'
              "The default id will be used but the number of requests to",
              "WG API will be limited and the results may be truncated.")
    else:
        print("New application id loaded from config: {id}".format(id=APP_ID))

    # Prepare output file
    if not os.path.isdir(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    if not os.path.exists(CSV_FILE):
        open(CSV_FILE, "w").close()

    # Select search mode
    SEARCH_MODES = [('fast', 0.0001), ('light', 0.001), ('medium', 0.01), ('dense', 0.1), ('full', 1)]
    search_mode_selection = -1
    print("Choose the search mode for account id testing among the followings:")
    for i, search_mode in enumerate(SEARCH_MODES):
        print("  {number} : {name}".format(number=(i + 1), name=search_mode[0]))
    while search_mode_selection not in range(1, len(SEARCH_MODES) + 1):
        try:
            search_mode_selection = int(input("Number of the search mode to use (recommended: 2) : "))
            if search_mode_selection not in range(1, len(SEARCH_MODES) + 1):
                raise ValueError
        except:
            print("The value must be the number of a search mode.")
    step = int(1 / SEARCH_MODES[search_mode_selection - 1][1])

    # Select offset option
    OFFSET_OPTIONS = [('deterministic', False), ('random', True)]
    offset_option_selection = -1
    print("Choose between deterministic or random search:")
    for i, offset_option in enumerate(OFFSET_OPTIONS):
        print("  {number} : {name}".format(number=(i + 1), name=offset_option[0]))
    while offset_option_selection not in range(1, len(OFFSET_OPTIONS) + 1):
        try:
            offset_option_selection = int(input("Number of the selection (recommended: 2) : "))
            if offset_option_selection not in range(1, len(OFFSET_OPTIONS) + 1):
                raise ValueError
        except:
            print("The value must be the number of a search method.")
    random_offset = OFFSET_OPTIONS[offset_option_selection - 1][1]

    # Perform search
    account_ids = list_accounts(step, random_offset)
    register_accounts(account_ids)
