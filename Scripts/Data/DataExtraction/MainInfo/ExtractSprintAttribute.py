import datetime
import json
import os
import sys

import pymysql

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Utility.DBConfig as DB
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo

# CREATE TABLE `sprint_feature` (
#   `board_id` int(11) NOT NULL,
#   `sprint_id` int(11) NOT NULL,
#   `sequence` int(11) NULL,
#   `sprint_name` varchar(100) DEFAULT NULL,
#   `state` varchar(45) DEFAULT NULL,
#   `start_date` datetime DEFAULT NULL,
#   `end_date` datetime DEFAULT NULL,
#   `complete_date` datetime DEFAULT NULL,
#   `lastUserToClose` varchar(100) DEFAULT NULL COMMENT 'the whole tag <a> that contain a username',
#   `plan_duration` int(11) DEFAULT NULL COMMENT 'enddate - startdate',
#   `actual_duration` int(11) DEFAULT NULL COMMENT 'completedate - startdate',
#   `delay_duration` int(11) DEFAULT NULL COMMENT 'completedate - enddate: positive=delay'
#   PRIMARY KEY (`board_id`,`sprint_id`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8;


def extractSprintFeature():
    print("Collect Sprint Feature...")
    
    #------------- START Duplicate sprint table to sprint_feature table -------------#
    print("Start Inserting board_id and sprint_id...")
    select = "SELECT distinct board_id, sprint_id FROM sprint WHERE NOT EXISTS (SELECT board_id, sprint_id FROM sprint_feature WHERE sprint.board_id = sprint_feature.board_id AND sprint.sprint_id = sprint_feature.sprint_id)"
    cursor.execute(select)
    result = cursor.fetchall()
    countSprint = 0
    for row in result:
        boardID = row['board_id']
        sprintID = row['sprint_id']

        insertBoardIdSprintId = "INSERT INTO sprint_feature(board_id, sprint_id) VALUES(%s, %s)"
        inputPara = (
            boardID,
            sprintID
        )

        cursor.execute(insertBoardIdSprintId, inputPara)
        connection.commit()
    #------------- END Duplicate sprint table to sprint_feature table -------------#


    #------------- START update sprint_feature table -------------#
    print("Start updating board_id and sprint_id...")
    select = "SELECT board_id, sprint_id FROM sprint_feature"
    cursor.execute(select)
    result = cursor.fetchall()
    for row in result:
        boardID = str(row['board_id'])
        sprintID = str(row['sprint_id'])
        print("BID: " + boardID, "SID: " + sprintID)

        # read Sprint file
        sprint = Utility.loadSprintJSON(boardID, sprintID, repo.name, db.folder)

        try:
            feat = sprint['sprint']
        except Exception as e:
            print("ERROR: {} [boardID: {}, sprintID: {}]".format(e, boardID, sprintID))
            continue

        sequence = feat['sequence']
        name = feat['name']

        # collect the feature for only CLOSED sprint
        state = feat['state']
        if state != "CLOSED":
            delete = "DELETE FROM `sprint_feature` WHERE board_id = %s AND sprint_id = %s"
            inputPara = (
                int(boardID),
                int(sprintID)
            )
            cursor.execute(delete, inputPara)
            connection.commit()
            continue

        # eg. 08/Sep/14 6:00 PM
        dateTimeCode = '%d/%b/%y %I:%M %p'
        if repo.name == 'jira':
            # eg. 08/Sep/2014 6:00 PM
            dateTimeCode = '%d/%b/%Y %I:%M %p'

        # check whether it is None
        try:
            startDate = datetime.datetime.strptime(feat['startDate'], dateTimeCode)
        except Exception as e:
            startDate = None
        try:
            endDate = datetime.datetime.strptime(feat['endDate'], dateTimeCode)
        except Exception as e:
            endDate = None
        try:
            completeDate = datetime.datetime.strptime(feat['completeDate'], dateTimeCode)
        except Exception as e:
            completeDate = None
        
        # if there is no lastUser
        try:
            lastUser = sprint['lastUserToClose']
        except Exception as e:
            lastUser = None

        # compute duration
        if startDate != None and startDate != "None":
            planDuration = int((endDate - startDate).total_seconds() // 3600)
            if completeDate != None and completeDate != "None":
                actualDuration = int((completeDate - startDate).total_seconds() // 3600)
                delayDuration = int((completeDate - endDate).total_seconds() // 3600) # positive=delay
            else:
                actualDuration = None
                delayDuration = None
        else:
            planDuration = None
            actualDuration = None
            delayDuration = None

        insertSprintFeat = "UPDATE sprint_feature SET sequence = %s, sprint_name = %s, state = %s, start_date = %s, end_date = %s, complete_date = %s, lastUserToClose = %s, plan_duration = %s, actual_duration = %s, delay_duration = %s WHERE board_id = %s AND sprint_id = %s"
        inputPara = (
            sequence,
            name,
            state,
            startDate,
            endDate,
            completeDate,
            lastUser,
            planDuration,
            actualDuration,
            delayDuration,
            boardID,
            sprintID
        )

        cursor.execute(insertSprintFeat, inputPara)
        connection.commit()
        #------------- END update sprint_feature table -------------#

        countSprint += 1
    
        print("Feature of Sprint '{}' on board {} is collected\n".format(sprintID, boardID))
    
    print("Total CLOSED Sprints: {}".format(countSprint))
    print("-------------COMPLETED {}-------------".format(repo.name.upper()))



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
    
    extractSprintFeature()

    cursor.close()
    connection.close()
    print("DB Connection is closed")
