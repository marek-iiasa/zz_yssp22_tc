import os
from ixmp import Platform
import message_ix

# Path to message_data repository
msg_data_path = r'C:\Users\...\Documents\Github\message_data\message_data'

# Switching to the path of reporting files
reporting_path = '{}\\tools\\post_processing'.format(msg_data_path)
os.chdir(reporting_path)

# Importing the main function for reporting
from iamc_report_hackathon import report as reporting

# Defining the output path for saving the reporting output Excel files
output_path = r'C:\Users\...\Documents\output'

# %% Loading the platform
mp = Platform(name='ene_ixmp', jvmargs=['-Xms800m', '-Xmx8g'])

# Model/scenario/version
model = 'ENGAGE_SSP2_v4.1.2'
scenario = 'baseline'
version = 9
reporting_history = False

# Loading a scenario for reporting its results
sc = message_ix.Scenario(mp, model, scenario, version, cache=True)

# Compiling the reporting for historical years if needed
if reporting_history:
    reporting(mp, sc, 'True', model, scenario, version, out_dir=output_path)

# Compiling the reporting for optimization years
reporting(mp, sc, 'False', model, scenario, version, out_dir=output_path)
