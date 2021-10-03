# -*- coding: utf-8 -*-
"""
Created on Tue May 18 19:13:24 2021

@author: hunt
"""

# 1. Loading required packages
import ixmp as ix
import message_ix
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import gridspec
from message_ix import Reporter
from ixmp.reporting import configure
from itertools import product

run_mode = 'MESSAGE'
mp = ix.Platform(name='ene_ixmp', jvmargs=['-Xms800m', '-Xmx8g'])

# Loading a baseline scenario

# 2.2. Scenario with sub-annual time slices
model_new = 'ENGAGE_SSP2_v4.1.2'
scenario_new = "baseline_t12"
version_new = 13 # 10 also works


# Cloning to a new scenario for editing
base = message_ix.Scenario(mp, model=model_new, scenario= scenario_new, version= version_new)

scen = base.clone(model_new,  "baseline_t12_new_i_rc_spec", 
                  keep_solution=False)

# Code to check the rc_spec demand in the existing scenario
#df=scen.par('demand',{'node':'R11_EEU', 'commodity': 'rc_spec','year':2020})

# Add the share of rc_spec out of the data below for each region, as follows:
# [('region',t_1,t_2,t_3,t_4,t_5,t_6), ...]
# The i_spec demand will be calculated as (1-rc_spec). 
# The same time 1-6 time slices for the summer and used for the winter (7-12).
data = [('R11_NAM',0.47,0.45,0.46,0.50,0.54,0.51),
        ('R11_LAM',0.48,0.41,0.40,0.44,0.58,0.50),
        ('R11_WEU',0.30,0.30,0.28,0.34,0.46,0.35),
        ('R11_EEU',0.61,0.54,0.57,0.60,0.72,0.73),
        ('R11_FSU',0.38,0.62,0.60,0.63,0.67,0.59),
        ('R11_AFR',0.62,0.60,0.61,0.63,0.67,0.67),
        ('R11_MEA',0.71,0.76,0.76,0.69,0.69,0.71),
        ('R11_SAS',0.45,0.41,0.38,0.45,0.52,0.49),
        ('R11_CPA',0.27,0.25,0.24,0.23,0.27,0.27),
        ('R11_PAS',0.67,0.69,0.61,0.64,0.78,0.70),
        ('R11_PAO',0.59,0.55,0.52,0.54,0.62,0.60),
        ]

# Loading the existing data in the original scenario
old = scen.par('demand', {'commodity': ['i_spec', 'rc_spec']})
old_i_spec = scen.par('demand', {'commodity': ['i_spec']})
old_rc_spec = scen.par('demand', {'commodity': ['rc_spec']})
# A new table for updated values
new = old.copy().set_index(['node', 'year', 'commodity', 'time']).sort_index()
# Model years
model_yrs = list(set(old['year']))
# Summing up building and industry electricity demand
old_total_t = old.groupby(['node', 'year', 'time']).sum()
old_i_spec_t = old_i_spec.groupby(['node', 'year', 'time']).sum()
old_rc_spec_t = old_rc_spec.groupby(['node', 'year', 'time']).sum()

sectors = ['i_spec', 'rc_spec'] 

# Updating values in the new dataframe
for (region, t_1,t_2,t_3,t_4,t_5,t_6), yr in product(data, model_yrs):

# The following code is used to make the distribution of i_spec and rc_spec 
# to be as much similar as possible to the data entered in lines 42 of this
# script but at the same time maintain the agreggated share of the existing
# year aggregate for the i_spec and rc_spec demand.

# For each region, it is needed to equate the distribution of all time slices
# i_spec and rc_spec demands to guarantee the requirements above. 

# ratio1 is the comparison between the share of the desired new data
# ratio1_1 is the desired rc_spec/i_spec at time slice 1.
    ratio1_1 = t_1/(1-t_1)
    ratio1_2 = t_2/(1-t_2)
    ratio1_3 = t_3/(1-t_3)
    ratio1_4 = t_4/(1-t_4)
    ratio1_5 = t_5/(1-t_5)
    ratio1_6 = t_6/(1-t_6)

