# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 00:15:25 2020

@author: hunt
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm1
import xarray as xr
import datetime
from datetime import timedelta


# Count the time though the script
now = datetime.datetime.now()
file_path = r'C:\Users\zakeri\GDrive\Job\IIASA\Modelling\Julian'
# Download the hourly data from the 11 regions in one file. 
data = pd.read_excel(file_path + '//SWDH 11 regions.xlsx')
dt = data.values

# region => 0 = NAM, 1 = LAC, 2 = WEU, 3 = EEU, 4 = FSU, 5 = AFR, 6 = MEA, 7 = SAS, 8 = CPA, 9 = PAS, 10 = PAO
region = 0
regions = ['NAM','LAC','WEU','EEU','FSU','AFR','MEA','SAS','CPA','PAS','PAO']

# Cicle to create the time slices for all regions, working one by one as shown above. 
while region < 11:
    
    # Hourly salor, wind, hydro and demand data.
    solar = dt[:,1+5*region]
    wind = dt[:,2+5*region]
    hydro = dt[:,4+5*region]
    demand = dt[:,3+5*region]
    demand_MW = dt[:,5+5*region]
    
    # Yearly hourly load curve
    solar_load_curve = np.sort(solar, axis=None)[::-1]
    wind_load_curve = np.sort(wind, axis=None)[::-1]
    demand_load_curve = np.sort(demand, axis=None)[::-1]
    hydro_load_curve = np.sort(hydro, axis=None)[::-1]

    # Seasonal yearly load curve 
    solar_load_curve_Wi = np.sort(solar[0:2190], axis=None)[::-1]
    wind_load_curve_Wi = np.sort(wind[0:2190], axis=None)[::-1]
    hydro_load_curve_Wi = np.sort(hydro[0:2190], axis=None)[::-1]    
    demand_load_curve_Wi = np.sort(demand[0:2190], axis=None)[::-1]

    solar_load_curve_Sp = np.sort(solar[2190:4380], axis=None)[::-1]
    wind_load_curve_Sp = np.sort(wind[2190:4380], axis=None)[::-1]
    hydro_load_curve_Sp = np.sort(hydro[2190:4380], axis=None)[::-1]
    demand_load_curve_Sp = np.sort(demand[2190:4380], axis=None)[::-1]

    solar_load_curve_Su = np.sort(solar[4380:6570], axis=None)[::-1]
    wind_load_curve_Su = np.sort(wind[4380:6570], axis=None)[::-1]
    hydro_load_curve_Su = np.sort(hydro[4380:6570], axis=None)[::-1]
    demand_load_curve_Su = np.sort(demand[4380:6570], axis=None)[::-1]

    solar_load_curve_Au = np.sort(solar[6570:8760], axis=None)[::-1]
    wind_load_curve_Au = np.sort(wind[6570:8760], axis=None)[::-1]
    hydro_load_curve_Au = np.sort(hydro[6570:8760], axis=None)[::-1]
    demand_load_curve_Au = np.sort(demand[6570:8760], axis=None)[::-1]


    # Reducing the hour resolution to 4 hourly resolution.
    solar_4h = np.zeros(shape=(2190))
    wind_4h = np.zeros(shape=(2190))
    hydro_4h = np.zeros(shape=(2190))
    demand_4h = np.zeros(shape=(2190))
    
    x = 0
    xx = 3 #xx = 0 = 245.27 / xx = 1 = 242.11 / xx = 2 = 263.40 / xx = 3 = 264.99 / x = 4 = 245.27 / x = 4 = 245.27
    xxx = 0
    xxxx = 0
    w1 = 0
    w2 = 0
    w3 = 0
    w4 = 0
    w5 = 0
    w6 = 0 
    
    # Adjust the starting day of the series to midnight. 
    while x < 8760:
        if xx < 4:
            nothing = 0
        else:
            xx = 0
            if xxxx == 0:
                w1 = w1 + solar_4h[xxx]
                xxxx = xxxx + 1
            elif xxxx == 1:
                w2 = w2 + solar_4h[xxx]       
                xxxx = xxxx + 1
            elif xxxx == 2:
                w3 = w3 + solar_4h[xxx]   
                xxxx = xxxx + 1
            elif xxxx == 3:
                w4 = w4 + solar_4h[xxx]   
                xxxx = xxxx + 1
            elif xxxx == 4:
                w5 = w5 + solar_4h[xxx]   
                xxxx = xxxx + 1
            elif xxxx == 5:
                w6 = w6 + solar_4h[xxx]                
                xxxx = 0
                
            xxx = xxx + 1
            
        if xxx == 0 or xxx == 2190:
            solar_4h[0] = solar_4h[0] + solar[x]/4  
            wind_4h[0] = wind_4h[0] + wind[x]/4
            hydro_4h[0] = hydro_4h[0] + hydro[x]/4        
            demand_4h[0] = demand_4h[0] + demand[x]/4
    
        else:
            solar_4h[xxx] = solar_4h[xxx] + solar[x]/4 
            wind_4h[xxx] = wind_4h[xxx] + wind[x]/4 
            hydro_4h[xxx] = hydro_4h[xxx] + hydro[x]/4        
            demand_4h[xxx] = demand_4h[xxx] + demand[x]/4 
    
        x = x + 1
        xx = xx + 1
    



    
