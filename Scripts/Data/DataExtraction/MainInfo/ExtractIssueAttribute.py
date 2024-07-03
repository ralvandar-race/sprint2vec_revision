import datetime
import json
import os
import sys
import time

import pymysql

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Utility.DBConfig as DB
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo

"""
# for normal issue
CREATE TABLE `sprint_issue_feature` (
  `board_id` int(11) NOT NULL,
  `sprint_id` int(11) NOT NULL,
  `issue_key` varchar(45) NOT NULL,
  `openeddate` datetime DEFAULT NULL COMMENT 'issue creation date',
  `addedDuringSprint` int(11) DEFAULT NULL,
  `summary` text,
  `description` text,
  `storypoint` double DEFAULT NULL,
  `type` varchar(45) DEFAULT NULL,
  `priority` varchar(45) DEFAULT NULL,
  `no_affectversion` int(11) DEFAULT NULL,
  `no_fixversion` int(11) DEFAULT NULL,
  `no_component` int(11) DEFAULT NULL,
  `reporter` varchar(45) DEFAULT NULL,
  `creator` varchar(45) DEFAULT NULL,
  `assignee` varchar(45) DEFAULT NULL,
  `status` varchar(45) DEFAULT NULL,
  `resolution` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`board_id`,`sprint_id`,`issue_key`),
  KEY `issue_key` (`issue_key`) USING BTREE,
  KEY `openeddate` (`openeddate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

# for issue from activity stream
CREATE TABLE `sprint_teammember_issue_feature` (
  `board_id` int(11) NOT NULL,
  `sprint_id` int(11) NOT NULL,
  `issue_key` varchar(45) NOT NULL,
  `openeddate` datetime DEFAULT NULL COMMENT 'issue creation date',
  `summary` text,
  `description` text,
  `storypoint` double DEFAULT NULL,
  `type` varchar(45) DEFAULT NULL,
  `priority` varchar(45) DEFAULT NULL,
  `no_affectversion` int(11) DEFAULT NULL,
  `no_fixversion` int(11) DEFAULT NULL,
  `no_component` int(11) DEFAULT NULL,
  `reporter` varchar(45) DEFAULT NULL,
  `creator` varchar(45) DEFAULT NULL,
  `assignee` varchar(45) DEFAULT NULL,
  `status` varchar(45) DEFAULT NULL,
  `resolution` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`board_id`,`sprint_id`,`issue_key`),
  KEY `issue_key` (`issue_key`) USING BTREE,
  KEY `openeddate` (`openeddate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""

def extractIssueFeature(choice, issueTable, featureTable):
    """
    Extract the issue feature from the issue table
    """
    print("Collect Issue Feature...")
    
    #------------- START Duplicate sprint_issue table to sprint_issue_feature table -------------#
    print("Start Inserting board_id, sprint_id, issue_key, and addedDuringSprint in {} table...".format(featureTable))
    if choice == 1:
        select = "SELECT board_id, sprint_id, issue_key, addedDuringSprint FROM sprint_issue WHERE NOT EXISTS (SELECT board_id, sprint_id, issue_key FROM sprint_issue_feature WHERE sprint_issue.board_id = sprint_issue_feature.board_id AND sprint_issue.sprint_id = sprint_issue_feature.sprint_id AND sprint_issue.issue_key = sprint_issue_feature.issue_key) AND exist_in_website = 1"
    else:
        select = "SELECT DISTINCT(issue_key), board_id, sprint_id FROM " + issueTable + " WHERE NOT EXISTS (SELECT board_id, sprint_id, issue_key FROM " + featureTable + " WHERE " + issueTable + ".board_id = " + featureTable + ".board_id AND " + issueTable + ".sprint_id = " + featureTable + ".sprint_id AND " + issueTable + ".issue_key = " + featureTable + ".issue_key) AND exist_in_website = 1"

    cursor.execute(select)
    result = cursor.fetchall()
    
    countIssue = 0
    for row in result:
        boardID = row['board_id']
        sprintID = row['sprint_id']
        issueKey = row['issue_key']

        if choice == 1:
            addedDuringSprint = row['addedDuringSprint']
            insert = "INSERT INTO sprint_issue_feature(board_id, sprint_id, issue_key, addedDuringSprint) VALUES(%s, %s, %s, %s)"
            inputPara = (
                boardID,
                sprintID,
                issueKey,
                addedDuringSprint
            )
        else:
            insert = "INSERT INTO " + featureTable + " (board_id, sprint_id, issue_key) VALUES(%s, %s, %s)"
            inputPara = (
                    boardID,
                    sprintID,
                    issueKey
                )

        cursor.execute(insert, inputPara)
        connection.commit()
    #------------- END Duplicate sprint_issue table to sprint_issue_feature table -------------#

        
    #------------- START update sprint_issue_feature table -------------#
    print("Start updating sprint_feature...")
    select = "SELECT board_id, sprint_id, issue_key FROM " + featureTable
    cursor.execute(select)
    result = cursor.fetchall()
    for row in result:
        boardID = str(row['board_id'])
        sprintID = str(row['sprint_id'])
        issueKey = str(row['issue_key'])
        print("IssueKey: {}".format(issueKey))

        # read issue description file
        issue = Utility.loadIssueDescriptionJSON(issueKey, repo.name, db.folder)

        try:
            key = issue['key']
        except:
            print("The issue [{}] doesn't exist in Website".format(key))
            continue

        fields = issue['fields']
        # 2016-11-14T21:07:31.000-0600
        datetime_code = '%Y-%m-%dT%H:%M:%S.%f%z'
        openDate = datetime.datetime.strptime(fields['created'], datetime_code)
        summary = fields['summary']
        description = fields['description']

        try:
            storypoint = fields["customfield_" + repo.storypoint1]
        except:
            storypoint = None
        
        # for JIRA
        if repo.name == "jira":
            if storypoint == None:
                try:
                    storypoint = fields["customfield_" + repo.storypoint2]
                except:
                    storypoint = None
                if storypoint == None:
                    try:
                        storypoint = fields["customfield_" + repo.storypoint3]
                    except:
                        storypoint = None

        issueType = fields['issuetype']['name']
        try:
            priority = fields['priority']['name']
        except:
            priority = None
        try:
            noAffectVersion = len(fields['versions'])
        except:
            noAffectVersion = 0
        try:
            noFixVersion = len(fields['fixVersions'])
        except:
            noFixVersion = 0

        try:
            noComponent = len(fields['components'])
        except:
            noComponent = 0

        try:
            reporter = fields['reporter']['name']
        except:
            reporter = None

        try:
            creator = fields['creator']['name']
        except:
            creator = None

        try:
            assignee = fields['assignee']['name']
        except:
            assignee = None

        status = fields['status']['name']
        
        try:
            resolution = fields['resolution']['name']
        except:
            resolution = None

        update = "UPDATE " + featureTable + " SET openeddate = %s, summary = %s, description = %s, storypoint = %s, type = %s, priority = %s, no_affectversion = %s, no_fixversion = %s, no_component = %s, reporter = %s, creator = %s, assignee = %s, status = %s, resolution = %s WHERE board_id = %s AND sprint_id = %s AND issue_key = %s"
        inputPara = (
            openDate,
            summary,
            description,
            storypoint,
            issueType,
            priority,
            noAffectVersion,
            noFixVersion,
            noComponent,
            reporter,
            creator,
            assignee,
            status,
            resolution,
            boardID,
            sprintID,
            issueKey
        )

        cursor.execute(update, inputPara)
        connection.commit()

        #------------- END update sprint_issue_feature table -------------#

        countIssue += 1

        print("Feature of Issue '{}' in sprint {} on board {} is collected\n".format(issueKey, sprintID, boardID))

    print("Total Issue: {}".format(countIssue))
    print("-------------COMPLETED {}-------------".format(repo.name.upper()))

        


if __name__ == '__main__':
    repo = Repo.createRepo()
    db = DB.createDB(repo)

    choice = int(input("Please choose the choice\n[1]Normal Issue\n[2]Issue from activity stream\n:"))
    # normal issue
    if choice == 1:
        issueTable = "sprint_issue"
        featureTable = "sprint_issue_feature"
    # issue from activity stream
    else:
        issueTable = "sprint_teammember_issue_new"
        featureTable = "sprint_teammember_issue_feature_new"

    connection = pymysql.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        passwd=db.pwd,
        database=db.repo.name,
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connection.cursor()   
    
    extractIssueFeature(choice, issueTable, featureTable)

    cursor.close()
    connection.close()
    print("DB Connection is closed")
