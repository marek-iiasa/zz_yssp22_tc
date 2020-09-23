# -*- coding: utf-8 -*-
"""
This script can be used to compile and report the results of one or a number of
MESSAGEix scenarios. The script reads the information from an Excel template
file, and based on that generates yearly or time slice specific reports. The
results will be imported to Excel file (name specified by the user).
"""

import ixmp as ix
import message_ix
import pandas as pd
mp = ix.Platform(name='ene_ixmp')

#%% 1) Input data for years and regions to be included
year_min = 2015
year_max = 2050
regions = ['KAZ', 'KRG', 'TAJ', 'TKM', 'UZB']
repo_path = r'C:\Users\...\Documents\Github\time_clustering\scenario_work'
file_path = repo_path + '\\reporting\\reporting_template.xlsx'
results_path = repo_path + '\\reporting'
xl_input = 'vre_use'               # sheet name for technology/definition
xl_output = 'CAS_generation-2050_by-month'

time_reporting = True      # if True, results will be reported at sub-annual time level
ref_value = True           # if True before first model year is needed
non_zero = False           # if True, the results will be only if not zero
par_ref = 'historical_activity'
commodity = ['electr', 'i_spec', 'rc_spec'] # electricity related commodities
variable = 'Generation (activity)'
years = [2050]            #  either [] for all years, or [2030] for specific years
time_exclude = ['year']

#%% 1.2) Specifiying scenario names and upload names
scen_names= [ # model, scenario, version, Excel file name
              ["MESSAGE_CASm", "baseline_t12", 8, 'baseline'],
                ["MESSAGE_CASm", "renewable-50", 4, '50% RE'],
                ["MESSAGE_CASm", "renewable-50_no-PHS", 3, '50% RE, no PHS'],
                ["MESSAGE_CASm", "renewable-70", 5, '70% RE'],
                ["MESSAGE_CASm", "renewable-70_no-PHS", 4, '70% RE, no PHS'],
                ["MESSAGE_CASm", "water-inflow-20", 2, '-20% water inflow'],
                ["MESSAGE_CASm", "water-inflow-20_renewable-50", 2, '-20% water inflow, 50% RE'],
                ["MESSAGE_CASm", "water-demand-20", 2, '+20% water demand'],
                ["MESSAGE_CASm", "water-demand-20_renewable-50", 2, '+20% water demand, 50% RE'],
            ]


#%% 2) Loading Excel file of template
filename = results_path + '\\' +  xl_output + '.xlsx'
writer = pd.ExcelWriter(filename, engine='xlsxwriter')

xls = pd.ExcelFile(file_path)
xls_sheet = xls.parse(xl_input)
xls_sheet = xls_sheet[xls_sheet['active'] == 'yes']
tec_list = xls_sheet['technology'].tolist()

