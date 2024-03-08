import sys
import gzip
import _pickle as pkl
import pandas as pd
import numpy as np
from Utility import Utility

try:
    repo = sys.argv[1]
except:
    print("No argument")
    sys.exit()

approach_name = "onlysprint"

sprint_dict = {}

print("Reading data...")
dataset = Utility.read_prep_dataset(repo)
sprint_dict['train'] = dataset[0]
sprint_dict['valid'] = dataset[1]
sprint_dict['test'] = dataset[2]

# add for regression
sprint_dict = Utility.replace_class_with_ratio(repo, sprint_dict)

print("shape of sprint train: ", sprint_dict['train'].shape)
print("shape of sprint valid: ", sprint_dict['valid'].shape)
print("shape of sprint test: ", sprint_dict['test'].shape)

print("Processing data...")
for data_set in ['train', 'valid', 'test']:
    # drop id
    sprint_dict[data_set].rename(columns=lambda x: 's_' + x if x not in ['id', 'productivity', 'quality_impact'] else x, inplace=True)
    sprint_dict[data_set].drop('id', axis=1, inplace=True)
    Utility.dump_prep_final_dataset(sprint_dict[data_set], "{}_{}_{}".format(repo, approach_name, data_set))

print("shape of sprint train: ", sprint_dict['train'].shape)
print("shape of sprint valid: ", sprint_dict['valid'].shape)
print("shape of sprint test: ", sprint_dict['test'].shape)
