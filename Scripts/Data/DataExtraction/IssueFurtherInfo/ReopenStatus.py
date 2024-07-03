import sys
import os
import requests
import json
import base64
import pymysql
import time
from collections import Counter
import operator
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo


def collectReopenIss():
    """
    Collect the number of reopen issue in the sprint
    """

    print("Try to create new column [no_reopen] ...")
    # Add no_reopen column
    try:
        addColumn = "ALTER TABLE sprint_issue_feature_insight ADD `reopen_status` TINYINT NOT NULL AFTER `no_comment`"
        cursor.execute(addColumn)
        connection.commit()
        print("Add no_reopen column successfully")
    except:
        print("This repo already has no_reopen column")

    print("Collect No Reopen Issue in Issue level")

    select = "SELECT board_id, sprint_id, issue_key FROM sprint_issue_feature_insight"
    cursor.execute(select)
    result = cursor.fetchall() 

    for row in result:
        countReOp = 0
        currentBoardID = str(row['board_id'])
        currentSprintID = str(row['sprint_id'])   
        currentIssueKey = str(row['issue_key'])
 
        selectissue = "SELECT state FROM sprint_issue WHERE board_id = %s AND sprint_id = %s AND issue_key = %s AND exist_in_website = 1"
        inputPara = (
            currentBoardID,
            currentSprintID,
            currentIssueKey
        )
        cursor.execute(selectissue, inputPara)
        res = cursor.fetchone()

        if res['state'] == 'Completed':

            selectComple = "SELECT complete_date FROM sprint_feature WHERE board_id = %s AND sprint_id = %s"    
            inputPara = (
                currentBoardID,
                currentSprintID
            )   
            cursor.execute(selectComple, inputPara) 
            resultComple = cursor.fetchone()
            currentcompleteDate = resultComple['complete_date']  

            selectChangelog = "SELECT CreatedDate FROM issue_changelog WHERE issue_key = %s"
            inputPara = (
                currentIssueKey
            )
            cursor.execute(selectChangelog, inputPara)
            resultCl = cursor.fetchall()

            for changelog in resultCl:
                CreatedDate = changelog['CreatedDate']
                # Modified 8//6/2019 - update criteria
                try:
                    calTime = (currentcompleteDate-CreatedDate).days
                except: 
                    continue
                if calTime <= 0 :
                    countReOp += 1
                    break

        updateNoReopen = "UPDATE sprint_issue_feature_insight SET reopen_status = %s WHERE board_id = %s AND sprint_id = %s AND issue_key = %s"
        inputPara = (
            countReOp,
            currentBoardID,
            currentSprintID,
            currentIssueKey
        )
        cursor.execute(updateNoReopen, inputPara)
        connection.commit()

        # print("Issue {} has {} no of being reopened".format(currentIssueKey, countReOp))

    print("\r\n---------------------- UPDATE NO_REOPEN COMPLETED for {}----------------------\r\n".format(repo.upper()))        


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

    collectReopenIss()

    cursor.close()
    connection.close()
    print("DB Connection is closed")