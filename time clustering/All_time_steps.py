# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 00:15:25 2020

@author: hunt
"""
import pandas as pd
import datetime
import os

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm1
import xarray as xr
from datetime import timedelta

# Add the directory used to run the time clustering algorithm. 
path = 'C:/Users/julia/Documents/Julian/IIASA/Behnam/Time slices paper/time clustering/'

os.chdir(path) 

now = datetime.datetime.now()

# Algorithm time selection
# Select the op value according to the scenario you want to analyze from 1 to 3

# select the number os hourly time slices = 24, 12, 6, 4, 3, 2, 1 
hourly_time_slices_in_a_day = 6

# default = 1. If 2, the algorithm will look for a representative week with 4 seasons, 2 days and 6 hours, i.e. 48 time slices.
daily_time_slices_in_a_week = 1 

# True = time slices will be divided into months. False = time slices will be divided into seasons
monthly = True

# if monthly = True, select the number of monthly time slices = 12, 6, 4, 3, 2, 1 
# 12 = JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SET, OCT, NOV, DEC
# 6  = JAN-FEB, MAR-APR, MAY-JUN, JUL-AUG, SET-OCT, NOV-DEC
# 4  = JAN-MAR, APR-JUN, JUL-SET, OCT-DEC
# 3  = JAN-APR, MAY-AUG, SET-DEC
# 2  = JAN-JUN, JUL-DEC
# 1  = JAN-DEC
monthly_time_slices_in_a_year = 12

# if monthly = False, select the number of seasons time slices = 4, 2, 1 
# 4 = Winter, Spring, Summer, Autumn = 21/DEC-19/MAR, 20/MAR-19/JUN, 20/JUN-21/SEP, 22/SEP-20/DEC
# 2 = Winter-Spring, Summer, Autumn = 21/DEC-19/JUN, 20/JUN-20/DEC
# 1 = Winter-Autumn = 21/DEC-20/DEC
seasonal_time_slices_in_a_year = 0

# Weights selection
#Define the weights for each kind of energy source (sum must be equal to 1): 
# If a country of region has small wind or hydropower potential, the weight of wind and hydropower should be reduced so that the time slice improves the representation of solar and demand, for example. 
solar_weight = 0.3 
wind_weight = 0.3
hydro_weight = 0.1
demand_weight = 0.3 

# Start time selection
# If you want the timeslices to start at 00:00 GTM for al reagions gtm = True. For aleatory start time gtm = False
# Starting at 00:00 GTM is interesting if the model will consider the transmission between regions. Thus solar power during the day in Europa can supply the night electricity demand in China. 
# Not starting at 00:00 GTM results in better overall results for each individual country or region. 
gtm = True
if gtm == True:
    mid_night = 6 # 6 is the number of time slices in the day. By jumping 6 time slices, the algorithm only consider days starting from midnight GTM time. 
else:
    mid_night = 1 # This alternative will look for the best day for each reagion starting from 00:00, 04:00, 08:00, 12:00, 16:00, 18:00, 20:00. However, each reagion might have a different day start time. 

# Data selections:
# There are two sets of data ready to run the time clustering algorithms: 1) 11 regions (11_regions =True) 2) Individual Countries (11_regions =False). 
r_or_c = False # True = 11 regions / False = individual countries
if r_or_c == True:
    input_data = pd.read_excel('11 regions.xlsx')

    # Select the number of the regions that needs to be analysed with the numbers below:
    # region => NAM = 0, LAC = 1, WEU = 2, EEU = 3, FSU = 4, AFR = 5, MEA = 6, SAS = 7, CPA = 8, PAS = 9, PAO = 10
    regions_or_countries = ['NAM','EEU','CPA']
    selected_regions_or_countries = [0,3,8] 
    
else:
    input_data = pd.read_excel('individual countries.xlsx')
    # Select the number of the country that needs to be analysed with the numbers below:
    # country => AFG = 0; AGO = 1; ALB = 2; ARE = 3; ARG = 4; ARM = 5; AUS = 6; AUT = 7; AZE = 8; BDI = 9; BEL = 10; BEN = 11; BFA = 12; BGD = 13; BGR = 14; BHR = 15; BIH = 16; BLR = 17; BLZ = 18; BOL = 19; BRA = 20; 
    #BRN = 21; BTN = 22; BWA = 23; CAF = 24; CAN = 25; CHE = 26; CHL = 27; CHN = 28; CIV = 29; CMR = 30; COD = 31; COG = 32; COL = 33; CPV = 34; CRI = 35; CUB = 36; CYP = 37; CZE = 38; DEU = 39; DJI = 40; 
    #DNK = 41; DOM = 42; DZA = 43; ECU = 44; EGY = 45; ERI = 46; ESH = 47; ESP = 48; EST = 49; ETH = 50; FIN = 51; FJI = 52; FRA = 53; GAB = 54; GBR = 55; GEO = 56; GHA = 57; GIN = 58; GMB = 59; GNB = 60; 
    #GNQ = 61; GRC = 62; GTM = 63; GUF = 64; GUY = 65; HND = 66; HRV = 67; HTI = 68; HUN = 69; IDN = 70; IND = 71; IRL = 72; IRN = 73; IRQ = 74; ISL = 75; ISR = 76; ITA = 77; JAM = 78; JOR = 79; JPN = 80; 
    #KAZ = 81; KEN = 82; KGZ = 83; KHM = 84; KOR = 85; KOS = 86; KWT = 87; LAO = 88; LBN = 89; LBR = 90; LBY = 91; LKA = 92; LSO = 93; LTU = 94; LUX = 95; LVA = 96; MAR = 97; MDA = 98; MDG = 99; MEX = 100; 
    #MKD = 101; MLI = 102; MLT = 103; MMR = 104; MNE = 105; MNG = 106; MOZ = 107; MRT = 108; MUS = 109; MWI = 110; MYS = 111; NAM = 112; NER = 113; NGA = 114; NIC = 115; NLD = 116; NOR = 117; NPL = 118; NZL = 119; OMN = 120; 
    #PAK = 121; PAN = 122; PER = 123; PHL = 124; PNG = 125; POL = 126; PRK = 127; PRT = 128; PRY = 129; QAT = 130; ROU = 131; RUS = 132; RWA = 133; SAU = 134; SDN = 135; SEN = 136; SGP = 137; SLE = 138; SLV = 139; SOM = 140;
    #SRB = 141; SUR = 142; SVK = 143; SVN = 144; SWE = 145; SWZ = 146; SYR = 147; TCD = 148; TGO = 149; THA = 150; TJK = 151; TKM = 152; TLS = 153; TTO = 154; TUN = 155; TUR = 156; TWN = 157; TZA = 158; UGA = 159; UKR = 160; 
    #URY = 161; USA = 162; UZB = 163; VEN = 164; VNM = 165; YEM = 166; ZAF = 167; ZMB = 168; ZWE = 169; 
    regions_or_countries = ['BRA']
    selected_regions_or_countries = [20]    
    
if daily_time_slices_in_a_week == 2:
    from Time_steps_clustering_48 import algorithm as t48
    t48(input_data,regions_or_countries,selected_regions_or_countries,solar_weight,wind_weight,hydro_weight,demand_weight,mid_night,path)
    x = 0

else:
    #from All_time_steps import algorithm as t12
    #t12(input_data,regions_or_countries,selected_regions_or_countries,solar_weight,wind_weight,hydro_weight,demand_weight,mid_night,path,hourly_time_slices_in_a_day, monthly, monthly_time_slices_in_a_year, seasonal_time_slices_in_a_year)
    #algorithm(input_data,regions_or_countries,selected_regions_or_countries,solar_weight,wind_weight,hydro_weight,demand_weight,mid_night,path,hourly_time_slices_in_a_day, monthly, monthly_time_slices_in_a_year, seasonal_time_slices_in_a_year)

    hours_in_a_time_slice = 24/hourly_time_slices_in_a_day
    if monthly == True:
        total_number_of_time_slices = hourly_time_slices_in_a_day*monthly_time_slices_in_a_year
        yearly_divisions = monthly_time_slices_in_a_year
        yearly_divisions_type = 'monthly'
        seasonal_time_slices_in_a_year = 0
    else:
        total_number_of_time_slices = hourly_time_slices_in_a_day*seasonal_time_slices_in_a_year      
        yearly_divisions = seasonal_time_slices_in_a_year
        yearly_divisions_type = 'seasonal'
        monthly_time_slices_in_a_year = 0

    
    dt = input_data.values
    total_regions = len(regions_or_countries)
    solar_and_wind_seasonal = np.zeros(shape=(total_number_of_time_slices))
    solar_and_wind_sorter_seasonal = np.zeros(shape=(total_number_of_time_slices))
    solar_and_wind_duration_curve_seasonal =  np.zeros(shape=(8760))
    
    solar_and_wind_annual = np.zeros(shape=(total_number_of_time_slices))
    solar_and_wind_sorter_annual = np.zeros(shape=(total_number_of_time_slices))
    solar_and_wind_duration_curve_annual =  np.zeros(shape=(8760))
          
    region = 0
    # Cicle to create the time slices for all regions, working one by one as shown above. 
    while region < total_regions:
        
        # Extracting hourly solar, wind, hydro and demand data from the input data.
        solar = dt[:,1+5*selected_regions_or_countries[region]]
        wind = dt[:,2+5*selected_regions_or_countries[region]]
        demand = dt[:,3+5*selected_regions_or_countries[region]]
        hydro = dt[:,4+5*selected_regions_or_countries[region]]
        demand_MW = dt[:,5+5*selected_regions_or_countries[region]]      

        solar_load_curve_annual = np.sort(solar, axis=None)[::-1]   
        wind_load_curve_annual = np.sort(wind, axis=None)[::-1] 
        demand_load_curve_annual = np.sort(demand, axis=None)[::-1]
        hydro_load_curve_annual = np.sort(hydro, axis=None)[::-1]
  
        solar_load_curve_seasonal = np.zeros(shape=(8760))
        wind_load_curve_seasonal = np.zeros(shape=(8760))
        demand_load_curve_seasonal = np.zeros(shape=(8760))
        hydro_load_curve_seasonal = np.zeros(shape=(8760))
        
        # This creates the data repositoty for the load curve for solar, wind, hydro and demand for the different year divisions
        SWHD_h_lc = np.zeros(shape=(4,int(8760/hours_in_a_time_slice)))
        h = 0
        while h < 8760:          
            SWHD_h_lc[0,int(h/hours_in_a_time_slice)] = SWHD_h_lc[0,int(h/hours_in_a_time_slice)] + solar[h]/hours_in_a_time_slice
            SWHD_h_lc[1,int(h/hours_in_a_time_slice)] = SWHD_h_lc[1,int(h/hours_in_a_time_slice)] + wind[h]/hours_in_a_time_slice
            SWHD_h_lc[2,int(h/hours_in_a_time_slice)] = SWHD_h_lc[2,int(h/hours_in_a_time_slice)] + hydro[h]/hours_in_a_time_slice        
            SWHD_h_lc[3,int(h/hours_in_a_time_slice)] = SWHD_h_lc[3,int(h/hours_in_a_time_slice)] + demand[h]/hours_in_a_time_slice 
            h = h + 1        

        #if (hourly_time_slices_in_a_day == 6 and monthly_time_slices_in_a_year == 3 and s==0):
        #    SWHD_h_ms_lc_sorted = np.zeros(shape=(4,yearly_divisions,int(8760/yearly_divisions/hours_in_a_time_slice-1)))
        #else:
        SWHD_h_ms_lc_sorted = np.zeros(shape=(4,yearly_divisions,int(8760/yearly_divisions/hours_in_a_time_slice)))
            
        SWHD_ms_lc_sorted = np.zeros(shape=(4,yearly_divisions,int(8760/yearly_divisions)))
        day_comparison =  np.zeros(shape=(yearly_divisions,int(365/yearly_divisions),1))
        s = 0
        while s < yearly_divisions:  
            if (hourly_time_slices_in_a_day == 3 and (monthly_time_slices_in_a_year == 2 or seasonal_time_slices_in_a_year == 2) and s==1) or (hourly_time_slices_in_a_day == 1 and (monthly_time_slices_in_a_year == 2 or seasonal_time_slices_in_a_year == 2) and s==1) or (hourly_time_slices_in_a_day == 6 and (monthly_time_slices_in_a_year == 1 or seasonal_time_slices_in_a_year == 1) and s==1) or (hourly_time_slices_in_a_day == 6 and (monthly_time_slices_in_a_year == 4 or seasonal_time_slices_in_a_year == 4) and (s==1 or s==3)) or (hourly_time_slices_in_a_day == 6 and monthly_time_slices_in_a_year == 12 and (s==1 or s==3 or s==5 or s==7 or s==9 or s==11)):
                correction = -1
            else:
                correction = 0
             
            SWHD_ms_lc_sorted[0,s,:] = np.sort(solar[int(s*8760/yearly_divisions):int((s+1)*8760/yearly_divisions)], axis=None)[::-1]
            SWHD_ms_lc_sorted[1,s,:] = np.sort(wind[int(s*8760/yearly_divisions):int((s+1)*8760/yearly_divisions)], axis=None)[::-1]
            SWHD_ms_lc_sorted[2,s,:] = np.sort(hydro[int(s*8760/yearly_divisions):int((s+1)*8760/yearly_divisions)], axis=None)[::-1]   
            SWHD_ms_lc_sorted[3,s,:] = np.sort(demand[int(s*8760/yearly_divisions):int((s+1)*8760/yearly_divisions)], axis=None)[::-1]
            
            SWHD_h_ms_lc_sorted[0,s,:] = np.sort(SWHD_h_lc[0,int(s*8760/yearly_divisions/hours_in_a_time_slice):int((s+1)*8760/yearly_divisions/hours_in_a_time_slice+correction)], axis=None)[::-1]
            SWHD_h_ms_lc_sorted[1,s,:] = np.sort(SWHD_h_lc[1,int(s*8760/yearly_divisions/hours_in_a_time_slice):int((s+1)*8760/yearly_divisions/hours_in_a_time_slice+correction)], axis=None)[::-1]
            SWHD_h_ms_lc_sorted[2,s,:] = np.sort(SWHD_h_lc[2,int(s*8760/yearly_divisions/hours_in_a_time_slice):int((s+1)*8760/yearly_divisions/hours_in_a_time_slice+correction)], axis=None)[::-1]   
            SWHD_h_ms_lc_sorted[3,s,:] = np.sort(SWHD_h_lc[3,int(s*8760/yearly_divisions/hours_in_a_time_slice):int((s+1)*8760/yearly_divisions/hours_in_a_time_slice+correction)], axis=None)[::-1]

            solar_load_curve_seasonal[int(s*8760/yearly_divisions):int((s+1)*8760/yearly_divisions)] = np.sort(solar[int(s*8760/yearly_divisions):int((s+1)*8760/yearly_divisions)], axis=None)[::-1]   
            wind_load_curve_seasonal[int(s*8760/yearly_divisions):int((s+1)*8760/yearly_divisions)] = np.sort(wind[int(s*8760/yearly_divisions):int((s+1)*8760/yearly_divisions)], axis=None)[::-1] 
            demand_load_curve_seasonal[int(s*8760/yearly_divisions):int((s+1)*8760/yearly_divisions)] = np.sort(demand[int(s*8760/yearly_divisions):int((s+1)*8760/yearly_divisions)], axis=None)[::-1]
            hydro_load_curve_seasonal[int(s*8760/yearly_divisions):int((s+1)*8760/yearly_divisions)] = np.sort(hydro[int(s*8760/yearly_divisions):int((s+1)*8760/yearly_divisions)], axis=None)[::-1]

            day_comparison[s,:,0] = 10000000000            
            s = s + 1  

            
#        w_minimum = [10000000000,0,0]
#        su_minimum = [10000000000,0,0]
          
                
        solar_results_seasonal = np.zeros(shape=(yearly_divisions, hourly_time_slices_in_a_day))
        wind_results_seasonal = np.zeros(shape=(yearly_divisions, hourly_time_slices_in_a_day))
        hydro_results_seasonal = np.zeros(shape=(yearly_divisions, hourly_time_slices_in_a_day))
        demand_results_seasonal = np.zeros(shape=(yearly_divisions, hourly_time_slices_in_a_day))
        
        solar_results_sorted_s = np.zeros(shape=(yearly_divisions, hourly_time_slices_in_a_day))
        wind_results_sorted_s = np.zeros(shape=(yearly_divisions, hourly_time_slices_in_a_day))
        hydro_results_sorted_s = np.zeros(shape=(yearly_divisions, hourly_time_slices_in_a_day))
        demand_results_sorted_s = np.zeros(shape=(yearly_divisions, hourly_time_slices_in_a_day))
        
        solar_results_annual = np.zeros(shape=(0))
        wind_results_annual = np.zeros(shape=(0))
        hydro_results_annual = np.zeros(shape=(0))
        demand_results_annual = np.zeros(shape=(0))        
        
        solar_results_sorted_seasonal = np.zeros(shape=(0))
        wind_results_sorted_seasonal = np.zeros(shape=(0))
        hydro_results_sorted_seasonal = np.zeros(shape=(0))
        demand_results_sorted_seasonal = np.zeros(shape=(0))
        
        calculation_results = np.zeros(shape=(yearly_divisions))
        
        s = 0
        while s < yearly_divisions:          
            minimum_distance = 10000000000   
            d = 0
            d_minimum = 0
            while d < 365/yearly_divisions-1: 
                h = 0
                while h < 24:                 
                    calculation_results[s] = calculation_results[s] + (SWHD_ms_lc_sorted[0,s,int(d*24+h)] - np.sort(SWHD_h_lc[0,int((s*365/yearly_divisions+d)*hourly_time_slices_in_a_day+h/hours_in_a_time_slice)], axis=None)[::-1])**2*solar_weight
                    calculation_results[s] = calculation_results[s] + (SWHD_ms_lc_sorted[1,s,int(d*24+h)] - np.sort(SWHD_h_lc[1,int((s*365/yearly_divisions+d)*hourly_time_slices_in_a_day+h/hours_in_a_time_slice)], axis=None)[::-1])**2*wind_weight
                    calculation_results[s] = calculation_results[s] + (SWHD_ms_lc_sorted[2,s,int(d*24+h)] - np.sort(SWHD_h_lc[2,int((s*365/yearly_divisions+d)*hourly_time_slices_in_a_day+h/hours_in_a_time_slice)], axis=None)[::-1])**2*hydro_weight
                    calculation_results[s] = calculation_results[s] + (SWHD_ms_lc_sorted[3,s,int(d*24+h)] - np.sort(SWHD_h_lc[3,int((s*365/yearly_divisions+d)*hourly_time_slices_in_a_day+h/hours_in_a_time_slice)], axis=None)[::-1])**2*demand_weight                    
                    h = h + 1

                day_comparison[s,d,0] = calculation_results[s]  
                if calculation_results[s] < minimum_distance: 
                    d_minimum = d
                    minimum_distance = calculation_results[s]
                    s_h_ts_sorted = np.sort(SWHD_h_lc[0,int((s*365/yearly_divisions+d_minimum)*hourly_time_slices_in_a_day):int((s*365/yearly_divisions+d_minimum+1)*hourly_time_slices_in_a_day)], axis=None)[::-1]
                    w_h_ts_sorted = np.sort(SWHD_h_lc[1,int((s*365/yearly_divisions+d_minimum)*hourly_time_slices_in_a_day):int((s*365/yearly_divisions+d_minimum+1)*hourly_time_slices_in_a_day)], axis=None)[::-1]                    
                    h_h_ts_sorted = np.sort(SWHD_h_lc[2,int((s*365/yearly_divisions+d_minimum)*hourly_time_slices_in_a_day):int((s*365/yearly_divisions+d_minimum+1)*hourly_time_slices_in_a_day)], axis=None)[::-1]
                    d_h_ts_sorted = np.sort(SWHD_h_lc[3,int((s*365/yearly_divisions+d_minimum)*hourly_time_slices_in_a_day):int((s*365/yearly_divisions+d_minimum+1)*hourly_time_slices_in_a_day)], axis=None)[::-1]

                    solar_results_seasonal[s,0:hourly_time_slices_in_a_day]         = SWHD_h_lc[0,int((s*365/yearly_divisions+d_minimum)*hourly_time_slices_in_a_day):int((s*365/yearly_divisions+d_minimum+1)*hourly_time_slices_in_a_day)]
                    wind_results_seasonal[s,0:hourly_time_slices_in_a_day]          = SWHD_h_lc[1,int((s*365/yearly_divisions+d_minimum)*hourly_time_slices_in_a_day):int((s*365/yearly_divisions+d_minimum+1)*hourly_time_slices_in_a_day)]
                    hydro_results_seasonal[s,0:hourly_time_slices_in_a_day]         = SWHD_h_lc[2,int((s*365/yearly_divisions+d_minimum)*hourly_time_slices_in_a_day):int((s*365/yearly_divisions+d_minimum+1)*hourly_time_slices_in_a_day)]
                    demand_results_seasonal[s,0:hourly_time_slices_in_a_day]        = SWHD_h_lc[3,int((s*365/yearly_divisions+d_minimum)*hourly_time_slices_in_a_day):int((s*365/yearly_divisions+d_minimum+1)*hourly_time_slices_in_a_day)]
                    solar_results_sorted_s[s,0:hourly_time_slices_in_a_day]  = s_h_ts_sorted
                    wind_results_sorted_s[s,0:hourly_time_slices_in_a_day]   = w_h_ts_sorted
                    hydro_results_sorted_s[s,0:hourly_time_slices_in_a_day]  = h_h_ts_sorted
                    demand_results_sorted_s[s,0:hourly_time_slices_in_a_day] = d_h_ts_sorted
                                                                                               
                print('r ' + regions_or_countries[region] + ' - s '+ str(s) + ' - d '+ str(d))
                d = d + 1
                

            s = s + 1  
                                 

        s = 0
        while s < yearly_divisions:          
            solar_results_annual = np.concatenate((solar_results_seasonal[s,:],solar_results_annual), axis=0)
            wind_results_annual = np.concatenate((wind_results_seasonal[s,:],wind_results_annual), axis=0)
            hydro_results_annual = np.concatenate((hydro_results_seasonal[s,:],hydro_results_annual), axis=0)
            demand_results_annual = np.concatenate((demand_results_seasonal[s,:],demand_results_annual), axis=0)    
            
            solar_results_sorted_seasonal = np.concatenate((solar_results_sorted_s[s,:],solar_results_sorted_seasonal), axis=0)
            wind_results_sorted_seasonal = np.concatenate((wind_results_sorted_s[s,:],wind_results_sorted_seasonal), axis=0)
            hydro_results_sorted_seasonal = np.concatenate((hydro_results_sorted_s[s,:],hydro_results_sorted_seasonal), axis=0)
            demand_results_sorted_seasonal = np.concatenate((demand_results_sorted_s[s,:],demand_results_sorted_seasonal), axis=0)
            s = s + 1       
            
        solar_results_sorted_annual_ts = np.sort(solar_results_annual, axis=None)[::-1]
        wind_results_sorted_annual_ts = np.sort(wind_results_annual, axis=None)[::-1]
        hydro_results_sorted_annual_ts = np.sort(hydro_results_annual, axis=None)[::-1]
        demand_results_sorted_annual_ts = np.sort(demand_results_annual, axis=None)[::-1]     
        
        solar_and_wind_seasonal = np.vstack((solar_and_wind_seasonal,solar_results_annual,wind_results_annual,hydro_results_annual,demand_results_annual))
        solar_and_wind_sorter_seasonal = np.vstack((solar_and_wind_sorter_seasonal,solar_results_sorted_seasonal,wind_results_sorted_seasonal,hydro_results_sorted_seasonal,demand_results_sorted_seasonal)) 
        solar_and_wind_duration_curve_seasonal = np.vstack((solar_and_wind_duration_curve_seasonal,solar_load_curve_seasonal,wind_load_curve_seasonal,hydro_load_curve_seasonal,demand_load_curve_seasonal))
    
        solar_and_wind_annual = np.vstack((solar_and_wind_annual,solar_results_sorted_annual_ts,wind_results_sorted_annual_ts,hydro_results_sorted_annual_ts,demand_results_sorted_annual_ts))
        solar_and_wind_sorter_annual = np.vstack((solar_and_wind_sorter_annual,solar_results_sorted_annual_ts,wind_results_sorted_annual_ts,hydro_results_sorted_annual_ts,demand_results_sorted_annual_ts)) 
        solar_and_wind_duration_curve_annual = np.vstack((solar_and_wind_duration_curve_annual,solar_load_curve_annual,wind_load_curve_annual,hydro_load_curve_annual,demand_load_curve_annual))
        
        region = region + 1 

    # Save the time slices
    path_results = path+'Results/'+yearly_divisions_type+'_ts='+str(yearly_divisions)+' hourly_ts='+str(hourly_time_slices_in_a_day)+'/'                        
    if not os.path.exists(path_results):
        os.makedirs(path_results)

    panda = pd.DataFrame(solar_and_wind_seasonal.T)
    panda.to_excel(path_results+yearly_divisions_type+' time slices.xlsx')

    panda = pd.DataFrame(solar_and_wind_sorter_seasonal.T)
    panda.to_excel(path_results+'sorted '+yearly_divisions_type+' time slices.xlsx')

    panda = pd.DataFrame(solar_and_wind_duration_curve_seasonal.T)
    panda.to_excel(path_results+yearly_divisions_type+' duration curve.xlsx')

    panda = pd.DataFrame(solar_and_wind_annual.T)
    panda.to_excel(path_results+'annual time slices.xlsx')

    panda = pd.DataFrame(solar_and_wind_sorter_annual.T)
    panda.to_excel(path_results+'sorted annual time slices.xlsx')

    panda = pd.DataFrame(solar_and_wind_duration_curve_annual.T)
    panda.to_excel(path_results+'annual duration curve.xlsx')



    # Plotting the seasonal results
    x_axis = np.arange(hourly_time_slices_in_a_day+1)
    x2_axis = np.arange(8760/yearly_divisions+1)
    s_w_h_ds = ['Solar','Wind','Hydro','Demand']
    
    region = 0 # if region = 0, the ploting starts from the first column. 
    n = 1
    while region < total_regions: 
        s_w_h_d = 0
        while s_w_h_d < 4:
            fig=plt.figure()
            s = 0
            while s < yearly_divisions:                     
                ax=fig.add_subplot(4, 3, s+1, label="1")
                ax2=fig.add_subplot(4, 3, s+1, label="1", frame_on=False)
                ax.plot(x_axis[1:hourly_time_slices_in_a_day+1], np.sort(solar_and_wind_sorter_seasonal[n,s*hourly_time_slices_in_a_day:(s+1)*hourly_time_slices_in_a_day], axis=None)[::-1], color="b")
                ax.set_xlabel("Time Slices")
                ax.set_ylabel("%")
                ax.set_title(regions_or_countries[region]+' - '+ s_w_h_ds[s_w_h_d]+' - '+yearly_divisions_type+'_'+str(s+1))
                ax.set_xlim([1,hourly_time_slices_in_a_day])
                ax.set_ylim([0,1])
                ax2.plot(x2_axis[1:int(8760/yearly_divisions+1)], solar_and_wind_duration_curve_seasonal[n,int(s*8760/yearly_divisions):int((s+1)*8760/yearly_divisions)], color="r")
                ax2.get_xaxis().set_visible(False)
                ax2.get_yaxis().set_visible(False)
                ax2.set_xlim([1,int(8760/yearly_divisions)])
                ax2.set_ylim([0,1])
                s = s + 1     
         
            plt.tight_layout()
            fig.subplots_adjust(hspace=0.6, wspace=0.4)
    
            plt.savefig(path_results+ regions_or_countries[region]+' '+yearly_divisions_type+' '+s_w_h_ds[s_w_h_d])
            
            n = n + 1
            s_w_h_d = s_w_h_d + 1      
        region = region + 1

    # Plotting annual results
    x_axis = np.arange(total_number_of_time_slices+1)
    x2_axis = np.arange(8761)
    s_w_h_ds = ['Solar','Wind','Hydro','Demand']
    
    region = 0
    n = 1
    while region < total_regions:
        s_w_h_d = 0
        
        fig=plt.figure()
        ax=fig.add_subplot(2, 2, 1, label="1")
        ax2=fig.add_subplot(2,2, 1, label="1", frame_on=False)
        ax.plot(x_axis[1:total_number_of_time_slices+1], solar_and_wind_sorter_annual[n,:], color="b")
        ax.set_xlabel("Time Slices")
        ax.set_ylabel("%")
        ax.set_title(regions_or_countries[region]+' '+s_w_h_ds[s_w_h_d])
        ax.set_xlim([1,total_number_of_time_slices])
        ax.set_ylim([0,1])
        ax2.plot(x2_axis[1:8761], solar_and_wind_duration_curve_annual[n,:], color="r")
        ax2.get_xaxis().set_visible(False)
        ax2.get_yaxis().set_visible(False)
        ax2.set_xlim([1,8760])
        ax2.set_ylim([0,1])
        
        n = n + 1
        s_w_h_d = s_w_h_d + 1
        
        ax=fig.add_subplot(2, 2, 2, label="1")
        ax2=fig.add_subplot(2, 2, 2, label="1", frame_on=False)
        ax.plot(x_axis[1:total_number_of_time_slices+1], solar_and_wind_sorter_annual[n,:], color="b")
        ax.set_xlabel("Time Slices")
        ax.set_ylabel("%")
        ax.set_title(regions_or_countries[region]+' '+s_w_h_ds[s_w_h_d])
        ax.set_xlim([1,total_number_of_time_slices])
        ax.set_ylim([0,1])
        ax2.plot(x2_axis[1:8761], solar_and_wind_duration_curve_annual[n,:], color="r")
        ax2.get_xaxis().set_visible(False)
        ax2.get_yaxis().set_visible(False)
        ax2.set_xlim([1,8760])
        ax2.set_ylim([0,1])
            
        n = n + 1
        s_w_h_d = s_w_h_d + 1
        
        ax=fig.add_subplot(2, 2, 3, label="1")
        ax2=fig.add_subplot(2, 2, 3, label="1", frame_on=False)
        ax.plot(x_axis[1:total_number_of_time_slices+1], solar_and_wind_sorter_annual[n,:], color="b")
        ax.set_xlabel("Time Slices")
        ax.set_ylabel("%")
        ax.set_title(regions_or_countries[region]+' '+s_w_h_ds[s_w_h_d])
        ax.set_xlim([1,total_number_of_time_slices])
        ax.set_ylim([0,1])
        ax2.plot(x2_axis[1:8761], solar_and_wind_duration_curve_annual[n,:], color="r")
        ax2.get_xaxis().set_visible(False)
        ax2.get_yaxis().set_visible(False)
        ax2.set_xlim([1,8760])
        ax2.set_ylim([0,1])
        
        n = n + 1
        s_w_h_d = s_w_h_d + 1
        
        ax=fig.add_subplot(2, 2, 4, label="1")
        ax2=fig.add_subplot(2, 2, 4, label="1", frame_on=False)
        ax.plot(x_axis[1:total_number_of_time_slices+1], solar_and_wind_sorter_annual[n,:], color="b")
        ax.set_xlabel("Time Slices")
        ax.set_ylabel("%")
        ax.set_title(regions_or_countries[region]+' '+s_w_h_ds[s_w_h_d])
        ax.set_xlim([1,total_number_of_time_slices])
        ax.set_ylim([0,1])
        ax2.plot(x2_axis[1:8761], solar_and_wind_duration_curve_annual[n,:], color="r")
        ax2.get_xaxis().set_visible(False)
        ax2.get_yaxis().set_visible(False)
        ax2.set_xlim([1,8760])
        ax2.set_ylim([0,1])
        
        plt.tight_layout()
        fig.subplots_adjust(hspace=0.6, wspace=0.4)
        
        plt.savefig(path_results + regions_or_countries[region]+' annual '+s_w_h_ds[s_w_h_d])    
       
        n = n + 1        
        region = region + 1


