# -*- coding: utf-8 -*-

"""Provide tools to compute the WN8 of players."""

import os
import json

import requests


APP_ID = 'demo'
ACCOUNT_STATS_REQUEST_URL = 'https://api.worldoftanks.eu/wot/account/info/'
ACCOUNT_TANKS_REQUEST_URL = 'https://api.worldoftanks.eu/wot/account/tanks/'
TANK_STATS_REQUEST_URL = 'https://api.worldoftanks.eu/wot/tanks/stats/'
BATCH_SIZE = 100
ACCOUNT_STATS_FIELD_LIST = [
    'statistics.all.battles',
    'statistics.all.damage_dealt',
    'statistics.all.spotted',
    'statistics.all.frags',
    'statistics.all.dropped_capture_points',
    'statistics.all.wins'
]
ACCOUNT_TANKS_FIELD_LIST = [
    'tank_id',
    'statistics.battles'
]
TANK_STATS_FIELD_LIST = [
    'all.damage_dealt',
    'all.spotted',
    'all.frags',
    'all.dropped_capture_points',
    'all.wins'
]
EXP_VALUES_FILE_URL = 'https://static.modxvm.com/wn8-data-exp/json/wn8exp.json'
RES_FOLDER = '../res'
EXP_VALUES_FILE_PATH = '{folder}/wn8_exp_values.json'.format(folder=RES_FOLDER)


def set_app_id(app_id):
    """Replace the default application id by a new one."""
    APP_ID = app_id
    return APP_ID


def get_exp_values_d():
    """Download or load the last version of WN8 expected values."""
    if not os.path.isdir(RES_FOLDER):
        os.makedirs(RES_FOLDER)

    exp_values_json = None
    if not os.path.exists(EXP_VALUES_FILE_PATH):
        response = requests.get(EXP_VALUES_FILE_URL)
        with open(EXP_VALUES_FILE_PATH, 'w') as exp_values_file:
            exp_values_file.write(response.text)
            exp_values_json = response.json()
    else:
        with open(EXP_VALUES_FILE_PATH, 'r') as exp_values_file:
            exp_values_json = json.load(exp_values_file)

    exp_values_d = {}
    if exp_values_json:
        for tank_data in exp_values_json['data']:
            exp_values_d[tank_data['IDNum']] = {
                'damage_ratio': tank_data['expDamage'],
                'spot_ratio': tank_data['expSpot'],
                'kill_ratio': tank_data['expFrag'],
                'defense_ratio': tank_data['expDef'],
                'win_ratio': tank_data['expWinRate']
            }
    return exp_values_d


def calculate_wn8(player_ids, exp_values_d):
    """Calculate the WN8 of a batch of players."""
    wn8_d, account_stats_d, exp_stats_d = {}, {}, {}
    missing_tanks_d = {player_id: [] for player_id in player_ids}

    index, batches = 0, []
    while index < len(player_ids):
        batches.append(player_ids[index:min(index + BATCH_SIZE, len(player_ids))])
        index += len(batches[-1])
    for batch in batches:
        load_account_stats(account_stats_d, batch)
        load_expected_stats(exp_stats_d, missing_tanks_d, batch, exp_values_d)

    for player_id in player_ids:
        if all(player_id in stats for stats in (account_stats_d, exp_stats_d)):
            adjust_account_stats(account_stats_d, player_id, missing_tanks_d[player_id])
            dmgs, spots, kills, defs, wins = account_stats_d[player_id]
            exp_dmgs, exp_spots, exp_kills, exp_defs, exp_wins = exp_stats_d[player_id]

            r_dmg = dmgs / exp_dmgs if exp_dmgs > 0 else 0
            r_spot = spots / exp_spots if exp_spots > 0 else 0
            r_kill = kills / exp_kills if exp_kills > 0 else 0
            r_def = defs / exp_defs if exp_defs > 0 else 0
            r_win = wins / exp_wins if exp_wins > 0 else 0

            r_dmg_c = max(0, (r_dmg - 0.22) / 0.78)
            r_spot_c = max(0, min(r_dmg_c + 0.1, (r_spot - 0.38) / 0.62))
            r_kill_c = max(0, min(r_dmg_c + 0.2, (r_kill - 0.12) / 0.88))
            r_def_c = max(0, min(r_dmg_c + 0.1, (r_def - 0.10) / 0.90))
            r_win_c = max(0, (r_win - 0.71) / 0.29)

            wn8 = 980 * r_dmg_c
            wn8 += 210 * r_dmg_c * r_kill_c
            wn8 += 155 * r_kill_c * r_spot_c
            wn8 += 75 * r_def_c * r_kill_c
            wn8 += 145 * min(1.8, r_win_c)
            wn8_d[player_id] = wn8

    return wn8_d


