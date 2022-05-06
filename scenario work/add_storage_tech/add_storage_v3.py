# -*- coding: utf-8 -*-
"""
This script does the following (includes modes of operation for storage):
    1. initializes sets and parameters needed for the modeling of storage
    2. adds storage representation (pumped hydro or reservoir hydro, etc.) to
    an existing model (clones into a new model)

The input data should be provided through an Excel file (no hardcoded data
here in python)

"""
import pandas as pd
from itertools import product


# Initializing storage sets and parameters if needed
def init_storage(sc):
    sc.check_out()
    # 1) Adding sets
    idx = ['node', 'technology', 'mode', 'level', 'commodity', 'year', 'time']
    dict_set = {'storage_tec': None,
                'level_storage': None,
                'map_tec_storage': ['node', 'technology', 'mode',
                                    'storage_tec', 'mode',
                                    'level', 'commodity', 'lvl_temporal'],
                'is_relation_lower_time': ['relation', 'node', 'year', 'time'],
                'is_relation_upper_time': ['relation', 'node', 'year', 'time'],
                 }
    for item, idxs in dict_set.items():
        try:
            sc.init_set(item, idx_sets=idxs)
        except:
            if item == 'map_tec_storage':
                sc.remove_set(item)
                sc.init_set(item, idx_sets=idxs,
                            idx_names=['node', 'technology', 'mode',
                                       'storage_tec', 'mode_storage',
                                       'level', 'commodity', 'lvl_temporal'])
            else:
                pass
    # 2) Adding parameters
    
    dict_par = {'time_order': ['lvl_temporal', 'time'],
                'storage_self_discharge': idx,
                'storage_initial': idx,
                 }

    for item, idxs in dict_par.items():
        try:
            sc.init_par(item, idx_sets=idxs)
        except:
            if "storage" in item:
                sc.remove_par(item)
                sc.init_par(item, idx_sets=idxs)
            else:
                pass

    sc.commit('')


