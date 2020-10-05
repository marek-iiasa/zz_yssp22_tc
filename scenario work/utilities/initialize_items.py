# -*- coding: utf-8 -*-
"""
This script add new items (sets, parameters, and variables) to a MESSAGEix
scenario. A new item is an item that is not defined by default in a scenario.
"""

# Initializing new sets and parameters if needed
def init_new_items(sc):

    # 1) Adding sets
    dict_set = {
        'is_relation_upper_time': [
            ['relation', 'node', 'year', 'time'],
            ['relation', 'node_rel', 'year_rel', 'time']
            ],
        'is_relation_lower_time': [
            ['relation', 'node', 'year', 'time'],
            ['relation', 'node_rel', 'year_rel', 'time']
            ],
        }
    for item, idxs in dict_set.items():
        try:
            sc.init_set(item, idx_sets=idxs[0], idx_names=idxs[1])
            print('- Set {} was initialized.'.format(item))
        except:
            pass
    # 2) Adding parameters
    data = {
        'relation_activity_time': [
            ['relation', 'node', 'year', 'node', 'technology', 'year',
             'mode', 'time'],
            ['relation', 'node_rel', 'year_rel', 'node_loc', 'technology',
             'year_act', 'mode', 'time']
            ],
        'relation_lower_time': [
            ['relation', 'node', 'year', 'time'],
            ['relation', 'node_rel', 'year_rel', 'time']
            ],
        'relation_upper_time': [
            ['relation', 'node', 'year', 'time'],
            ['relation', 'node_rel', 'year_rel', 'time']
            ],
        'emission_factor_time': [
            ['node', 'technology', 'year', 'year', 'mode', 'emission', 'time'],
            ['node', 'technology', 'year_vtg', 'year_act', 'mode', 'emission',
             'time'],
            ],
        }

    for item, idxs in data.items():
        try:
            sc.init_par(item, idx_sets=idxs[0], idx_names=idxs[1])
            print('- Parameter {} was initialized.'.format(item))
        except:
            pass

    # 3) Adding variables
    data = {
        'STORAGE': [
            ['node', 'technology', 'level', 'commodity', 'year', 'time'],
            ['node', 'technology', 'level', 'commodity', 'year', 'time'],
            ],
        }

    for item, idxs in data.items():
        try:
            sc.init_var(item, idx_sets=idxs[0], idx_names=idxs[1])
            print('- Variable {} was initialized.'.format(item))
        except:
            pass