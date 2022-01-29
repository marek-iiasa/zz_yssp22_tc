# -*- coding: utf-8 -*-
"""
This script creates simple models for testing storage.
It is written in a flexible function to design different storage options with
# different configurations automatically.

"""

from itertools import product
from message_ix import Scenario

# I) Funcitons for building a simple model with (or without) storage
# A function for adding required parameters for representing "capacity"
def add_cap_par(scen, years, tec, data={"inv_cost": 0.1, "technical_lifetime": 5}):

    for year, (parname, val) in product(years, data.items()):
        scen.add_par(parname, ["Wonderland", tec, year], val, "-")


# A function for generating a simple model with sub-annual time slices
def model_generator(
    test_mp,
    comment,
    tec_dict,
    time_steps,
    demand,
    com_dict,
    add_bound={},
    var_cost={("gas_ppl", "M1"): 20},
    yr=2020,
    capacity={"gas_ppl": 600},
    unit="GWa",
    storage={},
    ):
    """

    Generates a simple model with two technologies, and a flexible number of
    time slices.

    Parameters
    ----------
    test_mp : ixmp.Platform()
    comment : string
        Annotation for saving different scenarios and comparing their results.
    tec_dict : dict
        A dictionary for a technology and required information for time-related
        parameters.
        (e.g., tec_dict = {("gas_ppl", "M1"): {"time_origin": ["summer"],
                                       "time": ["summer"], "time_dest": ["summer"]})
    time_steps : list of tuples
        Information about each time slice, packed in a tuple with four elements,
        including: time slice name, duration relative to "year", "temporal_lvl",
        and parent time slice.
        (e.g., time_steps = [("summer", 1, "season", "year")])
    demand : dict
        A dictionary for information of "demand" in each time slice.
        (e.g., demand = {"summer": 2.5})
    com_dict : dict
        A dictionary for specifying "input" and "output" commodities.
        (e.g., com_dict = {"gas_ppl": {"input": "fuel", "output": "electr"}})
    yr : int, optional
        Model year. The default is 2020.
    capacity : bool, optional
        Parameterization of capacity. The default is True.
    unit :  string
        Unit of "demand"


    """

    # Building an empty scenario
    scen = Scenario(test_mp, "test-time", comment, version="new")

    # Adding required sets
    scen.add_set("node", "Wonderland")
    for (tec, mode), data in com_dict.items():
        scen.add_set("mode", mode)
        scen.add_set("commodity", [x[0] for x in list(data.values()) if x])
        scen.add_set("level", [x[1] for x in list(data.values()) if x])

    scen.add_set("year", yr)
    scen.add_set("type_year", yr)
    scen.add_set("technology", [x[0] for x in list(tec_dict.keys())])
    scen.add_set("lvl_temporal", [x[2] for x in time_steps])
    scen.add_set("time", [x[0] for x in time_steps])
    scen.add_set("time", [x[3] for x in time_steps])

    # Adding "time" and "duration_time" to the model
    for (h, dur, tmp_lvl, parent) in time_steps:
        scen.add_set("map_temporal_hierarchy", [tmp_lvl, h, parent])
        scen.add_par("duration_time", [h], dur, "-")

    # Defining demand
    for h, value in demand.items():
        scen.add_par("demand", ["Wonderland", "electr", "final", yr, h], value, unit)

    # Adding "input" and "output" parameters of technologies
    for (tec, mode), times in tec_dict.items():
        if times["time_dest"]:
            for h1, h2 in zip(times["time"], times["time_dest"]):
                out_spec = [
                    yr,
                    yr,
                    mode,
                    "Wonderland",
                    com_dict[(tec, mode)]["output"][0],
                    com_dict[(tec, mode)]["output"][1],
                    h1,
                    h2,
                ]
                scen.add_par("output", ["Wonderland", tec] + out_spec, 1, "-")
                
        if times["time_origin"]:
            for h1, h2 in zip(times["time"], times["time_origin"]):
                inp_spec = [
                    yr,
                    yr,
                    mode,
                    "Wonderland",
                    com_dict[(tec, mode)]["input"][0],
                    com_dict[(tec, mode)]["input"][1],
                    h1,
                    h2,
                ]
                scen.add_par("input", ["Wonderland", tec] + inp_spec, 1, "-")
    
    # Defining bounds on activity
    for tec, data in add_bound.items():
        for h, value in data.items():
            scen.add_par("bound_activity_up", ["Wonderland", tec, yr, "M1", h], value, unit)
            
    # Defining variable cost
    for (t, m), val in var_cost.items():
        for h in set(scen.par("output", {"technology": t})["time"]):
            scen.add_par("var_cost", ["Wonderland", t, yr, yr, m, h], val, "USD/kWa")
    # Adding capacity related parameters
    for t, val in capacity.items():
        add_cap_par(scen, [2020], t, data={"inv_cost": val, "technical_lifetime": 5})
    
    # Adding storage parameters (optional)
    for (tec, mode), s in storage.items():
        # Specifying the level of storage (will be excluded from commodity balance)
        scen.add_set("level", s["level"])
        scen.add_set("level_storage", s["level"])
        
        # Adding storage technologies (reservoir, charger, and discharger)
        scen.add_set("technology", tec)
        scen.add_set("mode", mode)
        
        # Specifying storage reservoir technology
        scen.add_set("storage_tec", tec)
        
        # Adding mapping for storage and charger/discharger technologies
        for (t, m) in s["charger"] + s["discharger"]:
            scen.add_set("map_tec_storage",
                ["Wonderland", t, m, tec, mode, s["level"], s["commodity"],
                 s["lvl_temporal"]])
        
        # Storage specification for storage parameters
        storage_spec = [
                    "Wonderland", tec, mode, s["level"], s["commodity"], 2020]
        # Adding time sequence
        for lvl, pairs in s["time-order"].items():
            for h in pairs.keys():
                scen.add_par("time_order", [lvl, h], pairs[h], "-")
                
                # Adding storage self-discharge
                if s["self-discharge"]:
                    scen.add_par("storage_self_discharge",
                        storage_spec + [h], s["self-discharge"], "%")
        # Adding initial content of storage (optional)
        if s["initial"]:
            scen.add_par("storage_initial", storage_spec + [s["initial"][0]],
                         s["initial"][1], "GWa")

    # Committing and solving
    scen.commit("scenario was set up.")
    scen.solve()
    scen.set_as_default()

    return scen

