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


# connect to the database
# <host_name>: the host name of the database
# <port>: the port of the database
# <username>: the username to connect to the database
# <password>: the password associated with the username
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

