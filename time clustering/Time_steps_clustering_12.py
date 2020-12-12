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
from datetime import timedelta

def algorithm(data,name,value,solarweight,windweight,hydroweight,demandweight,mid_night,path): 

    dt = data.values
    total_regions = len(name)
    solar_and_wind_seasonal = np.zeros(shape=(12))
    solar_and_wind_sorter_seasonal = np.zeros(shape=(12))
    solar_and_wind_duration_curve_seasonal =  np.zeros(shape=(8760))
    
    solar_and_wind_annual = np.zeros(shape=(12))
    solar_and_wind_sorter_annual = np.zeros(shape=(12))
    solar_and_wind_duration_curve_annual =  np.zeros(shape=(8760))
          
    region = 0
    # Cicle to create the time slices for all regions, working one by one as shown above. 
    while region < total_regions:
        
        # Hourly salor, wind, hydro and demand data.
        solar = dt[:,1+5*value[region]]
        wind = dt[:,2+5*value[region]]
        hydro = dt[:,4+5*value[region]]
        demand = dt[:,3+5*value[region]]
        demand_MW = dt[:,5+5*value[region]]
        
        # Yearly hourly load curve
        solar_load_curve_annual = np.sort(solar, axis=None)[::-1]
        wind_load_curve_annual = np.sort(wind, axis=None)[::-1]
        demand_load_curve_annual = np.sort(demand, axis=None)[::-1]
        hydro_load_curve_annual = np.sort(hydro, axis=None)[::-1]
    
        # Seasonal yearly load curve 
        solar_load_curve_Wi = np.sort(solar[0:4380], axis=None)[::-1]
        wind_load_curve_Wi = np.sort(wind[0:4380], axis=None)[::-1]
        hydro_load_curve_Wi = np.sort(hydro[0:4380], axis=None)[::-1]    
        demand_load_curve_Wi = np.sort(demand[0:4380], axis=None)[::-1]
    
        solar_load_curve_Su = np.sort(solar[4380:8760], axis=None)[::-1]
        wind_load_curve_Su = np.sort(wind[4380:8760], axis=None)[::-1]
        hydro_load_curve_Su = np.sort(hydro[4380:8760], axis=None)[::-1]
        demand_load_curve_Su = np.sort(demand[4380:8760], axis=None)[::-1]
    
    
        # Reducing the hour resolution to 4 hourly resolution.
        solar_4h = np.zeros(shape=(2190))
        wind_4h = np.zeros(shape=(2190))
        hydro_4h = np.zeros(shape=(2190))
        demand_4h = np.zeros(shape=(2190))
    
        # Adjust the starting day of the series to midnight. 
        x = 0
        while x < 8760:          
            solar_4h[int(x/4)] = solar_4h[int(x/4)] + solar[x]/4
            wind_4h[int(x/4)] = wind_4h[int(x/4)] + wind[x]/4 
            hydro_4h[int(x/4)] = hydro_4h[int(x/4)] + hydro[x]/4        
            demand_4h[int(x/4)] = demand_4h[int(x/4)] + demand[x]/4 
            x = x + 1
        
    # NEW METHOD: Pick the most representative day in the season, then pick a scrambles day to better represent the season and the week. 
    # How to do it: First pick the best representative day in the season. Then look for the other times slices in the week. 
    
    # Calculating separetely Winter, Spring, Summer and Autumn. 
    
    # For each season,  there are 547.5 comparisonas required. 
    # For each comparison, the 2190 days will be compared with the 2 days of the representative week. 
    
    #(mininum sum non 0,w,d1,h1,h2,h3,h4,)
        
        w_minimum = [10000000000,0,0]#
        su_minimum = [10000000000,0,0]
            
        solar_results_seasonal = np.zeros(shape=(12))
        wind_results_seasonal = np.zeros(shape=(12))
        hydro_results_seasonal = np.zeros(shape=(12))
        demand_results_seasonal = np.zeros(shape=(12))
        
        solar_results_sorted_seasonal = np.zeros(shape=(12))
        wind_results_sorted_seasonal = np.zeros(shape=(12))
        hydro_results_sorted_seasonal = np.zeros(shape=(12))
        demand_results_sorted_seasonal = np.zeros(shape=(12))
        
        w = 0
        x1 = 0
        while w < 13*2:
            #This is the equation that balances the load curve and the clustered values, thus it should vary between - and + numbers. And the number closest to 0 should be selected. 
            x2 = 0
            s_w_4_sorted1  = solar_4h[w*42:w*42+42]
            s_su_4_sorted1 = solar_4h[547+547+w*42:547+547+w*42+42] 
        
            w_w_4_sorted1  = wind_4h[w*42:w*42+42]
            w_su_4_sorted1 = wind_4h[547+547+w*42:547+547+w*42+42]
        
            h_w_4_sorted1  = hydro_4h[w*42:w*42+42]
            h_su_4_sorted1 = hydro_4h[547+547+w*42:547+547+w*42+42]
            
            d_w_4_sorted1  = demand_4h[w*42:w*42+42]
            d_su_4_sorted1 = demand_4h[547+547+w*42:547+547+w*42+42]  
        
            d1 = 0
            while d1 < 7:                          
                s_w_4_sorted  = np.sort(s_w_4_sorted1[0+d1*6:6+d1*6])
                s_su_4_sorted = np.sort(s_su_4_sorted1[0+d1*6:6+d1*6])
                
                w_w_4_sorted  = np.sort(w_w_4_sorted1[0+d1*6:6+d1*6])
                w_su_4_sorted = np.sort(w_su_4_sorted1[0+d1*6:6+d1*6])
        
                h_w_4_sorted  = np.sort(h_w_4_sorted1[0+d1*6:6+d1*6])
                h_su_4_sorted = np.sort(h_su_4_sorted1[0+d1*6:6+d1*6])
                
                d_w_4_sorted  = np.sort(d_w_4_sorted1[0+d1*6:6+d1*6])
                d_su_4_sorted = np.sort(d_su_4_sorted1[0+d1*6:6+d1*6])
                                
                x2 = 0
                sum1 = 0
                sum3 = 0
                while x2 < 2190 + 2190:
                    sum1 = sum1 + ((solar_load_curve_Wi[x2] - s_w_4_sorted[int(x2/365/2)])**2) #Inverno         
                    sum3 = sum3 + ((solar_load_curve_Su[x2] - s_su_4_sorted[int(x2/365/2)])**2) #Verao   
                
                    sum1 = sum1 + ((wind_load_curve_Wi[x2] - w_w_4_sorted[int(x2/365/2)])**2)         
                    sum3 = sum3 + ((wind_load_curve_Su[x2] - w_su_4_sorted[int(x2/365/2)])**2)          
        
                    sum1 = sum1 + ((hydro_load_curve_Wi[x2] - h_w_4_sorted[int(x2/365/2)])**2)/3 # Hydropower is not well represented in the model, so we reduce the impact of hydropower on the final results.       
                    sum3 = sum3 + ((hydro_load_curve_Su[x2] - h_su_4_sorted[int(x2/365/2)])**2)/3     
                        
                    sum1 = sum1 + ((demand_load_curve_Wi[x2] - d_w_4_sorted[int(x2/365/2)])**2)           
                    sum3 = sum3 + ((demand_load_curve_Su[x2] - d_su_4_sorted[int(x2/365/2)])**2)            
                    x2 = x2 + 1
                                
                if sum1 != 0 and sum1 < w_minimum[0]:
                    w_minimum = [sum1,w,d1]
                    solar_results_seasonal[0:6] = s_w_4_sorted1[0+d1*6:6+d1*6]
                    wind_results_seasonal[0:6] = w_w_4_sorted1[0+d1*6:6+d1*6]
                    hydro_results_seasonal[0:6] = h_w_4_sorted1[0+d1*6:6+d1*6]
                    demand_results_seasonal[0:6] = d_w_4_sorted1[0+d1*6:6+d1*6]
                    solar_results_sorted_seasonal[0:6] = s_w_4_sorted
                    wind_results_sorted_seasonal[0:6] = w_w_4_sorted
                    hydro_results_sorted_seasonal[0:6] = h_w_4_sorted
                    demand_results_sorted_seasonal[0:6] = d_w_4_sorted                        
                                                                    
                if sum3 != 0 and sum3 < su_minimum[0]:
                    su_minimum = [sum3,w,d1]
                    solar_results_seasonal[6:12] = s_su_4_sorted1[0+d1*6:6+d1*6]
                    wind_results_seasonal[6:12] = w_su_4_sorted1[0+d1*6:6+d1*6]
                    hydro_results_seasonal[6:12] = h_su_4_sorted1[0+d1*6:6+d1*6]
                    demand_results_seasonal[6:12] = d_su_4_sorted1[0+d1*6:6+d1*6]
                    solar_results_sorted_seasonal[6:12] = s_su_4_sorted
                    wind_results_sorted_seasonal[6:12] = w_su_4_sorted
                    hydro_results_sorted_seasonal[6:12] = h_su_4_sorted
                    demand_results_sorted_seasonal[6:12] = d_su_4_sorted 
                                    
                d1 = d1 + mid_night
                print('r ' + name[region] + ' - w '+ str(w) + ' - d '+ str(d1))
            w = w + 1
        
        solar_load_curve_seasonal =  np.zeros(shape=(8760))
        wind_load_curve_seasonal =  np.zeros(shape=(8760))
        hydro_load_curve_seasonal =  np.zeros(shape=(8760))
        demand_load_curve_seasonal =  np.zeros(shape=(8760))
        
        solar_load_curve_seasonal[0:4380] = solar_load_curve_Wi
        solar_load_curve_seasonal[4380:8760] = solar_load_curve_Su
        wind_load_curve_seasonal[0:4380] = wind_load_curve_Wi
        wind_load_curve_seasonal[4380:8760] = wind_load_curve_Su
        hydro_load_curve_seasonal[0:4380] = hydro_load_curve_Wi
        hydro_load_curve_seasonal[4380:8760] = hydro_load_curve_Su
        demand_load_curve_seasonal[0:4380] = demand_load_curve_Wi
        demand_load_curve_seasonal[4380:8760] = demand_load_curve_Su
    
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
                
    # Save the time slices        
    panda = pd.DataFrame(solar_and_wind_seasonal.T)
    panda.to_excel(path+'Results/12 Time Slices (Seasonal).xlsx')

    panda = pd.DataFrame(solar_and_wind_sorter_seasonal.T)
    panda.to_excel(path+'Results/12 Time Slices Sorted (Seasonal).xlsx')

    panda = pd.DataFrame(solar_and_wind_duration_curve_seasonal.T)
    panda.to_excel(path+'Results/Duration Curve (Seasonal).xlsx')

    panda = pd.DataFrame(solar_and_wind_annual.T)
    panda.to_excel(path+'Results/12 Time Slices (Annual).xlsx')

    panda = pd.DataFrame(solar_and_wind_sorter_annual.T)
    panda.to_excel(path+'Results/12 Time Slices Sorted (Annual).xlsx')

    panda = pd.DataFrame(solar_and_wind_duration_curve_annual.T)
    panda.to_excel(path+'Results/Duration Curve (Annual).xlsx')

     


    # Plotting the seasonal results
    x_axis = np.arange(13)
    x2_axis = np.arange(2191+2190)
    s_w_h_ds = ['Solar','Wind','Hydro','Demand']
    
    region = 0 #se region = 0 começa sempre da primeira coluna; se eu seleciono 
    n = 1
    while region < total_regions: 
        s_w_h_d = 0
        while s_w_h_d < 4:
            fig=plt.figure()
            ax=fig.add_subplot(2, 2, 1, label="1")
            ax2=fig.add_subplot(2,2, 1, label="1", frame_on=False)
            ax.plot(x_axis[1:7], np.sort(solar_and_wind_sorter_seasonal[n,0:6], axis=None)[::-1], color="b")
            ax.set_xlabel("Time Slices")
            ax.set_ylabel("%")
            ax.set_title(name[region]+' - '+ s_w_h_ds[s_w_h_d]+' - Winter')
            ax.set_xlim([1,6])
            ax.set_ylim([0,1])
            ax2.plot(x2_axis[1:2191+2190], solar_and_wind_duration_curve_seasonal[n,0:2190+2190], color="r")
            ax2.get_xaxis().set_visible(False)
            ax2.get_yaxis().set_visible(False)
            ax2.set_xlim([1,2190+2190])
            ax2.set_ylim([0,1])
                       
            ax=fig.add_subplot(2, 2, 3, label="1")
            ax2=fig.add_subplot(2, 2, 3, label="1", frame_on=False)
            ax.plot(x_axis[1:7], np.sort(solar_and_wind_sorter_seasonal[n,6:12], axis=None)[::-1], color="b")
            ax.set_xlabel("Time Slices")
            ax.set_ylabel("%")
            ax.set_title(name[region]+' - '+ s_w_h_ds[s_w_h_d]+' - Summer')
            ax.set_xlim([1,6])
            ax.set_ylim([0,1])
            ax2.plot(x2_axis[1:2191+2190], solar_and_wind_duration_curve_seasonal[n,2190+2190:2190+2190+2190+2190], color="r")
            ax2.get_xaxis().set_visible(False)
            ax2.get_yaxis().set_visible(False)
            ax2.set_xlim([1,2190+2190])
            ax2.set_ylim([0,1])
            
            plt.tight_layout()
            fig.subplots_adjust(hspace=0.6, wspace=0.4)
    
            plt.savefig(path+'Results/12 Time slices '+ name[region]+' seasonal '+s_w_h_ds[s_w_h_d])
            
            n = n + 1
            s_w_h_d = s_w_h_d + 1      
        region = region + 1

    # Plotting annual results
    x_axis = np.arange(13)
    x2_axis = np.arange(8761)
    s_w_h_ds = ['Solar','Wind','Hydro','Demand']
    
    region = 0
    n = 1
    while region < total_regions:
        s_w_h_d = 0
        
        fig=plt.figure()
        ax=fig.add_subplot(2, 2, 1, label="1")
        ax2=fig.add_subplot(2,2, 1, label="1", frame_on=False)
        ax.plot(x_axis[1:13], solar_and_wind_sorter_annual[n,:], color="b")
        ax.set_xlabel("Time Slices")
        ax.set_ylabel("%")
        ax.set_title(name[region]+' '+s_w_h_ds[s_w_h_d])
        ax.set_xlim([1,12])
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
        ax.plot(x_axis[1:13], solar_and_wind_sorter_annual[n,:], color="b")
        ax.set_xlabel("Time Slices")
        ax.set_ylabel("%")
        ax.set_title(name[region]+' '+s_w_h_ds[s_w_h_d])
        ax.set_xlim([1,12])
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
        ax.plot(x_axis[1:13], solar_and_wind_sorter_annual[n,:], color="b")
        ax.set_xlabel("Time Slices")
        ax.set_ylabel("%")
        ax.set_title(name[region]+' '+s_w_h_ds[s_w_h_d])
        ax.set_xlim([1,12])
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
        ax.plot(x_axis[1:13], solar_and_wind_sorter_annual[n,:], color="b")
        ax.set_xlabel("Time Slices")
        ax.set_ylabel("%")
        ax.set_title(name[region]+' '+s_w_h_ds[s_w_h_d])
        ax.set_xlim([1,12])
        ax.set_ylim([0,1])
        ax2.plot(x2_axis[1:8761], solar_and_wind_duration_curve_annual[n,:], color="r")
        ax2.get_xaxis().set_visible(False)
        ax2.get_yaxis().set_visible(False)
        ax2.set_xlim([1,8760])
        ax2.set_ylim([0,1])
        
        plt.tight_layout()
        fig.subplots_adjust(hspace=0.6, wspace=0.4)
        
        plt.savefig(path+'Results/12 Time slices '+ name[region]+' annual '+s_w_h_ds[s_w_h_d])    
       
        n = n + 1        
        region = region + 1



#%%

