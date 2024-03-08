import sys
import json
import pymysql
import os
import datetime
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo

def countComment():

    addCol = "ALTER TABLE `sprint_issue_feature_insight` ADD `no_comment` TINYINT NOT NULL AFTER `change_priority`;"
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

        select = "SELECT board_id, sprint_id, issue_key, (SELECT count(comment_id) FROM sprint_issue_comment sic WHERE sif.board_id = sic.board_id AND sif.sprint_id = sic.sprint_id AND sif.issue_key = sic.issue_key AND sic.createddate <= %s) AS no_comment FROM sprint_issue_feature sif WHERE board_id = %s AND sprint_id = %s"
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
            noComment = row['no_comment']

            update = "UPDATE sprint_issue_feature_insight SET no_comment = %s WHERE board_id = %s and sprint_id = %s and issue_key = %s"
            inputPara =(
                noComment,
                boardID,
                sprintID,
                issueKey
            )
            cursor.execute(update,inputPara)
            connection.commit()
            # print("update {} {} {} into DB successfully".format(boardID, sprintID, issueKey))



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
    
    countComment()

    cursor.close()
    connection.close()
    print("DB Connection is closed")