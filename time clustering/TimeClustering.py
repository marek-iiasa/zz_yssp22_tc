# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 15:02:13 2020

@author: hunt
"""
import pandas as pd
import datetime
import os

# Add the directory used to run the time clustering algorithm.
path_xls = 'C:/Users/zakeri/Documents/Excel_files/timeslices/'
path_dir = 'C:/Users/zakeri/Documents/Github/time_clustering/time clustering'
os.chdir(path_dir)

now = datetime.datetime.now()

# Algorithm time selection
# Select the op value according to the scenario you want to analyze from 1 to 3
op=2
# op = 1 = 12 Time steps clustering
# op = 2 = 24 Time steps clustering
# op = 3 = 48 Time steps clustering

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
if r_or_c:
    input_data = pd.read_excel(path_xls + '11 regions.xlsx')

    # Select the number of the regions that needs to be analysed with the numbers below:
    # region => NAM = 0, LAC = 1, WEU = 2, EEU = 3, FSU = 4, AFR = 5, MEA = 6, SAS = 7, CPA = 8, PAS = 9, PAO = 10
    regions_or_countries = ['NAM','EEU','CPA']
    selected_regions_or_countries = [0,3,8]

else:
    input_data = pd.read_excel(path_xls + 'individual_countries.xlsx')
    print('- Large Excel file being loaded, please wait...')
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

# Output folder
folder = '_'.join(regions_or_countries)
out_dir = path_dir + "/Results/" + folder
if not os.path.exists(out_dir):
        os.mkdir(out_dir)

if op==1:
    from Time_steps_clustering_12 import algorithm as t12
    t12(input_data, regions_or_countries, selected_regions_or_countries,
        solar_weight, wind_weight, hydro_weight, demand_weight, mid_night,
        out_dir)
    x = 0

elif op==2:
    from Time_steps_clustering_24 import algorithm as t24
    t24(input_data, regions_or_countries, selected_regions_or_countries,
        solar_weight, wind_weight, hydro_weight, demand_weight, mid_night,
        path_dir)
    x = 0

elif op==3:
    from Time_steps_clustering_48 import algorithm as t48
    t48(input_data, regions_or_countries, selected_regions_or_countries,
        solar_weight, wind_weight, hydro_weight, demand_weight, mid_night,
        path_dir)
    x = 0



#%%