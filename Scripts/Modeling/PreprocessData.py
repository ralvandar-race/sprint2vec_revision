import pandas as pd
import sys
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
import gzip
# import pickle5 as pkl
import _pickle as pkl

from Utility import Utility

try:
    repo = sys.argv[1]
except:
    print("No argument")
    sys.exit()

def oneHotEncode(dataframe):
    ohEncoders = {}
    dfOneHots = []
    droppedColumns = []
    for column in dataframe.columns:
        if column in ['type', 'priority', 'most_prefer_type']:
            oh = OneHotEncoder()
            ohEncoders[column] = oh
            oneHot = oh.fit_transform(
                dataframe[column].values.reshape(-1,1)).toarray()
            dfOneHots.append(pd.DataFrame(
                oneHot, 
                columns=[f'{column}_{cat}' for cat in oh.categories_[0]]))
            droppedColumns.append(column)
    dataframe = pd.concat([dataframe, *dfOneHots], axis=1)
    dataframe = dataframe.drop(droppedColumns, axis=1)
    return dataframe

# read data
print("Reading raw data...")
sprint_df, issue_df, developer_df = Utility.read_raw_dataset(repo)

sprint_df.insert(0, 'id', range(1, len(sprint_df) + 1))

print("Preprocessing issue data...")
# replace board_id and sprint_id with id in sprint_df
issue_df = issue_df.merge(sprint_df[['id', 'board_id', 'sprint_id']], on=['board_id', 'sprint_id'])
# concate summary and description
issue_df['summary'] = issue_df['summary'].fillna('')
issue_df['description'] = issue_df['description'].fillna('')
issue_df['text'] = issue_df['summary'] + ' ' + issue_df['description']
# drop board_id, sprint_id, issue_key, storypoint
issue_df = issue_df.drop(['board_id', 'sprint_id', 'issue_key', 'storypoint', 'summary', 'description'], axis=1)
# priority jira
imp = SimpleImputer(missing_values=np.nan, strategy='most_frequent')
issue_df['priority'] = imp.fit_transform(issue_df[['priority']])
# move id to the first column
cols = list(issue_df)
cols.insert(0, cols.pop(cols.index('id')))
issue_df = issue_df.loc[:, cols]
issue_df = oneHotEncode(issue_df)

print("Preprocessing developer data...")
# replace board_id and sprint_id with id in sprint_df
developer_df = developer_df.merge(sprint_df[['id', 'board_id', 'sprint_id']], on=['board_id', 'sprint_id'])
# drop board_id, sprint_id
developer_df = developer_df.drop(['board_id', 'sprint_id'], axis=1)
# move id to the first column
cols = list(developer_df)
cols.insert(0, cols.pop(cols.index('id')))
developer_df = developer_df.loc[:, cols]
imp = SimpleImputer(missing_values=np.nan, strategy='constant', fill_value='Na')
developer_df['most_prefer_type'] = imp.fit_transform(developer_df[['most_prefer_type']])
developer_df['seq_action'] = developer_df['seq_action'].fillna('')
developer_df = oneHotEncode(developer_df)

print("Preprocessing sprint labels...")
label_dict = {
    "productivity": {"low": 1, "balanced": 2, "high": 3},
    "quality_impact": {"no": 1, "minor": 2, "moderate": 3, "major": 4}
    }
sprint_df.replace(label_dict, inplace=True)
sprint_df.drop(columns=['board_id', 'sprint_id', 'complete_ratio', 'reopen_ratio'], inplace=True)

path_3sets = '3sets/{}_3sets.tsv'.format(repo)
with open(path_3sets, 'r') as f:
    lines = f.readlines()
    sprint_train_df = sprint_df[sprint_df['id'].isin([int(line.split('\t')[0]) for line in lines if line.split('\t')[3].strip() == 'train'])]
    sprint_valid_df = sprint_df[sprint_df['id'].isin([int(line.split('\t')[0]) for line in lines if line.split('\t')[3].strip() == 'valid'])]
    sprint_test_df = sprint_df[sprint_df['id'].isin([int(line.split('\t')[0]) for line in lines if line.split('\t')[3].strip() == 'test'])]
    issue_train_df = issue_df[issue_df['id'].isin([int(line.split('\t')[0]) for line in lines if line.split('\t')[3].strip() == 'train'])]
    issue_valid_df = issue_df[issue_df['id'].isin([int(line.split('\t')[0]) for line in lines if line.split('\t')[3].strip() == 'valid'])]
    issue_test_df = issue_df[issue_df['id'].isin([int(line.split('\t')[0]) for line in lines if line.split('\t')[3].strip() == 'test'])]
    developer_train_df = developer_df[developer_df['id'].isin([int(line.split('\t')[0]) for line in lines if line.split('\t')[3].strip() == 'train'])]
    developer_valid_df = developer_df[developer_df['id'].isin([int(line.split('\t')[0]) for line in lines if line.split('\t')[3].strip() == 'valid'])]
    developer_test_df = developer_df[developer_df['id'].isin([int(line.split('\t')[0]) for line in lines if line.split('\t')[3].strip() == 'test'])]

print("shape of sprint_train_df: ", sprint_train_df.shape)
print("shape of sprint_valid_df: ", sprint_valid_df.shape)
print("shape of sprint_test_df: ", sprint_test_df.shape)
print("shape of issue_train_df: ", issue_train_df.shape)
print("shape of issue_valid_df: ", issue_valid_df.shape)
print("shape of issue_test_df: ", issue_test_df.shape)
print("shape of developer_train_df: ", developer_train_df.shape)
print("shape of developer_valid_df: ", developer_valid_df.shape)
print("shape of developer_test_df: ", developer_test_df.shape)

print("Dumping data...")
Utility.dump_prep_dataset(repo,
    (sprint_train_df, sprint_valid_df, sprint_test_df,
    issue_train_df, issue_valid_df, issue_test_df, 
    developer_train_df, developer_valid_df, developer_test_df)
)

print("Done for {}".format(repo))