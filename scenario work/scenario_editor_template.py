# -*- coding: utf-8 -*-

# 1) Importing required packages and specifying input data
import ixmp as ix
import message_ix
import pandas as pd

# 1.1) Specifying scenario identifiers (model/scenario/version)
model = "MESSAGE_CASm"
scenario = "baseline_t12"
version = 7     # to be loaded, if exists (see 3.2.1)


# %% 2) Loading a platform
# 2.1) By loading local default database
mp = ix.Platform()

# 2.1) Loading a database in a different path
# mp = ix.Platform(name='iiasa')
#%% 3) Loading/clonning a scenario
# 3.1) creating a new (empty) scenario
# sc = message_ix.Scenario(mp, model, scenario, version='new')

# 3.2) Loading an existing scenario from database
# 3.2.1) Loading using version number
sc = message_ix.Scenario(mp, model, scenario, version)

# 3.2.2) Loading without version number (loads the default scenario)
# sc = message_ix.Scenario(mp, model, scenario)

# 3.3.) Cloning
# 3.3.1) Cloning with the same model/scenario name
# sc_new = sc.clone()  # (only version number will increase by one)

# 3.3.2) Cloning to a different model or scenario name (you can change both)
# sc_new = sc.clone('new model', 'new_scenario')

#%% 3.4) Loading data from Excel
# xls_path = r'C:/.../model_data.xlsx'
# sc.read_excel(xls_path, add_units=True, init_items=True, commit_steps=True)

#%% 4) Loading/modifying parameters if needed
# 4.1) Removing solution (if any) and checking-out before editing
# Notice: you don't need to remove solution if you just want to see the results
if sc.has_solution():
    sc.remove_solution()
sc.check_out()

# 4.2) Removing data
# (NOTICE: be careful when you remove, sometimes this can be destructive,
# specially if you remove an element of a set, that will remove all information
# about that element from all parameters as well.)

# A. DESTRUCTIVE actions (try to avoid unless you know what you are doing):
# sc.remove_set('techno')
# sc.remove_par('parameter')

# B. removing data from sets and parameters
sc.remove_set('technology', 'coffee_maker')

# for parameters, we need to first load that data that should be removed
table_remove = sc.par('input', {'node_loc':'IIASA', 'technology':'extra_tec'})
sc.remove_par('input', table_remove)

# 4.3) Adding or changing/overwriting data
df = sc.par('input', {'node_loc':'IIASA', 'technology':'extra_tec',
                      'year_act': 2020})
df['value'] = 1.15   # changing the input value
sc.add_par('input', df)

# 4.4) Discarding changes if not desirable
# sc.discard_changes()

# 4.5) Accepting changes and saving to the scenario
sc.commit('changes saved')

#%% 5) Exporting scenario data to GAMS gdx and solve the model
# 5.1) An optional name for the scenario GDX files
caseName = sc.model + '__' + sc.scenario + '__v' + str(sc.version)

# 5.2) Solving
sc.solve(case=caseName, solve_options={'lpmethod': '4'})
#%% 6) Looking into some results
# 6.1) Activity of some power plants
df = sc.var('ACT', {'node_loc': 'LAM', 'technology': ['gas_cc']})

# 6.2) Capacity of some power plants in specific years
df = sc.var('CAP', {'node_loc': 'LAM', 'technology': ['gas_cc'],
                    'year_act': [2020, 2025]})

# 6.2.1) Finding total installed capacity per year
df2 = df.groupby(['node_loc', 'technology', 'year_act']).sum()

# 6.3) Total cost per region
df = sc.var('COST_NODAL_NET', {'node_loc': 'LAM'})

#%% Examples for manupulating data
# Example 1: changing data for a group of technologies by overwriting data
df = sc.par('technical_lifetime', {'node_loc': 'LAM',
                                   'technology': ['wind_ppl', 'wind_ppf'],
                                   'year_act': 2020})
df['value'] = 30                       # changing the input value

# Example 2: averaging data (also suitable for sum, etc.)
df = sc.par('capacity_factor', {'technology': 'gas_cc'})
df2 = df.groupby(['node_loc', 'technology', 'year_vtg']).mean()

# Example 3: dropping a column
df3 = df2.drop(['year_act'], axis=1)

# Example 4: expanding a multindex
df4 = df3.reset_index()

# Example 5: renaming columns 'year_vtg' --> 'year'
df5 = df4.rename({'year_vtg': 'year'}, axis=1)

# Example 6: replacing/renaming some members of dataframe
df6 = df5.replace({'gas_cc': 'combined_cycle', 'R11_AFR': 'AFR'})

# Example7: pivot table
df7 = pd.pivot_table(df6, index=['node_loc', 'technology'], columns='year',
                     values='value')
