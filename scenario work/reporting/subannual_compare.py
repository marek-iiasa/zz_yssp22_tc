# -*- coding: utf-8 -*-
"""
This script includes some workflows to compare the input data and the results
of two scenarios;
    sc_ref: a scenario without sub-annual time slices
    sc: the corresponding scenario but with time slices
"""

# 1. Loading required packages
import ixmp as ix
import message_ix
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import gridspec
from message_ix import Reporter
from ixmp.reporting import configure


# 2. Input data
run_mode = 'MESSAGE'
mp = ix.Platform(name='ene_ixmp', jvmargs=['-Xms800m', '-Xmx8g'])

# 2.1. Reference scenario (without sub-annual time slices)
model_ref = 'ENGAGE_SSP2_v4.1.2'
scenario_ref = "baseline"
version_ref = 4

# 2.2. Scenario with sub-annual time slices
model_new = 'ENGAGE_SSP2_v4.1.2'
scenario_new = "baseline_t12"
version_new = 13

# 3. Loading scenarios and main characteristics
# 3.1. Scenarios
sc_ref = message_ix.Scenario(mp, model_ref, scenario_ref, version_ref)
sc = message_ix.Scenario(mp, model_new, scenario_new, version_new)

# 3.2. Main feature
# Nodes
regions = [x for x in sc.set('node') if x not in ['World', 'R11_GLB']]
# Sample region
reg = ['R11_LAM']

# Years
years = [x for x in sc.set('year') if x >= sc.firstmodelyear]
# Sample year
yr = [2030]

# Subannual time slices
times = [x for x in sc.set('time') if x not in ['year']]

# Electricity sectors (demand side)
sectors = ['i_spec', 'rc_spec']     # ['i_spec', 'rc_spec']

# Technologies (doesn't need to relate to sectors)
tecs = ['solar_pv_ppl'] #, 'wind_ppl']

# %% 4. Required utility functions
rename = {
    'i_spec': 'Industry',
    'rc_spec': 'Res/comm',
    'solar_pv_ppl': 'Solar PV',
    'wind_ppl': 'Wind onshore',
    }

# A function for sorting the data in pivot table format
def grouping(df, grpby=['node_loc', 'technology', 'time'],
             col_idx='time', value='value', aggregate={}, rename={}):
    # Grouping by specified indexes
    df = df.groupby(grpby).sum()[[value]].reset_index()
    # Renaming some names from MESSAGE format (optional)
    df = df.replace(rename)

    # Pivot table
    idx = [x for x in grpby if x not in [col_idx]]
    df = df.pivot_table(index=idx, columns=col_idx, values=value)
    df = df.fillna(0)

    # Aggregation
    if aggregate:
        d = pd.DataFrame(index=df.index)
        for key, val in aggregate.items():
            d[key] = df.loc[:, df.columns.isin(val)].sum(axis=1)
        df = d.copy()

    # Choosing non-zero columns
    df = df.loc[:, (df != 0).any(axis=0)].copy()
    df.index.name = None
    return df

# A function for plotting new and old data
def plot_new_old(df1, df2, tit, capacity=False):
    # df1.index = [x[0] for x in df1.index]
    # For capacity-related data no time slice needed
    if capacity:
        df2.plot(kind='bar', rot=30)
        plt.title(tit)
        
    else:
        # For not capacity-related data, sub-annual time slice does matter
        fig, axes = plt.subplots(1, 2, figsize=(8, 4),
                           # sharey=True
                           )
        fig.subplots_adjust(bottom=0.15, wspace=0.2, right=1.1)
        fig.suptitle(tit, fontweight='bold', position=(0.6, 0.95))
        gs = gridspec.GridSpec(1, 2, width_ratios=[4, 1]) 
        ax0 = plt.subplot(gs[0])
        ax1 = plt.subplot(gs[1])
        
        df2.plot(ax=ax0, kind='bar', rot=30)
        # ax0.legend(loc='center right')
        df1.plot(ax=ax1, kind='bar', rot=30)
        # ax1.legend(loc='center right', bbox_to_anchor=(2.4, 0.9))
        plt.ylim([None, 1.45 * max(df1['sub-annual'])])

        
    plt.show()


# A function for sorting time slices
def sort_time(df, times, col='time'):
    # Saving time column as category
    df[col] = df[col].astype("category")
    # Sorting
    df[col].cat.set_categories(times, inplace=True)
    return df.sort_values([col])


# A utility for calculating cumulative output
def cumulative_output(sc, df):
    dur = sc.par('duration_period').set_index(['year'])
    for i in df.columns:
        df.loc[:, i] *= float(dur.loc[i, 'value'])
    return df

