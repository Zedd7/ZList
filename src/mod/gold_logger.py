"""WoT mod for logging gold users into the ZList. Forked from https://wgmods.net/1233/."""

import re
import BigWorld
import nations
import ResMgr
from functools import wraps, partial
from items import _xml
from constants import ITEM_DEFS_PATH
from helpers.EffectsList import _PixieEffectDesc
from helpers.bound_effects import ModelBoundEffects, StaticSceneBoundEffects

import os


ZLIST_FOLDER = './res_mods/mods/shared_resources/xvm/res/clanicons/EU/nick'
LOG_FILE = './GOLD_USER.csv'


def prepare_log_file():
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'w').close()


def log_gold_user(player_name, account_id):
    with open(LOG_FILE, 'a') as log_file:
        log_file.write("%s,%s\n" % (player_name, account_id))


class ModifiedValueManager:
    def __init__(self):
        self._values = []
    def add_value(self, container, key, restore_value):
        self._values.append((container, key, restore_value))
    def restore(self):
        for (container, key, restore_value) in self._values:
            container[key] = restore_value
        self._values = []


def run_before(module, func_name):
    def decorator(callback):
        func = getattr(module, func_name)

        @wraps(func)
        def run_before_wrapper(*args, **kwargs):
            callback(*args, **kwargs)
            return func(*args, **kwargs)

        setattr(module, func_name, run_before_wrapper)
        return callback

    return decorator


def load_shell_prices(nation):
    xml_path = ITEM_DEFS_PATH + 'vehicles/' + nation + '/components/shells.xml'
    section = ResMgr.openSection(xml_path)
    prices = {}
    for name, subsection in section.items():
        if name in ('icons', 'xmlns:xmlref'):
            continue
        xml_ctx = (None, xml_path + '/' + name)
        shell_id = _xml.readInt(xml_ctx, subsection, 'id', 0, 65535)
        prices[shell_id] = _xml.readPrice(xml_ctx, subsection, 'price')
    ResMgr.purge(xml_path, True)
    return prices


def get_pixie_effects(effects_list):
    effects_desc = effects_list._EffectsList__effectDescList
    return [desc for desc in effects_desc if isinstance(desc, _PixieEffectDesc)]


def get_gun(attacker_id, players):
    attacker = players.get(attacker_id, None)
    if attacker is None:
        return None
    gun, _ = attacker['vehicleType'].getComponentsByType('vehicleGun')
    return gun


def get_gold_ammo_types_from_prices(shell_prices, default_gold_ammo_types, gun):
    if gun is None:
        return default_gold_ammo_types
    gold_ammo_types = []
    for shot in gun.shots:
        nation_id, shell_id = shot.shell.id
        gold_price = shell_prices[nation_id][shell_id].get('gold', None)
        if gold_price is not None:
            gold_ammo_types.append(shot.shell.kind)
    if len(gold_ammo_types) > 0:
        return gold_ammo_types
    credits_prices = []
    for shot in gun.shots:
        nation_id, shell_id = shot.shell.id
        credits_price = shell_prices[nation_id][shell_id].get('credits', 0)
        credits_prices.append(credits_price)
    avg_price = reduce(lambda total, price: total + price, credits_prices, 0) / len(credits_prices)
    premium_shells = [index for (index, price) in enumerate(credits_prices) if price > avg_price]
    return map(lambda index: gun.shots[index].shell.kind, premium_shells)


get_gold_ammo_types = partial(
    get_gold_ammo_types_from_prices,
    map(lambda nation: load_shell_prices(nation), nations.NAMES),
    []
)


def get_ingame_player_id(player, players):
    player_name = player.name
    return [player_id for (player_id, player) in players.items() if player['name'] == player_name][0]


def get_team_id(player_id, players):
    return players.get(player_id, {}).get('team', None)


def should_log_attacker(player, players, shell_type, gun, attacker_id):
    return not(is_own_player(attacker_id, player, players) or is_gold_shell_type_ambiguous(shell_type, gun))


def is_own_player(attacker_id, player, players):
    return get_ingame_player_id(player, players) == attacker_id


def is_gold_shell_type_ambiguous(shell_type, gun):
    if gun is None:
        return False
    gold_shell_types = get_gold_ammo_types(gun)
    if shell_type not in gold_shell_types:
        return False
    shell_types = map(lambda s: s.shell.kind, gun.shots)
    occ_in_shell_types = reduce(lambda total, st: int(st == shell_type) + total, shell_types, 0)
    occ_in_gold_shell_types = reduce(lambda total, st: int(st == shell_type) + total, gold_shell_types, 0)
    return occ_in_shell_types > occ_in_gold_shell_types


def shell_type_from_effect_name(effect_name):
    shell_type = 'ARMOR_PIERCING'
    if '_AP_CR' in effect_name.upper():
        shell_type = 'ARMOR_PIERCING_CR'
    elif '_HC' in effect_name.upper():
        shell_type = 'HOLLOW_CHARGE'
    elif '_HE' in effect_name.upper():
        shell_type = 'HIGH_EXPLOSIVE'
    return shell_type


def restore_with_mgr_and_modify_effect(modified_file_name_mgr, effects_list, attacker_id):
    modified_file_name_mgr.restore()
    player = BigWorld.player()
    players = player.arena.vehicles
    gun = get_gun(attacker_id, players)
    gold_ammo_types = get_gold_ammo_types(gun)
    pixie_effects = get_pixie_effects(effects_list)
    for pixie_effect in pixie_effects:
        for (index, file_path) in enumerate(pixie_effect._files):
            match = re.search('^particles/Shells_Eff/([a-zA-Z0-9_-]+)\.xml$', file_path)
            if match is not None:
                effect_name = match.group(1)
                shell_type = shell_type_from_effect_name(effect_name)
                if shell_type in gold_ammo_types and should_log_attacker(player, players, shell_type, gun, attacker_id):
                    attacker_name = players[attacker_id]['name']
                    attacker_dbid = players[attacker_id]['accountDBID']
                    log_gold_user(attacker_name, attacker_dbid)


prepare_log_file()

restore_and_modify_effect = partial(restore_with_mgr_and_modify_effect, ModifiedValueManager())


@run_before(StaticSceneBoundEffects, 'addNew')
def modify_static_bound_effect(*args, **kwargs):
    return restore_and_modify_effect(args[2], kwargs.get('attackerID', 0))


@run_before(ModelBoundEffects, 'addNewToNode')
def modify_model_bound_effect(*args, **kwargs):
    return restore_and_modify_effect(args[3], kwargs.get('attackerID', 0))
