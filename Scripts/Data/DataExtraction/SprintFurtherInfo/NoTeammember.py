import sys
import json
import pymysql
import os
import datetime
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo

def extractTotalNoTeammember():
    """
    Extract the total number of team member in the sprint
    """
    addCol = "ALTER TABLE `sprint_feature` ADD `no_teammember` INT(11) NOT NULL AFTER `no_issue`;"
    try:
        cursor.execute(addCol)
        connection.commit()
    except:
        pass

    select = "SELECT \
        sfi.`board_id`,\
        sfi.`sprint_id`,\
        (SELECT COUNT(sif.assignee) FROM sprint_issue_feature sif WHERE sif.board_id = sfi.board_id AND sif.sprint_id = sfi.sprint_id AND sif.addedDuringSprint = 0) as no_teammember \
        FROM sprint_feature sfi"
    cursor.execute(select)
    result = cursor.fetchall()

    for row in result:
        update = "UPDATE sprint_feature SET no_teammember = %s WHERE board_id = %s AND sprint_id = %s"
        inputPara = (
            row['no_teammember'],
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

    extractTotalNoTeammember()

    cursor.close()
    connection.close()
    print("DB Connection is closed")