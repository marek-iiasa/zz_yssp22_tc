# -*- coding: utf-8 -*-
"""
This script does the following:
    1. initializes sets and parameters needed for the modeling of storage
    2. adds storage representation (pumped hydro or reservoir hydro, etc.) to
    an existing model (clones into a new model)
    3. if needed, add the parametrization of water flows

The input data should be provided through an Excel file (no hardcoded data
here in python)

"""
import pandas as pd
import os
from itertools import product
path_files = (r'C:\Users\zakeri\Documents\Github\time_clustering' +
              r'\scenario work\add_storage_tech')
os.chdir(path_files)
from copy_par import tec_parameters_copier


# Initializing storage sets and parameters if needed
def init_storage(sc):
    sc.check_out()
    # 1) Adding sets
    dict_set = {'storage_tec': None,
                'level_storage': None,
                'map_tec_storage': ['node', 'technology', 'storage_tec',
                                    'level', 'commodity'],
                 }
    for item, idxs in dict_set.items():
        try:
            sc.init_set(item, idx_sets=idxs)
        except:
            pass
    # 2) Adding parameters
    idx_par = ['node', 'technology', 'level', 'commodity', 'year', 'time']
    dict_par = {'time_order': ['lvl_temporal', 'time'],
                'storage_self_discharge': idx_par,
                'storage_initial': idx_par,
                 }

    for item, idxs in dict_par.items():
        try:
            sc.init_par(item, idx_sets=idxs)
        except:
            pass

    sc.commit('')