# %% II) Testing different storage configurations
# 1) Testing storage with different charger/discharge technology
# Time slices
times = ["1", "2", "3", "4"]

# Defining demand in each time slice
demand = {"1": 0.15, "2": 0.2, "3": 0.4, "4": 0.25}

# Relating "time", "duration time", temporal level and parent time
# to be used in parameter "duration_time" and set "map_temporal_hierarchy"
time_steps = [
        ("1", 0.25, "season", "year"),
        ("2", 0.25, "season", "year"),
        ("3", 0.25, "season", "year"),
        ("4", 0.25, "season", "year"),
    ]
# Dictionary of technology input/output time slices
tec_dict = {
    ("gas_ppl", "M1"): {
        "time_origin": [],
        "time": times,
        "time_dest": times,
    },
    ("wind_ppl", "M1"): {
        "time_origin": [],
        "time": times,
        "time_dest": times,
    },
    ("hydro_pump", "M1"): {
        "time_origin": times,
        "time": times,
        "time_dest": times,
    },
    ("hydro_turb", "M1"): {
        "time_origin": times,
        "time": times,
        "time_dest": times,
    },
}

# Defining input/output
com_dict={
    ("gas_ppl", "M1"): {"input": (), "output": ("electr", "final")},
    ("wind_ppl", "M1"): {"input": (), "output": ("electr", "final")},
    ("hydro_pump", "M1"): {"input": ("electr", "final"),
                   "output": ("water", "stor")},
    ("hydro_turb", "M1"): {"input": ("water", "stor"),
                   "output": ("electr", "final")},
}
# Defining bounds and costs 
add_bound = {"wind_ppl": {"1": 0.25, "2": 0.25, "3": 0.25, "4": 0.25},
               }
