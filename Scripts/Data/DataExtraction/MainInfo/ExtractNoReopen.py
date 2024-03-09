import sys
import os
import requests
import json
import base64
import pymysql
import matplotlib.pyplot as plt
import numpy as np
import time
from collections import Counter
import operator
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Utility.RepoConfig as Repo
import Utility.DBConfig as DB


def collectReopenIss():

    print("Try to create new column [no_reopen] ...")
    # Add no_reopen column
    addColumn = "ALTER TABLE `sprint_feature` ADD `no_reopen` INT(11) NOT NULL;"
    try:
        cursor.execute(addColumn)
        connection.commit()
        print("Add no_reopen column successfully")
    except:
        print("This repo already has no_reopen column")

    time.sleep(3)

    print("Collect Reopen Issue from Sprint ...")

    select = "SELECT board_id, sprint_id, complete_date FROM sprint_feature"
    cursor.execute(select)
    result = cursor.fetchall()

    for row in result:
        currentBoardID = str(row['board_id'])
        currentSprintID = str(row['sprint_id'])
        currentcompleteDate = row['complete_date']
 
        selectissue = "SELECT issue_key FROM sprint_issue WHERE board_id = %s AND sprint_id = %s AND exist_in_website = 1 AND state = 'Completed'"        # Modified 8//6/2019 - update criteria
        inputPara = (
            currentBoardID,
            currentSprintID
        )
        cursor.execute(selectissue, inputPara)
        res = cursor.fetchall()
        countReopen = 0

        for issue in res:
            currentIssuekey = str(issue['issue_key'])
            selectChangelog = "SELECT CreatedDate, ToString FROM issue_changelog WHERE issue_key = %s"
            inputPara = (
                currentIssuekey
            )
            cursor.execute(selectChangelog, inputPara)
            resultCl = cursor.fetchall()

            for changelog in resultCl:
                CreatedDate = changelog['CreatedDate']
                try:
                    calTime = (currentcompleteDate-CreatedDate).total_seconds()
                except: 
                    continue
                if calTime <= 0 :
                    countReopen += 1
                    break

        updateNoReopen = "UPDATE sprint_feature SET no_reopen = %s WHERE board_id = %s AND sprint_id = %s"
        inputPara = (
            countReopen,
            currentBoardID,
            currentSprintID
        )
        cursor.execute(updateNoReopen, inputPara)
        connection.commit()

        print("Sprint {} on Board {} has {} reopened issue(s)".format(currentSprintID, currentBoardID, countReopen))

    print("\r\n---------------------- UPDATE NO_REOPEN COMPLETED for {}----------------------\r\n".format(repo.name.upper()))        


if __name__ == '__main__':
    repo = Repo.createRepo()
    db = DB.createDB(repo)

    connection = pymysql.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        passwd=db.pwd,
        database=db.repo.name,
        cursorclass=pymysql.cursors.DictCursor
    )

    cursor = connection.cursor()   

    collectReopenIss()

    cursor.close()
    connection.close()
    print("DB Connection is closed")