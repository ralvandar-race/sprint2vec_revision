import sys
import gzip
import _pickle as pkl
import pandas as pd
import numpy as np
from Utility import Utility

try:
    repo = sys.argv[1]
    pooling = sys.argv[2]
except:
    print("No argument")
    sys.exit()

approach_name = "onlytabular"

sprint_dict = {}
issue_dict = {}
developer_dict = {}

print("Reading data...")
dataset = Utility.read_prep_dataset(repo)
sprint_dict['train'] = dataset[0]
sprint_dict['valid'] = dataset[1]
sprint_dict['test'] = dataset[2]
issue_dict['train'] = dataset[3]
issue_dict['valid'] = dataset[4]
issue_dict['test'] = dataset[5]
developer_dict['train'] = dataset[6]
developer_dict['valid'] = dataset[7]
developer_dict['test'] = dataset[8]

# add for regression
sprint_dict = Utility.replace_class_with_ratio(repo, sprint_dict)

print("shape of sprint train: ", sprint_dict['train'].shape)
print("shape of sprint valid: ", sprint_dict['valid'].shape)
print("shape of sprint test: ", sprint_dict['test'].shape)

print("Processing data...")
for data_set in ['train', 'valid', 'test']:
    issue_dict[data_set].drop(['text'], axis=1, inplace=True)
    issue_dict[data_set] = issue_dict[data_set].groupby('id').agg(pooling).reset_index()
    issue_dict[data_set].rename(columns=lambda x: 'i_' + x if x != 'id' else x, inplace=True)

    developer_dict[data_set].drop(['seq_action'], axis=1, inplace=True)
    developer_dict[data_set] = developer_dict[data_set].groupby('id').agg(pooling).reset_index()
    developer_dict[data_set].rename(columns=lambda x: 'd_' + x if x != 'id' else x, inplace=True)

    # join sprint, issue, developer using id
    sprint_dict[data_set].rename(columns=lambda x: 's_' + x if x not in ['id', 'productivity', 'quality_impact'] else x, inplace=True)
    sprint_dict[data_set] = sprint_dict[data_set].merge(issue_dict[data_set], on='id', how='left')
    sprint_dict[data_set] = sprint_dict[data_set].merge(developer_dict[data_set], on='id', how='left')
    # drop id
    sprint_dict[data_set].drop('id', axis=1, inplace=True)
    Utility.dump_prep_final_dataset(sprint_dict[data_set], "{}_{}_{}_{}".format(repo, approach_name, pooling, data_set))
    
print("shape of sprint train: ", sprint_dict['train'].shape)
print("shape of sprint valid: ", sprint_dict['valid'].shape)
print("shape of sprint test: ", sprint_dict['test'].shape)

print("Done for {}".format(repo))