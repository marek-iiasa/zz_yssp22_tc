# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 15:02:13 2020

@author: hunt
"""
import pandas as pd
import datetime
import os

# Add the directory used to run the time clustering algorithm. 
path_dir = 'C:/Users/julia/Documents/Julian/IIASA/Behnam/Time slices paper/Running Time Slices Module/Documented Scripts/'

os.chdir(path_dir) 

now = datetime.datetime.now()
 
op=1 # Select the op value according to the scenario you want to analyze from 1 to 3

# 1. 12 Time steps clustering
# 2. 24 Time steps clustering
# 3. 48 Time steps clustering
    
    
# Select the regions you want to consider - 11 available: NAM, LAC, WEU, EEU, FSU, AFR, MEA, SAS, CPA, PAS, PAO
# Regions follow the order named in excel
# region => 0 = NAM, 1 = LAC, 2 = WEU, 3 = EEU, 4 = FSU, 5 = AFR, 6 = MEA, 7 = SAS, 8 = CPA, 9 = PAS, 10 = PAO
# Note that NAM must be the first region to be analased. To analise the other resgions, add them to the brakets.
    
selected_regions = ['NAM']#,'LAC','WEU','EEU','FSU','AFR','MEA','SAS','CPA','PAS','PAO'] 

# Upload your model input data
  
input_data = pd.read_excel('SWDH 11 regions.xlsx')
  
#Define the weights for each kind of energy source (sum must be equal to 1): 
solar_weight = 0.3 
wind_weight = 0.3
hydro_weight = 0.1
demand_weight = 0.3 

#If you want the timeslices to start at 00:00 GTM for al reagions gtm = True. For aleatory start time gtm = False
gtm = True

if gtm == True:
    mid_night = 6
else:
    mid_night = 1


if op==1:
    from Time_steps_clustering_12 import algorithm as t12
    t12(input_data,selected_regions,solar_weight,wind_weight,hydro_weight,demand_weight,mid_night,path_dir)
    x = 0

elif op==2:
    from Time_steps_clustering_24 import algorithm as t24
    t24(input_data,selected_regions,solar_weight,wind_weight,hydro_weight,demand_weight,mid_night,path_dir)
    x = 0

elif op==3:
    from Time_steps_clustering_48 import algorithm as t48
    t48(input_data,selected_regions,solar_weight,wind_weight,hydro_weight,demand_weight,mid_night,path_dir)
    x = 0
   


#%%