var_cost={("gas_ppl", "M1"): 2, ("hydro_pump", "M1"): 0.2, ("hydro_turb", "M1"): 0.3}
# capacity={"gas_ppl": 600, "solar_pv_ppl": 900, "hydro_lc": 1800},

storage={("hydro_dam", "M1"):
    {"charger": [("hydro_pump", "M1")],
    "discharger": [("hydro_turb", "M1")],
    "level": "stor",
    "commodity": "water",
    "lvl_temporal": "season",
    "time-order": {"season": {"1": 1, "2": 2, "3": 3, "4": 4}},
    "initial": [],
    "self-discharge": 0.05,
         },
    }

    
def test_storage_equaltime(test_mp):
    comment = "equal-time-storage-no-input"
    # Running the main function
    sc = model_generator(
        test_mp,
        comment,
        tec_dict,
        time_steps,
        demand,
        com_dict,
        add_bound,
        var_cost,
        storage=storage,
        capacity={},
    )


# 2) Testing storage with charger/discharge as one technology but in two modes
def test_storage_equaltime_mode(test_mp):
    comment = "equal-time-storage-mode"
    # Update technology
    tec_dict.pop(("hydro_turb", "M1"))
    tec_dict.pop(("hydro_pump", "M1"))
    tec_dict.update({
        ("hydro_turb", "C"): {
        "time_origin": times,
        "time": times,
        "time_dest": times,
        },
        ("hydro_turb", "D"): {
            "time_origin": times,
            "time": times,
            "time_dest": times,
    }})

    # Update input and output
    com_dict.pop(("hydro_turb", "M1"))
    com_dict.pop(("hydro_pump", "M1"))
    com_dict.update({("hydro_turb", "C"): {"input": ("electr", "final"),
                   "output": ("water", "stor")},
                     ("hydro_turb", "D"): {"input": ("water", "stor"),
                   "output": ("electr", "final")}})
    # Update storage mapping
    storage[("hydro_dam", "M1")].update({"charger": [("hydro_turb", "C")],
                    "discharger": [("hydro_turb", "D")]})
    
    var_cost.pop(("hydro_pump", "M1"))
    var_cost.pop(("hydro_turb", "M1"))
    var_cost.update({("hydro_turb", "C"): 0.2, ("hydro_turb", "D"): 0.3})
    
    # Running the main function
    sc = model_generator(
        test_mp,
        comment,
        tec_dict,
        time_steps,
        demand,
        com_dict,
        add_bound,
        var_cost,
        storage=storage,
        capacity={},
    )
    sc.set_as_default()

   
