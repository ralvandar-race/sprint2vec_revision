import sys
import json
import pymysql
import os
import datetime
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Utility.DBConfig as DB
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo


def main(featureTable):
    selectMax = "SELECT MAX(`no_component`) as maxCom FROM " + featureTable
    try:
        cursor.execute(selectMax)
        res = cursor.fetchone()
    except:
        pass

    try:
        for c in range(0, int(res['maxCom'])):
            addCol = 'ALTER TABLE ' + featureTable + ' ADD `component_{}` VARCHAR(255)  NULL DEFAULT NULL;'.format(c+1)
            cursor.execute(addCol)
            connection.commit()
    except:
        pass

    selectIssue = "SELECT board_id, sprint_id, issue_key, no_component FROM " + featureTable
    cursor.execute(selectIssue)
    result = cursor.fetchall()
    for row in result:
        boardID = str(row['board_id'])
        sprintID = str(row['sprint_id'])
        issueKey = str(row['issue_key'])
        print("IssueKey: {}".format(issueKey))
        noComponent = int(row['no_component'])

        if not noComponent == 0:
            # read issue description file
            issue = Utility.loadIssueDescriptionJSON(issueKey, repo.name, db.folder)
            fields = issue['fields']
            componentList = fields['components']

            i = 1
            for component in componentList:
                update = 'UPDATE {} SET component_{} = %s WHERE board_id = %s AND sprint_id = %s AND issue_key = %s'.format(featureTable, i)
                inputPara = (
                    component['name'],
                    boardID,
                    sprintID,
                    issueKey
                )
                cursor.execute(update, inputPara)
                connection.commit()
                i = i + 1


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
    
    main(featureTable)
    
    cursor.close()
    connection.close()
    print("DB Connection is closed")