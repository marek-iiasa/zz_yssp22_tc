# -*- coding: utf-8 -*-
'''
This script shows how to load the data of a scenario from excel.
'''

# 1) Importing required packages and specifying input data
import ixmp as ix
import message_ix

# Specifying model and scenario that we want to save in our database
model = "MESSAGE_CAS"
scenario = "baseline"

# Path to the excel file
xls_path = r'C:\Users\...\Github\time_clustering\scenario work\data'  #update this path to yours

# Excel file name
file_name = 'MESSAGE_CASm__baseline_t12__v8.xlsx'

xls_file = xls_path + '\\' + file_name

# 2) Loading a platform and creating a new empty scenario
# 2.1) By loading local default database
mp = ix.Platform()

# 2.2)creating a new (empty) scenario
sc = message_ix.Scenario(mp, model, scenario, version='new')

# 3) Reading data from Excel
sc.read_excel(xls_file, add_units=True, init_items=True, commit_steps=True)

# 4) Solving the model
# An optional name for the scenario GDX files
caseName = sc.model + '__' + sc.scenario + '__v' + str(sc.version)

# Solving
sc.solve(case=caseName, solve_options={'lpmethod': '4'})
