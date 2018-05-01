# -*- coding: utf-8 -*-

"""Enumerate available stats."""

import player_profiler as profiler

STATS = {
    'battles': {
        'stats_fetcher': profiler.get_total_stat_d,
        'short_name': "battles",
        'long_name': "battle count",
        'field': 'statistics.all.battles',
        'use_exp_values': False,
        'group_by_value': False,
        'is_percentage': False,
        'preferred_lb': 0,
        'preferred_ub': 100000,
        'mark_step': 5000
    },
    'wn8': {
        'stats_fetcher': profiler.get_wn8_d,
        'short_name': "WN8",
        'long_name': "WN8",
        'use_exp_values': True,
        'group_by_value': False,
        'is_percentage': False,
        'preferred_lb': 0,
        'preferred_ub': 3500,
        'mark_step': 500
    },
    'global_rating': {
        'stats_fetcher': profiler.get_total_stat_d,
        'short_name': "global rating",
        'long_name': "global rating",
        'field': 'global_rating',
        'use_exp_values': False,
        'group_by_value': False,
        'is_percentage': False,
        'preferred_lb': 0,
        'preferred_ub': 12000,
        'mark_step': 600
    },
    'wr': {
        'stats_fetcher': profiler.get_average_stat_d,
        'short_name': "WR",
        'long_name': "win ratio",
        'field': 'statistics.all.wins',
        'dependency_field': 'statistics.all.battles',
        'use_exp_values': False,
        'group_by_value': False,
        'is_percentage': True,
        'preferred_lb': 40,
        'preferred_ub': 75,
        'mark_step': 5
    },
    'avg_xp': {
        'stats_fetcher': profiler.get_total_stat_d,
        'short_name': "average xp",
        'long_name': "average experience points",
        'field': 'statistics.all.battle_avg_xp',
        'use_exp_values': False,
        'group_by_value': False,
        'is_percentage': False,
        'preferred_lb': 0,
        'preferred_ub': 1200,
        'mark_step': 60
    },
    'avg_damage': {
        'stats_fetcher': profiler.get_average_stat_d,
        'short_name': "average damage",
        'long_name': "average damage dealt",
        'field': 'statistics.all.damage_dealt',
        'dependency_field': 'statistics.all.battles',
        'use_exp_values': False,
        'group_by_value': False,
        'is_percentage': False,
        'preferred_lb': 0,
        'preferred_ub': 3000,
        'mark_step': 150
    },
    'avg_assist': {
        'stats_fetcher': profiler.get_total_stat_d,
        'short_name': "average assist",
        'long_name': "average damage assisted",
        'field': 'statistics.all.avg_damage_assisted',
        'use_exp_values': False,
        'group_by_value': False,
        'is_percentage': False,
        'preferred_lb': 0,
        'preferred_ub': 800,
        'mark_step': 40
    },
    'avg_blocked': {
        'stats_fetcher': profiler.get_total_stat_d,
        'short_name': "average blocked",
        'long_name': "average damage blocked",
        'field': 'statistics.all.avg_damage_blocked',
        'use_exp_values': False,
        'group_by_value': False,
        'is_percentage': False,
        'preferred_lb': 0,
        'preferred_ub': 800,
        'mark_step': 40
    },
    'avg_kill': {
        'stats_fetcher': profiler.get_average_stat_d,
        'short_name': "average kill",
        'long_name': "average vehicles destroyed",
        'field': 'statistics.all.frags',
        'dependency_field': 'statistics.all.battles',
        'use_exp_values': False,
        'group_by_value': False,
        'is_percentage': False,
        'preferred_lb': 0,
        'preferred_ub': 2,
        'mark_step': 1
    },
    'avg_spot': {
        'stats_fetcher': profiler.get_average_stat_d,
        'short_name': "average spot",
        'long_name': "average vehicles spotted",
        'field': 'statistics.all.spotted',
        'dependency_field': 'statistics.all.battles',
        'use_exp_values': False,
        'group_by_value': False,
        'is_percentage': False,
        'preferred_lb': 0,
        'preferred_ub': 3,
        'mark_step': 1
    },
    'hit_ratio': {
        'stats_fetcher': profiler.get_per_shot_stat_d,
        'short_name': "hit ratio",
        'long_name': "direct hit ratio",
        'field': 'statistics.all.hits',
        'dependency_field': 'statistics.all.shots',
        'use_exp_values': False,
        'group_by_value': False,
        'is_percentage': True,
        'preferred_lb': 20,
        'preferred_ub': 100,
        'mark_step': 4
    },
    'avg_capture': {
        'stats_fetcher': profiler.get_average_stat_d,
        'short_name': "average capture",
        'long_name': "average capture points",
        'field': 'statistics.all.capture_points',
        'dependency_field': 'statistics.all.battles',
        'use_exp_values': False,
        'group_by_value': False,
        'is_percentage': False,
        'preferred_lb': 0,
        'preferred_ub': 4,
        'mark_step': 1
    },
    'avg_defense': {
        'stats_fetcher': profiler.get_average_stat_d,
        'short_name': "average defense",
        'long_name': "average defense points",
        'field': 'statistics.all.dropped_capture_points',
        'dependency_field': 'statistics.all.battles',
        'use_exp_values': False,
        'group_by_value': False,
        'is_percentage': False,
        'preferred_lb': 0,
        'preferred_ub': 3,
        'mark_step': 1
    },
    'splash_ratio': {
        'stats_fetcher': profiler.get_average_stat_d,
        'short_name': "splash ratio",
        'long_name': "splash received ratio",
        'field': 'statistics.all.explosion_hits',
        'dependency_field': 'statistics.all.battles',
        'use_exp_values': False,
        'group_by_value': False,
        'is_percentage': True,
        'preferred_lb': 0,
        'preferred_ub': 0,
        'mark_step': 5
    },
    'count': {
        'stats_fetcher': profiler.get_count_d,
        'short_name': "count",
        'long_name': "player count",
        'use_exp_values': False,
        'group_by_value': True,
        'sort_by_count': False
    },
    'language': {
        'stats_fetcher': profiler.get_language_d,
        'short_name': "language",
        'long_name': "client language",
        'field': 'client_language',
        'use_exp_values': False,
        'group_by_value': True,
        'sort_by_count': True
    }
}
