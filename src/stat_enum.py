# -*- coding: utf-8 -*-

"""Enumerate available stats."""

import player_profiler as profiler

STAT_ENUM = {
    'wn8': {
        'stats_fetcher': profiler.get_wn8_d,
        'short_name': "WN8",
        'long_name': "WN8",
        'use_exp_values': True,
        'group_by_value': False,
        'is_precentage': False,
        'preferred_lb': 0,
        'preferred_ub': 3500,
        'mark_step': 500
    },
    'wr': {
        'stats_fetcher': profiler.get_average_stat_d,
        'short_name': "WR",
        'long_name': "win ratio",
        'field': 'statistics.all.wins',
        'dependency_field': 'statistics.all.battles',
        'use_exp_values': False,
        'group_by_value': False,
        'is_precentage': True,
        'preferred_lb': 40,
        'preferred_ub': 75,
        'mark_step': 5
    },
    'battles': {
        'stats_fetcher': profiler.get_total_stat_d,
        'short_name': "battles",
        'long_name': "battle count",
        'field': 'statistics.all.battles',
        'use_exp_values': False,
        'group_by_value': False,
        'is_precentage': False,
        'preferred_lb': 0,
        'preferred_ub': 100000,
        'mark_step': 5000
    },
    'avg_xp': {
        'stats_fetcher': profiler.get_total_stat_d,
        'short_name': "average xp",
        'long_name': "average experience points",
        'field': 'statistics.all.battle_avg_xp',
        'use_exp_values': False,
        'group_by_value': False,
        'is_precentage': False,
        'preferred_lb': 0,
        'preferred_ub': 1200,
        'mark_step': 60
    },
    'hit_ratio': {
        'stats_fetcher': profiler.get_per_shot_stat_d,
        'short_name': "hit ratio",
        'long_name': "direct hit ratio",
        'field': 'statistics.all.hits',
        'dependency_field': 'statistics.all.shots',
        'use_exp_values': False,
        'group_by_value': False,
        'is_precentage': True,
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
        'is_precentage': True,
        'preferred_lb': 0,
        'preferred_ub': 300,
        'mark_step': 15
    },
    'splash_ratio': {
        'stats_fetcher': profiler.get_average_stat_d,
        'short_name': "splash ratio",
        'long_name': "splash received ratio",
        'field': 'statistics.all.explosion_hits',
        'dependency_field': 'statistics.all.battles',
        'use_exp_values': False,
        'group_by_value': False,
        'is_precentage': True,
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
