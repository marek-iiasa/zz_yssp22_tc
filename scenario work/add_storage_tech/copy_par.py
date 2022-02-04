# -*- coding: utf-8 -*-
"""
This scripts copies parameters of one technology from an existing MESSAGE 
model/scenario (sc_ref) and does the specified changes,
then adds those parameters to a new technology in another scenario
"""

import pandas as pd

# Main function
def tec_parameters_copier(
        sc_ref, sc_new, tec_ref, tec_new, node_ref='all', node_new='all',
        mode_ref=None, mode_new=None,
        add_tec=False, par_copy='all', dict_change={}, par_exclude=[],
        par_remove=[], test_run=True):

    if not test_run:
        if add_tec and not tec_new in set(sc_new.set('technology')):
            sc_new.check_out()
            sc_new.add_set('technology', tec_new)
            sc_new.commit('')
            print('> New technology "{}" added to the scenario.'.format(
                tec_new))

    if par_copy == 'all':
        par_list = [x for x in sc_ref.par_list() if
                    'technology' in sc_ref.idx_names(x)]
    else:
        par_list = par_copy
    par_list = [x for x in par_list if
                [y for y in ['node','node_loc','node_rel'] if
                 y in sc_ref.idx_names(x)]]

    par_dict1={}
    par_dict2={}

    year_new = sc_new.set('year').tolist()

    # First, loading availabe data from each scenario
    for parname in par_list:
        node_cols = [x for x in sc_ref.idx_names(parname) if 'node' in x]
        year_cols = [x for x in sc_ref.idx_names(parname) if 'year' in x]
        if 'node_loc' in node_cols:
            node_col = 'node_loc'
        else:
            node_col = node_cols[0]
        
        # Copying data from selected nodes or all nodes
        if node_ref == 'all':
            df_par1 = sc_ref.par(parname, {'technology': tec_ref})
        else:
            df_par1 = sc_ref.par(parname, {'technology': tec_ref,
                                           node_col: node_ref})
        if "mode" in sc_ref.idx_sets(parname) and mode_ref:
            df_par1 = df_par1.loc[df_par1["mode"] == mode_ref].copy()
        for year_col in year_cols:
            df_par1 = df_par1.loc[df_par1[year_col].isin(year_new)].copy()

        df_par2 = pd.DataFrame()
        if tec_new in set(sc_new.set('technology')):
            if node_new == 'all':
                df_par2 = sc_new.par(parname, {'technology': tec_new})
            else:
                df_par2 = sc_new.par(parname, {'technology': tec_new,
                                               node_col: node_new})

        if not df_par1.empty:
            par_dict1[parname] = df_par1
        if not df_par2.empty:
            par_dict2[parname] = df_par2

    if par_remove == 'all':
        par_remove = [x for x in list(set(par_dict2.keys())) if
                      x not in par_exclude]
    par_diff = [x for x in par_dict1.keys() if
                x not in list(set(par_dict2.keys())) + par_exclude]
    par_add = par_diff + par_remove
    print('> These parameters copied for technology {} in node {}:'.format(
        tec_new, node_new))

    # Second, copying the difference between the two scenarios,
    # removing extra parameters, and changing some if needed
    if not test_run:

        if sc_new.has_solution():
            sc_new.remove_solution()
        sc_new.check_out()
        for parname in par_add:
            print(parname)
            if parname in par_dict1.keys():
                df_copy = par_dict1[parname].copy()
                
                # renaming nodes if needed
                if node_ref != 'all':
                    for node_r, node_n in zip(node_ref, node_new):
                        df_copy = df_copy.replace({node_r: node_n})
                
                # Renaming technology
                df_copy['technology'] = tec_new
                
                # Renaming mode
                if mode_new and "mode" in sc_new.idx_sets(parname):
                    df_copy['mode'] = mode_new
                    
            else:
                df_copy = pd.DataFrame()

            if parname in par_remove and parname in par_dict2.keys():
                sc_new.remove_par(parname, par_dict2[parname])
            if parname not in par_exclude and not df_copy.empty:
                sc_new.add_par(parname, df_copy)

            if parname in dict_change.keys():
                df_change = df_copy.copy()
                for column in dict_change[parname][0].keys():
                    df_change = df_change.loc[df_change[column].isin(
                        dict_change[parname][0][column])]

                sc_new.remove_par(parname, df_change)
                for column in dict_change[parname][1].keys():
                    df_change[column] = dict_change[parname][1][column]
                sc_new.add_par(parname,df_change)

        sc_new.commit('')
    return par_dict1, par_dict2