# sum_1_7_ts is the sum of the old and new demand for time slice 1 and 7.
# This is because t_1 represent the desired demand share of time slice 1 and 7.
    sum_1_7_ts =  old_total_t.loc[(region, yr, '1'), 'value'] + old_total_t.loc[(region, yr, '7'), 'value']
    sum_2_8_ts =  old_total_t.loc[(region, yr, '2'), 'value'] + old_total_t.loc[(region, yr, '8'), 'value']    
    sum_3_9_ts =  old_total_t.loc[(region, yr, '3'), 'value'] + old_total_t.loc[(region, yr, '9'), 'value']
    sum_4_10_ts =  old_total_t.loc[(region, yr, '4'), 'value'] + old_total_t.loc[(region, yr, '10'), 'value']
    sum_5_11_ts =  old_total_t.loc[(region, yr, '5'), 'value'] + old_total_t.loc[(region, yr, '11'), 'value']
    sum_6_12_ts =  old_total_t.loc[(region, yr, '6'), 'value'] + old_total_t.loc[(region, yr, '12'), 'value']

# total_region_year is the total new and old demand for the region in a year.
    total_region_year = sum_1_7_ts + sum_2_8_ts + sum_3_9_ts + sum_4_10_ts + sum_5_11_ts + sum_6_12_ts 

# ratio2 check the contribution of the ration1 in the new total demand.
    ratio2_1 = ratio1_1 * sum_1_7_ts  / total_region_year 
    ratio2_2 = ratio1_2 * sum_2_8_ts  / total_region_year 
    ratio2_3 = ratio1_3 * sum_3_9_ts  / total_region_year 
    ratio2_4 = ratio1_4 * sum_4_10_ts  / total_region_year 
    ratio2_5 = ratio1_5 * sum_5_11_ts  / total_region_year 
    ratio2_6 = ratio1_6 * sum_6_12_ts  / total_region_year 

# existing_ratio shows the ratio of the old total demand
    existing_ratio =  float(old_i_spec_t.loc[(region, yr, '1'), 'value'])/ float(
        old_rc_spec_t.loc[(region, yr, '1'), 'value'])

# ratio2_average is the not yet adjusted average ratio of the new demand.
# The average ration of the new demand has to be the same as the old demand.
    ratio2_average = (ratio2_1 + ratio2_2 + ratio2_3 + ratio2_4 + ratio2_5 + ratio2_6)/6

# ratio3 makes sure that the new average ration is the same as the old. 
    ratio3_1 = ratio2_1 *  existing_ratio /  ratio2_average
    ratio3_2 = ratio2_2 *  existing_ratio /  ratio2_average
    ratio3_3 = ratio2_3 *  existing_ratio /  ratio2_average
    ratio3_4 = ratio2_4 *  existing_ratio /  ratio2_average
    ratio3_5 = ratio2_5 *  existing_ratio /  ratio2_average
    ratio3_6 = ratio2_6 *  existing_ratio /  ratio2_average

# ratio4 is applied to calculate the corrected share of the new demand. 
    ratio4_1 = 1/ratio3_1
    ratio4_2 = 1/ratio3_2
    ratio4_3 = 1/ratio3_3 
    ratio4_4 = 1/ratio3_4
    ratio4_5 = 1/ratio3_5
    ratio4_6 = 1/ratio3_6   
    
