import sys
import gzip
import _pickle as pkl
import pandas as pd
import numpy as np
from Utility import Utility
from Utility.Utility import read_prep_dataset


try:
    repo = sys.argv[1]
except:
    print("No argument")
    sys.exit()

approach_name = "existing"

# read data
print("Reading data...")
(sprint_train_df, sprint_valid_df, sprint_test_df,
issue_train_df, issue_valid_df, issue_test_df, 
developer_train_df, developer_valid_df, developer_test_df) = read_prep_dataset(repo)

num_col = ['no_component', 'fog_index', 'no_comments', 'no_change_description', 'no_change_priority', 'no_change_fix']
issue_dict = {'train': issue_train_df, 'valid': issue_valid_df, 'test': issue_test_df}
sprint_dict = {'train': sprint_train_df, 'valid': sprint_valid_df, 'test': sprint_test_df}
sprint_dict = Utility.replace_class_with_ratio(repo, sprint_dict)
final_data_dict = {}

for data_set in issue_dict.keys():
    issue_dict[data_set].drop(['text'], axis=1, inplace=True)
    num_issue_df = issue_dict[data_set][['id'] + num_col]
    num_issue_df = num_issue_df.groupby('id').agg(['mean', 'min', 'max', np.median, np.std, np.var, np.ptp]).reset_index()
    new_col = []
    for col in num_col:
        for stat in ['mean', 'min', 'max', 'median', 'std', 'var', 'ptp']:
            new_col.append(col + '_' + stat)
    num_issue_df.columns = ['id'] + new_col
    if data_set == 'train':
        num_issue_df.fillna(num_issue_df.mean(), inplace=True)
    else:
        num_issue_df.fillna(final_data_dict['train'].mean(), inplace=True)
    cat_issue_df = issue_dict[data_set].drop(num_col, axis=1)
    cat_issue_df = cat_issue_df.groupby('id').agg(['sum']).reset_index()
    cat_issue_df.columns = cat_issue_df.columns.droplevel(1)
    prep_issue_df = pd.merge(num_issue_df, cat_issue_df, on='id')
    sprint_df = pd.merge(sprint_dict[data_set], prep_issue_df, on='id')
    sprint_df.drop(['id'], axis=1, inplace=True)
    final_data_dict[data_set] = sprint_df
    Utility.dump_prep_final_dataset(final_data_dict[data_set], "{}_{}_{}".format(repo, approach_name, data_set))

print("Done for existing features")