# NEW METHOD: Pick the most representative day in the season, then pick a scrambles day to better represent the season and the week. 
# How to do it: First pick the best representative day in the season. Then look for the other times slices in the week. 

# Calculating separetely Winter, Spring, Summer and Autumn. 

# For each season,  there are 547.5 comparisonas required. 
# For each comparison, the 2190 days will be compared with the 2 days of the representative week. 

#(mininum sum non 0,w,d1,h1,h2,h3,h4,)
    
    w_minimum = [10000000000,0,0,0,0,0,0]#
    sp_minimum = [10000000000,0,0,0,0,0,0]#
    su_minimum = [10000000000,0,0,0,0,0,0]#
    a_minimum = [10000000000,0,0,0,0,0,0]#
    
    solar_results = np.zeros(shape=(48))
    wind_results = np.zeros(shape=(48))
    hydro_results = np.zeros(shape=(48))
    demand_results = np.zeros(shape=(48))
    
    solar_results_sorted = np.zeros(shape=(48))
    wind_results_sorted = np.zeros(shape=(48))
    hydro_results_sorted = np.zeros(shape=(48))
    demand_results_sorted = np.zeros(shape=(48))
    
    w = 0
    x1 = 0
    while w < 13:
        #This is the equation that balances the load curve and the clustered values, thus it should vary between - and + numbers. And the number closest to 0 should be selected. 
        x2 = 0
        s_w_4_sorted1  = solar_4h[w*42:w*42+42]
        s_sp_4_sorted1 = solar_4h[547+w*42:547+w*42+42]
        s_su_4_sorted1 = solar_4h[547+547+w*42:547+547+w*42+42]
        s_a_4_sorted1  = solar_4h[547+547+547+w*42:547+547+547+w*42+42]    
    
        w_w_4_sorted1  = wind_4h[w*42:w*42+42]
        w_sp_4_sorted1 = wind_4h[547+w*42:547+w*42+42]
        w_su_4_sorted1 = wind_4h[547+547+w*42:547+547+w*42+42]
        w_a_4_sorted1  = wind_4h[547+547+547+w*42:547+547+547+w*42+42]    
    
        h_w_4_sorted1  = hydro_4h[w*42:w*42+42]
        h_sp_4_sorted1 = hydro_4h[547+w*42:547+w*42+42]
        h_su_4_sorted1 = hydro_4h[547+547+w*42:547+547+w*42+42]
        h_a_4_sorted1  = hydro_4h[547+547+547+w*42:547+547+547+w*42+42]  
        
        d_w_4_sorted1  = demand_4h[w*42:w*42+42]
        d_sp_4_sorted1 = demand_4h[547+w*42:547+w*42+42]
        d_su_4_sorted1 = demand_4h[547+547+w*42:547+547+w*42+42]
        d_a_4_sorted1  = demand_4h[547+547+547+w*42:547+547+547+w*42+42]    
    
        d1= 0
        while d1 < 36:
            list_of_days = []
            list_of_days.append(d1)
            list_of_days.append(d1+1)
            list_of_days.append(d1+2)
            list_of_days.append(d1+3)
            list_of_days.append(d1+4)
            list_of_days.append(d1+5)  
            if d1 == 0:
                h1 = 6
            else:
    
                h1 = 0
            while h1 < 35:
                list_of_days.append(h1)
                if d1 == 0:
                    h2 = 7
                elif d1 == 1:
                    h2 = 7
                else:
                    h2 = 1
                while h2 < 34:
                    h3 = 0
                    if d1 == 0:
                        h3 = 8
                    elif d1 == 1:
                        h3 = 8
                    elif d1 == 2:
                        h3 = 8
                    else:
                        h3 = 2
                    while h3 < 33:
                        list_of_days.append(h3)
                        if d1 == 0:
                            h4 = 9
                        elif d1 == 1:
                            h4 = 9
                        elif d1 == 2:
                            h4 = 9
                        elif d1 == 3:
                            h4 = 9
                        else:
                            h4 = 3    
                        while h4 < 32:
                            list_of_days.append(h4)
                           
                            s_w_4_sorted  = np.sort(np.concatenate([s_w_4_sorted1[d1:d1+6],[s_w_4_sorted1[h1],s_w_4_sorted1[h2],s_w_4_sorted1[h3],s_w_4_sorted1[h4],solar_load_curve_Wi.max(),solar_load_curve_Wi.min()]]))[::-1]
                            s_sp_4_sorted = np.sort(np.concatenate([s_sp_4_sorted1[d1:d1+6],[s_sp_4_sorted1[h1],s_sp_4_sorted1[h2],s_sp_4_sorted1[h3],s_sp_4_sorted1[h4],solar_load_curve_Sp.max(),solar_load_curve_Sp.min()]]))[::-1]
                            s_su_4_sorted = np.sort(np.concatenate([s_su_4_sorted1[d1:d1+6],[s_su_4_sorted1[h1],s_su_4_sorted1[h2],s_su_4_sorted1[h3],s_su_4_sorted1[h4],solar_load_curve_Su.max(),solar_load_curve_Su.min()]]))[::-1]
                            s_a_4_sorted  = np.sort(np.concatenate([s_a_4_sorted1[d1:d1+6],[s_a_4_sorted1[h1],s_a_4_sorted1[h2],s_a_4_sorted1[h3],s_a_4_sorted1[h4],solar_load_curve_Au.max(),solar_load_curve_Au.min()]]))[::-1]
            
                            w_w_4_sorted  = np.sort(np.concatenate([w_w_4_sorted1[d1:d1+6],[w_w_4_sorted1[h1],w_w_4_sorted1[h2],w_w_4_sorted1[h3],w_w_4_sorted1[h4],wind_load_curve_Wi.max(),wind_load_curve_Wi.min()]]))[::-1]
                            w_sp_4_sorted = np.sort(np.concatenate([w_sp_4_sorted1[d1:d1+6],[w_sp_4_sorted1[h1],w_sp_4_sorted1[h2],w_sp_4_sorted1[h3],w_sp_4_sorted1[h4],wind_load_curve_Sp.max(),wind_load_curve_Sp.min()]]))[::-1]
                            w_su_4_sorted = np.sort(np.concatenate([w_su_4_sorted1[d1:d1+6],[w_su_4_sorted1[h1],w_su_4_sorted1[h2],w_su_4_sorted1[h3],w_su_4_sorted1[h4],wind_load_curve_Su.max(),wind_load_curve_Su.min()]]))[::-1]
                            w_a_4_sorted  = np.sort(np.concatenate([w_a_4_sorted1[d1:d1+6],[w_a_4_sorted1[h1],w_a_4_sorted1[h2],w_a_4_sorted1[h3],w_a_4_sorted1[h4],wind_load_curve_Au.max(),wind_load_curve_Au.min()]]))[::-1]
    
                            h_w_4_sorted  = np.sort(np.concatenate([h_w_4_sorted1[d1:d1+6],[h_w_4_sorted1[h1],h_w_4_sorted1[h2],h_w_4_sorted1[h3],h_w_4_sorted1[h4],hydro_load_curve_Wi.max(),hydro_load_curve_Wi.min()]]))[::-1]
                            h_sp_4_sorted = np.sort(np.concatenate([h_sp_4_sorted1[d1:d1+6],[h_sp_4_sorted1[h1],h_sp_4_sorted1[h2],h_sp_4_sorted1[h3],h_sp_4_sorted1[h4],hydro_load_curve_Sp.max(),hydro_load_curve_Sp.min()]]))[::-1]
                            h_su_4_sorted = np.sort(np.concatenate([h_su_4_sorted1[d1:d1+6],[h_su_4_sorted1[h1],h_su_4_sorted1[h2],h_su_4_sorted1[h3],h_su_4_sorted1[h4],hydro_load_curve_Su.max(),hydro_load_curve_Su.min()]]))[::-1]
                            h_a_4_sorted  = np.sort(np.concatenate([h_a_4_sorted1[d1:d1+6],[h_a_4_sorted1[h1],h_a_4_sorted1[h2],h_a_4_sorted1[h3],h_a_4_sorted1[h4],hydro_load_curve_Au.max(),hydro_load_curve_Au.min()]]))[::-1]
            
                            d_w_4_sorted  = np.sort(np.concatenate([d_w_4_sorted1[d1:d1+6],[d_w_4_sorted1[h1],d_w_4_sorted1[h2],d_w_4_sorted1[h3],d_w_4_sorted1[h4],demand_load_curve_Wi.max(),demand_load_curve_Wi.min()]]))[::-1]
                            d_sp_4_sorted = np.sort(np.concatenate([d_sp_4_sorted1[d1:d1+6],[d_sp_4_sorted1[h1],d_sp_4_sorted1[h2],d_sp_4_sorted1[h3],d_sp_4_sorted1[h4],demand_load_curve_Sp.max(),demand_load_curve_Sp.min()]]))[::-1]
                            d_su_4_sorted = np.sort(np.concatenate([d_su_4_sorted1[d1:d1+6],[d_su_4_sorted1[h1],d_su_4_sorted1[h2],d_su_4_sorted1[h3],d_su_4_sorted1[h4],demand_load_curve_Su.max(),demand_load_curve_Su.min()]]))[::-1]
                            d_a_4_sorted  = np.sort(np.concatenate([d_a_4_sorted1[d1:d1+6],[d_a_4_sorted1[h1],d_a_4_sorted1[h2],d_a_4_sorted1[h3],d_a_4_sorted1[h4],demand_load_curve_Au.max(),demand_load_curve_Au.min()]]))[::-1]
                            
                            x2 = 182
                            sum1 = 0
                            sum2 = 0
                            sum3 = 0
                            sum4 = 0
                            while x2 < 2190 - 182:
                                sum1 = sum1 + ((solar_load_curve_Wi[x2] - s_w_4_sorted[int(x2/182.5)])**2)          
                                sum2 = sum2 + ((solar_load_curve_Sp[x2] - s_sp_4_sorted[int(x2/182.5)])**2)           
                                sum3 = sum3 + ((solar_load_curve_Su[x2] - s_su_4_sorted[int(x2/182.5)])**2)           
                                sum4 = sum4 + ((solar_load_curve_Au[x2] - s_a_4_sorted[int(x2/182.5)])**2)          
                        
                                sum1 = sum1 + ((wind_load_curve_Wi[x2] - w_w_4_sorted[int(x2/182.5)])**2)         
                                sum2 = sum2 + ((wind_load_curve_Sp[x2] - w_sp_4_sorted[int(x2/182.5)])**2)          
                                sum3 = sum3 + ((wind_load_curve_Su[x2] - w_su_4_sorted[int(x2/182.5)])**2)          
                                sum4 = sum4 + ((wind_load_curve_Au[x2] - w_a_4_sorted[int(x2/182.5)])**2)         
    
                                sum1 = sum1 + ((hydro_load_curve_Wi[x2] - h_w_4_sorted[int(x2/182.5)])**2)/3 # Hydropower is not well represented in the model, so we reduce the impact of hydropower on the final results.       
                                sum2 = sum2 + ((hydro_load_curve_Sp[x2] - h_sp_4_sorted[int(x2/182.5)])**2)/3           
                                sum3 = sum3 + ((hydro_load_curve_Su[x2] - h_su_4_sorted[int(x2/182.5)])**2)/3           
                                sum4 = sum4 + ((hydro_load_curve_Au[x2] - h_a_4_sorted[int(x2/182.5)])**2)/3          
                    
                                sum1 = sum1 + ((demand_load_curve_Wi[x2] - d_w_4_sorted[int(x2/182.5)])**2)           
                                sum2 = sum2 + ((demand_load_curve_Sp[x2] - d_sp_4_sorted[int(x2/182.5)])**2)            
                                sum3 = sum3 + ((demand_load_curve_Su[x2] - d_su_4_sorted[int(x2/182.5)])**2)            
                                sum4 = sum4 + ((demand_load_curve_Au[x2] - d_a_4_sorted[int(x2/182.5)])**2)           
                                x2 = x2 + 1
                            
                            if sum1 != 0 and sum1 < w_minimum[0]:
                                w_minimum = [sum1,w,d1,h1,h2,h3,h4]
                                solar_results[0:12] = np.concatenate([s_w_4_sorted1[d1:d1+6],[s_w_4_sorted1[h1],s_w_4_sorted1[h2],s_w_4_sorted1[h3],s_w_4_sorted1[h4],solar_load_curve_Wi.max(),solar_load_curve_Wi.min()]])
                                wind_results[0:12] = np.concatenate([w_w_4_sorted1[d1:d1+6],[w_w_4_sorted1[h1],w_w_4_sorted1[h2],w_w_4_sorted1[h3],w_w_4_sorted1[h4],wind_load_curve_Wi.max(),wind_load_curve_Wi.min()]])
                                hydro_results[0:12] = np.concatenate([h_w_4_sorted1[d1:d1+6],[h_w_4_sorted1[h1],h_w_4_sorted1[h2],h_w_4_sorted1[h3],h_w_4_sorted1[h4],hydro_load_curve_Wi.max(),hydro_load_curve_Wi.min()]])
                                demand_results[0:12] = np.concatenate([d_w_4_sorted1[d1:d1+6],[d_w_4_sorted1[h1],d_w_4_sorted1[h2],d_w_4_sorted1[h3],d_w_4_sorted1[h4],demand_load_curve_Wi.max(),demand_load_curve_Wi.min()]])
                                solar_results_sorted[0:12] = s_w_4_sorted
                                wind_results_sorted[0:12] = w_w_4_sorted
                                hydro_results_sorted[0:12] = h_w_4_sorted
                                demand_results_sorted[0:12] = d_w_4_sorted                        
                                
                            if sum2 != 0 and sum2 < sp_minimum[0]:
                                sp_minimum = [sum2,w,d1,h1,h2,h3,h4]
                                solar_results[12:24] = np.concatenate([s_sp_4_sorted1[d1:d1+6],[s_sp_4_sorted1[h1],s_sp_4_sorted1[h2],s_sp_4_sorted1[h3],s_sp_4_sorted1[h4],solar_load_curve_Sp.max(),solar_load_curve_Sp.min()]])
                                wind_results[12:24] = np.concatenate([w_sp_4_sorted1[d1:d1+6],[w_sp_4_sorted1[h1],w_sp_4_sorted1[h2],w_sp_4_sorted1[h3],w_sp_4_sorted1[h4],wind_load_curve_Sp.max(),wind_load_curve_Sp.min()]])
                                hydro_results[12:24] = np.concatenate([h_sp_4_sorted1[d1:d1+6],[h_sp_4_sorted1[h1],h_sp_4_sorted1[h2],h_sp_4_sorted1[h3],h_sp_4_sorted1[h4],hydro_load_curve_Sp.max(),hydro_load_curve_Sp.min()]])
                                demand_results[12:24] = np.concatenate([d_sp_4_sorted1[d1:d1+6],[d_sp_4_sorted1[h1],d_sp_4_sorted1[h2],d_sp_4_sorted1[h3],d_sp_4_sorted1[h4],demand_load_curve_Sp.max(),demand_load_curve_Sp.min()]])
                                solar_results_sorted[12:24] = s_sp_4_sorted
                                hydro_results_sorted[12:24] = h_sp_4_sorted
                                wind_results_sorted[12:24] = w_sp_4_sorted
                                demand_results_sorted[12:24] = d_sp_4_sorted 
                                
                            if sum3 != 0 and sum3 < su_minimum[0]:
                                su_minimum = [sum3,w,d1,h1,h2,h3,h4]
                                solar_results[24:36] = np.concatenate([s_su_4_sorted1[d1:d1+6],[s_su_4_sorted1[h1],s_su_4_sorted1[h2],s_su_4_sorted1[h3],s_su_4_sorted1[h4],solar_load_curve_Su.max(),solar_load_curve_Su.min()]])
                                wind_results[24:36] = np.concatenate([w_su_4_sorted1[d1:d1+6],[w_su_4_sorted1[h1],w_su_4_sorted1[h2],w_su_4_sorted1[h3],w_su_4_sorted1[h4],wind_load_curve_Su.max(),wind_load_curve_Su.min()]])
                                hydro_results[24:36] = np.concatenate([h_su_4_sorted1[d1:d1+6],[h_su_4_sorted1[h1],h_su_4_sorted1[h2],h_su_4_sorted1[h3],h_su_4_sorted1[h4],hydro_load_curve_Su.max(),hydro_load_curve_Su.min()]])
                                demand_results[24:36] = np.concatenate([d_su_4_sorted1[d1:d1+6],[d_su_4_sorted1[h1],d_su_4_sorted1[h2],d_su_4_sorted1[h3],d_su_4_sorted1[h4],demand_load_curve_Su.max(),demand_load_curve_Su.min()]])
                                solar_results_sorted[24:36] = s_su_4_sorted
                                wind_results_sorted[24:36] = w_su_4_sorted
                                hydro_results_sorted[24:36] = h_su_4_sorted
                                demand_results_sorted[24:36] = d_su_4_sorted 
                                
                            if sum4 != 0 and sum4 < a_minimum[0]:
                                a_minimum = [sum4,w,d1,h1,h2,h3,h4]
                                solar_results[36:48] = np.concatenate([s_a_4_sorted1[d1:d1+6],[s_a_4_sorted1[h1],s_a_4_sorted1[h2],s_a_4_sorted1[h3],s_a_4_sorted1[h4],solar_load_curve_Au.max(),solar_load_curve_Au.min()]])
                                wind_results[36:48] = np.concatenate([w_a_4_sorted1[d1:d1+6],[w_a_4_sorted1[h1],w_a_4_sorted1[h2],w_a_4_sorted1[h3],w_a_4_sorted1[h4],wind_load_curve_Au.max(),wind_load_curve_Au.min()]])
                                hydro_results[36:48] = np.concatenate([h_a_4_sorted1[d1:d1+6],[h_a_4_sorted1[h1],h_a_4_sorted1[h2],h_a_4_sorted1[h3],h_a_4_sorted1[h4],hydro_load_curve_Au.max(),hydro_load_curve_Au.min()]])
                                demand_results[36:48] = np.concatenate([d_a_4_sorted1[d1:d1+6],[d_a_4_sorted1[h1],d_a_4_sorted1[h2],d_a_4_sorted1[h3],d_a_4_sorted1[h4],demand_load_curve_Au.max(),demand_load_curve_Au.min()]])
                                solar_results_sorted[36:48] = s_a_4_sorted
                                wind_results_sorted[36:48] = w_a_4_sorted
                                hydro_results_sorted[36:48] = h_a_4_sorted
                                demand_results_sorted[36:48] = d_a_4_sorted                             
    
                           
                            h4 = h4 + 3
                            while h4 in list_of_days:
                                h4 = h4 + 1
                        h3 = h3 + 1
                        while h3 in list_of_days:
                            h3 = h3 + 1                       
                    h2 = h2 + 1
                    while h2 in list_of_days:
                        h2 = h2 + 1
                h1 = h1 + 1
                while h1 in list_of_days:
                    h1 = h1 + 1
            d1 = d1 + 1
            print('r ' + regions[region] + ' - w '+ str(w) + ' - d '+ str(d1))
        w = w + 1
    
    solar_load_curve =  np.zeros(shape=(8760))
    wind_load_curve =  np.zeros(shape=(8760))
    hydro_load_curve =  np.zeros(shape=(8760))
    demand_load_curve =  np.zeros(shape=(8760))
    
    solar_load_curve[0:2190] = solar_load_curve_Wi
    solar_load_curve[2190:4380] = solar_load_curve_Sp
    solar_load_curve[4380:6570] = solar_load_curve_Su
    solar_load_curve[6570:8760] = solar_load_curve_Au
    wind_load_curve[0:2190] = wind_load_curve_Wi
    wind_load_curve[2190:4380] = wind_load_curve_Sp
    wind_load_curve[4380:6570] = wind_load_curve_Su
    wind_load_curve[6570:8760] = wind_load_curve_Au
    hydro_load_curve[0:2190] = hydro_load_curve_Wi
    hydro_load_curve[2190:4380] = hydro_load_curve_Sp
    hydro_load_curve[4380:6570] = hydro_load_curve_Su
    hydro_load_curve[6570:8760] = hydro_load_curve_Au
    demand_load_curve[0:2190] = demand_load_curve_Wi
    demand_load_curve[2190:4380] = demand_load_curve_Sp
    demand_load_curve[4380:6570] = demand_load_curve_Su
    demand_load_curve[6570:8760] = demand_load_curve_Au
    
    solar_and_wind = np.stack((solar_results,wind_results,hydro_results,demand_results))
    solar_and_wind_sorter = np.stack((solar_results_sorted,wind_results_sorted,hydro_results_sorted,demand_results_sorted)) 
    solar_and_wind_duration_curve = np.stack((solar_load_curve,wind_load_curve,hydro_load_curve,demand_load_curve))
    
    panda = pd.DataFrame(solar_and_wind.T)
    panda.to_excel(file_path + '//' + regions[region] + 'time_slices.xlsx')
    
    panda = pd.DataFrame(solar_and_wind_sorter.T)
    panda.to_excel(file_path + '//' + regions[region] + 'time_slices_sorted.xlsx')
    
    panda = pd.DataFrame(solar_and_wind_duration_curve.T)
    panda.to_excel(file_path + '//' + regions[region] + 'data_duration_curve.xlsx')

    region = region + 1    

#%%