def load_account_stats(account_stats_d, player_ids):
    """Retrieve the required statistics of the accounts."""
    payload = {
        'application_id': APP_ID,
        'account_id': ','.join(player_ids),
        'fields': ','.join(ACCOUNT_STATS_FIELD_LIST)
    }
    response = requests.get(ACCOUNT_STATS_REQUEST_URL, params=payload)
    response_content = response.json()

    for player_id in player_ids:
        account_stats = None
        if response_content['status'] == 'ok':
            player_data = response_content['data'][player_id]
            if player_data:
                player_stats = player_data['statistics']['all']
                dmgs = player_stats['damage_dealt']
                spots = player_stats['spotted']
                kills = player_stats['frags']
                defs = player_stats['dropped_capture_points']
                wins = player_stats['wins']
                account_stats = dmgs, spots, kills, defs, wins
        if account_stats:
            account_stats_d[player_id] = account_stats


def load_expected_stats(exp_stats_d, missing_tanks_d, player_ids, exp_values_d):
    """Calculate the required expected statistics of the accounts."""
    payload = {
        'application_id': APP_ID,
        'account_id': ','.join(player_ids),
        'fields': ','.join(ACCOUNT_TANKS_FIELD_LIST)
    }
    response = requests.get(ACCOUNT_TANKS_REQUEST_URL, params=payload)
    response_content = response.json()

    for player_id in player_ids:
        exp_stats = None
        if response_content['status'] == 'ok':
            exp_dmgs, exp_spots, exp_kills, exp_defs, exp_wins = (0,) * 5
            player_data = response_content['data'][player_id]
            if player_data:
                for tank_data in player_data:
                    tank_id = tank_data['tank_id']
                    battles = tank_data['statistics']['battles']
                    if tank_id in exp_values_d:
                        tank_exp_values = exp_values_d[tank_id]
                        exp_dmgs += tank_exp_values['damage_ratio'] * battles
                        exp_spots += tank_exp_values['spot_ratio'] * battles
                        exp_kills += tank_exp_values['kill_ratio'] * battles
                        exp_defs += tank_exp_values['defense_ratio'] * battles
                        exp_wins += (tank_exp_values['win_ratio'] / 100) * battles
                    else:
                        missing_tanks_d[player_id].append(str(tank_id))
                exp_stats = exp_dmgs, exp_spots, exp_kills, exp_defs, exp_wins
        if exp_stats:
            exp_stats_d[player_id] = exp_stats


def adjust_account_stats(account_stats_d, player_id, missing_tanks):
    """Adjust account totals with stats of missing tanks."""
    if missing_tanks:
        payload = {
            'application_id': APP_ID,
            'account_id': player_id,
            'fields': ','.join(TANK_STATS_FIELD_LIST),
            'tank_id': ','.join(missing_tanks)
        }
        response = requests.get(TANK_STATS_REQUEST_URL, params=payload)
        response_content = response.json()

        if response_content['status'] == 'ok':
            dmgs, spots, kills, defs, wins = account_stats_d[player_id]
            player_data = response_content['data'][player_id]
            if player_data:
                for tank_stats in player_data:
                    dmgs -= tank_stats['all']['damage_dealt']
                    spots -= tank_stats['all']['spotted']
                    kills -= tank_stats['all']['frags']
                    defs -= tank_stats['all']['dropped_capture_points']
                    wins -= tank_stats['all']['wins']
                account_stats = dmgs, spots, kills, defs, wins
                account_stats_d[player_id] = account_stats