# A function for adding storage technologies to an existing scenario
def add_storage(sc, setup_file, lvl_temporal, init_items=False):

    # 1) Initialization if needed
    if init_items:
        init_storage(sc)

    # 2) Adding required sets and parameters for storage technologies
    df = (pd.ExcelFile(setup_file)).parse('storage')
    df = df.loc[df['active'] == 'yes']

    sc.check_out()

    # 2.1) Adding storage technologies
    all_tecs = df['technology'].dropna().tolist()
    sc.add_set('technology', all_tecs)

    # 2.2) Adding missing commodities and levels
    for par, column in product(['input', 'output'], ['commodity', 'level']):
        item_list = df[par + '_' + column].dropna().tolist()
        for item in item_list:
            sc.add_set(column,  item.split('/'))

    # 2.3) Adding storage to set technology and level_storage
    d_stor = df.loc[df['storage_tec'] == 'yes']
    storage_tecs = d_stor['technology'].tolist()
    sc.add_set('storage_tec', storage_tecs)

    storage_lvls = d_stor['input_level'].tolist()
    sc.add_set('level_storage', storage_lvls)

    # 2.4) Adding mapping of charger-discharger technologies to their storage
    for i in d_stor.index:
        if d_stor['node_loc'][i] != 'all':
            nodes = d_stor['node_loc'][i].split('/')
        else:
            node_exclude = d_stor['node_exclude'][i].split('/')
            nodes = [x for x in sc.set('node') if
                     x not in ['World'] + node_exclude]
        tec = d_stor['technology'][i]
        tecs = df.loc[df['storage_tec'] == tec]['technology'].tolist()
        for t, node in product(tecs, nodes):
            sc.add_set('map_tec_storage', [node, t, tec,
                                           d_stor['input_level'][i],
                                           d_stor['input_commodity'][i]])
    print('- Storage sets and mappings added.')

    # 3) Adding parameter "time_seq" for time order
    parname = 'time_order'
    df2 = pd.DataFrame(index=[0], columns=['lvl_temporal', 'time',
                                          'value', 'unit'])
    if lvl_temporal:
        timap = sc.set('map_temporal_hierarchy')
        times = timap.loc[timap['lvl_temporal'] == lvl_temporal,
                          'time'].tolist()
    else:
        times = ['year']
        print('>Warning<: scenario has no time steps at the level specified!')

    for ti in range(len(times)):
        d = df2.copy()
        d['time'] = times[ti]
        d['value'] = ti + 1
        d['lvl_temporal'] = lvl_temporal
        d['unit'] = '-'
        sc.add_par(parname, d)

    sc.commit('setup added')

    # 4) Parametrization of storage technologies
    model_yrs = [int(x) for x in sc.set('year') if int(x) >= sc.firstmodelyear]
    df = df.set_index('technology')
    removal = []
    for tec in df.index:
        tec_ref = df.loc[tec, 'tec_from']
        if df.loc[tec, 'node_loc'] == 'all':
            node_exclude = d_stor['node_exclude'][i].split('/')
            nodes = [x for x in sc.set('node') if
                     x not in ['World'] + node_exclude]
            nodes_ref = nodes
        else:
            nodes = df.loc[tec, 'node_loc'].split('/')
            nodes_ref = df.loc[tec, 'node_from'].split('/')

        sc.check_out()
        # 4.1) Adding input and output of storage technology
        for par in ['input', 'output']:
            df_ref = sc.par(par, {'technology': tec_ref, 'node_loc': nodes})

            # if empty finds another technology with the same lifetime
            n = 0
            while df_ref.empty:
                df_lt = sc.par('technical_lifetime', {'node_loc': nodes})
                lt = float(df_lt.loc[df_lt['technology'] == tec_ref
                                     ]['value'].mode())
                tec_lt = list(set(df_lt.loc[df_lt['value'] == lt
                                           ]['technology']))[n]
                n = n + 1
                df_ref = sc.par(par, {'technology': tec_lt, 'node_loc': nodes})

            df_new = df_ref.copy()
            df_new['technology'] = tec
            com_list = df.loc[tec, par + '_commodity']
            if not pd.isna(com_list):
                com_list = com_list.split('/')
                for com in com_list:
                    num = com_list.index(com)
                    df_new['commodity'] = com
                    df_new['level'] = df.loc[tec,
                                             par + '_level'].split('/')[num]
                    df_new['value'] = float(str(df.loc[tec, par + '_value']
                                                ).split('/')[num])
                    sc.add_par(par, df_new)
        print('- Storage "input" and "output" parameters',
              'configured for {}.'.format(tec))

        # 4.2) Adding storage reservoir parameters
        if tec in storage_tecs:
            par_list = ['storage_self_discharge', 'storage_initial']
            for parname in par_list:
                cols = sc.idx_names(parname) + ['unit', 'value']
                d = pd.DataFrame(index=product(model_yrs, times),
                                 columns=cols)
                d['technology'] = tec
                d['year'] = [i[0] for i in d.index]
                d['time'] = [i[1] for i in d.index]
                d['level'] = df.loc[tec, 'input_level']
                d['commodity'] = df.loc[tec, 'input_commodity']

                if parname == 'storage_initial':
                    slicer = [x for x in d.index if x[1] == times[0]]
                    d = d.loc[slicer, :]
                    d['value'] = df.loc[tec, parname]
                    d['unit'] = 'GWa'
                else:
                    d['value'] = df.loc[tec, parname]
                    d['unit'] = '-'

                for node in nodes:
                    d['node'] = node
                    d = d.reset_index(drop=True)
                    sc.add_par(parname, d)
            print('- Storage reservoir parameters added for {}'.format(tec))

        # Transferring historical activity if needed
        if not pd.isna(df.loc[tec, 'historical']):
            tec_hist = df.loc[tec, 'historical']
            for parname in ['historical_activity', 'historical_new_capacity']:
                hist = sc.par(parname, {'technology': tec_hist,
                                        'node_loc': nodes})
                hist['technology'] = tec
                sc.add_par(parname, hist)
            removal = removal + [[tec_hist, nodes]]

        sc.commit('')

        # 4.3) Copying all other parameters from a reference technology
        par_excl = [x for x in sc.par_list() if
                    any(y in x for y in ['bound_',
                                         'historical',
                                         'relation_'])]
        par_excl = par_excl + ['input', 'output', 'emission_factor']

        pars = [x for x in df.columns if x in sc.par_list() and x not in
                ['storage_self_discharge', 'storage_initial'] and x in
                ['relation_activity_time', 'relation_upper_time',
                 'relation_lower_time']
                ]

        # Building dictionary of required changes in parameters from Excel
        dict_ch = {}
        for parname in pars:
            value = float(df.loc[tec, parname])
            dict_ch[parname] = [{'node_loc': [nodes]}, {'value': value}]
                
        # Copying parameters from existing to new technologies
        d1, d2 = tec_parameters_copier(sc, sc, tec_ref, tec, nodes_ref, nodes,
                                       add_tec=False, dict_change=dict_ch,
                                       par_exclude=par_excl,
                                       par_remove='all', test_run=False)
    sc.check_out()
    if not df['historical'].empty:
        for i, parname in product(removal, ['historical_activity',
                                            'historical_new_capacity']):
            hist = sc.par(parname, {'technology': i[0], 'node_loc': i[1]})
            sc.remove_par(parname, hist)
        print('- Historical data of {} was'.format(removal),
              'removed after introducing new storage technologies.')
    sc.commit('')

    print('- Storage parameterization done successfully for all technologies.')
    return all_tecs


# Adding mapping sets of new parameters
def mapping_sets(sc, par_list=['relation_lower_time', 'relation_upper_time']):
    sc.check_out()
    for parname in par_list:
        setname = 'is_' + parname

        # initiating the sets
        idx_s = sc.idx_sets(parname)
        idx_n = sc.idx_names(parname)
        try:
            sc.set(setname)
        except:
            sc.init_set(setname, idx_sets=idx_s, idx_names=idx_n)
            print('- Set {} was initiated.'.format(setname))

        # emptying old data in sets
        df = sc.set(setname)
        sc.remove_set(setname, df)

        # adding data to the mapping sets
        df = sc.par(parname)
        if not df.empty:
            for i in df.index:
                d = df.loc[i, :].copy().drop(['value', 'unit'])
                sc.add_set(setname, d)

            print('- Mapping sets updated for "{}"'.format(setname))
    sc.commit('')