# 3) Loading scenarios and generating output
for scen in scen_names:
    sc = message_ix.Scenario(mp, scen[0], scen[1], scen[2])

    if not years:
        years = [x for x in sc.set('year').tolist() if
                 x >= year_min and x <= year_max]

    times = [x for x in set(sc.set('time')) if x not in time_exclude]

    # Reading values from parameter input and output
    if commodity:
        df_inp = sc.par('input', {'commodity': commodity,
                                  'technology': tec_list, 'time': times,
                                  'year_act': years, 'node_loc': regions})
        df_inp = df_inp.drop(['year_vtg'], axis=1
                             ).groupby(['node_loc', 'year_act', 'technology',
                                        'time']).mean()

        df_out = sc.par('output', {'commodity': commodity,
                                   'technology': tec_list, 'time': times,
                                   'year_act': years, 'node_loc': regions})
        df_out = df_out.drop(['year_vtg'], axis=1
                             ).groupby(['node_loc', 'year_act', 'technology',
                                        'time']).mean()
    else:
        df_inp = pd.DataFrame(index=[0])
        df_out = pd.DataFrame(index=[0])

    # Reading output values
    year_model = [x for x in years if x >= sc.firstmodelyear]

    if isinstance(list(set(xls_sheet['parameter']))[0], str):
        parname = list(set(xls_sheet['parameter']))[0]
        df_act = sc.par(parname, {'technology': tec_list, 'node_loc': regions,
                                  'time': times})
        df_act = df_act.drop(['year_vtg'], axis=1).groupby(['node_loc',
                        'year_act', 'technology', 'time']).mean()
    elif isinstance(list(set(xls_sheet['variable']))[0], str):
        if not sc.has_solution:
            print('- WARNING: scenario has no solution, only historical'
                  ' data can be reported.')
            continue
        var_list = list(set(xls_sheet['variable']))
        df_act = pd.DataFrame()

        # Compiling results for different output variables
        for varname in var_list:
            tec_var = list(set(xls_sheet.loc[xls_sheet['variable'] == varname,
                                             'technology']))
            node_col = [x for x in sc.idx_names(varname) if 'node' in x][0]
            year_col = [x for x in sc.idx_names(varname) if
                        'year' in x and x != 'year_vtg'][0]
            if 'time' in sc.idx_names(varname):
                df_a = sc.var(varname, {'technology': tec_var,
                                        node_col: regions, 'time': times})
            else:
                df_a = sc.var(varname, {'technology': tec_var,
                                        node_col: regions})
                df_a.loc[:, 'time'] = 'year'   # An arbitrary value

            df_a = df_a.rename({node_col: 'node_loc',
                                year_col: 'year_act'}, axis=1)
            if 'year_vtg' not in df_a.columns:
                df_a.loc[:, 'year_vtg'] = 20   # An arbitrary value

            df_a = df_a.drop(['mrg', 'year_vtg'], axis=1
                             ).groupby(['node_loc', 'year_act', 'technology',
                                        'time']).sum().rename({'lvl': 'value'},
                                                              axis=1)
            df_act = df_act.append(df_a, ignore_index=False, sort=True)


    # reading historical (reference) values
    if ref_value:
        year_ref = [x for x in years if x < sc.firstmodelyear]
        df_ref = sc.par(par_ref, {'technology': tec_list, 'year_act': year_ref,
                                  'node_loc': regions, 'time': times})
        df_ref = df_ref.drop(['mode'], axis=1).groupby(['node_loc', 'year_act',
                     'technology', 'time']).sum()
    else:
        df_ref = pd.DataFrame(columns=['node_loc', 'year_act',
                     'technology', 'time']).set_index(['node_loc', 'year_act',
                     'technology', 'time'])

    df_act = df_act.loc[df_act.index.get_level_values(1).isin(year_model)]
    if not df_inp.empty:
        df_inp = df_inp.loc[(df_inp.index.isin(df_act.index)
                             )|(df_inp.index.isin(df_ref.index))]
    if not df_out.empty:
        df_out = df_out.loc[(df_out.index.isin(df_act.index)
                             )|(df_out.index.isin(df_ref.index))]

    df_act = df_act.copy().append(df_ref, ignore_index=False, sort=True)

    # Compiling results for each technology specified in Excel
    df_f = pd.DataFrame()
    for i in xls_sheet.index:
        inp = xls_sheet.loc[i, 'inp or out']
        tec = xls_sheet.loc[i, 'technology']
        slicer = (df_act.index.get_level_values('technology') == tec)
        d = df_act.loc[slicer]
        slicer_in = (df_inp.index.isin(d.index))
        slicer_out = (df_out.index.isin(d.index))
        if inp == 'input':
            df = df_inp.loc[slicer_in] * d
        elif inp == 'input-output':
            df = (df_inp.loc[slicer_in] - 1) * d

        elif inp == 'output':
            df = df_out.loc[slicer_out] * d
        else:
            df = d.copy()

        if not df.empty:
            df[variable] = xls_sheet.loc[i, 'upload']
            # value and unit
            df.loc[:, 'Unit'] = xls_sheet.loc[i, 'unit']
            df.loc[:, 'value'] *= xls_sheet.loc[i, 'conversion']

            df_f = df_f.append(df)

    df_f = df_f.reset_index().rename(
        {'node_loc': 'Region', 'year_act': 'Year'}, axis=1
        ).drop('technology', axis=1)

    # Sorting and finalizing
    if list(set(xls_sheet['method']))[0] == 'average':
        df_f = df_f.groupby(['Region', variable, 'Year', 'time', 'Unit']).mean()
    else:
        df_f = df_f.groupby(['Region', variable, 'Year', 'time', 'Unit']).sum()

    if time_reporting:
        df_f = df_f.pivot_table(index = ['Region', variable, 'Year', 'Unit'],
                            columns='time', values='value')
    else:
        df_f = df_f.reset_index().drop(['time'], axis=1)
        df_f = df_f.pivot_table(index = ['Region', variable, 'Unit'],
                            columns='Year', values='value')

    if non_zero:
        df_f = df_f[(df_f > 0).any(1)]

    # Sorting columns
    if time_reporting:
        sorter = [str(i) for i in sorted([int(x) for x in df_f.columns])]
        df_f = df_f.reindex(columns=sorter).reset_index()
    else:
        df_f = df_f.reset_index()

    # Sorting rows
    sorter = xls_sheet['upload'].unique().tolist()

    # giving a category to column that should be sorted based on a list
    df_f[variable] = df_f[variable].astype("category")
    df_f[variable].cat.set_categories(sorter, inplace=True)

    # Example of renaming regions
    df_f['Region'] = df_f['Region'].str.replace('R14_',
                                                '').str.replace('UBM', 'BMU')
    df = df_f.sort_values(['Region', variable])

    # Writing results for each scenario to one Excel sheet
    df.to_excel(writer, sheet_name = scen[3], index=False)
    print('- Results of scenario {}/{}/{} was compiled.'.format(scen[0],
                                                                scen[1], str(scen[2])))
    sc = None

# Saving and closing Excel
writer.save()
writer.close()
