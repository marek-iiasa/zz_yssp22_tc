# -*- coding: utf-8 -*-
"""
This script tests the functionality of storage technologies. This is done by
a few changes in the scenario to invoke the operation of storage, including:
    - adding required "input" commodity for the charger of storage (see test 4 and 5).
    - making storage technology very cheap (see test 6).
    - adding limitation on electricity generation in some time slices (see test 7)
"""
import os
import ixmp as ix
import message_ix
from message_ix.utils import make_df

mp = ix.Platform()
git_path = r"C:\Users\zakeri\Documents\Github"
path_files = git_path + r"\python_scripts"
os.chdir(path_files)

# reference model/scenario
model = "MESSAGEix-China"
scenario = "baseline_c_t16_stor"
version = None

node_list = ["China"]

# Removing input commodity of storage reservoir (must be done)
remove_input_storage = True

# Selecting a few time slices for applying changes that invoke storage
test_time_storage = ["3", "5", "11"]

# Changing investment and capacity factor in some time slices of PV (multiplier)
# if no change is desired leave the values as 1
change_inv_pv = {"solar_pv_ppl": 1}

# Changing investment cost of storage
# if no change is desired leave the values as 1
change_inv_storage = {"battery": 1, "battery_pcs": 1}

# Changing capacity factor in some time slices (multiplier)
# if no change is desired leave the values as 1
change_cf = {"solar_pv_ppl": 0.001}

# Adding an emission bound (None or a value)
add_emission_bound = None

# Adding a technology for water supply
add_water_inflow = False

# Adding bounds on supply of water in a few time slices
add_bound_water_supply = False

# Adding demand for water in a few time slices
add_water_demand = False

# Removing bounds from some technologies at "year" carried over from the old scenario
remove_bound = {"solar_pv_ppl": ["year"]}

# Storage discharge technologies
storage_techs = ["turbine", "battery_pcs"]


# %% Loading reference scenario
sc_ref = message_ix.Scenario(mp, model, scenario , version)
sc = sc_ref.clone(scenario="test_storage", keep_solution=False)

# Modifications and testing
sc.check_out()
model_years = [x for x in set(sc.set("year")) if x >= sc.firstmodelyear]

# Making capacity factor of PV zero in some time slices
if change_inv_pv:
    # Making investment cost of PV small
    for tec, val in change_inv_pv.items():
        df = sc.par("inv_cost", {"technology": tec})
        df["value"] *= val
        sc.add_par("inv_cost", df)

# Making investment cost of one storage technology cheaper
if change_inv_storage:
    # Making investment cost of storage small
    for tec, val in change_inv_storage.items():
        for parname in ["inv_cost", "fix_cost"]:
            df = sc.par(parname, {"technology": tec})
            df["value"] *= val
            sc.add_par(parname, df)
    
# Removing "input" and "output" of reservoir technology
if remove_input_storage:
    for parname in ["input", "output"]:
        df = sc.par(parname, {"technology": ["battery", "hydro_phs"]})
        sc.remove_par(parname, df)

# Adding water inflow 
# Naming convention for water commodity and supply technology for hydropower
water_com = 'water'  
water_supply_tec = 'water_inflow'
water_spil_tec = "water_spillage"
water_in_level = "water_upstream"
water_out_level = "water_downstream"
if add_water_inflow:
    sc.add_set('technology', [water_supply_tec, water_spil_tec])
    tec_water = [("turbine", "Cha")]
    
    for tec, mode in tec_water:
        # Adding output for water supply
        df = sc.par('output', {'technology': tec, "mode": mode})
        df['technology'] = water_supply_tec
        df["mode"] = "M1"
        df['level'] = list(set(sc.par('input', {'technology': tec, "mode": mode,
                                      'commodity': water_com})['level']))[0]
        sc.add_par('output', df)
        
        # Adding input/output for water spillage
        df["technology"] = water_spil_tec
        df["level"] = water_out_level
        sc.add_par('output', df)
        
        # Adding input for water spillage
        df["level"] = water_in_level
        df = df.rename({"time_dest": "time_origin", "node_dest": "node_origin"},
                       axis=1)
        sc.add_par('input', df)
        
    # Adding bounds on supply of water 
    if add_bound_water_supply:
        bound = {"technology": water_supply_tec,
                 "mode": "M1",
                 "time": test_time_storage,
                 "node_loc": "China",
                 "value": 0,
                 "unit": "-",
                 }
        for yr in model_years:
            bd = make_df("bound_activity_up", **bound, year_act=yr)
            sc.add_par("bound_activity_up", bd)
            
# Adding water demand
if add_water_demand:
    demand = {"commodity": water_com,
             "time": test_time_storage,
             "level": water_out_level,
             "node": "China",
             "value": 20,
             "unit": "-",
             }
    for yr in model_years:
        dem = make_df("demand", **demand, year=yr)
        sc.add_par("demand", dem)

# Adding emission bound
if add_emission_bound:
    sc.add_par("bound_emission", ["China", "TCE", "all", "cumulative"],
               add_emission_bound, '-')

# Limit generation in a few time slices
if change_cf:
    # Making capacity factor of some technologies small in some time slices
    for tec, val in change_cf.items():
        df = sc.par("capacity_factor", {"technology": tec, "time": test_time_storage})
        df["value"] *= val
        sc.add_par("capacity_factor", df)
    
# Remove bound on solar PV
if remove_bound:
    for parname in ["bound_activity_up", "bound_new_capacity_up", "bound_total_capacity_up"]:
        for tec, times in remove_bound.items():
            df = sc.par(parname, {"technology": tec})
            if "activity" in parname:
                df = df.loc[df["time"].isin(times)].copy()
            sc.remove_par(parname, df)

# Commit and solve
sc.commit("")
print("- Solving the scenario ...")
case = sc.model + '__' + sc.scenario + '__v' + str(sc.version)
sc.solve(solve_options={'lpmethod': '4'})

# %% Notes for the tests
# 1) No storage: when there is no inflow of water (add_water_inflow = False)
# and no limit on generation of electricity (limit_generation = []) ==> model solves, storage is not needed.

# 2) Water needed but no inflow: when there is water demand in
# some time slices (add_water_demand = True) but there is no inflow of water (add_water_inflow = False)
# the model is not solving (infeasible) because no supply of water

# 3) Water needed but no PHS (pumped hydro storage)): when there is water demand in
# some time slices (add_water_demand = True) as well inflow of water (add_water_inflow = True)
# and there is no bound on supply (add_bound_water_supply = False), the model solves, no storage needed, as spillage technology brings water to demand

# 4) PHS working to meet water demand: when there is water demand in some time slices (add_water_demand = True)
# and there is inflow of water (add_water_inflow = True) but inflow limited in some time slices
# (add_bound_water_supply = True) ==> model solves, water storage works

# 5) PHS working due to electricity needs: add water demand in some time slices (add_water_demand = True)
# and there is inflow of water (add_water_inflow = True) and not limited (add_bound_water_supply = False)
# Then, limit generation in some time slices (using change_cf),
# ==> model solves, hydropower storage works for balancing electricity

# 6) Battery working to meet electricity needs: 
# Deactivate PHS by adding no inflow of water (add_water_inflow = False)
# Then, make battery cheap by multiplying the costs by 0.001
# ==> model solves, battery works for balancing electricity in related time slices