''' 
Script to extract assignee of Sprint
'''

import sys
import json
import os
import pymysql
import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Utility.DBConfig as DB
import Utility.RepoConfig as Repo

"""
CREATE TABLE `sprint_teammember` (
  `board_id` int(11) NOT NULL,
  `sprint_id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `sprint_teammember`
  ADD PRIMARY KEY (`board_id`,`sprint_id`,`username`) USING BTREE;
COMMIT;
"""

def extractSprintMember():
    print("Collect Sprint member...")
    
    # Modified 18/8/2019 - focus on only CLOSED sprint
    select = "SELECT board_id, sprint_id FROM sprint_feature"
    cursor.execute(select)
    result = cursor.fetchall()

    for sprint in result:
        boardID = str(sprint['board_id'])
        sprintID = str(sprint['sprint_id'])

        select = "SELECT issue_key FROM sprint_issue WHERE board_id = %s AND sprint_id = %s"
        inputPara = (
            boardID,
            sprintID
        )
        cursor.execute(select, inputPara)
        result = cursor.fetchall()
        
        for issue in result:
            issueKey = str(issue['issue_key'])
            select = "SELECT assignee FROM sprint_issue_feature WHERE board_id = %s AND sprint_id = %s AND issue_key = %s AND assignee IS NOT NULL"
            inputPara = (
                boardID,
                sprintID,
                issueKey
            )
            cursor.execute(select, inputPara)
            result = cursor.fetchall()

            for item in result:
                assignee = str(item['assignee'])

                insertAssignee = "INSERT INTO sprint_teammember(board_id, sprint_id, username) VALUES(%s, %s, %s)"
                inputPara = (
                    boardID,
                    sprintID,
                    assignee
                )
                # don't insert dup username for the same sprint
                try:
                    cursor.execute(insertAssignee, inputPara)
                    connection.commit()
                except:
                    continue

                print("Issue {} in Sprint {} on Board {} has {} as assignee".format(issueKey, sprintID, boardID, assignee))
        
    print("\r\n---------------------- INSERT ASSIGNEE NAME COMPLETED for {}----------------------\r\n".format(repo.name.upper())) 


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
    
    extractSprintMember()

    cursor.close()
    connection.close()
    print("DB Connection is closed")