# %% Sample input data
if __name__  == ' __main__':
    import message_ix
    import ixmp as ix
    from timeit import default_timer as timer
    from datetime import datetime

    mp = ix.Platform(name='ene_ixmp', jvmargs=['-Xms800m', '-Xmx8g'])

    # test one country: 'MESSAGE_ID', 'test_t4', 3
    # test Central Asia (5 region): 'MESSAGE_CASm', 'baseline_t12', 10
    # test global model R11: 'ENGAGE_SSP2_v4.1.2', 'baseline_t12', 13
    
    # Reference scenario to clone from
    model = 'ENGAGE_SSP2_v4.1.2'
    scen_ref = 'baseline_t12'
    version_ref = 13
    
    # File name for the Excel file of input data
    filename = 'AddSetup_R11.xlsx'
    setup_file = path_files + '\\' + filename
    
    # Naming convention for water commodity and supply technology for hydropower
    water_com = 'water'  
    water_supply_tec = 'water_inflow'
    
    
    solve = True         # if True, solving scenario at the end

    sc_ref = message_ix.Scenario(mp, model, scen_ref, version_ref)

    start = timer()
    sc = sc_ref.clone(model, scen_ref + '_stor', keep_solution=False)

    # Parameterization of storage
    lvl_temporal = [x for x in sc.set('lvl_temporal') if x not in ['year']][0]
    # sc.discard_changes()
    tecs = add_storage(sc, setup_file, lvl_temporal, init_items=False)
    
    # Adding an unlimited source of water (this can be revisited or renamed)
    # For example, in the global model, there is water extraction level
    # This part can be specified later in Excel too.
    sc.check_out()
    sc.add_set('technology', water_supply_tec)
    
    for tec in ['pump', 'inflow_dummy']:
        df = sc.par('output', {'technology': tec})
        df['technology'] = water_supply_tec
        df['level'] = list(set(sc.par('input', {'technology': tec,
                                        'commodity': water_com})['level']))[0]
        sc.add_par('output', df)
    
    # Adding relation activity for year equivalent of each storage technology
    df = sc.par('relation_activity_time', {'technology': 'gas_cc',
                                           'relation': 'gas_cc_year'})
    df_lo = sc.par('relation_lower_time', {'relation': 'gas_cc_year'})

    for t in tecs:
        rel = t + '_year'
        sc.add_set('relation', rel)
        nodes = list(set(sc.par('output', {'technology': t})['node_loc']))
        df_t = df.loc[df['node_loc'].isin(nodes)].copy()
        df_t['relation'] = rel
        df_t['technology'] = t
        sc.add_par('relation_activity_time', df_t)

        # relation upper and lower
        df_l = df_lo.loc[df_lo['node_rel'].isin(nodes)].copy()
        df_l['relation'] = rel
        sc.add_par('relation_lower_time', df_l)
        sc.add_par('relation_upper_time', df_l)

    # Adding new hydropower plants to flexibility and reliability parameters
    data_update = {'relation_activity_time': 'oper_res',
                   'relation_total_capacity': 'res_marg'}
    nodes = list(set(sc.par('relation_activity_time',
                            {'technology': 'hydro_dam'})['node_loc']))
    for parname, rel in data_update.items():

        df = sc.par(parname, {'relation': rel, 'technology': 'hydro_lc',
                              'node_rel': nodes})
        for t in ['turbine', 'turbine_dam']:
            df['technology'] = t
            sc.add_par(parname, df)

    # Adding upper bound on activity of dam hydro based on historical data
    df = sc.par('bound_activity_up', {'technology': 'hydro_lc',
                                      'node_loc': nodes})
    df['technology'] = 'turbine_dam'
    sc.add_par('bound_activity_up', df)
    sc.commit('')

    # Updating mapping sets of relations
    mapping_sets(sc)

    end = timer()
    print('Elapsed time for adding storage setup:',
          int((end - start)/60),
          'min and', round((end - start) % 60, 2), 'sec.')

    # 5) Solving the model
    if solve:
        case = sc.model + '__' + sc.scenario + '__v' + str(sc.version)
        print('Solving scenario "{}" in "{}" mode, started at {}, please wait.'
              '..!'.format(case, 'MESSAGE', datetime.now().strftime('%H:%M:%S')))

        start = timer()
        sc.solve(model='MESSAGE', case=case, solve_options={'lpmethod': '4'})
        end = timer()
        print('Elapsed time for solving scenario:', int((end - start)/60),
              'min and', round((end - start) % 60, 2), 'sec.')
    # sc.remove_solution()
    # sc.commit('')
    # sc.discard_changes()
    # sc.to_excel(path_xls+'\\'+caseName + '.xlsx')