# The final corrected value is loaded to a i_spec and rc_spec data frame.
    new.loc[(region, yr, 'i_spec', '1'), 'value'] = 1/(1+ratio4_1)*float(old_total_t.loc[(region, yr, '1'), 'value'])
    new.loc[(region, yr, 'i_spec', '2'), 'value'] = 1/(1+ratio4_2)*float(old_total_t.loc[(region, yr, '2'), 'value'])
    new.loc[(region, yr, 'i_spec', '3'), 'value'] = 1/(1+ratio4_3)*float(old_total_t.loc[(region, yr, '3'), 'value'])
    new.loc[(region, yr, 'i_spec', '4'), 'value'] = 1/(1+ratio4_4)*float(old_total_t.loc[(region, yr, '4'), 'value'])
    new.loc[(region, yr, 'i_spec', '5'), 'value'] = 1/(1+ratio4_5)*float(old_total_t.loc[(region, yr, '5'), 'value'])
    new.loc[(region, yr, 'i_spec', '6'), 'value'] = 1/(1+ratio4_6)*float(old_total_t.loc[(region, yr, '6'), 'value'])
    new.loc[(region, yr, 'i_spec', '7'), 'value'] = 1/(1+ratio4_1)*float(old_total_t.loc[(region, yr, '7'), 'value'])
    new.loc[(region, yr, 'i_spec', '8'), 'value'] = 1/(1+ratio4_2)*float(old_total_t.loc[(region, yr, '8'), 'value'])
    new.loc[(region, yr, 'i_spec', '9'), 'value'] = 1/(1+ratio4_3)*float(old_total_t.loc[(region, yr, '9'), 'value'])
    new.loc[(region, yr, 'i_spec', '10'), 'value'] = 1/(1+ratio4_4)*float(old_total_t.loc[(region, yr, '10'), 'value'])
    new.loc[(region, yr, 'i_spec', '11'), 'value'] = 1/(1+ratio4_5)*float(old_total_t.loc[(region, yr, '11'), 'value'])
    new.loc[(region, yr, 'i_spec', '12'), 'value'] = 1/(1+ratio4_6)*float(old_total_t.loc[(region, yr, '12'), 'value'])
    
    new.loc[(region, yr,'rc_spec' ,'1' ), 'value'] = ratio4_1/(1+ratio4_1)*float(old_total_t.loc[(region, yr, '1'), 'value'])
    new.loc[(region, yr,'rc_spec' ,'2' ), 'value'] = ratio4_2/(1+ratio4_2)*float(old_total_t.loc[(region, yr, '2'), 'value'])
    new.loc[(region, yr,'rc_spec' ,'3' ), 'value'] = ratio4_3/(1+ratio4_3)*float(old_total_t.loc[(region, yr, '3'), 'value'])
    new.loc[(region, yr,'rc_spec' ,'4' ), 'value'] = ratio4_4/(1+ratio4_4)*float(old_total_t.loc[(region, yr, '4'), 'value'])
    new.loc[(region, yr,'rc_spec' ,'5' ), 'value'] = ratio4_5/(1+ratio4_5)*float(old_total_t.loc[(region, yr, '5'), 'value'])
    new.loc[(region, yr,'rc_spec' ,'6' ), 'value'] = ratio4_6/(1+ratio4_6)*float(old_total_t.loc[(region, yr, '6'), 'value'])
    new.loc[(region, yr,'rc_spec' ,'7' ), 'value'] = ratio4_1/(1+ratio4_1)*float(old_total_t.loc[(region, yr, '7'), 'value'])
    new.loc[(region, yr,'rc_spec' ,'8' ), 'value'] = ratio4_2/(1+ratio4_2)*float(old_total_t.loc[(region, yr, '8'), 'value'])
    new.loc[(region, yr,'rc_spec' ,'9' ), 'value'] = ratio4_3/(1+ratio4_3)*float(old_total_t.loc[(region, yr, '9'), 'value'])
    new.loc[(region, yr,'rc_spec' ,'10' ), 'value'] = ratio4_4/(1+ratio4_4)*float(old_total_t.loc[(region, yr, '10'), 'value'])
    new.loc[(region, yr,'rc_spec' ,'11' ), 'value'] = ratio4_5/(1+ratio4_5)*float(old_total_t.loc[(region, yr, '11'), 'value'])
    new.loc[(region, yr,'rc_spec' ,'12' ), 'value'] = ratio4_6/(1+ratio4_6)*float(old_total_t.loc[(region, yr, '12'), 'value'])
    
# Reset index of the new table and add to the model
scen.check_out()

# The data frame is loaded to the scenario.
scen.add_par('demand', new.reset_index())

scen.commit('demand updated')              
#scen.commit(comment='adding industry and residential data')
#scen.set_as_default()

scen.solve()

mp.close_db()
