# -*- coding: utf-8 -*-

"""List a fraction of all existing account ids and save them to file."""

import sys
import random
import csv

import requests

import ui_utils

CONFIG_FILE = '../res/config.txt'
APP_ID = 'demo'
ACCOUNT_INFO_REQUEST_URL = "https://api.worldoftanks.eu/wot/account/info/"
BATCH_SIZE = 100
DATA_FOLDER = "../data"
CSV_FILE = '{data_folder}/SERVER_ID.csv'.format(data_folder=DATA_FOLDER)
ID_LOWER_BOUND = 500000000
ID_UPPER_BOUND = 560000000


def list_accounts(step, csv_file_path, use_random_offset=True):
    """List a fraction of all existing accounts ids in provided range."""
    account_ids, loaded_account_id_amount = load_account_ids()
    offset = random.randint(0, step) if use_random_offset else 0
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
    input("The module player_lister connects to the WG API to retrieve the "
          "list of registered account on the EU cluster.\n"
          "As the number of account is too large to be explored in one run, "
          "several methods are proposed to explore the database.\n"
          "Each next method is 10 times slower than the previous method but is "
          "expected to find 10 times more existing accounts.\n"
          "You will be asked to choose one among the list of search methods.\n"
          "You will also be asked to choose whether you want to add randomness "
          "to the search (retrieves new account ids each time but does not "
          "allow replication) or not.\n\n"
          "Press ENTER to continue (or CTRL + C + ENTER to abort).\n")

    APP_ID = ui_utils.load_app_id(CONFIG_FILE, APP_ID)
    ui_utils.prepare_files(DATA_FOLDER, CSV_FILE)

    step = int(1 / ui_utils.select_search_mode(
        ('fast', 0.0001),
        ('light', 0.001),
        ('medium', 0.01),
        ('dense', 0.1),
        ('full', 1)
    ))
    use_random_offset = ui_utils.select_offset_option(
        ('deterministic', False),
        ('random', True)
    )

    account_ids = list_accounts(step, use_random_offset)
    register_accounts(account_ids)
