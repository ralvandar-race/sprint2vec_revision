import sys
import json
import pymysql
import os
import datetime
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo


def countChange():
    """
    Count the number of changes in the priority of the issue
    """

    addCol = "ALTER TABLE `sprint_issue_feature_insight` ADD `change_priority` INT(11) NOT NULL AFTER `no_labels`;"
    try:
        cursor.execute(addCol)
        connection.commit()
    except:
        pass

    check = "SELECT start_date, board_id, sprint_id FROM sprint_feature_insight"
    cursor.execute(check)
    resultcheck = cursor.fetchall()

    for row in resultcheck:
        start_date = row['start_date']
        boardID = row['board_id']
        sprintID = row['sprint_id']

        select = "SELECT board_id, sprint_id, issue_key, (SELECT COUNT(idIssueChangeLog) FROM issue_changelog ic WHERE sif.issue_key = ic.issue_key AND Field = 'priority' AND ic.CreatedDate < %s) AS no_change_prior FROM sprint_issue_feature_insight sif WHERE board_id = %s AND sprint_id = %s"
        inputPara =(
            start_date,
            boardID,
            sprintID,
        )
        cursor.execute(select,inputPara)
        result = cursor.fetchall()

        for row in result:
            boardID = row['board_id']
            sprintID = row['sprint_id']
            issueKey = row['issue_key']
            no_change = row['no_change_prior']

            update = "UPDATE sprint_issue_feature_insight SET change_priority = %s WHERE board_id = %s AND sprint_id = %s AND issue_key = %s"
            inputPara =(
                no_change,
                boardID,
                sprintID,
                issueKey
            )
            cursor.execute(update,inputPara)
            connection.commit()
            # print("update {} {} into DB successfully".format(boardID, sprintID))



if __name__ == '__main__':
    try:
        repo = sys.argv[1]
    except:
        print("No argument")
        sys.exit()

    connection = pymysql.connect(
        host="localhost",
        user="root",
        passwd="whateverpasswordiwant",
        database=repo,
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connection.cursor()   

    countChange()
    cursor.close()
    connection.close()
    print("DB Connection is closed")