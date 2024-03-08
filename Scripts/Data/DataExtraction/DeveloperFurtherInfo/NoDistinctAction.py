import sys
import json
import pymysql
import os
import datetime
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo

def main():

    create_table_sql = "CREATE TABLE IF NOT EXISTS `sprint_teammember_insight` SELECT * FROM `sprint_teammember`;"
    try:
        cursor.execute(create_table_sql)
        connection.commit()
    except:
        pass

    addCol = "ALTER TABLE `sprint_teammember_insight` ADD `no_distinct_action` INT(11) NOT NULL AFTER `username`;"
    try:
        cursor.execute(addCol)
        connection.commit()
    except:
        pass

    select = "SELECT board_id, sprint_id, username, count(distinct(action)) as no_action from sprint_teammember_issue_new group by board_id, sprint_id, username"
    cursor.execute(select)
    result = cursor.fetchall()

    for row in result:
        boardID = row['board_id']
        sprintID = row['sprint_id']
        username = row['username']
        noAction = row['no_action']

        update = "UPDATE sprint_teammember_insight si SET si.no_distinct_action = %s WHERE si.board_id = %s and si.sprint_id = %s and si.username = %s"
        inputPara =(
            noAction,
            boardID,
            sprintID,
            username
        )
        cursor.execute(update,inputPara)
        connection.commit()
        # print("update {} {} {} into DB successfully".format(boardID, sprintID, username))



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
    
    main()

    cursor.close()
    connection.close()
    print("DB Connection is closed")