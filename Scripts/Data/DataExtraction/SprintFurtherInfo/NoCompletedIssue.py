import sys
import os
import requests
import json
import base64
import pymysql
import time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo
import Utility.DBConfig as DB



def extractCompletedIssue():
    """
    Extract the number of completed issue in each sprint
    """

    try:
        addColumn = "ALTER TABLE sprint_feature ADD no_completed_issue int(11)"
        cursor.execute(addColumn)
        connection.commit()
    except:
        pass

    select = "SELECT board_id, sprint_id FROM sprint_feature"      
    cursor.execute(select)
    result = cursor.fetchall()

    for row in result:
        currentBoardID = str(row['board_id'])
        currentSprintID = str(row['sprint_id'])
 
        selectCountCompleted = "SELECT COUNT(issue_key) as countCom FROM sprint_issue WHERE board_id = %s AND sprint_id = %s AND exist_in_website = 1 AND state = 'Completed'"        # Modified 8//6/2019 - update criteria
        inputPara = (
            currentBoardID,
            currentSprintID
        )
        cursor.execute(selectCountCompleted, inputPara)
        res = cursor.fetchone()
            
        updateNoCom = "UPDATE sprint_feature SET no_completed_issue = %s WHERE board_id = %s AND sprint_id = %s"
        inputPara = (
            res['countCom'],
            currentBoardID,
            currentSprintID
        )
        cursor.execute(updateNoCom, inputPara)
        connection.commit()



if __name__ == '__main__':
    try:
        host = sys.argv[1]
        port = sys.argv[2]
        user = sys.argv[3]
        pwd = sys.argv[4]
        repo = sys.argv[5]
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

    extractCompletedIssue()

    cursor.close()
    connection.close()
    print("DB Connection is closed")