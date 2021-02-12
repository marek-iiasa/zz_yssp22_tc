# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 15:06:04 2021

@author: zakeri
"""

import ixmp as ix
import message_ix
from timeit import default_timer as timer
from datetime import datetime


# Input data
model = 'MESSAGE_CASm'
scenario = "jh_protocol"
version = 2
new_scenario = 'jh_protocol_test'
run_mode = 'MESSAGE'


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
sc = sc_ref.clone(scenario=new_scenario)

# Removing the solution
sc.remove_solution()

# %% Doing some edits if needed (scenario protocol)
sc.check_out()
# 1) making inv_cost of wind and solar zero
df = sc.par('inv_cost', {'technology': ['solar_pv_ppl', 'wind_ppl']})
df['value'] = 0
sc.add_par('inv_cost', df)

# 2) making inv_cost of pumped hydro zero
df = sc.par('inv_cost', {'technology': ['hydro_pump', 'pump', 'turbine']})
df['value'] = 0
sc.add_par('inv_cost', df)

# 3) adding a renewable electricity target of 50% in 2030 and 80% in 2050 for the whole region
df = sc.par('relation_activity_time', {'relation': 'share_renewable'})
# First, removing hydro from renewable share
sc.remove_par('relation_activity_time', df)
# Second, adding a share for solar and wind
df = df.loc[df['technology'].isin(['solar_pv_ppl', 'wind_ppl',
                                   'elec_t_d_cas'])]  # needed as the basis for share
# Third changing the share value to e.g. 50% for 2030 and 80% for 2050
df.loc[(df['technology'] == 'elec_t_d_cas') & (
    df['year_rel'].isin([2030, 2035, 2040])), 'value'] = -0.5
df.loc[(df['technology'] == 'elec_t_d_cas') & (
    df['year_rel'].isin([2045, 2050, 2055, 2060])), 'value'] = -0.8
sc.add_par('relation_activity_time', df)

# 4) Removing bound activity up and down for generation technologies
# BZ: is not needed, there is no bound on generation of any plant
# We can increase the penetration rate and growth rate of renewables
df = sc.par('growth_activity_up', {'technology': ['solar_pv_ppl', 'wind_ppl']})
df['value'] = 0.075
sc.add_par('growth_activity_up', df)

for parname in ['initial_new_capacity_up', 'initial_activity_up']:
    df = sc.par(parname, {'technology': ['solar_pv_ppl','wind_ppl']})
    df['value'] = 0.05    # increasing the penetration rate
    sc.add_par(parname, df)
# 5) Remove capacity up and down for generation technologies.
# BZ: not needed, there is no bound on capacity of any technology in the model

# 6) Create a relation that if 1 GW of turbine is installed 1 GW of pump is also installed.
# BZ: not needed. This is already essential in the storage equations.

# Commit at the end of changes
sc.commit('')

# Updating the mapping of relations (needed whenever relation_activity_time is changed)
update_mapping_sets(sc)

# %% Solving
case = sc.model + '__' + sc.scenario + '__v' + str(sc.version)
print('Solving scenario "{}" in "{}" mode, started at {}, please wait...'
      '!'.format(case, run_mode, datetime.now().strftime('%H:%M:%S')))
start = timer()
sc.solve(model=run_mode, case=case, solve_options={'lpmethod': '4'},
         var_list=['STORAGE', 'STORAGE_INIT'])
end = timer()
print('Elapsed time for solving:', int((end - start)/60), 'min and', round((
        end - start) % 60, 2), 'sec.')

# %% Postprocessing and plotting
from matplotlib import pyplot as plt
node = 'TAJ'
pumped_hydro = True
yr = 2030

# Storage technology: 'hydro_dam': reservoir hydro, 'hydro_pump': pumped hydro
if pumped_hydro:
    tec_st = 'hydro_pump'
else:
    tec_st = 'hydro_dam'

# Time slices
times = [x for x in sc.set('time') if x != 'year']

# Capacity of storage (GW)
act_dam = sc.var('ACT', {'node_loc': node, 'technology': tec_st,
                         'year_act': yr, 'time': times})['lvl'].sum()
cap_dam = sc.var('CAP', {'node_loc': node,
                         'technology': tec_st, 'year_act': yr})['lvl'].sum()
cf = sc.par('capacity_factor', {'node_loc': node,
                         'technology': tec_st, 'year_act': yr})['value'].mean()
act_max = sc.var('ACT', {'node_loc': node, 'time': times,
                         'technology': tec_st, 'year_act': yr})['lvl'].max()

# Dividing capacity by max of ACT should be lower thaninput duration_time
dur_rel = act_max / (cap_dam * cf)
input_dur = sc.par('duration_time')
time_duration = float(input_dur.loc[input_dur['time'] == '1', 'value'])

if dur_rel > time_duration:
    print('Warning: Capacity of storage do not match its activity!!!')

# Initial value of storage
init = float(sc.var("STORAGE_INIT", {'node': node, 'technology': tec_st,
                         'year': yr, 'time': times})['lvl'])

# The optimal value of the initial value
initial_percent = (init / time_duration) / cap_dam
print('- The initial content of {} is {} of storage capacity.'.format(
    tec_st, str(initial_percent * 100).split(".")[0] + '%'))

# Plotting the state of charge of storage
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

# Plotting the activity of different technologies
# Plot for water
if pumped_hydro:
    tec_list = ['turbine', 'pump', 'inflow_up_amu', 'inflow_up_amu2']
else:
    tec_list = ['turbine_dam', 'inflow_up_amu', 'inflow_up_amu2']

act = sc.var("ACT", {'node_loc': node, 'technology': tec_list,
                     'year_act': yr, 'time': times}
             ).groupby(['time', 'technology']).sum().reset_index()

fig = plt.figure('water')
for tec in tec_list:
    y = act.loc[act['technology'] == tec, 'lvl']
    if 'pump' in tec:
        y = -y
    plt.step(times, y, label=tec, where='mid')

# Laying demand on the same plot
dem = sc.par('demand', {'node': node, 'commodity': 'water-amu',
                        'year': yr, 'time': times})
plt.step(dem['time'], dem['value'], label='demand', where='mid')

# Adding legend
plt.legend(loc='upper right', ncol=2)
plt.title('Water demand and activity of storage technologies in {}'.format(yr))

# Plot for energy
if pumped_hydro:
    tec_list = ['turbine', 'pump', 'wind_ppl', 'solar_pv_ppl', 'gas_ppl',
                'coal_ppl']
else:
    tec_list = ['turbine_dam', 'wind_ppl', 'solar_pv_ppl', 'gas_ppl',
                'coal_ppl']

act = sc.var("ACT", {'node_loc': node, 'technology': tec_list,
                     'year_act': yr, 'time': times}
             ).groupby(['time', 'technology']).sum().reset_index()
act['time'] = [int(x) for x in act['time']]
act = act.sort_values(['time'])

fig = plt.figure('energy')
for tec in tec_list:
    y = act.loc[act['technology'] == tec, 'lvl']
    if 'pump' in tec:
        y = -y
    plt.step(times, y, label=tec, where='mid')

# Laying demand on the same plot
dem = sc.var('ACT', {'node_loc': node, 'technology': ['elec_t_d'],
                     'year_act': yr, 'time': times}
             ).groupby(['time']).sum()
dem.index = [int(x) for x in dem.index]
dem = dem.sort_index()
plt.step(dem.index, dem['lvl'], label='demand', where='mid')

# Adding legend
plt.legend(loc='upper right', ncol=2)
plt.title('Electricity demand and activity of technologies (GWa) in {}'.format(yr))