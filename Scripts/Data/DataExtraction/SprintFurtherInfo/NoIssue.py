import sys
import json
import pymysql
import os
import datetime
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo

def extractTotalNoIssue():
    """
    Extract the total number of issues in the sprint
    """
    addCol = "ALTER TABLE `sprint_feature` ADD `no_issue` INT(11) NOT NULL;"
    try:
        cursor.execute(addCol)
        connection.commit()
    except:
        pass

    select = "SELECT \
        sfi.`board_id`,\
        sfi.`sprint_id`,\
        (SELECT COUNT(*) FROM sprint_issue_feature sif WHERE sif.board_id = sfi.board_id AND sif.sprint_id = sfi.sprint_id AND sif.addedDuringSprint = 0) as no_issue \
        FROM sprint_feature sfi"
    cursor.execute(select)
    result = cursor.fetchall()

    for row in result:
        update = "UPDATE sprint_feature SET no_issue = %s WHERE board_id = %s AND sprint_id = %s"
        inputPara = (
            row['no_issue'],
            row['board_id'],
            row['sprint_id']
        ) 
        cursor.execute(update, inputPara)
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

    extractTotalNoIssue()

    cursor.close()
    connection.close()
    print("DB Connection is closed")