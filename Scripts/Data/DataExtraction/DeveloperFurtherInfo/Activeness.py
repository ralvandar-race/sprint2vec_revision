import sys
import json
import pymysql
import os
import datetime
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo

def extractNoIssue():
    """
    Extract the number of issues that the developer has done
    """
    addCol = "ALTER TABLE `sprint_teammember_insight` ADD `developer_activeness` INT(11) NOT NULL AFTER `no_distinct_action`;"
    try:
        cursor.execute(addCol)
        connection.commit()
    except:
        pass

    select = "SELECT board_id, sprint_id, username, exist_in_website, count(distinct(issue_key)) as no_issue from sprint_teammember_issue_new group by board_id, sprint_id, username HAVING exist_in_website = 1"
    cursor.execute(select)
    result = cursor.fetchall()

    for row in result:
        boardID = row['board_id']
        sprintID = row['sprint_id']
        username = row['username']
        noIssue = row['no_issue']

        update = "UPDATE sprint_teammember_insight si SET si.developer_activeness = %s WHERE si.board_id = %s and si.sprint_id = %s and si.username = %s"
        inputPara =(
            noIssue,
            boardID,
            sprintID,
            username
        )
        cursor.execute(update,inputPara)
        connection.commit()
        print("update {} {} {} into DB successfully".format(boardID, sprintID, username))


def extractTotal():
    """
    Extract the total number of issues that the team member has done
    """
    addCol = "ALTER TABLE `sprint_feature_insight` ADD `no_teammember_issue` INT(11) NULL DEFAULT 0"
    try:
        cursor.execute(addCol)
        connection.commit()
    except:
        pass
    select = "SELECT board_id, sprint_id, sum(developer_activeness) as dev_ex from sprint_teammember_insight group by board_id, sprint_id"
    cursor.execute(select)
    result = cursor.fetchall()

    for row in result:
        boardID = row['board_id']
        sprintID = row['sprint_id']
        devEx = row['dev_ex']

        update = "UPDATE sprint_feature_insight SET no_teammember_issue = %s WHERE board_id = %s and sprint_id = %s"
        inputPara =(
            devEx,
            boardID,
            sprintID
        )
        cursor.execute(update,inputPara)
        connection.commit()
        print("update {} {} into DB successfully".format(boardID, sprintID))

if __name__ == '__main__':
    try:
        repo = sys.argv[1]
        host = sys.argv[2]
        port = sys.argv[3]
        user = sys.argv[4]
        pwd = sys.argv[5]
    except:
        print("No argument")
        sys.exit()

    connection = pymysql.connect(
        host=host,
        port=int(port),
        user=user,
        password=pwd,
        db=repo,
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connection.cursor()   
    
    extractNoIssue()
    # extractTotal()

    cursor.close()
    connection.close()
    print("DB Connection is closed")