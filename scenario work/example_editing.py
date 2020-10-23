# -*- coding: utf-8 -*-
"""
This script shows some examples for editing a scenario or adding policies and
constraints.

"""
import ixmp as ix
import message_ix

model = "MESSAGE_CAS"
scenario = "baseline"  # "INDC2030i-con-prim-dir-ncr"//baseline
version = 1

new_scenario = 'policy'

# %% 1) Loading the platform
mp = ix.Platform()
# 1.1) Loading the reference scenario
sc_ref = message_ix.Scenario(mp, model, scenario, version)
# 1.2) Cloning to a new scenario for editing
sc = sc_ref.clone(scenario=new_scenario, keep_solution=False)

#%% Changing share of variable renewable energy in 2050 (if this share exists)
sc.check_out()
df = sc.par('relation_activity_time', {'relation': 'share_renew',
                                       'year_rel': 2050,
                                       'technology': 'elec_t_d_cas'})
df['value'] = -0.5      # changing the value to -0.5 for 50%
sc.add_par('relation_activity_time', df)
sc.commit('')

#%% Deactivating a technology (e.g., pumped hydro) to see the impact
sc.check_out()
df = sc.par('output', {'technology': 'turbine', 'commodity': 'electr',
                       })
df['value'] = 0       # changing the output value to zero (no generation)
sc.add_par('output', df)
sc.commit('')


#%% Adding a cabron budget policy
remove_old_bound = True      # removing existing bounds if exists
type_tec = 'all'             # for type of technologies
bound = 20                   # unit MtCeq/yr

sc.check_out()
df_old = sc.par('bound_emission')
sc.remove_par('bound_emission', df_old)

sc.add_par('bound_emission', ['CAS', # node that bound applies
                              'TCE', # type of emission ('TCE': total carbon equivalent)
                              type_tec,  # type of technologies included
                              2050],     # year for bound
           bound, '-')
sc.commit('')

#%% Limiting the activity of CCS technologies (e.g., to 50% of reference scenario)
sc.check_out()
df = sc_ref.var('ACT', {'technology': 'co2_tr_dis'})  # Loading the output activity
df = df.rename({'lvl': 'value', 'mrg': 'unit'}, axis=1)
df['value'] *= 0.5    # multiplying by 0.5, to limit to 50% of initial value
df['unit'] = 'GWa'
sc.add_par('bound_activity_up', df)
sc.commit('')

#%% Changing the capacity factor some technologies
sc.check_out()
tec_list = ['solar_pv_ppl', 'wind_ppl']
df = sc.par('capacity_factor', {'technology': tec_list})
df['value'] *= 0.9          # reducing CF by 10% (multiplying by 0.9)
sc.add_par('capacity_factor', df)
sc.commit('')

#%% Changing the upper bounds on activity of some trade technologies
sc.check_out()
for tec, val in [('coal_imp', 1), ('loil_imp', 4), ('foil_imp', 3),
        ('gas_imp', 5)]:
    df = sc.par('bound_activity_up', {'technology': tec})
    df['value'] *= val
    df['value'] += 1.25
    sc.add_par('bound_activity_up', df)
sc.commit('')

#%% Debugging and test (only if needed)
# Chaning the mass flow of water relative to electricity in hydropower technologies (1000 m3/s =~ 1 GW)
# For example, by increasing that by 10%, we multiply the value by 1.1
sc.check_out()
tec_in =['hydro_pump', 'pump', 'pump2', 'turbine', 'turbine2',  'hydro_dam']
df = sc.par('input', {'commodity': 'water', 'technology': tec_in})
df['value'] *= 1.1
sc.add_par('input', df)

tec_out =['pump', 'pump2', 'turbine', 'turbine2', 'hydro_pump',
          'hydro_dam']
df = sc.par('output', {'commodity': 'water', 'technology': tec_out})
df['value'] *= 1.1
sc.add_par('output', df)
sc.commit('')

#%% Deactivating the share on renewables (if exists)
sc.check_out()
df = sc.par('relation_activity_time', {'relation':'share_vre',
                                       'technology':'elec_t_d_year'})

df['value'] = 0         # minimum share
sc.add_par('relation_activity_time', df)
sc.commit('')

#%% Adding var_cost for inteconnectors to avoid circulation
elec_exp = [x for x in set(sc.set('technology')) if 'elec_exp' in x]  # all electricity export technologies

sc.check_out()
df = sc.par('relation_activity_time', {'relation': 'fuel_price',
                                       'technology': 'elec_imp'})
df['value'] = 15
sc.add_par('relation_activity_time', df)
sc.commit('')

#%% Adjusting supply of water (by changing the amount of water inflow in upstream)
sc.check_out()
tecs = [x for x in sc.set('technology') if 'inflow' in x]
df = sc.par('bound_activity_up', {'technology': tecs})
df['value'] *= 0.8    # 0.8 means: 80% of existing inflow (reducing inflow)
sc.add_par('bound_activity_up', df)
sc.commit('')

#%% Adjusting demand of water (by changing the amount of water demand)
sc.check_out()
coms = [x for x in sc.set('commodity') if 'water' in x]
df = sc.par('demand', {'commodity': coms})
df['value'] *= 1.2    # 1.2 means 20% higher water demand than existing data
sc.add_par('demand', df)
sc.commit('')



