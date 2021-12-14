# -*- coding: utf-8 -*-
"""
This script does the following:
    1. initializes sets and parameters needed for the modeling of storage
    2. adds storage representation (pumped hydro or reservoir hydro, etc.) to
    an existing model (clones into a new model)

The input data should be provided through an Excel file (no hardcoded data
here in python)

"""
import pandas as pd
import os
from itertools import product
path_files = (r'C:/Downloads')
os.chdir(path_files)

from copy_par import tec_parameters_copier


# Initializing storage sets and parameters if needed
def init_storage(sc):
    sc.check_out()
    # 1) Adding sets
    idx = ['node', 'technology', 'mode', 'level', 'commodity', 'year', 'time']
    dict_set = {'storage_tec': None,
                'level_storage': None,
                'map_tec_storage': ['node', 'technology', 'mode',
                                    'storage_tec', 'mode',
                                    'level', 'commodity'],
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
                                       'level', 'commodity'])
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
def add_storage(sc, setup_file, lvl_temporal, init_items=False,
                remove_ref=False):

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
            for m in df.loc[df['technology'] == t, 'mode'].values:                
                sc.add_set('map_tec_storage', [node, t, m, tec,
                                           d_stor['mode'][i],
                                           d_stor['input_level'][i],
                                           d_stor['input_commodity'][i]])
                
                
    print('- Storage sets and mappings added.')

    # 3) Parameter "time_order" for the order of time slices in each level
    parname = 'time_order'
    df2 = pd.DataFrame(index=[0], columns=['lvl_temporal', 'time',
                                          'value', 'unit'])
    if lvl_temporal:
        timap = sc.set('map_temporal_hierarchy')
        times = timap.loc[timap['lvl_temporal'] == lvl_temporal,
                          'time'].tolist()
    else:
        times = ['year']
        print('>Warning<: scenario has no time steps at the specified level!')

    for ti in range(len(times)):
        d = df2.copy()
        d['time'] = times[ti]
        d['value'] = ti + 1
        d['lvl_temporal'] = lvl_temporal
        d['unit'] = '-'
        sc.add_par(parname, d)

    sc.commit('setup added')

    # 4) Parametrization of storage technologies
    model_yrs = [2020]#[int(x) for x in sc.set('year') if int(x) >= sc.firstmodelyear]
    df = df.set_index('technology')
    removal = []
    for tec in df.index:
        # Mode
        mode_t = df.loc[tec, 'mode']
        
        # Refrence technology
        tec_ref = df.loc[tec, 'tec_from']
        
        # Nodes
        if str(df.loc[tec, 'node_loc']) == 'all':
            node_exclude = d_stor['node_exclude'][i].split('/')
            nodes = [x for x in sc.set('node') if
                     x not in ['World'] + node_exclude]
            nodes_ref = nodes
        else:
            nodes = str(df.loc[tec, 'node_loc']).split('/')
            nodes_ref = str(df.loc[tec, 'node_from']).split('/')

        sc.check_out()
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

            df_new = df_ref.copy()
            
            # Making sure node_dest/node_origin are the same as node_loc
            node_col = [x for x in sc.idx_names(par) if
                        'node' in x and x != 'node_loc'][0]
            df_new[node_col] = df_new['node_loc']
            
            df_new['technology'] = tec
            df_new['mode'] = mode_t
            com_list = df.loc[tec, par + '_commodity']
            if not pd.isna(com_list):
                for num, com in enumerate(com_list.split('/')):
                    lvl = df.loc[tec, par + '_level'].split('/')[num]
                    df_new['commodity'] = com
                    df_new['level'] = lvl
                    df_new['value'] = float(str(df.loc[tec, par + '_value']
                                                ).split('/')[num])
                    sc.add_par(par, df_new)
        print('- Storage "input" and "output" parameters',
              'configured for "{}".'.format(tec))

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
                d['mode'] = df.loc[tec, 'mode']
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

        # 4.3.1) Transferring historical data if needed
        if not pd.isna(df.loc[tec, 'historical']):
            tec_hist = df.loc[tec, 'historical']
            for parname in ['historical_activity', 'historical_new_capacity']:
                hist = sc.par(parname, {'technology': tec_hist,
                                        'node_loc': nodes})
                
                # Adding new data
                hist['technology'] = tec
                if "activity" in parname:
                    hist["mode"] = mode_t
                sc.add_par(parname, hist)
                removal = removal + [(parname, tec_hist, nodes)]

        # 4.3.2) Transferring relation activity (Notice: relation capacity?)
        if not pd.isna(df.loc[tec, 'relation']):
            tec_rel = df.loc[tec, 'relation']
            parname = 'relation_activity_time'
            rel = sc.par(parname, {'technology': tec_rel, 'node_loc': nodes})
            
            # Adding new data
            rel['technology'] = tec
            rel["mode"] = mode_t
            sc.add_par(parname, rel)
            removal = removal + [(parname, tec_rel, nodes)]

        # 4.3) Adding some parameters and changes in values specified in Excel
        pars = [x for x in df.columns if x in sc.par_list() and x not in
        ['storage_self_discharge', 'storage_initial']
        ]
        
        for parname in pars:
            # Loading existing data
            node_col = [x for x in sc.idx_names(parname) if 'node' in x][0]
            d = sc.par(parname, {node_col: nodes_ref, 'technology': tec_ref})
            
            # Checking if the value is directly from Excel or as a multiplier
            excl = df.loc[tec, parname]
            if excl.split(':')[0] == 'value':
                d['value'] = float(excl.split(':')[1])
            elif excl.split(':')[0] == 'multiply':
                d['value'] *= float(excl.split(':')[1])
                
            # Renaming technology, mode, and node names
            d['technology'] = tec
            if "mode" in sc.idx_sets(parname):
                d["mode"] = mode_t
            for node_r, node_n in zip(nodes_ref, nodes):
                        d = d.replace({node_r: node_n})
            
            # Adding the data back to the scenario
            sc.add_par(parname, d)
            
        print('- Data of "{}" copied to "{}"'.format(tec_ref, tec),
              'for parameters {},'.format(pars), 
              'with updated values from Excel.')
        sc.commit('')
        
        # 4.4) Copying all other parameters from existing to new technologies
        par_excl = [x for x in sc.par_list() if any(y in x for y in [
            'bound_', 'historical_', 'relation_', 'ref_'])]
        par_excl = par_excl + pars + ['input', 'output', 'emission_factor']
        dict_ch = {}
        
        d1, d2 = tec_parameters_copier(
            sc, sc, tec_ref, tec, nodes_ref, nodes, add_tec=False,
            dict_change=dict_ch, par_exclude=par_excl,
            par_remove='all', test_run=False)

    # Removing extra information after creating new storage technologies
    if remove_ref:
        sc.check_out()
        for (parname, t, region) in removal:
            old = sc.par(parname, {'technology': t, 'node_loc': region})
            if not old.empty:
                sc.remove_par(parname, old)
                print('- Data of "{}" in parameter "{}"'.format(t, parname),
                      'was removed for {}'.format(region),
                      ', after introducing new storage technologies.')
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
__name__ =' __main__'
if __name__  == ' __main__':
    import message_ix
    import ixmp as ix
    from timeit import default_timer as timer
    from datetime import datetime    
    from message_ix.utils import make_df

    mp = ix.Platform(name='ene_ixmp', jvmargs=['-Xms800m', '-Xmx8g'])

    # test one country: 'MESSAGE_ID', 'test_t4', 3
    # test Central Asia (5 region): 'MESSAGE_CASm', 'baseline_t12', 10
    # test global model R11: 'ENGAGE_SSP2_v4.1.2', 'baseline_t12', 13
    # test R4: 'MESSAGE_R4', 'baseline_t12', 1 (4 region)
    # test R4: 'MESSAGE_R4', 'baseline_t12', 2 (4 region, last year 2055)
    
    # Reference scenario to clone from

    model = 'test-time'
    scen_ref = 'four-technology'
    version_ref = 10
    '''
    model = 'test-time'
    scen_ref = 'four-technology'
    version_ref = 10
    '''
    # File name for the Excel file of input data
    filename = 'GM_11R_add_storage_simple_mode.xlsx'
    xls_files = r'C:\Users\zakeri\Documents\Excel_files'
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
    
    xls = pd.ExcelFile(setup_file).parse()
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
    
    
    
    
    
    

    # Removing non-necessary parameters from technologies
    tec_list = ["river_dist", "river", "water_distribution", "dam_hydro", 
                "spillway_hydro", "pump_turb_phs", "dam_sphs", "hydro_dam"]
    par_list = ["inv_cost", "fix_cost"]
    for parname in par_list:
        df = sc.par(parname, {"technology": tec_list})
        sc.remove_par(parname, df)

    tec_list = ["river_dist", "river", "water_distribution", "dam_hydro", 
                "spillway_hydro", "pump_turb_sphs", "dam_sphs"]
    par_list = ["capacity_factor"]
    for parname in par_list:
        df = sc.par(parname, {"technology": tec_list})
        sc.remove_par(parname, df)
        df["value"] = 1
        
        sc.add_par(parname, df)       
         
        
    year_df = 2020#sc.vintage_and_active_years()
    vintage_years, act_years = 2020,2020#year_df['year_vtg'], year_df['year_act']

       
    #sc.add_set("balance_equality", ["water", "primary"])
           
                  
        #annual demand is the sum of all seasonal demand
    #water_com = {'water': 84720}									

    inflow_water = pd.DataFrame({
                'node_loc': 'Wonderland',
                'technology':'river_dist',
                'year_act':  [2020],
                'mode': 'mode', 
                'time': '1',
                'value': 100
                })           
    sc.add_par('bound_activity_up', inflow_water)
    inflow_water = pd.DataFrame({
                'node_loc': 'Wonderland',
                'technology':'river_dist',
                'year_act':  [2020],
                'mode': 'mode', 
                'time': '2',
                'value': 50
                })           
    sc.add_par('bound_activity_up',  inflow_water)             
    inflow_water = pd.DataFrame({
                'node_loc': 'Wonderland',
                'technology':'river_dist',
                'year_act':  [2020],
                'mode': 'mode', 
                'time': '3',
                'value': 20
                })           
    sc.add_par('bound_activity_up',  inflow_water)     
    inflow_water = pd.DataFrame({
                'node_loc': 'Wonderland',
                'technology':'river_dist',
                'year_act':  [2020],
                'mode': 'mode', 
                'time': '4',
                'value': 50
                })           
    sc.add_par('bound_activity_up',  inflow_water)     
               
    for t in sc.set('time'):
      if t != 'year':  
        demand_water = pd.DataFrame({
                'node': 'Wonderland',
                'commodity': 'water',
                'level': 'secondary',
                'year':  [2020],
                'time': t,
                'value': [55], 
                'unit': 'm^3/a',
                })          
          
        demand_data = make_df(demand_water)  
        sc.add_par("demand", demand_data)


    # Remove old data
    sc.remove_set("technology", "water_inflow")
    
    '''
    # Only those technologies you want to link to final demand
    water_tec = ["water_distribution"]    
    df = sc.par("output", {"technology": water_tec})
    # Remove old data
    sc.remove_par("output", df)
    # Change to year and add to the model
    df["time_dest"] = "year"
    sc.add_par("output", df)
    '''
      
    tec = ["river_dist", "water_distribution", "dam_hydro", 
                "spillway_hydro", "pump_turb_sphs", "dam_sphs"]           
    
    # Time slices other than "year"
    times = [x for x in sc.set("time") if x != "year"]
    # technologies which we need to change the "input"
    for tec in tec_list:
        df = sc.par("input", {"technology": tec, "time_origin": "year"})
        # Remove input from "year" if not needed
        sc.remove_par("input", df)
        # Add input from each time slice (h) between 1 and 12
        for h in times:
            df["time_origin"] = h
            sc.add_par("input", df)   
    '''
    # Create input
    df = sc.par("input", {"technology": "river_dist"})
    # Change tec 
    df["technology"] = "water_distribution"
    # Change level
    df["level"] = "secondary"
    sc.add_par("input", df)    
    '''
    # Update technical lifetime
    df = sc.par("technical_lifetime", {"technology": 'dam_hydro'})
    # Remove old data
    sc.remove_par("technical_lifetime", df)
    # Change to year and add to the model
    df["value"] = 500
    sc.add_par("technical_lifetime", df)    
    
    # Update technical lifetime
    df = sc.par("technical_lifetime", {"technology": 'dam_sphs'})
    # Remove old data
    sc.remove_par("technical_lifetime", df)
    # Change to year and add to the model
    df["value"] = 500
    sc.add_par("technical_lifetime", df)    
    
    # Update technical lifetime
    df = sc.par("technical_lifetime", {"technology": 'river'})
    # Remove old data
    sc.remove_par("technical_lifetime", df)
    # Change to year and add to the model
    df["value"] = 10000
    sc.add_par("technical_lifetime", df)  

    # Update technical lifetime
    df = sc.par("capacity_factor", {"technology": 'hydro_dam'})
    # Remove old data
    sc.remove_par("capacity_factor", df)
    # Change to year and add to the model
    df["value"] = 0.7
    sc.add_par("capacity_factor", df)  

    # Update technical lifetime
    df = sc.set('pump_turb_sphs2')
    # Remove old data
    sc.remove_par("capacity_factor", df)
    # Change to year and add to the model
    df["value"] = 0.7
    sc.add_par("capacity_factor", df)  
    

    sc.remove_set("technology", "hydro_lc")   
    
        
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
    # sc.remove_solution()
    
    # sc.commit('')
    # sc.discard_changes()
    # sc.to_excel(path_xls+'\\'+caseName + '.xlsx')
    
        
    # %% Plotting one output for all regions in one year
    
    tecs = ["hydro_dam", "hydro_lc","hydro_hc","wind_cv1","solar_i","solar_rc","pump_turb_sphs"]
        
    new = sc.var('ACT', {'technology': tecs, 'year_act': 2030, 'time': times})
    
    new.to_csv('H:/Things in C Drive/IIASA/Energy Group/MESSAGE/Hydropower storage representation/ACT.csv')

  