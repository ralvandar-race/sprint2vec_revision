import sys
import gzip
import _pickle as pkl
import pandas as pd
import numpy as np
from Utility import Utility

try:
    repo = sys.argv[1]
    text_type = sys.argv[2]
    pooling = sys.argv[3]
except:
    print("No argument")
    sys.exit()

approach_name = "sprintissue"

sprint_dict = {}
issue_dict = {}
developer_dict = {}

print("Reading text data...")
text_dataset = Utility.read_prep_text_dataset(repo, text_type)
sprint_dict['train'] = text_dataset[0]
sprint_dict['valid'] = text_dataset[1]
sprint_dict['test'] = text_dataset[2]
issue_dict['train'] = text_dataset[3]
issue_dict['valid'] = text_dataset[4]
issue_dict['test'] = text_dataset[5]

# add for regression
sprint_dict = Utility.replace_class_with_ratio(repo, sprint_dict)

def explode_feats(df, col_name):
    exploded_df = pd.DataFrame(df[col_name].tolist(), index=df.index)
    df.drop(col_name, axis=1, inplace=True)
    return df.join(exploded_df.add_prefix(col_name + '_'))

print("Processing data...")
for data_set in ['train', 'valid', 'test']:
    issue_dict[data_set] = explode_feats(issue_dict[data_set], 'text')
    issue_dict[data_set] = issue_dict[data_set].groupby('id').agg(pooling).reset_index()
    issue_dict[data_set].rename(columns=lambda x: 'i_' + x if x != 'id' else x, inplace=True)
    # join sprint, issue, developer using id
    sprint_dict[data_set].rename(columns=lambda x: 's_' + x if x not in ['id', 'productivity', 'quality_impact'] else x, inplace=True)
    sprint_dict[data_set] = sprint_dict[data_set].merge(issue_dict[data_set], on='id', how='left')
    # drop id
    sprint_dict[data_set].drop('id', axis=1, inplace=True)
    Utility.dump_prep_final_dataset(sprint_dict[data_set], "{}_{}_{}_{}_{}".format(repo, approach_name, text_type, pooling, data_set))
    
print("shape of sprint train: ", sprint_dict['train'].shape)
print("shape of sprint valid: ", sprint_dict['valid'].shape)
print("shape of sprint test: ", sprint_dict['test'].shape)

print("Done for {}".format(repo))
