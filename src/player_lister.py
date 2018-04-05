# -*- coding: utf-8 -*-

"""List a fraction of all existing account ids and save them to file."""

import sys
import os
# import random
import csv

import requests

CONFIG_FILE = '../res/config.txt'
APP_ID = 'demo'
ACCOUNT_INFO_REQUEST_URL = "https://api.worldoftanks.eu/wot/account/info/"
BATCH_SIZE = 100
OUTPUT_FOLDER = "../data"
OUTPUT_FILE = '{folder}/CLUSTER_ID.csv'.format(folder=OUTPUT_FOLDER)
ID_LOWER_BOUND = 500000000
ID_UPPER_BOUND = 547800100
ID_SKIP_INTERVAL = 100000
# (ID_UPPER_BOUND - ID_LOWER_BOUND) / ID_SKIP_INTERVAL = nb of accounts enumerated

# TODO: random skip
# TODO: load from previous file


def list_accounts():
    """List a fraction of all existing accounts ids in provided range."""
    accounts = []
    account_id = ID_LOWER_BOUND
    while account_id <= ID_UPPER_BOUND:
        batch = []
        while len(batch) < BATCH_SIZE and account_id <= ID_UPPER_BOUND:
            batch.append(str(account_id))
            if account_id < ID_UPPER_BOUND:
                account_id = min(account_id + ID_SKIP_INTERVAL, ID_UPPER_BOUND)
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
                    accounts.append((player_name, player_id))

        progress = (account_id - ID_LOWER_BOUND) / (ID_UPPER_BOUND - ID_LOWER_BOUND + 1) * 100
        sys.stdout.write("\rTesting account ids : %.2f %%" % progress)
        sys.stdout.flush()
    print()

    return accounts


def register_accounts(accounts, output_file_path):
    """Register existing accounts in CSV file."""
    print("%d existing account found." % len(accounts))
    print("Registering account ids to CSV file... ", end='')
    with open(output_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        for player_name, player_id in sorted(accounts, key=lambda x: x[1]):
            csv_writer.writerow([player_name, player_id])
    print("Done.")


if __name__ == "__main__":
    default_app_id = True
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as config:
            app_id_line = config.readline().rstrip()
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

    if not os.path.isdir(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    if not os.path.exists(OUTPUT_FILE):
        open(OUTPUT_FILE, "w").close()

    accounts = list_accounts()
    register_accounts(accounts, OUTPUT_FILE)