# 3) Testing two storage technologies operating at two different temporal levels   
def test_storage_two_lvl(test_mp):
    comment = "two-temporal-level"
    
    # Times and temporal levels
    times_w = ["1", "2", "3", "4"]
    times_s = ["5", "6"]
    times = times_w + times_s
    
    time_steps = [('summer', 0.5, 'season', 'year'),
                 ('winter', 0.5, 'season', 'year'),
                 ('1', 0.125, 'day-w', 'winter'),
                 ('2', 0.125, 'day-w', 'winter'),
                 ('3', 0.125, 'day-w', 'winter'),
                 ('4', 0.125, 'day-w', 'winter'),
                 ('5', 0.25, 'day-s', 'summer'),
                 ('6', 0.25, 'day-s', 'summer'),
                 ('1', 0.125, 'day', 'winter'),
                 ('2', 0.125, 'day', 'winter'),
                 ('3', 0.125, 'day', 'winter'),
                 ('4', 0.125, 'day', 'winter'),
                 ('5', 0.25, 'day', 'summer'),
                 ('6', 0.25, 'day', 'summer'),
                 ]
    # Defining demand
    demand = {"1": 0.15, "2": 0.2, "3": 0.4, "4": 0.18, "5": 0.35}

    # Storage technologies
    storage={
        ("battery", "M1"):
            {"charger": [("inverter", "C")],
            "discharger": [("inverter", "D")],
            "level": "stor",
            "commodity": "electrolyte",
            "lvl_temporal": "day-w",
            "time-order": {"day-w": {"1": 1, "2": 2, "3": 3, "4": 4}},
            "initial": [],
            "self-discharge": 0.02,
                 },
        ("hydro_phs", "M1"):
            {"charger": [("turbine", "C")],
            "discharger": [("turbine", "D")],
            "level": "stor",
            "commodity": "water",
            "lvl_temporal": "day",
            # "time-order": {"season": {"winter": 1, "summer": 2}},
            "time-order": {"day": {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6}},
            "initial": [],
            "self-discharge": 0.05,
                 },
    }
        
    # Update technologies
    tec_dict = {
        ("gas_ppl", "M1"): {
        "time_origin": [],
        "time": times,
        "time_dest": times,
    },
        ("wind_ppl", "M1"): {
        "time_origin": [],
        "time": times,
        "time_dest": times,
    },
        ("inverter", "C"): {
            "time_origin": times_w,
            "time": times_w,
            "time_dest": times_w,
        },
        ("inverter", "D"): {
            "time_origin": times_w,
            "time": times_w,
            "time_dest": times_w,
        },
        ("turbine", "C"): {
            "time_origin": times_w + times_s,
            "time": times_w + times_s,
            "time_dest": times_w + times_s,
        },
        ("turbine", "D"): {
            "time_origin": times_w + times_s,
            "time": times_w + times_s,
            "time_dest": times_w + times_s,
        },
        }
    
    # Update input and output
    com_dict = {
    ("gas_ppl", "M1"): {"input": (), "output": ("electr", "final")},
    ("wind_ppl", "M1"): {"input": (), "output": ("electr", "final")},
    ("turbine", "C"): {"input": ("electr", "final"),
                       "output": ("water", "stor")},
    ("turbine", "D"): {"input": ("water", "stor"),
                       "output": ("electr", "final")},
    ("inverter", "C"): {"input": ("electr", "final"),
                       "output": ("electrolyte", "stor")},
    ("inverter", "D"): {"input": ("electrolyte", "stor"),
                       "output": ("electr", "final")},
                    }

    # Variable cost
    var_cost = {("gas_ppl", "M1"): 2, ("wind_ppl", "M1"): 0.0001, ("turbine", "C"): 0.1,
                ("inverter", "C"): 0.01}

    # Defining bounds and costs 
    add_bound = {"wind_ppl": {"1": 0.25, "2": 0.25, "3": 0.25, "4": 0.25,
                              "5": 0.25, "6": 0.25},
                   }    
    # Running the main function
    sc = model_generator(
        test_mp,
        comment,
        tec_dict,
        time_steps,
        demand,
        com_dict,
        add_bound,
        var_cost,
        storage=storage,
        capacity={},
    )
    sc.set_as_default()
    

