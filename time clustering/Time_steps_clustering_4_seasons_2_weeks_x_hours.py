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


def algorithm(input_data,regions_or_countries,selected_regions_or_countries,solarweight,windweight,hydroweight,demandweight,mid_night,path,hourly_ts_day): 
        
    # Count the time though the script
    total_regions = len(regions_or_countries)
    dt = input_data.values  
    region = 0
    
    ts_hours = 24/hourly_ts_day
    ts = 4*2*hourly_ts_day
    _8760_per_ts_hours = int(8760/ts_hours) 
    ts_per_week = 7 * hourly_ts_day
    ts_per_season = 7 * hourly_ts_day * 13 + 1 
    
    solar_and_wind_seasonal = np.zeros(shape=(ts))
    solar_and_wind_sorter_seasonal = np.zeros(shape=(ts))
    solar_and_wind_duration_curve_seasonal =  np.zeros(shape=(8760))
    
    solar_and_wind_annual = np.zeros(shape=(ts))
    solar_and_wind_sorter_annual = np.zeros(shape=(ts))
    solar_and_wind_duration_curve_annual =  np.zeros(shape=(8760))
        
    # Cicle to create the time slices for all regions. 
    while region < total_regions:
        
        # Hourly solar, wind, hydro and demand data.
        solar = dt[:,1+5*selected_regions_or_countries[region]]
        wind = dt[:,2+5*selected_regions_or_countries[region]]
        hydro = dt[:,4+5*selected_regions_or_countries[region]]
        demand = dt[:,3+5*selected_regions_or_countries[region]]
        demand_MW = dt[:,5+5*selected_regions_or_countries[region]]
        
        # Yearly hourly load curve
        solar_load_curve_annual = np.sort(solar, axis=None)[::-1]
        wind_load_curve_annual = np.sort(wind, axis=None)[::-1]
        demand_load_curve_annual = np.sort(demand, axis=None)[::-1]
        hydro_load_curve_annual = np.sort(hydro, axis=None)[::-1]
    
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
        solar_hours = np.zeros(shape=(int(_8760_per_ts_hours)))
        wind_hours = np.zeros(shape=(int(_8760_per_ts_hours)))
        hydro_hours = np.zeros(shape=(int(_8760_per_ts_hours)))
        demand_hours = np.zeros(shape=(int(_8760_per_ts_hours)))
        
        x = 0
        xx = 3 # xx = 0 = 245.27 / xx = 1 = 242.11 / xx = 2 = 263.40 / xx = 3 = 264.99 / x = 4 = 245.27 
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
            if xx < ts_hours:
                nothing = 0
            else:
                xx = 0
                if xxxx == 0:
                    w1 = w1 + solar_hours[xxx]
                    xxxx = xxxx + 1
                elif xxxx == 1:
                    w2 = w2 + solar_hours[xxx]       
                    xxxx = xxxx + 1
                elif xxxx == 2:
                    w3 = w3 + solar_hours[xxx]   
                    xxxx = xxxx + 1
                elif xxxx == 3:
                    w4 = w4 + solar_hours[xxx]   
                    xxxx = xxxx + 1
                elif xxxx == 4:
                    w5 = w5 + solar_hours[xxx]   
                    xxxx = xxxx + 1
                elif xxxx == 5:
                    w6 = w6 + solar_hours[xxx]                
                    xxxx = 0
                    
                xxx = xxx + 1
                
            if xxx == 0 or xxx == _8760_per_ts_hours:
                solar_hours[0] = solar_hours[0] + solar[x]/ts_hours  
                wind_hours[0] = wind_hours[0] + wind[x]/ts_hours
                hydro_hours[0] = hydro_hours[0] + hydro[x]/ts_hours    
                demand_hours[0] = demand_hours[0] + demand[x]/ts_hours
        
            else:
                solar_hours[xxx] = solar_hours[xxx] + solar[x]/ts_hours
                wind_hours[xxx] = wind_hours[xxx] + wind[x]/ts_hours
                hydro_hours[xxx] = hydro_hours[xxx] + hydro[x]/ts_hours    
                demand_hours[xxx] = demand_hours[xxx] + demand[x]/ts_hours
        
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
            
        solar_results_seasonal = np.zeros(shape=(ts))
        wind_results_seasonal = np.zeros(shape=(ts))
        hydro_results_seasonal = np.zeros(shape=(ts))
        demand_results_seasonal = np.zeros(shape=(ts))
        
        solar_results_sorted_seasonal = np.zeros(shape=(ts))
        wind_results_sorted_seasonal = np.zeros(shape=(ts))
        hydro_results_sorted_seasonal = np.zeros(shape=(ts))
        demand_results_sorted_seasonal = np.zeros(shape=(ts))
        
        w = 0
        x1 = 0
        while w < 13:
            #This is the equation that balances the load curve and the clustered values, thus it should vary between - and + numbers. And the number closest to 0 should be selected. 
            x2 = 0
            s_w_4_sorted1  = solar_hours[w*ts_per_week:w*ts_per_week+ts_per_week]
            s_sp_4_sorted1 = solar_hours[ts_per_season+w*ts_per_week:ts_per_season+w*ts_per_week+ts_per_week]
            s_su_4_sorted1 = solar_hours[ts_per_season+ts_per_season+w*ts_per_week:ts_per_season+ts_per_season+w*ts_per_week+ts_per_week]
            s_a_4_sorted1  = solar_hours[ts_per_season+ts_per_season+ts_per_season+w*ts_per_week:ts_per_season+ts_per_season+ts_per_season+w*ts_per_week+ts_per_week]    
        
            w_w_4_sorted1  = wind_hours[w*ts_per_week:w*ts_per_week+ts_per_week]
            w_sp_4_sorted1 = wind_hours[ts_per_season+w*ts_per_week:ts_per_season+w*ts_per_week+ts_per_week]
            w_su_4_sorted1 = wind_hours[ts_per_season+ts_per_season+w*ts_per_week:ts_per_season+ts_per_season+w*ts_per_week+ts_per_week]
            w_a_4_sorted1  = wind_hours[ts_per_season+ts_per_season+ts_per_season+w*ts_per_week:ts_per_season+ts_per_season+ts_per_season+w*ts_per_week+ts_per_week]    
        
            h_w_4_sorted1  = hydro_hours[w*ts_per_week:w*ts_per_week+ts_per_week]
            h_sp_4_sorted1 = hydro_hours[ts_per_season+w*ts_per_week:ts_per_season+w*ts_per_week+ts_per_week]
            h_su_4_sorted1 = hydro_hours[ts_per_season+ts_per_season+w*ts_per_week:ts_per_season+ts_per_season+w*ts_per_week+ts_per_week]
            h_a_4_sorted1  = hydro_hours[ts_per_season+ts_per_season+ts_per_season+w*ts_per_week:ts_per_season+ts_per_season+ts_per_season+w*ts_per_week+ts_per_week]  
            
            d_w_4_sorted1  = demand_hours[w*ts_per_week:w*ts_per_week+ts_per_week]
            d_sp_4_sorted1 = demand_hours[ts_per_season+w*ts_per_week:ts_per_season+w*ts_per_week+ts_per_week]
            d_su_4_sorted1 = demand_hours[ts_per_season+ts_per_season+w*ts_per_week:ts_per_season+ts_per_season+w*ts_per_week+ts_per_week]
            d_a_4_sorted1  = demand_hours[ts_per_season+ts_per_season+ts_per_season+w*ts_per_week:ts_per_season+ts_per_season+ts_per_season+w*ts_per_week+ts_per_week]    
        
            d1= 0
            








            if hourly_ts_day == 24: # correto
             while d1 < 24*7-24: #28
                list_of_days = []
                list_of_days.append(d1)
                list_of_days.append(d1+1)
                list_of_days.append(d1+2)
                list_of_days.append(d1+3)
                list_of_days.append(d1+4)
                list_of_days.append(d1+5)    
                list_of_days.append(d1+6)
                list_of_days.append(d1+7)         
                list_of_days.append(d1+8)
                list_of_days.append(d1+9)    
                list_of_days.append(d1+10)
                list_of_days.append(d1+11)               
                list_of_days.append(d1+12)
                list_of_days.append(d1+13)
                list_of_days.append(d1+14)
                list_of_days.append(d1+15)
                list_of_days.append(d1+16)
                list_of_days.append(d1+17)    
                list_of_days.append(d1+18)
                list_of_days.append(d1+19)         
                list_of_days.append(d1+20)
                list_of_days.append(d1+21)    
                list_of_days.append(d1+22)
                list_of_days.append(d1+23)                   
                if d1 == 0:
                    h1 = 24
                else:
        
                    h1 = 0
                while h1 <  24*7-24-1: #27
                    list_of_days.append(h1)
                    if d1 == 0:
                        h2 = 24+1
                    elif d1 == 1:
                        h2 = 24+1
                    else:
                        h2 = 1
                    while h2 < 24*7-24-2: #26
                        list_of_days.append(h2)
                        if d1 == 0:
                            h3 = 24+2
                        elif d1 == 1:
                            h3 = 24+2
                        elif d1 == 2:
                            h3 = 24+2
                        else:
                            h3 = 2
                        while h3 < 24*7-24-3: #26
                            list_of_days.append(h3)
                            if d1 == 0:
                                h4 = 24+3
                            elif d1 == 1:
                                h4 = 24+3
                            elif d1 == 2:
                                h4 = 24+3
                            elif d1 == 3:
                                h4 = 24+3
                            else:
                                h4 = 3    
                            while h4 < 24*7-24-4: #26
                                list_of_days.append(h4)
                                if d1 == 0:
                                    h5 = 24+4
                                elif d1 == 1:
                                    h5 = 24+4
                                elif d1 == 2:
                                    h5 = 24+4
                                elif d1 == 3:
                                    h5 = 24+4
                                elif d1 == 4:
                                    h5 = 24+4
                                else:
                                    h5 = 4
                                    while h5 < 24*7-24-5: #26
                                     list_of_days.append(h5)
                                     if d1 == 0:
                                         h6 = 24+5
                                     elif d1 == 1:
                                         h6 = 24+5
                                     elif d1 == 2:
                                         h6 = 24+5
                                     elif d1 == 3:
                                         h6 = 24+5
                                     elif d1 == 4:
                                         h6 = 24+5       
                                     elif d1 == 5:
                                         h6 = 24+5
                                     else:
                                         h6 = 5   
                                    
                                     while h6 < 24*7-24-6:
                                          list_of_days.append(h6)
                                          if d1 == 0:
                                              h7 = 24+6
                                          elif d1 == 1:
                                              h7 = 24+6
                                          elif d1 == 2:
                                              h7 = 24+6
                                          elif d1 == 3:
                                              h7 = 24+6
                                          elif d1 == 4:
                                              h7 = 24+6       
                                          elif d1 == 5:
                                              h7 = 24+6
                                          elif d1 == 6:
                                              h7 = 24+6
                                          else:
                                              h7 = 6   
                                    
                                          while h7 < 24*7-24-7:
                                             list_of_days.append(h7)
                                             if d1 == 0:
                                                 h8 = 24+7
                                             elif d1 == 1:
                                                 h8 = 24+7
                                             elif d1 == 2:
                                                 h8 = 24+7
                                             elif d1 == 3:
                                                 h8 = 24+7
                                             elif d1 == 4:
                                                 h8 = 24+7       
                                             elif d1 == 5:
                                                 h8 = 24+7
                                             elif d1 == 6:
                                                 h8 = 24+7       
                                             elif d1 == 7:
                                                 h8 = 24+7
                                             elif d1 == 8:
                                                 h8 = 24+7
                                             else:
                                                 h8 = 7
                                    
                                             while h8 < 24*7-24-8:
                                                list_of_days.append(h8) 
                                                if d1 == 0:
                                                    h9 = 24+8
                                                elif d1 == 1:
                                                    h9 = 24+8
                                                elif d1 == 2:
                                                    h9 = 24+8
                                                elif d1 == 3:
                                                    h9 = 24+8
                                                elif d1 == 4:
                                                    h9 = 24+8       
                                                elif d1 == 5:
                                                    h9 = 24+8
                                                elif d1 == 6:
                                                    h9 = 24+8       
                                                elif d1 == 7:
                                                    h9 = 24+8
                                                elif d1 == 8:
                                                    h9 = 24+8       
                                                elif d1 == 9:
                                                    h9 = 24+8
                                                else:
                                                    h9 = 8
                                                while h9 < 24*7-24-9:
                                                   list_of_days.append(h9)
                                                   if d1 == 0:
                                                       h10 = 24+9
                                                   elif d1 == 1:
                                                       h10 = 24+9
                                                   elif d1 == 2:
                                                       h10 = 24+9
                                                   elif d1 == 3:
                                                       h10 = 24+9
                                                   elif d1 == 4:
                                                       h10 = 24+9       
                                                   elif d1 == 5:
                                                       h10 = 24+9
                                                   elif d1 == 6:
                                                       h10 = 24+9       
                                                   elif d1 == 7:
                                                       h10 = 24+9
                                                   elif d1 == 8:
                                                       h10 = 24+9
                                                   elif d1 == 9:
                                                       h10 = 24+9       
                                                   elif d1 == 10:
                                                       h10 = 24+9
                                                   else:
                                                       h10 = 9
                                                   while h10 < 24*7-24-10:
                                                      list_of_days.append(h10)
                                                      if d1 == 0:
                                                          h11 = 24+10
                                                      elif d1 == 1:
                                                          h11 = 24+10
                                                      elif d1 == 2:
                                                          h11 = 24+10
                                                      elif d1 == 3:
                                                          h11 = 24+10
                                                      elif d1 == 4:
                                                          h11 = 24+10      
                                                      elif d1 == 5:
                                                          h11 = 24+10
                                                      elif d1 == 6:
                                                          h11 = 24+10      
                                                      elif d1 == 7:
                                                          h11 = 24+10
                                                      elif d1 == 8:
                                                          h11 = 24+10      
                                                      elif d1 == 9:
                                                          h11 = 24+10
                                                      elif d1 == 10:
                                                          h11 = 24+10      
                                                      elif d1 == 11:
                                                          h11 = 24+10
                                                      else:
                                                          h11 = 10
                                                      while h11 < 24*7-24-11:
                                                         list_of_days.append(h11)
                                                         if d1 == 0:
                                                             h12 = 24+11
                                                         elif d1 == 1:
                                                             h12 = 24+11
                                                         elif d1 == 2:
                                                             h12 = 24+11
                                                         elif d1 == 3:
                                                             h12 = 24+11
                                                         elif d1 == 4:
                                                             h12 = 24+11      
                                                         elif d1 == 5:
                                                             h12 = 24+11
                                                         elif d1 == 6:
                                                             h12 = 24+11      
                                                         elif d1 == 7:
                                                             h12 = 24+11
                                                         elif d1 == 8:
                                                             h12 = 24+11      
                                                         elif d1 == 9:
                                                             h12 = 24+11
                                                         elif d1 == 10:
                                                             h12 = 24+11      
                                                         elif d1 == 11:
                                                             h12 = 24+11
                                                         else:
                                                             h12 = 11
                                    
                                                         while h12 < 24*7-24-12:
                                                                                 list_of_days.append(h12)    
                                                                                 s_w_4_sorted  = np.sort(np.concatenate([s_w_4_sorted1[d1:d1+24],[s_w_4_sorted1[h1],s_w_4_sorted1[h2],s_w_4_sorted1[h3],s_w_4_sorted1[h4],s_w_4_sorted1[h5],s_w_4_sorted1[h6],s_w_4_sorted1[h7],s_w_4_sorted1[h8],s_w_4_sorted1[h9],s_w_4_sorted1[h10],s_w_4_sorted1[h11],s_w_4_sorted1[h12],s_w_4_sorted1[h12+1],s_w_4_sorted1[h12+2],s_w_4_sorted1[h12+3]                  ,s_w_4_sorted1[h12+4],s_w_4_sorted1[h12+5],s_w_4_sorted1[h12+6],s_w_4_sorted1[h12+7],s_w_4_sorted1[h12+8],s_w_4_sorted1[h12+9],s_w_4_sorted1[h12+10],s_w_4_sorted1[h12+11],s_w_4_sorted1[h12+12]]]))[::-1]
                                                                                 s_sp_4_sorted = np.sort(np.concatenate([s_sp_4_sorted1[d1:d1+24],[s_sp_4_sorted1[h1],s_sp_4_sorted1[h2],s_sp_4_sorted1[h3],s_sp_4_sorted1[h4],s_sp_4_sorted1[h5],s_sp_4_sorted1[h6],s_sp_4_sorted1[h7],s_sp_4_sorted1[h8],s_sp_4_sorted1[h9],s_sp_4_sorted1[h10],s_sp_4_sorted1[h11],s_sp_4_sorted1[h12],s_sp_4_sorted1[h12+1],s_sp_4_sorted1[h12+2],s_sp_4_sorted1[h12+3],s_sp_4_sorted1[h12+4],s_sp_4_sorted1[h12+5],s_sp_4_sorted1[h12+6],s_sp_4_sorted1[h12+7],s_sp_4_sorted1[h12+8],s_sp_4_sorted1[h12+9],s_sp_4_sorted1[h12+10],s_sp_4_sorted1[h12+11],s_sp_4_sorted1[h12+12]]]))[::-1]
                                                                                 s_su_4_sorted = np.sort(np.concatenate([s_su_4_sorted1[d1:d1+24],[s_su_4_sorted1[h1],s_su_4_sorted1[h2],s_su_4_sorted1[h3],s_su_4_sorted1[h4],s_su_4_sorted1[h5],s_su_4_sorted1[h6],s_su_4_sorted1[h7],s_su_4_sorted1[h8],s_su_4_sorted1[h9],s_su_4_sorted1[h10],s_su_4_sorted1[h11],s_su_4_sorted1[h12],s_su_4_sorted1[h12+1],s_su_4_sorted1[h12+2],s_su_4_sorted1[h12+3],s_su_4_sorted1[h12+4],s_su_4_sorted1[h12+5],s_su_4_sorted1[h12+6],s_su_4_sorted1[h12+7],s_su_4_sorted1[h12+8],s_su_4_sorted1[h12+9],s_su_4_sorted1[h12+10],s_su_4_sorted1[h12+11],s_su_4_sorted1[h12+12]]]))[::-1]
                                                                                 s_a_4_sorted  = np.sort(np.concatenate([s_a_4_sorted1[d1:d1+24],[s_a_4_sorted1[h1],s_a_4_sorted1[h2],s_a_4_sorted1[h3],s_a_4_sorted1[h4],s_a_4_sorted1[h5],s_a_4_sorted1[h6],s_a_4_sorted1[h7],s_a_4_sorted1[h8],s_a_4_sorted1[h9],s_a_4_sorted1[h10],s_a_4_sorted1[h11],s_a_4_sorted1[h12],s_a_4_sorted1[h12+1],s_a_4_sorted1[h12+2],s_a_4_sorted1[h12+3]                  ,s_a_4_sorted1[h12+4],s_a_4_sorted1[h12+5],s_a_4_sorted1[h12+6],s_a_4_sorted1[h12+7],s_a_4_sorted1[h12+8],s_a_4_sorted1[h12+9],s_a_4_sorted1[h12+10],s_a_4_sorted1[h12+11],s_a_4_sorted1[h12+12]]]))[::-1]
                
                                                                                 w_w_4_sorted  = np.sort(np.concatenate([w_w_4_sorted1[d1:d1+24],[w_w_4_sorted1[h1],w_w_4_sorted1[h2],w_w_4_sorted1[h3],w_w_4_sorted1[h4],w_w_4_sorted1[h5],w_w_4_sorted1[h6],w_w_4_sorted1[h7],w_w_4_sorted1[h8],w_w_4_sorted1[h9],w_w_4_sorted1[h10],w_w_4_sorted1[h11],w_w_4_sorted1[h12],w_w_4_sorted1[h12+1],w_w_4_sorted1[h12+2],w_w_4_sorted1[h12+3]                  ,w_w_4_sorted1[h12+4],w_w_4_sorted1[h12+5],w_w_4_sorted1[h12+6],w_w_4_sorted1[h12+7],w_w_4_sorted1[h12+8],w_w_4_sorted1[h12+9],w_w_4_sorted1[h12+10],w_w_4_sorted1[h12+11],w_w_4_sorted1[h12+12]]]))[::-1]
                                                                                 w_sp_4_sorted = np.sort(np.concatenate([w_sp_4_sorted1[d1:d1+24],[w_sp_4_sorted1[h1],w_sp_4_sorted1[h2],w_sp_4_sorted1[h3],w_sp_4_sorted1[h4],w_sp_4_sorted1[h5],w_sp_4_sorted1[h6],w_sp_4_sorted1[h7],w_sp_4_sorted1[h8],w_sp_4_sorted1[h9],w_sp_4_sorted1[h10],w_sp_4_sorted1[h11],w_sp_4_sorted1[h12],w_sp_4_sorted1[h12+1],w_sp_4_sorted1[h12+2],w_sp_4_sorted1[h12+3],w_sp_4_sorted1[h12+4],w_sp_4_sorted1[h12+5],w_sp_4_sorted1[h12+6],w_sp_4_sorted1[h12+7],w_sp_4_sorted1[h12+8],w_sp_4_sorted1[h12+9],w_sp_4_sorted1[h12+10],w_sp_4_sorted1[h12+11],w_sp_4_sorted1[h12+12]]]))[::-1]
                                                                                 w_su_4_sorted = np.sort(np.concatenate([w_su_4_sorted1[d1:d1+24],[w_su_4_sorted1[h1],w_su_4_sorted1[h2],w_su_4_sorted1[h3],w_su_4_sorted1[h4],w_su_4_sorted1[h5],w_su_4_sorted1[h6],w_su_4_sorted1[h7],w_su_4_sorted1[h8],w_su_4_sorted1[h9],w_su_4_sorted1[h10],w_su_4_sorted1[h11],w_su_4_sorted1[h12],w_su_4_sorted1[h12+1],w_su_4_sorted1[h12+2],w_su_4_sorted1[h12+3],w_su_4_sorted1[h12+4],w_su_4_sorted1[h12+5],w_su_4_sorted1[h12+6],w_su_4_sorted1[h12+7],w_su_4_sorted1[h12+8],w_su_4_sorted1[h12+9],w_su_4_sorted1[h12+10],w_su_4_sorted1[h12+11],w_su_4_sorted1[h12+12]]]))[::-1]
                                                                                 w_a_4_sorted  = np.sort(np.concatenate([w_a_4_sorted1[d1:d1+24],[w_a_4_sorted1[h1],w_a_4_sorted1[h2],w_a_4_sorted1[h3],w_a_4_sorted1[h4],w_a_4_sorted1[h5],w_a_4_sorted1[h6],w_su_4_sorted1[h7],w_su_4_sorted1[h8],w_a_4_sorted1[h9],w_a_4_sorted1[h10],w_a_4_sorted1[h11],w_su_4_sorted1[h12],w_a_4_sorted1[h12+1],w_a_4_sorted1[h12+2],w_a_4_sorted1[h12+3]               ,w_a_4_sorted1[h12+4],w_a_4_sorted1[h12+5],w_a_4_sorted1[h12+6],w_su_4_sorted1[h12+7],w_su_4_sorted1[h12+8],w_a_4_sorted1[h12+9],w_a_4_sorted1[h12+10],w_a_4_sorted1[h12+11],w_su_4_sorted1[h12+12]]]))[::-1]
        
                                                                                 h_w_4_sorted  = np.sort(np.concatenate([h_w_4_sorted1[d1:d1+24],[h_w_4_sorted1[h1],h_w_4_sorted1[h2],h_w_4_sorted1[h3],h_w_4_sorted1[h4],h_w_4_sorted1[h5],h_w_4_sorted1[h6],h_w_4_sorted1[h7],h_w_4_sorted1[h8],h_w_4_sorted1[h9],h_w_4_sorted1[h10],h_w_4_sorted1[h11],h_w_4_sorted1[h12],h_w_4_sorted1[h12+1],h_w_4_sorted1[h12+2],h_w_4_sorted1[h12+3]                  ,h_w_4_sorted1[h12+4],h_w_4_sorted1[h12+5],h_w_4_sorted1[h12+6],h_w_4_sorted1[h12+7],h_w_4_sorted1[h12+8],h_w_4_sorted1[h12+9],h_w_4_sorted1[h12+10],h_w_4_sorted1[h12+11],h_w_4_sorted1[h12+12]]]))[::-1]
                                                                                 h_sp_4_sorted = np.sort(np.concatenate([h_sp_4_sorted1[d1:d1+24],[h_sp_4_sorted1[h1],h_sp_4_sorted1[h2],h_sp_4_sorted1[h3],h_sp_4_sorted1[h4],h_sp_4_sorted1[h5],h_sp_4_sorted1[h6],h_sp_4_sorted1[h7],h_sp_4_sorted1[h8],h_sp_4_sorted1[h9],h_sp_4_sorted1[h10],h_sp_4_sorted1[h11],h_sp_4_sorted1[h12],h_sp_4_sorted1[h12+1],h_sp_4_sorted1[h12+2],h_sp_4_sorted1[h12+3],h_sp_4_sorted1[h12+4],h_sp_4_sorted1[h12+5],h_sp_4_sorted1[h12+6],h_sp_4_sorted1[h12+7],h_sp_4_sorted1[h12+8],h_sp_4_sorted1[h12+9],h_sp_4_sorted1[h12+10],h_sp_4_sorted1[h12+11],h_sp_4_sorted1[h12+12]]]))[::-1]
                                                                                 h_su_4_sorted = np.sort(np.concatenate([h_su_4_sorted1[d1:d1+24],[h_su_4_sorted1[h1],h_su_4_sorted1[h2],h_su_4_sorted1[h3],h_su_4_sorted1[h4],h_su_4_sorted1[h5],h_su_4_sorted1[h6],h_su_4_sorted1[h7],h_su_4_sorted1[h8],h_su_4_sorted1[h9],h_su_4_sorted1[h10],h_su_4_sorted1[h11],h_su_4_sorted1[h12],h_su_4_sorted1[h12+1],h_su_4_sorted1[h12+2],h_su_4_sorted1[h12+3],h_su_4_sorted1[h12+4],h_su_4_sorted1[h12+5],h_su_4_sorted1[h12+6],h_su_4_sorted1[h12+7],h_su_4_sorted1[h12+8],h_su_4_sorted1[h12+9],h_su_4_sorted1[h12+10],h_su_4_sorted1[h12+11],h_su_4_sorted1[h12+12]]]))[::-1]
                                                                                 h_a_4_sorted  = np.sort(np.concatenate([h_a_4_sorted1[d1:d1+24],[h_a_4_sorted1[h1],h_a_4_sorted1[h2],h_a_4_sorted1[h3],h_a_4_sorted1[h4],h_a_4_sorted1[h5],h_a_4_sorted1[h6],h_a_4_sorted1[h7],h_a_4_sorted1[h8],h_a_4_sorted1[h9],h_a_4_sorted1[h10],h_a_4_sorted1[h11],h_a_4_sorted1[h12],h_a_4_sorted1[h12+1],h_a_4_sorted1[h12+2],h_a_4_sorted1[h12+3]                  ,h_a_4_sorted1[h12+4],h_a_4_sorted1[h12+5],h_a_4_sorted1[h12+6],h_a_4_sorted1[h12+7],h_a_4_sorted1[h12+8],h_a_4_sorted1[h12+9],h_a_4_sorted1[h12+10],h_a_4_sorted1[h12+11],h_a_4_sorted1[h12+12]]]))[::-1]
                
                                                                                 d_w_4_sorted  = np.sort(np.concatenate([d_w_4_sorted1[d1:d1+24],[d_w_4_sorted1[h1],d_w_4_sorted1[h2],d_w_4_sorted1[h3],d_w_4_sorted1[h4],d_w_4_sorted1[h5],d_w_4_sorted1[h6],d_w_4_sorted1[h7],d_w_4_sorted1[h8],d_w_4_sorted1[h9],d_w_4_sorted1[h10],d_w_4_sorted1[h11],d_w_4_sorted1[h12],d_w_4_sorted1[h12+1],d_w_4_sorted1[h12+2],d_w_4_sorted1[h12+3]                  ,d_w_4_sorted1[h12+4],d_w_4_sorted1[h12+5],d_w_4_sorted1[h12+6],d_w_4_sorted1[h12+7],d_w_4_sorted1[h12+8],d_w_4_sorted1[h12+9],d_w_4_sorted1[h12+10],d_w_4_sorted1[h12+11],d_w_4_sorted1[h12+12]]]))[::-1]
                                                                                 d_sp_4_sorted = np.sort(np.concatenate([d_sp_4_sorted1[d1:d1+24],[d_sp_4_sorted1[h1],d_sp_4_sorted1[h2],d_sp_4_sorted1[h3],d_sp_4_sorted1[h4],d_sp_4_sorted1[h5],d_sp_4_sorted1[h6],d_sp_4_sorted1[h7],d_sp_4_sorted1[h8],d_sp_4_sorted1[h9],d_sp_4_sorted1[h10],d_sp_4_sorted1[h11],d_sp_4_sorted1[h12],d_sp_4_sorted1[h12+1],d_sp_4_sorted1[h12+2],d_sp_4_sorted1[h12+3],d_sp_4_sorted1[h12+4],d_sp_4_sorted1[h12+5],d_sp_4_sorted1[h12+6],d_sp_4_sorted1[h12+7],d_sp_4_sorted1[h12+8],d_sp_4_sorted1[h12+9],d_sp_4_sorted1[h12+10],d_sp_4_sorted1[h12+11],d_sp_4_sorted1[h12+12]]]))[::-1]
                                                                                 d_su_4_sorted = np.sort(np.concatenate([d_su_4_sorted1[d1:d1+24],[d_su_4_sorted1[h1],d_su_4_sorted1[h2],d_su_4_sorted1[h3],d_su_4_sorted1[h4],d_su_4_sorted1[h5],d_su_4_sorted1[h6],d_su_4_sorted1[h7],d_su_4_sorted1[h8],d_su_4_sorted1[h9],d_su_4_sorted1[h10],d_su_4_sorted1[h11],d_su_4_sorted1[h12],d_su_4_sorted1[h12+1],d_su_4_sorted1[h12+2],d_su_4_sorted1[h12+3],d_su_4_sorted1[h12+4],d_su_4_sorted1[h12+5],d_su_4_sorted1[h12+6],d_su_4_sorted1[h12+7],d_su_4_sorted1[h12+8],d_su_4_sorted1[h12+9],d_su_4_sorted1[h12+10],d_su_4_sorted1[h12+11],d_su_4_sorted1[h12+12]]]))[::-1]
                                                                                 d_a_4_sorted  = np.sort(np.concatenate([d_a_4_sorted1[d1:d1+24],[d_a_4_sorted1[h1],d_a_4_sorted1[h2],d_a_4_sorted1[h3],d_a_4_sorted1[h4],d_a_4_sorted1[h5],d_a_4_sorted1[h6],d_a_4_sorted1[h7],d_a_4_sorted1[h8],d_a_4_sorted1[h9],d_a_4_sorted1[h10],d_a_4_sorted1[h11],d_a_4_sorted1[h12],d_a_4_sorted1[h12+1],d_a_4_sorted1[h12+2],d_a_4_sorted1[h12+3]                  ,d_a_4_sorted1[h12+4],d_a_4_sorted1[h12+5],d_a_4_sorted1[h12+6],d_a_4_sorted1[h12+7],d_a_4_sorted1[h12+8],d_a_4_sorted1[h12+9],d_a_4_sorted1[h12+10],d_a_4_sorted1[h12+11],d_a_4_sorted1[h12+12]]]))[::-1]
                                
                                                                                 x2 = int(2190/2/hourly_ts_day)
                                                                                 sum1 = 0
                                                                                 sum2 = 0    
                                                                                 sum3 = 0
                                                                                 sum4 = 0
                                                                                 while x2 < 2190 - int(2190/2/hourly_ts_day):
                                                                                     sum1 = sum1 + ((solar_load_curve_Wi[x2] - s_w_4_sorted[int(x2/2190/2/hourly_ts_day)])**2) *solarweight      
                                                                                     sum2 = sum2 + ((solar_load_curve_Sp[x2] - s_sp_4_sorted[int(x2/2190/2/hourly_ts_day)])**2)*solarweight           
                                                                                     sum3 = sum3 + ((solar_load_curve_Su[x2] - s_su_4_sorted[int(x2/2190/2/hourly_ts_day)])**2)*solarweight           
                                                                                     sum4 = sum4 + ((solar_load_curve_Au[x2] - s_a_4_sorted[int(x2/2190/2/hourly_ts_day)])**2) *solarweight         
                        
                                                                                     sum1 = sum1 + ((wind_load_curve_Wi[x2] - w_w_4_sorted[int(x2/2190/2/hourly_ts_day)])**2) *windweight        
                                                                                     sum2 = sum2 + ((wind_load_curve_Sp[x2] - w_sp_4_sorted[int(x2/2190/2/hourly_ts_day)])**2)*windweight          
                                                                                     sum3 = sum3 + ((wind_load_curve_Su[x2] - w_su_4_sorted[int(x2/2190/2/hourly_ts_day)])**2)*windweight          
                                                                                     sum4 = sum4 + ((wind_load_curve_Au[x2] - w_a_4_sorted[int(x2/2190/2/hourly_ts_day)])**2) *windweight        
        
                                                                                     sum1 = sum1 + ((hydro_load_curve_Wi[x2] - h_w_4_sorted[int(x2/2190/2/hourly_ts_day)])**2) *hydroweight # Hydropower is not well represented in the model, so we reduce the impact of hydropower on the final results.       
                                                                                     sum2 = sum2 + ((hydro_load_curve_Sp[x2] - h_sp_4_sorted[int(x2/2190/2/hourly_ts_day)])**2)*hydroweight           
                                                                                     sum3 = sum3 + ((hydro_load_curve_Su[x2] - h_su_4_sorted[int(x2/2190/2/hourly_ts_day)])**2)*hydroweight 
                                                                                     sum4 = sum4 + ((hydro_load_curve_Au[x2] - h_a_4_sorted[int(x2/2190/2/hourly_ts_day)])**2) *hydroweight
                        
                                                                                     sum1 = sum1 + ((demand_load_curve_Wi[x2] - d_w_4_sorted[int(x2/2190/2/hourly_ts_day)])**2) *demandweight       
                                                                                     sum2 = sum2 + ((demand_load_curve_Sp[x2] - d_sp_4_sorted[int(x2/2190/2/hourly_ts_day)])**2)*demandweight
                                                                                     sum3 = sum3 + ((demand_load_curve_Su[x2] - d_su_4_sorted[int(x2/2190/2/hourly_ts_day)])**2)*demandweight
                                                                                     sum4 = sum4 + ((demand_load_curve_Au[x2] - d_a_4_sorted[int(x2/2190/2/hourly_ts_day)])**2) *demandweight
                                                                                     x2 = x2 + 1
                                
                                                                                 if sum1 != 0 and sum1 < w_minimum[0]:
                                                                                         w_minimum = [sum1,w,d1,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12]
                                                                                         solar_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([s_w_4_sorted1[d1:d1+24],[s_w_4_sorted1[h1],s_w_4_sorted1[h2],s_w_4_sorted1[h3],s_w_4_sorted1[h4],s_w_4_sorted1[h5],s_w_4_sorted1[h6],s_w_4_sorted1[h7],s_w_4_sorted1[h8],s_w_4_sorted1[h9],s_w_4_sorted1[h10],s_w_4_sorted1[h11],s_w_4_sorted1[h12],s_w_4_sorted1[h12+1],s_w_4_sorted1[h12+2],s_w_4_sorted1[h12+3],s_w_4_sorted1[h12+4],s_w_4_sorted1[h12+5]                     ,s_w_4_sorted1[h12+6],s_w_4_sorted1[h12+7],s_w_4_sorted1[h12+8],s_w_4_sorted1[h12+9],s_w_4_sorted1[h12+10],s_w_4_sorted1[h12+11],s_w_4_sorted1[h12+12]]])
                                                                                         wind_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([w_w_4_sorted1[d1:d1+24],[w_w_4_sorted1[h1],w_w_4_sorted1[h2],w_w_4_sorted1[h3],w_w_4_sorted1[h4],w_w_4_sorted1[h5],w_w_4_sorted1[h6],w_w_4_sorted1[h7],w_w_4_sorted1[h8],w_w_4_sorted1[h9],w_w_4_sorted1[h10],w_w_4_sorted1[h11],w_w_4_sorted1[h12],w_w_4_sorted1[h12+1],w_w_4_sorted1[h12+2],w_w_4_sorted1[h12+3],w_w_4_sorted1[h12+4],w_w_4_sorted1[h12+5]                      ,w_w_4_sorted1[h12+6],w_w_4_sorted1[h12+7],w_w_4_sorted1[h12+8],w_w_4_sorted1[h12+9],w_w_4_sorted1[h12+10],w_w_4_sorted1[h12+11],w_w_4_sorted1[h12+12]]])
                                                                                         hydro_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([h_w_4_sorted1[d1:d1+24],[h_w_4_sorted1[h1],h_w_4_sorted1[h2],h_w_4_sorted1[h3],h_w_4_sorted1[h4],h_w_4_sorted1[h5],h_w_4_sorted1[h6],h_w_4_sorted1[h7],h_w_4_sorted1[h8],h_w_4_sorted1[h9],h_w_4_sorted1[h10],h_w_4_sorted1[h11],h_w_4_sorted1[h12],h_w_4_sorted1[h12+1],h_w_4_sorted1[h12+2],h_w_4_sorted1[h12+3],h_w_4_sorted1[h12+4],h_w_4_sorted1[h12+5]                     ,h_w_4_sorted1[h12+6],h_w_4_sorted1[h12+7],h_w_4_sorted1[h12+8],h_w_4_sorted1[h12+9],h_w_4_sorted1[h12+10],h_w_4_sorted1[h12+11],h_w_4_sorted1[h12+12]]])
                                                                                         demand_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([d_w_4_sorted1[d1:d1+24],[d_w_4_sorted1[h1],d_w_4_sorted1[h2],d_w_4_sorted1[h3],d_w_4_sorted1[h4],d_w_4_sorted1[h5],d_w_4_sorted1[h6],d_w_4_sorted1[h7],d_w_4_sorted1[h8],d_w_4_sorted1[h9],d_w_4_sorted1[h10],d_w_4_sorted1[h11],d_w_4_sorted1[h12],d_w_4_sorted1[h12+1],d_w_4_sorted1[h12+2],d_w_4_sorted1[h12+3],d_w_4_sorted1[h12+4],d_w_4_sorted1[h12+5]                    ,d_w_4_sorted1[h12+6],d_w_4_sorted1[h12+7],d_w_4_sorted1[h12+8],d_w_4_sorted1[h12+9],d_w_4_sorted1[h12+10],d_w_4_sorted1[h12+11],d_w_4_sorted1[h12+12]]])
                                                                                         solar_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = s_w_4_sorted
                                                                                         wind_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = w_w_4_sorted
                                                                                         hydro_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = h_w_4_sorted
                                                                                         demand_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = d_w_4_sorted      
                                                                                 if sum2 != 0 and sum2 < sp_minimum[0]:
                                                                                         sp_minimum = [sum2,w,d1,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12]
                                                                                         solar_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([s_sp_4_sorted1[d1:d1+24],[s_sp_4_sorted1[h1],s_sp_4_sorted1[h2],s_sp_4_sorted1[h3],s_sp_4_sorted1[h4],s_sp_4_sorted1[h5],s_sp_4_sorted1[h6],s_sp_4_sorted1[h7],s_sp_4_sorted1[h8],s_sp_4_sorted1[h9],s_sp_4_sorted1[h10],s_sp_4_sorted1[h11],s_sp_4_sorted1[h12],s_sp_4_sorted1[h12+1],s_sp_4_sorted1[h12+2],s_sp_4_sorted1[h12+3],s_sp_4_sorted1[h12+4],s_sp_4_sorted1[h12+5]  ,s_sp_4_sorted1[h12+6],s_sp_4_sorted1[h12+7],s_sp_4_sorted1[h12+8],s_sp_4_sorted1[h12+9],s_sp_4_sorted1[h12+10],s_sp_4_sorted1[h12+11],s_sp_4_sorted1[h12+12]]])
                                                                                         wind_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([w_sp_4_sorted1[d1:d1+24],[w_sp_4_sorted1[h1],w_sp_4_sorted1[h2],w_sp_4_sorted1[h3],w_sp_4_sorted1[h4],w_sp_4_sorted1[h5],w_sp_4_sorted1[h6],w_sp_4_sorted1[h7],w_sp_4_sorted1[h8],w_sp_4_sorted1[h9],w_sp_4_sorted1[h10],w_sp_4_sorted1[h11],w_sp_4_sorted1[h12],w_sp_4_sorted1[h12+1],w_sp_4_sorted1[h12+2],w_sp_4_sorted1[h12+3],w_sp_4_sorted1[h12+4],w_sp_4_sorted1[h12+5]   ,w_sp_4_sorted1[h12+6],w_sp_4_sorted1[h12+7],w_sp_4_sorted1[h12+8],w_sp_4_sorted1[h12+9],w_sp_4_sorted1[h12+10],w_sp_4_sorted1[h12+11],w_sp_4_sorted1[h12+12]]])
                                                                                         hydro_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([h_sp_4_sorted1[d1:d1+24],[h_sp_4_sorted1[h1],h_sp_4_sorted1[h2],h_sp_4_sorted1[h3],h_sp_4_sorted1[h4],h_sp_4_sorted1[h5],h_sp_4_sorted1[h6],h_sp_4_sorted1[h7],h_sp_4_sorted1[h8],h_sp_4_sorted1[h9],h_sp_4_sorted1[h10],h_sp_4_sorted1[h11],h_sp_4_sorted1[h12],h_sp_4_sorted1[h12+1],h_sp_4_sorted1[h12+2],h_sp_4_sorted1[h12+3],h_sp_4_sorted1[h12+4],h_sp_4_sorted1[h12+5]  ,h_sp_4_sorted1[h12+6],h_sp_4_sorted1[h12+7],h_sp_4_sorted1[h12+8],h_sp_4_sorted1[h12+9],h_sp_4_sorted1[h12+10],h_sp_4_sorted1[h12+11],h_sp_4_sorted1[h12+12]]])
                                                                                         demand_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([d_sp_4_sorted1[d1:d1+24],[d_sp_4_sorted1[h1],d_sp_4_sorted1[h2],d_sp_4_sorted1[h3],d_sp_4_sorted1[h4],d_sp_4_sorted1[h5],d_sp_4_sorted1[h6],d_sp_4_sorted1[h7],d_sp_4_sorted1[h8],d_sp_4_sorted1[h9],d_sp_4_sorted1[h10],d_sp_4_sorted1[h11],d_sp_4_sorted1[h12],d_sp_4_sorted1[h12+1],d_sp_4_sorted1[h12+2],d_sp_4_sorted1[h12+3],d_sp_4_sorted1[h12+4],d_sp_4_sorted1[h12+5] ,d_sp_4_sorted1[h12+6],d_sp_4_sorted1[h12+7],d_sp_4_sorted1[h12+8],d_sp_4_sorted1[h12+9],d_sp_4_sorted1[h12+10],d_sp_4_sorted1[h12+11],d_sp_4_sorted1[h12+12]]])
                                                                                         solar_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = s_sp_4_sorted
                                                                                         hydro_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = h_sp_4_sorted
                                                                                         wind_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = w_sp_4_sorted
                                                                                         demand_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = d_sp_4_sorted 
                                                                                 if sum3 != 0 and sum3 < su_minimum[0]:
                                                                                         su_minimum = [sum3,w,d1,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12]
                                                                                         solar_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([s_su_4_sorted1[d1:d1+24],[s_su_4_sorted1[h1],s_su_4_sorted1[h2],s_su_4_sorted1[h3],s_su_4_sorted1[h4],s_su_4_sorted1[h5],s_su_4_sorted1[h6],s_su_4_sorted1[h7],s_su_4_sorted1[h8],s_su_4_sorted1[h9],s_su_4_sorted1[h10],s_su_4_sorted1[h11],s_su_4_sorted1[h12],s_su_4_sorted1[h12+1],s_su_4_sorted1[h12+2],s_su_4_sorted1[h12+3],s_su_4_sorted1[h12+4],s_su_4_sorted1[h12+5]  ,s_su_4_sorted1[h12+6],s_su_4_sorted1[h12+7],s_su_4_sorted1[h12+8],s_su_4_sorted1[h12+9],s_su_4_sorted1[h12+10],s_su_4_sorted1[h12+11],s_su_4_sorted1[h12+12]]])
                                                                                         wind_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([w_su_4_sorted1[d1:d1+24],[w_su_4_sorted1[h1],w_su_4_sorted1[h2],w_su_4_sorted1[h3],w_su_4_sorted1[h4],w_su_4_sorted1[h5],w_su_4_sorted1[h6],w_su_4_sorted1[h7],w_su_4_sorted1[h8],w_su_4_sorted1[h9],w_su_4_sorted1[h10],w_su_4_sorted1[h11],w_su_4_sorted1[h12],w_su_4_sorted1[h12+1],w_su_4_sorted1[h12+2],w_su_4_sorted1[h12+3],w_su_4_sorted1[h12+4],w_su_4_sorted1[h12+5]   ,w_su_4_sorted1[h12+6],w_su_4_sorted1[h12+7],w_su_4_sorted1[h12+8],w_su_4_sorted1[h12+9],w_su_4_sorted1[h12+10],w_su_4_sorted1[h12+11],w_su_4_sorted1[h12+12]]])
                                                                                         hydro_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([h_su_4_sorted1[d1:d1+24],[h_su_4_sorted1[h1],h_su_4_sorted1[h2],h_su_4_sorted1[h3],h_su_4_sorted1[h4],h_su_4_sorted1[h5],h_su_4_sorted1[h6],h_su_4_sorted1[h7],h_su_4_sorted1[h8],h_su_4_sorted1[h9],h_su_4_sorted1[h10],h_su_4_sorted1[h11],h_su_4_sorted1[h12],h_su_4_sorted1[h12+1],h_su_4_sorted1[h12+2],h_su_4_sorted1[h12+3],h_su_4_sorted1[h12+4],h_su_4_sorted1[h12+5]  ,h_su_4_sorted1[h12+6],h_su_4_sorted1[h12+7],h_su_4_sorted1[h12+8],h_su_4_sorted1[h12+9],h_su_4_sorted1[h12+10],h_su_4_sorted1[h12+11],h_su_4_sorted1[h12+12]]])
                                                                                         demand_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([d_su_4_sorted1[d1:d1+24],[d_su_4_sorted1[h1],d_su_4_sorted1[h2],d_su_4_sorted1[h3],d_su_4_sorted1[h4],d_su_4_sorted1[h5],d_su_4_sorted1[h6],d_su_4_sorted1[h7],d_su_4_sorted1[h8],d_su_4_sorted1[h9],d_su_4_sorted1[h10],d_su_4_sorted1[h11],d_su_4_sorted1[h12],d_su_4_sorted1[h12+1],d_su_4_sorted1[h12+2],d_su_4_sorted1[h12+3],d_su_4_sorted1[h12+4],d_su_4_sorted1[h12+5] ,d_su_4_sorted1[h12+6],d_su_4_sorted1[h12+7],d_su_4_sorted1[h12+8],d_su_4_sorted1[h12+9],d_su_4_sorted1[h12+10],d_su_4_sorted1[h12+11],d_su_4_sorted1[h12+12]]])
                                                                                         solar_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = s_su_4_sorted
                                                                                         wind_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = w_su_4_sorted
                                                                                         hydro_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = h_su_4_sorted
                                                                                         demand_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = d_su_4_sorted 
                                                                                 if sum4 != 0 and sum4 < a_minimum[0]:
                                                                                         a_minimum = [sum4,w,d1,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12]
                                                                                         solar_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([s_a_4_sorted1[d1:d1+24],[s_a_4_sorted1[h1],s_a_4_sorted1[h2],s_a_4_sorted1[h3],s_a_4_sorted1[h4],s_a_4_sorted1[h5],s_a_4_sorted1[h6],s_a_4_sorted1[h7],s_a_4_sorted1[h8],s_a_4_sorted1[h9],s_a_4_sorted1[h10],s_a_4_sorted1[h11],s_a_4_sorted1[h12],s_a_4_sorted1[h12+1],s_a_4_sorted1[h12+2],s_a_4_sorted1[h12+3],s_a_4_sorted1[h12+4],s_a_4_sorted1[h12+5]                                   ,s_a_4_sorted1[h12+6],s_a_4_sorted1[h12+7],s_a_4_sorted1[h12+8],s_a_4_sorted1[h12+9],s_a_4_sorted1[h12+10],s_a_4_sorted1[h12+11],s_a_4_sorted1[h12+12]]])
                                                                                         wind_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([w_a_4_sorted1[d1:d1+24],[w_a_4_sorted1[h1],w_a_4_sorted1[h2],w_a_4_sorted1[h3],w_a_4_sorted1[h4],w_a_4_sorted1[h5],w_a_4_sorted1[h6],w_a_4_sorted1[h7],w_a_4_sorted1[h8],w_a_4_sorted1[h9],w_a_4_sorted1[h10],w_a_4_sorted1[h11],w_a_4_sorted1[h12],w_a_4_sorted1[h12+1],w_a_4_sorted1[h12+2],w_a_4_sorted1[h12+3],w_a_4_sorted1[h12+4],w_a_4_sorted1[h12+5]                                    ,w_a_4_sorted1[h12+6],w_a_4_sorted1[h12+7],w_a_4_sorted1[h12+8],w_a_4_sorted1[h12+9],w_a_4_sorted1[h12+10],w_a_4_sorted1[h12+11],w_a_4_sorted1[h12+12]]])
                                                                                         hydro_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([h_a_4_sorted1[d1:d1+24],[h_a_4_sorted1[h1],h_a_4_sorted1[h2],h_a_4_sorted1[h3],h_a_4_sorted1[h4],h_a_4_sorted1[h5],h_a_4_sorted1[h6],h_a_4_sorted1[h7],h_a_4_sorted1[h8],h_a_4_sorted1[h9],h_a_4_sorted1[h10],h_a_4_sorted1[h11],h_a_4_sorted1[h12],h_a_4_sorted1[h12+1],h_a_4_sorted1[h12+2],h_a_4_sorted1[h12+3],h_a_4_sorted1[h12+4],h_a_4_sorted1[h12+5]                                   ,h_a_4_sorted1[h12+6],h_a_4_sorted1[h12+7],h_a_4_sorted1[h12+8],h_a_4_sorted1[h12+9],h_a_4_sorted1[h12+10],h_a_4_sorted1[h12+11],h_a_4_sorted1[h12+12]]])
                                                                                         demand_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([d_a_4_sorted1[d1:d1+24],[d_a_4_sorted1[h1],d_a_4_sorted1[h2],d_a_4_sorted1[h3],d_a_4_sorted1[h4],d_a_4_sorted1[h5],d_a_4_sorted1[h6],d_a_4_sorted1[h7],d_a_4_sorted1[h8],d_a_4_sorted1[h9],d_a_4_sorted1[h10],d_a_4_sorted1[h11],d_a_4_sorted1[h12],d_a_4_sorted1[h12+1],d_a_4_sorted1[h12+2],d_a_4_sorted1[h12+3],d_a_4_sorted1[h12+4],d_a_4_sorted1[h12+5]                                  ,d_a_4_sorted1[h12+6],d_a_4_sorted1[h12+7],d_a_4_sorted1[h12+8],d_a_4_sorted1[h12+9],d_a_4_sorted1[h12+10],d_a_4_sorted1[h12+11],d_a_4_sorted1[h12+12]]])
                                                                                         solar_results_sorted_seasonal[3*2*hourly_ts_day:ts] = s_a_4_sorted
                                                                                         wind_results_sorted_seasonal[3*2*hourly_ts_day:ts] = w_a_4_sorted
                                                                                         hydro_results_sorted_seasonal[3*2*hourly_ts_day:ts] = h_a_4_sorted
                                                                                         demand_results_sorted_seasonal[3*2*hourly_ts_day:ts] = d_a_4_sorted                             

                                                                                 h12 = h12 + 1
                                                                                 while h12 in list_of_days:
                                                                                       h12 = h12 + 1
                                                         h11 = h11 + 1
                                                         while h11 in list_of_days:
                                                               h11 = h11 + 1      
                                                      h10 = h10 + 1
                                                      while h10 in list_of_days:
                                                          h10 = h10 + 1
                                                   h9 = h9 + 1
                                                   while h9 in list_of_days:
                                                      h9 = h9 + 1                                     
                                                h8 = h8 + 1
                                                while h8 in list_of_days:
                                                    h8 = h8 + 1
                                             h7 = h7 + 1
                                             while h7 in list_of_days:
                                                 h7 = h7 + 1      
                                          h6 = h6 + 1
                                          while h6 in list_of_days:
                                            h6 = h6 + 1
                                     h5 = h5 + 1
                                     while h5 in list_of_days:
                                        h5 = h5 + 1                                     
                                h4 = h4 + 1
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
                d1 = d1 + mid_night
                print('r ' + regions_or_countries[region] + ' - w '+ str(w) + ' - d '+ str(d1))










            if hourly_ts_day == 12: # correto
             while d1 < 12*7-12: #28
                list_of_days = []
                list_of_days.append(d1)
                list_of_days.append(d1+1)
                list_of_days.append(d1+2)
                list_of_days.append(d1+3)
                list_of_days.append(d1+4)
                list_of_days.append(d1+5)    
                list_of_days.append(d1+6)
                list_of_days.append(d1+7)         
                list_of_days.append(d1+8)
                list_of_days.append(d1+9)    
                list_of_days.append(d1+10)
                list_of_days.append(d1+11)                   
                if d1 == 0:
                    h1 = 12
                else:
        
                    h1 = 0
                while h1 <  12*7-12-1: #27
                    list_of_days.append(h1)
                    if d1 == 0:
                        h2 = 12+1
                    elif d1 == 1:
                        h2 = 12+1
                    else:
                        h2 = 1
                    while h2 < 12*7-12-2: #26
                        list_of_days.append(h2)
                        if d1 == 0:
                            h3 = 12+2
                        elif d1 == 1:
                            h3 = 12+2
                        elif d1 == 2:
                            h3 = 12+2
                        else:
                            h3 = 2
                        while h3 < 12*7-12-3: #26
                            list_of_days.append(h3)
                            if d1 == 0:
                                h4 = 12+3
                            elif d1 == 1:
                                h4 = 12+3
                            elif d1 == 2:
                                h4 = 12+3
                            elif d1 == 3:
                                h4 = 12+3
                            else:
                                h4 = 3    
                            while h4 < 12*7-12-4: #26
                                list_of_days.append(h4)
                                if d1 == 0:
                                    h5 = 12+4
                                elif d1 == 1:
                                    h5 = 12+4
                                elif d1 == 2:
                                    h5 = 12+4
                                elif d1 == 3:
                                    h5 = 12+4
                                elif d1 == 4:
                                    h5 = 12+4
                                else:
                                    h5 = 4
                                    while h5 < 12*7-12-5: #26
                                     list_of_days.append(h5)
                                     if d1 == 0:
                                         h6 = 12+5
                                     elif d1 == 1:
                                         h6 = 12+5
                                     elif d1 == 2:
                                         h6 = 12+5
                                     elif d1 == 3:
                                         h6 = 12+5
                                     elif d1 == 4:
                                         h6 = 12+5       
                                     elif d1 == 5:
                                         h6 = 12+5
                                     else:
                                         h6 = 5   
                                    
                                     while h6 < 12*7-12-6:
                                          list_of_days.append(h6)
                                          if d1 == 0:
                                              h7 = 12+6
                                          elif d1 == 1:
                                              h7 = 12+6
                                          elif d1 == 2:
                                              h7 = 12+6
                                          elif d1 == 3:
                                              h7 = 12+6
                                          elif d1 == 4:
                                              h7 = 12+6       
                                          elif d1 == 5:
                                              h7 = 12+6
                                          elif d1 == 6:
                                              h7 = 12+6
                                          else:
                                              h7 = 6   
                                    
                                          while h7 < 12*7-12-7:
                                             list_of_days.append(h7)
                                             if d1 == 0:
                                                 h8 = 12+7
                                             elif d1 == 1:
                                                 h8 = 12+7
                                             elif d1 == 2:
                                                 h8 = 12+7
                                             elif d1 == 3:
                                                 h8 = 12+7
                                             elif d1 == 4:
                                                 h8 = 12+7       
                                             elif d1 == 5:
                                                 h8 = 12+7
                                             elif d1 == 6:
                                                 h8 = 12+7       
                                             elif d1 == 7:
                                                 h8 = 12+7
                                             elif d1 == 8:
                                                 h8 = 12+7
                                             else:
                                                 h8 = 7
                                    
                                             while h8 < 12*7-12-8:
                                                list_of_days.append(h8) 
                                                if d1 == 0:
                                                    h9 = 12+8
                                                elif d1 == 1:
                                                    h9 = 12+8
                                                elif d1 == 2:
                                                    h9 = 12+8
                                                elif d1 == 3:
                                                    h9 = 12+8
                                                elif d1 == 4:
                                                    h9 = 12+8       
                                                elif d1 == 5:
                                                    h9 = 12+8
                                                elif d1 == 6:
                                                    h9 = 12+8       
                                                elif d1 == 7:
                                                    h9 = 12+8
                                                elif d1 == 8:
                                                    h9 = 12+8       
                                                elif d1 == 9:
                                                    h9 = 12+8
                                                else:
                                                    h9 = 8
                                                while h9 < 12*7-12-9:
                                                   list_of_days.append(h9)
                                                   if d1 == 0:
                                                       h10 = 12+9
                                                   elif d1 == 1:
                                                       h10 = 12+9
                                                   elif d1 == 2:
                                                       h10 = 12+9
                                                   elif d1 == 3:
                                                       h10 = 12+9
                                                   elif d1 == 4:
                                                       h10 = 12+9       
                                                   elif d1 == 5:
                                                       h10 = 12+9
                                                   elif d1 == 6:
                                                       h10 = 12+9       
                                                   elif d1 == 7:
                                                       h10 = 12+9
                                                   elif d1 == 8:
                                                       h10 = 12+9
                                                   elif d1 == 9:
                                                       h10 = 12+9       
                                                   elif d1 == 10:
                                                       h10 = 12+9
                                                   else:
                                                       h10 = 9
                                                   while h10 < 12*7-12-10:
                                                      list_of_days.append(h10)
                                                      if d1 == 0:
                                                          h11 = 12+10
                                                      elif d1 == 1:
                                                          h11 = 12+10
                                                      elif d1 == 2:
                                                          h11 = 12+10
                                                      elif d1 == 3:
                                                          h11 = 12+10
                                                      elif d1 == 4:
                                                          h11 = 12+10      
                                                      elif d1 == 5:
                                                          h11 = 12+10
                                                      elif d1 == 6:
                                                          h11 = 12+10      
                                                      elif d1 == 7:
                                                          h11 = 12+10
                                                      elif d1 == 8:
                                                          h11 = 12+10      
                                                      elif d1 == 9:
                                                          h11 = 12+10
                                                      elif d1 == 10:
                                                          h11 = 12+10      
                                                      elif d1 == 11:
                                                          h11 = 12+10
                                                      else:
                                                          h11 = 10
                                                      while h11 < 12*7-12-11:
                                                         list_of_days.append(h11)
                                                         if d1 == 0:
                                                             h12 = 12+11
                                                         elif d1 == 1:
                                                             h12 = 12+11
                                                         elif d1 == 2:
                                                             h12 = 12+11
                                                         elif d1 == 3:
                                                             h12 = 12+11
                                                         elif d1 == 4:
                                                             h12 = 12+11      
                                                         elif d1 == 5:
                                                             h12 = 12+11
                                                         elif d1 == 6:
                                                             h12 = 12+11      
                                                         elif d1 == 7:
                                                             h12 = 12+11
                                                         elif d1 == 8:
                                                             h12 = 12+11      
                                                         elif d1 == 9:
                                                             h12 = 12+11
                                                         elif d1 == 10:
                                                             h12 = 12+11      
                                                         elif d1 == 11:
                                                             h12 = 12+11
                                                         else:
                                                             h12 = 11
                                    
                                                         while h12 < 12*7-12-12:
                                                            list_of_days.append(h12)                                                
                                                
                                                            s_w_4_sorted  = np.sort(np.concatenate([s_w_4_sorted1[d1:d1+12],[s_w_4_sorted1[h1],s_w_4_sorted1[h2],s_w_4_sorted1[h3],s_w_4_sorted1[h4],s_w_4_sorted1[h5],s_w_4_sorted1[h6],s_w_4_sorted1[h7],s_w_4_sorted1[h8],s_w_4_sorted1[h9],s_w_4_sorted1[h10],s_w_4_sorted1[h11],s_w_4_sorted1[h12]]]))[::-1]
                                                            s_sp_4_sorted = np.sort(np.concatenate([s_sp_4_sorted1[d1:d1+12],[s_sp_4_sorted1[h1],s_sp_4_sorted1[h2],s_sp_4_sorted1[h3],s_sp_4_sorted1[h4],s_sp_4_sorted1[h5],s_sp_4_sorted1[h6],s_sp_4_sorted1[h7],s_sp_4_sorted1[h8],s_sp_4_sorted1[h9],s_sp_4_sorted1[h10],s_sp_4_sorted1[h11],s_sp_4_sorted1[h12]]]))[::-1]
                                                            s_su_4_sorted = np.sort(np.concatenate([s_su_4_sorted1[d1:d1+12],[s_su_4_sorted1[h1],s_su_4_sorted1[h2],s_su_4_sorted1[h3],s_su_4_sorted1[h4],s_su_4_sorted1[h5],s_su_4_sorted1[h6],s_su_4_sorted1[h7],s_su_4_sorted1[h8],s_su_4_sorted1[h9],s_su_4_sorted1[h10],s_su_4_sorted1[h11],s_su_4_sorted1[h12]]]))[::-1]
                                                            s_a_4_sorted  = np.sort(np.concatenate([s_a_4_sorted1[d1:d1+12],[s_a_4_sorted1[h1],s_a_4_sorted1[h2],s_a_4_sorted1[h3],s_a_4_sorted1[h4],s_a_4_sorted1[h5],s_a_4_sorted1[h6],s_a_4_sorted1[h7],s_a_4_sorted1[h8],s_a_4_sorted1[h9],s_a_4_sorted1[h10],s_a_4_sorted1[h11],s_a_4_sorted1[h12]]]))[::-1]
                
                                                            w_w_4_sorted  = np.sort(np.concatenate([w_w_4_sorted1[d1:d1+12],[w_w_4_sorted1[h1],w_w_4_sorted1[h2],w_w_4_sorted1[h3],w_w_4_sorted1[h4],w_w_4_sorted1[h5],w_w_4_sorted1[h6],w_w_4_sorted1[h7],w_w_4_sorted1[h8],w_w_4_sorted1[h9],w_w_4_sorted1[h10],w_w_4_sorted1[h11],w_w_4_sorted1[h12]]]))[::-1]
                                                            w_sp_4_sorted = np.sort(np.concatenate([w_sp_4_sorted1[d1:d1+12],[w_sp_4_sorted1[h1],w_sp_4_sorted1[h2],w_sp_4_sorted1[h3],w_sp_4_sorted1[h4],w_sp_4_sorted1[h5],w_sp_4_sorted1[h6],w_sp_4_sorted1[h7],w_sp_4_sorted1[h8],w_sp_4_sorted1[h9],w_sp_4_sorted1[h10],w_sp_4_sorted1[h11],w_sp_4_sorted1[h12]]]))[::-1]
                                                            w_su_4_sorted = np.sort(np.concatenate([w_su_4_sorted1[d1:d1+12],[w_su_4_sorted1[h1],w_su_4_sorted1[h2],w_su_4_sorted1[h3],w_su_4_sorted1[h4],w_su_4_sorted1[h5],w_su_4_sorted1[h6],w_su_4_sorted1[h7],w_su_4_sorted1[h8],w_su_4_sorted1[h9],w_su_4_sorted1[h10],w_su_4_sorted1[h11],w_su_4_sorted1[h12]]]))[::-1]
                                                            w_a_4_sorted  = np.sort(np.concatenate([w_a_4_sorted1[d1:d1+12],[w_a_4_sorted1[h1],w_a_4_sorted1[h2],w_a_4_sorted1[h3],w_a_4_sorted1[h4],w_a_4_sorted1[h5],w_a_4_sorted1[h6],w_su_4_sorted1[h7],w_su_4_sorted1[h8],w_a_4_sorted1[h9],w_a_4_sorted1[h10],w_a_4_sorted1[h11],w_su_4_sorted1[h12]]]))[::-1]
        
                                                            h_w_4_sorted  = np.sort(np.concatenate([h_w_4_sorted1[d1:d1+12],[h_w_4_sorted1[h1],h_w_4_sorted1[h2],h_w_4_sorted1[h3],h_w_4_sorted1[h4],h_w_4_sorted1[h5],h_w_4_sorted1[h6],h_w_4_sorted1[h7],h_w_4_sorted1[h8],h_w_4_sorted1[h9],h_w_4_sorted1[h10],h_w_4_sorted1[h11],h_w_4_sorted1[h12]]]))[::-1]
                                                            h_sp_4_sorted = np.sort(np.concatenate([h_sp_4_sorted1[d1:d1+12],[h_sp_4_sorted1[h1],h_sp_4_sorted1[h2],h_sp_4_sorted1[h3],h_sp_4_sorted1[h4],h_sp_4_sorted1[h5],h_sp_4_sorted1[h6],h_sp_4_sorted1[h7],h_sp_4_sorted1[h8],h_sp_4_sorted1[h9],h_sp_4_sorted1[h10],h_sp_4_sorted1[h11],h_sp_4_sorted1[h12]]]))[::-1]
                                                            h_su_4_sorted = np.sort(np.concatenate([h_su_4_sorted1[d1:d1+12],[h_su_4_sorted1[h1],h_su_4_sorted1[h2],h_su_4_sorted1[h3],h_su_4_sorted1[h4],h_su_4_sorted1[h5],h_su_4_sorted1[h6],h_su_4_sorted1[h7],h_su_4_sorted1[h8],h_su_4_sorted1[h9],h_su_4_sorted1[h10],h_su_4_sorted1[h11],h_su_4_sorted1[h12]]]))[::-1]
                                                            h_a_4_sorted  = np.sort(np.concatenate([h_a_4_sorted1[d1:d1+12],[h_a_4_sorted1[h1],h_a_4_sorted1[h2],h_a_4_sorted1[h3],h_a_4_sorted1[h4],h_a_4_sorted1[h5],h_a_4_sorted1[h6],h_a_4_sorted1[h7],h_a_4_sorted1[h8],h_a_4_sorted1[h9],h_a_4_sorted1[h10],h_a_4_sorted1[h11],h_a_4_sorted1[h12]]]))[::-1]
                
                                                            d_w_4_sorted  = np.sort(np.concatenate([d_w_4_sorted1[d1:d1+12],[d_w_4_sorted1[h1],d_w_4_sorted1[h2],d_w_4_sorted1[h3],d_w_4_sorted1[h4],d_w_4_sorted1[h5],d_w_4_sorted1[h6],d_w_4_sorted1[h7],d_w_4_sorted1[h8],d_w_4_sorted1[h9],d_w_4_sorted1[h10],d_w_4_sorted1[h11],d_w_4_sorted1[h12]]]))[::-1]
                                                            d_sp_4_sorted = np.sort(np.concatenate([d_sp_4_sorted1[d1:d1+12],[d_sp_4_sorted1[h1],d_sp_4_sorted1[h2],d_sp_4_sorted1[h3],d_sp_4_sorted1[h4],d_sp_4_sorted1[h5],d_sp_4_sorted1[h6],d_sp_4_sorted1[h7],d_sp_4_sorted1[h8],d_sp_4_sorted1[h9],d_sp_4_sorted1[h10],d_sp_4_sorted1[h11],d_sp_4_sorted1[h12]]]))[::-1]
                                                            d_su_4_sorted = np.sort(np.concatenate([d_su_4_sorted1[d1:d1+12],[d_su_4_sorted1[h1],d_su_4_sorted1[h2],d_su_4_sorted1[h3],d_su_4_sorted1[h4],d_su_4_sorted1[h5],d_su_4_sorted1[h6],d_su_4_sorted1[h7],d_su_4_sorted1[h8],d_su_4_sorted1[h9],d_su_4_sorted1[h10],d_su_4_sorted1[h11],d_su_4_sorted1[h12]]]))[::-1]
                                                            d_a_4_sorted  = np.sort(np.concatenate([d_a_4_sorted1[d1:d1+12],[d_a_4_sorted1[h1],d_a_4_sorted1[h2],d_a_4_sorted1[h3],d_a_4_sorted1[h4],d_a_4_sorted1[h5],d_a_4_sorted1[h6],d_a_4_sorted1[h7],d_a_4_sorted1[h8],d_a_4_sorted1[h9],d_a_4_sorted1[h10],d_a_4_sorted1[h11],d_a_4_sorted1[h12]]]))[::-1]
                                
                                                            x2 = int(2190/2/hourly_ts_day)
                                                            sum1 = 0
                                                            sum2 = 0    
                                                            sum3 = 0
                                                            sum4 = 0
                                                            while x2 < 2190 - int(2190/2/hourly_ts_day):
                                                                sum1 = sum1 + ((solar_load_curve_Wi[x2] - s_w_4_sorted[int(x2/2190/2/hourly_ts_day)])**2) *solarweight      
                                                                sum2 = sum2 + ((solar_load_curve_Sp[x2] - s_sp_4_sorted[int(x2/2190/2/hourly_ts_day)])**2)*solarweight
                                                                sum3 = sum3 + ((solar_load_curve_Su[x2] - s_su_4_sorted[int(x2/2190/2/hourly_ts_day)])**2)*solarweight
                                                                sum4 = sum4 + ((solar_load_curve_Au[x2] - s_a_4_sorted[int(x2/2190/2/hourly_ts_day)])**2) *solarweight
                            
                                                                sum1 = sum1 + ((wind_load_curve_Wi[x2] - w_w_4_sorted[int(x2/2190/2/hourly_ts_day)])**2) *windweight
                                                                sum2 = sum2 + ((wind_load_curve_Sp[x2] - w_sp_4_sorted[int(x2/2190/2/hourly_ts_day)])**2)*windweight
                                                                sum3 = sum3 + ((wind_load_curve_Su[x2] - w_su_4_sorted[int(x2/2190/2/hourly_ts_day)])**2)*windweight
                                                                sum4 = sum4 + ((wind_load_curve_Au[x2] - w_a_4_sorted[int(x2/2190/2/hourly_ts_day)])**2) *windweight
        
                                                                sum1 = sum1 + ((hydro_load_curve_Wi[x2] - h_w_4_sorted[int(x2/2190/2/hourly_ts_day)])**2) *hydroweight # Hydropower is not well represented in the model, so we reduce the impact of hydropower on the final results.       
                                                                sum2 = sum2 + ((hydro_load_curve_Sp[x2] - h_sp_4_sorted[int(x2/2190/2/hourly_ts_day)])**2)*hydroweight 
                                                                sum3 = sum3 + ((hydro_load_curve_Su[x2] - h_su_4_sorted[int(x2/2190/2/hourly_ts_day)])**2)*hydroweight 
                                                                sum4 = sum4 + ((hydro_load_curve_Au[x2] - h_a_4_sorted[int(x2/2190/2/hourly_ts_day)])**2) *hydroweight
                        
                                                                sum1 = sum1 + ((demand_load_curve_Wi[x2] - d_w_4_sorted[int(x2/2190/2/hourly_ts_day)])**2) *demandweight          
                                                                sum2 = sum2 + ((demand_load_curve_Sp[x2] - d_sp_4_sorted[int(x2/2190/2/hourly_ts_day)])**2)*demandweight
                                                                sum3 = sum3 + ((demand_load_curve_Su[x2] - d_su_4_sorted[int(x2/2190/2/hourly_ts_day)])**2)*demandweight
                                                                sum4 = sum4 + ((demand_load_curve_Au[x2] - d_a_4_sorted[int(x2/2190/2/hourly_ts_day)])**2) *demandweight
                                                                x2 = x2 + 1
                                
                                                            if sum1 != 0 and sum1 < w_minimum[0]:
                                                                w_minimum = [sum1,w,d1,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12]
                                                                solar_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([s_w_4_sorted1[d1:d1+12],[s_w_4_sorted1[h1],s_w_4_sorted1[h2],s_w_4_sorted1[h3],s_w_4_sorted1[h4],s_w_4_sorted1[h5],s_w_4_sorted1[h6],s_w_4_sorted1[h7],s_w_4_sorted1[h8],s_w_4_sorted1[h9],s_w_4_sorted1[h10],s_w_4_sorted1[h11],s_w_4_sorted1[h12]]])
                                                                wind_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([w_w_4_sorted1[d1:d1+12],[w_w_4_sorted1[h1],w_w_4_sorted1[h2],w_w_4_sorted1[h3],w_w_4_sorted1[h4],w_w_4_sorted1[h5],w_w_4_sorted1[h6],w_w_4_sorted1[h7],w_w_4_sorted1[h8],w_w_4_sorted1[h9],w_w_4_sorted1[h10],w_w_4_sorted1[h11],w_w_4_sorted1[h12]]])
                                                                hydro_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([h_w_4_sorted1[d1:d1+12],[h_w_4_sorted1[h1],h_w_4_sorted1[h2],h_w_4_sorted1[h3],h_w_4_sorted1[h4],h_w_4_sorted1[h5],h_w_4_sorted1[h6],h_w_4_sorted1[h7],h_w_4_sorted1[h8],h_w_4_sorted1[h9],h_w_4_sorted1[h10],h_w_4_sorted1[h11],h_w_4_sorted1[h12]]])
                                                                demand_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([d_w_4_sorted1[d1:d1+12],[d_w_4_sorted1[h1],d_w_4_sorted1[h2],d_w_4_sorted1[h3],d_w_4_sorted1[h4],d_w_4_sorted1[h5],d_w_4_sorted1[h6],d_w_4_sorted1[h7],d_w_4_sorted1[h8],d_w_4_sorted1[h9],d_w_4_sorted1[h10],d_w_4_sorted1[h11],d_w_4_sorted1[h12]]])
                                                                solar_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = s_w_4_sorted
                                                                wind_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = w_w_4_sorted
                                                                hydro_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = h_w_4_sorted
                                                                demand_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = d_w_4_sorted                        
                                    
                                                            if sum2 != 0 and sum2 < sp_minimum[0]:
                                                                sp_minimum = [sum2,w,d1,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12]
                                                                solar_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([s_sp_4_sorted1[d1:d1+12],[s_sp_4_sorted1[h1],s_sp_4_sorted1[h2],s_sp_4_sorted1[h3],s_sp_4_sorted1[h4],s_sp_4_sorted1[h5],s_sp_4_sorted1[h6],s_sp_4_sorted1[h7],s_sp_4_sorted1[h8],s_sp_4_sorted1[h9],s_sp_4_sorted1[h10],s_sp_4_sorted1[h11],s_sp_4_sorted1[h12]]])
                                                                wind_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([w_sp_4_sorted1[d1:d1+12],[w_sp_4_sorted1[h1],w_sp_4_sorted1[h2],w_sp_4_sorted1[h3],w_sp_4_sorted1[h4],w_sp_4_sorted1[h5],w_sp_4_sorted1[h6],w_sp_4_sorted1[h7],w_sp_4_sorted1[h8],w_sp_4_sorted1[h9],w_sp_4_sorted1[h10],w_sp_4_sorted1[h11],w_sp_4_sorted1[h12]]])
                                                                hydro_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([h_sp_4_sorted1[d1:d1+12],[h_sp_4_sorted1[h1],h_sp_4_sorted1[h2],h_sp_4_sorted1[h3],h_sp_4_sorted1[h4],h_sp_4_sorted1[h5],h_sp_4_sorted1[h6],h_sp_4_sorted1[h7],h_sp_4_sorted1[h8],h_sp_4_sorted1[h9],h_sp_4_sorted1[h10],h_sp_4_sorted1[h11],h_sp_4_sorted1[h12]]])
                                                                demand_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([d_sp_4_sorted1[d1:d1+12],[d_sp_4_sorted1[h1],d_sp_4_sorted1[h2],d_sp_4_sorted1[h3],d_sp_4_sorted1[h4],d_sp_4_sorted1[h5],d_sp_4_sorted1[h6],d_sp_4_sorted1[h7],d_sp_4_sorted1[h8],d_sp_4_sorted1[h9],d_sp_4_sorted1[h10],d_sp_4_sorted1[h11],d_sp_4_sorted1[h12]]])
                                                                solar_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = s_sp_4_sorted
                                                                hydro_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = h_sp_4_sorted
                                                                wind_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = w_sp_4_sorted
                                                                demand_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = d_sp_4_sorted 
                                    
                                                            if sum3 != 0 and sum3 < su_minimum[0]:
                                                                su_minimum = [sum3,w,d1,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12]
                                                                solar_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([s_su_4_sorted1[d1:d1+12],[s_su_4_sorted1[h1],s_su_4_sorted1[h2],s_su_4_sorted1[h3],s_su_4_sorted1[h4],s_su_4_sorted1[h5],s_su_4_sorted1[h6],s_su_4_sorted1[h7],s_su_4_sorted1[h8],s_su_4_sorted1[h9],s_su_4_sorted1[h10],s_su_4_sorted1[h11],s_su_4_sorted1[h12]]])
                                                                wind_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([w_su_4_sorted1[d1:d1+12],[w_su_4_sorted1[h1],w_su_4_sorted1[h2],w_su_4_sorted1[h3],w_su_4_sorted1[h4],w_su_4_sorted1[h5],w_su_4_sorted1[h6],w_su_4_sorted1[h7],w_su_4_sorted1[h8],w_su_4_sorted1[h9],w_su_4_sorted1[h10],w_su_4_sorted1[h11],w_su_4_sorted1[h12]]])
                                                                hydro_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([h_su_4_sorted1[d1:d1+12],[h_su_4_sorted1[h1],h_su_4_sorted1[h2],h_su_4_sorted1[h3],h_su_4_sorted1[h4],h_su_4_sorted1[h5],h_su_4_sorted1[h6],h_su_4_sorted1[h7],h_su_4_sorted1[h8],h_su_4_sorted1[h9],h_su_4_sorted1[h10],h_su_4_sorted1[h11],h_su_4_sorted1[h12]]])
                                                                demand_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([d_su_4_sorted1[d1:d1+12],[d_su_4_sorted1[h1],d_su_4_sorted1[h2],d_su_4_sorted1[h3],d_su_4_sorted1[h4],d_su_4_sorted1[h5],d_su_4_sorted1[h6],d_su_4_sorted1[h7],d_su_4_sorted1[h8],d_su_4_sorted1[h9],d_su_4_sorted1[h10],d_su_4_sorted1[h11],d_su_4_sorted1[h12]]])
                                                                solar_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = s_su_4_sorted
                                                                wind_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = w_su_4_sorted
                                                                hydro_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = h_su_4_sorted
                                                                demand_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = d_su_4_sorted 
                                    
                                                            if sum4 != 0 and sum4 < a_minimum[0]:
                                                                a_minimum = [sum4,w,d1,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12]
                                                                solar_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([s_a_4_sorted1[d1:d1+12],[s_a_4_sorted1[h1],s_a_4_sorted1[h2],s_a_4_sorted1[h3],s_a_4_sorted1[h4],s_a_4_sorted1[h5],s_a_4_sorted1[h6],s_a_4_sorted1[h7],s_a_4_sorted1[h8],s_a_4_sorted1[h9],s_a_4_sorted1[h10],s_a_4_sorted1[h11],s_a_4_sorted1[h12]]])
                                                                wind_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([w_a_4_sorted1[d1:d1+12],[w_a_4_sorted1[h1],w_a_4_sorted1[h2],w_a_4_sorted1[h3],w_a_4_sorted1[h4],w_a_4_sorted1[h5],w_a_4_sorted1[h6],w_a_4_sorted1[h7],w_a_4_sorted1[h8],w_a_4_sorted1[h9],w_a_4_sorted1[h10],w_a_4_sorted1[h11],w_a_4_sorted1[h12]]])
                                                                hydro_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([h_a_4_sorted1[d1:d1+12],[h_a_4_sorted1[h1],h_a_4_sorted1[h2],h_a_4_sorted1[h3],h_a_4_sorted1[h4],h_a_4_sorted1[h5],h_a_4_sorted1[h6],h_a_4_sorted1[h7],h_a_4_sorted1[h8],h_a_4_sorted1[h9],h_a_4_sorted1[h10],h_a_4_sorted1[h11],h_a_4_sorted1[h12]]])
                                                                demand_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([d_a_4_sorted1[d1:d1+12],[d_a_4_sorted1[h1],d_a_4_sorted1[h2],d_a_4_sorted1[h3],d_a_4_sorted1[h4],d_a_4_sorted1[h5],d_a_4_sorted1[h6],d_a_4_sorted1[h7],d_a_4_sorted1[h8],d_a_4_sorted1[h9],d_a_4_sorted1[h10],d_a_4_sorted1[h11],d_a_4_sorted1[h12]]])
                                                                solar_results_sorted_seasonal[3*2*hourly_ts_day:ts] = s_a_4_sorted
                                                                wind_results_sorted_seasonal[3*2*hourly_ts_day:ts] = w_a_4_sorted
                                                                hydro_results_sorted_seasonal[3*2*hourly_ts_day:ts] = h_a_4_sorted
                                                                demand_results_sorted_seasonal[3*2*hourly_ts_day:ts] = d_a_4_sorted                             
                                                            
                                                            h12 = h12 + 1
                                                            while h12 in list_of_days:
                                                                  h12 = h12 + 1
                                                         h11 = h11 + 1
                                                         while h11 in list_of_days:
                                                               h11 = h11 + 1      
                                                      h10 = h10 + 1
                                                      while h10 in list_of_days:
                                                          h10 = h10 + 1
                                                   h9 = h9 + 1
                                                   while h9 in list_of_days:
                                                      h9 = h9 + 1                                     
                                                h8 = h8 + 1
                                                while h8 in list_of_days:
                                                    h8 = h8 + 1
                                             h7 = h7 + 1
                                             while h7 in list_of_days:
                                                 h7 = h7 + 1      
                                          h6 = h6 + 1
                                          while h6 in list_of_days:
                                            h6 = h6 + 1
                                     h5 = h5 + 1
                                     while h5 in list_of_days:
                                        h5 = h5 + 1                                     
                                h4 = h4 + 1
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
                d1 = d1 + mid_night
                print('r ' + regions_or_countries[region] + ' - w '+ str(w) + ' - d '+ str(d1))







            if hourly_ts_day == 8: # correto
             while d1 < 8*7-8: #28
                list_of_days = []
                list_of_days.append(d1)
                list_of_days.append(d1+1)
                list_of_days.append(d1+2)
                list_of_days.append(d1+3)
                list_of_days.append(d1+4)
                list_of_days.append(d1+5)    
                list_of_days.append(d1+6)
                list_of_days.append(d1+7)                    
                if d1 == 0:
                    h1 = 8
                else:
        
                    h1 = 0
                while h1 <  8*7-8-1: #27
                    list_of_days.append(h1)
                    if d1 == 0:
                        h2 = 8+1
                    elif d1 == 1:
                        h2 = 8+1
                    else:
                        h2 = 1
                    while h2 < 8*7-8-2: #26
                        list_of_days.append(h2)
                        if d1 == 0:
                            h3 = 8+2
                        elif d1 == 1:
                            h3 = 8+2
                        elif d1 == 2:
                            h3 = 8+2
                        else:
                            h3 = 2
                        while h3 < 8*7-8-3: #26
                            list_of_days.append(h3)
                            if d1 == 0:
                                h4 = 8+3
                            elif d1 == 1:
                                h4 = 8+3
                            elif d1 == 2:
                                h4 = 8+3
                            elif d1 == 3:
                                h4 = 8+3
                            else:
                                h4 = 3    
                            while h4 < 8*7-8-4: #26
                                list_of_days.append(h4)
                                if d1 == 0:
                                    h5 = 8+4
                                elif d1 == 1:
                                    h5 = 8+4
                                elif d1 == 2:
                                    h5 = 8+4
                                elif d1 == 3:
                                    h5 = 8+4
                                elif d1 == 4:
                                    h5 = 8+4
                                else:
                                    h5 = 4
                                    while h5 < 8*7-8-5: #26
                                     list_of_days.append(h5)
                                     if d1 == 0:
                                         h6 = 8+5
                                     elif d1 == 1:
                                         h6 = 8+5
                                     elif d1 == 2:
                                         h6 = 8+5
                                     elif d1 == 3:
                                         h6 = 8+5
                                     elif d1 == 4:
                                         h6 = 8+5       
                                     elif d1 == 5:
                                         h6 = 8+5
                                     else:
                                         h6 = 5   
                                    
                                     while h6 < 8*7-8-6:
                                          list_of_days.append(h6)
                                          if d1 == 0:
                                              h7 = 8+6
                                          elif d1 == 1:
                                              h7 = 8+6
                                          elif d1 == 2:
                                              h7 = 8+6
                                          elif d1 == 3:
                                              h7 = 8+6
                                          elif d1 == 4:
                                              h7 = 8+6       
                                          elif d1 == 5:
                                              h7 = 8+6
                                          elif d1 == 6:
                                              h7 = 8+6
                                          else:
                                              h7 = 6   
                                    
                                          while h7 < 8*7-8-7:
                                             list_of_days.append(h7)
                                             if d1 == 0:
                                                 h8 = 8+7
                                             elif d1 == 1:
                                                 h8 = 8+7
                                             elif d1 == 2:
                                                 h8 = 8+7
                                             elif d1 == 3:
                                                 h8 = 8+7
                                             elif d1 == 4:
                                                 h8 = 8+7       
                                             elif d1 == 5:
                                                 h8 = 8+7
                                             elif d1 == 6:
                                                 h8 = 8+7       
                                             elif d1 == 7:
                                                 h8 = 8+7
                                             else:
                                                 h8 = 7 
                                    
                                             while h8 < 8*7-8-8:
                                                list_of_days.append(h8) 
                                                s_w_4_sorted  = np.sort(np.concatenate([s_w_4_sorted1[d1:d1+8],[s_w_4_sorted1[h1],s_w_4_sorted1[h2],s_w_4_sorted1[h3],s_w_4_sorted1[h4],s_w_4_sorted1[h5],s_w_4_sorted1[h6],s_w_4_sorted1[h7],s_w_4_sorted1[h8]]]))[::-1]
                                                s_sp_4_sorted = np.sort(np.concatenate([s_sp_4_sorted1[d1:d1+8],[s_sp_4_sorted1[h1],s_sp_4_sorted1[h2],s_sp_4_sorted1[h3],s_sp_4_sorted1[h4],s_sp_4_sorted1[h5],s_sp_4_sorted1[h6],s_sp_4_sorted1[h7],s_sp_4_sorted1[h8]]]))[::-1]
                                                s_su_4_sorted = np.sort(np.concatenate([s_su_4_sorted1[d1:d1+8],[s_su_4_sorted1[h1],s_su_4_sorted1[h2],s_su_4_sorted1[h3],s_su_4_sorted1[h4],s_su_4_sorted1[h5],s_su_4_sorted1[h6],s_su_4_sorted1[h7],s_su_4_sorted1[h8]]]))[::-1]
                                                s_a_4_sorted  = np.sort(np.concatenate([s_a_4_sorted1[d1:d1+8],[s_a_4_sorted1[h1],s_a_4_sorted1[h2],s_a_4_sorted1[h3],s_a_4_sorted1[h4],s_a_4_sorted1[h5],s_a_4_sorted1[h6],s_a_4_sorted1[h7],s_a_4_sorted1[h8]]]))[::-1]
                
                                                w_w_4_sorted  = np.sort(np.concatenate([w_w_4_sorted1[d1:d1+8],[w_w_4_sorted1[h1],w_w_4_sorted1[h2],w_w_4_sorted1[h3],w_w_4_sorted1[h4],w_w_4_sorted1[h5],w_w_4_sorted1[h6],w_w_4_sorted1[h7],w_w_4_sorted1[h8]]]))[::-1]
                                                w_sp_4_sorted = np.sort(np.concatenate([w_sp_4_sorted1[d1:d1+8],[w_sp_4_sorted1[h1],w_sp_4_sorted1[h2],w_sp_4_sorted1[h3],w_sp_4_sorted1[h4],w_sp_4_sorted1[h5],w_sp_4_sorted1[h6],w_sp_4_sorted1[h7],w_sp_4_sorted1[h8]]]))[::-1]
                                                w_su_4_sorted = np.sort(np.concatenate([w_su_4_sorted1[d1:d1+8],[w_su_4_sorted1[h1],w_su_4_sorted1[h2],w_su_4_sorted1[h3],w_su_4_sorted1[h4],w_su_4_sorted1[h5],w_su_4_sorted1[h6],w_su_4_sorted1[h7],w_su_4_sorted1[h8]]]))[::-1]
                                                w_a_4_sorted  = np.sort(np.concatenate([w_a_4_sorted1[d1:d1+8],[w_a_4_sorted1[h1],w_a_4_sorted1[h2],w_a_4_sorted1[h3],w_a_4_sorted1[h4],w_a_4_sorted1[h5],w_a_4_sorted1[h6],w_su_4_sorted1[h7],w_su_4_sorted1[h8]]]))[::-1]
        
                                                h_w_4_sorted  = np.sort(np.concatenate([h_w_4_sorted1[d1:d1+8],[h_w_4_sorted1[h1],h_w_4_sorted1[h2],h_w_4_sorted1[h3],h_w_4_sorted1[h4],h_w_4_sorted1[h5],h_w_4_sorted1[h6],h_w_4_sorted1[h7],h_w_4_sorted1[h8]]]))[::-1]
                                                h_sp_4_sorted = np.sort(np.concatenate([h_sp_4_sorted1[d1:d1+8],[h_sp_4_sorted1[h1],h_sp_4_sorted1[h2],h_sp_4_sorted1[h3],h_sp_4_sorted1[h4],h_sp_4_sorted1[h5],h_sp_4_sorted1[h6],h_sp_4_sorted1[h7],h_sp_4_sorted1[h8]]]))[::-1]
                                                h_su_4_sorted = np.sort(np.concatenate([h_su_4_sorted1[d1:d1+8],[h_su_4_sorted1[h1],h_su_4_sorted1[h2],h_su_4_sorted1[h3],h_su_4_sorted1[h4],h_su_4_sorted1[h5],h_su_4_sorted1[h6],h_su_4_sorted1[h7],h_su_4_sorted1[h8]]]))[::-1]
                                                h_a_4_sorted  = np.sort(np.concatenate([h_a_4_sorted1[d1:d1+8],[h_a_4_sorted1[h1],h_a_4_sorted1[h2],h_a_4_sorted1[h3],h_a_4_sorted1[h4],h_a_4_sorted1[h5],h_a_4_sorted1[h6],h_a_4_sorted1[h7],h_a_4_sorted1[h8]]]))[::-1]
                
                                                d_w_4_sorted  = np.sort(np.concatenate([d_w_4_sorted1[d1:d1+8],[d_w_4_sorted1[h1],d_w_4_sorted1[h2],d_w_4_sorted1[h3],d_w_4_sorted1[h4],d_w_4_sorted1[h5],d_w_4_sorted1[h6],d_w_4_sorted1[h7],d_w_4_sorted1[h8]]]))[::-1]
                                                d_sp_4_sorted = np.sort(np.concatenate([d_sp_4_sorted1[d1:d1+8],[d_sp_4_sorted1[h1],d_sp_4_sorted1[h2],d_sp_4_sorted1[h3],d_sp_4_sorted1[h4],d_sp_4_sorted1[h5],d_sp_4_sorted1[h6],d_sp_4_sorted1[h7],d_sp_4_sorted1[h8]]]))[::-1]
                                                d_su_4_sorted = np.sort(np.concatenate([d_su_4_sorted1[d1:d1+8],[d_su_4_sorted1[h1],d_su_4_sorted1[h2],d_su_4_sorted1[h3],d_su_4_sorted1[h4],d_su_4_sorted1[h5],d_su_4_sorted1[h6],d_su_4_sorted1[h7],d_su_4_sorted1[h8]]]))[::-1]
                                                d_a_4_sorted  = np.sort(np.concatenate([d_a_4_sorted1[d1:d1+8],[d_a_4_sorted1[h1],d_a_4_sorted1[h2],d_a_4_sorted1[h3],d_a_4_sorted1[h4],d_a_4_sorted1[h5],d_a_4_sorted1[h6],d_a_4_sorted1[h7],d_a_4_sorted1[h8]]]))[::-1]
                                
                                                x2 = int(2190/2/hourly_ts_day)
                                                sum1 = 0
                                                sum2 = 0    
                                                sum3 = 0
                                                sum4 = 0
                                                while x2 < 2190 - int(2190/2/hourly_ts_day):
                                                    sum1 = sum1 + ((solar_load_curve_Wi[x2] - s_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *solarweight     
                                                    sum2 = sum2 + ((solar_load_curve_Sp[x2] - s_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*solarweight
                                                    sum3 = sum3 + ((solar_load_curve_Su[x2] - s_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*solarweight
                                                    sum4 = sum4 + ((solar_load_curve_Au[x2] - s_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *solarweight
                            
                                                    sum1 = sum1 + ((wind_load_curve_Wi[x2] - w_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *windweight
                                                    sum2 = sum2 + ((wind_load_curve_Sp[x2] - w_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*windweight
                                                    sum3 = sum3 + ((wind_load_curve_Su[x2] - w_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*windweight
                                                    sum4 = sum4 + ((wind_load_curve_Au[x2] - w_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*windweight
        
                                                    sum1 = sum1 + ((hydro_load_curve_Wi[x2] - h_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *hydroweight # Hydropower is not well represented in the model, so we reduce the impact of hydropower on the final results.       
                                                    sum2 = sum2 + ((hydro_load_curve_Sp[x2] - h_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*hydroweight 
                                                    sum3 = sum3 + ((hydro_load_curve_Su[x2] - h_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*hydroweight 
                                                    sum4 = sum4 + ((hydro_load_curve_Au[x2] - h_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *hydroweight
                        
                                                    sum1 = sum1 + ((demand_load_curve_Wi[x2] - d_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *demandweight 
                                                    sum2 = sum2 + ((demand_load_curve_Sp[x2] - d_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*demandweight 
                                                    sum3 = sum3 + ((demand_load_curve_Su[x2] - d_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*demandweight 
                                                    sum4 = sum4 + ((demand_load_curve_Au[x2] - d_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *demandweight 
                                                    x2 = x2 + 1
                                
                                                if sum1 != 0 and sum1 < w_minimum[0]:
                                                    w_minimum = [sum1,w,d1,h1,h2,h3,h4,h5,h6,h7,h8]
                                                    solar_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([s_w_4_sorted1[d1:d1+8],[s_w_4_sorted1[h1],s_w_4_sorted1[h2],s_w_4_sorted1[h3],s_w_4_sorted1[h4],s_w_4_sorted1[h5],s_w_4_sorted1[h6],s_w_4_sorted1[h7],s_w_4_sorted1[h8]]])
                                                    wind_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([w_w_4_sorted1[d1:d1+8],[w_w_4_sorted1[h1],w_w_4_sorted1[h2],w_w_4_sorted1[h3],w_w_4_sorted1[h4],w_w_4_sorted1[h5],w_w_4_sorted1[h6],w_w_4_sorted1[h7],w_w_4_sorted1[h8]]])
                                                    hydro_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([h_w_4_sorted1[d1:d1+8],[h_w_4_sorted1[h1],h_w_4_sorted1[h2],h_w_4_sorted1[h3],h_w_4_sorted1[h4],h_w_4_sorted1[h5],h_w_4_sorted1[h6],h_w_4_sorted1[h7],h_w_4_sorted1[h8]]])
                                                    demand_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([d_w_4_sorted1[d1:d1+8],[d_w_4_sorted1[h1],d_w_4_sorted1[h2],d_w_4_sorted1[h3],d_w_4_sorted1[h4],d_w_4_sorted1[h5],d_w_4_sorted1[h6],d_w_4_sorted1[h7],d_w_4_sorted1[h8]]])
                                                    solar_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = s_w_4_sorted
                                                    wind_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = w_w_4_sorted
                                                    hydro_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = h_w_4_sorted
                                                    demand_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = d_w_4_sorted                        
                                    
                                                if sum2 != 0 and sum2 < sp_minimum[0]:
                                                    sp_minimum = [sum2,w,d1,h1,h2,h3,h4,h5,h6,h7,h8]
                                                    solar_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([s_sp_4_sorted1[d1:d1+8],[s_sp_4_sorted1[h1],s_sp_4_sorted1[h2],s_sp_4_sorted1[h3],s_sp_4_sorted1[h4],s_sp_4_sorted1[h5],s_sp_4_sorted1[h6],s_sp_4_sorted1[h7],s_sp_4_sorted1[h8]]])
                                                    wind_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([w_sp_4_sorted1[d1:d1+8],[w_sp_4_sorted1[h1],w_sp_4_sorted1[h2],w_sp_4_sorted1[h3],w_sp_4_sorted1[h4],w_sp_4_sorted1[h5],w_sp_4_sorted1[h6],w_sp_4_sorted1[h7],w_sp_4_sorted1[h8]]])
                                                    hydro_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([h_sp_4_sorted1[d1:d1+8],[h_sp_4_sorted1[h1],h_sp_4_sorted1[h2],h_sp_4_sorted1[h3],h_sp_4_sorted1[h4],h_sp_4_sorted1[h5],h_sp_4_sorted1[h6],h_sp_4_sorted1[h7],h_sp_4_sorted1[h8]]])
                                                    demand_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([d_sp_4_sorted1[d1:d1+8],[d_sp_4_sorted1[h1],d_sp_4_sorted1[h2],d_sp_4_sorted1[h3],d_sp_4_sorted1[h4],d_sp_4_sorted1[h5],d_sp_4_sorted1[h6],d_sp_4_sorted1[h7],d_sp_4_sorted1[h8]]])
                                                    solar_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = s_sp_4_sorted
                                                    hydro_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = h_sp_4_sorted
                                                    wind_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = w_sp_4_sorted
                                                    demand_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = d_sp_4_sorted 
                                    
                                                if sum3 != 0 and sum3 < su_minimum[0]:
                                                    su_minimum = [sum3,w,d1,h1,h2,h3,h4,h5,h6,h7,h8]
                                                    solar_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([s_su_4_sorted1[d1:d1+8],[s_su_4_sorted1[h1],s_su_4_sorted1[h2],s_su_4_sorted1[h3],s_su_4_sorted1[h4],s_su_4_sorted1[h5],s_su_4_sorted1[h6],s_su_4_sorted1[h7],s_su_4_sorted1[h8]]])
                                                    wind_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([w_su_4_sorted1[d1:d1+8],[w_su_4_sorted1[h1],w_su_4_sorted1[h2],w_su_4_sorted1[h3],w_su_4_sorted1[h4],w_su_4_sorted1[h5],w_su_4_sorted1[h6],w_su_4_sorted1[h7],w_su_4_sorted1[h8]]])
                                                    hydro_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([h_su_4_sorted1[d1:d1+8],[h_su_4_sorted1[h1],h_su_4_sorted1[h2],h_su_4_sorted1[h3],h_su_4_sorted1[h4],h_su_4_sorted1[h5],h_su_4_sorted1[h6],h_su_4_sorted1[h7],h_su_4_sorted1[h8]]])
                                                    demand_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([d_su_4_sorted1[d1:d1+8],[d_su_4_sorted1[h1],d_su_4_sorted1[h2],d_su_4_sorted1[h3],d_su_4_sorted1[h4],d_su_4_sorted1[h5],d_su_4_sorted1[h6],d_su_4_sorted1[h7],d_su_4_sorted1[h8]]])
                                                    solar_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = s_su_4_sorted
                                                    wind_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = w_su_4_sorted
                                                    hydro_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = h_su_4_sorted
                                                    demand_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = d_su_4_sorted 
                                    
                                                if sum4 != 0 and sum4 < a_minimum[0]:
                                                    a_minimum = [sum4,w,d1,h1,h2,h3,h4,h5,h6,h7,h8]
                                                    solar_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([s_a_4_sorted1[d1:d1+8],[s_a_4_sorted1[h1],s_a_4_sorted1[h2],s_a_4_sorted1[h3],s_a_4_sorted1[h4],s_a_4_sorted1[h5],s_a_4_sorted1[h6],s_a_4_sorted1[h7],s_a_4_sorted1[h8]]])
                                                    wind_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([w_a_4_sorted1[d1:d1+8],[w_a_4_sorted1[h1],w_a_4_sorted1[h2],w_a_4_sorted1[h3],w_a_4_sorted1[h4],w_a_4_sorted1[h5],w_a_4_sorted1[h6],w_a_4_sorted1[h7],w_a_4_sorted1[h8]]])
                                                    hydro_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([h_a_4_sorted1[d1:d1+8],[h_a_4_sorted1[h1],h_a_4_sorted1[h2],h_a_4_sorted1[h3],h_a_4_sorted1[h4],h_a_4_sorted1[h5],h_a_4_sorted1[h6],h_a_4_sorted1[h7],h_a_4_sorted1[h8]]])
                                                    demand_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([d_a_4_sorted1[d1:d1+8],[d_a_4_sorted1[h1],d_a_4_sorted1[h2],d_a_4_sorted1[h3],d_a_4_sorted1[h4],d_a_4_sorted1[h5],d_a_4_sorted1[h6],d_a_4_sorted1[h7],d_a_4_sorted1[h8]]])
                                                    solar_results_sorted_seasonal[3*2*hourly_ts_day:ts] = s_a_4_sorted
                                                    wind_results_sorted_seasonal[3*2*hourly_ts_day:ts] = w_a_4_sorted
                                                    hydro_results_sorted_seasonal[3*2*hourly_ts_day:ts] = h_a_4_sorted
                                                    demand_results_sorted_seasonal[3*2*hourly_ts_day:ts] = d_a_4_sorted                             

                                                h8 = h8 + 1
                                                while h8 in list_of_days:
                                                    h8 = h8 + 1
                                             h7 = h7 + 1
                                             while h7 in list_of_days:
                                                 h7 = h7 + 1      
                                          h6 = h6 + 1
                                          while h6 in list_of_days:
                                            h6 = h6 + 1
                                     h5 = h5 + 1
                                     while h5 in list_of_days:
                                        h5 = h5 + 1                                     
                                h4 = h4 + 1
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
                d1 = d1 + mid_night
                print('r ' + regions_or_countries[region] + ' - w '+ str(w) + ' - d '+ str(d1))












            if hourly_ts_day == 6: # correto
             while d1 < 6*7-6: #28
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
                while h1 <  6*7-6-1: #27
                    list_of_days.append(h1)
                    if d1 == 0:
                        h2 = 6+1
                    elif d1 == 1:
                        h2 = 6+1
                    else:
                        h2 = 1
                    while h2 < 6*7-6-2: #26
                        list_of_days.append(h2)
                        if d1 == 0:
                            h3 = 6+2
                        elif d1 == 1:
                            h3 = 6+2
                        elif d1 == 2:
                            h3 = 6+2
                        else:
                            h3 = 2
                        while h3 < 6*7-6-3: #26
                            list_of_days.append(h3)
                            if d1 == 0:
                                h4 = 6+3
                            elif d1 == 1:
                                h4 = 6+3
                            elif d1 == 2:
                                h4 = 6+3
                            elif d1 == 3:
                                h4 = 6+3
                            else:
                                h4 = 3    
                            while h4 < 6*7-6-4: #26
                                list_of_days.append(h4)
                                if d1 == 0:
                                    h5 = 6+4
                                elif d1 == 1:
                                    h5 = 6+4
                                elif d1 == 2:
                                    h5 = 6+4
                                elif d1 == 3:
                                    h5 = 6+4
                                elif d1 == 4:
                                    h5 = 6+4
                                else:
                                    h5 = 4
                                    while h5 < 6*7-6-5: #26
                                     list_of_days.append(h5)
                                     if d1 == 0:
                                         h6 = 6+5
                                     elif d1 == 1:
                                         h6 = 6+5
                                     elif d1 == 2:
                                         h6 = 6+5
                                     elif d1 == 3:
                                         h6 = 6+5
                                     elif d1 == 4:
                                         h6 = 6+5       
                                     elif d1 == 5:
                                         h6 = 6+5
                                     else:
                                         h6 = 5   
                                    
                                     while h6 < 6*7-6-6:
                                        list_of_days.append(h6)
                               
                                        s_w_4_sorted  = np.sort(np.concatenate([s_w_4_sorted1[d1:d1+6],[s_w_4_sorted1[h1],s_w_4_sorted1[h2],s_w_4_sorted1[h3],s_w_4_sorted1[h4],s_w_4_sorted1[h5],s_w_4_sorted1[h6]]]))[::-1]
                                        s_sp_4_sorted = np.sort(np.concatenate([s_sp_4_sorted1[d1:d1+6],[s_sp_4_sorted1[h1],s_sp_4_sorted1[h2],s_sp_4_sorted1[h3],s_sp_4_sorted1[h4],s_sp_4_sorted1[h5],s_sp_4_sorted1[h6]]]))[::-1]
                                        s_su_4_sorted = np.sort(np.concatenate([s_su_4_sorted1[d1:d1+6],[s_su_4_sorted1[h1],s_su_4_sorted1[h2],s_su_4_sorted1[h3],s_su_4_sorted1[h4],s_su_4_sorted1[h5],s_su_4_sorted1[h6]]]))[::-1]
                                        s_a_4_sorted  = np.sort(np.concatenate([s_a_4_sorted1[d1:d1+6],[s_a_4_sorted1[h1],s_a_4_sorted1[h2],s_a_4_sorted1[h3],s_a_4_sorted1[h4],s_a_4_sorted1[h5],s_a_4_sorted1[h6]]]))[::-1]
                
                                        w_w_4_sorted  = np.sort(np.concatenate([w_w_4_sorted1[d1:d1+6],[w_w_4_sorted1[h1],w_w_4_sorted1[h2],w_w_4_sorted1[h3],w_w_4_sorted1[h4],w_w_4_sorted1[h5],w_w_4_sorted1[h6]]]))[::-1]
                                        w_sp_4_sorted = np.sort(np.concatenate([w_sp_4_sorted1[d1:d1+6],[w_sp_4_sorted1[h1],w_sp_4_sorted1[h2],w_sp_4_sorted1[h3],w_sp_4_sorted1[h4],w_sp_4_sorted1[h5],w_sp_4_sorted1[h6]]]))[::-1]
                                        w_su_4_sorted = np.sort(np.concatenate([w_su_4_sorted1[d1:d1+6],[w_su_4_sorted1[h1],w_su_4_sorted1[h2],w_su_4_sorted1[h3],w_su_4_sorted1[h4],w_su_4_sorted1[h5],w_su_4_sorted1[h6]]]))[::-1]
                                        w_a_4_sorted  = np.sort(np.concatenate([w_a_4_sorted1[d1:d1+6],[w_a_4_sorted1[h1],w_a_4_sorted1[h2],w_a_4_sorted1[h3],w_a_4_sorted1[h4],w_a_4_sorted1[h5],w_a_4_sorted1[h6]]]))[::-1]
        
                                        h_w_4_sorted  = np.sort(np.concatenate([h_w_4_sorted1[d1:d1+6],[h_w_4_sorted1[h1],h_w_4_sorted1[h2],h_w_4_sorted1[h3],h_w_4_sorted1[h4],h_w_4_sorted1[h5],h_w_4_sorted1[h6]]]))[::-1]
                                        h_sp_4_sorted = np.sort(np.concatenate([h_sp_4_sorted1[d1:d1+6],[h_sp_4_sorted1[h1],h_sp_4_sorted1[h2],h_sp_4_sorted1[h3],h_sp_4_sorted1[h4],h_sp_4_sorted1[h5],h_sp_4_sorted1[h6]]]))[::-1]
                                        h_su_4_sorted = np.sort(np.concatenate([h_su_4_sorted1[d1:d1+6],[h_su_4_sorted1[h1],h_su_4_sorted1[h2],h_su_4_sorted1[h3],h_su_4_sorted1[h4],h_su_4_sorted1[h5],h_su_4_sorted1[h6]]]))[::-1]
                                        h_a_4_sorted  = np.sort(np.concatenate([h_a_4_sorted1[d1:d1+6],[h_a_4_sorted1[h1],h_a_4_sorted1[h2],h_a_4_sorted1[h3],h_a_4_sorted1[h4],h_a_4_sorted1[h5],h_a_4_sorted1[h6]]]))[::-1]
                
                                        d_w_4_sorted  = np.sort(np.concatenate([d_w_4_sorted1[d1:d1+6],[d_w_4_sorted1[h1],d_w_4_sorted1[h2],d_w_4_sorted1[h3],d_w_4_sorted1[h4],d_w_4_sorted1[h5],d_w_4_sorted1[h6]]]))[::-1]
                                        d_sp_4_sorted = np.sort(np.concatenate([d_sp_4_sorted1[d1:d1+6],[d_sp_4_sorted1[h1],d_sp_4_sorted1[h2],d_sp_4_sorted1[h3],d_sp_4_sorted1[h4],d_sp_4_sorted1[h5],d_sp_4_sorted1[h6]]]))[::-1]
                                        d_su_4_sorted = np.sort(np.concatenate([d_su_4_sorted1[d1:d1+6],[d_su_4_sorted1[h1],d_su_4_sorted1[h2],d_su_4_sorted1[h3],d_su_4_sorted1[h4],d_su_4_sorted1[h5],d_su_4_sorted1[h6]]]))[::-1]
                                        d_a_4_sorted  = np.sort(np.concatenate([d_a_4_sorted1[d1:d1+6],[d_a_4_sorted1[h1],d_a_4_sorted1[h2],d_a_4_sorted1[h3],d_a_4_sorted1[h4],d_a_4_sorted1[h5],d_a_4_sorted1[h6]]]))[::-1]
                                
                                        x2 = int(2190/2/hourly_ts_day)
                                        sum1 = 0
                                        sum2 = 0    
                                        sum3 = 0
                                        sum4 = 0
                                        while x2 < 2190 - int(2190/2/hourly_ts_day):
                                            sum1 = sum1 + ((solar_load_curve_Wi[x2] - s_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *solarweight         
                                            sum2 = sum2 + ((solar_load_curve_Sp[x2] - s_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*solarweight 
                                            sum3 = sum3 + ((solar_load_curve_Su[x2] - s_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*solarweight 
                                            sum4 = sum4 + ((solar_load_curve_Au[x2] - s_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *solarweight 
                            
                                            sum1 = sum1 + ((wind_load_curve_Wi[x2] - w_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *windweight
                                            sum2 = sum2 + ((wind_load_curve_Sp[x2] - w_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*windweight
                                            sum3 = sum3 + ((wind_load_curve_Su[x2] - w_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*windweight
                                            sum4 = sum4 + ((wind_load_curve_Au[x2] - w_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *windweight
        
                                            sum1 = sum1 + ((hydro_load_curve_Wi[x2] - h_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *hydroweight # Hydropower is not well represented in the model, so we reduce the impact of hydropower on the final results.       
                                            sum2 = sum2 + ((hydro_load_curve_Sp[x2] - h_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*hydroweight 
                                            sum3 = sum3 + ((hydro_load_curve_Su[x2] - h_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*hydroweight 
                                            sum4 = sum4 + ((hydro_load_curve_Au[x2] - h_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *hydroweight
                        
                                            sum1 = sum1 + ((demand_load_curve_Wi[x2] - d_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *demandweight
                                            sum2 = sum2 + ((demand_load_curve_Sp[x2] - d_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*demandweight
                                            sum3 = sum3 + ((demand_load_curve_Su[x2] - d_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*demandweight
                                            sum4 = sum4 + ((demand_load_curve_Au[x2] - d_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *demandweight
                                            x2 = x2 + 1
                                
                                        if sum1 != 0 and sum1 < w_minimum[0]:
                                            w_minimum = [sum1,w,d1,h1,h2,h3,h4,h5,h6]
                                            solar_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([s_w_4_sorted1[d1:d1+6],[s_w_4_sorted1[h1],s_w_4_sorted1[h2],s_w_4_sorted1[h3],s_w_4_sorted1[h4],s_w_4_sorted1[h5],s_w_4_sorted1[h6]]])
                                            wind_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([w_w_4_sorted1[d1:d1+6],[w_w_4_sorted1[h1],w_w_4_sorted1[h2],w_w_4_sorted1[h3],w_w_4_sorted1[h4],w_w_4_sorted1[h5],w_w_4_sorted1[h6]]])
                                            hydro_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([h_w_4_sorted1[d1:d1+6],[h_w_4_sorted1[h1],h_w_4_sorted1[h2],h_w_4_sorted1[h3],h_w_4_sorted1[h4],h_w_4_sorted1[h5],h_w_4_sorted1[h6]]])
                                            demand_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([d_w_4_sorted1[d1:d1+6],[d_w_4_sorted1[h1],d_w_4_sorted1[h2],d_w_4_sorted1[h3],d_w_4_sorted1[h4],d_w_4_sorted1[h5],d_w_4_sorted1[h6]]])
                                            solar_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = s_w_4_sorted
                                            wind_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = w_w_4_sorted
                                            hydro_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = h_w_4_sorted
                                            demand_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = d_w_4_sorted                        
                                    
                                        if sum2 != 0 and sum2 < sp_minimum[0]:
                                            sp_minimum = [sum2,w,d1,h1,h2,h3,h4,h5,h6]
                                            solar_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([s_sp_4_sorted1[d1:d1+6],[s_sp_4_sorted1[h1],s_sp_4_sorted1[h2],s_sp_4_sorted1[h3],s_sp_4_sorted1[h4],s_sp_4_sorted1[h5],s_sp_4_sorted1[h6]]])
                                            wind_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([w_sp_4_sorted1[d1:d1+6],[w_sp_4_sorted1[h1],w_sp_4_sorted1[h2],w_sp_4_sorted1[h3],w_sp_4_sorted1[h4],w_sp_4_sorted1[h5],w_sp_4_sorted1[h6]]])
                                            hydro_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([h_sp_4_sorted1[d1:d1+6],[h_sp_4_sorted1[h1],h_sp_4_sorted1[h2],h_sp_4_sorted1[h3],h_sp_4_sorted1[h4],h_sp_4_sorted1[h5],h_sp_4_sorted1[h6]]])
                                            demand_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([d_sp_4_sorted1[d1:d1+6],[d_sp_4_sorted1[h1],d_sp_4_sorted1[h2],d_sp_4_sorted1[h3],d_sp_4_sorted1[h4],d_sp_4_sorted1[h5],d_sp_4_sorted1[h6]]])
                                            solar_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = s_sp_4_sorted
                                            hydro_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = h_sp_4_sorted
                                            wind_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = w_sp_4_sorted
                                            demand_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = d_sp_4_sorted 
                                    
                                        if sum3 != 0 and sum3 < su_minimum[0]:
                                            su_minimum = [sum3,w,d1,h1,h2,h3,h4,h5,h6]
                                            solar_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([s_su_4_sorted1[d1:d1+6],[s_su_4_sorted1[h1],s_su_4_sorted1[h2],s_su_4_sorted1[h3],s_su_4_sorted1[h4],s_su_4_sorted1[h5],s_su_4_sorted1[h6]]])
                                            wind_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([w_su_4_sorted1[d1:d1+6],[w_su_4_sorted1[h1],w_su_4_sorted1[h2],w_su_4_sorted1[h3],w_su_4_sorted1[h4],w_su_4_sorted1[h5],w_su_4_sorted1[h6]]])
                                            hydro_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([h_su_4_sorted1[d1:d1+6],[h_su_4_sorted1[h1],h_su_4_sorted1[h2],h_su_4_sorted1[h3],h_su_4_sorted1[h4],h_su_4_sorted1[h5],h_su_4_sorted1[h6]]])
                                            demand_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([d_su_4_sorted1[d1:d1+6],[d_su_4_sorted1[h1],d_su_4_sorted1[h2],d_su_4_sorted1[h3],d_su_4_sorted1[h4],d_su_4_sorted1[h5],d_su_4_sorted1[h6]]])
                                            solar_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = s_su_4_sorted
                                            wind_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = w_su_4_sorted
                                            hydro_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = h_su_4_sorted
                                            demand_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = d_su_4_sorted 
                                    
                                        if sum4 != 0 and sum4 < a_minimum[0]:
                                            a_minimum = [sum4,w,d1,h1,h2,h3,h4,h5,h6]
                                            solar_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([s_a_4_sorted1[d1:d1+6],[s_a_4_sorted1[h1],s_a_4_sorted1[h2],s_a_4_sorted1[h3],s_a_4_sorted1[h4],s_a_4_sorted1[h5],s_a_4_sorted1[h6]]])
                                            wind_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([w_a_4_sorted1[d1:d1+6],[w_a_4_sorted1[h1],w_a_4_sorted1[h2],w_a_4_sorted1[h3],w_a_4_sorted1[h4],w_a_4_sorted1[h5],w_a_4_sorted1[h6]]])
                                            hydro_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([h_a_4_sorted1[d1:d1+6],[h_a_4_sorted1[h1],h_a_4_sorted1[h2],h_a_4_sorted1[h3],h_a_4_sorted1[h4],h_a_4_sorted1[h5],h_a_4_sorted1[h6]]])
                                            demand_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([d_a_4_sorted1[d1:d1+6],[d_a_4_sorted1[h1],d_a_4_sorted1[h2],d_a_4_sorted1[h3],d_a_4_sorted1[h4],d_a_4_sorted1[h5],d_a_4_sorted1[h6]]])
                                            solar_results_sorted_seasonal[3*2*hourly_ts_day:ts] = s_a_4_sorted
                                            wind_results_sorted_seasonal[3*2*hourly_ts_day:ts] = w_a_4_sorted
                                            hydro_results_sorted_seasonal[3*2*hourly_ts_day:ts] = h_a_4_sorted
                                            demand_results_sorted_seasonal[3*2*hourly_ts_day:ts] = d_a_4_sorted                             
        
                                        h6 = h6 + 1
                                        while h6 in list_of_days:
                                            h6 = h6 + 1
                                     h5 = h5 + 1
                                     while h5 in list_of_days:
                                        h5 = h5 + 1                                     
                                h4 = h4 + 1
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
                d1 = d1 + mid_night
                print('r ' + regions_or_countries[region] + ' - w '+ str(w) + ' - d '+ str(d1))





            if hourly_ts_day == 4:
             while d1 < 4*7-4: #28
                list_of_days = []
                list_of_days.append(d1)
                list_of_days.append(d1+1)
                list_of_days.append(d1+2)
                list_of_days.append(d1+3)
                if d1 == 0:
                    h1 = 4
                else:
        
                    h1 = 0
                while h1 <  4*7-4-1: #27
                    list_of_days.append(h1)
                    if d1 == 0:
                        h2 = 4+1
                    elif d1 == 1:
                        h2 = 4+1
                    else:
                        h2 = 1
                    while h2 < 4*7-4-2: #26
                        list_of_days.append(h2)
                        if d1 == 0:
                            h3 = 4+2
                        elif d1 == 1:
                            h3 = 4+2
                        elif d1 == 2:
                            h3 = 4+2
                        else:
                            h3 = 2
                        while h3 < 4*7-4-3: #26
                            list_of_days.append(h3)
                            if d1 == 0:
                                h4 = 4+3
                            elif d1 == 1:
                                h4 = 4+3
                            elif d1 == 2:
                                h4 = 4+3
                            elif d1 == 3:
                                h4 = 4+3
                            else:
                                h4 = 3    
                                    
                            while h4 < 4*7-4-4:
                                        list_of_days.append(h4)
                               
                                        s_w_4_sorted  = np.sort(np.concatenate([s_w_4_sorted1[d1:d1+4],[s_w_4_sorted1[h1],s_w_4_sorted1[h2],s_w_4_sorted1[h3],s_w_4_sorted1[h4]]]))[::-1]
                                        s_sp_4_sorted = np.sort(np.concatenate([s_sp_4_sorted1[d1:d1+4],[s_sp_4_sorted1[h1],s_sp_4_sorted1[h2],s_sp_4_sorted1[h3],s_sp_4_sorted1[h4]]]))[::-1]
                                        s_su_4_sorted = np.sort(np.concatenate([s_su_4_sorted1[d1:d1+4],[s_su_4_sorted1[h1],s_su_4_sorted1[h2],s_su_4_sorted1[h3],s_su_4_sorted1[h4]]]))[::-1]
                                        s_a_4_sorted  = np.sort(np.concatenate([s_a_4_sorted1[d1:d1+4],[s_a_4_sorted1[h1],s_a_4_sorted1[h2],s_a_4_sorted1[h3],s_a_4_sorted1[h4]]]))[::-1]
                
                                        w_w_4_sorted  = np.sort(np.concatenate([w_w_4_sorted1[d1:d1+4],[w_w_4_sorted1[h1],w_w_4_sorted1[h2],w_w_4_sorted1[h3],w_w_4_sorted1[h4]]]))[::-1]
                                        w_sp_4_sorted = np.sort(np.concatenate([w_sp_4_sorted1[d1:d1+4],[w_sp_4_sorted1[h1],w_sp_4_sorted1[h2],w_sp_4_sorted1[h3],w_sp_4_sorted1[h4]]]))[::-1]
                                        w_su_4_sorted = np.sort(np.concatenate([w_su_4_sorted1[d1:d1+4],[w_su_4_sorted1[h1],w_su_4_sorted1[h2],w_su_4_sorted1[h3],w_su_4_sorted1[h4]]]))[::-1]
                                        w_a_4_sorted  = np.sort(np.concatenate([w_a_4_sorted1[d1:d1+4],[w_a_4_sorted1[h1],w_a_4_sorted1[h2],w_a_4_sorted1[h3],w_a_4_sorted1[h4]]]))[::-1]
        
                                        h_w_4_sorted  = np.sort(np.concatenate([h_w_4_sorted1[d1:d1+4],[h_w_4_sorted1[h1],h_w_4_sorted1[h2],h_w_4_sorted1[h3],h_w_4_sorted1[h4]]]))[::-1]
                                        h_sp_4_sorted = np.sort(np.concatenate([h_sp_4_sorted1[d1:d1+4],[h_sp_4_sorted1[h1],h_sp_4_sorted1[h2],h_sp_4_sorted1[h3],h_sp_4_sorted1[h4]]]))[::-1]
                                        h_su_4_sorted = np.sort(np.concatenate([h_su_4_sorted1[d1:d1+4],[h_su_4_sorted1[h1],h_su_4_sorted1[h2],h_su_4_sorted1[h3],h_su_4_sorted1[h4]]]))[::-1]
                                        h_a_4_sorted  = np.sort(np.concatenate([h_a_4_sorted1[d1:d1+4],[h_a_4_sorted1[h1],h_a_4_sorted1[h2],h_a_4_sorted1[h3],h_a_4_sorted1[h4]]]))[::-1]
                
                                        d_w_4_sorted  = np.sort(np.concatenate([d_w_4_sorted1[d1:d1+4],[d_w_4_sorted1[h1],d_w_4_sorted1[h2],d_w_4_sorted1[h3],d_w_4_sorted1[h4]]]))[::-1]
                                        d_sp_4_sorted = np.sort(np.concatenate([d_sp_4_sorted1[d1:d1+4],[d_sp_4_sorted1[h1],d_sp_4_sorted1[h2],d_sp_4_sorted1[h3],d_sp_4_sorted1[h4]]]))[::-1]
                                        d_su_4_sorted = np.sort(np.concatenate([d_su_4_sorted1[d1:d1+4],[d_su_4_sorted1[h1],d_su_4_sorted1[h2],d_su_4_sorted1[h3],d_su_4_sorted1[h4]]]))[::-1]
                                        d_a_4_sorted  = np.sort(np.concatenate([d_a_4_sorted1[d1:d1+4],[d_a_4_sorted1[h1],d_a_4_sorted1[h2],d_a_4_sorted1[h3],d_a_4_sorted1[h4]]]))[::-1]
                                
                                        x2 = int(2190/2/hourly_ts_day)
                                        sum1 = 0
                                        sum2 = 0    
                                        sum3 = 0
                                        sum4 = 0
                                        while x2 < 2190 - int(2190/2/hourly_ts_day):
                                            sum1 = sum1 + ((solar_load_curve_Wi[x2] - s_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *solarweight        
                                            sum2 = sum2 + ((solar_load_curve_Sp[x2] - s_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*solarweight
                                            sum3 = sum3 + ((solar_load_curve_Su[x2] - s_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*solarweight
                                            sum4 = sum4 + ((solar_load_curve_Au[x2] - s_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *solarweight
                            
                                            sum1 = sum1 + ((wind_load_curve_Wi[x2] - w_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *windweight
                                            sum2 = sum2 + ((wind_load_curve_Sp[x2] - w_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*windweight
                                            sum3 = sum3 + ((wind_load_curve_Su[x2] - w_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*windweight
                                            sum4 = sum4 + ((wind_load_curve_Au[x2] - w_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *windweight
        
                                            sum1 = sum1 + ((hydro_load_curve_Wi[x2] - h_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *hydroweight # Hydropower is not well represented in the model, so we reduce the impact of hydropower on the final results.       
                                            sum2 = sum2 + ((hydro_load_curve_Sp[x2] - h_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*hydroweight 
                                            sum3 = sum3 + ((hydro_load_curve_Su[x2] - h_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*hydroweight 
                                            sum4 = sum4 + ((hydro_load_curve_Au[x2] - h_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *hydroweight
                        
                                            sum1 = sum1 + ((demand_load_curve_Wi[x2] - d_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *demandweight        
                                            sum2 = sum2 + ((demand_load_curve_Sp[x2] - d_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*demandweight
                                            sum3 = sum3 + ((demand_load_curve_Su[x2] - d_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*demandweight
                                            sum4 = sum4 + ((demand_load_curve_Au[x2] - d_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *demandweight
                                            x2 = x2 + 1
                                
                                        if sum1 != 0 and sum1 < w_minimum[0]:
                                            w_minimum = [sum1,w,d1,h1,h2,h3,h4]
                                            solar_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([s_w_4_sorted1[d1:d1+4],[s_w_4_sorted1[h1],s_w_4_sorted1[h2],s_w_4_sorted1[h3],s_w_4_sorted1[h4]]])
                                            wind_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([w_w_4_sorted1[d1:d1+4],[w_w_4_sorted1[h1],w_w_4_sorted1[h2],w_w_4_sorted1[h3],w_w_4_sorted1[h4]]])
                                            hydro_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([h_w_4_sorted1[d1:d1+4],[h_w_4_sorted1[h1],h_w_4_sorted1[h2],h_w_4_sorted1[h3],h_w_4_sorted1[h4]]])
                                            demand_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([d_w_4_sorted1[d1:d1+4],[d_w_4_sorted1[h1],d_w_4_sorted1[h2],d_w_4_sorted1[h3],d_w_4_sorted1[h4]]])
                                            solar_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = s_w_4_sorted
                                            wind_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = w_w_4_sorted
                                            hydro_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = h_w_4_sorted
                                            demand_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = d_w_4_sorted                        
                                    
                                        if sum2 != 0 and sum2 < sp_minimum[0]:
                                            sp_minimum = [sum2,w,d1,h1,h2,h3,h4]
                                            solar_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([s_sp_4_sorted1[d1:d1+4],[s_sp_4_sorted1[h1],s_sp_4_sorted1[h2],s_sp_4_sorted1[h3],s_sp_4_sorted1[h4]]])
                                            wind_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([w_sp_4_sorted1[d1:d1+4],[w_sp_4_sorted1[h1],w_sp_4_sorted1[h2],w_sp_4_sorted1[h3],w_sp_4_sorted1[h4]]])
                                            hydro_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([h_sp_4_sorted1[d1:d1+4],[h_sp_4_sorted1[h1],h_sp_4_sorted1[h2],h_sp_4_sorted1[h3],h_sp_4_sorted1[h4]]])
                                            demand_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([d_sp_4_sorted1[d1:d1+4],[d_sp_4_sorted1[h1],d_sp_4_sorted1[h2],d_sp_4_sorted1[h3],d_sp_4_sorted1[h4]]])
                                            solar_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = s_sp_4_sorted
                                            hydro_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = h_sp_4_sorted
                                            wind_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = w_sp_4_sorted
                                            demand_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = d_sp_4_sorted 
                                    
                                        if sum3 != 0 and sum3 < su_minimum[0]:
                                            su_minimum = [sum3,w,d1,h1,h2,h3,h4]
                                            solar_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([s_su_4_sorted1[d1:d1+4],[s_su_4_sorted1[h1],s_su_4_sorted1[h2],s_su_4_sorted1[h3],s_su_4_sorted1[h4]]])
                                            wind_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([w_su_4_sorted1[d1:d1+4],[w_su_4_sorted1[h1],w_su_4_sorted1[h2],w_su_4_sorted1[h3],w_su_4_sorted1[h4]]])
                                            hydro_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([h_su_4_sorted1[d1:d1+4],[h_su_4_sorted1[h1],h_su_4_sorted1[h2],h_su_4_sorted1[h3],h_su_4_sorted1[h4]]])
                                            demand_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([d_su_4_sorted1[d1:d1+4],[d_su_4_sorted1[h1],d_su_4_sorted1[h2],d_su_4_sorted1[h3],d_su_4_sorted1[h4]]])
                                            solar_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = s_su_4_sorted
                                            wind_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = w_su_4_sorted
                                            hydro_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = h_su_4_sorted
                                            demand_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = d_su_4_sorted 
                                    
                                        if sum4 != 0 and sum4 < a_minimum[0]:
                                            a_minimum = [sum4,w,d1,h1,h2,h3,h4]
                                            solar_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([s_a_4_sorted1[d1:d1+4],[s_a_4_sorted1[h1],s_a_4_sorted1[h2],s_a_4_sorted1[h3],s_a_4_sorted1[h4]]])
                                            wind_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([w_a_4_sorted1[d1:d1+4],[w_a_4_sorted1[h1],w_a_4_sorted1[h2],w_a_4_sorted1[h3],w_a_4_sorted1[h4]]])
                                            hydro_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([h_a_4_sorted1[d1:d1+4],[h_a_4_sorted1[h1],h_a_4_sorted1[h2],h_a_4_sorted1[h3],h_a_4_sorted1[h4],]])
                                            demand_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([d_a_4_sorted1[d1:d1+4],[d_a_4_sorted1[h1],d_a_4_sorted1[h2],d_a_4_sorted1[h3],d_a_4_sorted1[h4]]])
                                            solar_results_sorted_seasonal[3*2*hourly_ts_day:ts] = s_a_4_sorted
                                            wind_results_sorted_seasonal[3*2*hourly_ts_day:ts] = w_a_4_sorted
                                            hydro_results_sorted_seasonal[3*2*hourly_ts_day:ts] = h_a_4_sorted
                                            demand_results_sorted_seasonal[3*2*hourly_ts_day:ts] = d_a_4_sorted                             
        
                             
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
                d1 = d1 + mid_night
                print('r ' + regions_or_countries[region] + ' - w '+ str(w) + ' - d '+ str(d1))






            if hourly_ts_day == 3:
             while d1 < 3*7-3: #28
                list_of_days = []
                list_of_days.append(d1)
                list_of_days.append(d1+1)
                list_of_days.append(d1+2)
                if d1 == 0:
                    h1 = 3
                else:
        
                    h1 = 0
                while h1 <  3*7-3-1: #27
                    list_of_days.append(h1)
                    if d1 == 0:
                        h2 = 3+1
                    elif d1 == 1:
                        h2 = 3+1
                    else:
                        h2 = 1
                    while h2 < 3*7-3-2: #26
                        list_of_days.append(h2)
                        if d1 == 0:
                            h3 = 3+2
                        elif d1 == 1:
                            h3 = 3+2
                        elif d1 == 2:
                            h3 = 3+2
                        else:
                            h3 = 2
                        while h3 < 3*7-3-3: #26
                                        list_of_days.append(h3)
         
                                        s_w_4_sorted  = np.sort(np.concatenate([s_w_4_sorted1[d1:d1+3],[s_w_4_sorted1[h1],s_w_4_sorted1[h2],s_w_4_sorted1[h3]]]))[::-1]
                                        s_sp_4_sorted = np.sort(np.concatenate([s_sp_4_sorted1[d1:d1+3],[s_sp_4_sorted1[h1],s_sp_4_sorted1[h2],s_sp_4_sorted1[h3]]]))[::-1]
                                        s_su_4_sorted = np.sort(np.concatenate([s_su_4_sorted1[d1:d1+3],[s_su_4_sorted1[h1],s_su_4_sorted1[h2],s_su_4_sorted1[h3]]]))[::-1]
                                        s_a_4_sorted  = np.sort(np.concatenate([s_a_4_sorted1[d1:d1+3],[s_a_4_sorted1[h1],s_a_4_sorted1[h2],s_a_4_sorted1[h3]]]))[::-1]
                
                                        w_w_4_sorted  = np.sort(np.concatenate([w_w_4_sorted1[d1:d1+3],[w_w_4_sorted1[h1],w_w_4_sorted1[h2],w_w_4_sorted1[h3]]]))[::-1]
                                        w_sp_4_sorted = np.sort(np.concatenate([w_sp_4_sorted1[d1:d1+3],[w_sp_4_sorted1[h1],w_sp_4_sorted1[h2],w_sp_4_sorted1[h3]]]))[::-1]
                                        w_su_4_sorted = np.sort(np.concatenate([w_su_4_sorted1[d1:d1+3],[w_su_4_sorted1[h1],w_su_4_sorted1[h2],w_su_4_sorted1[h3]]]))[::-1]
                                        w_a_4_sorted  = np.sort(np.concatenate([w_a_4_sorted1[d1:d1+3],[w_a_4_sorted1[h1],w_a_4_sorted1[h2],w_a_4_sorted1[h3]]]))[::-1]
        
                                        h_w_4_sorted  = np.sort(np.concatenate([h_w_4_sorted1[d1:d1+3],[h_w_4_sorted1[h1],h_w_4_sorted1[h2],h_w_4_sorted1[h3]]]))[::-1]
                                        h_sp_4_sorted = np.sort(np.concatenate([h_sp_4_sorted1[d1:d1+3],[h_sp_4_sorted1[h1],h_sp_4_sorted1[h2],h_sp_4_sorted1[h3]]]))[::-1]
                                        h_su_4_sorted = np.sort(np.concatenate([h_su_4_sorted1[d1:d1+3],[h_su_4_sorted1[h1],h_su_4_sorted1[h2],h_su_4_sorted1[h3]]]))[::-1]
                                        h_a_4_sorted  = np.sort(np.concatenate([h_a_4_sorted1[d1:d1+3],[h_a_4_sorted1[h1],h_a_4_sorted1[h2],h_a_4_sorted1[h3]]]))[::-1]
                
                                        d_w_4_sorted  = np.sort(np.concatenate([d_w_4_sorted1[d1:d1+3],[d_w_4_sorted1[h1],d_w_4_sorted1[h2],d_w_4_sorted1[h3]]]))[::-1]
                                        d_sp_4_sorted = np.sort(np.concatenate([d_sp_4_sorted1[d1:d1+3],[d_sp_4_sorted1[h1],d_sp_4_sorted1[h2],d_sp_4_sorted1[h3]]]))[::-1]
                                        d_su_4_sorted = np.sort(np.concatenate([d_su_4_sorted1[d1:d1+3],[d_su_4_sorted1[h1],d_su_4_sorted1[h2],d_su_4_sorted1[h3]]]))[::-1]
                                        d_a_4_sorted  = np.sort(np.concatenate([d_a_4_sorted1[d1:d1+3],[d_a_4_sorted1[h1],d_a_4_sorted1[h2],d_a_4_sorted1[h3]]]))[::-1]
                                
                                        x2 = int(2190/2/hourly_ts_day)
                                        sum1 = 0
                                        sum2 = 0    
                                        sum3 = 0
                                        sum4 = 0
                                        while x2 < 2190 - int(2190/2/hourly_ts_day):
                                            sum1 = sum1 + ((solar_load_curve_Wi[x2] - s_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *solarweight    
                                            sum2 = sum2 + ((solar_load_curve_Sp[x2] - s_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*solarweight
                                            sum3 = sum3 + ((solar_load_curve_Su[x2] - s_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*solarweight
                                            sum4 = sum4 + ((solar_load_curve_Au[x2] - s_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *solarweight
                            
                                            sum1 = sum1 + ((wind_load_curve_Wi[x2] - w_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *windweight
                                            sum2 = sum2 + ((wind_load_curve_Sp[x2] - w_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*windweight
                                            sum3 = sum3 + ((wind_load_curve_Su[x2] - w_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*windweight
                                            sum4 = sum4 + ((wind_load_curve_Au[x2] - w_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *windweight
        
                                            sum1 = sum1 + ((hydro_load_curve_Wi[x2] - h_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *hydroweight # Hydropower is not well represented in the model, so we reduce the impact of hydropower on the final results.       
                                            sum2 = sum2 + ((hydro_load_curve_Sp[x2] - h_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*hydroweight  
                                            sum3 = sum3 + ((hydro_load_curve_Su[x2] - h_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*hydroweight 
                                            sum4 = sum4 + ((hydro_load_curve_Au[x2] - h_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *hydroweight
                        
                                            sum1 = sum1 + ((demand_load_curve_Wi[x2] - d_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *demandweight  
                                            sum2 = sum2 + ((demand_load_curve_Sp[x2] - d_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*demandweight  
                                            sum3 = sum3 + ((demand_load_curve_Su[x2] - d_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*demandweight  
                                            sum4 = sum4 + ((demand_load_curve_Au[x2] - d_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *demandweight  
                                            x2 = x2 + 1
                                
                                        if sum1 != 0 and sum1 < w_minimum[0]:
                                            w_minimum = [sum1,w,d1,h1,h2,h3]
                                            solar_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([s_w_4_sorted1[d1:d1+3],[s_w_4_sorted1[h1],s_w_4_sorted1[h2],s_w_4_sorted1[h3]]])
                                            wind_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([w_w_4_sorted1[d1:d1+3],[w_w_4_sorted1[h1],w_w_4_sorted1[h2],w_w_4_sorted1[h3]]])
                                            hydro_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([h_w_4_sorted1[d1:d1+3],[h_w_4_sorted1[h1],h_w_4_sorted1[h2],h_w_4_sorted1[h3]]])
                                            demand_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([d_w_4_sorted1[d1:d1+3],[d_w_4_sorted1[h1],d_w_4_sorted1[h2],d_w_4_sorted1[h3]]])
                                            solar_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = s_w_4_sorted
                                            wind_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = w_w_4_sorted
                                            hydro_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = h_w_4_sorted
                                            demand_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = d_w_4_sorted                        
                                    
                                        if sum2 != 0 and sum2 < sp_minimum[0]:
                                            sp_minimum = [sum2,w,d1,h1,h2,h3]
                                            solar_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([s_sp_4_sorted1[d1:d1+3],[s_sp_4_sorted1[h1],s_sp_4_sorted1[h2],s_sp_4_sorted1[h3]]])
                                            wind_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([w_sp_4_sorted1[d1:d1+3],[w_sp_4_sorted1[h1],w_sp_4_sorted1[h2],w_sp_4_sorted1[h3]]])
                                            hydro_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([h_sp_4_sorted1[d1:d1+3],[h_sp_4_sorted1[h1],h_sp_4_sorted1[h2],h_sp_4_sorted1[h3]]])
                                            demand_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([d_sp_4_sorted1[d1:d1+3],[d_sp_4_sorted1[h1],d_sp_4_sorted1[h2],d_sp_4_sorted1[h3]]])
                                            solar_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = s_sp_4_sorted
                                            hydro_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = h_sp_4_sorted
                                            wind_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = w_sp_4_sorted
                                            demand_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = d_sp_4_sorted 
                                    
                                        if sum3 != 0 and sum3 < su_minimum[0]:
                                            su_minimum = [sum3,w,d1,h1,h2,h3]
                                            solar_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([s_su_4_sorted1[d1:d1+3],[s_su_4_sorted1[h1],s_su_4_sorted1[h2],s_su_4_sorted1[h3]]])
                                            wind_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([w_su_4_sorted1[d1:d1+3],[w_su_4_sorted1[h1],w_su_4_sorted1[h2],w_su_4_sorted1[h3]]])
                                            hydro_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([h_su_4_sorted1[d1:d1+3],[h_su_4_sorted1[h1],h_su_4_sorted1[h2],h_su_4_sorted1[h3]]])
                                            demand_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([d_su_4_sorted1[d1:d1+3],[d_su_4_sorted1[h1],d_su_4_sorted1[h2],d_su_4_sorted1[h3]]])
                                            solar_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = s_su_4_sorted
                                            wind_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = w_su_4_sorted
                                            hydro_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = h_su_4_sorted
                                            demand_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = d_su_4_sorted 
                                    
                                        if sum4 != 0 and sum4 < a_minimum[0]:
                                            a_minimum = [sum4,w,d1,h1,h2,h3]
                                            solar_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([s_a_4_sorted1[d1:d1+3],[s_a_4_sorted1[h1],s_a_4_sorted1[h2],s_a_4_sorted1[h3]]])
                                            wind_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([w_a_4_sorted1[d1:d1+3],[w_a_4_sorted1[h1],w_a_4_sorted1[h2],w_a_4_sorted1[h3]]])
                                            hydro_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([h_a_4_sorted1[d1:d1+3],[h_a_4_sorted1[h1],h_a_4_sorted1[h2],h_a_4_sorted1[h3]]])
                                            demand_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([d_a_4_sorted1[d1:d1+3],[d_a_4_sorted1[h1],d_a_4_sorted1[h2],d_a_4_sorted1[h3]]])
                                            solar_results_sorted_seasonal[3*2*hourly_ts_day:ts] = s_a_4_sorted
                                            wind_results_sorted_seasonal[3*2*hourly_ts_day:ts] = w_a_4_sorted
                                            hydro_results_sorted_seasonal[3*2*hourly_ts_day:ts] = h_a_4_sorted
                                            demand_results_sorted_seasonal[3*2*hourly_ts_day:ts] = d_a_4_sorted                             
        
                                        h3 = h3 + 2
                                        while h3 in list_of_days:
                                            h3 = h3 + 1                       
                        h2 = h2 + 1
                        while h2 in list_of_days:
                            h2 = h2 + 1
                    h1 = h1 + 1
                    while h1 in list_of_days:
                        h1 = h1 + 1
                d1 = d1 + mid_night
                print('r ' + regions_or_countries[region] + ' - w '+ str(w) + ' - d '+ str(d1))












            if hourly_ts_day == 2:
             while d1 < 2*7-2: #28
                list_of_days = []
                list_of_days.append(d1)
                list_of_days.append(d1+1)
                if d1 == 0:
                    h1 = 2
                else:
        
                    h1 = 0
                while h1 <  2*7-2-1: #27
                    list_of_days.append(h1)
                    if d1 == 0:
                        h2 = 2+1
                    elif d1 == 1:
                        h2 = 2+1
                    else:
                        h2 = 1
                    while h2 < 2*7-2-2: #26
                                        list_of_days.append(h2)
         
                                        s_w_4_sorted  = np.sort(np.concatenate([s_w_4_sorted1[d1:d1+2],[s_w_4_sorted1[h1],s_w_4_sorted1[h2]]]))[::-1]
                                        s_sp_4_sorted = np.sort(np.concatenate([s_sp_4_sorted1[d1:d1+2],[s_sp_4_sorted1[h1],s_sp_4_sorted1[h2]]]))[::-1]
                                        s_su_4_sorted = np.sort(np.concatenate([s_su_4_sorted1[d1:d1+2],[s_su_4_sorted1[h1],s_su_4_sorted1[h2]]]))[::-1]
                                        s_a_4_sorted  = np.sort(np.concatenate([s_a_4_sorted1[d1:d1+2],[s_a_4_sorted1[h1],s_a_4_sorted1[h2]]]))[::-1]
                
                                        w_w_4_sorted  = np.sort(np.concatenate([w_w_4_sorted1[d1:d1+2],[w_w_4_sorted1[h1],w_w_4_sorted1[h2]]]))[::-1]
                                        w_sp_4_sorted = np.sort(np.concatenate([w_sp_4_sorted1[d1:d1+2],[w_sp_4_sorted1[h1],w_sp_4_sorted1[h2]]]))[::-1]
                                        w_su_4_sorted = np.sort(np.concatenate([w_su_4_sorted1[d1:d1+2],[w_su_4_sorted1[h1],w_su_4_sorted1[h2]]]))[::-1]
                                        w_a_4_sorted  = np.sort(np.concatenate([w_a_4_sorted1[d1:d1+2],[w_a_4_sorted1[h1],w_a_4_sorted1[h2]]]))[::-1]
        
                                        h_w_4_sorted  = np.sort(np.concatenate([h_w_4_sorted1[d1:d1+2],[h_w_4_sorted1[h1],h_w_4_sorted1[h2]]]))[::-1]
                                        h_sp_4_sorted = np.sort(np.concatenate([h_sp_4_sorted1[d1:d1+2],[h_sp_4_sorted1[h1],h_sp_4_sorted1[h2]]]))[::-1]
                                        h_su_4_sorted = np.sort(np.concatenate([h_su_4_sorted1[d1:d1+2],[h_su_4_sorted1[h1],h_su_4_sorted1[h2]]]))[::-1]
                                        h_a_4_sorted  = np.sort(np.concatenate([h_a_4_sorted1[d1:d1+2],[h_a_4_sorted1[h1],h_a_4_sorted1[h2]]]))[::-1]
                
                                        d_w_4_sorted  = np.sort(np.concatenate([d_w_4_sorted1[d1:d1+2],[d_w_4_sorted1[h1],d_w_4_sorted1[h2]]]))[::-1]
                                        d_sp_4_sorted = np.sort(np.concatenate([d_sp_4_sorted1[d1:d1+2],[d_sp_4_sorted1[h1],d_sp_4_sorted1[h2]]]))[::-1]
                                        d_su_4_sorted = np.sort(np.concatenate([d_su_4_sorted1[d1:d1+2],[d_su_4_sorted1[h1],d_su_4_sorted1[h2]]]))[::-1]
                                        d_a_4_sorted  = np.sort(np.concatenate([d_a_4_sorted1[d1:d1+2],[d_a_4_sorted1[h1],d_a_4_sorted1[h2]]]))[::-1]
                                
                                        x2 = 0#int(2190/2/hourly_ts_day)
                                        sum1 = 0
                                        sum2 = 0    
                                        sum3 = 0
                                        sum4 = 0
                                        while x2 < 2190 - int(2190/2/hourly_ts_day):
                                            sum1 = sum1 + ((solar_load_curve_Wi[x2] - s_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *solarweight    
                                            sum2 = sum2 + ((solar_load_curve_Sp[x2] - s_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*solarweight
                                            sum3 = sum3 + ((solar_load_curve_Su[x2] - s_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*solarweight
                                            sum4 = sum4 + ((solar_load_curve_Au[x2] - s_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *solarweight
                            
                                            sum1 = sum1 + ((wind_load_curve_Wi[x2] - w_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *windweight 
                                            sum2 = sum2 + ((wind_load_curve_Sp[x2] - w_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*windweight 
                                            sum3 = sum3 + ((wind_load_curve_Su[x2] - w_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*windweight 
                                            sum4 = sum4 + ((wind_load_curve_Au[x2] - w_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *windweight 
        
                                            sum1 = sum1 + ((hydro_load_curve_Wi[x2] - h_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *hydroweight  # Hydropower is not well represented in the model, so we reduce the impact of hydropower on the final results.       
                                            sum2 = sum2 + ((hydro_load_curve_Sp[x2] - h_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*hydroweight 
                                            sum3 = sum3 + ((hydro_load_curve_Su[x2] - h_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*hydroweight 
                                            sum4 = sum4 + ((hydro_load_curve_Au[x2] - h_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *hydroweight 
                        
                                            sum1 = sum1 + ((demand_load_curve_Wi[x2] - d_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *demandweight 
                                            sum2 = sum2 + ((demand_load_curve_Sp[x2] - d_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*demandweight 
                                            sum3 = sum3 + ((demand_load_curve_Su[x2] - d_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*demandweight 
                                            sum4 = sum4 + ((demand_load_curve_Au[x2] - d_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *demandweight 
                                            x2 = x2 + 1
                                
                                        if sum1 != 0 and sum1 < w_minimum[0]:
                                            w_minimum = [sum1,w,d1,h1,h2]
                                            solar_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([s_w_4_sorted1[d1:d1+2],[s_w_4_sorted1[h1],s_w_4_sorted1[h2]]])
                                            wind_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([w_w_4_sorted1[d1:d1+2],[w_w_4_sorted1[h1],w_w_4_sorted1[h2]]])
                                            hydro_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([h_w_4_sorted1[d1:d1+2],[h_w_4_sorted1[h1],h_w_4_sorted1[h2]]])
                                            demand_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([d_w_4_sorted1[d1:d1+2],[d_w_4_sorted1[h1],d_w_4_sorted1[h2]]])
                                            solar_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = s_w_4_sorted
                                            wind_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = w_w_4_sorted
                                            hydro_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = h_w_4_sorted
                                            demand_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = d_w_4_sorted                        
                                    
                                        if sum2 != 0 and sum2 < sp_minimum[0]:
                                            sp_minimum = [sum2,w,d1,h1,h2]
                                            solar_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([s_sp_4_sorted1[d1:d1+2],[s_sp_4_sorted1[h1],s_sp_4_sorted1[h2]]])
                                            wind_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([w_sp_4_sorted1[d1:d1+2],[w_sp_4_sorted1[h1],w_sp_4_sorted1[h2]]])
                                            hydro_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([h_sp_4_sorted1[d1:d1+2],[h_sp_4_sorted1[h1],h_sp_4_sorted1[h2]]])
                                            demand_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([d_sp_4_sorted1[d1:d1+2],[d_sp_4_sorted1[h1],d_sp_4_sorted1[h2]]])
                                            solar_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = s_sp_4_sorted
                                            hydro_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = h_sp_4_sorted
                                            wind_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = w_sp_4_sorted
                                            demand_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = d_sp_4_sorted 
                                    
                                        if sum3 != 0 and sum3 < su_minimum[0]:
                                            su_minimum = [sum3,w,d1,h1,h2]
                                            solar_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([s_su_4_sorted1[d1:d1+2],[s_su_4_sorted1[h1],s_su_4_sorted1[h2]]])
                                            wind_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([w_su_4_sorted1[d1:d1+2],[w_su_4_sorted1[h1],w_su_4_sorted1[h2]]])
                                            hydro_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([h_su_4_sorted1[d1:d1+2],[h_su_4_sorted1[h1],h_su_4_sorted1[h2]]])
                                            demand_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([d_su_4_sorted1[d1:d1+2],[d_su_4_sorted1[h1],d_su_4_sorted1[h2]]])
                                            solar_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = s_su_4_sorted
                                            wind_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = w_su_4_sorted
                                            hydro_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = h_su_4_sorted
                                            demand_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = d_su_4_sorted 
                                    
                                        if sum4 != 0 and sum4 < a_minimum[0]:
                                            a_minimum = [sum4,w,d1,h1,h2]
                                            solar_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([s_a_4_sorted1[d1:d1+2],[s_a_4_sorted1[h1],s_a_4_sorted1[h2]]])
                                            wind_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([w_a_4_sorted1[d1:d1+2],[w_a_4_sorted1[h1],w_a_4_sorted1[h2]]])
                                            hydro_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([h_a_4_sorted1[d1:d1+2],[h_a_4_sorted1[h1],h_a_4_sorted1[h2]]])
                                            demand_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([d_a_4_sorted1[d1:d1+2],[d_a_4_sorted1[h1],d_a_4_sorted1[h2]]])
                                            solar_results_sorted_seasonal[3*2*hourly_ts_day:ts] = s_a_4_sorted
                                            wind_results_sorted_seasonal[3*2*hourly_ts_day:ts] = w_a_4_sorted
                                            hydro_results_sorted_seasonal[3*2*hourly_ts_day:ts] = h_a_4_sorted
                                            demand_results_sorted_seasonal[3*2*hourly_ts_day:ts] = d_a_4_sorted                             
               
                                        h2 = h2 + 1
                                        while h2 in list_of_days:
                                            h2 = h2 + 1
                    h1 = h1 + 1
                    while h1 in list_of_days:
                        h1 = h1 + 1
                d1 = d1 + mid_night
                print('r ' + regions_or_countries[region] + ' - w '+ str(w) + ' - d '+ str(d1))







            if hourly_ts_day == 1:
             while d1 < 1*7-1: #28
                list_of_days = []
                list_of_days.append(d1)
                if d1 == 0:
                    h1 = 1
                else:
        
                    h1 = 0
                while h1 <  1*7-1-1: #27
                                        list_of_days.append(h1)
         
                                        s_w_4_sorted  = np.sort(np.concatenate([s_w_4_sorted1[d1:d1+1],[s_w_4_sorted1[h1]]]))[::-1]
                                        s_sp_4_sorted = np.sort(np.concatenate([s_sp_4_sorted1[d1:d1+1],[s_sp_4_sorted1[h1]]]))[::-1]
                                        s_su_4_sorted = np.sort(np.concatenate([s_su_4_sorted1[d1:d1+1],[s_su_4_sorted1[h1]]]))[::-1]
                                        s_a_4_sorted  = np.sort(np.concatenate([s_a_4_sorted1[d1:d1+1],[s_a_4_sorted1[h1]]]))[::-1]
                
                                        w_w_4_sorted  = np.sort(np.concatenate([w_w_4_sorted1[d1:d1+1],[w_w_4_sorted1[h1]]]))[::-1]
                                        w_sp_4_sorted = np.sort(np.concatenate([w_sp_4_sorted1[d1:d1+1],[w_sp_4_sorted1[h1]]]))[::-1]
                                        w_su_4_sorted = np.sort(np.concatenate([w_su_4_sorted1[d1:d1+1],[w_su_4_sorted1[h1]]]))[::-1]
                                        w_a_4_sorted  = np.sort(np.concatenate([w_a_4_sorted1[d1:d1+1],[w_a_4_sorted1[h1]]]))[::-1]
        
                                        h_w_4_sorted  = np.sort(np.concatenate([h_w_4_sorted1[d1:d1+1],[h_w_4_sorted1[h1]]]))[::-1]
                                        h_sp_4_sorted = np.sort(np.concatenate([h_sp_4_sorted1[d1:d1+1],[h_sp_4_sorted1[h1]]]))[::-1]
                                        h_su_4_sorted = np.sort(np.concatenate([h_su_4_sorted1[d1:d1+1],[h_su_4_sorted1[h1]]]))[::-1]
                                        h_a_4_sorted  = np.sort(np.concatenate([h_a_4_sorted1[d1:d1+1],[h_a_4_sorted1[h1]]]))[::-1]
                
                                        d_w_4_sorted  = np.sort(np.concatenate([d_w_4_sorted1[d1:d1+1],[d_w_4_sorted1[h1]]]))[::-1]
                                        d_sp_4_sorted = np.sort(np.concatenate([d_sp_4_sorted1[d1:d1+1],[d_sp_4_sorted1[h1]]]))[::-1]
                                        d_su_4_sorted = np.sort(np.concatenate([d_su_4_sorted1[d1:d1+1],[d_su_4_sorted1[h1]]]))[::-1]
                                        d_a_4_sorted  = np.sort(np.concatenate([d_a_4_sorted1[d1:d1+1],[d_a_4_sorted1[h1]]]))[::-1]
                                
                                        x2 = 0#int(2190/2/hourly_ts_day)
                                        sum1 = 0
                                        sum2 = 0    
                                        sum3 = 0
                                        sum4 = 0
                                        while x2 < 2190 - int(2190/2/hourly_ts_day):
                                            sum1 = sum1 + ((solar_load_curve_Wi[x2] - s_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *solarweight    
                                            sum2 = sum2 + ((solar_load_curve_Sp[x2] - s_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*solarweight
                                            sum3 = sum3 + ((solar_load_curve_Su[x2] - s_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*solarweight
                                            sum4 = sum4 + ((solar_load_curve_Au[x2] - s_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *solarweight
                            
                                            sum1 = sum1 + ((wind_load_curve_Wi[x2] - w_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *windweight 
                                            sum2 = sum2 + ((wind_load_curve_Sp[x2] - w_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*windweight 
                                            sum3 = sum3 + ((wind_load_curve_Su[x2] - w_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*windweight 
                                            sum4 = sum4 + ((wind_load_curve_Au[x2] - w_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *windweight 
        
                                            sum1 = sum1 + ((hydro_load_curve_Wi[x2] - h_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *hydroweight # Hydropower is not well represented in the model, so we reduce the impact of hydropower on the final results.       
                                            sum2 = sum2 + ((hydro_load_curve_Sp[x2] - h_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*hydroweight 
                                            sum3 = sum3 + ((hydro_load_curve_Su[x2] - h_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*hydroweight 
                                            sum4 = sum4 + ((hydro_load_curve_Au[x2] - h_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *hydroweight
                        
                                            sum1 = sum1 + ((demand_load_curve_Wi[x2] - d_w_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *demandweight 
                                            sum2 = sum2 + ((demand_load_curve_Sp[x2] - d_sp_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*demandweight 
                                            sum3 = sum3 + ((demand_load_curve_Su[x2] - d_su_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2)*demandweight 
                                            sum4 = sum4 + ((demand_load_curve_Au[x2] - d_a_4_sorted[int(x2/_8760_per_ts_hours/2/hourly_ts_day)])**2) *demandweight 
                                            x2 = x2 + 1
                                
                                        if sum1 != 0 and sum1 < w_minimum[0]:
                                            w_minimum = [sum1,w,d1,h1]
                                            solar_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([s_w_4_sorted1[d1:d1+1],[s_w_4_sorted1[h1]]])
                                            wind_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([w_w_4_sorted1[d1:d1+1],[w_w_4_sorted1[h1]]])
                                            hydro_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([h_w_4_sorted1[d1:d1+1],[h_w_4_sorted1[h1]]])
                                            demand_results_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = np.concatenate([d_w_4_sorted1[d1:d1+1],[d_w_4_sorted1[h1]]])
                                            solar_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = s_w_4_sorted
                                            wind_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = w_w_4_sorted
                                            hydro_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = h_w_4_sorted
                                            demand_results_sorted_seasonal[0*2*hourly_ts_day:1*2*hourly_ts_day] = d_w_4_sorted                        
                                    
                                        if sum2 != 0 and sum2 < sp_minimum[0]:
                                            sp_minimum = [sum2,w,d1,h1]
                                            solar_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([s_sp_4_sorted1[d1:d1+1],[s_sp_4_sorted1[h1]]])
                                            wind_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([w_sp_4_sorted1[d1:d1+1],[w_sp_4_sorted1[h1]]])
                                            hydro_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([h_sp_4_sorted1[d1:d1+1],[h_sp_4_sorted1[h1]]])
                                            demand_results_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = np.concatenate([d_sp_4_sorted1[d1:d1+1],[d_sp_4_sorted1[h1]]])
                                            solar_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = s_sp_4_sorted
                                            hydro_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = h_sp_4_sorted
                                            wind_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = w_sp_4_sorted
                                            demand_results_sorted_seasonal[1*2*hourly_ts_day:2*2*hourly_ts_day] = d_sp_4_sorted 
                                    
                                        if sum3 != 0 and sum3 < su_minimum[0]:
                                            su_minimum = [sum3,w,d1,h1]
                                            solar_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([s_su_4_sorted1[d1:d1+1],[s_su_4_sorted1[h1]]])
                                            wind_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([w_su_4_sorted1[d1:d1+1],[w_su_4_sorted1[h1]]])
                                            hydro_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([h_su_4_sorted1[d1:d1+1],[h_su_4_sorted1[h1]]])
                                            demand_results_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = np.concatenate([d_su_4_sorted1[d1:d1+1],[d_su_4_sorted1[h1]]])
                                            solar_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = s_su_4_sorted
                                            wind_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = w_su_4_sorted
                                            hydro_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = h_su_4_sorted
                                            demand_results_sorted_seasonal[2*2*hourly_ts_day:3*2*hourly_ts_day] = d_su_4_sorted 
                                    
                                        if sum4 != 0 and sum4 < a_minimum[0]:
                                            a_minimum = [sum4,w,d1,h1]
                                            solar_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([s_a_4_sorted1[d1:d1+1],[s_a_4_sorted1[h1]]])
                                            wind_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([w_a_4_sorted1[d1:d1+1],[w_a_4_sorted1[h1]]])
                                            hydro_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([h_a_4_sorted1[d1:d1+1],[h_a_4_sorted1[h1]]])
                                            demand_results_seasonal[3*2*hourly_ts_day:ts] = np.concatenate([d_a_4_sorted1[d1:d1+1],[d_a_4_sorted1[h1]]])
                                            solar_results_sorted_seasonal[3*2*hourly_ts_day:ts] = s_a_4_sorted
                                            wind_results_sorted_seasonal[3*2*hourly_ts_day:ts] = w_a_4_sorted
                                            hydro_results_sorted_seasonal[3*2*hourly_ts_day:ts] = h_a_4_sorted
                                            demand_results_sorted_seasonal[3*2*hourly_ts_day:ts] = d_a_4_sorted                             

                                        h1 = h1 + 1
                                        while h1 in list_of_days:
                                            h1 = h1 + 1
                d1 = d1 + mid_night
                print('r ' + regions_or_countries[region] + ' - w '+ str(w) + ' - d '+ str(d1))





            w = w + 1
        
        solar_load_curve_seasonal =  np.zeros(shape=(8760))
        wind_load_curve_seasonal =  np.zeros(shape=(8760))
        hydro_load_curve_seasonal =  np.zeros(shape=(8760))
        demand_load_curve_seasonal =  np.zeros(shape=(8760))
        
        solar_load_curve_seasonal[0:2190] = solar_load_curve_Wi
        solar_load_curve_seasonal[2190:4380] = solar_load_curve_Sp
        solar_load_curve_seasonal[4380:6570] = solar_load_curve_Su
        solar_load_curve_seasonal[6570:8760] = solar_load_curve_Au
        wind_load_curve_seasonal[0:2190] = wind_load_curve_Wi
        wind_load_curve_seasonal[2190:4380] = wind_load_curve_Sp
        wind_load_curve_seasonal[4380:6570] = wind_load_curve_Su
        wind_load_curve_seasonal[6570:8760] = wind_load_curve_Au
        hydro_load_curve_seasonal[0:2190] = hydro_load_curve_Wi
        hydro_load_curve_seasonal[2190:4380] = hydro_load_curve_Sp
        hydro_load_curve_seasonal[4380:6570] = hydro_load_curve_Su
        hydro_load_curve_seasonal[6570:8760] = hydro_load_curve_Au
        demand_load_curve_seasonal[0:2190] = demand_load_curve_Wi
        demand_load_curve_seasonal[2190:4380] = demand_load_curve_Sp
        demand_load_curve_seasonal[4380:6570] = demand_load_curve_Su
        demand_load_curve_seasonal[6570:8760] = demand_load_curve_Au
    
        solar_results_annual = np.sort(solar_results_seasonal, axis=None)[::-1]
        wind_results_annual = np.sort(wind_results_seasonal, axis=None)[::-1]
        hydro_results_annual = np.sort(hydro_results_seasonal, axis=None)[::-1]
        demand_results_annual = np.sort(demand_results_seasonal, axis=None)[::-1]
        
        solar_results_sorted_annual = np.sort(solar_results_sorted_seasonal, axis=None)[::-1]
        wind_results_sorted_annual = np.sort(wind_results_sorted_seasonal, axis=None)[::-1]
        hydro_results_sorted_annual = np.sort(hydro_results_sorted_seasonal, axis=None)[::-1]
        demand_results_sorted_annual = np.sort(demand_results_sorted_seasonal, axis=None)[::-1]
        
        
        solar_and_wind_seasonal = np.vstack((solar_and_wind_seasonal,solar_results_seasonal,wind_results_seasonal,hydro_results_seasonal,demand_results_seasonal))
        solar_and_wind_sorter_seasonal = np.vstack((solar_and_wind_sorter_seasonal,solar_results_sorted_seasonal,wind_results_sorted_seasonal,hydro_results_sorted_seasonal,demand_results_sorted_seasonal)) 
        solar_and_wind_duration_curve_seasonal = np.vstack((solar_and_wind_duration_curve_seasonal,solar_load_curve_seasonal,wind_load_curve_seasonal,hydro_load_curve_seasonal,demand_load_curve_seasonal))
    
        solar_and_wind_annual = np.vstack((solar_and_wind_annual,solar_results_annual,wind_results_annual,hydro_results_annual,demand_results_annual))
        solar_and_wind_sorter_annual = np.vstack((solar_and_wind_sorter_annual,solar_results_sorted_annual,wind_results_sorted_annual,hydro_results_sorted_annual,demand_results_sorted_annual)) 
        solar_and_wind_duration_curve_annual = np.vstack((solar_and_wind_duration_curve_annual,solar_load_curve_annual,wind_load_curve_annual,hydro_load_curve_annual,demand_load_curve_annual))
        
        region = region + 1    
    
    # Save time slices
    panda = pd.DataFrame(solar_and_wind_seasonal.T)
    panda.to_excel(path+'Results/Time slices (seasonal) 4 seasons, 2 weekly, '+ str(hourly_ts_day) +' hours.xlsx')

    panda = pd.DataFrame(solar_and_wind_sorter_seasonal.T)
    panda.to_excel(path+'Results/Time slices sorted (seasonal) 4 seasons, 2 weekly, '+ str(hourly_ts_day) +' hours.xlsx')

    panda = pd.DataFrame(solar_and_wind_duration_curve_seasonal.T)
    panda.to_excel(path+'Results/Duration curve (seasonal) 4 seasons, 2 weekly, '+ str(hourly_ts_day) +' hours.xlsx')

    panda = pd.DataFrame(solar_and_wind_annual.T)
    panda.to_excel(path+'Results/Time slices (annual) 4 seasons, 2 weekly, '+ str(hourly_ts_day) +' hours.xlsx')

    panda = pd.DataFrame(solar_and_wind_sorter_annual.T)
    panda.to_excel(path+'Results/Time slices sorted (annual) 4 seasons, 2 weekly, '+ str(hourly_ts_day) +' hours.xlsx')

    panda = pd.DataFrame(solar_and_wind_duration_curve_annual.T)
    panda.to_excel(path+'Results/Duration curve (annual) 4 seasons, 2 weekly, '+ str(hourly_ts_day) +' hours.xlsx')
    
    
    # Plotting seasonal results
    x_axis = np.arange(1*2*hourly_ts_day+1)
    x2_axis = np.arange(2190+1)
    s_w_h_ds = ['Solar','Wind','Hydro','Demand']
    
    region = 0
    n = 1
    while region < total_regions:
        s_w_h_d = 0
        while s_w_h_d < 4:
            fig=plt.figure()
            ax=fig.add_subplot(2, 2, 1, label="1")
            ax2=fig.add_subplot(2,2, 1, label="1", frame_on=False)
            ax.plot(x_axis[1:1*2*hourly_ts_day+1], solar_and_wind_sorter_seasonal[n,0:1*2*hourly_ts_day], color="b")
            ax.set_xlabel("Time Slices")
            ax.set_ylabel("%")
            ax.set_title(regions_or_countries[region]+' - '+ s_w_h_ds[s_w_h_d]+' - Winter')
            ax.set_xlim([1,1*2*hourly_ts_day])
            ax.set_ylim([0,1])
            ax2.plot(x2_axis[1:2190+1], solar_and_wind_duration_curve_seasonal[n,0:2190], color="r")
            ax2.get_xaxis().set_visible(False)
            ax2.get_yaxis().set_visible(False)
            ax2.set_xlim([1,2190])
            ax2.set_ylim([0,1])
            
            ax=fig.add_subplot(2, 2, 2, label="1")
            ax2=fig.add_subplot(2, 2, 2, label="1", frame_on=False)
            ax.plot(x_axis[1:1*2*hourly_ts_day+1], solar_and_wind_sorter_seasonal[n,1*2*hourly_ts_day:2*2*hourly_ts_day], color="b")
            ax.set_xlabel("Time Slices")
            ax.set_ylabel("%")
            ax.set_title(regions_or_countries[region]+' - '+ s_w_h_ds[s_w_h_d]+' - Spring')
            ax.set_xlim([1,1*2*hourly_ts_day])
            ax.set_ylim([0,1])
            ax2.plot(x2_axis[1:2190+1], solar_and_wind_duration_curve_seasonal[n,2190:2190*2], color="r")
            ax2.get_xaxis().set_visible(False)
            ax2.get_yaxis().set_visible(False)
            ax2.set_xlim([1,2190])
            ax2.set_ylim([0,1])
                
            ax=fig.add_subplot(2, 2, 3, label="1")
            ax2=fig.add_subplot(2, 2, 3, label="1", frame_on=False)
            ax.plot(x_axis[1:1*2*hourly_ts_day+1], solar_and_wind_sorter_seasonal[n,2*2*hourly_ts_day:3*2*hourly_ts_day], color="b")
            ax.set_xlabel("Time Slices")
            ax.set_ylabel("%")
            ax.set_title(regions_or_countries[region]+' - '+ s_w_h_ds[s_w_h_d]+' - Summer')
            ax.set_xlim([1,1*2*hourly_ts_day])
            ax.set_ylim([0,1])
            ax2.plot(x2_axis[1:2190+1], solar_and_wind_duration_curve_seasonal[n,2190*2:2190*3], color="r")
            ax2.get_xaxis().set_visible(False)
            ax2.get_yaxis().set_visible(False)
            ax2.set_xlim([1,2190])
            ax2.set_ylim([0,1])
            
            ax=fig.add_subplot(2, 2, 4, label="1")
            ax2=fig.add_subplot(2, 2, 4, label="1", frame_on=False)
            ax.plot(x_axis[1:1*2*hourly_ts_day+1], solar_and_wind_sorter_seasonal[n,3*2*hourly_ts_day:ts], color="b")
            ax.set_xlabel("Time Slices")
            ax.set_ylabel("%")
            ax.set_title(regions_or_countries[region]+' - '+ s_w_h_ds[s_w_h_d]+' - Autumn')
            ax.set_xlim([1,1*2*hourly_ts_day])
            ax.set_ylim([0,1])
            ax2.plot(x2_axis[1:2190+1], solar_and_wind_duration_curve_seasonal[n,2190*3:2190*4], color="r")
            ax2.get_xaxis().set_visible(False)
            ax2.get_yaxis().set_visible(False)
            ax2.set_xlim([1,2190])
            ax2.set_ylim([0,1])
            
            plt.tight_layout()
            fig.subplots_adjust(hspace=0.6, wspace=0.4)

            plt.savefig(path+'Results/Time slices '+regions_or_countries[region]+' seasonal '+s_w_h_ds[s_w_h_d] + '4 seasons, 2 weekly, '+ str(hourly_ts_day) +' hours')  
            
            n = n + 1
            s_w_h_d = s_w_h_d + 1      
        region = region + 1

    # Plotting annual results    
    x_axis = np.arange(ts+1)
    x2_axis = np.arange(8761)
    s_w_h_ds = ['Solar','Wind','Hydro','Demand']
    
    region = 0
    n = 1
    while region < total_regions:
        s_w_h_d = 0
        
        fig=plt.figure()
        ax=fig.add_subplot(2, 2, 1, label="1")
        ax2=fig.add_subplot(2,2, 1, label="1", frame_on=False)
        ax.plot(x_axis[1:ts+1], solar_and_wind_sorter_annual[n,:], color="b")
        ax.set_xlabel("Time Slices")
        ax.set_ylabel("%")
        ax.set_title(regions_or_countries[region]+' '+s_w_h_ds[s_w_h_d])
        ax.set_xlim([1,ts])
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
        ax.plot(x_axis[1:ts+1], solar_and_wind_sorter_annual[n,:], color="b")
        ax.set_xlabel("Time Slices")
        ax.set_ylabel("%")
        ax.set_title(regions_or_countries[region]+' '+s_w_h_ds[s_w_h_d])
        ax.set_xlim([1,ts])
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
        ax.plot(x_axis[1:ts+1], solar_and_wind_sorter_annual[n,:], color="b")
        ax.set_xlabel("Time Slices")
        ax.set_ylabel("%")
        ax.set_title(regions_or_countries[region]+' '+s_w_h_ds[s_w_h_d])
        ax.set_xlim([1,ts])
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
        ax.plot(x_axis[1:ts+1], solar_and_wind_sorter_annual[n,:], color="b")
        ax.set_xlabel("Time Slices")
        ax.set_ylabel("%")
        ax.set_title(regions_or_countries[region]+' '+s_w_h_ds[s_w_h_d])
        ax.set_xlim([1,ts])
        ax.set_ylim([0,1])
        ax2.plot(x2_axis[1:8761], solar_and_wind_duration_curve_annual[n,:], color="r")
        ax2.get_xaxis().set_visible(False)
        ax2.get_yaxis().set_visible(False)
        ax2.set_xlim([1,8760])
        ax2.set_ylim([0,1])
        
        plt.tight_layout()
        fig.subplots_adjust(hspace=0.6, wspace=0.4)

        plt.savefig(path+'Results/Time slices '+regions_or_countries[region]+' annual '+s_w_h_ds[s_w_h_d] + '4 seasons, 2 weekly, '+ str(hourly_ts_day) +' hours')    
          
        n = n + 1        
        region = region + 1
    