# %% 5. Comparing some input data
# Notice: for sub-annual time slices, it's better to filter with "time"

# 5.1. Fetching data directly from the scenario (ixmp database)
# 5.1.1. Electricity demand by sector for one region
old = sc_ref.par('demand', {'node': reg, 'commodity': sectors, 'year': yr})
new = sc.par('demand', {'node': reg, 'commodity': sectors, 'year': yr,
                        'time': times})

# Sorting
old = grouping(old, grpby=['commodity', 'time'], col_idx='time',
               rename=rename)
new = grouping(new, grpby=['commodity', 'time'], col_idx='time',
               rename=rename)
new = new[times]
old['sub-annual'] = new.sum(axis=1)

# Plotting
plot_new_old(old, new,
             'Electricity demand (GWa) {} {}'.format(reg[0].split("_")[1],
                                                     yr[0]))

# 5.1.2. Capacity factor of one or more technologies by time for one region
old = sc_ref.par('capacity_factor', {'node_loc': reg, 'technology': tecs,
                                     'year_act': yr, 'year_vtg': yr})
new = sc.par('capacity_factor', {'node_loc': reg, 'technology': tecs,
                                 'year_act': yr, 'year_vtg': yr,
                                 'time': times})

# Sorting
old = grouping(old, grpby=['technology', 'time'], col_idx='time',
               rename=rename)
new = grouping(new, grpby=['technology', 'time'], col_idx='time',
               rename=rename)
new = new[times]
dur = sc.par('duration_time')
dur = dur.loc[dur['time'].isin(times)].copy()
old['sub-annual'] = new.mean(axis=1)

# Plotting
plot_new_old(old, new,
             'Capacity factor (-) in {}'.format(reg[0].split("_")[1]))    

# 5.2. Using "new reporting" package for fetching data
configure(units={'replace': {'-': ''}})
configure(units={'replace': {'???': 'GWa/a'}})

data = {}
for scen, name in zip([sc_ref, sc], ['old', 'new']):
    rep = Reporter.from_scenario(scen)
    # Adding filters
    rep.set_filters(t=tecs, y=yr, ya=yr, yv=yr, nl=reg, c=sectors, n=reg)
    
    # 5.2.1. Capacity factor of one or more technologies in one region
    cf = rep.full_key('capacity_factor')
    cf = rep.get(cf.drop('yv', 'ya', 'nl')
                 ).to_frame().reset_index().rename(
                     {0: 'value', 'h': 'time'}, axis=1)
    if cf.loc[0, 'time'] != 'year':
        cf = sort_time(cf, times)

    # Saving results
    data[name] = grouping(cf, grpby=['t', 'time'], col_idx='time',
                          rename=rename)

data['old']['sub-annual'] = data['new'].mean(axis=1)
# Plotting
plot_new_old(data['old'], data['new'],
             'Capacity factor (-) in {}, new reporting'.format(
                 reg[0].split("_")[1])) 

# %% 6. Looking into model results
# 6.1. Fetching results directly from the scenario (ixmp database)
# 6.1.1. Generation of one or more technologies by time for one region
old = sc_ref.var('ACT', {'node_loc': reg, 'technology': tecs, 'year_act': yr})
new = sc.var('ACT', {'node_loc': reg, 'technology': tecs, 'year_act': yr,
                     'time': times})

# Sorting
old = grouping(old, grpby=['technology', 'time'], col_idx='time', value='lvl',
               rename=rename)
new = grouping(new, grpby=['technology', 'time'], col_idx='time', value='lvl',
               rename=rename)
new = new[times]
old['sub-annual'] = new.sum(axis=1)

# Plotting
plot_new_old(old, new,
             'Electricity generation (GWa) {} {}'.format(reg[0].split("_")[1],
                                                         yr[0]))

# 6.1.2. Capacity of one or more technologies by time for one region
old = sc_ref.var('CAP', {'node_loc': reg, 'technology': tecs, 'year_act': yr})
new = sc.var('CAP', {'node_loc': reg, 'technology': tecs, 'year_act': yr})

# Sorting
old = grouping(old, grpby=['technology', 'year_act'], col_idx='year_act',
               value='lvl', rename=rename)
new = grouping(new, grpby=['technology', 'year_act'], col_idx='year_act',
               value='lvl', rename=rename)
old = old.rename({yr[0]: 'year'}, axis=1)
old.columns.rename(None, inplace=True)
old['sub-annual'] = new.sum(axis=1)

# Plotting
plot_new_old(new, old,
             'Installed capacity (GW) {} {}'.format(
                 reg[0].split("_")[1], yr[0]), True)

