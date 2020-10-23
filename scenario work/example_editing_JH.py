# -*- coding: utf-8 -*-
"""
This script shows some examples for editing a scenario or adding policies and
constraints.

"""
import ixmp as ix
import message_ix

import os
import time

os.environ["JAVA_HOME"] =  'C:/Users/hunt/.conda/envs/message_env_storage/Library/bin/server'
path_msg = r'C:\Users\hunt\.conda\envs\message_env_storage\Lib\site-packages\message_ix'

# 1.1) Specifying scenario identifiers (model/scenario/version)
model = "MESSAGE_CASm"
scenario = "baseline_elec_stor"
version = 6     # to be loaded, if exists (see 3.2.1)


# % 2) Loading a platform
# 2.1) By loading local default database
#mp = ix.Platform()
mp = ix.Platform(dbprops=r'C:/Users/hunt/.conda/envs/message_env_storage/Lib/site-packages/message_ix/model/default_new.properties')

# 2.1) Loading a database in a different path
# mp = ix.Platform(name='iiasa')

#% 3) Loading/clonning a scenario
sc = message_ix.Scenario(mp, model, scenario, version)
sc_new = sc.clone(model, scenario +'_JH10')

if sc_new.has_solution():
    sc_new.remove_solution()

#%% Required utilities
# Adding mapping sets of new parameters
def update_mapping_sets(sc, par_list=['relation_lower_time', 'relation_upper_time']):
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
#%% Changing share of variable renewable energy in 2050 (if this share exists)
sc_new.check_out()
df = sc_new.par('relation_activity_time', {'relation': 'share_renewable',
                                       'year_rel': 2050,
                                       'technology': 'elec_t_d_cas'})
# console 11 = -0.5   Console 12 = -0.95  Console 13 - -0.99   Console 14 = -1
df['value'] = -1#-0.5      # changing the value to -0.5 for 50%
sc_new.add_par('relation_activity_time', df)
sc_new.commit('')

#%% Changing the initial content of storage
sc_new.check_out()
df = sc_new.par('storage_initial', {'node': 'TAJ',
                                'technology': 'hydro_dam'})
df['value'] = 5      # changing the value
sc_new.add_par('storage_initial', df)
sc_new.commit('')

#%% Deactivating a technology (e.g., pumped hydro) to see the impact
sc_new.check_out()
df = sc_new.par('output', {'technology': 'turbine', 'commodity': 'electr',
                       })
df['value'] = 0       # changing the output value to zero (no generation)
sc_new.add_par('output', df)
sc_new.commit('')


#%% Adding a carbon budget policy
remove_old_bound = True      # removing existing bounds if exists
type_tec = 'all'             # for type of technologies
bound = 20                   # unit MtCeq/yr

sc_new.check_out()
df_old = sc_new.par('bound_emission')
sc_new.remove_par('bound_emission', df_old)

sc_new.add_par('bound_emission', ['CAS', # node that bound applies
                              'TCE', # type of emission ('TCE': total carbon equivalent)
                              type_tec,  # type of technologies included
                              2050],     # year for bound
           bound, '-')
sc_new.commit('')

#%% Limiting the activity of CCS technologies (e.g., to 50% of reference sc_newenario)
sc_new.check_out()
df = sc_new.var('ACT', {'technology': 'co2_tr_dis'})  # Loading the output activity
df = df.rename({'lvl': 'value', 'mrg': 'unit'}, axis=1)
df['value'] *= 0.5    # multiplying by 0.5, to limit to 50% of initial value
df['unit'] = 'GWa'
sc_new.add_par('bound_activity_up', df)
sc_new.commit('')



#%% Changing the inv_cost some technologies
sc_new.check_out()
tec_list = ['wind_ppl', 'wind_ppf']
df = sc_new.par('inv_cost', {'technology': tec_list})
df['value'] = 4000000          # reducing CF by 10% (multiplying by 0.9)
sc_new.add_par('inv_cost', df)
sc_new.commit('')


#%% Changing the inv_cost some technologies
sc_new.check_out()
tec_list = ['pump', 'turbine','turbine_dam']
df = sc_new.par('inv_cost', {'technology': tec_list})
df['value'] = 4          # reducing CF by 10% (multiplying by 0.9)
sc_new.add_par('inv_cost', df)
sc_new.commit('')


#%% Changing the capacity factor some technologies
sc_new.check_out()
tec_list = ['solar_pv_ppl', 'wind_ppl']
df = sc_new.par('capacity_factor', {'technology': tec_list})
df['value'] *= 0.9          # reducing CF by 10% (multiplying by 0.9)
sc_new.add_par('capacity_factor', df)
sc_new.commit('')

#%% Changing the upper bounds on activity of some trade technologies
sc_new.check_out()
for tec, val in [('coal_imp', 1), ('loil_imp', 4), ('foil_imp', 3),
        ('gas_imp', 5)]:
    df = sc_new.par('bound_activity_up', {'technology': tec})
    df['value'] *= val
    df['value'] += 1.25
    sc_new.add_par('bound_activity_up', df)