# A function for adding storage technologies to an existing scenario
def add_storage(sc, setup_file, init_items=False, remove_ref=False):

    # 1) Initialization if needed
    if init_items:
        init_storage(sc)

    # 2) Adding required sets and parameters for storage technologies
    df = pd.ExcelFile(setup_file, engine="openpyxl").parse('storage')
    df = df.loc[df['active'] == 'yes']

    sc.check_out()

    # 2.1) Adding storage technologies and modes
    all_tecs = df['technology'].dropna().tolist()
    sc.add_set('technology', all_tecs)
    sc.add_set('mode', list(set(df['mode'].dropna())))
    df = df.set_index(['technology', 'mode']).sort_index()

    # 2.2) Adding missing commodities and levels
    for par, column in product(['input', 'output'], ['commodity', 'level']):
        item_list = df[par + '_' + column].dropna().tolist()
        for item in item_list:
            sc.add_set(column, item.split('/'))

    # 2.3) Adding storage to set technology and level_storage
    d_stor = df.loc[df['storage_tec'] == 'yes']
    storage_tecs = [x[0] for x in d_stor.index]
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
        tec = i[0]
        mode = i[1]
        tecs = df.loc[df['storage_tec'] == tec + "," + mode].index
        for (t, mode_t), node in product(tecs, nodes):
            sc.add_set('map_tec_storage', [node, t, mode_t, tec, mode,
                                           d_stor['input_level'][i],
                                           d_stor['input_commodity'][i],
                                           d_stor['lvl_temporal'][i],
                                           ])
    
        # 3) Parameter "time_order" for the order of time slices in each level
        parname = 'time_order'
        df2 = pd.DataFrame(index=[0], columns=['lvl_temporal', 'time',
                                              'value', 'unit'])
        ti_map = sc.set('map_temporal_hierarchy')
        times = ti_map.loc[ti_map['lvl_temporal'] == d_stor['lvl_temporal'][i],
                          'time'].tolist()
        # Adding order of times
        for ti in range(len(times)):
            d = df2.copy()
            d['time'] = times[ti]
            d['value'] = ti + 1
            d['lvl_temporal'] = d_stor['lvl_temporal'][i]
            d['unit'] = '-'
            sc.add_par(parname, d)

    print('- Storage sets and mappings added.')

    # 4) Parametrization of storage technologies
    try:
        model_yrs = [int(x) for x in sc.set('year') if int(x) >= sc.firstmodelyear]
    except:
        model_yrs = sc.set('year').to_list()
    
    removal = []
    df = df[~df.index.duplicated(keep='first')].copy()
    for i in df.index:
        # Refrence technology
        tec_ref = df.loc[i, 'tec_from']
        
        # Time slices (relevant to this technology)
        times = ti_map.loc[ti_map['lvl_temporal'] == df.loc[i, 'lvl_temporal'],
                          'time'].tolist()
        
        # Nodes
        if df.loc[i, 'node_loc'] == 'all':
            node_exclude = df.loc[i, 'node_exclude'].split('/')
            nodes = [x for x in sc.set('node') if
                     x not in ['World'] + node_exclude]
            nodes_ref = nodes
        else:
            nodes = df.loc[i, 'node_loc'].split('/')
            nodes_ref = df.loc[i, 'node_from'].split('/')
        
        # 4.1) Adding input and output of storage reservoir technology
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
            
            # Slicing for timeslices relevant to this technology
            df_new = df_ref.loc[df_ref["time"].isin(times)].copy()
            
            # Updating technology and mode
            df_new['technology'] = i[0]
            df_new['mode'] = i[1]
            
            # Ensuring "time" and "time_origin"/"time_dest" match
            time_col = [x for x in sc.idx_names(par) if "time_" in x][0]
            df_new[time_col] = df_new["time"]
            
            # Making sure node_dest/node_origin are the same as node_loc
            node_col = [x for x in sc.idx_names(par) if
                        'node' in x and x != 'node_loc'][0]
            df_new[node_col] = df_new['node_loc']
            
            com_list = df.loc[i, par + '_commodity']
            if not pd.isna(com_list):
                for num, com in enumerate(com_list.split('/')):
                    lvl = df.loc[i, par + '_level'].split('/')[num]
                    df_new['commodity'] = com
                    df_new['level'] = lvl
                    df_new['value'] = float(str(df.loc[i, par + '_value']
                                                ).split('/')[num])
                    sc.add_par(par, df_new)
        print('- Storage "input" and "output" parameters',
              'configured for "{}".'.format(i))

        # 4.2) Adding storage reservoir parameters
        if i[0] in storage_tecs:
            par_list = ['storage_self_discharge', 'storage_initial']
            
            for parname in par_list:
                cols = sc.idx_names(parname) + ['unit', 'value']
                d = pd.DataFrame(index=product(model_yrs, times),
                                 columns=cols)
                d['technology'] = i[0]
                d['year'] = [y[0] for y in d.index]
                d['time'] = [y[1] for y in d.index]
                d['mode'] = i[1]
                d['level'] = df.loc[i, 'input_level']
                d['commodity'] = df.loc[i, 'input_commodity']

                if parname == 'storage_initial':
                    slicer = [x for x in d.index if x[1] == times[0]]
                    d = d.loc[slicer, :]
                    d['value'] = df.loc[i, parname]
                    d['unit'] = 'GWa'
                else:
                    d['value'] = df.loc[i, parname]
                    d['unit'] = '-'

                for node in nodes:
                    d['node'] = node
                    d = d.reset_index(drop=True)
                    sc.add_par(parname, d)
            print('- Storage reservoir parameters added for {}'.format(i))

        # 4.3.1) Transferring historical data if needed
        if not pd.isna(df.loc[i, 'historical']):
            tec_hist = df.loc[i, 'historical']
            for parname in ['historical_activity', 'historical_new_capacity']:
                if "activity" in parname:
                    filters = {'technology': tec_hist,
                               'node_loc': nodes, "time": times}
                else:
                    filters = {'technology': tec_hist, 'node_loc': nodes}
                hist = sc.par(parname, filters)
                
                # Adding new data
                hist['technology'] = i[0]
                if "activity" in parname:
                    hist["mode"] = i[1]
                sc.add_par(parname, hist)
                removal = removal + [(parname, tec_hist, nodes)]

        # 4.3.2) Transferring relation activity (Notice: relation capacity?)
        if not pd.isna(df.loc[i, 'relation']):
            tec_rel = df.loc[i, 'relation']
            parname = 'relation_activity_time'
            rel = sc.par(parname, {'technology': tec_rel, 'node_loc': nodes,
                                   "time": times})
            
            # Adding new data
            rel['technology'] = i[0]
            rel["mode"] = i[1]
            sc.add_par(parname, rel)
            removal = removal + [(parname, tec_rel, nodes)]

        # 4.3) Adding all other parameters and changes in values specified in Excel
        # Excluding bound and relations
        par_excl = [x for x in sc.par_list() if any(y in x for y in [
            'bound_', 'historical_', 'relation_', 'ref_'])]
        par_excl = par_excl + ['input', 'output', 'emission_factor',
                               'storage_self_discharge', 'storage_initial']
         
        par_list = [x for x in sc.par_list() if "technology" in sc.idx_sets(x)
                    and x not in par_excl]
        
        for parname in par_list:
            # Loading existing data
            node_col = [x for x in sc.idx_names(parname) if 'node' in x][0]
            d = sc.par(parname, {node_col: nodes_ref, 'technology': tec_ref})
            
            # Checking if the value is directly from Excel or as a multiplier
            if parname in df.columns:
                excl = df.loc[i, parname]
                if excl.split(':')[0] == 'value':
                    d['value'] = float(excl.split(':')[1])
                elif excl.split(':')[0] == 'multiply':
                    d['value'] *= float(excl.split(':')[1])
                
            # Renaming technology, mode, and node names
            d['technology'] = i[0]
            if "mode" in sc.idx_sets(parname):
                d["mode"] = i[1]
            for node_r, node_n in zip(nodes_ref, nodes):
                        d = d.replace({node_r: node_n})
            
            # Slicing correct timeslices
            if "time" in d.columns:
                d = d.loc[d["time"].isin(times)]
            
            # Adding the data back to the scenario
            sc.add_par(parname, d)
            
        print('- Data of "{}" copied to "{}"'.format(tec_ref, i[0]),
              'with possible updated values from Excel.')
    
    # Removing extra information after creating new storage technologies
    if remove_ref:
        for (parname, t, region) in removal:
            old = sc.par(parname, {'technology': t, 'node_loc': region})
            if not old.empty:
                sc.remove_par(parname, old)
                print('- Data of "{}" in parameter "{}"'.format(t, parname),
                      'was removed for {}'.format(region),
                      ', after introducing new storage technologies.')
    sc.commit('')
    print('- Storage parameterization done successfully for all technologies.')
    return df.index.unique().to_list()


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
    import os
    from timeit import default_timer as timer
    from datetime import datetime
    
    # Testing storage setup
    test_storage = False
    path_files = (r'C:\Users\zakeri\Documents\Github\time_clustering' +
              r'\scenario work\China\data')
    os.chdir(path_files)

    mp = ix.Platform(name='ene_ixmp', jvmargs=['-Xms800m', '-Xmx8g'])

    # test one country: 'MESSAGE_ID', 'test_t4', 3
    # test Central Asia (5 region): 'MESSAGE_CASm', 'baseline_t12', 10
    # test China: 'MESSAGEix_China', 'baseline_t48', None
    # test global model R11: 'ENGAGE_SSP2_v4.1.2', 'baseline_t12', 13
    # test R4: 'MESSAGE_R4', 'baseline_t12', 1 (4 region)
    # test R4: 'MESSAGE_R4', 'baseline_t12', 2 (4 region, last year 2055)
    
    # Reference scenario to clone from
    model = 'MESSAGEix-China'
    scen_ref = 'baseline_t48'
    version_ref = None
    
    # File name for the Excel file of input data
    filename = 'setup_storage_CHN.xlsx'
    xls_files = path_files
    setup_file = xls_files + '\\' + filename
    
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
    tecs = add_storage(sc, setup_file, init_items=True)
    
    # Adding an unlimited source of water (this can be revisited or renamed)
    # For example, in the global model, there is water extraction level
    # This part can be specified later in Excel too.
    sc.check_out()
    sc.add_set('technology', water_supply_tec)
    
    xls = pd.ExcelFile(setup_file, engine="openpyxl").parse()
    tec_charger = xls.loc[xls['section'] == 'charger', 'technology'].to_list()
    tec_discharger = xls.loc[xls['section'] == 'discharger',
                             'technology'].to_list()
    tec_water = [x for x in tec_charger if
                 water_com in set(sc.par('input', {'technology': x}
                                         )['commodity'])]
    
    for tec in tec_water:
        df = sc.par('output', {'technology': tec})
        df['technology'] = water_supply_tec
        df['level'] = list(set(sc.par('input', {'technology': tec,
                                      'commodity': water_com})['level']))[0]
        sc.add_par('output', df)
    
    # Adding relation activity for year equivalent of each storage technology
    df = sc.par('relation_activity_time', {'technology': 'gas_cc',
                                           'relation': 'gas_cc_year'})
    df_lo = sc.par('relation_lower_time', {'relation': 'gas_cc_year'})

    for (t, m) in tecs:
        rel = t + '_year'
        sc.add_set('relation', rel)
        nodes = list(set(sc.par('output', {'technology': t})['node_loc']))
        df_t = df.loc[df['node_loc'].isin(nodes)].copy()
        df_t['relation'] = rel
        df_t['technology'] = t
        df_t["mode"] = m
        sc.add_par('relation_activity_time', df_t)

        # relation upper and lower
        df_l = df_lo.loc[df_lo['node_rel'].isin(nodes)].copy()
        df_l['relation'] = rel
        sc.add_par('relation_lower_time', df_l)
        sc.add_par('relation_upper_time', df_l)
    
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
        sc.set_as_default()
    
    # Testing if storage technology works    
    if test_storage:
        # sc = message_ix.Scenario(mp, model, scen_ref + "_stor")
        sc_test = sc.clone(scenario=sc.scenario + "_test", keep_solution=False)
        sc_test.check_out()
        
        # Making capacity factor of PV zero in some time slices
        df = sc.par("capacity_factor", {"technology": "solar_pv_ppl"})
        df = df.loc[df["time"].isin(test_storage)]
        df["value"] = 0.001
        sc_test.add_par("capacity_factor", df)
        
        # Making investment cost of PV and storage near zero
        df = sc.par("inv_cost", {"technology":
                                 [
                                  "solar_pv_ppl",
                                  "battery", "battery_pcs",
                                  "turbine", "hydro_phs",
                                  ]})
        df["value"] = 0.001
        sc_test.add_par("inv_cost", df)
        
        # Removing "input" and "output" of reservoir technology
        for parname in ["input", "output"]:
            df = sc_test.par(parname, {"technology": ["battery", "hydro_phs"]})
            sc_test.remove_par(parname, df)
        sc_test.commit("")
        case = sc_test.model + '__' + sc_test.scenario + '__v' + str(sc_test.version)
        sc_test.solve(model='MESSAGE', case=case, solve_options={'lpmethod': '4'})
    
        
        
    # sc.remove_solution()
    # sc.commit('')
    # sc.discard_changes()
    # sc.to_excel(path_xls+'\\'+caseName + '.xlsx')