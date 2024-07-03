import sys
import json
import pymysql
import os
import datetime
import operator
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo

def extractMostPre():
    """
    Extract the most preferred issue type of the developer
    """
   
    addCol = "ALTER TABLE `sprint_teammember_insight` ADD `most_prefer_type` varchar(255) NOT NULL AFTER `no_comment`;"
    try:
        cursor.execute(addCol)
        connection.commit()
    except:
        pass

    select = "SELECT board_id, sprint_id, username from sprint_teammember_insight WHERE most_prefer_type = '' and board_id >= '1696' and sprint_id >= '3938';"
    cursor.execute(select)
    result = cursor.fetchall()

    for row in result:
        maxType = ''
        boardID = row['board_id']
        sprintID = row['sprint_id']
        username = row['username']
        print(boardID, sprintID, username)

        typeD = dict()

        select = "SELECT DISTINCT(issue_key) as issue_keys FROM sprint_teammember_issue_new WHERE board_id = %s and sprint_id = %s and username = %s and exist_in_website = 1"
        inputPara = (
            boardID,
            sprintID,
            username
        )
        cursor.execute(select, inputPara)
        result2 = cursor.fetchall()

        for row2 in result2:
            select = "SELECT type FROM sprint_teammember_issue_feature_insight_new WHERE issue_key = %s"
            inputPara = (
                row2['issue_keys']
            )
            cursor.execute(select, inputPara)
            result3 = cursor.fetchall()
            for row3 in result3:
                if not str(row3['type']) in typeD.keys():
                    typeD[str(row3['type'])] = 1
                else:
                    typeD[str(row3['type'])] = typeD[str(row3['type'])] + 1

            maxType = max(typeD.items(), key = operator.itemgetter(1))[0] 

        print(maxType)
        update = "UPDATE sprint_teammember_insight si SET si.most_prefer_type = %s WHERE si.board_id = %s and si.sprint_id = %s and si.username = %s"
        inputPara =(
            maxType,
            boardID,
            sprintID,
            username
        )
        cursor.execute(update,inputPara)
        connection.commit()
        print("update {} {} {} into DB successfully".format(boardID, sprintID, username))


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
    
    extractMostPre()

    cursor.close()
    connection.close()
    print("DB Connection is closed")