sc_new.commit('')

#%% Debugging and test (only if needed)
# Chaning the mass flow of water relative to electricity in hydropower technologies (1000 m3/s =~ 1 GW)
# For example, by increasing that by 10%, we multiply the value by 1.1
sc_new.check_out()
tec_in =['hydro_pump', 'pump', 'pump2', 'turbine', 'turbine2',  'hydro_dam']
df = sc_new.par('input', {'commodity': 'water', 'technology': tec_in})
df['value'] *= 1.1
sc_new.add_par('input', df)

tec_out =['pump', 'pump2', 'turbine', 'turbine2', 'hydro_pump',
          'hydro_dam']
df = sc_new.par('output', {'commodity': 'water', 'technology': tec_out})
df['value'] *= 1.1
sc_new.add_par('output', df)
sc_new.commit('')

#%% Deactivating the share on renewables (if exists)
sc_new.check_out()
df = sc_new.par('relation_activity_time', {'relation':'share_vre',
                                           'technology':'elec_t_d_year'})

df['value'] = 0         # minimum share
sc_new.add_par('relation_activity_time', df)
sc_new.commit('')

#%% Adding var_cost for inteconnectors to avoid circulation
elec_exp = [x for x in set(sc_new.set('technology')) if 'elec_exp' in x]  # all electricity export technologies

sc_new.check_out()
df = sc_new.par('relation_activity_time', {'relation': 'fuel_price',
                                       'technology': 'elec_imp'})
df['value'] = 15
sc_new.add_par('relation_activity_time', df)
sc_new.commit('')

#%% Adjusting supply of water (by changing the amount of water inflow in upstream)
sc_new.check_out()
tecs = [x for x in sc_new.set('technology') if 'inflow' in x]
df = sc_new.par('bound_activity_up', {'technology': tecs})
df['value'] *= 0.8    # 0.8 means: 80% of existing inflow (reducing inflow)
sc_new.add_par('bound_activity_up', df)
sc_new.commit('')

#%% Adjusting demand of water (by changing the amount of water demand)
sc_new.check_out()
coms = [x for x in sc_new.set('commodity') if 'water' in x]
df = sc_new.par('demand', {'commodity': coms})
df['value'] *= 1.2    # 1.2 means 20% higher water demand than existing data
sc_new.add_par('demand', df)
sc_new.commit('')


#%%


sc_new.check_out()
df = sc_new.par('relation_activity_time', {'relation': 'share_renewable',
                                       'year_rel': 2050,
                                       'technology': 'elec_t_d_cas'})
# console 11 = -0.5   Console 12 = -0.95  Console 13 - -0.99   Console 14 = -1
df['value'] = -1#-0.5      # changing the value to -0.5 for 50%
sc_new.add_par('relation_activity_time', df)
sc_new.commit('')


# Changing the initial content of storage
sc_new.check_out()
df = sc_new.par('storage_initial', {
                                'technology': 'hydro_dam'})
df['value'] = 500      # changing the value
sc_new.add_par('storage_initial', df)
sc_new.commit('')

# Changing the initial content of storage
sc_new.check_out()
df = sc_new.par('storage_initial', {
                                'technology': 'hydro_pump'})
df['value'] = 500      # changing the value
sc_new.add_par('storage_initial', df)
sc_new.commit('')



#% Changing the inv_cost some technologies
sc_new.check_out()
tec_list = ['wind_ppl', 'wind_ppf']
df = sc_new.par('inv_cost', {'technology': tec_list})
df['value'] = 4000000          # reducing CF by 10% (multiplying by 0.9)
sc_new.add_par('inv_cost', df)
sc_new.commit('')


#% Changing the inv_cost some technologies
sc_new.check_out()
tec_list = ['pump', 'turbine','turbine_dam']
df = sc_new.par('inv_cost', {'technology': tec_list})
df['value'] = 4          # reducing CF by 10% (multiplying by 0.9)
sc_new.add_par('inv_cost', df)
sc_new.commit('')

#%% Adding a relation between the content of storage in two time slices
new_relation = 'storage_cycle_phs'
sc_new.check_out()
sc.add_set('relation', new_relation)
df = sc_new.par('relation_activity_time', {'relation':'storage_cycle'})
df['technology'] = 'hydro_pump'
df['relation'] = new_relation
sc_new.add_par('relation_activity_time', df)

# adding relaiton_lower_time
df = sc_new.par('relation_lower_time', {'relation':'storage_cycle'})
df['relation'] = new_relation
sc_new.add_par('relation_lower_time', df)
sc_new.commit('')

#%% Notice: Update mapping sets for new parameters, whenever you change
# new parameters, e.g., relation_activity_time:
update_mapping_sets(sc)

#%% Solving the scenario
# 5) Exporting scenario data to GAMS gdx and solve the model
# 5.1) An optional name for the scenario GDX files
caseName = sc_new.model + '__' + sc_new.scenario + '_JH_v' + str(sc_new.version)

# 5.2) Solving
sc_new.solve(case=caseName, solve_options={'lpmethod': '4'})

