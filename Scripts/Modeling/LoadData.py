import sys
import os
import pymysql
import csv
import pandas as pd
# import pickle5 as pkl
import _pickle as pkl
from collections import Counter
import operator

import matplotlib.pyplot as plt
import numpy as np

try:
    repo = sys.argv[1]
except:
    print("No argument")
    sys.exit()

if not os.path.exists('Data'):
    os.makedirs('Data')

selectSprintDeliver = "SELECT \
    sfi.`board_id`, \
    sfi.`sprint_id`, \
    sfi.`plan_duration`, \
    sfi.`no_issue`, \
    sfi.`no_teammember`, \
    sfi.`complete_ratio`, \
    sfi.`reopen_ratio`\
    FROM sprint_feature sfi \
    WHERE EXISTS (SELECT * FROM sprint_issue si WHERE sfi.board_id = si.board_id AND sfi.sprint_id = si.sprint_id AND si.addedDuringSprint = 0 AND si.exist_in_website = 1) \
    AND NOT sfi.complete_ratio = 0\
    ORDER BY sfi.`start_date` ASC;" 
    
selectIssueDeliver = "SELECT \
    sif.board_id, \
    sif.sprint_id, \
    sif.issue_key, \
    sif.storypoint, \
    sif.summary, \
    sif.description, \
    sif.type, \
    sif.priority, \
    sif.no_component, \
    sif.fog_index, \
    sif.no_comments, \
    sif.no_change_description, \
    sif.no_change_priority, \
    sif.no_change_fix \
    FROM sprint_issue_feature_insight sif \
    JOIN sprint_issue_feature si \
    ON si.board_id = sif.board_id \
    AND si.sprint_id = sif.sprint_id \
    AND si.issue_key = sif.issue_key \
    JOIN sprint_feature sf \
    ON sif.board_id = sf.board_id \
    AND sif.sprint_id = sf.sprint_id \
    WHERE si.addedDuringSprint = 0 \
    AND NOT sf.achievement = 'non-delivered'\
    ORDER BY sf.start_date ASC ;"

selectDeveloperDeliver = "SELECT sti.`board_id`, sti.`sprint_id`, sti.`no_distinct_action`, sti.`developer_activeness`, sti.`no_comment`, sti.`most_prefer_type`, sti.`seq_action` \
    FROM `sprint_teammember_insight` sti \
    JOIN sprint_feature sf \
    ON sti.board_id = sf.board_id \
    AND sti.sprint_id = sf.sprint_id \
    JOIN sprint_feature sfi \
    ON sti.board_id = sfi.board_id \
    AND sti.sprint_id = sfi.sprint_id \
    WHERE EXISTS (SELECT * FROM sprint_issue si WHERE sti.board_id = si.board_id AND sti.sprint_id = si.sprint_id AND si.addedDuringSprint = 0 AND si.exist_in_website = 1) \
    AND NOT sfi.achievement = 'non-delivered'\
    ORDER BY sf.start_date ASC "


connection = pymysql.connect(
    host="<host_name>",
    port="<port>",
    user="<username>",
    passwd="<password>",
    database=repo,
    cursorclass=pymysql.cursors.DictCursor
)

cursor = connection.cursor()
print("PROJECT: {}".format(repo))
cursor.execute(selectSprintDeliver)
sprintResult = cursor.fetchall()

sprint_df = pd.DataFrame(sprintResult)
# remove outliers for apache [668 233 233]
if repo == 'apache':
    sprint_df.drop(sprint_df[sprint_df.no_issue > 100].index, inplace=True)

headers = [col[0] for col in cursor.description]

complete_ratio = sprint_df['complete_ratio'].tolist()
complete_ratio.sort()
reopen_ratio = sprint_df['reopen_ratio'].tolist()
reopen_ratio.sort()

first_complete_index = round(0.33 * len(complete_ratio))
second_complete_index = round(0.66 * len(complete_ratio))
first_complete_threshold = complete_ratio[first_complete_index - 1]
second_complete_threshold = complete_ratio[second_complete_index - 1]
print("First Complete Threshold: {}".format(first_complete_threshold))
print("Second Complete Threshold: {}".format(second_complete_threshold))

first_reopen_index = round(0.20 * len(reopen_ratio))
second_reopen_index = round(0.40 * len(reopen_ratio))
third_reopen_index = round(0.60 * len(reopen_ratio))
first_reopen_threshold = reopen_ratio[first_reopen_index - 1]
second_reopen_threshold = reopen_ratio[second_reopen_index - 1]
third_reopen_threshold = reopen_ratio[third_reopen_index - 1]
print("First Reopen Threshold: {}".format(first_reopen_threshold))
print("Second Reopen Threshold: {}".format(second_reopen_threshold))
print("Third Reopen Threshold: {}".format(third_reopen_threshold))

productivity = []
quality_impact = []
for index, row in sprint_df.iterrows():
    if row['complete_ratio'] < first_complete_threshold:
        productivity.append('low')
    elif row['complete_ratio'] > second_complete_threshold:
        productivity.append('high')
    else:
        productivity.append('balanced')
    if row['reopen_ratio'] <= first_reopen_threshold:
        quality_impact.append('no')
    elif row['reopen_ratio'] > first_reopen_threshold and row['reopen_ratio'] <= second_reopen_threshold:
        quality_impact.append('minor')
    elif row['reopen_ratio'] > second_reopen_threshold and row['reopen_ratio'] <= third_reopen_threshold:
        quality_impact.append('moderate')
    else:
        quality_impact.append('major')

sprint_df['productivity'] = productivity
sprint_df['quality_impact'] = quality_impact
sprint_df.head()

# save threshold as text file
print("save threshold ...")
with open('Data/{}_threshold.txt'.format(repo), 'w') as f:
    f.write('First Prod Threshold: {}\n'.format(first_complete_threshold))
    f.write('Second Prod Threshold: {}\n'.format(second_complete_threshold))
    f.write('First Qual Threshold: {}\n'.format(first_reopen_threshold))
    f.write('Second Qual Threshold: {}\n'.format(second_reopen_threshold))
    f.write('Third Qual Threshold: {}\n'.format(third_reopen_threshold))

print("save data ...")
# save sprint_df as csv file
sprint_df.to_csv('Data/{}_sprint.csv'.format(repo), index=False)
print("\nNo. of sprint: {}".format(len(sprint_df)))

# save issue_df as csv file
cursor.execute(selectIssueDeliver)
issueResult = cursor.fetchall()
issue_df = pd.DataFrame(issueResult)
issue_df.to_csv('Data/{}_issue.csv'.format(repo), index=False)
print("No. of issue: {}".format(len(issue_df)))

# save developer_df as csv file
cursor.execute(selectDeveloperDeliver)
developerResult = cursor.fetchall()
developer_df = pd.DataFrame(developerResult)
developer_df.to_csv('Data/{}_developer.csv'.format(repo), index=False)
print("No. of developer: {}".format(len(developer_df)))

print("Done for {}".format(repo))