# 4) Testing storage in three temporal levels. One technology (battery) can
# operate at two different temporal levels (e.g., in two daily cycles in two
# different seasons)
def test_storage_three_lvl(test_mp):
    comment = "three-temporal-level"
    
    # Times and temporal levels
    times_w = ["1", "2", "3", "4"]
    times_s = ["5", "6"]
    times = times_w + times_s
    
    time_steps = [('summer', 0.5, 'season', 'year'),
                 ('winter', 0.5, 'season', 'year'),
                 ('1', 0.125, 'day-w', 'winter'),
                 ('2', 0.125, 'day-w', 'winter'),
                 ('3', 0.125, 'day-w', 'winter'),
                 ('4', 0.125, 'day-w', 'winter'),
                 ('5', 0.25, 'day-s', 'summer'),
                 ('6', 0.25, 'day-s', 'summer'),
                 ('1', 0.125, 'day', 'winter'),
                 ('2', 0.125, 'day', 'winter'),
                 ('3', 0.125, 'day', 'winter'),
                 ('4', 0.125, 'day', 'winter'),
                 ('5', 0.25, 'day', 'summer'),
                 ('6', 0.25, 'day', 'summer'),
                 ]
    # Defining demand
    demand = {"1": 0.15, "2": 0.2, "3": 0.4, "4": 0.18, "5": 0.35}

    # Storage technologies
    storage={
        ("battery", "M1"):
            {"charger": [("inverter", "C")],
            "discharger": [("inverter", "D")],
            "level": "stor",
            "commodity": "electrolyte",
            "lvl_temporal": "day-w",
            "time-order": {"day-w": {"1": 1, "2": 2, "3": 3, "4": 4}},
            "initial": [],
            "self-discharge": 0.02,
                 },
        ("battery", "M2"):
            {"charger": [("inverter", "C")],
            "discharger": [("inverter", "D")],
            "level": "stor",
            "commodity": "electrolyte",
            "lvl_temporal": "day-s",
            "time-order": {"day-s": {"5": 1, "6": 2}},
            "initial": [],
            "self-discharge": 0.02,
                 },
        ("hydro_phs", "M1"):
            {"charger": [("turbine", "C")],
            "discharger": [("turbine", "D")],
            "level": "stor",
            "commodity": "water",
            "lvl_temporal": "day",
            # "time-order": {"season": {"winter": 1, "summer": 2}},
            "time-order": {"day": {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6}},
            "initial": [],
            "self-discharge": 0.05,
                 },
    }
        
    # Update technologies
    tec_dict = {
        ("gas_ppl", "M1"): {
        "time_origin": [],
        "time": times,
        "time_dest": times,
    },
        ("wind_ppl", "M1"): {
        "time_origin": [],
        "time": times,
        "time_dest": times,
    },
        ("inverter", "C"): {
            "time_origin": times,
            "time": times,
            "time_dest": times,
        },
        ("inverter", "D"): {
            "time_origin": times,
            "time": times,
            "time_dest": times,
        },
        ("turbine", "C"): {
            "time_origin": times_w + times_s,
            "time": times_w + times_s,
            "time_dest": times_w + times_s,
        },
        ("turbine", "D"): {
            "time_origin": times_w + times_s,
            "time": times_w + times_s,
            "time_dest": times_w + times_s,
        },
        }
    
    # Update input and output
    com_dict = {
    ("gas_ppl", "M1"): {"input": (), "output": ("electr", "final")},
    ("wind_ppl", "M1"): {"input": (), "output": ("electr", "final")},
    ("turbine", "C"): {"input": ("electr", "final"),
                       "output": ("water", "stor")},
    ("turbine", "D"): {"input": ("water", "stor"),
                       "output": ("electr", "final")},
    ("inverter", "C"): {"input": ("electr", "final"),
                       "output": ("electrolyte", "stor")},
    ("inverter", "D"): {"input": ("electrolyte", "stor"),
                       "output": ("electr", "final")},
                    }

    # Variable cost
    var_cost = {("gas_ppl", "M1"): 2, ("wind_ppl", "M1"): 0.0001, ("turbine", "C"): 0.1,
                ("inverter", "C"): 0.01}

    # Defining bounds and costs 
    add_bound = {"wind_ppl": {"1": 0.25, "2": 0.25, "3": 0.25, "4": 0.25,
                              "5": 0.25, "6": 0.25},
                   }    
    # Running the main function
    sc = model_generator(
        test_mp,
        comment,
        tec_dict,
        time_steps,
        demand,
        com_dict,
        add_bound,
        var_cost,
        storage=storage,
        capacity={},
    )
    sc.set_as_default()
# %% Sample runs
if __name__ == "__main__":
    import ixmp as ix
    mp = ix.Platform()
    test_storage_equaltime_mode(mp)
    test_storage_two_lvl(mp)
    test_storage_three_lvl(mp)
    