# %% 7) Plotting one output for all regions in one year
old = sc_ref.var('ACT', {'technology': tecs, 'year_act': yr})
new = sc.var('ACT', {'technology': tecs, 'year_act': yr, 'time': times})

# Sorting
old = grouping(old, grpby=['node_loc', 'technology', 'time'], col_idx='time',
               value='lvl', rename=rename)
new = grouping(new, grpby=['node_loc', 'technology', 'time'], col_idx='time',
               value='lvl', rename=rename)
new = new[times]
old['sub-annual'] = new.sum(axis=1)
old.index = [x[0].split('_')[1] for x in old.index]

new = old.sum(axis=0).to_frame().copy()
new.columns = ['World']

# Plotting
plot_new_old(new.T, old,
             'Electricity generation (GWa) from {} in {}'.format(tecs, yr[0]))

# 7.2) Emissions in one year
tec = 'CO2_TCE'
old = sc_ref.var('ACT', {'technology': tec, 'year_act': yr})
new = sc.var('ACT', {'technology': tec, 'year_act': yr})

# Sorting
old = grouping(old, grpby=['node_loc', 'technology', 'time'], col_idx='time',
               value='lvl', rename=rename)
new = grouping(new, grpby=['node_loc', 'technology', 'time'], col_idx='time',
               value='lvl', rename=rename)
# new = new[times]
old['sub-annual'] = new.sum(axis=1)
old.index = [x[0].split('_')[1] for x in old.index]
old *= (44/12)/1000

# old.loc['World', :] = old.sum(axis=0)
new = old.sum(axis=0).to_frame().copy()
new.columns = ['World']
# Plotting
plot_new_old(new.T, old,
             'CO2 emissions (GtCO2/yr) in {}'.format(yr[0]))

# %% 8) Plotting one output for all regions for the entire model horizon
# 8.1) Average output for all regions
old = sc_ref.var('ACT', {'technology': tec})
new = sc.var('ACT', {'technology': tec})

# Sorting
old = grouping(old, grpby=['node_loc', 'year_act'], col_idx='year_act',
               value='lvl', rename=rename)
new = grouping(new, grpby=['node_loc', 'year_act'], col_idx='year_act',
               value='lvl', rename=rename)
old['year'] = old.mean(axis=1)
old['sub-annual'] = new.mean(axis=1)
old.index = [x.split('_')[1] for x in old.index]
old *= (44/12)/1000
old = old[['year', 'sub-annual']].copy()
new = old.sum(axis=0).to_frame().copy()
new.columns = ['World']
# Plotting
plot_new_old(new.T, old, 'Average CO2 emissions (GtCO2/yr) (2020-2100)')

# %% 8.1) Total output for all regions for the entire model horizon
old = sc_ref.var('ACT', {'technology': tec})
new = sc.var('ACT', {'technology': tec})

# Sorting
old = grouping(old, grpby=['node_loc', 'year_act'], col_idx='year_act',
               value='lvl', rename=rename)
new = grouping(new, grpby=['node_loc', 'year_act'], col_idx='year_act',
               value='lvl', rename=rename)

# cumulative
old = cumulative_output(sc_ref, old).sum(axis=1).to_frame()
old.columns = ['year']
new = cumulative_output(sc, new)

old['sub-annual'] = new.sum(axis=1)
old.index = [x.split('_')[1] for x in old.index]
old *= (44/12)/1000

# old.loc['World', :] = old.sum(axis=0)
new = old.sum(axis=0).to_frame().copy()
new.columns = ['World']
# Plotting
plot_new_old(new.T, old, 'Total CO2 emissions (GtCO2) (2020-2100)')

# 8.2) Total output for one technology
tec = 'solar_pv_ppl'
unit_conv = (8760/1000) / 1000   # from GWa to PWh
title = 'Total electricity generation solar PV (PWh) 2020-2100'
old = sc_ref.var('ACT', {'technology': tec})
new = sc.var('ACT', {'technology': tec, 'time': 'year'})

# Sorting
old = grouping(old, grpby=['node_loc', 'year_act'], col_idx='year_act',
               value='lvl', rename=rename)
new = grouping(new, grpby=['node_loc', 'year_act'], col_idx='year_act',
               value='lvl', rename=rename)

# cumulative
old = cumulative_output(sc_ref, old).sum(axis=1).to_frame()
old.columns = ['year']
new = cumulative_output(sc, new)

old['sub-annual'] = new.sum(axis=1)
old.index = [x.split('_')[1] for x in old.index]
old *= unit_conv

# old.loc['World', :] = old.sum(axis=0)
new = old.sum(axis=0).to_frame().copy()
new.columns = ['World']
# Plotting
plot_new_old(new.T, old, title)