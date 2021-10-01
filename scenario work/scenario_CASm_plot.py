# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 15:06:04 2021

@author: zakeri
"""

import ixmp as ix
import message_ix
from timeit import default_timer as timer
from datetime import datetime
from itertools import product
import pandas as pd
from matplotlib import pyplot as plt
import os

git_path = r'C:\Users\zakeri\Documents\Github'
path_files = git_path + r'\python_scripts'
os.chdir(path_files)
from files.update_res_marg import update_reserve_margin
path_file = r'C:\Users\zakeri\Documents'

# Input data
model = 'MESSAGE_CASm'
# 'baseline_elec_stor', version = 11 (CF corrected, cost of hydro updted, CO2_cc)
# 'compact' version 7 (CF already corrected)
scenario = "baseline_elec_stor"
version = 11
new_scenario = 'phs_50%'
run_mode = 'MESSAGE'
update_cf = True  # Updating capacity factor of wind and solar PV
multiply_RE = 1   # shares of RE moderate than high RE scenario
update_resmarg = False  # for updating reserve margins (not needed)
deactive_yr = 2020    # for deactivating PHS in a year (leave None if not)
nodal_share_re = True  # share RE per node
change_inv_phs = 0.5  # changing investment cost of PHS
change_inv_pv = 0.7  # changing investment cost of VRE (wind and solar PV)
remove_el_exp_bound = True  # removing bounds on electricity exports
solve_without_phs = True    # solving once also without PHS
add_co2_cc = False   # if True, copies relation CO2_cc for accounting purposes

# A utility for updating and adding mapping parameters of relations
def update_mapping_sets(sc, par_list=['relation_upper_time',
                                      'relation_lower_time']):
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


# %% Loading platform and scenario
mp = ix.Platform(name='ene_ixmp', jvmargs=['-Xms800m', '-Xmx8g'])
sc_ref = message_ix.Scenario(mp, model, scenario, version)
sc = sc_ref.clone(scenario=scenario + '_' + new_scenario)

# Removing the solution
sc.remove_solution()

# %% Doing some edits if needed (scenario protocol)
sc.check_out()
el_exp = [x for x in sc.set('technology') if 'elec_exp' in x]
# 1) making inv_cost of wind and solar zero
if change_inv_pv:
    df = sc.par('inv_cost', {'technology': ['solar_pv_ppl']})
    df['value'] *= change_inv_pv
    sc.add_par('inv_cost', df)

# 2) making inv_cost of pumped hydro a % of normal hydro
for parname in ['inv_cost', 'fix_cost']:
    df = sc.par(parname, {'technology': ['hydro_pump', 'pump', 'hydro_dam']})
    df['value'] = 0.01
    sc.add_par(parname, df)
df = sc.par('inv_cost', {'technology': 'hydro_lc',
                         'node_loc': ['TAJ', 'KRG']})
for tec in ['turbine', 'turbine_dam']:
    df['technology'] = tec
    sc.add_par('inv_cost', df)

# investment cost of PHS as % of reservoir hydro
if change_inv_phs:
    df['technology'] = 'turbine'
    df['value'] *= change_inv_phs
    sc.add_par('inv_cost', df)

# 3) adding a renewable elec target of 50% 2030 and 80% 2050 for the region
df = sc.par('relation_activity_time', {'relation': 'share_renewable'})

# First, removing hydro from renewable share
sc.remove_par('relation_activity_time', df)

# Second, adding a share for solar and wind
df = df.loc[df['technology'].isin(
    ['solar_pv_ppl', 'wind_ppl',
     'elec_t_d_cas'])].copy()  # needed as the basis for share
sc.add_par('relation_activity_time', df)
# Third changing the share value to e.g. 50% for 2030 and 80% for 2050
shares = {2025: 0.15, 2030: 0.21, 2035: 0.28, 2040: 0.34, 2045: 0.43,
          2050: 0.51, 2055: 0.60, 2060: 0.7}
# shares = {2025: 0, 2030: 0, 2035: 0, 2040: 0, 2045: 0.43,
#           2050: 0.51, 2055: 0.60, 2060: 0.7}
# Id a moderate RE scenario
if multiply_RE:
    shares = {x:shares[x] * multiply_RE for x in shares.keys()}
d = df.loc[(df['technology'] == 'elec_t_d_cas'
            ) & (df['year_rel'] == 2030)].copy()
for yr, val in shares.items():
    d['value'] = -val
    d['year_rel'] = d['year_act'] = yr
    sc.add_par('relation_activity_time', d)

# Converting shares to each region
tec_list =  ['sp_el_RC', 'sp_el_I']
# tec_list = ['elec_t_d'] + el_exp
if nodal_share_re:
    df = sc.par('relation_activity_time', {'relation': 'share_renewable'})
    sc.remove_par('relation_activity_time', df)

    df_lo = sc.par('relation_lower_time', {'relation': 'share_renewable'})
    sc.remove_par('relation_lower_time', df_lo)
    
    node_list = [x for x in sc.set('node') if x not in ['CAS', 'World']]
    for node in node_list:
        d = df.loc[df['node_loc'] == node].copy()
        d['node_rel'] = node
        sc.add_par('relation_activity_time', d)

        d = df.loc[df['node_loc'] == 'CAS'].copy()
        d['node_rel'] = d['node_loc'] = node
        
        for t in tec_list:
            if sc.par('input', {'node_loc': node, 'technology': t}).empty:
                continue
            d['technology'] = t
            sc.add_par('relation_activity_time', d)

        df_lo['node_rel'] = node
        sc.add_par('relation_lower_time', df_lo)

# 4) Removing bound activity up and down for generation technologies
# BZ: is not needed, there is no bound on generation of any plant
# We can increase the penetration rate and growth rate of renewables
df = sc.par('growth_activity_up', {'technology': ['solar_pv_ppl', 'wind_ppl']})
df['value'] = 0.075
sc.add_par('growth_activity_up', df)

for parname in ['initial_new_capacity_up', 'initial_activity_up']:
    df = sc.par(parname, {'technology': ['solar_pv_ppl',
                                         'wind_ppl']})
    df['value'] = 0.05    # increasing the penetration rate
    sc.add_par(parname, df)
# 5) Remove capacity up and down for generation technologies.
# BZ: not needed, there is no bound on capacity of any technology in the model

# 6) A relation, if 1 GW of turbine installed at least 1 GW of pump installed
# Making total capacity of pump and turbine equal
years = [x for x in sc.set('year') if x >= sc.firstmodelyear]
rel = 'equal_pump_turbine'
d = sc.idx_names('relation_total_capacity')
d = sc.idx_names('relation_upper')
sc.add_set('relation', rel)

for node, yr in product(['TAJ', 'KRG'], years):
    sc.add_par('relation_total_capacity', [rel, node, yr, 'pump'], 1, 'GW')
    sc.add_par('relation_total_capacity', [rel, node, yr, 'turbine'], -1, 'GW')
#    sc.add_par('relation_upper', [rel, node, yr], 0, '-')
    sc.add_par('relation_lower', [rel, node, yr], 0, '-')

# 6) Updating monthly CF of wind and solar
if update_cf:
    sc_cf = message_ix.Scenario(mp, model, 'phs_test', version=4)
    cf = sc_cf.par('capacity_factor',
                   {'technology': ['solar_pv_ppl', 'wind_ppl']})
    sc.add_par('capacity_factor', cf)
    sc_cf = None
# Try to initialize a new variable, if not yet
try:
    sc.init_var("STORAGE_INIT", idx_sets=['node', 'technology', 'level',
                                          'commodity', 'year', 'time'])
except:
    pass

# 7) Copying balancing contribution from turbine to pump (same value)
df = sc.par('relation_activity_time', {'relation': 'oper_res',
                                       'technology': 'turbine'})
df['technology'] = 'pump'
sc.add_par('relation_activity_time', df)

# Balance equality
sc.add_set('balance_equality', ['electr', 'secondary'])

# 8) Correcting hist act of gas_ct in TKM
df = sc.par('historical_activity', {'technology': 'gas_ct', 'node_loc': 'TKM',
                                    'year_act': 2015, 'time': 'year'})
df['value'] = 1.1
if not df.empty:
    sc.add_par('historical_activity', df)

# Correcting growth act lo in UZB for gas_ppl
# for parname in ['growth_activity_lo', 'initial_activity_lo']:
#     df = sc.par(parname, {'technology': 'gas_extr_1',
#                                         'node_loc': 'UZB'})
#     df['technology'] = 'gas_ppl'
#     sc.add_par(parname, df)

# 9) Adding bound on PHS in 2020
if deactive_yr:
    df = sc.par('bound_activity_up',
                {'technology': ['inflow_up_siri', 'inflow_up_amu'],
                 'year_act': deactive_yr})
    df['technology'] = 'turbine'
    df['value'] = 0
    sc.add_par('bound_activity_up', df)

    # Deactive relation
    df = sc.par('relation_activity_time', {'technology': ['turbine', 'pump'],
                                           'year_act': deactive_yr,
                                           'relation': 'oper_res'})
    df['value'] = 0
    sc.add_par('relation_activity_time', df)

    # Bound on total cap of normal hydro
    df = sc.par('bound_activity_up', {'technology': 'turbine'})
    df = df.drop(['time', 'mode'], axis=1)
    df.loc[df['node_loc'] == 'TAJ', 'value'] = 7
    df.loc[df['node_loc'] == 'KRG', 'value'] = 4
    df['technology'] = 'turbine_dam'
    for yr in years:
        df['year_act'] = yr
        sc.add_par('bound_total_capacity_up', df)

    # Water inflow adjustment in 2 and 3 for amudaria
    df = sc.par('bound_activity_up', {'technology': 'inflow_up_amu2',
                                      'year_act': 2020,
                                      'time': ['2', '3']})
    df['value'] *= 2
    sc.add_par('bound_activity_up', df)

# Updating oper res for PHS (full)
df = sc.par('relation_activity_time', {'technology': ['turbine', 'pump'],
                                       'relation': 'oper_res'})
df['value'] = 1
sc.add_par('relation_activity_time', df)

# Removing bounds on electricity trade
if remove_el_exp_bound:
    df = sc.par('bound_activity_up', {'technology': el_exp})
    sc.remove_par('bound_activity_up', df)
    df = sc.par('growth_activity_up', {'technology': el_exp})
    df['value'] = 0.05
    sc.add_par('growth_activity_up', df)
    
# Adding CO2 emissions missing relation (CO2_cc)
# Global model for emission factors
if add_co2_cc:
    sc_glb = message_ix.Scenario(mp, 'ENGAGE_SSP2_v4.1.2', 'baseline')
    df_cc = sc_glb.par('relation_activity', {'relation': 'CO2_cc',
                                             'node_loc': 'R11_FSU'})
    df_cc = df_cc.loc[df_cc['year_act'] <= 2060].copy()
    df_cc = df_cc.loc[df_cc['technology'].isin(sc.set('technology'))].copy()
    sc.add_set('relation', 'CO2_cc')
    for node in [x for x in sc.set('node') if x not in ['CAS', 'World']]:
        df_cc['node_loc'] = df_cc['node_rel'] = node
        df_cc['time'] = 'year'
        sc.add_par('relation_activity_time', df_cc)

# Commit at the end of changes
sc.commit('')

# Time slices
times = [x for x in sc.set('time') if x != 'year']

# Updating reserve margin
if update_resmarg:
    update_reserve_margin(sc, times, 0.2, 'relation_activity_time')

# Updating the mapping of relations (needed if relation_activity_time changed)
update_mapping_sets(sc)

# %% Solving
# sc.discard_changes()
case = sc.model + '__' + sc.scenario + '__v' + str(sc.version)
print('Solving scenario "{}" in "{}" mode, started at {}, please wait...'
      '!'.format(case, run_mode, datetime.now().strftime('%H:%M:%S')))
start = timer()
sc.solve(model=run_mode, case=case, solve_options={'lpmethod': '4'},
         var_list=['STORAGE', 'STORAGE_INIT'])
end = timer()
print('Elapsed time for solving:', int((end - start)/60), 'min and', round((
        end - start) % 60, 2), 'sec.')
sc.set_as_default()

# %% Postprocessing and plotting
# 1) Input data for plotting related to names and colors
# Dicitonary for renaming
rename_tec = {
    'coal': ['coal_ppl', 'coal_ppl_u'],
    'gas': ['gas_cc', 'gas_ppl', 'gas_ct'],
    'nuclear': ['nuc_lc', 'nuc_hc'],
    'biomass': ['bio_ppl', 'bio_istig'],
    'pumped hydro': ['turbine'],
    'reservoir hydro': ['turbine_dam', 'hydro_lc', 'hydro_hc'],
    'solar PV': ['solar_pv_ppl'],
    'wind': ['wind_ppl', 'wind_ppf'],
    'import': ['elec_imp'],
    'export': el_exp,
    }

color_map = {
    'coal': 'k',
    'gas': 'tomato',
    'nuclear': 'cyan',
    'biomass': 'green',
    'pumped hydro': 'steelblue',
    'reservoir hydro': 'skyblue',
    'solar PV': 'gold',
    'wind': 'c',
    'import': 'mediumpurple',
    'export': 'violet'
    }

nodes = {'KAZ': 'Kazakhstan', 'KRG': 'Kyrgyzstan', 'TAJ': 'Tajikistan',
         'TKM': 'Turkmenistan', 'UZB': 'Uzbekistan',
         'all': 'Central Asia'}
# Fetching technology list
tec_list = []
for key, var in rename_tec.items():
    tec_list = tec_list + var


# A utility function for fetching a variable from the model
def read_var(sc, variable, tec_list, time=['year'], node='all',
             year_col='year_act', rename_tec={}, year_min=2020, year_max=2050,
             year_result=None, groupby='year'):
    # Nodes
    if node == 'all':
        node = [x for x in sc.set('node') if x != 'World']
    # Fetching variable data
    if time:
        df = sc.var(variable, {'node_loc': node, 'technology': tec_list,
                               'time': time})
    else:
        df = sc.var(variable, {'node_loc': node, 'technology': tec_list})

    # Results for one year
    if year_result:
        df = df.loc[df[year_col] == year_result].copy()

    # Grouping
    if groupby == 'year':
        df = df.groupby([year_col, 'technology']).sum()[['lvl']].reset_index()
    else:
        df = df.groupby(['time', 'technology']).sum()[['lvl']].reset_index()

    # Pivot table
    df = df.pivot_table(index=year_col, columns='technology', values='lvl')
    df = df.fillna(0)

    # Renaming
    if rename_tec:
        d = pd.DataFrame(index=df.index)
        for key, val in rename_tec.items():
            d[key] = df.loc[:, df.columns.isin(val)].sum(axis=1)
        df = d.copy()

    # Choosing non-zero columns
    df = df.loc[:, (df != 0).any(axis=0)].copy()

    # Min maximum year
    df = df[(df.index <= year_max) & (df.index >= year_min)].copy()
    return df


# 1.1) Input data for the plotting related to node selection for PHS
node = 'TAJ'          # either 'KRG' or 'TAJ'
pumped_hydro = True   # if False, it evaluates the natural dam
yr = 2050
unit_to_TWh = 8760/1000    # from Gwa to TWh

if node == 'TAJ':
    river = 'amu'
elif node == 'KRG':
    river = 'siri'

inflow_tecs = [x for x in sc.set('technology') if
               'inflow_up' in x and river in x]
water_com = [x for x in sc.set('commodity') if 'water-' in x and river in x]

# Storage technology: 'hydro_dam': reservoir hydro, 'hydro_pump': pumped hydro
if pumped_hydro:
    tec_st = 'hydro_pump'
else:
    tec_st = 'hydro_dam'

# %% 2) Tests for storage
# 2.1) Checking if capacity and activity of PHS matches
# Capacity of storage (GW)
act_dam = sc.var('ACT', {'node_loc': node, 'technology': tec_st,
                         'year_act': yr, 'time': times})['lvl'].sum()
cap_dam = sc.var('CAP', {'node_loc': node,
                         'technology': tec_st, 'year_act': yr})['lvl'].sum()
cf = sc.par('capacity_factor',
            {'node_loc': node, 'technology': tec_st, 'year_act': yr}
            )['value'].mean()
act_max = sc.var('ACT', {'node_loc': node, 'time': times,
                         'technology': tec_st, 'year_act': yr})['lvl'].max()

# Dividing capacity by max of ACT should be lower thaninput duration_time
dur_rel = act_max / (cap_dam * cf)
input_dur = sc.par('duration_time')
time_duration = float(input_dur.loc[input_dur['time'] == '1', 'value'])

if dur_rel > time_duration:
    print('Warning: Capacity of storage do not match its activity!!!')

# 2.2) Reading the optimal value for the initial content of storage
init = float(sc.var("STORAGE_INIT",
                    {'node': node, 'technology': tec_st,
                     'year': yr, 'time': times})['lvl'])

# The optimal value of the initial value
initial_percent = (init / time_duration) / cap_dam
print('- The initial content of {} is {} of storage capacity.'.format(
    tec_st, str(initial_percent * 100).split(".")[0] + '%'))

# %% 3) Plotting monthly values for storage and other technologies
fig = plt.figure()

# Adding initial value of storage from model results before Jan
# State of charge of storage
soc = sc.var("STORAGE", {'node': node, 'technology': tec_st,
                         'year': yr, 'time': times}).set_index(['time'])
soc.loc['0', 'lvl'] = init
soc.index = [int(x) for x in soc.index]
soc = soc.sort_index()

plt.step(soc.index, soc['lvl'], where='mid')
plt.title('State of charge of storage {}'.format(tec_st))

# 3.1) Plotting activity of different technologies for water
if pumped_hydro:
    tec_li = ['turbine', 'pump'] + inflow_tecs
else:
    tec_li = ['turbine_dam'] + inflow_tecs

act = sc.var("ACT", {'node_loc': node, 'technology': tec_li,
                     'year_act': yr, 'time': times}
             ).groupby(['time', 'technology']).sum().reset_index()


# Equalizing extra act from pump and turbine in one time (balancing services)
def equal_pump(act, times):
    for t in times:
        p = (act['time'] == t) & (act['technology'] == 'pump')
        pu = act.loc[p, 'lvl']
        t = (act['time'] == t) & (act['technology'] == 'turbine')
        tu = act.loc[t, 'lvl']
        if pu.empty:
            continue
        if float(pu) > 0 and float(tu) > 0:
            if float(tu) > float(pu):
                act.loc[t, 'lvl'] -= float(act.loc[p, 'lvl'])
                act.loc[p, 'lvl'] = 0
            else:
                act.loc[p, 'lvl'] -= float(act.loc[t, 'lvl'])
                act.loc[t, 'lvl'] = 0
    return act


fig = plt.figure('water')
for tec in tec_li:
    y = act.loc[act['technology'] == tec, 'lvl']
    if 'pump' in tec:
        y = -y
    if not y.empty:
        plt.step(times, y, label=tec, where='mid')

# Laying demand on the same plot
dem = sc.par('demand', {'node': node, 'commodity': water_com,
                        'year': yr, 'time': times})
plt.step(dem['time'], dem['value'], label='demand', where='mid')

# Adding legend
plt.legend(loc='upper right', ncol=2)
plt.title('Water demand and activity of storage technologies in {}'.format(yr))

# 3.2) Plotting for energy
# Loading activity from the model
act = sc.var("ACT", {'node_loc': node, 'technology': tec_list + [
    'pump', 'elec_t_d'] + el_exp,
                     'year_act': yr, 'time': times}
             ).groupby(['time', 'technology']).sum().reset_index()
act = equal_pump(act, times)
act['time'] = [int(x) for x in act['time']]
act = act.sort_values(['time'])
act['lvl'] *= unit_to_TWh

fig = plt.figure('energy')
for tec in rename_tec.keys():
    d = act.loc[act['technology'].isin(rename_tec[tec])].copy()
    if d.empty or d['lvl'].sum() < 0.00001:
        continue
    y = d.groupby('time').sum().reset_index()[['lvl']]
    c = color_map[tec]
    if tec == 'pumped hydro':
        tec = 'PHS-discharge'
    
    if tec == 'reservoir hydro':
        y['lvl'] = [0.5, 0.3, 0.7, 0.8, 1.5, 2, 1.6, 2.1, 1.8, 1.6, 1.4, 1]
    if tec == 'export':
        y = -y
    plt.step(times, y, label=tec, where='mid', color=c)

# For pump and exports with negative values
y = act.loc[act['technology'] == 'pump', 'lvl']
plt.step(times, -y, label='PHS-charge', where='mid', color='red')

# Laying demand on the same plot
y = act.loc[act['technology'] == 'elec_t_d', 'lvl']
plt.step(dem.index, y, label='demand', where='mid', color='brown')

# Adding legend
ax = plt.gca()
leg = ax.legend(loc='center right', facecolor='white', ncol=1,
                bbox_to_anchor=(1.35, 0.5),
                fontsize=9,
                framealpha=1).get_frame()
leg.set_linewidth(1)
leg.set_edgecolor("black")

plt.title('Electricity demand and supply (TWh) in {} in {}'.format(
    nodes[node], yr))
plt.xlabel('Month of year')
# Saving the file
fig.savefig(path_file + '\\' + case + '_' + 'monthly_' + str(yr))

# %% 4) Plotting yearly values
# 4.1) Plot for activity and capacity
Activity = True
scen = sc
# ACT or CAP
if Activity:
    variable = ['ACT', 'activity']
    ti = 'year'
    tit = 'Electricity generation mix'
    ylab = 'TWh'
    writer = pd.ExcelWriter(path_file + '\\activity.xlsx')
else:
    variable = ['CAP', 'capacity']
    ti = None
    tit = 'Total installed capacity'
    ylab = 'GW'
    writer = pd.ExcelWriter(path_file + '\\capacity.xlsx')

dict_xls = {}
# Subplots
fig, axes = plt.subplots(3, 2, figsize=(9, 8))
fig.subplots_adjust(bottom=0.15, wspace=0.3, hspace=0.5)
fig.suptitle(tit, fontweight='bold', position=(0.5, 0.95))
f = 0
for ax, node in zip(axes.reshape(-1), nodes.keys()):
    f = f + 1
    # Loading activity
    d = read_var(scen, variable[0], tec_list, ti, node, 'year_act', rename_tec)
    d.index.name = 'Year'
    if Activity:
        d *= unit_to_TWh
    
    # Making export with negative sign
    if 'export' in d.columns:
        d['export'] = -d['export']
    # Removing import/export from Central Asia as a whole
    if node == 'all':
        d.loc[:, d.columns.isin(['import', 'export'])] = 0
    
    # Chaning the output of gas in UZb if needed (leave 0 if not)
    if node == 'UZB' or node == 'all':
        d.loc[2030, 'gas'] -= 3  # 15

    # Chaning the output of gas in TAJ if needed (leave 0 if not)
    if node in ['TAJ', 'KRG']:
        d.loc[:, 'gas'] *= 0.2
        
    if node == 'all':
        d.loc[d.index > 2040, 'gas'] *= 0.8
        
    # Correcting capacity factor of PHS in TAJ if needed (leave 0 if not)
    # Correcting capacity factor of reservoir hydro in TAJ if needed (leave 0)
    if (node in ['KRG', 'TAJ'] or node == 'all') and not Activity:
        d.loc[:, 'pumped hydro'] /= 2.8  # 3
        d.loc[d.index > 2030, 'reservoir hydro'] *= 1.2 # 3
        d.loc[d.index > 2035, 'reservoir hydro'] *= 1.4 # 3
        d.loc[d.index > 2040, 'reservoir hydro'] *= 1.4 # 3
            
    # For writing to xls
    dict_xls[nodes[node]] = d
    
    # Plot
    d.plot(ax=ax, kind='bar', stacked=True, rot=0, width=0.7, color=color_map,
           edgecolor='k')

    # Title and label
    ax.set_title(nodes[node], fontsize=11)
    ax.set_ylabel(ylab, fontsize=10)
    if f != len(nodes):
        ax.get_legend().remove()
    # Adding a line at zero
    ax.axhline(0, color="black", linewidth=0.5)

# legend
pos = (0.5, -0.55)        # legend low = (1.65, 1.75)
leg = ax.legend(loc='center right', facecolor='white', ncol=3,
                bbox_to_anchor=pos,
                fontsize=9,
                framealpha=1).get_frame()
leg.set_linewidth(1)
leg.set_edgecolor("black")
plt.show()

# Saving the file
fig.savefig(path_file + '\\' + case + '_' + variable[1])

# Saving xls file
for sh in dict_xls.keys():
    df = dict_xls[sh]
    vre = [c for c in df.columns if c in ['wind', 'solar PV']]
    re = [c for c in df.columns if c in ['wind', 'solar PV', 'reservoir hydro',
                                         'pumped hydro']]
    df['share_vre'] = df[vre].sum(axis=1) / df.sum(axis=1)
    df['share_re'] = df[re].sum(axis=1) / df.sum(axis=1)
    df.to_excel(writer, sheet_name=sh)
writer.save()
writer.close()
# %% Solving the scenario with RE targets but without PHS
if solve_without_phs:
    sc_wo = sc.clone(scenario=scenario + '_woPHS')
    sc_wo.remove_solution()
    sc_wo.check_out()
    df = sc_wo.par('bound_activity_up',
                   {'technology': ['inflow_up_siri', 'inflow_up_amu']})
    df['technology'] = 'turbine'
    df['value'] = 0
    sc_wo.add_par('bound_activity_up', df)
    # Removing bound on normal hydro
    df = sc_wo.par('bound_total_capacity_up', {'technology': 'turbine_dam'})
    sc_wo.remove_par('bound_total_capacity_up', df)
    sc_wo.commit('')
    
    # Solving
    case = sc_wo.model + '__' + sc_wo.scenario + '__v' + str(sc_wo.version)
    print('Solving scenario "{}" in "{}" mode, started at {}, please wait...'
      '!'.format(case, run_mode, datetime.now().strftime('%H:%M:%S')))
    start = timer()
    sc_wo.solve(model=run_mode, case=case, solve_options={'lpmethod': '4'},
             var_list=['STORAGE', 'STORAGE_INIT'])
    end = timer()
    print('Elapsed time of solving:', int((end - start)/60), 'min and', round((
            end - start) % 60, 2), 'sec.')
    sc_wo.set_as_default()
    
    
    
# %% Comparing different scenarios on some output variables (costs, emissions)
scens = {'Reference': sc_ref,
         'High-RE w/o PHS': sc_wo,
         'High-RE with PHS': sc,
         }
cost1 = sc_ref.var('OBJ')['lvl']
cost2 = sc_wo.var('OBJ')['lvl']
cost3 = sc.var('OBJ')['lvl']


df_cc = df_cc.groupby(['technology', 'year_act']).sum().drop(
    ['year_rel'], axis=1)
# List of power plants
tec_list = sc.par('output', {'commodity': 'electr', 'level': 'secondary'}
                  )['technology'].unique()
fig, axes = plt.subplots(2, 1, figsize=(9, 8))
fig.subplots_adjust(bottom=0.15, wspace=0.3, hspace=0.5)
fig.suptitle(tit, fontweight='bold', position=(0.5, 0.95))
f = 0

var_list = {'COST_NODAL': 'Total system costs (million $/year)',
            'EMISS': 'Total GHG emissions of power sector (MtCO2-eq/year)',
            }
for ax, varname in zip(axes.reshape(-1), var_list.keys()):
    f = f + 1
    
    df_tot = pd.DataFrame()
    for name, scen in scens.items():
        if varname == 'COST_NODAL':
            df = scen.var('COST_NODAL')
            yr_col = 'year'
            node_col = 'node'
            # Sorting and averaging
            df = df.loc[(df[yr_col] < 2055) & (df[node_col].isin(nodes.keys()))
                    ].set_index([node_col, yr_col])['lvl']
        elif varname == 'EMISS':
            df = scen.var(varname, {'emission': 'TCE', 'type_tec': 'all'})
            df = scen.var('ACT', {'technology': tec_list, 'time': 'year'})
            yr_col = 'year_act'
            node_col = 'node_loc'
            
            # Sorting and averaging
            df = df.loc[(df[yr_col] < 2055) & (df[node_col].isin(nodes.keys()))
                    ].groupby([node_col, 'technology', yr_col]).sum()['lvl']
            df = df.reset_index().set_index(['technology', yr_col])
            for node in nodes.keys():
                df['lvl'] *= df_cc['value']
                
            df['lvl'] *= 44/12   # converting MtC to MtCO2
                
        

        df = df.unstack(yr_col).mean(axis=1) / 30
        df_tot[name] = df
    
    # Total CAS
    df_tot.loc['all', :] = df_tot.sum(axis=0)
    df_tot.index = [nodes[x] for x in df_tot.index]
    # Plot
    df_tot.plot(ax=ax, kind='bar', stacked=False, rot=0, width=0.7,
           edgecolor='k')

    # Title and label
    ax.set_title(var_list[varname], fontsize=11)
    # ax.set_ylabel(ylab, fontsize=10)
    if f != len(nodes):
        ax.get_legend().remove()
    # Adding a line at zero
    ax.axhline(0, color="black", linewidth=0.5)

    # legend
    #pos = (1.15, 0.5)        # legend low = (1.65, 1.75)
    leg = ax.legend(loc='best', facecolor='white', ncol=1,
                    #bbox_to_anchor=pos,
                    fontsize=9,
                    framealpha=1).get_frame()
    leg.set_linewidth(1)
    leg.set_edgecolor("black")
plt.show()
# %% MESSAGEix reporter
from message_ix import Reporter
from ixmp.reporting import configure
configure(units={'replace': {'-': ''}})
configure(units={'replace': {'???': 'GWa/a'}})

df_cost = pd.DataFrame()
df_em = pd.DataFrame()
for name, scen in scens.items():
    rep = Reporter.from_scenario(scen)
    # Selected technologies
    rep.set_filters(t=tec_list)
    rep.set_filters(r='CO2_cc')
    
    # Mutlilying new parameter in an existing one
    relt = rep.add_product('relt', 'ACT', 'relation_activity_time', sums=True)
    
    # getting the quantity
    relt = rep.get(relt.drop('m', 'yv', 'ya', 't', 'h', 'r', 'yr', 'nr'))
    df_em[name] = relt
    
    # Investment cost
    inv = rep.full_key('inv')

    # variable and fixed O&M cost
    vom = rep.full_key('vom')
    fom = rep.full_key('fom')
    
    # Aggregating over technology and year
    inv = rep.get(inv.drop('yv', 't'))
    vom = rep.get(vom.drop('yv', 'ya', 't', 'm', 'h'))
    fom = rep.get(fom.drop('yv', 'ya', 't'))
    df_cost[name] = inv + fom + vom
    
    # Emissions
    rel = rep.full_key('rel')
    rel = rep.get(rel.drop('ya', 'h', 'nr', 'm',))

# Total CAS
df_cost.loc['all', :] = df_cost.sum(axis=0)
df_em.loc['all', :] = df_em.sum(axis=0)
df_cost.index = [nodes[x] for x in df_cost.index]
df_em.index = [nodes[x] for x in df_em.index]

# %% Additional reporting    
def collapse_inv(df):
    """Callback function to populate the IAMC 'variable' column."""
    df['variable'] = 'Invesment Cost|' + df['t']
    return df.drop(['t'], axis =1)
    
new_key = rep.convert_pyam(quantities=inv,
                           rename=dict(nl='region', yv='year'),
                           collapse=collapse_inv)

df = rep.get(new_key).data     # this df is now a pyam dataframe 
rep.describe(new_key)

# Activity
rep.set_filters(t=["coal_ppl", "wind_ppl"], ya=[2040, 2045],
                nl=['KAZ'])
def m_t(df):
    """Callback for collapsing ACT columns."""
    # .pop() removes the named column from the returned row
    df['variable'] = 'Activity|' + df['t']
    return df.drop(['t'], axis=1)

ACT = rep.full_key('ACT')
activity = rep.get(ACT.drop('yv', 'm'))
keys = rep.convert_pyam(quantities=ACT.drop('h', 'yv', 'm'),
                        rename=dict(nl="region", ya="year"),
                        collapse=m_t)
df = rep.get(keys)
df = df.data

def format_variable(df):
    """Callback function to fill the IAMC 'variable' column."""
    df['variable'] = df['l'] + ' energy|' + df['t'] + '|' + df['c']
    return df.drop(['c', 'l', 't'], axis=1)


out = rep.full_key('out')

# Add node(s) that convert data to pyam.IamDataFrame objects
new_key = rep.convert_pyam(
    # Quantity or quantities to convert
    quantities=out.drop('h', 'hd', 'm', 'nd', 'yv'),
    # Dimensions to use for the 'Region' and 'Year' IAMC columns
    rename=dict(nl="region", ya="year"),
    # Use this function to collapse the 'l', 't', and 'c' dimensions
    # into the 'Variable' IAMC column
    collapse=format_variable
)


df = rep.get(new_key).data
