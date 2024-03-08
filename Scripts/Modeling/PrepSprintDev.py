import sys
import gzip
import _pickle as pkl
import pandas as pd
import numpy as np
from Utility import Utility

try:
    repo = sys.argv[1]
    act_type = sys.argv[2]
    rnn_type = sys.argv[3]
    act_dim = sys.argv[4]
    pooling = sys.argv[5]
except:
    print("No argument")
    sys.exit()

approach_name = "sprintdev"

sprint_dict = {}
issue_dict = {}
developer_dict = {}

print("Reading act data...")
act_dataset = Utility.read_prep_act_dataset(repo, act_type, rnn_type, act_dim)
sprint_dict['train'] = act_dataset[0]
sprint_dict['valid'] = act_dataset[1]
sprint_dict['test'] = act_dataset[2]
developer_dict['train'] = act_dataset[6]
developer_dict['valid'] = act_dataset[7]
developer_dict['test'] = act_dataset[8]
print("shape of sprint train: ", sprint_dict['train'].shape)
print("shape of sprint valid: ", sprint_dict['valid'].shape)
print("shape of sprint test: ", sprint_dict['test'].shape)

# add for regression
sprint_dict = Utility.replace_class_with_ratio(repo, sprint_dict)

def explode_feats(df, col_name):
    exploded_df = pd.DataFrame(df[col_name].tolist(), index=df.index)
    df.drop(col_name, axis=1, inplace=True)
    return df.join(exploded_df.add_prefix(col_name + '_'))

print("Processing data...")
for data_set in ['train', 'valid', 'test']:
    developer_dict[data_set] = explode_feats(developer_dict[data_set], 'rnn_feats')
    developer_dict[data_set] = developer_dict[data_set].groupby('id').agg(pooling).reset_index()
    if data_set == 'train':
        developer_dict[data_set].fillna(developer_dict[data_set].mean(), inplace=True)
    else:
        developer_dict[data_set].fillna(developer_dict['train'].mean(), inplace=True)
    developer_dict[data_set].rename(columns=lambda x: 'd_' + x if x != 'id' else x, inplace=True)
    # join sprint, issue, developer using id
    sprint_dict[data_set].rename(columns=lambda x: 's_' + x if x not in ['id', 'productivity', 'quality_impact'] else x, inplace=True)
    sprint_dict[data_set] = sprint_dict[data_set].merge(developer_dict[data_set], on='id', how='left')
    # drop id
    sprint_dict[data_set].drop('id', axis=1, inplace=True)

    Utility.dump_prep_final_dataset(sprint_dict[data_set], "{}_{}_{}_{}_{}_{}_{}".format(repo, approach_name, act_type, rnn_type, act_dim, pooling, data_set))

print("shape of sprint train: ", sprint_dict['train'].shape)
print("shape of sprint valid: ", sprint_dict['valid'].shape)
print("shape of sprint test: ", sprint_dict['test'].shape)

print("Done for {}".format(repo))
